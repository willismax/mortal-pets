"""產生小梅、小竹的 Codex 寵物 spritesheet（同人像素風）。

Codex app 讀取固定的 8 欄 x 9 列圖集，每格 192x208。
每格先在 48x52 的像素畫布上作畫，再以最近鄰放大 4 倍。

用法：python3 tools/build_sprites.py            # 輸出到 codex/pets/<id>/
      python3 tools/build_sprites.py --preview  # 另外輸出 qa/ 的預覽 GIF 與總覽圖
"""

import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
W, H, SCALE = 48, 52, 4
CELL_W, CELL_H = W * SCALE, H * SCALE
COLS, ROWS = 8, 9

# 依 hatch-pet 的 references/animation-rows.md
ROW_SPEC = [
    ("idle", [280, 110, 110, 140, 140, 320]),
    ("running-right", [120] * 7 + [220]),
    ("running-left", [120] * 7 + [220]),
    ("waving", [140] * 3 + [280]),
    ("jumping", [140] * 4 + [280]),
    ("failed", [140] * 7 + [240]),
    ("waiting", [150] * 5 + [260]),
    ("running", [120] * 5 + [220]),
    ("review", [150] * 5 + [280]),
]

OUTLINE = (42, 28, 36, 255)

CHARACTERS = {
    "xiaomei": {
        "displayName": "小梅",
        "description": "崆峒飛天門的虞小梅：高馬尾、白衣紅裙、愛鬧愛笑、廚藝一流。招牌是飛踢與鶴手，說「本梅」的時候才是真心話。（活俠傳同人）",
        # 依官方立繪：高馬尾紅髮繩、白上衣紅交領、深褐腰封、紅色長褶裙、褐色護腕
        "hair": (34, 28, 34, 255),
        "hair_hi": (78, 66, 74, 255),
        "skin": (255, 226, 204, 255),
        "skin_sh": (240, 190, 165, 255),
        "eye": (70, 26, 40, 255),
        "cloth": (252, 248, 242, 255),
        "cloth_sh": (222, 212, 206, 255),
        "accent": (204, 58, 62, 255),  # 紅裙、紅交領
        "accent_sh": (150, 34, 40, 255),
        "sleeve": (252, 248, 242, 255),
        "obi": (98, 66, 50, 255),  # 深褐腰封
        "bracer": (102, 70, 52, 255),  # 褐色護腕
        "shoe": (150, 34, 40, 255),
        "leg": (252, 248, 242, 255),  # 白襪
        "blush": (255, 150, 160, 255),
        "ponytail": True,
        "outfit": "hakama",
        "long_hair": False,
        "height_drop": 0,
        "default_eyes": "open",
    },
    "xiaozhu": {
        "displayName": "小竹",
        "description": "崆峒鐵拳門的郁竹，人稱「裂骨魔」：身形嬌小、力大無窮、熬夜打鐵做玩具。眼神兇是因為近視又沒睡。（活俠傳同人）",
        # 依官方立繪：卡其頭巾與領巾、淺綠短袖上衣、長工作手套、卡其長圍裙
        "hair": (44, 38, 36, 255),
        "hair_hi": (84, 74, 68, 255),
        "skin": (255, 226, 204, 255),
        "skin_sh": (238, 190, 166, 255),
        "eye": (138, 88, 42, 255),  # 琥珀色眼睛
        "lid": (52, 40, 36, 255),
        "cloth": (150, 186, 86, 255),
        "cloth_sh": (110, 144, 60, 255),
        "accent": (206, 188, 150, 255),  # 卡其長圍裙
        "accent_sh": (164, 144, 106, 255),
        "sleeve": (150, 186, 86, 255),
        "glove": (196, 176, 136, 255),  # 長工作手套
        "kerchief": (184, 168, 132, 255),  # 頭巾、領巾
        "kerchief_sh": (146, 130, 98, 255),
        "belt": (74, 64, 56, 255),
        "shoe": (74, 58, 46, 255),
        "leg": (110, 144, 60, 255),
        "blush": (246, 160, 150, 255),
        "bags": (214, 176, 180, 255),  # 黑眼圈
        "blush_always": True,
        "outfit": "apron",
        "round": True,  # 整隻圓滾滾：圓身體、粗手腳
        "long_hair": False,
        "height_drop": 2,
        "default_eyes": "drowsy",
    },
}

# 以下三位依官方立繪（唐默鈴角色設定圖、LoM Wiki 立繪）
CHARACTERS["xiaoshimei"] = {
    "displayName": "小師妹",
    "description": "唐門掌門獨生女唐默鈴：氣質宛如森林小動物，生性淡漠，身繫七串鈴鐺卻從來聽不見響聲；喜歡摺紙，輕功天下前五卻常迷路。（活俠傳同人）",
    # 長黑髮側分、頸上掛鈴、暗紅交領短袖上衣（白色荷葉袖口、袖上掛鈴）、深藍腰帶、粉紅長裙
    "hair": (30, 26, 32, 255), "hair_hi": (78, 70, 84, 255),
    "skin": (255, 232, 218, 255), "skin_sh": (240, 198, 180, 255),
    "eye": (70, 64, 76, 255),
    "cloth": (150, 44, 52, 255), "cloth_sh": (112, 30, 38, 255),
    "accent": (230, 150, 176, 255), "accent_sh": (196, 112, 142, 255),
    "collar": (196, 150, 90, 255),
    "sash": (62, 66, 112, 255),
    "sleeve": (150, 44, 52, 255), "cuff": (250, 246, 244, 255), "bells": True,
    "shoe": (112, 30, 38, 255), "leg": (250, 240, 240, 255),
    "blush": (255, 160, 170, 255),
    "outfit": "dress", "head": "locks", "tassel": True, "waist": True,
    "long_hair": False, "height_drop": 2, "default_eyes": "open",
}
CHARACTERS["longxiang"] = {
    "displayName": "龍湘",
    "description": "師承錦香宮、劍法精絕的清麗佳人龍湘，人稱「雞腿女俠」：白衣青帶、坦率開朗又有點呆，從小拿雞腿當劍練，最愛餐餐有雞腿。（活俠傳同人）",
    # 長髮半束成髻、青色髮簪、額間紅花鈿、白衣青領、青色寬腰帶與護腕、左手持劍（紅色劍穗）
    "hair": (30, 36, 36, 255), "hair_hi": (72, 86, 86, 255),
    "skin": (255, 228, 210, 255), "skin_sh": (238, 190, 168, 255),
    "eye": (60, 90, 110, 255),
    "cloth": (250, 250, 252, 255), "cloth_sh": (214, 222, 226, 255),
    "accent": (248, 250, 252, 255), "accent_sh": (206, 216, 222, 255),
    "collar": (84, 150, 150, 255),
    "sash": (84, 150, 150, 255), "sash_pattern": (46, 96, 100, 255),
    "ribbon": (96, 176, 176, 255),
    "bracer": (84, 150, 150, 255),
    "skirt_band": (84, 150, 150, 255),
    "sleeve": (250, 250, 252, 255),
    "shoe": (60, 80, 84, 255), "leg": (250, 250, 252, 255),
    "blush": (255, 160, 150, 255),
    "outfit": "dress", "head": "ribbon", "scabbard": True, "topknot": True, "forehead": (210, 50, 60, 255),
    "long_hair": True, "height_drop": -2, "tall": 2, "default_eyes": "open",
}
CHARACTERS["xiahoulan"] = {
    "displayName": "夏侯蘭",
    "description": "崆峒奪魄門的夏侯蘭，人稱「奪魄幽蘭」：齊瀏海長黑髮、一身藍衣、撐著油紙傘，總是一臉冷淡無神；嘴上對「懶徒兒」尖酸刻薄，照顧起來卻無微不至。（活俠傳同人）",
    # 齊瀏海長直髮、側邊藍色髮繩與翠綠耳墜、藍色寬袖長衣、淺藍內領、油紙傘
    "hair": (24, 22, 28, 255), "hair_hi": (64, 62, 74, 255),
    "skin": (252, 238, 234, 255), "skin_sh": (228, 204, 200, 255),
    "eye": (58, 46, 80, 255), "lid": (24, 20, 28, 255),  # 深紫黑的眼珠
    "glint": (128, 112, 156, 255),
    "cloth": (58, 92, 196, 255), "cloth_sh": (38, 62, 150, 255),
    "accent": (52, 82, 182, 255), "accent_sh": (34, 54, 136, 255),
    "collar": (150, 196, 246, 255),
    "sash": (34, 50, 120, 255),
    "band": (70, 120, 220, 255), "earring": (80, 180, 120, 255),
    "sleeve": (70, 108, 212, 255), "wide_sleeves": True,
    "shoe": (30, 30, 50, 255), "leg": (52, 82, 182, 255),
    "blush": (240, 150, 160, 255), "lips": (206, 70, 86, 255),
    "outfit": "dress", "head": "hime",
    "long_hair": True, "height_drop": -1, "tall": 1, "default_eyes": "dull",
}

# 小竹・裂骨魔：同一個人，換上鐵網護甲、虎紋背帶、虎頭面具與機關臂，背著刻紅紋的大刀
CHARACTERS["xiaozhu-battle"] = {
    **CHARACTERS["xiaozhu"],
    "displayName": "小竹・裂骨魔",
    "description": "郁竹的戰鬥裝束：鐵網護甲、虎紋肩甲，右臂是扛著紅紋巨劍的機關臂，左手拿虎頭盾，兩者在背後靠背包相連。平常睏睏的，掄起兵器就是「裂骨魔」。（活俠傳同人）",
    "battle": True,
}


def P(**kw):
    base = dict(dy=0, dx=0, eyes=None, mouth="smile", arms=("down", "down"),
                legs="stand", facing="front", tilt=0, prop=None, fx=(), blush=False,
                hair_sway=0)
    base.update(kw)
    return base


class Painter:
    def __init__(self, c):
        self.c = c
        self.img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def px(self, x, y, col):
        if 0 <= x < W and 0 <= y < H:
            self.img.putpixel((int(x), int(y)), col)

    def rect(self, x0, y0, x1, y1, col):
        self.d.rectangle([x0, y0, x1, y1], fill=col)

    def ell(self, x0, y0, x1, y1, col, outline=None):
        self.d.ellipse([x0, y0, x1, y1], fill=col, outline=outline)

    def poly(self, pts, col, outline=None):
        self.d.polygon(pts, fill=col, outline=outline)

    def line(self, pts, col, w=1):
        self.d.line(pts, fill=col, width=w)


ARM_HANDS = {
    # (dx, dy) 相對肩膀；左右手分開定義（L 為畫面左側）
    "down": ((-2, 7), (2, 7)),
    "hip": ((-4, 4), (4, 4)),
    "up": ((-5, -9), (5, -9)),
    "wave_up": ((-6, -9), (6, -9)),
    "wave_mid": ((-8, -4), (8, -4)),
    "front": ((3, 6), (-3, 6)),
    "swing_f": ((4, 4), (4, 4)),
    "swing_b": ((-4, 5), (-4, 5)),
    "chin": ((3, -3), (-3, -3)),
    "brow": ((4, -9), (-4, -9)),
    "hold": ((5, 2), (5, 2)),
    "hammer_up": ((7, -7), (7, -7)),
    "fist_up": ((-5, -10), (5, -10)),
    "behind": ((-1, 4), (1, 4)),
    "crane": ((-7, -12), (7, -12)),
    "crane_mid": ((-8, -7), (8, -7)),
    "spread": ((-10, -3), (10, -4)),
    "fist_side": ((3, -3), (-3, -3)),
    "bonk": ((5, -18), (4, -18)),
    "belly": ((5, 5), (-5, 5)),
    "wipe": ((-5, -9), (5, -9)),
    "cross": ((7, 3), (-7, 3)),  # 雙手抱胸
    "clasp": ((5, -1), (-5, -1)),  # 雙手交握在胸前（小師妹的招牌姿勢）
    "hair_hold": ((-1, -3), (1, -3)),  # 雙手握著胸前的鬢髮
    "tremble": ((2, -4), (-2, -4)),  # 嚇得縮起雙手
    "umbrella": ((2, 2), (3, 0)),  # 握傘柄
    "sleeve_face": ((6, -6), (-6, -6)),  # 用袖子遮臉
    "beckon": ((-9, -1), (9, -1)),  # 伸手示意「跟我來」
    "beckon_in": ((-7, -3), (7, -3)),
    "thrust": ((-9, -5), (11, -3)),  # 出劍、出掌
    "nibble": ((3, -6), (-2, -7)),  # 拿雞腿到嘴邊
    "hold_up": ((5, -2), (-5, -2)),  # 雙手捧起東西端詳  # 手肘往外抬；前臂在畫完臉之後補上
    "hammer_down": ((7, 3), (7, 3)),
    "stir_a": ((5, 5), (3, 6)),
    "stir_b": ((7, 4), (5, 7)),
    "droop": ((-1, 8), (1, 8)),
    "face": ((5, -5), (-5, -5)),
    "ask": ((3, 2), (6, -2)),
}


def draw_frame(cid, pose):
    c = CHARACTERS[cid]
    p = Painter(c)
    dy = pose["dy"] + c["height_drop"]
    dx = pose["dx"]
    face_r = pose["facing"] == "right"
    look = 2 if face_r else 0
    eyes = pose["eyes"] or c["default_eyes"]
    if eyes == "squint" and c["default_eyes"] == "drowsy":
        eyes = "drowsy"  # 小竹的「兇」其實是睏
    if c["default_eyes"] == "dull" and eyes in ("open", "squint", "side"):
        eyes = "dull_side" if eyes == "side" else "dull"  # 夏侯蘭睜眼時一律是無神的眼睛

    hx = 24 + dx + pose["tilt"]  # 頭中心
    hy = 19 + dy
    sx_l, sx_r, sy = 19 + dx, 29 + dx, 35 + dy  # 肩膀
    if c.get("round"):
        sx_l, sx_r, sy = 16 + dx, 32 + dx, 34 + dy  # 圓身體的肩膀在兩側
    hip_y = 44 + dy

    battle = c.get("battle", False)
    rnd = c.get("round", False)

    # 後髮
    sway = pose["hair_sway"]
    if c.get("ponytail"):
        p.ell(hx - 12, hy - 12, hx + 12, hy + 10, c["hair"], OUTLINE)
        # 高馬尾從頭頂右後方甩出去，往右跑時甩到左邊
        k = -1 if face_r else 1
        bx0 = hx + 4 * k
        pts = [(bx0, hy - 14), (bx0 + 4 * k, hy - 15), (bx0 + 11 * k + sway * k, hy - 9),
               (bx0 + 13 * k + sway * 2 * k, hy + 1), (bx0 + 10 * k + sway * 2 * k, hy + 5),
               (bx0 + 9 * k + sway * k, hy - 4), (bx0 + 3 * k, hy - 10)]
        p.poly(pts, c["hair"], OUTLINE)
        p.line([(bx0 + 5 * k, hy - 12), (bx0 + 10 * k + sway * k, hy - 5)], c["hair_hi"])
    elif c.get("head") == "locks":
        # 小師妹：頭髮往後梳，後面只到肩膀
        p.ell(hx - 12, hy - 12, hx + 12, hy + 10, c["hair"], OUTLINE)
        p.rect(hx - 10, hy + 6, hx + 10, hy + 12, c["hair"])
    elif c["long_hair"]:
        tail = -3 if face_r else 0
        p.poly([(hx - 11 + tail + sway, hy), (hx + 11 + tail + sway, hy),
                (hx + 10 + tail + sway * 2, hy + 21), (hx - 10 + tail + sway * 2, hy + 21)],
               c["hair"], OUTLINE)
        if c.get("topknot"):
            p.ell(hx - 5, hy - 17, hx + 5, hy - 9, c["hair"], OUTLINE)
            p.rect(hx - 2, hy - 15, hx - 1, hy - 14, c["hair_hi"])
    else:
        p.ell(hx - 12, hy - 12, hx + 12, hy + 9, c["hair"], OUTLINE)
        # 腦後隨手紮起的一小撮頭髮
        tx = hx + 9 - (5 if face_r else 0) + sway
        p.ell(tx, hy - 1, tx + 5, hy + 5, c["hair"], OUTLINE)
        p.line([(tx + 3, hy + 5), (tx + 4, hy + 9)], c["hair"], 2)

    # 腿
    legs = pose["legs"]
    shoe, skin = c["shoe"], c["skin"]

    def leg(x, top, bottom, lift=0):
        w = 3 if rnd else 2
        p.rect(x - 1, top, x + w, bottom - lift, OUTLINE)
        p.rect(x, top, x + w - 1, bottom - lift, c["leg"])
        p.rect(x - 1, bottom - lift + 1, x + w, bottom - lift + 2, shoe)

    base_bottom = 47 + dy + c.get("tall", 0)
    if legs == "stand":
        leg(21 + dx, hip_y, base_bottom)
        leg(26 + dx, hip_y, base_bottom)
    elif legs == "stepA":
        leg(23 + dx, hip_y, base_bottom, 0)
        leg(18 + dx, hip_y, base_bottom - 1, 1)
        p.px(23 + dx + 3, base_bottom + 1, shoe)
    elif legs == "stepB":
        leg(19 + dx, hip_y, base_bottom, 0)
        leg(27 + dx, hip_y, base_bottom - 1, 1)
        p.px(27 + dx + 3, base_bottom - 1, shoe)
    elif legs == "pass":
        leg(22 + dx, hip_y, base_bottom)
        leg(25 + dx, hip_y, base_bottom - 2, 0)
    elif legs == "tuck":
        leg(20 + dx, hip_y, hip_y + 2)
        leg(27 + dx, hip_y, hip_y + 2)
    elif legs == "kick":
        # 左腳收起、右腳往旁邊踢直
        leg(20 + dx, hip_y, hip_y + 1)
        kx0, ky0, kx1, ky1 = 26 + dx, hip_y - 1, 40 + dx, hip_y - 7
        p.line([(kx0, ky0), (kx1, ky1)], OUTLINE, 5)
        p.line([(kx0, ky0), (kx1, ky1)], c["leg"], 3)
        p.rect(kx1 - 1, ky1 - 3, kx1 + 4, ky1 + 2, OUTLINE)
        p.rect(kx1, ky1 - 2, kx1 + 3, ky1 + 1, shoe)
    elif legs == "crouch":
        leg(20 + dx, hip_y, base_bottom)
        leg(27 + dx, hip_y, base_bottom)

    if battle:
        # 背包與虎紋背架：從背後把機關臂和虎頭盾連在一起，只露出邊緣
        p.rect(12 + dx, 27 + dy, 36 + dx, 41 + dy, OUTLINE)
        p.rect(13 + dx, 28 + dy, 35 + dx, 40 + dy, (112, 92, 70, 255))
        p.line([(13 + dx, 29 + dy), (35 + dx, 29 + dy)], (232, 160, 40, 255), 2)
        for k in range(14, 36, 4):
            p.px(k + dx, 29 + dy, (30, 24, 20, 255)); p.px(k + dx, 30 + dy, (30, 24, 20, 255))

    # 身體（裙裝）
    flare = -1 if face_r else 0
    if rnd:
        p.ell(14 + dx + flare, 30 + dy, 34 + dx + flare, 47 + dy, c["cloth"], OUTLINE)
    else:
        body = [(20 + dx, 33 + dy), (28 + dx, 33 + dy), (32 + dx + flare, 45 + dy), (16 + dx + flare, 45 + dy)]
        if c.get("waist"):  # 小師妹：泡泡袖撐起肩膀、腰帶束出細腰
            body = [(17 + dx, 33 + dy), (31 + dx, 33 + dy), (29 + dx, 38 + dy), (19 + dx, 38 + dy)]
        p.poly(body, c["cloth"], OUTLINE)
        p.line([(17 + dx + flare, 44 + dy), (31 + dx + flare, 44 + dy)], c["cloth_sh"])
    if c.get("outfit") == "hakama":
        # 紅色長褶裙（踢腿時往踢的方向揚起）
        kick = legs == "kick"
        skirt = [(18 + dx, 40 + dy), (30 + dx, 40 + dy),
                 (37 + dx if kick else 33 + dx + flare, (41 if kick else 48) + dy),
                 (15 + dx + flare, 48 + dy)]
        p.poly(skirt, c["accent"], OUTLINE)
        for k_ in (20, 23, 26, 29):
            p.line([(k_ + dx, 42 + dy), (k_ + dx + (2 if kick else flare), 47 + dy)], c["accent_sh"])
        # 紅交領
        p.line([(21 + dx, 33 + dy), (24 + dx, 37 + dy)], c["accent"])
        p.line([(27 + dx, 33 + dy), (24 + dx, 37 + dy)], c["accent"])
        # 深褐腰封與紅線
        p.rect(18 + dx, 37 + dy, 30 + dx, 40 + dy, c["obi"])
        p.line([(18 + dx, 39 + dy), (30 + dx, 39 + dy)], c["accent"])
    elif c.get("outfit") == "dress":
        # 上衣、交領、腰帶與長裙（長裙蓋住大半雙腿，身高高的角色裙子較長）
        hem = 46 + dy + c.get("tall", 0)
        kick = legs == "kick"
        if c.get("waist"):  # 小師妹：裙子從細腰順順往下垂，只微微變寬
            skirt = [(19 + dx, 40 + dy), (29 + dx, 40 + dy), (31 + dx + flare, hem), (17 + dx + flare, hem)]
        else:
            skirt = [(18 + dx, 40 + dy), (30 + dx, 40 + dy), (33 + dx + flare, hem), (15 + dx + flare, hem)]
        p.poly(skirt, c["accent"], OUTLINE)
        for k_ in (21, 24, 27):
            p.line([(k_ + dx, 42 + dy), (k_ + dx + flare, hem - 1)], c["accent_sh"])
        if "skirt_band" in c:  # 白裙正中的青色長帶
            p.line([(24 + dx, 41 + dy), (24 + dx + flare, hem - 1)], c["skirt_band"], 2)
        col = c.get("collar", c["accent_sh"])
        p.line([(21 + dx, 33 + dy), (24 + dx, 37 + dy)], col)
        p.line([(27 + dx, 33 + dy), (24 + dx, 37 + dy)], col)
        sw = 1 if c.get("waist") else 0  # 細腰的腰帶窄一點
        p.rect(18 + sw + dx, (37 if "sash_pattern" in c else 38) + dy, 30 - sw + dx, 40 + dy, c["sash"])  # 龍湘的腰帶較寬
        if "sash_pattern" in c:  # 腰帶上的菱形紋
            for k_ in (20, 24, 28):
                p.px(k_ + dx, 38 + dy, c["sash_pattern"]); p.px(k_ + 1 + dx, 39 + dy, c["sash_pattern"])
        p.line([(29 + dx, 41 + dy), (30 + dx + flare, 44 + dy)], c["sash"])  # 腰帶垂下的帶子
        if c.get("tassel"):  # 小師妹腰間的小荷包與流蘇
            p.ell(25 + dx, 40 + dy, 28 + dx, 43 + dy, (176, 140, 90, 255), OUTLINE)
            p.line([(21 + dx, 41 + dy), (21 + dx + flare, 46 + dy)], (200, 160, 80, 255))
        if c.get("scabbard"):  # 左腰的劍（深色劍鞘、紅色劍穗）
            p.line([(16 + dx, 36 + dy), (12 + dx, 48 + dy)], OUTLINE, 4)
            p.line([(16 + dx, 36 + dy), (12 + dx, 48 + dy)], (52, 56, 60, 255), 2)
            p.line([(17 + dx, 34 + dy), (16 + dx, 36 + dy)], (200, 170, 90, 255), 2)
            p.line([(15 + dx, 38 + dy), (14 + dx, 43 + dy)], (200, 40, 50, 255))
            p.px(13 + dx, 44 + dy, (220, 180, 80, 255))
    else:
        # 圍裙吊帶、深色腰帶、卡其長圍裙
        p.line([(20 + dx, 32 + dy), (20 + dx, 38 + dy)], c["accent"], 2)
        p.line([(27 + dx, 32 + dy), (27 + dx, 38 + dy)], c["accent"], 2)
        p.d.chord([16 + dx + flare, 31 + dy, 32 + dx + flare, 47 + dy], 0, 180, fill=c["accent"], outline=OUTLINE)
        p.line([(20 + dx + flare, 42 + dy), (20 + dx + flare, 45 + dy)], c["accent_sh"])
        p.line([(28 + dx + flare, 42 + dy), (28 + dx + flare, 45 + dy)], c["accent_sh"])
        p.line([(15 + dx + flare, 39 + dy), (33 + dx + flare, 39 + dy)], c["belt"])

    if battle:
        # 鐵網護甲
        p.rect(19 + dx, 31 + dy, 29 + dx, 38 + dy, (198, 182, 140, 255))
        for gx in range(19, 30, 2):
            p.line([(gx + dx, 31 + dy), (gx + dx, 38 + dy)], (96, 86, 70, 255))
        for gy in range(31, 39, 2):
            p.line([(19 + dx, gy + dy), (29 + dx, gy + dy)], (96, 86, 70, 255))

    # 手臂
    al, ar = pose["arms"]

    def arm(sx, name, side):
        hdx, hdy = ARM_HANDS[name][side]
        ex, ey = sx + hdx, sy + hdy
        aw = 3 if rnd or "bracer" in c or c.get("wide_sleeves") or "cuff" in c else 2  # 圓手腳、寬袖
        p.line([(sx, sy), (ex, ey)], OUTLINE, aw + 2)
        p.line([(sx, sy), (ex, ey)], c["sleeve"], aw)
        p.px(ex, ey, OUTLINE)
        hand = c["skin"]
        if name == "behind":  # 雙手背在身後：只露出一點袖子
            return ex, ey
        if "cuff" in c:  # 小師妹：手肘的白色荷葉邊袖口與鈴鐺
            mx, my = (sx + ex) // 2, (sy + ey) // 2
            p.line([(mx, my), (ex, ey)], c["skin"], 2)
            p.rect(mx - 1, my - 1, mx + 1, my + 1, c["cuff"])
            if c.get("bells"):
                p.px(mx + (1 if side else -1), my - 2, (226, 190, 80, 255))
        if "bracer" in c:  # 前臂的護腕
            mx, my = (sx + ex * 2) // 3, (sy + ey * 2) // 3
            p.line([(mx, my), (ex, ey)], c["bracer"], aw)
        if name in ("crane", "crane_mid"):
            # 鶴手：手腕下彎、指尖朝下
            d_ = 1 if side == 1 else -1
            hook = [(ex, ey), (ex + 2 * d_, ey - 2), (ex + 4 * d_, ey - 1), (ex + 5 * d_, ey + 2), (ex + 5 * d_, ey + 4)]
            p.line(hook, OUTLINE, 4)
            p.line(hook, hand, 2)
            p.px(ex + 5 * d_, ey + 5, OUTLINE)
            return ex, ey
        if "glove" in c:  # 短袖，前臂到手掌是長手套
            mx, my = (sx * 2 + ex) // 3, (sy * 2 + ey) // 3
            p.line([(mx, my), (ex, ey)], c["glove"], aw)
            hand = c["glove"]
        if rnd:
            p.ell(ex - 2, ey - 2, ex + 2, ey + 2, hand, OUTLINE)
        else:
            p.rect(ex - 1, ey - 1, ex + 1, ey + 1, OUTLINE)
            p.rect(ex - 1, ey - 1, ex, ey, hand)
        return ex, ey

    if battle:
        prop = pose["prop"]
        if prop and prop[0] == "hammer":
            blade = "high" if prop[1] == "up" else "low"
        elif ar in ("up", "wave_up", "fist_up"):
            blade = "high"
        elif ar == "droop":
            blade = "droop"
        else:
            blade = "rest"
        rig_r = {"rest": 0, "high": -2, "low": 2, "droop": 3}[blade]
        rig_y = dy - 2 + rig_r  # 原點以站姿為準
        pose = dict(pose, prop=None)  # 戰鬥裝不拿鐵鎚
        ar = "rig"
        ARM_HANDS["rig"] = ((0, 0), (5, -1 + rig_r))
        ARM_HANDS["shield"] = ((-4, 6), (0, 0))
        al = "shield" if al in ("down", "hip", "front", "droop", "chin", "brow", "face", "ask", "swing_b", "swing_f") else al

    hand_l = arm(sx_l, al, 0)
    hand_r = arm(sx_r, ar, 1)

    if battle:
        # 肩甲：虎紋護肩蓋在兩邊肩膀上（與背後的背包相連）
        for shx in (sx_l, sx_r):
            p.ell(shx - 3, sy - 3, shx + 3, sy + 2, (232, 160, 40, 255), OUTLINE)
            p.line([(shx - 1, sy - 2), (shx - 2, sy + 1)], (30, 24, 20, 255))
            p.line([(shx + 2, sy - 2), (shx + 1, sy + 1)], (30, 24, 20, 255))
        # 虎頭盾
        sx0, sy0 = hand_l[0] - 7, hand_l[1] - 6
        orange, dark, stripe = (214, 132, 60, 255), (30, 24, 20, 255), (150, 78, 30, 255)
        p.rect(sx0 + 1, sy0 - 2, sx0 + 3, sy0, OUTLINE); p.px(sx0 + 2, sy0 - 1, orange)
        p.rect(sx0 + 8, sy0 - 2, sx0 + 10, sy0, OUTLINE); p.px(sx0 + 9, sy0 - 1, orange)
        p.ell(sx0, sy0 - 1, sx0 + 11, sy0 + 11, orange, OUTLINE)
        p.line([(sx0 + 4, sy0 + 1), (sx0 + 7, sy0 + 1)], dark)  # 額頭的「王」
        p.px(sx0 + 5, sy0 + 2, dark)
        p.line([(sx0 + 2, sy0 + 4), (sx0 + 4, sy0 + 5)], dark); p.line([(sx0 + 9, sy0 + 4), (sx0 + 7, sy0 + 5)], dark)
        p.line([(sx0 + 1, sy0 + 7), (sx0 + 3, sy0 + 7)], stripe); p.line([(sx0 + 8, sy0 + 7), (sx0 + 10, sy0 + 7)], stripe)
        p.rect(sx0 + 5, sy0 + 6, sx0 + 6, sy0 + 7, (240, 196, 140, 255))
        p.line([(sx0 + 3, sy0 + 9), (sx0 + 8, sy0 + 9)], dark)

    if battle:
        # 紅紋巨劍：劍柄被機關臂的爪子抓住，劍身越過頭頂伸向左邊
        grip = (42, 6 + rig_y)
        tip = {"rest": (2, 3 + rig_y), "high": (3, max(0, rig_y)), "low": (2, 9 + rig_y), "droop": (4, 20 + rig_y)}[blade]
        p.line([grip, tip], OUTLINE, 6)
        p.line([grip, tip], (172, 174, 184, 255), 4)
        p.line([(grip[0], grip[1] - 1), (tip[0], tip[1] - 1)], (228, 230, 236, 255), 1)
        for t in (0.35, 0.42, 0.5):
            p.px(round(grip[0] + (tip[0] - grip[0]) * t), round(grip[1] + (tip[1] - grip[1]) * t), (200, 40, 40, 255))
        p.line([(42, 6 + rig_y), (47, 6 + rig_y)], OUTLINE, 4)
        p.line([(42, 6 + rig_y), (46, 6 + rig_y)], (70, 68, 74, 255), 2)

    if pose["prop"] and pose["prop"][0] == "umbrella":
        # 夏侯蘭的油紙傘：右手握傘柄，傘面斜在右肩後
        x, y = hand_r
        k = -1 if face_r else 1
        # 傘面撐開在頭的後上方，像官方立繪那樣襯在身後
        cx, cy = hx + 7 * k, hy - 6
        p.line([(x, y), (cx, cy)], OUTLINE, 3)
        p.line([(x, y), (cx, cy)], (120, 80, 50, 255), 1)
        p.d.chord([cx - 16, cy - 15, cx + 16, cy + 13], 180, 360, fill=(196, 128, 72, 255), outline=OUTLINE)
        for t in (-13, -8, -3, 3, 8, 13):
            p.line([(cx, cy - 13), (cx + t, cy - 1)], (138, 82, 44, 255))
        p.line([(cx - 15, cy - 1), (cx + 15, cy - 1)], (138, 82, 44, 255))

    # 頭
    hw = 11 if rnd else 10  # 小竹臉頰比較圓
    chin = 13 if c.get("mature") else 12  # 夏侯蘭下巴稍長、臉型成熟
    p.ell(hx - hw, hy - 8, hx + hw, hy + chin, c["skin"], OUTLINE)
    hair = c["hair"]
    if c.get("head") == "locks":
        # 小師妹：側分、露出額頭，不畫整排瀏海
        p.d.chord([hx - 11, hy - 13, hx + 11, hy - 1], 180, 360, fill=hair, outline=OUTLINE)
    else:
        # 瀏海
        p.d.chord([hx - 11, hy - 12, hx + 11, hy + 8], 180, 360, fill=hair, outline=OUTLINE)
        fringe_y = hy - 2
        for i, fx_ in enumerate(range(hx - 9, hx + 10, 3)):
            h = 3 if i % 2 == 0 else 2
            p.poly([(fx_, fringe_y), (fx_ + 3, fringe_y), (fx_ + 1 + (1 if face_r else 0), fringe_y + h)], hair)
        # 側髮
        p.rect(hx - 11, hy - 2, hx - 9, hy + 7, hair)
        p.rect(hx + 9, hy - 2, hx + 11, hy + 7, hair)
    p.px(hx - 6, hy - 8, c["hair_hi"])
    p.px(hx - 5, hy - 8, c["hair_hi"])
    p.px(hx - 4, hy - 9, c["hair_hi"])

    if c.get("ponytail"):
        # 馬尾根部的紅髮繩
        bx = hx + (-5 if face_r else 4)
        by = hy - 13
        p.rect(bx - 1, by - 1, bx + 2, by + 1, OUTLINE)
        p.rect(bx, by, bx + 1, by, c["accent"])
        p.px(bx + 2, by - 2, c["accent"]); p.px(bx - 1, by - 2, c["accent"])
        # 長側髮
        p.rect(hx - 11, hy - 2, hx - 9, hy + 10, hair)
        p.rect(hx + 9, hy - 2, hx + 11, hy + 10, hair)
        if "forehead" in c:  # 額間的紅色花鈿
            p.px(hx + look, hy - 2, c["forehead"])
    elif c.get("head") == "locks":
        # 依官方立繪：頭髮往後梳、額頭露出來，一側分線，
        # 一綹頭髮從分線斜斜梳到另一側額角；鬢髮順著臉頰垂到鎖骨
        k = -1 if face_r else 1
        part = hx - 4 * k
        # 斜斜的髮際線：分線這側額頭露出來，一大綹瀏海往另一側額角梳過去
        p.poly([(part, hy - 8), (hx + 11 * k, hy - 7), (hx + 11 * k, hy + 3), (hx + 8 * k, hy + 1),
                (hx + 3 * k, hy - 3), (part + 2 * k, hy - 6)], hair, OUTLINE)
        p.poly([(part, hy - 8), (hx - 11 * k, hy - 7), (hx - 11 * k, hy - 1), (hx - 8 * k, hy - 5)], hair)
        p.line([(part + 2 * k, hy - 7), (hx + 9 * k, hy - 4)], c["hair_hi"])  # 往後梳的髮絲光澤
        p.line([(part - k, hy - 10), (hx - 7 * k, hy - 9)], c["hair_hi"])
        for side in (-1, 1):
            x0 = hx + 10 * side
            p.poly([(x0 - side, hy - 3), (x0 + side * 2, hy - 2), (x0 + side * 2, hy + 12),
                    (x0, hy + 14), (x0 - side * 2, hy + 10), (x0 - side * 2, hy + 3)], hair, OUTLINE)
    elif c.get("head") == "ribbon":
        # 頭頂髮髻插著青色髮簪，簪尾垂著青色髮帶
        k = -1 if face_r else 1
        p.line([(hx - 2 * k, hy - 12), (hx + 5 * k, hy - 14)], OUTLINE, 3)
        p.line([(hx - 2 * k, hy - 12), (hx + 5 * k, hy - 14)], c["ribbon"], 1)
        p.line([(hx + 5 * k, hy - 12), (hx + 8 * k, hy - 6)], c["ribbon"])
        p.rect(hx - 11, hy - 2, hx - 9, hy + 10, hair)
        p.rect(hx + 9, hy - 2, hx + 11, hy + 10, hair)
    elif c.get("head") == "hime":
        # 齊瀏海、長直鬢髮，側邊藍色髮繩與翠綠耳墜
        p.rect(hx - 9, hy - 3, hx + 9, hy + 1, hair)
        p.line([(hx - 9, hy + 1), (hx + 9, hy + 1)], OUTLINE)
        p.rect(hx - 11, hy - 2, hx - 9, hy + 13, hair)
        p.rect(hx + 9, hy - 2, hx + 11, hy + 13, hair)
        k = -1 if face_r else 1
        bx = hx + 10 * k
        p.rect(bx - 1, hy - 7, bx + 1, hy - 5, c["band"])
        p.line([(bx, hy - 4), (bx + k, hy + 2)], c["band"])
        p.px(hx - 9 * k, hy + 8, c["earring"]); p.px(hx - 9 * k, hy + 9, c["earring"])
    else:
        # 卡其頭巾包住頭頂，結打在腦後
        p.d.chord([hx - 11, hy - 12, hx + 11, hy + 9], 180, 360, fill=c["kerchief"], outline=OUTLINE)
        p.line([(hx - 8, hy - 6), (hx - 3, hy - 9)], c["kerchief_sh"])
        p.line([(hx + 2, hy - 9), (hx + 7, hy - 6)], c["kerchief_sh"])
        # 頭巾下露出的瀏海
        for i, fx_ in enumerate(range(hx - 8, hx + 8, 3)):
            p.poly([(fx_, hy - 2), (fx_ + 3, hy - 2), (fx_ + 1, hy + (2 if i % 2 else 1))], hair)
        kx = hx - 13 if face_r else hx + 11
        kd = -1 if face_r else 1
        p.poly([(kx, hy - 6), (kx + 3 * kd, hy - 4), (kx + 2 * kd, hy - 1), (kx, hy - 3)], c["kerchief"], OUTLINE)
        # 翹起的髮梢
        p.px(hx - 11, hy - 4, hair); p.px(hx - 12, hy - 3, hair)

    # 五官
    ey = hy + 3
    lx, rx = hx - 5 + look, hx + 3 + look
    eye = c["eye"]
    white = (255, 255, 255, 255)

    def eye_open(x, big=False):
        top = ey - (1 if big else 0)
        p.rect(x, top, x + 1, ey + 2, eye)
        if "lid" in c:
            p.line([(x - 1, top - 1), (x + 2, top - 1)], c["lid"])
        p.px(x, top, white)

    if eyes in ("open", "wide"):
        eye_open(lx, eyes == "wide")
        eye_open(rx, eyes == "wide")
    elif eyes == "blink":
        p.line([(lx, ey + 2), (lx + 1, ey + 2)], eye)
        p.line([(rx, ey + 2), (rx + 1, ey + 2)], eye)
    elif eyes == "happy":
        for x in (lx, rx):
            p.px(x, ey + 1, eye); p.px(x + 1, ey, eye); p.px(x + 2, ey + 1, eye)
    elif eyes == "wink":
        eye_open(lx)
        p.px(rx, ey + 1, eye); p.px(rx + 1, ey, eye); p.px(rx + 2, ey + 1, eye)
    elif eyes == "squint":
        p.line([(lx - 1, ey), (lx + 2, ey + 1)], eye)
        p.line([(rx - 1, ey + 1), (rx + 2, ey)], eye)
        p.line([(lx, ey + 2), (lx + 1, ey + 2)], eye)
        p.line([(rx, ey + 2), (rx + 1, ey + 2)], eye)
    elif eyes == "sad":
        p.line([(lx - 1, ey + 1), (lx + 2, ey)], eye)
        p.line([(rx - 1, ey), (rx + 2, ey + 1)], eye)
        p.rect(lx, ey + 2, lx + 1, ey + 2, eye)
        p.rect(rx, ey + 2, rx + 1, ey + 2, eye)
    elif eyes == "closed":
        p.line([(lx - 1, ey + 2), (lx + 2, ey + 2)], eye)
        p.line([(rx - 1, ey + 2), (rx + 2, ey + 2)], eye)
    elif eyes == "drowsy":  # 眼皮半垂、琥珀色眼珠
        for x in (lx, rx):
            p.line([(x - 1, ey), (x + 2, ey)], c["lid"])
            p.rect(x, ey + 1, x + 1, ey + 2, eye)
            p.px(x + 1, ey + 1, white)
    elif eyes in ("dull", "dull_side"):  # 夏侯蘭：大而無神的眼睛，眼皮半垂、濃密睫毛往外挑，沒有光
        lid = c.get("lid", eye)
        po = 1 if eyes == "dull_side" else 0  # 斜眼時瞳孔偏向一側
        for x, out in ((lx, -1), (rx, 1)):
            # 清秀的鳳眼：細長眼線、眼尾輕輕上挑，眼皮微垂蓋住瞳孔上緣
            p.line([(x - 1, ey), (x + 2, ey)], lid)
            p.px(x + (3 if out > 0 else -2), ey - 1, lid)
            p.rect(x, ey + 1, x + 1, ey + 2, eye)  # 深色瞳孔
            gx = x + (1 if out < 0 else 0)  # 微光靠眼頭
            if po:
                gx = x + 1
            p.px(gx, ey + 1, c.get("glint", eye))
    elif eyes == "side":  # 害羞地往旁邊看
        for x in (lx, rx):
            p.rect(x + 1, ey, x + 2, ey + 2, eye)
            p.px(x + 2, ey, white)
    elif eyes == "look_up":
        p.rect(lx, ey - 1, lx + 1, ey + 1, eye)
        p.rect(rx, ey - 1, rx + 1, ey + 1, eye)
        p.px(lx + 1, ey - 1, white); p.px(rx + 1, ey - 1, white)
    if "bags" in c and eyes not in ("happy", "closed"):
        p.line([(lx - 1, ey + 3), (lx + 2, ey + 3)], c["bags"])
        p.line([(rx - 1, ey + 3), (rx + 2, ey + 3)], c["bags"])

    mx, my = hx - 1 + look, hy + 8
    m = pose["mouth"]
    mouth = (150, 50, 60, 255)
    if "lips" in c and m in ("flat", "small"):
        m = "lips"
    if m == "lips":  # 小巧的紅唇
        p.line([(mx, my), (mx + 1, my)], c["lips"])
    elif m == "smile":
        p.px(mx - 1, my - 1, mouth); p.px(mx, my, mouth); p.px(mx + 1, my, mouth); p.px(mx + 2, my - 1, mouth)
    elif m == "grin":
        p.rect(mx - 1, my - 1, mx + 2, my, mouth); p.line([(mx - 1, my - 1), (mx + 2, my - 1)], white)
    elif m == "open":
        p.rect(mx, my - 1, mx + 1, my + 1, mouth)
    elif m == "tongue":  # 吐舌
        p.px(mx - 1, my - 1, mouth); p.px(mx, my, mouth); p.px(mx + 1, my, mouth); p.px(mx + 2, my - 1, mouth)
        p.rect(mx + 1, my + 1, mx + 2, my + 2, (236, 110, 130, 255))
    elif m == "laugh":  # 張嘴大笑
        p.rect(mx - 1, my - 1, mx + 2, my + 1, mouth)
        p.line([(mx, my + 1), (mx + 1, my + 1)], (236, 110, 130, 255))
    elif m == "small":
        p.line([(mx, my), (mx + 1, my)], (196, 96, 96, 255))
    elif m == "o":
        p.rect(mx, my, mx + 1, my + 1, mouth)
    elif m == "flat":
        p.line([(mx - 1, my), (mx + 2, my)], mouth)
    elif m == "frown":
        p.px(mx - 1, my + 1, mouth); p.px(mx, my, mouth); p.px(mx + 1, my, mouth); p.px(mx + 2, my + 1, mouth)
    elif m == "cat":
        p.px(mx - 1, my, mouth); p.px(mx, my + 1, mouth); p.px(mx + 1, my, mouth); p.px(mx + 2, my + 1, mouth); p.px(mx + 3, my, mouth)
    elif m == "smirk":
        p.px(mx, my, mouth); p.px(mx + 1, my, mouth); p.px(mx + 2, my - 1, mouth)

    if c.get("bells"):  # 頸上繫著鈴鐺的細繩（鈴鐺從不作響）
        p.line([(hx - 4, hy + 12), (hx + 4, hy + 12)], (60, 40, 40, 255))
        p.ell(hx - 1, hy + 12, hx + 1, hy + 14, (232, 196, 80, 255), OUTLINE)
    if "lips" in c and m == "smirk":
        p.px(mx, my, c["lips"])

    if "kerchief" in c:  # 領巾
        p.poly([(hx - 4, hy + 11), (hx + 4, hy + 11), (hx, hy + 15)], c["kerchief"], OUTLINE)
        p.px(hx - 1, hy + 12, c["kerchief_sh"])

    if ar == "wipe":
        # 擦汗：戴手套的前臂從手肘橫到額頭前
        elbow = (sx_r + 5, sy - 9)
        hand = (hx + 5 + look, hy)
        p.line([elbow, hand], OUTLINE, 5)
        p.line([elbow, hand], c.get("glove", c["skin"]), 3)
        p.ell(hand[0] - 2, hand[1] - 2, hand[0] + 2, hand[1] + 2, c.get("glove", c["skin"]), OUTLINE)

    if pose["blush"] or c.get("blush_always"):
        p.rect(hx - 8 + look, hy + 6, hx - 7 + look, hy + 6, c["blush"])
        p.rect(hx + 6 + look, hy + 6, hx + 7 + look, hy + 6, c["blush"])

    # 道具
    prop = pose["prop"]
    if prop:
        kind = prop[0]
        if kind == "hammer" and battle:
            # 大刀：舉起時刀尖朝上，劈下時朝右下
            x, y = hand_r
            tip = (x + 3, max(1, y - 17)) if prop[1] == "up" else (min(46, x + 10), y + 7)
            p.line([(x, y), tip], OUTLINE, 5)
            p.line([(x, y), tip], (176, 178, 186, 255), 3)
            p.line([(x + 1, y), (tip[0] + 1, tip[1])], (226, 228, 234, 255), 1)
            mx_, my_ = (x + tip[0]) // 2, (y + tip[1]) // 2
            p.px(mx_, my_, (200, 40, 40, 255)); p.px(mx_ + (1 if prop[1] == "up" else -1), my_ + 2, (200, 40, 40, 255))
            p.rect(x - 1, y - 1, x + 1, y + 1, (204, 164, 70, 255))
        elif kind == "hammer":
            # prop[1] = 'up' / 'down'
            wood, iron, shine = (128, 84, 50, 255), (128, 132, 144, 255), (196, 200, 210, 255)
            x, y = hand_r
            if prop[1] == "up":
                p.line([(x, y + 1), (x + 1, y - 7)], OUTLINE, 3)
                p.line([(x, y + 1), (x + 1, y - 7)], wood, 1)
                p.rect(x - 3, y - 13, x + 5, y - 7, OUTLINE)
                p.rect(x - 2, y - 12, x + 4, y - 8, iron)
                p.line([(x - 2, y - 12), (x + 4, y - 12)], shine)
            else:
                p.line([(x - 1, y), (x + 6, y + 1)], OUTLINE, 3)
                p.line([(x - 1, y), (x + 6, y + 1)], wood, 1)
                p.rect(x + 5, y - 4, x + 10, y + 4, OUTLINE)
                p.rect(x + 6, y - 3, x + 9, y + 3, iron)
                p.line([(x + 6, y - 3), (x + 9, y - 3)], shine)
        elif kind == "paper":  # 摺紙：stage 0 方紙、1 摺一半、2 紙鶴
            x, y = (hand_l[0] + hand_r[0]) // 2, min(hand_l[1], hand_r[1]) - 2
            paper, fold = (252, 248, 236, 255), (196, 204, 222, 255)  # 米白色紙
            if prop[1] == 0:
                p.rect(x - 4, y - 4, x + 4, y + 1, OUTLINE); p.rect(x - 3, y - 3, x + 3, y, paper)
                p.line([(x - 3, y - 3), (x + 3, y)], fold)
            elif prop[1] == 1:
                p.poly([(x - 4, y + 1), (x + 4, y + 1), (x, y - 5)], paper, OUTLINE)
                p.line([(x, y - 4), (x, y)], fold)
            else:
                y += 3  # 紙鶴捧在胸前，不擋到臉
                p.poly([(x - 8, y - 4), (x, y + 1), (x, y - 1)], paper)  # 左翅
                p.poly([(x + 8, y - 4), (x, y + 1), (x, y - 1)], fold)  # 右翅
                p.poly([(x - 2, y), (x + 2, y), (x, y + 3)], paper)  # 身體
                p.line([(x + 2, y), (x + 5, y - 3)], paper)  # 脖子
                p.px(x + 6, y - 4, fold)  # 頭
                p.px(x - 8, y - 5, OUTLINE); p.px(x + 8, y - 5, OUTLINE)
        elif kind == "drumstick":  # 雞腿
            x, y = hand_r
            if prop[1] == "mouth":
                x, y = hx + 3 + look, hy + 9
            p.line([(x, y), (x + 2, y - 2)], OUTLINE, 3)
            p.line([(x, y), (x + 2, y - 2)], (250, 246, 236, 255), 1)
            p.ell(x + 1, y - 7, x + 6, y - 2, (196, 120, 56, 255), OUTLINE)
            p.px(x + 3, y - 6, (236, 170, 96, 255))
            if prop[1] == "mouth":
                p.ell(x - 2, y - 1, x + 1, y + 2, c["skin"], OUTLINE)
        elif kind == "sword":  # 長劍：thrust 平刺、up 朝上
            x, y = hand_r
            tip = (min(47, x + 13), y - 2) if prop[1] == "thrust" else (x + 2, max(0, y - 14))
            p.line([(x, y), tip], OUTLINE, 3)
            p.line([(x, y), tip], (214, 222, 236, 255), 1)
            p.line([(x - 1, y + 1), (x + 1, y - 1)], (200, 170, 90, 255), 2)
        elif kind == "pot":
            ax, y0 = 36 + dx, 41 + dy
            p.rect(ax - 5, y0, ax + 4, y0 + 5, (70, 60, 60, 255))
            p.line([(ax - 6, y0), (ax + 5, y0)], (110, 100, 100, 255))
            p.rect(ax - 4, y0 + 1, ax + 3, y0 + 1, (250, 220, 150, 255))
            x, y = hand_r
            p.line([(x, y), (ax - 1, y0 + 1)], (170, 120, 70, 255), 1)
        elif kind == "frog":  # 小竹做的木頭青蛙玩具
            x, y = prop[1]
            p.rect(x, y, x + 3, y + 2, (120, 186, 96, 255))
            p.px(x, y - 1, (120, 186, 96, 255)); p.px(x + 3, y - 1, (120, 186, 96, 255))
            p.px(x, y - 1, (20, 20, 20, 255))
        elif kind == "gear":
            x, y = hand_r
            x -= 3; y -= 3
            col = (190, 160, 70, 255)
            p.ell(x - 2, y - 2, x + 2, y + 2, col)
            p.px(x, y, (90, 70, 30, 255))
            for ox, oy in ((0, -3), (3, 0), (0, 3), (-3, 0)):
                p.px(x + ox, y + oy, col)
        elif kind == "cake":  # 小梅的梅花糕
            x, y = hand_r
            p.rect(x, y - 3, x + 3, y - 1, (255, 205, 215, 255))
            p.px(x + 1, y - 4, c["accent"])
        elif kind == "needle":  # 審視時指間一根銀針（千燈樓的伏筆）
            x, y = hand_r
            p.line([(x, y - 1), (x + 3, y - 4)], (210, 214, 224, 255))

    if battle:
        # 機關臂：右前臂是一整塊直立的機關板，頂端三隻爪子抓著劍柄
        brass, steel, deep = (206, 160, 70, 255), (150, 146, 136, 255), (96, 90, 84, 255)
        px0, py0, py1 = 34 + dx, 9 + rig_y, 38 + rig_y
        p.rect(px0 - 1, py0 - 1, px0 + 8, py1 + 1, OUTLINE)
        p.rect(px0, py0, px0 + 7, py1, steel)
        p.rect(px0 + 1, py0 + 8, px0 + 6, py1 - 3, deep)
        p.line([(px0 + 2, py0 + 10), (px0 + 5, py0 + 13)], steel); p.line([(px0 + 3, py0 + 16), (px0 + 5, py0 + 18)], steel)
        p.rect(px0 + 2, py1 - 1, px0 + 5, py1 + 2, OUTLINE)
        for k in range(3):
            cx = px0 + 1 + k * 3
            p.poly([(cx - 1, py0 + 1), (cx + 2, py0 + 1), (cx + 1, py0 - 4)], brass, OUTLINE)

    # 附著效果（不脫離角色本體）
    for f in pose["fx"]:
        if f == "tear":
            p.px(lx, ey + 3, (120, 180, 255, 255)); p.px(lx, ey + 4, (120, 180, 255, 255))
        elif f == "tear2":
            p.px(lx, ey + 3, (120, 180, 255, 255)); p.px(lx, ey + 4, (120, 180, 255, 255))
            p.px(rx + 1, ey + 3, (120, 180, 255, 255)); p.px(rx + 1, ey + 5, (120, 180, 255, 255))
        elif f == "sweat":
            p.px(hx + 10, hy - 2, (150, 200, 255, 255)); p.px(hx + 10, hy - 1, (150, 200, 255, 255))
            p.px(hx + 11, hy - 1, (150, 200, 255, 255))
        elif f == "spark":
            ax, y0 = 35 + dx, 41 + c["height_drop"]
            for ox, oy in ((-2, -2), (3, -3), (0, -4), (5, -1)):
                p.px(ax + ox, y0 + oy, (255, 210, 80, 255))
        elif f == "steam":
            ax, y0 = 36 + dx, 40 + dy
            p.px(ax - 2, y0 - 1, (230, 230, 240, 200)); p.px(ax - 1, y0 - 2, (230, 230, 240, 200))
            p.px(ax + 1, y0 - 1, (230, 230, 240, 200)); p.px(ax + 2, y0 - 3, (230, 230, 240, 200))
        elif f == "heart":
            x, y = hx + 9, hy - 10
            col = (240, 80, 110, 255)
            for ox, oy in ((0, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (1, 3)):
                p.px(x + ox, y + oy, col)
        elif f == "anger":  # 生氣記號，貼在頭的左上
            x, y = hx - 13, hy - 9
            col = (220, 40, 50, 255)
            for ox, oy in ((0, 1), (1, 0), (3, 0), (4, 1), (0, 3), (1, 4), (3, 4), (4, 3)):
                p.px(x + ox, y + oy, col)
        elif f == "star":  # 敲頭冒出的小星星，貼在拳頭旁
            x, y = hx + 13, hy - 9
            col = (250, 210, 70, 255)
            for ox, oy in ((1, 0), (0, 1), (1, 1), (2, 1), (1, 2)):
                p.px(x + ox, y + oy, col)
        elif f == "puff":  # 閉眼得意地「哼」一聲
            x, y = hx + 4 + look, hy + 7
            col = (245, 245, 250, 255)
            p.rect(x, y - 1, x + 2, y, col); p.px(x + 3, y - 1, col); p.px(x + 1, y - 2, col)
            p.px(x - 1, y, OUTLINE)
        elif f == "drool":
            p.px(hx + 1 + look, hy + 10, (170, 210, 255, 255)); p.px(hx + 1 + look, hy + 11, (170, 210, 255, 255))
        elif f == "chill":  # 「抖抖抖」：身體兩側的短線
            for yy in (32, 36, 40):
                p.line([(12 + dx, yy + dy), (13 + dx, yy + dy - 1)], OUTLINE)
                p.line([(35 + dx, yy + dy - 1), (36 + dx, yy + dy)], OUTLINE)
        elif f == "flowers":  # 開心時身邊冒出的小花（貼在頭的周圍）
            for fx0, fy0 in ((hx - 14, hy - 8), (hx + 13, hy - 10), (hx - 13, hy + 6), (hx + 13, hy + 4)):
                for ox, oy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
                    p.px(fx0 + ox, fy0 + oy, (240, 170, 200, 255))
                p.px(fx0, fy0, (255, 230, 150, 255))
        elif f == "q":  # 等待：頭上小問號（貼著頭頂）
            x, y = hx + 8, hy - 15
            col = (250, 200, 80, 255)
            for ox, oy in ((0, 0), (1, 0), (2, 1), (1, 2), (1, 4)):
                p.px(x + ox, y + oy, col)

    return p.img.resize((CELL_W, CELL_H), Image.NEAREST)


def mirror_row(frames):
    return [f.transpose(Image.FLIP_LEFT_RIGHT) for f in frames]


def run_row(**kw):
    run = []
    for i in range(8):
        a = i % 4
        legs = ["stepA", "pass", "stepB", "pass"][a]
        bob = [0, -1, 0, -1][a]
        arms = ("swing_f", "swing_b") if a < 2 else ("swing_b", "swing_f")
        run.append(P(facing="right", legs=legs, dy=bob, arms=arms, hair_sway=-1, **kw))
    return run


def poses_shimei():
    """小師妹：雙手交握、安靜、摺紙、輕功、鈴鐺不響、會迷路、一嚇就抖抖抖。"""
    m0 = "small"
    cl = ("clasp", "clasp")
    return {
        "idle": [P(arms=cl, mouth=m0), P(arms=cl, mouth=m0), P(arms=cl, eyes="blink", mouth=m0),
                 P(arms=cl, mouth=m0, dy=1), P(arms=cl, mouth=m0, dy=1, hair_sway=1), P(arms=cl, mouth=m0)],
        "running-right": run_row(mouth="small", eyes="open"),
        # 雙手交握、閉眼微笑，害羞地點頭
        # 依官方立繪：雙手握著鬢髮，開心得身邊冒出小花
        "waving": [P(arms=cl, mouth=m0, blush=True),
                   P(arms=("hair_hold", "hair_hold"), mouth="small", eyes="open", blush=True, fx=("flowers",)),
                   P(arms=("hair_hold", "hair_hold"), mouth="smile", eyes="happy", blush=True, fx=("flowers",), dy=-1),
                   P(arms=("hair_hold", "hair_hold"), mouth="smile", eyes="happy", blush=True, fx=("flowers",))],
        # 輕功：一躍而起，比誰都高
        "jumping": [P(dy=2, legs="crouch", arms=cl, eyes="closed", mouth=m0),
                    P(dy=-4, legs="tuck", arms=("spread", "spread"), mouth=m0),
                    P(dy=-6, legs="tuck", arms=("spread", "spread"), eyes="happy", mouth="smile"),
                    P(dy=-3, legs="stand", arms=("spread", "spread"), mouth=m0),
                    P(dy=1, legs="crouch", arms=cl, mouth="smile", eyes="happy", blush=True)],
        # 迷路／被嚇到：左看右看，然後縮著手「抖抖抖」
        "failed": [P(eyes="side", mouth="o", arms=cl, fx=("q",)),
                   P(eyes="side", mouth="o", arms=cl, fx=("q", "sweat")),
                   P(eyes="wide", mouth="o", arms=("tremble", "tremble"), fx=("sweat",)),
                   P(eyes="wide", mouth="o", arms=("tremble", "tremble"), fx=("sweat", "chill"), dx=1),
                   P(eyes="wide", mouth="o", arms=("tremble", "tremble"), fx=("chill",), dx=-1),
                   P(eyes="sad", mouth="frown", arms=("tremble", "tremble"), fx=("chill",), dx=1),
                   P(eyes="closed", mouth="frown", arms=("tremble", "tremble"), fx=("tear", "chill"), dx=-1),
                   P(eyes="sad", mouth=m0, arms=cl)],
        # 不說話，只是抬頭看著你等
        "waiting": [P(arms=cl, eyes="look_up", mouth=m0, fx=("q",)),
                    P(arms=cl, eyes="look_up", mouth=m0, fx=("q",), dy=-1),
                    P(arms=cl, eyes="blink", mouth=m0, fx=("q",)),
                    P(arms=cl, eyes="look_up", mouth=m0, fx=("q",), blush=True),
                    P(arms=cl, eyes="look_up", mouth=m0, fx=("q",), dy=-1, blush=True),
                    P(arms=cl, eyes="look_up", mouth=m0, fx=("q",))],
        # 工作中：安靜地摺紙鶴
        "running": [P(arms=("front", "front"), prop=("paper", 0), eyes="blink", mouth=m0),
                    P(arms=("front", "front"), prop=("paper", 0), eyes="open", mouth=m0),
                    P(arms=("front", "front"), prop=("paper", 1), eyes="blink", mouth=m0),
                    P(arms=("front", "front"), prop=("paper", 1), eyes="open", mouth=m0),
                    P(arms=("front", "front"), prop=("paper", 2), eyes="happy", mouth="smile"),
                    P(arms=("front", "front"), prop=("paper", 2), eyes="happy", mouth="smile", dy=-1)],
        # 捧著紙鶴端詳
        "review": [P(arms=("hold_up", "hold_up"), prop=("paper", 2), eyes="open", mouth=m0),
                   P(arms=("hold_up", "hold_up"), prop=("paper", 2), eyes="open", mouth=m0, tilt=1),
                   P(arms=("hold_up", "hold_up"), prop=("paper", 2), eyes="blink", mouth=m0, tilt=1),
                   P(arms=("hold_up", "hold_up"), prop=("paper", 2), eyes="open", mouth=m0, tilt=1),
                   P(arms=("hold_up", "hold_up"), prop=("paper", 2), eyes="happy", mouth="smile"),
                   P(arms=("hold_up", "hold_up"), prop=("paper", 2), eyes="open", mouth=m0)],
    }


def poses_longxiang():
    """龍湘：啃雞腿、拿雞腿當劍、坦率開朗又有點呆、錢包常被偷。"""
    stick = ("drumstick", "hand")
    return {
        # 站著啃雞腿
        "idle": [P(arms=("hip", "nibble"), prop=("drumstick", "mouth"), mouth="smile", eyes="happy"),
                 P(arms=("hip", "nibble"), prop=("drumstick", "mouth"), mouth="smile", eyes="happy", dy=1),
                 P(arms=("hip", "hold"), prop=stick, mouth="cat", eyes="open"),
                 P(arms=("hip", "hold"), prop=stick, mouth="cat", eyes="blink"),
                 P(arms=("hip", "nibble"), prop=("drumstick", "mouth"), mouth="smile", eyes="happy"),
                 P(arms=("hip", "hold"), prop=stick, mouth="smile", eyes="open")],
        "running-right": run_row(mouth="grin", eyes="open"),
        # 舉著雞腿大力揮手
        "waving": [P(arms=("hip", "wave_mid"), prop=stick, mouth="laugh", eyes="happy"),
                   P(arms=("hip", "wave_up"), prop=stick, mouth="grin", eyes="happy"),
                   P(arms=("hip", "wave_mid"), prop=stick, mouth="laugh", eyes="happy"),
                   P(arms=("hip", "wave_up"), prop=stick, mouth="grin", eyes="open")],
        # 以雞腿為劍：躍起直刺
        "jumping": [P(dy=2, legs="crouch", arms=("hip", "hold"), prop=stick, eyes="closed", mouth="flat"),
                    P(dy=-3, legs="tuck", arms=("spread", "wave_up"), prop=stick, eyes="wide", mouth="open"),
                    P(dy=-5, legs="tuck", arms=("spread", "thrust"), prop=stick, eyes="wide", mouth="grin"),
                    P(dy=-2, legs="stand", arms=("spread", "thrust"), prop=stick, eyes="open", mouth="grin"),
                    P(dy=1, legs="crouch", arms=("hip", "nibble"), prop=("drumstick", "mouth"), eyes="happy", mouth="smile")],
        # 錢包又被偷了：摸摸腰間、空空如也、哭
        "failed": [P(arms=("hip", "hip"), eyes="open", mouth="smile"),
                   P(arms=("hip", "belly"), eyes="wide", mouth="o"),
                   P(arms=("belly", "belly"), eyes="wide", mouth="o", fx=("sweat",)),
                   P(arms=("face", "face"), eyes="sad", mouth="frown", fx=("sweat",)),
                   P(arms=("face", "face"), eyes="closed", mouth="frown", fx=("tear2",)),
                   P(arms=("droop", "droop"), eyes="sad", mouth="frown", fx=("tear2",), dy=1),
                   P(arms=("droop", "droop"), eyes="sad", mouth="frown", dy=1),
                   P(arms=("hip", "hip"), eyes="open", mouth="flat")],
        # 肚子餓：摸肚子、流口水看著你
        "waiting": [P(arms=("belly", "belly"), eyes="look_up", mouth="o", fx=("q",)),
                    P(arms=("belly", "belly"), eyes="look_up", mouth="o", fx=("q", "drool"), dy=-1),
                    P(arms=("belly", "belly"), eyes="look_up", mouth="cat", fx=("q", "drool")),
                    P(arms=("belly", "belly"), eyes="blink", mouth="cat", fx=("q",)),
                    P(arms=("belly", "belly"), eyes="look_up", mouth="o", fx=("q", "drool"), dy=-1),
                    P(arms=("belly", "belly"), eyes="look_up", mouth="o", fx=("q",))],
        # 工作中：認真練劍
        "running": [P(arms=("hip", "hold"), prop=("sword", "up"), eyes="squint", mouth="flat"),
                    P(arms=("hip", "thrust"), prop=("sword", "thrust"), eyes="wide", mouth="open", dx=1),
                    P(arms=("hip", "thrust"), prop=("sword", "thrust"), eyes="squint", mouth="flat", dx=1),
                    P(arms=("hip", "hold"), prop=("sword", "up"), eyes="squint", mouth="flat"),
                    P(arms=("hip", "thrust"), prop=("sword", "thrust"), eyes="wide", mouth="open", dx=1),
                    P(arms=("hip", "hold"), prop=("sword", "up"), eyes="open", mouth="grin")],
        # 想事情：歪頭、問號，有點呆
        "review": [P(arms=("hip", "chin"), eyes="look_up", mouth="flat"),
                   P(arms=("hip", "chin"), eyes="look_up", mouth="o", tilt=1, fx=("q",)),
                   P(arms=("hip", "chin"), eyes="blink", mouth="o", tilt=1, fx=("q",)),
                   P(arms=("hip", "chin"), eyes="look_up", mouth="flat", tilt=1, fx=("q",)),
                   P(arms=("hip", "chin"), eyes="happy", mouth="grin"),
                   P(arms=("hip", "chin"), eyes="open", mouth="flat")],
    }


def poses_xiahoulan():
    """夏侯蘭：撐油紙傘、冷淡無神、「懶徒兒，跟我來」、用袖子遮臉、不屑。"""
    m0 = "flat"
    um = ("umbrella",)
    return {
        "idle": [P(arms=("down", "umbrella"), prop=um, mouth=m0),
                 P(arms=("down", "umbrella"), prop=um, mouth=m0),
                 P(arms=("down", "umbrella"), prop=um, eyes="closed", mouth=m0),
                 P(arms=("down", "umbrella"), prop=um, mouth=m0, dy=1),
                 P(arms=("down", "umbrella"), prop=um, mouth=m0, dy=1, hair_sway=1),
                 P(arms=("down", "umbrella"), prop=um, mouth=m0)],
        "running-right": run_row(mouth="flat", eyes="dull"),
        # 撐著傘伸手示意：「懶徒兒，跟我來。」
        "waving": [P(arms=("beckon", "umbrella"), prop=um, mouth=m0),
                   P(arms=("beckon_in", "umbrella"), prop=um, mouth="smirk"),
                   P(arms=("beckon", "umbrella"), prop=um, mouth=m0, eyes="closed"),
                   P(arms=("beckon_in", "umbrella"), prop=um, mouth="smirk")],
        # 難得的驚訝與害羞：用袖子遮臉
        "jumping": [P(arms=("down", "umbrella"), prop=um, eyes="dull", mouth=m0),
                    P(dy=-3, legs="tuck", arms=("sleeve_face", "umbrella"), prop=um, eyes="wide", mouth="o", blush=True),
                    P(dy=-4, legs="tuck", arms=("sleeve_face", "umbrella"), prop=um, eyes="wide", mouth="o", blush=True),
                    P(dy=-1, legs="stand", arms=("sleeve_face", "umbrella"), prop=um, eyes="side", mouth="small", blush=True),
                    P(arms=("down", "umbrella"), prop=um, eyes="side", mouth="flat", blush=True)],
        # 不悅：嘆氣，用袖子遮住半張臉
        "failed": [P(arms=("down", "umbrella"), prop=um, eyes="dull", mouth=m0),
                   P(arms=("down", "umbrella"), prop=um, eyes="closed", mouth="o"),
                   P(arms=("sleeve_face", "umbrella"), prop=um, eyes="closed", mouth="frown"),
                   P(arms=("sleeve_face", "umbrella"), prop=um, eyes="closed", mouth="frown", dy=1),
                   P(arms=("sleeve_face", "umbrella"), prop=um, eyes="sad", mouth="frown", dy=1),
                   P(arms=("sleeve_face", "umbrella"), prop=um, eyes="dull", mouth="frown"),
                   P(arms=("down", "umbrella"), prop=um, eyes="closed", mouth=m0),
                   P(arms=("down", "umbrella"), prop=um, eyes="dull", mouth=m0)],
        # 撐著傘斜眼，不耐煩地等你
        "waiting": [P(arms=("down", "umbrella"), prop=um, eyes="side", mouth=m0, fx=("q",)),
                    P(arms=("down", "umbrella"), prop=um, eyes="side", mouth=m0, fx=("q",), dy=1),
                    P(arms=("down", "umbrella"), prop=um, eyes="side", mouth=m0, fx=("q",)),
                    P(arms=("down", "umbrella"), prop=um, eyes="closed", mouth=m0, fx=("q",), dy=1),
                    P(arms=("down", "umbrella"), prop=um, eyes="side", mouth="smirk", fx=("q",)),
                    P(arms=("down", "umbrella"), prop=um, eyes="dull", mouth=m0, fx=("q",))],
        # 工作中：收起傘，示範奪魄門掌法
        "running": [P(arms=("cross", "cross"), eyes="dull", mouth=m0),
                    P(arms=("hip", "thrust"), eyes="squint", mouth=m0, dx=1),
                    P(arms=("hip", "thrust"), eyes="squint", mouth="open", dx=1),
                    P(arms=("thrust", "hip"), eyes="squint", mouth=m0, dx=-1),
                    P(arms=("thrust", "hip"), eyes="squint", mouth="open", dx=-1),
                    P(arms=("cross", "cross"), eyes="dull", mouth="smirk")],
        # 不屑：撐傘斜眼，冷冷一笑
        "review": [P(arms=("down", "umbrella"), prop=um, eyes="dull", mouth=m0),
                   P(arms=("down", "umbrella"), prop=um, eyes="side", mouth=m0, tilt=1),
                   P(arms=("down", "umbrella"), prop=um, eyes="side", mouth="smirk", tilt=1),
                   P(arms=("down", "umbrella"), prop=um, eyes="closed", mouth="smirk", tilt=1),
                   P(arms=("down", "umbrella"), prop=um, eyes="squint", mouth=m0),
                   P(arms=("down", "umbrella"), prop=um, eyes="dull", mouth=m0)],
    }


CUSTOM_POSES = {"xiaoshimei": poses_shimei, "longxiang": poses_longxiang, "xiahoulan": poses_xiahoulan}


def poses_for(cid):
    if cid in CUSTOM_POSES:
        return CUSTOM_POSES[cid]()
    mei = cid == "xiaomei"
    rows = {}
    # 0 idle：呼吸與眨眼
    m0 = "smile" if mei else "small"  # 小竹平常微張著嘴、有點害羞
    rows["idle"] = [
        P(mouth=m0), P(mouth=m0), P(eyes="blink", mouth=m0), P(dy=1, mouth=m0),
        P(dy=1, hair_sway=1, mouth=m0), P(mouth=m0),
    ]
    if mei:  # 小梅站著時雙手背在身後
        for f_ in rows["idle"]:
            f_["arms"] = ("behind", "behind")
    # 1 running-right
    run = []
    for i in range(8):
        a = i % 4
        legs = ["stepA", "pass", "stepB", "pass"][a]
        bob = [0, -1, 0, -1][a]
        arms = ("swing_f", "swing_b") if a < 2 else ("swing_b", "swing_f")
        run.append(P(facing="right", legs=legs, dy=bob, arms=arms, dx=0,
                     mouth="grin" if mei else "flat", hair_sway=-1,
                     eyes="open" if mei else "squint"))
    rows["running-right"] = run
    # 3 waving
    if mei:
        # 鶴手：抬手、手腕下彎、指尖朝下
        rows["waving"] = [
            P(arms=("behind", "crane_mid"), mouth="open", eyes="open", hair_sway=1),
            P(arms=("behind", "crane"), mouth="smile", eyes="happy"),
            P(arms=("behind", "crane"), mouth="cat", eyes="wink", hair_sway=1),
            P(arms=("behind", "crane_mid"), mouth="smile", eyes="happy"),
        ]
    else:
        rows["waving"] = [
            P(arms=("down", "wave_mid"), mouth="open", eyes="squint"),
            P(arms=("down", "wave_up"), mouth="grin", eyes="open", blush=True),
            P(arms=("down", "wave_mid"), mouth="open", eyes="open"),
            P(arms=("down", "wave_up"), mouth="smile", eyes="open", blush=True),
        ]
    # 4 jumping：預備、起跳、頂點、落下、站穩
    if mei:
        # 招牌飛踢：蹲、躍起、側踢（一手前推、一手握拳）、落地
        rows["jumping"] = [
            P(dy=2, legs="crouch", arms=("hip", "hip"), eyes="closed", mouth="flat"),
            P(dy=-4, legs="tuck", arms=("fist_side", "fist_side"), mouth="open", eyes="open", hair_sway=1),
            P(dy=-5, legs="kick", arms=("fist_side", "spread"), mouth="open", eyes="wide", hair_sway=2),
            P(dy=-4, legs="kick", arms=("fist_side", "spread"), mouth="grin", eyes="open", hair_sway=2),
            P(dy=1, legs="crouch", arms=("behind", "behind"), mouth="smile", eyes="happy", fx=("heart",)),
        ]
    else:
        # 依官方圖：一手握拳、一手高舉大鐵鎚，張嘴大喊
        rows["jumping"] = [
            P(dy=2, legs="crouch", arms=("hip", "hammer_down"), prop=("hammer", "down"), eyes="closed", mouth="flat"),
            P(dy=-3, legs="tuck", arms=("up", "fist_up"), prop=("hammer", "up"), eyes="wide", mouth="open"),
            P(dy=-6, legs="tuck", arms=("up", "fist_up"), prop=("hammer", "up"), eyes="wide", mouth="open", fx=("anger",)),
            P(dy=-2, legs="stand", arms=("up", "fist_up"), prop=("hammer", "up"), eyes="wide", mouth="open", fx=("anger",)),
            P(dy=1, legs="crouch", arms=("hip", "hammer_down"), prop=("hammer", "down"), eyes="drowsy", mouth="small"),
        ]
    # 5 failed
    if mei:
        # 搞砸了就眨眼吐舌、握拳敲頭（小梅的招牌裝傻）
        rows["failed"] = [
            P(eyes="wide", mouth="o", arms=("behind", "behind")),
            P(eyes="wide", mouth="o", arms=("behind", "behind"), fx=("sweat",)),
            P(eyes="wink", mouth="tongue", arms=("hip", "bonk"), tilt=1),
            P(eyes="wink", mouth="tongue", arms=("hip", "bonk"), tilt=1, fx=("star",)),
            P(eyes="wink", mouth="tongue", arms=("hip", "bonk"), tilt=1, dy=-1),
            P(eyes="wink", mouth="tongue", arms=("hip", "bonk"), tilt=1, fx=("star",)),
            P(eyes="happy", mouth="smile", arms=("hip", "bonk"), tilt=1),
            P(eyes="open", mouth="smile", arms=("behind", "behind")),
        ]
    else:
        rows["failed"] = [
            P(arms=("down", "hammer_down"), prop=("hammer", "down"), eyes="wide", mouth="o"),
            P(arms=("down", "hammer_down"), prop=("hammer", "down"), eyes="wide", mouth="o", fx=("sweat",)),
            P(arms=("droop", "droop"), eyes="sad", mouth="frown", dy=1, fx=("sweat",)),
            P(arms=("droop", "droop"), eyes="sad", mouth="frown", dy=2, tilt=1),
            P(arms=("droop", "droop"), eyes="closed", mouth="frown", dy=2, tilt=1, fx=("tear2",)),
            P(arms=("droop", "droop"), eyes="sad", mouth="frown", dy=2, tilt=1, fx=("tear2",)),
            P(arms=("droop", "droop"), eyes="sad", mouth="flat", dy=2, tilt=1),
            P(arms=("down", "down"), eyes="squint", mouth="flat", dy=1),
        ]
    # 6 waiting：期待你點頭
    if mei:
        # 雙手背在身後、臉紅冒汗地斜眼看你，等你回答
        rows["waiting"] = [
            P(arms=("behind", "behind"), eyes="side", mouth="smile", blush=True, fx=("q",)),
            P(arms=("behind", "behind"), eyes="side", mouth="smile", blush=True, fx=("q", "sweat"), dy=-1),
            P(arms=("behind", "behind"), eyes="side", mouth="cat", blush=True, fx=("q", "sweat")),
            P(arms=("behind", "behind"), eyes="blink", mouth="smile", blush=True, fx=("q",)),
            P(arms=("behind", "behind"), eyes="open", mouth="smile", blush=True, fx=("q",), dy=-1),
            P(arms=("behind", "behind"), eyes="side", mouth="smile", blush=True, fx=("q",)),
        ]
    else:
        rows["waiting"] = [
            P(arms=("front", "hold"), prop=("frog", (32, 37)), eyes="squint", mouth="flat", fx=("q",)),
            P(arms=("front", "hold"), prop=("frog", (32, 36)), eyes="open", mouth="flat", fx=("q",), dy=-1),
            P(arms=("front", "hold"), prop=("frog", (32, 34)), eyes="open", mouth="o", fx=("q",)),
            P(arms=("front", "hold"), prop=("frog", (32, 36)), eyes="blink", mouth="flat", fx=("q",)),
            P(arms=("front", "hold"), prop=("frog", (32, 37)), eyes="squint", mouth="smile", fx=("q",), blush=True),
            P(arms=("front", "hold"), prop=("frog", (32, 37)), eyes="squint", mouth="flat", fx=("q",)),
        ]
    # 7 running（工作中）：小梅做菜、小竹打鐵
    if mei:
        rows["running"] = [
            P(arms=("front", "stir_a"), prop=("pot",), eyes="happy", mouth="smile", fx=("steam",)),
            P(arms=("front", "stir_b"), prop=("pot",), eyes="happy", mouth="cat", dy=-1),
            P(arms=("front", "stir_a"), prop=("pot",), eyes="open", mouth="smile", fx=("steam",)),
            P(arms=("front", "stir_b"), prop=("pot",), eyes="happy", mouth="smile", dy=-1),
            P(arms=("front", "stir_a"), prop=("pot",), eyes="blink", mouth="cat", fx=("steam",)),
            P(arms=("front", "stir_b"), prop=("pot",), eyes="happy", mouth="smile", dy=-1),
        ]
    else:
        rows["running"] = [
            P(arms=("front", "hammer_up"), prop=("hammer", "up"), eyes="squint", mouth="flat", dy=-1),
            P(arms=("front", "hammer_up"), prop=("hammer", "up"), eyes="squint", mouth="flat", dy=-2),
            P(arms=("front", "hammer_down"), prop=("hammer", "down"), eyes="closed", mouth="grin", fx=("spark",)),
            P(arms=("front", "hammer_down"), prop=("hammer", "down"), eyes="squint", mouth="flat"),
            P(arms=("hip", "wipe"), eyes="closed", mouth="open", fx=("sweat",)),
            P(arms=("hip", "wipe"), eyes="happy", mouth="laugh", fx=("sweat",)),
        ]
        # 打鐵時加上鐵砧（畫在同一格內）
        for f in rows["running"]:
            f["fx"] = tuple(f["fx"])
            f["anvil"] = True
    # 8 review：小梅瞇眼打量（指間銀針）、小竹湊近看齒輪
    if mei:
        # 閉眼「哼」一聲，再瞇眼打量（指間閃過銀針）
        rows["review"] = [
            P(arms=("behind", "chin"), eyes="open", mouth="flat"),
            P(arms=("behind", "behind"), eyes="closed", mouth="smirk", fx=("puff",)),
            P(arms=("behind", "behind"), eyes="closed", mouth="smirk", fx=("puff",), dy=-1),
            P(arms=("behind", "hold"), prop=("needle",), eyes="squint", mouth="smirk", tilt=1),
            P(arms=("behind", "hold"), prop=("needle",), eyes="wink", mouth="smirk", tilt=1),
            P(arms=("behind", "chin"), eyes="open", mouth="smile"),
        ]
    else:
        rows["review"] = [
            P(arms=("down", "hold"), prop=("gear",), eyes="squint", mouth="flat"),
            P(arms=("down", "hold"), prop=("gear",), eyes="squint", mouth="flat", tilt=1, dy=1),
            P(arms=("brow", "hold"), prop=("gear",), eyes="squint", mouth="o", tilt=2, dy=1),
            P(arms=("brow", "hold"), prop=("gear",), eyes="blink", mouth="o", tilt=2, dy=1),
            P(arms=("down", "hold"), prop=("gear",), eyes="open", mouth="smile", tilt=1),
            P(arms=("down", "hold"), prop=("gear",), eyes="squint", mouth="flat"),
        ]
    return rows


def render_rows(cid):
    rows = poses_for(cid)
    out = {}
    for state, durations in ROW_SPEC:
        if state == "running-left":
            continue
        frames = []
        for pose in rows[state]:
            img = draw_frame(cid, pose)
            if pose.get("anvil") and not CHARACTERS[cid].get("battle"):
                # 鐵砧墊在角色後方：另畫一張再疊上
                anvil = draw_anvil(cid, glowing="spark" in pose["fx"])
                base = Image.new("RGBA", img.size, (0, 0, 0, 0))
                base.alpha_composite(anvil)
                base.alpha_composite(img)
                img = base
            frames.append(img)
        assert len(frames) == len(durations), (cid, state, len(frames))
        out[state] = frames
    out["running-left"] = mirror_row(out["running-right"])
    if CHARACTERS[cid].get("battle"):
        # 畫的時候武器在畫面右邊；小竹是右手持武器、左手持盾，
        # 正面看武器應在畫面左邊，所以整格鏡像，左右跑的兩列對調
        out = {k: mirror_row(v) for k, v in out.items()}
        out["running-right"], out["running-left"] = out["running-left"], out["running-right"]
    return out


def draw_anvil(cid, glowing):
    c = CHARACTERS[cid]
    p = Painter(c)
    ax, y0 = 37, 43
    p.rect(ax - 4, y0, ax + 6, y0 + 2, (96, 100, 112, 255))
    p.line([(ax - 4, y0), (ax + 6, y0)], (150, 154, 166, 255))
    p.rect(ax - 1, y0 + 3, ax + 3, y0 + 5, (72, 76, 88, 255))
    p.rect(ax - 3, y0 + 6, ax + 5, y0 + 7, (72, 76, 88, 255))
    if glowing:
        p.rect(ax, y0 - 1, ax + 3, y0 - 1, (255, 150, 60, 255))
    return p.img.resize((CELL_W, CELL_H), Image.NEAREST)


def build(cid, preview=False):
    rows = render_rows(cid)
    atlas = Image.new("RGBA", (CELL_W * COLS, CELL_H * ROWS), (0, 0, 0, 0))
    for r, (state, _) in enumerate(ROW_SPEC):
        for col, frame in enumerate(rows[state]):
            atlas.alpha_composite(frame, (col * CELL_W, r * CELL_H))
    pet_dir = ROOT / "codex" / "pets" / cid
    pet_dir.mkdir(parents=True, exist_ok=True)
    atlas.save(pet_dir / "spritesheet.webp", "WEBP", lossless=True, quality=100)
    c = CHARACTERS[cid]
    manifest = {
        "id": cid,
        "displayName": c["displayName"],
        "description": c["description"],
        "spritesheetPath": "spritesheet.webp",
    }
    (pet_dir / "pet.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if preview:
        qa = ROOT / "codex" / "qa"
        qa.mkdir(parents=True, exist_ok=True)
        sheet = Image.new("RGBA", atlas.size, (236, 228, 212, 255))
        sheet.alpha_composite(atlas)
        sheet.convert("RGB").save(qa / f"{cid}-contact-sheet.png")
        for state, durations in ROW_SPEC:
            frames = []
            for f in rows[state]:
                bg = Image.new("RGBA", f.size, (236, 228, 212, 255))
                bg.alpha_composite(f)
                frames.append(bg.convert("RGB"))
            frames[0].save(qa / f"{cid}-{state}.gif", save_all=True, append_images=frames[1:],
                           duration=durations, loop=0)
    return pet_dir


if __name__ == "__main__":
    preview = "--preview" in sys.argv
    for cid in CHARACTERS:
        print("built", build(cid, preview).relative_to(ROOT))

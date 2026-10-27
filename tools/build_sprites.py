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
    "blush": (255, 186, 190, 255), "blush_always": True,  # 臉上淡淡的腮紅
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

CHARACTERS["yeyunshang"] = {
    "displayName": "葉雲裳",
    "description": "點蒼明珠葉雲裳，葉雲舟的胞妹：俏皮愛搗蛋的小惡魔，盛夏也裹著貂裘斗篷，鬧不到半天就發燒倒下。（活俠傳同人）",
    # 依 LoM Wiki 立繪：深棕中分瀏海、頭頂雙小髻配紅花與紅緞帶、胸前低雙馬尾（綠繩）、
    # 珊瑚色斗篷配白毛領、粉紅領結、豆綠長裙、紅色細腰帶
    "hair": (62, 42, 38, 255), "hair_hi": (110, 82, 72, 255),
    "skin": (255, 234, 222, 255), "skin_sh": (240, 200, 184, 255),
    "eye": (96, 80, 74, 255),
    "cloth": (152, 184, 152, 255), "cloth_sh": (118, 150, 120, 255),
    "accent": (152, 184, 152, 255), "accent_sh": (118, 150, 120, 255),
    "collar": (250, 250, 248, 255),
    "sash": (176, 60, 52, 255),
    "sleeve": (236, 236, 244, 255),
    "cape": (226, 132, 112, 255), "cape_sh": (186, 98, 84, 255),
    "fur": (236, 236, 232, 255), "fur_sh": (186, 186, 182, 255),
    "flower": (214, 60, 70, 255), "tie": (90, 150, 110, 255),
    "shoe": (176, 60, 52, 255), "leg": (236, 236, 244, 255),
    "blush": (255, 160, 160, 255), "blush_always": True,
    "outfit": "dress", "head": "twin", "thin_sash": True,
    "long_hair": False, "height_drop": 2, "default_eyes": "open",
}

CHARACTERS["weiju"] = {
    "displayName": "魏菊",
    "description": "崆峒玄功門的當代掌門魏菊：儀態端莊、知書達禮，文靜秀麗、與崆峒派格格不入的奇女子；手裡總捧著郁竹打造的手爐。（活俠傳同人）",
    # 依 LoM Wiki 立繪：長髮往後梳露出額頭、頭頂盤髻插金簪、側邊淺藍髮帶；
    # 白色內衣淺藍交領、黃色寬袖外袍、橙黃長裙配藍色腰帶，雙手捧著深綠手爐
    "hair": (52, 48, 50, 255), "hair_hi": (96, 90, 92, 255),
    "skin": (255, 238, 228, 255), "skin_sh": (240, 206, 190, 255),
    "eye": (86, 80, 74, 255),
    "cloth": (250, 248, 238, 255), "cloth_sh": (222, 216, 200, 255),
    "accent": (234, 172, 74, 255), "accent_sh": (204, 140, 50, 255),
    "collar": (124, 176, 196, 255),
    "sash": (110, 158, 180, 255),
    "robe": (240, 202, 96, 255), "robe_sh": (214, 170, 66, 255),
    "sleeve": (240, 202, 96, 255), "wide_sleeves": True,
    "pin": (214, 168, 60, 255), "ribbon": (150, 196, 214, 255),
    "shoe": (110, 158, 180, 255), "leg": (250, 248, 238, 255),
    "blush": (255, 160, 160, 255),
    "outfit": "dress", "head": "updo", "topknot": True,
    "long_hair": True, "height_drop": -1, "tall": 1, "default_eyes": "open",
}

CHARACTERS["shangguanying"] = {
    "displayName": "上官螢",
    "description": "福州上官世家的獨女上官螢：驕傲好強的千金名媛，年紀輕輕便代父操持家業；嘴上不饒人，被說中心事就臉紅。（活俠傳同人）",
    # 依 LoM Wiki 立繪：深灰綠長髮往後梳、盤髻插著掛紫晶的金簪、腦後紅髮帶；
    # 白色立領內衣配米金交領、紫色寬袖外袍與白毛袖口、粉紫長裙，一手叉腰
    "hair": (58, 64, 58, 255), "hair_hi": (112, 124, 108, 255),
    "skin": (255, 236, 226, 255), "skin_sh": (240, 204, 190, 255),
    "eye": (96, 64, 56, 255), "lid": (40, 30, 34, 255),
    "cloth": (124, 88, 164, 255), "cloth_sh": (94, 64, 132, 255),
    "accent": (206, 128, 176, 255), "accent_sh": (172, 96, 146, 255),
    "collar": (214, 190, 140, 255), "kerchief": (246, 244, 242, 255), "kerchief_sh": (214, 190, 140, 255),  # 白色立領內衣、金色盤扣
    "sash": (226, 170, 200, 255), "thin_sash": True,
    "robe": (124, 88, 164, 255), "robe_sh": (94, 64, 132, 255),
    "sleeve": (124, 88, 164, 255), "wide_sleeves": True,
    "bracer": (240, 238, 234, 255),  # 寬袖口的白色毛邊
    "pin": (214, 176, 84, 255), "ribbon": (196, 44, 56, 255),
    "shoe": (124, 88, 164, 255), "leg": (246, 244, 242, 255),
    "blush": (255, 150, 170, 255),
    "outfit": "dress", "head": "updo", "topknot": True, "swept_back": True,
    "long_hair": True, "height_drop": -1, "tall": 1, "default_eyes": "open",
}

CHARACTERS["tangbuyi"] = {
    "displayName": "大師兄",
    "description": "唐門大師兄唐布衣，人稱「飛俠」：爽朗不羈、暗器輕功當世一流，指間轉著金錢鏢、哼著小調，夢想是退隱江湖說相聲。（活俠傳同人・番外）",
    # 依使用者提供的像素參考圖逐格描成底圖（tools/ref/tangbuyi_base.png）：
    # 蓬亂深棕髮、大呆毛、後腦金繩低綁的馬尾、劍眉；青藍交領長袍、白內領、胸前金十字、
    # 玉珮紅流蘇、金邊下襬、棕色袖套、黑長靴。表情與手臂依動作在底圖上重畫。
    "bitmap": "tools/ref/tangbuyi_base.png",
    "skin": (246, 214, 192, 255), "outline": (26, 32, 56, 255),
    "sleeve": (84, 106, 152, 255), "bracer": (104, 64, 44, 255), "gold": (206, 170, 90, 255),
    "eye": (34, 20, 26, 255), "iris": (150, 50, 40, 255), "mouth": (130, 30, 34, 255),
    "default_eyes": "open", "height_drop": 0,
}

CHARACTERS["zhaohuo"] = {
    "displayName": "趙活",
    "description": "活俠傳的主角趙活：在唐門打雜的外姓弟子，人稱「唐門醜俠」；自戀、嘴砲又賤，偷雞蛋只敢偷一顆，夢想有天當上大俠。（活俠傳同人・番外）",
    # 依網友提供的像素參考圖畫成 Q 版底圖（tools/ref/make_zhaohuo_base.py）：
    # 層次蓬鬆的深棕短髮帶淺色挑染、兩側髮尾外翹；青藍交領布衣、藍腰帶、開衩衣襬、燈籠褲、靴子、紅褐護腕。
    # 表情與手臂依動作在底圖上重畫，咧嘴時露出缺一顆的門牙
    "bitmap": "tools/ref/zhaohuo_base.png", "bitmap_noarms": "tools/ref/zhaohuo_noarms.png",
    "bm_face_clear": [], "bm_brows": "thin", "bm_mouth": "teeth",
    "bm_shoulders": ((19, 33), (29, 33)), "bm_feet": ((18, 23), (26, 31)),
    "skin": (240, 206, 178, 255), "outline": (34, 24, 30, 255),
    "sleeve": (88, 114, 136, 255), "bracer": (134, 66, 54, 255),
    "eye": (40, 28, 30, 255), "iris": (70, 46, 40, 255), "brow": (96, 62, 50, 255),
    "mouth": (150, 52, 48, 255), "blush": (236, 150, 140, 255),
    "default_eyes": "drowsy", "height_drop": 0,
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
    "cheek": ((-2, -8), (2, -8)),  # 一手撫著臉頰外側（趙活的自戀）
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
    "ribbon": ((4, -3), (-4, -3)),  # 葉雲裳：雙手捏著胸前的領結緞帶
    "cape_open": ((-7, -4), (7, -4)),  # 雙手抓著斗篷往兩邊張開
    "cradle": ((5, 4), (-5, 4)),  # 雙手捧著手爐
    "mouth_cover": ((6, -9), (-5, -6)),  # 一手摀嘴、一手舉在胸前（摀嘴的手在畫完臉之後補上）
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
    if "bitmap" in c:
        return draw_bitmap_frame(c, pose).resize((CELL_W, CELL_H), Image.NEAREST)
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
    elif c.get("head") == "short":
        # 趙活：短髮，腦後隨手紮一小撮馬尾
        p.ell(hx - 11, hy - 12, hx + 11, hy + 6, c["hair"], OUTLINE)
        k = -1 if face_r else 1
        bx0 = hx + 9 * k
        p.poly([(bx0, hy - 6), (bx0 + 3 * k, hy - 7), (bx0 + 6 * k + sway * k, hy - 1),
                (bx0 + 5 * k + sway * 2 * k, hy + 5), (bx0 + 2 * k + sway * k, hy + 1)], c["hair"], OUTLINE)
        p.line([(bx0 + 3 * k, hy - 4), (bx0 + 4 * k + sway * k, hy + 1)], c["hair_hi"])
    elif c.get("head") == "twin":
        # 葉雲裳：頭頂兩側的小髻
        p.ell(hx - 12, hy - 12, hx + 12, hy + 9, c["hair"], OUTLINE)
        for bx_ in (hx - 8, hx + 8):
            p.ell(bx_ - 3, hy - 15, bx_ + 3, hy - 9, c["hair"], OUTLINE)
            p.px(bx_ - 1, hy - 13, c["hair_hi"])
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

    if "cape" in c:
        # 珊瑚色斗篷從肩膀披到小腿，從身體兩側露出來
        p.poly([(17 + dx, 31 + dy), (31 + dx, 31 + dy), (36 + dx, 47 + dy), (12 + dx, 47 + dy)], c["cape"], OUTLINE)
        p.line([(15 + dx, 38 + dy), (13 + dx, 46 + dy)], c["cape_sh"])
        p.line([(33 + dx, 38 + dy), (35 + dx, 46 + dy)], c["cape_sh"])

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
        if "robe" in c:
            for side in (-1, 1):
                x_in, x_out = 24 + dx + 3 * side, 24 + dx + 9 * side
                p.poly([(x_in, 33 + dy), (24 + dx + 5 * side, 33 + dy), (x_out + flare + side, hem),
                        (x_in + 2 * side + flare, hem)], c["robe"], OUTLINE)
                p.line([(x_in + side, 35 + dy), (x_in + 3 * side + flare, hem - 1)], c["robe_sh"])
        col = c.get("collar", c["accent_sh"])
        p.line([(21 + dx, 33 + dy), (24 + dx, 37 + dy)], col)
        p.line([(27 + dx, 33 + dy), (24 + dx, 37 + dy)], col)
        sw = 1 if c.get("waist") else 0  # 細腰的腰帶窄一點
        if c.get("thin_sash"):  # 葉雲裳：紅色細腰帶，打結後兩條帶子垂下
            p.line([(18 + dx, 39 + dy), (30 + dx, 39 + dy)], c["sash"])
            p.line([(23 + dx, 40 + dy), (22 + dx + flare, 46 + dy)], c["sash"])
            p.line([(25 + dx, 40 + dy), (26 + dx + flare, 45 + dy)], c["sash"])
        else:
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
    elif c.get("outfit") == "tunic":
        # 趙活：交領布衣（淺色內領、藍色滾邊）、藍腰帶，衣襬到膝蓋，底下露出褲管
        hem = 44 + dy
        p.poly([(18 + dx, 39 + dy), (30 + dx, 39 + dy), (31 + dx + flare, hem), (17 + dx + flare, hem)], c["cloth"], OUTLINE)
        p.line([(24 + dx, 41 + dy), (25 + dx + flare, hem - 1)], c["cloth_sh"])  # 衣襟交疊
        p.line([(22 + dx, 33 + dy), (24 + dx, 36 + dy)], c["collar"])
        p.line([(26 + dx, 33 + dy), (24 + dx, 36 + dy)], c["collar"])
        p.line([(21 + dx, 33 + dy), (25 + dx, 38 + dy)], c["trim"])  # 藍色滾邊斜過胸前
        p.line([(27 + dx, 33 + dy), (26 + dx, 35 + dy)], c["trim"])
        p.rect(18 + dx, 38 + dy, 30 + dx, 40 + dy, c["sash"])
        p.line([(28 + dx, 40 + dy), (29 + dx + flare, 43 + dy)], c["sash"])
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
    if c.get("head") in ("locks", "short"):
        # 小師妹、趙活：側分、露出額頭，不畫整排瀏海
        p.d.chord([hx - 11, hy - 13, hx + 11, hy - 1], 180, 360, fill=hair, outline=OUTLINE)
        if c.get("head") == "short":  # 趙活的短鬢角
            p.rect(hx - 11, hy - 4, hx - 9, hy + 4, hair)
            p.rect(hx + 9, hy - 4, hx + 11, hy + 4, hair)
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
        # 鬢髮一部分順著肩膀垂到胸前（分線那側較長）
        for side in (-1, 1):
            x0 = hx + 10 * side
            end = 19 if side == -k else 16
            p.poly([(x0 - side, hy - 3), (x0 + side * 2, hy - 2), (x0 + side * 2, hy + 10),
                    (x0 - side, hy + end), (x0 - side * 3, hy + end - 2), (x0 - side * 2, hy + 3)], hair, OUTLINE)
            p.line([(x0, hy + 4), (x0 - side, hy + end - 3)], c["hair_hi"])
    elif c.get("head") == "ribbon":
        # 頭頂髮髻插著青色髮簪，簪尾垂著青色髮帶
        k = -1 if face_r else 1
        p.line([(hx - 2 * k, hy - 12), (hx + 5 * k, hy - 14)], OUTLINE, 3)
        p.line([(hx - 2 * k, hy - 12), (hx + 5 * k, hy - 14)], c["ribbon"], 1)
        p.line([(hx + 5 * k, hy - 12), (hx + 8 * k, hy - 6)], c["ribbon"])
        p.rect(hx - 11, hy - 2, hx - 9, hy + 10, hair)
        p.rect(hx + 9, hy - 2, hx + 11, hy + 10, hair)
    elif c.get("head") == "short":
        # 趙活：額前一撮頭髮翹起來往旁邊甩
        k = -1 if face_r else 1
        p.poly([(hx + 2 * k, hy - 6), (hx - 3 * k, hy - 3), (hx - 8 * k, hy + 1), (hx - 7 * k, hy - 2), (hx - 3 * k, hy - 6)], hair, OUTLINE)
        p.line([(hx, hy - 5), (hx - 6 * k, hy - 1)], c["hair_hi"])
    elif c.get("head") == "updo":
        # 長髮往後梳、額頭露出來：只留髮際線，兩側長髮順著臉頰垂下
        p.ell(hx - 7, hy - 5, hx + 7, hy + 3, c["skin"])
        p.line([(hx - 5, hy - 5), (hx - 1, hy - 6)], c["hair_hi"])
        if c.get("swept_back"):  # 上官螢：額上的頭髮往後梳進髮髻，幾道髮絲的光澤
            for x0, x1, top in ((-6, -3, -11), (-1, 1, -12), (4, 4, -11), (7, 6, -9)):
                p.line([(hx + x0, hy - 6), (hx + x1, hy + top)], c["hair_hi"])
        p.rect(hx - 11, hy - 3, hx - 9, hy + 12, hair)
        p.rect(hx + 9, hy - 3, hx + 11, hy + 12, hair)
        # 頭頂髮髻上橫插的金簪
        k = -1 if face_r else 1
        p.line([(hx - 6 * k, hy - 13), (hx + 8 * k, hy - 15)], OUTLINE, 3)
        p.line([(hx - 6 * k, hy - 13), (hx + 8 * k, hy - 15)], c["pin"], 1)
        p.px(hx - 7 * k, hy - 13, c["pin"])
        # 側邊垂下的淺藍髮帶
        p.line([(hx + 10 * k, hy - 8), (hx + 12 * k, hy - 1)], c["ribbon"], 2)
    elif c.get("head") == "twin":
        # 中分瀏海：額頭正中間露出一小塊
        p.poly([(hx - 2, hy + 1), (hx + 2, hy + 1), (hx, hy - 3)], c["skin"])
        p.rect(hx - 11, hy - 2, hx - 9, hy + 6, hair)
        p.rect(hx + 9, hy - 2, hx + 11, hy + 6, hair)
        # 右邊小髻上的紅花與垂下的紅緞帶
        k = -1 if face_r else 1
        fx0, fy0 = hx + 9 * k, hy - 9
        for ox, oy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            p.px(fx0 + ox, fy0 + oy, c["flower"])
        p.px(fx0, fy0, (255, 220, 120, 255))
        p.line([(fx0 + k, fy0 + 1), (fx0 + 2 * k, fy0 + 9)], c["flower"])
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
    elif eyes == "drowsy_sick":  # 發燒時沒力氣、半閉的眼睛
        for x in (lx, rx):
            p.line([(x - 1, ey + 1), (x + 2, ey + 1)], eye)
            p.rect(x, ey + 2, x + 1, ey + 2, eye)
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
    if c.get("homely"):  # 趙活奇貌不揚：大鼻子、法令紋
        p.rect(mx, hy + 5, mx + 1, hy + 6, c["skin_sh"])
        p.px(mx - 3, hy + 7, c["skin_sh"]); p.px(mx + 4, hy + 7, c["skin_sh"])
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
    elif m == "fang":  # 張大嘴生氣，露出小虎牙
        p.rect(mx - 1, my - 1, mx + 2, my + 1, mouth)
        p.px(mx - 1, my - 1, white); p.px(mx + 2, my - 1, white)
    elif m == "scream":  # 嚇到尖叫
        p.rect(mx - 1, my - 2, mx + 2, my + 2, mouth)
        p.line([(mx - 1, my - 2), (mx + 2, my - 2)], white)
    elif m == "wobble":  # 要哭的抖抖嘴
        p.px(mx - 1, my, mouth); p.px(mx, my - 1, mouth); p.px(mx + 1, my, mouth); p.px(mx + 2, my - 1, mouth)
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

    if "fur" in c:
        # 白色毛領圍住脖子，中間繫著粉紅領結
        p.ell(hx - 8, hy + 11, hx + 8, hy + 15, c["fur"], OUTLINE)
        p.line([(hx - 6, hy + 14), (hx + 6, hy + 14)], c["fur_sh"])
        p.px(hx - 1, hy + 15, (232, 120, 140, 255)); p.px(hx + 1, hy + 15, (232, 120, 140, 255))
        p.px(hx, hy + 16, (232, 120, 140, 255))
        # 低低的雙馬尾垂在胸前，綠繩綁住
        for side in (-1, 1):
            x0 = hx + 10 * side
            p.poly([(x0 - side, hy + 4), (x0 + side * 2, hy + 4), (x0 + side * 2, hy + 18),
                    (x0, hy + 20), (x0 - side * 2, hy + 17), (x0 - side * 2, hy + 7)], hair, OUTLINE)
            p.line([(x0 - side, hy + 10), (x0 + side, hy + 10)], c["tie"], 2)
    if c.get("bells"):  # 頸上繫著鈴鐺的細繩（鈴鐺從不作響）
        p.line([(hx - 4, hy + 12), (hx + 4, hy + 12)], (60, 40, 40, 255))
        p.ell(hx - 1, hy + 12, hx + 1, hy + 14, (232, 196, 80, 255), OUTLINE)
    if "lips" in c and m == "smirk":
        p.px(mx, my, c["lips"])

    if "kerchief" in c:  # 領巾
        p.poly([(hx - 4, hy + 11), (hx + 4, hy + 11), (hx, hy + 15)], c["kerchief"], OUTLINE)
        p.px(hx - 1, hy + 12, c["kerchief_sh"])

    if al == "mouth_cover":  # 摀著嘴的那隻手要蓋在臉上
        hand = (hx - 2 + look, hy + 9)
        p.line([(sx_l + 2, sy - 2), hand], OUTLINE, 5)
        p.line([(sx_l + 2, sy - 2), hand], c["sleeve"], 3)
        p.ell(hand[0] - 2, hand[1] - 2, hand[0] + 2, hand[1] + 1, c["skin"], OUTLINE)

    if ar == "wipe":
        # 擦汗：戴手套的前臂從手肘橫到額頭前
        # 擦淚（上官螢）：袖子橫到眼角，手背貼著眼睛
        crying = "tear" in pose["fx"] or "tear2" in pose["fx"]
        elbow = (sx_r + 5, sy - 9)
        hand = (hx + 5 + look, hy + (3 if crying else 0))
        p.line([elbow, hand], OUTLINE, 5)
        p.line([elbow, hand], c.get("glove", c["sleeve"] if crying else c["skin"]), 3)
        r_ = 1 if crying else 2  # 擦淚的手小一點，貼在眼角
        p.ell(hand[0] - r_, hand[1] - r_, hand[0] + r_, hand[1] + r_, c.get("glove", c["skin"]), OUTLINE)

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
        elif kind == "warmer":  # 郁竹打造的深綠手爐，雙手捧在身前
            x, y = (hand_l[0] + hand_r[0]) // 2, max(hand_l[1], hand_r[1]) - 1
            green, lid = (46, 76, 72, 255), (70, 104, 98, 255)
            p.ell(x - 4, y - 4, x + 4, y + 3, green, OUTLINE)
            p.line([(x - 3, y - 2), (x + 3, y - 2)], lid)
            p.px(x - 1, y, lid); p.px(x + 1, y, lid)
            p.d.arc([x - 3, y - 8, x + 3, y - 2], 180, 360, fill=OUTLINE)  # 提把
            if prop[1:] == ("steam",):
                for ox, oy in ((-1, -9), (1, -10), (0, -11)):
                    p.px(x + ox, y + oy, (236, 236, 244, 255))
        elif kind == "book":  # 攤開的書，prop[1] 是翻到第幾頁（讓書頁動起來）
            x, y = (hand_l[0] + hand_r[0]) // 2, min(hand_l[1], hand_r[1]) + 2
            p.rect(x - 7, y - 3, x + 7, y + 2, OUTLINE)
            p.rect(x - 6, y - 2, x - 1, y + 1, (252, 250, 240, 255))
            p.rect(x + 1, y - 2, x + 6, y + 1, (252, 250, 240, 255))
            p.line([(x, y - 3), (x, y + 2)], (140, 90, 60, 255))
            for k_ in range(2):
                yy = y - 1 + k_ * 2
                p.line([(x - 5, yy), (x - 2, yy)], (170, 170, 180, 255))
                p.line([(x + 2, yy), (x + 5, yy)], (170, 170, 180, 255))
            if prop[1] % 2:  # 正在翻的那一頁
                p.poly([(x, y - 3), (x + 4, y - 6), (x + 5, y - 2), (x + 1, y)], (252, 250, 240, 255), OUTLINE)
        elif kind == "stick":  # 葉雲裳的樹枝（聽雲棒）：up 舉起、down 揮下
            x, y = hand_r
            tip = (x - 3, max(1, y - 18)) if prop[1] == "up" else (min(46, x + 13), y + 4)
            p.line([(x, y), tip], OUTLINE, 3)
            p.line([(x, y), tip], (128, 88, 58, 255), 1)
            mx_, my_ = (x + tip[0]) // 2, (y + tip[1]) // 2
            p.px(mx_ + 1, my_, (128, 88, 58, 255))  # 小分岔
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
        elif f == "bruise":  # 被揍：黑眼圈、臉頰腫、頭上一個包
            purple, red = (130, 84, 150, 255), (224, 120, 110, 255)
            ex0 = hx - 5 + look
            for ox, oy in ((-1, 2), (-1, 3), (-1, 4), (0, 5), (1, 5), (2, 4), (2, 3), (2, 2), (0, 1), (1, 1)):
                p.px(ex0 + ox, hy + oy, purple)
            p.rect(hx + 5 + look, hy + 6, hx + 7 + look, hy + 8, red)
            p.ell(hx + 1, hy - 16, hx + 5, hy - 12, c["skin"], OUTLINE)
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
        elif f == "head_steam":  # 害羞得頭頂冒熱氣
            for ox, oy in ((-6, -16), (-4, -18), (5, -17), (7, -19), (0, -19)):
                p.px(hx + ox, hy + oy, (236, 236, 244, 255))
        elif f == "gloom":  # 臉上一片陰影、只剩眼睛發亮（她藏起來的另一面）
            for yy in range(hy - 6, ey):
                for xx in range(hx - 8, hx + 9):
                    if img_px(p, xx, yy) == c["skin"]:
                        p.px(xx, yy, (206, 192, 210, 255))
        elif f == "grumble":  # 嘟嘴生悶氣：頭的兩側冒出白色小氣團
            for gx, gy in ((hx - 14, hy - 8), (hx + 13, hy - 8)):
                p.ell(gx - 2, gy - 1, gx + 2, gy + 2, (250, 250, 250, 255), OUTLINE)
        elif f == "tears":  # 大哭：兩行淚
            for x in (lx, rx + 1):
                p.line([(x, ey + 3), (x, ey + 7)], (120, 180, 255, 255))
        elif f == "fever":  # 發燒：額頭一片陰影、滿臉通紅冒汗
            p.line([(hx - 5, hy + 2), (hx + 5, hy + 2)], (232, 214, 230, 255))  # 額頭淡淡的陰影
            p.rect(hx - 8 + look, hy + 5, hx - 6 + look, hy + 6, (255, 130, 130, 255))
            p.rect(hx + 5 + look, hy + 5, hx + 7 + look, hy + 6, (255, 130, 130, 255))
            p.px(hx + 9, hy, (150, 200, 255, 255)); p.px(hx + 9, hy + 1, (150, 200, 255, 255))
        elif f == "q":  # 等待：頭上小問號（貼著頭頂）
            x, y = hx + 8, hy - 15
            col = (250, 200, 80, 255)
            for ox, oy in ((0, 0), (1, 0), (2, 1), (1, 2), (1, 4)):
                p.px(x + ox, y + oy, col)

    return p.img.resize((CELL_W, CELL_H), Image.NEAREST)


def img_px(p, x, y):
    if 0 <= x < W and 0 <= y < H:
        return p.img.getpixel((x, y))
    return None


def mirror_row(frames):
    return [f.transpose(Image.FLIP_LEFT_RIGHT) for f in frames]


# 點陣底圖角色（大師兄、趙活）：大師兄底圖的眉毛位置，重畫表情前先抹成膚色（眼口在底圖上已抹掉）
BM_FACE = [(19, 20), (20, 20), (26, 20), (27, 20)]


def draw_bitmap_frame(c, pose):
    base = Image.open(ROOT / c["bitmap"]).convert("RGBA")
    noarms = Image.open(ROOT / c["bitmap_noarms"]).convert("RGBA") if "bitmap_noarms" in c else None
    img = base.copy()
    put = lambda x, y, col: 0 <= x < W and 0 <= y < H and img.putpixel((x, y), col)
    O, skin, eye = c["outline"], c["skin"], c["eye"]
    legs = pose["legs"]

    # 腳：跑步時輪流抬腳、跳躍時收腿
    def lift(x0, x1, n):
        for y in range(46, 52):
            for x in range(x0, x1 + 1):
                img.putpixel((x, y), (0, 0, 0, 0))
        for y in range(47, 51):
            for x in range(x0, x1 + 1):
                px = base.getpixel((x, y))
                if px[3]:
                    img.putpixel((x, y - n), px)
        for x in range(x0, x1 + 1):  # 抬起時補回下襬
            if base.getpixel((x, 46))[3] and not img.getpixel((x, 46))[3]:
                img.putpixel((x, 46), base.getpixel((x, 46)))
    (fl0, fl1), (fr0, fr1) = c.get("bm_feet", ((19, 23), (26, 30)))
    if legs in ("stepA",):
        lift(fl0, fl1, 1)
    elif legs in ("stepB",):
        lift(fr0, fr1, 1)
    elif legs == "tuck":
        lift(fl0, fl1, 2); lift(fr0, fr1, 2)

    # 手臂：不是垂手就把底圖的手抹掉，從肩膀重畫袖子、棕色袖套與手
    hands = [(19, 38), (29, 38)]
    for side, name in enumerate(pose["arms"]):
        if name == "down":
            continue
        xs = range(16, 20) if side == 0 else range(29, 33)
        if noarms:  # 有沒畫手臂的底圖就直接補回身體
            for y in range(31, 44):
                for x in xs:
                    img.putpixel((x, y), noarms.getpixel((x, y)))
        else:
            edge = 20 if side == 0 else 28
            for y in range(32, 40):
                for x in xs:
                    put(x, y, (0, 0, 0, 0))
                if img.getpixel((edge, y))[3]:
                    put(edge, y, O)
        sx, sy = c.get("bm_shoulders", ((20, 34), (28, 34)))[side]
        hdx, hdy = ARM_HANDS[name][side]
        ex, ey = sx + hdx, sy + hdy
        d = ImageDraw.Draw(img)
        d.line([(sx, sy), (ex, ey)], fill=O, width=4)
        d.line([(sx, sy), (ex, ey)], fill=c["sleeve"], width=2)
        mx, my = (sx + ex) // 2, (sy + ey) // 2
        d.line([(mx, my), (ex, ey)], fill=c["bracer"], width=2)
        if "gold" in c:  # 大師兄護腕上的金環
            put((mx + ex * 3) // 4, (my + ey * 3) // 4, c["gold"])
        d.rectangle([ex - 1, ey - 1, ex + 1, ey + 1], fill=O)
        d.rectangle([ex - 1, ey - 1, ex, ey], fill=skin)
        hands[side] = (ex, ey)

    # 五官
    for x, y in c.get("bm_face_clear", BM_FACE):
        put(x, y, skin)
    eyes = pose["eyes"] or c["default_eyes"]
    eyes = {"squint": "drowsy", "dull": "drowsy"}.get(eyes, eyes)
    mouth = pose["mouth"]
    sharp = eyes in ("open", "wide", "side", "look_up", "drowsy", "wink")
    brow = c.get("brow", eye)
    for x, y in ((19, 20), (20, 20), (27, 20), (28, 20)):  # 眉毛
        put(x, y, brow)
    if sharp and c.get("bm_brows", "sharp") == "sharp":  # 劍眉：睜眼時眉頭壓低，閉眼笑時不壓，免得看起來像打叉
        put(21, 21, eye); put(26, 21, eye)
    if eyes == "sad":  # 眉尾下垂
        put(19, 21, brow); put(28, 21, brow)
    L, R = 20, 27
    if eyes in ("open", "wide", "side", "look_up"):
        o = 1 if eyes == "side" else 0
        for x in (L + o, R + o):
            put(x, 22, eye); put(x, 23, c["iris"])
            if eyes == "wide":
                put(x, 24, eye)
    elif eyes == "drowsy":  # 半睜、瞇著眼的痞樣
        for x in (L, R):
            put(x - 1, 22, eye); put(x, 22, eye); put(x + 1, 22, eye); put(x, 23, c["iris"])
    elif eyes in ("happy", "closed", "blink"):
        for x in (L, R):
            if eyes == "happy":
                put(x - 1, 23, eye); put(x, 22, eye); put(x + 1, 23, eye)
            else:
                put(x - 1, 23, eye); put(x, 23, eye); put(x + 1, 23, eye)
    elif eyes == "wink":
        put(L, 22, eye); put(L, 23, c["iris"])
        put(R - 1, 23, eye); put(R, 22, eye); put(R + 1, 23, eye)
    elif eyes == "sad":
        for x in (L, R):
            put(x - 1, 23, eye); put(x, 23, eye); put(x + 1, 22, eye) if x == L else put(x - 1, 22, eye)
    if pose["blush"]:
        put(19, 25, c["blush"]); put(29, 25, c["blush"])
    m = c["mouth"]
    white = (250, 246, 236, 255)
    if "mouth_cover" in pose["arms"]:
        pass  # 嘴被手摀住
    elif c.get("bm_mouth") == "teeth":  # 趙活：咧嘴露出缺了一顆的門牙
        if mouth == "smirk":  # 歪嘴賊笑，一邊嘴角翹起來
            put(22, 26, m); put(23, 26, white); put(24, 26, eye); put(25, 26, white); put(26, 25, m)
            put(23, 27, m); put(24, 27, m); put(25, 27, m)
        elif mouth in ("smile", "grin"):
            put(22, 25, m); put(26, 25, m)
            put(22, 26, m); put(23, 26, white); put(24, 26, eye); put(25, 26, white); put(26, 26, m)
            put(23, 27, m); put(24, 27, m); put(25, 27, m)
        elif mouth in ("laugh", "fang", "open", "scream"):
            for x in range(22, 27):
                put(x, 26, m); put(x, 27, eye)
            put(23, 26, white); put(25, 26, white); put(24, 26, eye)
            for x in range(23, 26):
                put(x, 28, m)
        elif mouth == "flat":
            put(23, 26, m); put(24, 26, m); put(25, 26, m)
        elif mouth == "wobble":
            put(22, 27, m); put(23, 26, m); put(24, 27, m); put(25, 26, m); put(26, 27, m)
        elif mouth == "o":
            put(24, 26, eye); put(24, 27, eye)
    elif mouth in ("smirk", "smile"):
        put(23, 26, m); put(24, 26, m); put(25, 25, m)
    elif mouth == "flat":
        put(23, 26, m); put(24, 26, m); put(25, 26, m)
    elif mouth == "grin":
        put(22, 25, m); put(23, 26, m); put(24, 26, m); put(25, 26, m); put(26, 25, m)
    elif mouth in ("fang", "laugh", "open"):
        for x in (23, 24, 25):
            put(x, 26, eye); put(x, 27, m)
        if mouth == "fang":
            put(23, 27, (255, 255, 255, 255))
    elif mouth == "o":
        put(24, 26, eye); put(24, 27, m)

    # 道具：金錢鏢（方孔金錢）
    gold, shine, hole = (226, 182, 70, 255), (255, 236, 160, 255), (90, 60, 30, 255)

    def coin(cx, cy, edge=False):
        if edge:  # 轉到側面時只剩一條細線
            for y in (cy - 1, cy, cy + 1):
                put(cx, y, gold)
            put(cx - 1, cy, O); put(cx + 1, cy, O)
            return
        for x, y in ((cx - 1, cy - 2), (cx, cy - 2), (cx + 1, cy - 2), (cx - 1, cy + 2), (cx, cy + 2), (cx + 1, cy + 2),
                     (cx - 2, cy - 1), (cx - 2, cy), (cx - 2, cy + 1), (cx + 2, cy - 1), (cx + 2, cy), (cx + 2, cy + 1)):
            put(x, y, O)
        for x in (cx - 1, cx, cx + 1):
            for y in (cy - 1, cy, cy + 1):
                put(x, y, gold)
        put(cx, cy, hole); put(cx - 1, cy - 1, shine)

    prop = pose["prop"]
    if prop and prop[0] == "coins":
        x, y = hands[1]
        if prop[1] == "throw":  # 擲出：三枚金錢鏢帶著殘影飛出去
            k = prop[2] if len(prop) > 2 else 0
            # 手邊空間不多，三枚排成扇形往上、前、下散開，後面拖著殘影
            for i, (ox, oy) in enumerate(((3, -7), (5, -1), (3, 5))):
                cx = min(45, x + ox + 2 * k)
                cy = y + oy + (-2 * k if oy < 0 else 2 * k if oy > 0 else 0)
                for t in range(1, 4):
                    put(cx - 2 - t, cy - (oy // 4) * t // 2, (255, 236, 160, 170 - t * 40))
                coin(cx, cy, edge=(i + k) % 2 == 1)
            if k >= 1:  # 命中的火花
                for ox, oy in ((0, -2), (0, 2), (-2, 0), (2, 0), (0, 0)):
                    put(46 + min(0, ox), y - 1 + oy, (255, 220, 120, 255))
        else:  # 指間夾著兩三枚，輪流轉動
            fan = ((2, -2), (3, 1)) if prop[1] == 0 else ((3, -1), (1, -3), (4, 2))
            for i, (ox, oy) in enumerate(fan):
                coin(x + ox, y + oy, edge=(i + prop[1]) % 2 == 1)
    elif prop and prop[0] == "coin_up":  # 用拇指把一枚金錢彈上去再接住
        x, y = hands[0]  # 用沒被馬尾擋住的那隻手
        h = prop[1]
        coin(x - 1, y - 2 - h, edge=h == 5)
        if h:
            for t in range(1, min(h, 4)):
                put(x - 1, y - 2 - h + 2 + t, (255, 236, 160, 120))

    # 效果
    for f in pose["fx"]:
        if f == "note":
            col = (214, 168, 60, 255)
            for y in range(4, 9):
                put(38, y, col)
            put(39, 4, col); put(40, 5, col); put(37, 8, col); put(36, 8, col); put(37, 9, col)
        elif f == "q":
            col = (90, 130, 200, 255)
            for x, y in ((37, 6), (38, 5), (39, 5), (40, 6), (40, 7), (39, 8), (38, 9), (38, 11)):
                put(x, y, col)
        elif f == "sweat":
            col = (120, 180, 230, 255)
            put(31, 16, col); put(31, 17, col); put(30, 18, col); put(31, 18, col); put(32, 18, col)
        elif f == "idea":
            col = (176, 130, 70, 255)
            for pts in (((10, 10), (11, 12)), ((13, 7), (13, 9)), ((8, 14), (10, 15))):
                ImageDraw.Draw(img).line(pts, fill=col)
        elif f == "speechless":
            for x in (8, 10, 12):
                put(x, 14, O)
        elif f == "star":
            col = (250, 210, 70, 255)
            for x0, y0 in ((35, 8), (12, 6)):
                for ox, oy in ((1, 0), (0, 1), (1, 1), (2, 1), (1, 2)):
                    put(x0 + ox, y0 + oy, col)
        elif f == "bruise":  # 被揍：黑眼圈、臉頰腫、頭上一個包（卡通化，不畫流血）
            purple, red = (130, 84, 150, 255), (224, 120, 110, 255)
            for ox, oy in ((-1, 21), (0, 21), (1, 21), (-2, 22), (2, 22), (-2, 23), (2, 23), (-1, 24), (0, 24), (1, 24)):
                put(20 + ox, oy, purple)
            for x in (28, 29):
                for y in (24, 25):
                    put(x, y, red)
            d = ImageDraw.Draw(img)
            d.ellipse([25, 2, 29, 6], fill=skin, outline=O)
        elif f in ("tear", "tear2"):
            col = (120, 180, 230, 255)
            for x in ((20,) if f == "tear" else (20, 27)):
                put(x, 24, col); put(x, 25, col)
        elif f == "gloom":  # 臉上一片陰影
            dark = tuple(int(v * 0.72) for v in skin[:3]) + (255,)
            for y in range(17, 24):  # 眼睛那一帶
                for x in range(16, 33):
                    if img.getpixel((x, y)) == skin:
                        img.putpixel((x, y), dark)
        elif f == "spark":
            for x, y in ((11, 20), (36, 20), (13, 16), (34, 16)):
                put(x, y, (255, 220, 120, 255))

    # 身體上下移動（輕功、彈跳）
    shift = pose["dy"] + (1 if legs == "crouch" else 0)
    if shift or pose["dx"]:
        moved = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        moved.alpha_composite(img, (pose["dx"], shift))
        img = moved
    return img


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


def poses_yeyunshang():
    """葉雲裳：捏著領結、欸嘿、嘟嘴、興奮張開斗篷、祈禱、拿樹枝生氣、大哭、有心事、發燒。"""
    rb = ("ribbon", "ribbon")
    return {
        # 雙手捏著胸前的領結，眨眨眼
        "idle": [P(arms=rb, mouth="smile"), P(arms=rb, mouth="smile"), P(arms=rb, eyes="blink", mouth="smile"),
                 P(arms=rb, mouth="smile", dy=1), P(arms=rb, mouth="cat", dy=1), P(arms=rb, mouth="smile")],
        "running-right": run_row(mouth="grin", eyes="open"),
        # 欸嘿：眨眼吐舌冒星星
        "waving": [P(arms=rb, mouth="smile", eyes="happy"),
                   P(arms=rb, mouth="tongue", eyes="wink", fx=("star",)),
                   P(arms=rb, mouth="tongue", eyes="wink", fx=("star",), dy=-1),
                   P(arms=rb, mouth="smile", eyes="happy", blush=True)],
        # 興奮：抓著斗篷往兩邊張開跳起來
        "jumping": [P(dy=2, legs="crouch", arms=rb, eyes="closed", mouth="smile"),
                    P(dy=-3, legs="tuck", arms=("cape_open", "cape_open"), eyes="wide", mouth="grin"),
                    P(dy=-5, legs="tuck", arms=("cape_open", "cape_open"), eyes="happy", mouth="laugh"),
                    P(dy=-2, legs="stand", arms=("cape_open", "cape_open"), eyes="happy", mouth="grin"),
                    P(dy=1, legs="crouch", arms=rb, eyes="happy", mouth="smile", blush=True)],
        # 失敗：先嘟嘴生悶氣，再大哭，最後發燒沒力氣
        "failed": [P(arms=rb, eyes="sad", mouth="frown", fx=("grumble",)),
                   P(arms=rb, eyes="sad", mouth="frown", fx=("grumble",), dy=1),
                   P(arms=rb, eyes="sad", mouth="wobble", fx=("tears",)),
                   P(arms=rb, eyes="closed", mouth="wobble", fx=("tears",), dy=1),
                   P(arms=rb, eyes="sad", mouth="wobble", fx=("tears",)),
                   P(arms=("droop", "droop"), eyes="drowsy_sick", mouth="o", fx=("fever",), dy=1, tilt=-1),
                   P(arms=("droop", "droop"), eyes="drowsy_sick", mouth="o", fx=("fever",), dy=2, tilt=-1),
                   P(arms=rb, eyes="sad", mouth="small")],
        # 祈禱：雙手合十閉眼，拜託你快點頭
        "waiting": [P(arms=("clasp", "clasp"), eyes="closed", mouth="small", fx=("q",)),
                    P(arms=("clasp", "clasp"), eyes="closed", mouth="small", fx=("q",), dy=-1),
                    P(arms=("clasp", "clasp"), eyes="look_up", mouth="small", fx=("q",)),
                    P(arms=("clasp", "clasp"), eyes="look_up", mouth="o", fx=("q",), blush=True),
                    P(arms=("clasp", "clasp"), eyes="closed", mouth="small", fx=("q",), dy=-1),
                    P(arms=("clasp", "clasp"), eyes="look_up", mouth="small", fx=("q",))],
        # 工作中：拿著樹枝（聽雲棒）氣呼呼地比劃
        "running": [P(arms=("ribbon", "hammer_up"), prop=("stick", "up"), eyes="squint", mouth="fang", fx=("grumble",)),
                    P(arms=("ribbon", "hammer_up"), prop=("stick", "up"), eyes="squint", mouth="fang", dy=-1),
                    P(arms=("ribbon", "hammer_down"), prop=("stick", "down"), eyes="closed", mouth="fang", fx=("grumble",)),
                    P(arms=("ribbon", "hammer_down"), prop=("stick", "down"), eyes="squint", mouth="flat"),
                    P(arms=("ribbon", "hammer_up"), prop=("stick", "up"), eyes="squint", mouth="fang", dy=-1),
                    P(arms=("ribbon", "hammer_down"), prop=("stick", "down"), eyes="happy", mouth="grin")],
        # 有心事：垂著眼睛，安靜地捏著領結
        "review": [P(arms=rb, eyes="closed", mouth="flat"),
                   P(arms=rb, eyes="closed", mouth="flat", tilt=-1),
                   P(arms=rb, eyes="side", mouth="flat", tilt=-1),
                   P(arms=rb, eyes="closed", mouth="flat", tilt=-1),
                   P(arms=rb, eyes="side", mouth="small"),
                   P(arms=rb, eyes="open", mouth="smile", blush=True)],
    }


def poses_weiju():
    """魏菊：捧手爐微笑、害羞冒熱氣、閉眼臉紅笑、讀書、驚訝冒汗、嚇到尖叫、陰影微笑。"""
    cr = ("cradle", "cradle")
    wm = ("warmer",)
    return {
        "idle": [P(arms=cr, prop=wm, mouth="smile"), P(arms=cr, prop=wm, mouth="smile"),
                 P(arms=cr, prop=wm, eyes="blink", mouth="smile"), P(arms=cr, prop=("warmer", "steam"), mouth="smile", dy=1),
                 P(arms=cr, prop=("warmer", "steam"), mouth="smile", dy=1), P(arms=cr, prop=wm, mouth="smile")],
        "running-right": run_row(mouth="smile", eyes="open"),
        # 打招呼：微微欠身，害羞得頭頂冒熱氣
        "waving": [P(arms=cr, prop=wm, mouth="smile", eyes="happy"),
                   P(arms=cr, prop=wm, mouth="smile", eyes="side", blush=True, dy=1, fx=("sweat",)),
                   P(arms=cr, prop=wm, mouth="smile", eyes="side", blush=True, dy=1, fx=("head_steam", "sweat")),
                   P(arms=cr, prop=wm, mouth="smile", eyes="happy", blush=True, fx=("head_steam",))],
        # 開心：閉眼臉紅笑，端莊地輕輕一跳
        "jumping": [P(arms=cr, prop=wm, eyes="closed", mouth="smile"),
                    P(dy=-2, legs="tuck", arms=cr, prop=wm, eyes="closed", mouth="grin", blush=True),
                    P(dy=-3, legs="tuck", arms=cr, prop=wm, eyes="closed", mouth="grin", blush=True),
                    P(dy=-1, legs="stand", arms=cr, prop=wm, eyes="closed", mouth="grin", blush=True),
                    P(arms=cr, prop=wm, eyes="happy", mouth="smile", blush=True)],
        # 失敗：嚇到摀嘴尖叫、全身發抖，再勉強鎮定
        "failed": [P(arms=cr, prop=wm, eyes="wide", mouth="o", fx=("sweat",)),
                   P(arms=("mouth_cover", "tremble"), eyes="wide", mouth="scream", fx=("sweat", "chill")),
                   P(arms=("mouth_cover", "tremble"), eyes="wide", mouth="scream", fx=("chill",), dx=1),
                   P(arms=("mouth_cover", "tremble"), eyes="wide", mouth="scream", fx=("chill", "sweat"), dx=-1),
                   P(arms=("mouth_cover", "tremble"), eyes="wide", mouth="scream", fx=("chill",), dx=1),
                   P(arms=cr, prop=wm, eyes="sad", mouth="o", fx=("sweat",)),
                   P(arms=cr, prop=wm, eyes="closed", mouth="flat"),
                   P(arms=cr, prop=wm, eyes="open", mouth="small")],
        # 等你回覆：驚訝地看著你，冒一滴汗
        "waiting": [P(arms=cr, prop=wm, eyes="wide", mouth="o", fx=("q", "sweat")),
                    P(arms=cr, prop=wm, eyes="wide", mouth="o", fx=("q", "sweat"), tilt=1),
                    P(arms=cr, prop=wm, eyes="open", mouth="o", fx=("q",), tilt=1),
                    P(arms=cr, prop=wm, eyes="blink", mouth="small", fx=("q",), tilt=1),
                    P(arms=cr, prop=wm, eyes="open", mouth="o", fx=("q", "sweat")),
                    P(arms=cr, prop=wm, eyes="wide", mouth="o", fx=("q",))],
        # 工作中：捧著書安靜地讀，翻頁
        "running": [P(arms=("hold_up", "hold_up"), prop=("book", 0), eyes="side", mouth="smile"),
                    P(arms=("hold_up", "hold_up"), prop=("book", 0), eyes="side", mouth="smile"),
                    P(arms=("hold_up", "hold_up"), prop=("book", 1), eyes="blink", mouth="smile"),
                    P(arms=("hold_up", "hold_up"), prop=("book", 0), eyes="side", mouth="smile"),
                    P(arms=("hold_up", "hold_up"), prop=("book", 0), eyes="happy", mouth="smile"),
                    P(arms=("hold_up", "hold_up"), prop=("book", 1), eyes="blink", mouth="smile")],
        # 審視：臉上一片陰影，意味深長地微笑
        "review": [P(arms=cr, prop=wm, eyes="open", mouth="smile"),
                   P(arms=cr, prop=wm, eyes="happy", mouth="grin", fx=("gloom",)),
                   P(arms=cr, prop=wm, eyes="happy", mouth="grin", fx=("gloom",), tilt=1),
                   P(arms=cr, prop=wm, eyes="happy", mouth="grin", fx=("gloom",), tilt=1),
                   P(arms=cr, prop=wm, eyes="happy", mouth="smile", fx=("gloom",)),
                   P(arms=cr, prop=wm, eyes="open", mouth="smile")],
    }


def poses_shangguanying():
    """上官螢：叉腰的驕傲千金、看帳本、冒愛心冒煙、摀嘴害羞、擦眼淚、雙手抱胸、氣到握拳。"""
    hp = ("hip", "down")
    return {
        # 一手叉腰，抬著下巴；偶爾「哼」地閉眼別過頭
        "idle": [P(arms=hp, mouth="flat"), P(arms=hp, mouth="flat"),
                 P(arms=hp, eyes="blink", mouth="flat"), P(arms=hp, eyes="closed", mouth="flat", tilt=1),
                 P(arms=hp, eyes="side", mouth="smirk", tilt=1), P(arms=hp, mouth="flat")],
        "running-right": run_row(mouth="flat", eyes="open"),
        # 打招呼：抬手一揮，嘴上嫌你來得晚
        "waving": [P(arms=("hip", "wave_mid"), mouth="smirk"),
                   P(arms=("hip", "wave_up"), mouth="open"),
                   P(arms=("hip", "wave_mid"), mouth="smirk", eyes="side"),
                   P(arms=hp, mouth="flat", eyes="closed", tilt=1)],
        # 開心：雙手揪著衣襟，眼冒愛心、臉紅到頭頂冒煙
        "jumping": [P(arms=("clasp", "clasp"), eyes="happy", mouth="open", blush=True),
                    P(dy=-2, legs="tuck", arms=("clasp", "clasp"), eyes="happy", mouth="open", blush=True, fx=("heart",)),
                    P(dy=-3, legs="tuck", arms=("clasp", "clasp"), eyes="happy", mouth="laugh", blush=True, fx=("heart", "head_steam")),
                    P(dy=-1, legs="stand", arms=("clasp", "clasp"), eyes="happy", mouth="open", blush=True, fx=("heart", "head_steam")),
                    P(arms=("clasp", "clasp"), eyes="happy", mouth="smile", blush=True, fx=("head_steam",))],
        # 失敗：先氣到握拳冒青筋，再用袖子擦眼淚「才沒哭」
        "failed": [P(arms=("down", "fist_side"), eyes="squint", mouth="frown", fx=("anger",)),
                   P(arms=("down", "fist_side"), eyes="squint", mouth="frown", fx=("anger",), dx=1),
                   P(arms=("down", "fist_side"), eyes="squint", mouth="frown", fx=("anger",), dx=-1),
                   P(arms=("down", "wipe"), eyes="sad", mouth="wobble", blush=True, fx=("tear",)),
                   P(arms=("down", "wipe"), eyes="closed", mouth="wobble", blush=True, fx=("tear2",)),
                   P(arms=("down", "wipe"), eyes="sad", mouth="wobble", blush=True, fx=("tear",)),
                   P(arms=hp, eyes="side", mouth="flat", blush=True),
                   P(arms=hp, eyes="open", mouth="flat")],
        # 等你回覆：雙手抱胸，不耐煩地等
        "waiting": [P(arms=("cross", "cross"), eyes="open", mouth="flat", fx=("q",)),
                    P(arms=("cross", "cross"), eyes="side", mouth="flat", fx=("q",)),
                    P(arms=("cross", "cross"), eyes="squint", mouth="flat", fx=("q",), tilt=1),
                    P(arms=("cross", "cross"), eyes="blink", mouth="flat", fx=("q",), tilt=1),
                    P(arms=("cross", "cross"), eyes="open", mouth="frown", fx=("q",)),
                    P(arms=("cross", "cross"), eyes="open", mouth="flat", fx=("q",))],
        # 工作中：捧著帳本對帳
        "running": [P(arms=("hold_up", "hold_up"), prop=("book", 0), eyes="side", mouth="flat"),
                    P(arms=("hold_up", "hold_up"), prop=("book", 0), eyes="side", mouth="flat"),
                    P(arms=("hold_up", "hold_up"), prop=("book", 1), eyes="blink", mouth="flat"),
                    P(arms=("hold_up", "hold_up"), prop=("book", 0), eyes="squint", mouth="flat"),
                    P(arms=("hold_up", "hold_up"), prop=("book", 0), eyes="open", mouth="smirk"),
                    P(arms=("hold_up", "hold_up"), prop=("book", 1), eyes="blink", mouth="flat")],
        # 審視：一手摀著嘴、臉紅地斜眼打量
        "review": [P(arms=("mouth_cover", "hip"), eyes="side", blush=True),
                   P(arms=("mouth_cover", "hip"), eyes="side", blush=True),
                   P(arms=("mouth_cover", "hip"), eyes="squint", blush=True, tilt=1),
                   P(arms=("mouth_cover", "hip"), eyes="blink", blush=True, tilt=1),
                   P(arms=("mouth_cover", "hip"), eyes="open", blush=True),
                   P(arms=("mouth_cover", "hip"), eyes="side", blush=True)],
    }


def poses_tangbuyi():
    """大師兄（依 Q 版參考）：叉腰轉金錢鏢、豎指「有了！」、摸後腦大笑、抱胸、出掌擲鏢。"""
    return {
        # 叉腰歪著頭，用拇指把金錢彈上去再接住，接到了眨眼一笑
        "idle": [P(arms=("beckon", "hip"), prop=("coin_up", 0), mouth="smirk", tilt=1),
                 P(arms=("beckon", "hip"), prop=("coin_up", 5), mouth="smirk", tilt=1, eyes="look_up"),
                 P(arms=("beckon", "hip"), prop=("coin_up", 9), mouth="smirk", tilt=1, eyes="look_up", fx=("note",)),
                 P(arms=("beckon", "hip"), prop=("coin_up", 6), mouth="smirk", tilt=1, fx=("note",)),
                 P(arms=("beckon", "hip"), prop=("coin_up", 0), eyes="wink", mouth="fang", tilt=1),
                 P(arms=("hip", "hold"), prop=("coins", 1), mouth="smirk", tilt=1)],
        "running-right": run_row(mouth="grin", eyes="drowsy"),
        # 一手叉腰、一手豎起手指：「師弟，有了！」
        "waving": [P(arms=("hip", "up"), mouth="fang", eyes="happy", fx=("idea",)),
                   P(arms=("hip", "up"), mouth="laugh", eyes="happy"),
                   P(arms=("hip", "up"), mouth="fang", eyes="happy", fx=("idea",)),
                   P(arms=("hip", "up"), mouth="fang", eyes="open")],
        # 飛俠：壓低身子出掌，一躍擲出金錢鏢
        "jumping": [P(dy=2, legs="crouch", arms=("thrust", "hip"), eyes="drowsy", mouth="smirk"),
                    P(dy=0, legs="tuck", arms=("spread", "thrust"), prop=("coins", 1), mouth="grin"),
                    P(dy=-1, legs="tuck", arms=("spread", "thrust"), prop=("coins", "throw", 0), mouth="fang", eyes="happy"),
                    P(dy=0, legs="stand", arms=("spread", "thrust"), prop=("coins", "throw", 1), mouth="grin"),
                    P(dy=1, legs="crouch", arms=("hip", "hold"), prop=("coins", 0), mouth="smirk", fx=("note",))],
        # 失敗：愣住冒汗，接著摸著後腦哈哈大笑帶過
        "failed": [P(arms=("down", "down"), eyes="open", mouth="flat", fx=("speechless",)),
                   P(arms=("down", "down"), eyes="open", mouth="flat", fx=("speechless", "sweat")),
                   P(arms=("hip", "bonk"), eyes="happy", mouth="laugh", fx=("sweat",)),
                   P(arms=("hip", "bonk"), eyes="happy", mouth="fang", fx=("sweat",), dy=-1),
                   P(arms=("hip", "bonk"), eyes="happy", mouth="laugh"),
                   P(arms=("hip", "bonk"), eyes="happy", mouth="fang", dy=-1),
                   P(arms=("hip", "hold"), prop=("coins", 0), eyes="drowsy", mouth="smirk"),
                   P(arms=("hip", "hold"), prop=("coins", 1), eyes="drowsy", mouth="smirk")],
        # 等你回覆：伸手在你眼前晃，「回神了沒？」
        "waiting": [P(arms=("hip", "ask"), eyes="open", mouth="open", fx=("q",)),
                    P(arms=("hip", "wave_mid"), eyes="open", mouth="open", fx=("q",)),
                    P(arms=("hip", "ask"), eyes="open", mouth="smirk", fx=("q",)),
                    P(arms=("hip", "wave_mid"), eyes="blink", mouth="open", fx=("q",)),
                    P(arms=("hip", "ask"), eyes="open", mouth="smirk", fx=("q",), tilt=1),
                    P(arms=("hip", "wave_mid"), eyes="open", mouth="open", fx=("q",))],
        # 工作中：拉開架式，連發金錢鏢、命中冒火花
        "running": [P(legs="crouch", arms=("hip", "hold"), prop=("coins", 0), eyes="drowsy", mouth="smirk"),
                    P(legs="crouch", arms=("hip", "thrust"), prop=("coins", "throw", 0), eyes="open", mouth="grin", dx=1),
                    P(legs="crouch", arms=("hip", "thrust"), prop=("coins", "throw", 1), eyes="drowsy", mouth="smirk", dx=1),
                    P(arms=("hip", "hold"), prop=("coins", 1), eyes="closed", mouth="smirk", fx=("note",)),
                    P(legs="crouch", arms=("hip", "thrust"), prop=("coins", "throw", 0), eyes="open", mouth="grin", dx=1),
                    P(legs="crouch", arms=("hip", "thrust"), prop=("coins", "throw", 1), eyes="happy", mouth="smirk", dx=1)],
        # 審視：雙手抱胸，板著臉看，看完了才嘴角一勾
        "review": [P(arms=("cross", "cross"), eyes="drowsy", mouth="flat"),
                   P(arms=("cross", "cross"), eyes="drowsy", mouth="flat", tilt=1),
                   P(arms=("cross", "cross"), eyes="side", mouth="flat", tilt=1),
                   P(arms=("cross", "cross"), eyes="closed", mouth="flat"),
                   P(arms=("cross", "cross"), eyes="drowsy", mouth="smirk"),
                   P(arms=("cross", "cross"), eyes="drowsy", mouth="smirk", fx=("note",))],
    }


def poses_zhaohuo():
    """趙活（依官方表情）：自戀撫臉、狂笑、計畫通、被揍到鼻青臉腫、嚇呆、決心、冷笑。"""
    return {
        # 自戀：一手撫著臉，越看自己越順眼；偶爾挖個鼻孔
        "idle": [P(arms=("down", "cheek"), eyes="drowsy", mouth="smirk"),
                 P(arms=("down", "cheek"), eyes="drowsy", mouth="smirk", tilt=1),
                 P(arms=("down", "cheek"), eyes="closed", mouth="smirk", tilt=1, blush=True),
                 P(arms=("down", "cheek"), eyes="drowsy", mouth="smirk"),
                 P(arms=("down", "nibble"), eyes="side", mouth="flat"),
                 P(arms=("down", "cheek"), eyes="drowsy", mouth="smirk")],
        "running-right": run_row(mouth="grin", eyes="open"),
        # 打招呼：瞇眼狂笑、一手往前揮
        "waving": [P(arms=("down", "wave_mid"), eyes="happy", mouth="laugh"),
                   P(arms=("down", "wave_up"), eyes="happy", mouth="laugh", dy=-1),
                   P(arms=("down", "wave_mid"), eyes="happy", mouth="laugh"),
                   P(arms=("down", "wave_up"), eyes="happy", mouth="grin")],
        # 計畫通：握拳跳起來大笑
        "jumping": [P(dy=2, legs="crouch", arms=("fist_side", "fist_side"), eyes="squint", mouth="smirk"),
                    P(dy=-3, legs="tuck", arms=("fist_up", "fist_up"), eyes="happy", mouth="laugh"),
                    P(dy=-4, legs="tuck", arms=("fist_up", "fist_up"), eyes="happy", mouth="laugh", fx=("spark",)),
                    P(dy=-1, legs="stand", arms=("down", "fist_up"), eyes="happy", mouth="grin"),
                    P(arms=("down", "cheek"), eyes="drowsy", mouth="smirk", blush=True)],
        # 失敗：中招被揍，鼻青臉腫冒星星，再哀哀叫
        "failed": [P(arms=("down", "down"), eyes="wide", mouth="o", fx=("sweat",)),
                   P(arms=("down", "down"), eyes="closed", mouth="scream", fx=("star",), dx=-2),
                   P(arms=("down", "down"), eyes="closed", mouth="wobble", fx=("star", "bruise"), dx=-1),
                   P(arms=("down", "bonk"), eyes="sad", mouth="wobble", fx=("bruise", "tear")),
                   P(arms=("down", "bonk"), eyes="sad", mouth="wobble", fx=("bruise", "tear2")),
                   P(arms=("down", "bonk"), eyes="sad", mouth="wobble", fx=("bruise",)),
                   P(arms=("down", "down"), eyes="sad", mouth="flat", fx=("bruise",)),
                   P(arms=("down", "down"), eyes="open", mouth="flat", fx=("bruise",))],
        # 等你回覆：嚇呆、摀嘴冒冷汗
        "waiting": [P(arms=("mouth_cover", "down"), eyes="wide", fx=("sweat",)),
                    P(arms=("mouth_cover", "down"), eyes="wide", fx=("sweat", "q")),
                    P(arms=("mouth_cover", "down"), eyes="wide", fx=("sweat",), dx=1),
                    P(arms=("mouth_cover", "down"), eyes="wide", fx=("sweat", "q"), dx=-1),
                    P(arms=("down", "down"), eyes="wide", mouth="o", fx=("q",)),
                    P(arms=("down", "down"), eyes="open", mouth="o", fx=("q",))],
        # 工作中：決心，握拳擺出架式
        "running": [P(arms=("fist_side", "fist_side"), eyes="squint", mouth="flat"),
                    P(arms=("fist_side", "thrust"), eyes="squint", mouth="flat", dx=1),
                    P(arms=("fist_side", "fist_side"), eyes="squint", mouth="flat"),
                    P(arms=("thrust", "fist_side"), eyes="squint", mouth="fang", dx=-1),
                    P(arms=("fist_side", "fist_side"), eyes="squint", mouth="flat"),
                    P(arms=("fist_side", "fist_side"), eyes="open", mouth="smirk")],
        # 審視：猙獰冷笑，臉上一片陰影
        "review": [P(arms=("down", "cheek"), eyes="squint", mouth="smirk"),
                   P(arms=("down", "cheek"), eyes="squint", mouth="grin", fx=("gloom",)),
                   P(arms=("down", "cheek"), eyes="squint", mouth="grin", fx=("gloom",), tilt=1),
                   P(arms=("down", "cheek"), eyes="side", mouth="grin", fx=("gloom",), tilt=1),
                   P(arms=("down", "cheek"), eyes="squint", mouth="smirk", fx=("gloom",)),
                   P(arms=("down", "cheek"), eyes="drowsy", mouth="smirk")],
    }


CUSTOM_POSES = {"zhaohuo": poses_zhaohuo, "shangguanying": poses_shangguanying, "tangbuyi": poses_tangbuyi, "weiju": poses_weiju, "xiaoshimei": poses_shimei, "longxiang": poses_longxiang, "xiahoulan": poses_xiahoulan,
                "yeyunshang": poses_yeyunshang}


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

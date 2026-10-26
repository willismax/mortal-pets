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
        "description": "崆峒飛天門的虞小梅：紅白衣裙、愛鬧愛笑、廚藝一流。說「本梅」的時候才是真心話。（活俠傳同人）",
        "hair": (34, 28, 44, 255),
        "hair_hi": (74, 64, 96, 255),
        "skin": (255, 226, 204, 255),
        "skin_sh": (240, 190, 165, 255),
        "eye": (70, 26, 40, 255),
        "cloth": (252, 248, 242, 255),
        "cloth_sh": (222, 212, 206, 255),
        "accent": (200, 44, 60, 255),
        "accent_sh": (150, 28, 44, 255),
        "sleeve": (252, 248, 242, 255),
        "shoe": (150, 28, 44, 255),
        "leg": (252, 248, 242, 255),  # 白襪
        "blush": (255, 150, 160, 255),
        "long_hair": True,
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
        "long_hair": False,
        "height_drop": 2,
        "default_eyes": "drowsy",
    },
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

    hx = 24 + dx + pose["tilt"]  # 頭中心
    hy = 19 + dy
    sx_l, sx_r, sy = 19 + dx, 29 + dx, 35 + dy  # 肩膀
    hip_y = 44 + dy

    # 後髮
    sway = pose["hair_sway"]
    if c["long_hair"]:
        tail = -3 if face_r else 0
        p.poly([(hx - 11 + tail + sway, hy), (hx + 11 + tail + sway, hy),
                (hx + 10 + tail + sway * 2, hy + 21), (hx - 10 + tail + sway * 2, hy + 21)],
               c["hair"], OUTLINE)
        # 髮髻
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
        p.rect(x - 1, top, x + 2, bottom - lift, OUTLINE)
        p.rect(x, top, x + 1, bottom - lift, c["leg"])
        p.rect(x - 1, bottom - lift + 1, x + 2, bottom - lift + 2, shoe)

    base_bottom = 47 + dy
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
    elif legs == "crouch":
        leg(20 + dx, hip_y, base_bottom)
        leg(27 + dx, hip_y, base_bottom)

    # 身體（裙裝）
    flare = -1 if face_r else 0
    body = [(20 + dx, 33 + dy), (28 + dx, 33 + dy), (32 + dx + flare, 45 + dy), (16 + dx + flare, 45 + dy)]
    p.poly(body, c["cloth"], OUTLINE)
    p.line([(17 + dx + flare, 44 + dy), (31 + dx + flare, 44 + dy)], c["cloth_sh"])
    if cid == "xiaomei":
        # 紅腰帶、紅裙襬、紅領
        p.rect(19 + dx, 38 + dy, 29 + dx, 39 + dy, c["accent"])
        p.line([(17 + dx + flare, 43 + dy), (31 + dx + flare, 43 + dy)], c["accent"])
        p.line([(17 + dx + flare, 44 + dy), (31 + dx + flare, 44 + dy)], c["accent_sh"])
        p.poly([(22 + dx, 33 + dy), (26 + dx, 33 + dy), (24 + dx, 36 + dy)], c["accent"])
        p.px(30 + dx, 40 + dy, c["accent"])  # 腰帶垂穗
        p.px(30 + dx, 41 + dy, c["accent"])
    else:
        # 圍裙吊帶、深色腰帶、卡其長圍裙
        p.line([(21 + dx, 33 + dy), (21 + dx, 38 + dy)], c["accent"])
        p.line([(27 + dx, 33 + dy), (27 + dx, 38 + dy)], c["accent"])
        p.poly([(20 + dx, 39 + dy), (28 + dx, 39 + dy), (30 + dx + flare, 45 + dy), (18 + dx + flare, 45 + dy)],
               c["accent"], OUTLINE)
        p.line([(22 + dx, 41 + dy), (21 + dx + flare, 44 + dy)], c["accent_sh"])
        p.line([(26 + dx, 41 + dy), (27 + dx + flare, 44 + dy)], c["accent_sh"])
        p.rect(19 + dx, 38 + dy, 29 + dx, 38 + dy, c["belt"])

    # 手臂
    al, ar = pose["arms"]

    def arm(sx, name, side):
        hdx, hdy = ARM_HANDS[name][side]
        ex, ey = sx + hdx, sy + hdy
        p.line([(sx, sy), (ex, ey)], OUTLINE, 4)
        p.line([(sx, sy), (ex, ey)], c["sleeve"], 2)
        p.px(ex, ey, OUTLINE)
        hand = c["skin"]
        if "glove" in c:  # 短袖，前臂到手掌是長手套
            mx, my = (sx * 2 + ex) // 3, (sy * 2 + ey) // 3
            p.line([(mx, my), (ex, ey)], c["glove"], 2)
            hand = c["glove"]
        p.rect(ex - 1, ey - 1, ex + 1, ey + 1, OUTLINE)
        p.rect(ex - 1, ey - 1, ex, ey, hand)
        return ex, ey

    hand_l = arm(sx_l, al, 0)
    hand_r = arm(sx_r, ar, 1)

    # 頭
    p.ell(hx - 10, hy - 8, hx + 10, hy + 12, c["skin"], OUTLINE)
    # 瀏海
    hair = c["hair"]
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

    if cid == "xiaomei":
        # 梅花髮簪
        bx, by = hx + 6, hy - 11
        for ox, oy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            p.px(bx + ox, by + oy, c["accent"])
        p.px(bx, by, (255, 214, 90, 255))
        p.px(bx + 2, by + 2, c["accent_sh"])
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
    if m == "smile":
        p.px(mx - 1, my - 1, mouth); p.px(mx, my, mouth); p.px(mx + 1, my, mouth); p.px(mx + 2, my - 1, mouth)
    elif m == "grin":
        p.rect(mx - 1, my - 1, mx + 2, my, mouth); p.line([(mx - 1, my - 1), (mx + 2, my - 1)], white)
    elif m == "open":
        p.rect(mx, my - 1, mx + 1, my + 1, mouth)
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

    if "kerchief" in c:  # 領巾
        p.poly([(hx - 4, hy + 11), (hx + 4, hy + 11), (hx, hy + 15)], c["kerchief"], OUTLINE)
        p.px(hx - 1, hy + 12, c["kerchief_sh"])

    if pose["blush"] or c.get("blush_always"):
        p.rect(hx - 8 + look, hy + 6, hx - 7 + look, hy + 6, c["blush"])
        p.rect(hx + 6 + look, hy + 6, hx + 7 + look, hy + 6, c["blush"])

    # 道具
    prop = pose["prop"]
    if prop:
        kind = prop[0]
        if kind == "hammer":
            # prop[1] = 'up' / 'down'
            x, y = hand_r
            if prop[1] == "up":
                p.line([(x, y), (x + 2, y - 5)], (120, 80, 50, 255), 1)
                p.rect(x - 1, y - 9, x + 5, y - 5, OUTLINE)
                p.rect(x, y - 8, x + 4, y - 6, (140, 144, 156, 255))
                p.line([(x, y - 8), (x + 4, y - 8)], (200, 204, 214, 255))
            else:
                p.line([(x, y), (x + 5, y + 1)], (120, 80, 50, 255), 1)
                p.rect(x + 4, y - 3, x + 9, y + 3, OUTLINE)
                p.rect(x + 5, y - 2, x + 8, y + 2, (140, 144, 156, 255))
                p.line([(x + 5, y - 2), (x + 8, y - 2)], (200, 204, 214, 255))
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
        elif f == "q":  # 等待：頭上小問號（貼著頭頂）
            x, y = hx + 8, hy - 15
            col = (250, 200, 80, 255)
            for ox, oy in ((0, 0), (1, 0), (2, 1), (1, 2), (1, 4)):
                p.px(x + ox, y + oy, col)

    return p.img.resize((CELL_W, CELL_H), Image.NEAREST)


def mirror_row(frames):
    return [f.transpose(Image.FLIP_LEFT_RIGHT) for f in frames]


def poses_for(cid):
    mei = cid == "xiaomei"
    rows = {}
    # 0 idle：呼吸與眨眼
    m0 = "smile" if mei else "small"  # 小竹平常微張著嘴、有點害羞
    rows["idle"] = [
        P(mouth=m0), P(mouth=m0), P(eyes="blink", mouth=m0), P(dy=1, mouth=m0),
        P(dy=1, hair_sway=1, mouth=m0), P(mouth=m0),
    ]
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
    rows["waving"] = [
        P(arms=("down", "wave_mid"), mouth="open", eyes="happy" if mei else "squint"),
        P(arms=("down", "wave_up"), mouth="grin", eyes="happy" if mei else "open", blush=not mei),
        P(arms=("down", "wave_mid"), mouth="open", eyes="happy" if mei else "open"),
        P(arms=("down", "wave_up"), mouth="smile", eyes="wink" if mei else "open", blush=not mei),
    ]
    # 4 jumping：預備、起跳、頂點、落下、站穩
    rows["jumping"] = [
        P(dy=2, legs="crouch", arms=("hip", "hip"), eyes="closed"),
        P(dy=-4, legs="tuck", arms=("up", "up"), mouth="open", eyes="happy"),
        P(dy=-7, legs="tuck", arms=("up", "up"), mouth="grin", eyes="happy", fx=("heart",) if mei else ()),
        P(dy=-3, legs="stand", arms=("hip", "hip"), mouth="open"),
        P(dy=1, legs="crouch", arms=("down", "down"), mouth="smile"),
    ]
    # 5 failed
    if mei:
        rows["failed"] = [
            P(eyes="wide", mouth="o", arms=("down", "down")),
            P(eyes="wide", mouth="o", arms=("face", "face"), fx=("sweat",)),
            P(eyes="sad", mouth="frown", arms=("face", "face"), fx=("sweat",)),
            P(eyes="sad", mouth="frown", arms=("droop", "droop"), dy=1, tilt=-1),
            P(eyes="sad", mouth="frown", arms=("droop", "droop"), dy=2, tilt=-1, fx=("tear",)),
            P(eyes="closed", mouth="frown", arms=("droop", "droop"), dy=2, tilt=-1, fx=("tear",)),
            P(eyes="sad", mouth="flat", arms=("droop", "droop"), dy=2, tilt=-1),
            P(eyes="sad", mouth="flat", arms=("down", "down"), dy=1),
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
        rows["waiting"] = [
            P(arms=("front", "front"), eyes="look_up", mouth="smile", fx=("q",)),
            P(arms=("front", "front"), eyes="look_up", mouth="smile", dy=-1, fx=("q",)),
            P(arms=("front", "ask"), eyes="open", mouth="open", fx=("q",), tilt=1),
            P(arms=("front", "ask"), eyes="blink", mouth="smile", fx=("q",), tilt=1),
            P(arms=("front", "front"), eyes="look_up", mouth="cat", dy=-1, fx=("q",), blush=True),
            P(arms=("front", "front"), eyes="look_up", mouth="smile", fx=("q",)),
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
            P(arms=("front", "hammer_up"), prop=("hammer", "up"), eyes="squint", mouth="flat", dy=-1),
            P(arms=("front", "hammer_down"), prop=("hammer", "down"), eyes="closed", mouth="grin", fx=("spark",)),
        ]
        # 打鐵時加上鐵砧（畫在同一格內）
        for f in rows["running"]:
            f["fx"] = tuple(f["fx"])
            f["anvil"] = True
    # 8 review：小梅瞇眼打量（指間銀針）、小竹湊近看齒輪
    if mei:
        rows["review"] = [
            P(arms=("down", "chin"), eyes="open", mouth="flat"),
            P(arms=("down", "chin"), eyes="squint", mouth="smirk", tilt=1),
            P(arms=("down", "hold"), prop=("needle",), eyes="squint", mouth="smirk", tilt=1),
            P(arms=("down", "hold"), prop=("needle",), eyes="blink", mouth="smirk", tilt=1),
            P(arms=("down", "chin"), eyes="wink", mouth="smile"),
            P(arms=("down", "chin"), eyes="open", mouth="flat"),
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
            if pose.get("anvil"):
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

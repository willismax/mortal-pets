"""用大師兄的底圖骨架改出趙活：拿掉馬尾、呆毛與髮飾，改成蓬鬆棕色短髮；
袍子改成青灰布衣、藍腰帶、燈籠褲，拿掉金邊與玉珮，膚色曬深一點。
用法：python3 tools/ref/make_zhaohuo_base.py"""
from pathlib import Path
from PIL import Image

REF = Path(__file__).resolve().parent
src = Image.open(REF / "tangbuyi_base.png").convert("RGBA")
W, H = src.size
img = src.copy()
T = (0, 0, 0, 0)
get = lambda x, y: img.getpixel((x, y)) if 0 <= x < W and 0 <= y < H else T

HAIR_DARK = {(26, 20, 22), (34, 20, 26), (16, 14, 16)}
HAIR_HI = {(56, 38, 36), (84, 58, 54), (62, 44, 42)}
ORN = {(196, 156, 84), (206, 170, 90)}

# 1. 拿掉呆毛尖端、馬尾與髮飾
for y in range(0, 3):
    for x in range(W):
        img.putpixel((x, y), T)
for y in range(H):
    for x in range(W):
        if src.getpixel((x, y))[3] == 0:
            continue
        rgb = src.getpixel((x, y))[:3]
        cut = (8 <= y <= 21 and x >= 38) or (22 <= y <= 28 and x >= 36) or (y >= 29 and x >= 33 and y < 36)
        if cut and (rgb in HAIR_DARK or rgb in HAIR_HI):
            img.putpixel((x, y), T)
        elif y < 30 and rgb in ORN | {(34, 20, 26)}:
            img.putpixel((x, y), src.getpixel((x, y - 1)) if y > 0 else T)

# 2. 頭髮改成棕色：碰到透明的是外框，裡面是棕色，原本的亮線改成挑染
OUT, BROWN, HI, STREAK = (40, 20, 24, 255), (76, 44, 38, 255), (108, 66, 50, 255), (146, 96, 64, 255)
snap = img.copy()
for y in range(30):
    for x in range(W):
        p = snap.getpixel((x, y))
        if not p[3]:
            continue
        rgb = p[:3]
        if rgb in HAIR_DARK or rgb in ORN:
            edge = any(not (snap.getpixel((x + dx, y + dy)) if 0 <= x + dx < W and 0 <= y + dy < H else T)[3]
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            img.putpixel((x, y), OUT if edge else BROWN)
        elif rgb in HAIR_HI:
            img.putpixel((x, y), STREAK if (x * 3 + y) % 7 == 0 else HI)

# 3. 膚色曬深
SKIN, SKIN_SH = (246, 185, 143, 255), (214, 148, 112, 255)
for y in range(H):
    for x in range(W):
        rgb = img.getpixel((x, y))[:3]
        if rgb == (246, 214, 192):
            img.putpixel((x, y), SKIN)
        elif rgb == (222, 184, 164):
            img.putpixel((x, y), SKIN_SH)

# 4. 衣服：青灰布衣，拿掉金邊、玉珮與流蘇；第 39 列是藍腰帶；第 44 列起是燈籠褲
CL, CL_D, CL_O = (88, 114, 136, 255), (62, 82, 104, 255), (34, 38, 54, 255)
BELT, BELT_HI = (52, 92, 160, 255), (92, 136, 200, 255)
PANTS, PANTS_D = (70, 78, 96, 255), (50, 56, 72, 255)
for y in range(30, H):
    for x in range(W):
        p = img.getpixel((x, y))
        if not p[3]:
            continue
        rgb = p[:3]
        new = {(84, 106, 152): CL, (40, 58, 92): CL_D, (26, 32, 56): CL_O,
               (196, 156, 84): CL, (206, 170, 90): CL, (130, 196, 150): CL_D, (50, 90, 70): CL_D,
               (134, 26, 30): CL_D, (104, 64, 44): (120, 64, 54, 255)}.get(rgb)
        if new:
            img.putpixel((x, y), new)
for x in range(W):
    p = img.getpixel((x, 39))
    if p[3] and p[:3] != (26, 20, 22):
        img.putpixel((x, 39), BELT_HI if x in (24, 25) else BELT)
for x in range(W):
    if img.getpixel((x, 43))[3]:
        img.putpixel((x, 43), CL_O)
LEGS = ((18, 23), (26, 31))  # 兩條燈籠褲管，中間留空
for y in (44, 45, 46):
    for x in range(W):
        if not img.getpixel((x, y))[3]:
            continue
        leg = next((l for l in LEGS if l[0] <= x <= l[1]), None)
        if leg is None:
            img.putpixel((x, y), T)
        elif x in leg:
            img.putpixel((x, y), CL_O)
        else:
            img.putpixel((x, y), PANTS_D if y == 46 or x == leg[1] - 1 else PANTS)
for x in range(W):  # 靴子上緣只留褲管下方
    if img.getpixel((x, 47))[3] and not any(l[0] <= x <= l[1] for l in LEGS):
        img.putpixel((x, 47), T)

img.save(REF / "zhaohuo_base.png")
print("wrote", REF / "zhaohuo_base.png")

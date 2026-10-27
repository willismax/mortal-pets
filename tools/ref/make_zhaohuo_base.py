"""畫趙活的 48x52 點陣底圖（依網友提供的像素參考圖，Q 版比例），輸出 tools/ref/zhaohuo_base.png。

用法：python3 tools/ref/make_zhaohuo_base.py
另外輸出一張沒畫手臂的 zhaohuo_noarms.png。
臉上的眼睛、眉毛、嘴巴不畫在底圖上，由 build_sprites.py 依動作另外畫。
"""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent / "zhaohuo_base.png"
OUT_NOARMS = OUT.with_name("zhaohuo_noarms.png")  # 抬手的動作要先把垂著的手臂抹掉，用這張補回身體
O = (34, 24, 30, 255)        # 描線
H = (96, 62, 50, 255)        # 頭髮
h = (66, 42, 38, 255)        # 頭髮暗部
L = (178, 132, 88, 255)      # 頭髮淺色挑染
S = (240, 206, 178, 255)     # 皮膚
s = (216, 172, 146, 255)     # 皮膚暗部
C = (228, 224, 214, 255)     # 內領
B = (76, 116, 178, 255)      # 藍色滾邊、腰帶
T = (88, 114, 136, 255)      # 青藍布衣
t = (66, 88, 110, 255)       # 布衣暗部
P = (56, 72, 106, 255)       # 燈籠褲
p = (42, 54, 84, 255)
R = (134, 66, 54, 255)       # 紅褐護腕
K = (88, 58, 46, 255)        # 靴子
k = (60, 40, 34, 255)

im = Image.new("RGBA", (48, 52), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
px = im.putpixel

# 頭髮後半：蓬鬆的一團，兩側髮尾往外翹
d.ellipse([14, 4, 34, 25], fill=H, outline=O)
d.polygon([(15, 15), (11, 20), (12, 21), (15, 20), (17, 19)], fill=H, outline=O)
d.polygon([(33, 15), (37, 20), (36, 21), (33, 20), (31, 19)], fill=H, outline=O)
d.line([(12, 20), (14, 19)], fill=L)
d.line([(36, 20), (34, 19)], fill=L)

# 臉
d.ellipse([17, 13, 31, 29], fill=S, outline=O)
d.line([(19, 27), (22, 28)], fill=s)  # 下巴陰影
d.line([(29, 27), (26, 28)], fill=s)

# 瀏海：分線偏左，兩片頭髮往兩側撥開，髮尾一綹綹垂在額前
left_bang = [(15, 10), (23, 7), (22, 12), (21, 16), (20, 14), (18, 18), (17, 15), (16, 17)]
right_bang = [(23, 7), (33, 10), (33, 15), (31, 19), (30, 15), (28, 17), (27, 14), (25, 15), (24, 11)]
d.polygon(left_bang, fill=H)
d.polygon(right_bang, fill=H)
d.line(left_bang[1:], fill=O)    # 只描髮尖那一圈
d.line(right_bang[2:], fill=O)
for a, b_, col in (((21, 6), (26, 6), L), ((19, 9), (17, 14), L), ((20, 10), (19, 13), L),
                   ((27, 10), (30, 14), L), ((28, 9), (31, 12), h), ((25, 9), (26, 12), h)):
    d.line([a, b_], fill=col)
# 鬢角
d.rectangle([16, 18, 17, 22], fill=H)
d.rectangle([31, 18, 32, 22], fill=H)
px((16, 23), O); px((32, 23), O)
# 鼻子
px((24, 24), s); px((23, 25), s)

# 脖子
d.rectangle([22, 29, 26, 31], fill=S)
d.line([(22, 29), (26, 29)], fill=s)

# 上衣：交領布衣
d.polygon([(19, 31), (29, 31), (31, 38), (17, 38)], fill=T, outline=O)
d.polygon([(22, 31), (26, 31), (24, 34)], fill=C)
d.line([(21, 31), (26, 37)], fill=B)       # 藍色滾邊斜過胸前
d.line([(27, 31), (25, 34)], fill=B)
d.line([(19, 33), (20, 37)], fill=t)
d.line([(29, 33), (28, 37)], fill=t)

# 腰帶
d.rectangle([18, 37, 30, 39], fill=B)
d.line([(18, 39), (30, 39)], fill=O)
d.line([(29, 40), (30, 43)], fill=B)

# 衣襬：前後兩片開衩，下緣參差
d.polygon([(17, 40), (31, 40), (32, 45), (29, 46), (27, 43), (25, 46), (22, 43), (19, 46), (16, 45)], fill=T, outline=O)
d.line([(24, 41), (25, 45)], fill=t)
d.line([(20, 41), (19, 44)], fill=t)

# 燈籠褲
d.rectangle([19, 44, 23, 47], fill=P, outline=O)
d.rectangle([26, 44, 30, 47], fill=P, outline=O)
d.line([(20, 45), (20, 46)], fill=p)
d.line([(29, 45), (29, 46)], fill=p)

# 靴子
for x0, x1 in ((19, 23), (26, 30)):
    d.rectangle([x0, 47, x1, 50], fill=K, outline=O)
    d.line([(x0 + 1, 48), (x1 - 1, 48)], fill=k)
d.line([(18, 50), (23, 50)], fill=O)
d.line([(26, 50), (31, 50)], fill=O)

im.copy().save(OUT_NOARMS)

# 兩隻手臂：袖子、紅褐護腕、手
for x0, x1 in ((16, 19), (29, 32)):
    d.rectangle([x0, 32, x1, 36], fill=T, outline=O)
    d.rectangle([x0, 35, x1, 39], fill=R, outline=O)
    d.rectangle([x0, 39, x1, 42], fill=S, outline=O)
d.line([(17, 33), (17, 36)], fill=t)
d.line([(31, 33), (31, 36)], fill=t)


im.save(OUT)
print("ok", OUT.name)

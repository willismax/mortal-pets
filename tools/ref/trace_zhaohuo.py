"""把網友提供的趙活四個姿勢像素參考圖縮成 48x52 的底圖（每格取區塊內最多的顏色）。

用法：python3 tools/ref/trace_zhaohuo.py <參考圖> tools/ref
輸出 zhaohuo_idle／cheek／laugh／wave.png；五官由 build_sprites.py 重新畫在上面。
參考圖是四個並排的全身像（站立、撫臉、捧腹大笑、揮手），切割位置寫在 segs。
"""
import sys
import numpy as np
from PIL import Image

src, outdir = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGBA")
segs = [(105, 445), (592, 925), (1064, 1402), (1539, 1905)]
names = ["idle", "cheek", "laugh", "wave"]
TOP, BOT = 52, 753
SCALE = (BOT - TOP) / 49.0  # 頭頂到腳底 49 列（第 2 到 50 列）
for (x0, x1), name in zip(segs, names):
    crop = im.crop((x0 - 40, TOP, x1 + 40, BOT))
    a = np.asarray(crop)
    rgb = Image.fromarray(a[..., :3]).quantize(28, method=Image.Quantize.MEDIANCUT)
    pal = np.array(rgb.getpalette()[:28 * 3]).reshape(-1, 3)
    q = np.asarray(rgb)
    alpha = a[..., 3] > 128
    out = Image.new("RGBA", (48, 52))
    cx = (x0 + x1) / 2 - (x0 - 40)  # 圖中身體中心
    for j in range(49):
        for i in range(48):
            sx0 = cx + (i - 24) * SCALE
            sy0 = j * SCALE
            ys, xs = slice(int(sy0), int(sy0 + SCALE)), slice(max(0, int(sx0)), max(0, int(sx0 + SCALE)))
            blk_a = alpha[ys, xs]
            if blk_a.size == 0 or blk_a.mean() < 0.5:
                continue
            vals = q[ys, xs][blk_a]
            idx = np.bincount(vals.ravel()).argmax()
            out.putpixel((i, j + 2), tuple(int(v) for v in pal[idx]) + (255,))
    out.save(f"{outdir}/zhaohuo_{name}.png")
print("ok")

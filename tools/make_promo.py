"""產生活俠傳結緣寵物的宣傳圖與動畫 GIF，輸出到 promo/。

用法：python3 tools/make_promo.py [字型檔]
需要能顯示中日韓文的字型；沒指定時依序找文泉驛正黑、Noto Sans CJK。
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "promo"
CANDIDATES = [
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "C:/Windows/Fonts/msjh.ttc",
]
FONT = sys.argv[1] if len(sys.argv) > 1 else next((f for f in CANDIDATES if Path(f).exists()), None)
if not FONT:
    sys.exit("找不到中日韓文字型，請把字型檔路徑當參數傳進來：python3 tools/make_promo.py <字型檔>")
PAPER, INK, SOFT, SEAL = (243, 234, 216), (42, 28, 36), (107, 90, 95), (184, 40, 47)
CW, CH = 192, 208
ROWS = {"idle": (0, [280, 110, 110, 140, 140, 320]), "waving": (3, [140, 140, 140, 280]),
        "jumping": (4, [140, 140, 140, 140, 280]), "failed": (5, [140] * 7 + [240]),
        "running": (7, [120] * 5 + [220]), "review": (8, [150] * 5 + [280])}

def font(size): return ImageFont.truetype(FONT, size)
def sheet(cid): return Image.open(REPO / f"codex/pets/{cid}/spritesheet.webp").convert("RGBA")
def cell(cid, row, col, scale=1):
    im = sheet(cid).crop((col * CW, row * CH, (col + 1) * CW, (row + 1) * CH))
    return im.resize((CW * scale, CH * scale), Image.NEAREST) if scale != 1 else im

def backdrop(w, h):
    im = Image.new("RGBA", (w, h), PAPER + (255,))
    ink = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ink)
    # 淡淡的水墨圓（另一層半透明疊上去）
    r = int(min(w, h) * .40)
    d.ellipse([w * .66 - r, h * .52 - r, w * .66 + r, h * .52 + r], outline=INK + (22,), width=14)
    d.ellipse([w * .66 - r + 18, h * .52 - r + 18, w * .66 + r - 18, h * .52 + r - 18], outline=INK + (12,), width=4)
    im.alpha_composite(ink)
    return im

def sprite(cid, row, col, px):
    """取一格、縮回 48x52 的像素畫布、裁掉透明邊，再以 px 倍放大（像素保持銳利）。"""
    im = cell(cid, row, col).resize((48, 52), Image.NEAREST)
    im = im.crop(im.getbbox())
    return im.resize((im.width * px, im.height * px), Image.NEAREST)

def center_text(d, x, y, text, size, fill):
    f = font(size); tw = d.textlength(text, font=f)
    d.text((x - tw / 2, y), text, font=f, fill=fill)

# 宣傳圖用的招牌姿勢：(角色, 名字, 列, 欄)
LINEUP = [("xiaomei", "小梅", 3, 1), ("xiaozhu", "小竹", 4, 2), ("xiaozhu-battle", "裂骨魔", 0, 0),
          ("xiaoshimei", "小師妹", 3, 2), ("longxiang", "龍湘", 4, 2), ("xiahoulan", "夏侯蘭", 0, 0),
          ("yeyunshang", "葉雲裳", 3, 1), ("weiju", "魏菊", 0, 3), ("tangbuyi", "大師兄", 4, 2)]

def poster(w, h, cols, name):
    im = backdrop(w, h); d = ImageDraw.Draw(im)
    pad = int(w * .06)
    title = 92 if w > 1200 else 84
    d.text((pad, int(h * .07)), "活俠傳結緣寵物", font=font(title), fill=INK)
    tw = d.textlength("活俠傳結緣寵物", font=font(title))
    sx, sy = pad + tw + 24, int(h * .07) + title * .25
    sw = d.textlength("同人二創", font=font(30))
    d.rectangle([sx, sy, sx + sw + 28, sy + 50], outline=SEAL, width=4)
    d.text((sx + 14, sy + 6), "同人二創", font=font(30), fill=SEAL)
    d.text((pad, int(h * .07) + title + 22), "把結緣角色養在 Codex 與 Claude Code 裡", font=font(40), fill=SOFT)
    d.text((pad, int(h * .07) + title + 78), "摸頭・餵食・練功・聊天，好感慢慢累積", font=font(34), fill=SOFT)
    # 角色排成 cols 欄
    rows_ = [LINEUP[i:i + cols] for i in range(0, len(LINEUP), cols)]
    px = 6 if (w - 2 * pad) / cols >= 190 else 5
    head_end = int(h * .07) + title + 130
    foot_top = h - int(h * .13)
    block = len(rows_) * (47 * px + 70)
    top = head_end + max(20, (foot_top - head_end - block) // 2)  # 角色區在標題和頁尾之間置中
    base_h = 47 * px  # 角色腳底對齊同一條線
    for ri, rowc in enumerate(rows_):
        n = len(rowc); slot = (w - 2 * pad) / n
        y_base = top + ri * (base_h + 70) + base_h
        for i, (cid, nm, r, c) in enumerate(rowc):
            sp = sprite(cid, r, c, px)
            x = int(pad + slot * i + slot / 2 - sp.width / 2)
            im.alpha_composite(sp, (x, y_base - sp.height))
            center_text(d, pad + slot * i + slot / 2, y_base + 10, nm, 32, INK)
    foot = h - int(h * .11)
    d.text((pad, foot), "willismax.github.io/mortal-pets", font=font(38), fill=SEAL)
    d.text((pad, foot + 50), "中文・日本語・한국어・English　｜　非官方同人作品，非遊戲素材", font=font(26), fill=SOFT)
    im.convert("RGB").save(OUT / name, quality=95)

poster(1600, 1000, 9, "promo-landscape.png")   # 巴哈封面、橫式
poster(1080, 1350, 5, "promo-portrait.png")    # Threads 直式 4:5

# 動畫 GIF：六人同時做招牌動作
GIF = [("xiaomei", "小梅・飛踢", "jumping"), ("xiaozhu", "小竹・擦汗", "running"),
       ("xiaoshimei", "小師妹・抖抖抖", "failed"), ("longxiang", "龍湘・雞腿劍", "jumping"),
       ("xiahoulan", "夏侯蘭・跟我來", "waving"), ("yeyunshang", "葉雲裳・欸嘿", "waving"),
       ("weiju", "魏菊・嚇到", "failed"), ("tangbuyi", "大師兄・擲鏢", "jumping")]
TICK, TOTAL = 40, 3360
sheets = {cid: sheet(cid) for cid, _, _ in GIF}
frames = []
W, H = CW * len(GIF), CH + 56
for t in range(0, TOTAL, TICK):
    im = Image.new("RGBA", (W, H), PAPER + (255,)); d = ImageDraw.Draw(im)
    for i, (cid, label, st) in enumerate(GIF):
        row, durs = ROWS[st]
        tt, col = t % sum(durs), 0
        while tt >= durs[col]:
            tt -= durs[col]; col += 1
        im.alpha_composite(sheets[cid].crop((col * CW, row * CH, (col + 1) * CW, (row + 1) * CH)), (i * CW, 0))
        center_text(d, i * CW + CW / 2, CH + 8, label, 24, INK)
    frames.append(im.convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT))
frames[0].save(OUT / "promo-moves.gif", save_all=True, append_images=frames[1:], duration=TICK, loop=0, optimize=True)
print("ok")

# 0.4.0 更新公告：新角色魏菊與番外大師兄
def update_poster(name, version, cast, w=1080, h=1350):
    im = backdrop(w, h); d = ImageDraw.Draw(im)
    pad = int(w * .07)
    d.text((pad, int(h * .06)), "新角色登場", font=font(96), fill=INK)
    tw = d.textlength("新角色登場", font=font(96))
    sx, sy = pad + tw + 24, int(h * .06) + 24
    vw = d.textlength(version, font=font(34))
    d.rectangle([sx, sy, sx + vw + 28, sy + 54], outline=SEAL, width=4)
    d.text((sx + 14, sy + 6), version, font=font(34), fill=SEAL)
    d.text((pad, int(h * .06) + 128), "活俠傳結緣寵物（Codex／Claude Code）", font=font(40), fill=SOFT)
    slot = (w - 2 * pad) / len(cast)
    y_base = int(h * .74)
    for i, (cid, nm, sub, r, c) in enumerate(cast):
        sp = sprite(cid, r, c, 11)
        x = int(pad + slot * i + slot / 2 - sp.width / 2)
        im.alpha_composite(sp, (x, y_base - sp.height))
        center_text(d, pad + slot * i + slot / 2, y_base + 18, nm, 50, INK)
        center_text(d, pad + slot * i + slot / 2, y_base + 82, sub, 30, SOFT)
    foot = h - int(h * .11)
    d.text((pad, foot), "willismax.github.io/mortal-pets", font=font(38), fill=SEAL)
    d.text((pad, foot + 50), "非官方同人作品，像素圖與台詞皆為原創", font=font(26), fill=SOFT)
    im.convert("RGB").save(OUT / name, quality=95)

update_poster("update-0.4.0.png", "v0.4.0",
              [("weiju", "魏菊", "玄功門掌門・捧手爐", 0, 0), ("tangbuyi", "大師兄", "番外・飛俠唐布衣", 7, 2)])

UPD = [("weiju", "魏菊・害羞冒煙", "waving"), ("tangbuyi", "大師兄・彈金錢", "idle"), ("tangbuyi", "大師兄・連發金錢鏢", "running")]
frames = []
W2, H2 = CW * len(UPD), CH + 56
sheets = {cid: sheet(cid) for cid, _, _ in UPD}
for t in range(0, TOTAL, TICK):
    im = Image.new("RGBA", (W2, H2), PAPER + (255,)); d = ImageDraw.Draw(im)
    for i, (cid, label, st) in enumerate(UPD):
        row, durs = ROWS[st]
        tt, col = t % sum(durs), 0
        while tt >= durs[col]:
            tt -= durs[col]; col += 1
        im.alpha_composite(sheets[cid].crop((col * CW, row * CH, (col + 1) * CW, (row + 1) * CH)), (i * CW, 0))
        center_text(d, i * CW + CW / 2, CH + 8, label, 22, INK)
    frames.append(im.convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT))
frames[0].save(OUT / "update-0.4.0.gif", save_all=True, append_images=frames[1:], duration=TICK, loop=0, optimize=True)
print("ok")

"""產生 0.4.0 更新介紹短影片（Threads 不支援 GIF），輸出 promo/update-0.4.0.mp4。

用法：python3 tools/make_video.py [字型檔]
需要 ffmpeg 與能顯示中文的字型（同 make_promo.py）。
"""
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "promo" / "update-0.4.0.mp4"
CANDIDATES = [
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "C:/Windows/Fonts/msjh.ttc",
]
FONT = sys.argv[1] if len(sys.argv) > 1 else next((f for f in CANDIDATES if Path(f).exists()), None)
if not FONT:
    sys.exit("找不到中文字型，請把字型檔路徑當參數傳進來：python3 tools/make_video.py <字型檔>")

W, H, FPS = 1080, 1350, 30  # 4:5，Threads 動態上完整顯示
PAPER, INK, SOFT, SEAL = (243, 234, 216), (42, 28, 36), (107, 90, 95), (184, 40, 47)
CW, CH = 192, 208
# 各狀態在 spritesheet 的列與每格毫秒數（和 Codex 播放的節奏一致）
ROWS = {"idle": (0, [280, 110, 110, 140, 140, 320]), "waving": (3, [140, 140, 140, 280]),
        "jumping": (4, [140, 140, 140, 140, 280]), "failed": (5, [140] * 7 + [240]),
        "running": (7, [120] * 5 + [220]), "review": (8, [150] * 5 + [280])}

_fonts = {}
def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT, size)
    return _fonts[size]

_sheets = {}
def frame_of(cid, state, ms, scale):
    """依經過的毫秒數取該狀態動畫的一格，放大 scale 倍（像素保持銳利）。"""
    if cid not in _sheets:
        _sheets[cid] = Image.open(REPO / f"codex/pets/{cid}/spritesheet.webp").convert("RGBA")
    row, durs = ROWS[state]
    t, col = ms % sum(durs), 0
    while t >= durs[col]:
        t -= durs[col]; col += 1
    im = _sheets[cid].crop((col * CW, row * CH, (col + 1) * CW, (row + 1) * CH))
    return im.resize((CW * scale, CH * scale), Image.NEAREST)

def backdrop():
    im = Image.new("RGBA", (W, H), PAPER + (255,))
    ink = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ink)
    r = int(W * .42)
    d.ellipse([W * .5 - r, H * .5 - r, W * .5 + r, H * .5 + r], outline=INK + (22,), width=14)
    im.alpha_composite(ink)
    return im

def center(d, y, text, size, fill):
    tw = d.textlength(text, font=font(size))
    d.text(((W - tw) / 2, y), text, font=font(size), fill=fill)

def seal(d, x, y, text, size):
    tw = d.textlength(text, font=font(size))
    d.rectangle([x, y, x + tw + 28, y + size + 20], outline=SEAL, width=4)
    d.text((x + 14, y + 8), text, font=font(size), fill=SEAL)

BG = backdrop()

# 場景：(秒數, 畫法)。畫法收到場景內經過的毫秒數，回傳一張圖
def title(ms):
    im = BG.copy(); d = ImageDraw.Draw(im)
    center(d, 150, "活俠傳結緣寵物", 92, INK)
    tw = d.textlength("v0.4.0 更新", font=font(40))
    seal(d, (W - tw - 28) / 2, 270, "v0.4.0 更新", 40)
    for i, cid in enumerate(("weiju", "tangbuyi")):
        sp = frame_of(cid, "idle", ms, 3)
        im.alpha_composite(sp, (int(W / 2 + (i * 2 - 1) * 250 - sp.width / 2), 430))
    center(d, 1100, "新角色登場！", 64, SEAL)
    center(d, 1190, "New characters for Codex & Claude Code", 34, SOFT)
    return im

def showcase(cid, name, sub, state, caption, caption_en):
    def draw(ms):
        im = BG.copy(); d = ImageDraw.Draw(im)
        center(d, 90, name, 84, INK)
        center(d, 195, sub, 36, SOFT)
        sp = frame_of(cid, state, ms, 4)
        im.alpha_composite(sp, (int((W - sp.width) / 2), 300))
        center(d, 1150, caption, 56, SEAL)
        center(d, 1230, caption_en, 32, SOFT)
        return im
    return draw

def ending(ms):
    im = BG.copy(); d = ImageDraw.Draw(im)
    center(d, 110, "網頁直接玩", 72, INK)
    center(d, 210, "willismax.github.io/mortal-pets", 46, SEAL)
    for i, (cid, st) in enumerate((("weiju", "waving"), ("tangbuyi", "waving"))):
        sp = frame_of(cid, st, ms, 3)
        im.alpha_composite(sp, (int(W / 2 + (i * 2 - 1) * 250 - sp.width / 2), 330))
    center(d, 1000, "已安裝的人：", 38, INK)
    center(d, 1055, "claude plugin marketplace update mortal-pets", 30, SOFT)
    center(d, 1100, "claude plugin update mortal-buddy@mortal-pets", 30, SOFT)
    center(d, 1175, "中文・日本語・한국어・English", 34, INK)
    center(d, 1240, "非官方同人作品，像素圖與台詞皆為原創", 28, SOFT)
    return im

W_SUB, T_SUB = "玄功門掌門・魏菊", "番外・飛俠 唐布衣"
SCENES = [
    (2.6, title),
    (2.4, showcase("weiju", "魏菊", W_SUB, "idle", "捧著小竹打的手爐", "Hugging her hand warmer")),
    (2.2, showcase("weiju", "魏菊", W_SUB, "waving", "被誇到頭頂冒煙", "Blushing until she steams")),
    (2.4, showcase("weiju", "魏菊", W_SUB, "failed", "嚇到摀嘴尖叫……再恢復端莊", "Startled, then composed again")),
    (2.6, showcase("tangbuyi", "大師兄", T_SUB, "idle", "彈金錢、接住、眨眼", "Flicks a coin and catches it")),
    (2.4, showcase("tangbuyi", "大師兄", T_SUB, "running", "連發金錢鏢！", "Gold-coin darts, rapid fire")),
    (2.0, showcase("tangbuyi", "大師兄", T_SUB, "jumping", "飛俠一躍", "The Flying Knight leaps")),
    (2.0, showcase("tangbuyi", "大師兄", T_SUB, "waving", "「師弟，有了！」", "\"Little brother, I've got it!\"")),
    (4.0, ending),
]
FADE = 0.25  # 場景之間的淡入淡出秒數

def main():
    OUT.parent.mkdir(exist_ok=True)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
         "-movflags", "+faststart", str(OUT)],
        stdin=subprocess.PIPE)
    prev_last = None
    for secs, draw in SCENES:
        n = int(secs * FPS)
        for i in range(n):
            im = draw(int(i * 1000 / FPS)).convert("RGB")
            if prev_last is not None and i < FADE * FPS:  # 和上一場景交叉淡化
                im = Image.blend(prev_last, im, (i + 1) / (FADE * FPS))
            ff.stdin.write(im.tobytes())
        prev_last = draw(int((n - 1) * 1000 / FPS)).convert("RGB")
    ff.stdin.close()
    ff.wait()
    print("ok", OUT.relative_to(REPO))

main()

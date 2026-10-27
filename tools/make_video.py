"""產生宣傳短影片（Threads 不支援 GIF），輸出到 promo/。

用法：python3 tools/make_video.py [字型檔]
  promo/update-0.4.0.mp4   0.4.0 更新介紹（4:5，Threads 動態）
  promo/update-0.5.0.mp4   0.5.0 更新介紹（4:5）
  promo/shorts.mp4         全角色介紹（9:16，YouTube Shorts、IG Reels、Threads）
需要 ffmpeg 與能顯示中文的字型（同 make_promo.py）。
"""
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
CANDIDATES = [
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "C:/Windows/Fonts/msjh.ttc",
]
FONT = sys.argv[1] if len(sys.argv) > 1 else next((f for f in CANDIDATES if Path(f).exists()), None)
if not FONT:
    sys.exit("找不到中文字型，請把字型檔路徑當參數傳進來：python3 tools/make_video.py <字型檔>")

FPS = 30
PAPER, INK, SOFT, SEAL = (243, 234, 216), (42, 28, 36), (107, 90, 95), (184, 40, 47)
CW, CH = 192, 208
# 各狀態在 spritesheet 的列與每格毫秒數（和 Codex 播放的節奏一致）
ROWS = {"idle": (0, [280, 110, 110, 140, 140, 320]), "waving": (3, [140, 140, 140, 280]),
        "jumping": (4, [140, 140, 140, 140, 280]), "failed": (5, [140] * 7 + [240]),
        "waiting": (6, [150] * 5 + [260]), "running": (7, [120] * 5 + [220]),
        "review": (8, [150] * 5 + [280])}
FADE = 0.25  # 場景之間的淡入淡出秒數

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


class Canvas:
    """一種影片尺寸的背景與排版工具。"""

    def __init__(self, w, h):
        self.w, self.h = w, h
        im = Image.new("RGBA", (w, h), PAPER + (255,))
        ink = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(ink)
        r = int(w * .42)  # 淡淡的水墨圓
        d.ellipse([w * .5 - r, h * .5 - r, w * .5 + r, h * .5 + r], outline=INK + (22,), width=14)
        im.alpha_composite(ink)
        self.bg = im

    def new(self):
        im = self.bg.copy()
        return im, ImageDraw.Draw(im)

    def center(self, d, y, text, size, fill):
        tw = d.textlength(text, font=font(size))
        d.text(((self.w - tw) / 2, y), text, font=font(size), fill=fill)

    def seal(self, d, y, text, size):
        tw = d.textlength(text, font=font(size))
        x = (self.w - tw - 28) / 2
        d.rectangle([x, y, x + tw + 28, y + size + 20], outline=SEAL, width=4)
        d.text((x + 14, y + 8), text, font=font(size), fill=SEAL)

    def paste_center(self, im, sp, top, dx=0):
        im.alpha_composite(sp, (int((self.w - sp.width) / 2 + dx), top))


def render(cv, scenes, out):
    """scenes：(秒數, 畫法) 的清單，畫法收到場景內經過的毫秒數、回傳一張圖。"""
    out.parent.mkdir(exist_ok=True)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{cv.w}x{cv.h}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
         "-movflags", "+faststart", str(out)],
        stdin=subprocess.PIPE)
    prev_last = None
    for secs, draw in scenes:
        n = int(secs * FPS)
        for i in range(n):
            im = draw(int(i * 1000 / FPS)).convert("RGB")
            if prev_last is not None and i < FADE * FPS:  # 和上一場景交叉淡化
                im = Image.blend(prev_last, im, (i + 1) / (FADE * FPS))
            ff.stdin.write(im.tobytes())
        prev_last = draw(int((n - 1) * 1000 / FPS)).convert("RGB")
    ff.stdin.close()
    ff.wait()
    print("ok", out.relative_to(REPO))


# ---------- 0.4.0 更新介紹（4:5） ----------
def update_video():
    cv = Canvas(1080, 1350)

    def title(ms):
        im, d = cv.new()
        cv.center(d, 150, "活俠傳結緣寵物", 92, INK)
        cv.seal(d, 270, "v0.4.0 更新", 40)
        for i, cid in enumerate(("weiju", "tangbuyi")):
            cv.paste_center(im, frame_of(cid, "idle", ms, 3), 430, (i * 2 - 1) * 250)
        cv.center(d, 1100, "新角色登場！", 64, SEAL)
        cv.center(d, 1190, "New characters for Codex & Claude Code", 34, SOFT)
        return im

    def showcase(cid, name, sub, state, caption, caption_en):
        def draw(ms):
            im, d = cv.new()
            cv.center(d, 90, name, 84, INK)
            cv.center(d, 195, sub, 36, SOFT)
            cv.paste_center(im, frame_of(cid, state, ms, 4), 300)
            cv.center(d, 1150, caption, 56, SEAL)
            cv.center(d, 1230, caption_en, 32, SOFT)
            return im
        return draw

    def ending(ms):
        im, d = cv.new()
        cv.center(d, 110, "網頁直接玩", 72, INK)
        cv.center(d, 210, "willismax.github.io/mortal-pets", 46, SEAL)
        for i, cid in enumerate(("weiju", "tangbuyi")):
            cv.paste_center(im, frame_of(cid, "waving", ms, 3), 330, (i * 2 - 1) * 250)
        cv.center(d, 1000, "已安裝的人：", 38, INK)
        cv.center(d, 1055, "claude plugin marketplace update mortal-pets", 30, SOFT)
        cv.center(d, 1100, "claude plugin update mortal-buddy@mortal-pets", 30, SOFT)
        cv.center(d, 1175, "中文・日本語・한국어・English", 34, INK)
        cv.center(d, 1240, "非官方同人作品，像素圖與台詞皆為原創", 28, SOFT)
        return im

    w_sub, t_sub = "玄功門掌門・魏菊", "番外・飛俠 唐布衣"
    render(cv, [
        (2.6, title),
        (2.4, showcase("weiju", "魏菊", w_sub, "idle", "捧著小竹打的手爐", "Hugging her hand warmer")),
        (2.2, showcase("weiju", "魏菊", w_sub, "waving", "被誇到頭頂冒煙", "Blushing until she steams")),
        (2.4, showcase("weiju", "魏菊", w_sub, "failed", "嚇到摀嘴尖叫……再恢復端莊", "Startled, then composed again")),
        (2.6, showcase("tangbuyi", "大師兄", t_sub, "idle", "彈金錢、接住、眨眼", "Flicks a coin and catches it")),
        (2.4, showcase("tangbuyi", "大師兄", t_sub, "running", "連發金錢鏢！", "Gold-coin darts, rapid fire")),
        (2.0, showcase("tangbuyi", "大師兄", t_sub, "jumping", "飛俠一躍", "The Flying Knight leaps")),
        (2.0, showcase("tangbuyi", "大師兄", t_sub, "waving", "「師弟，有了！」", "\"Little brother, I've got it!\"")),
        (4.0, ending),
    ], REPO / "promo" / "update-0.4.0.mp4")


# ---------- 0.5.0 更新介紹（4:5） ----------
def update_video_050():
    cv = Canvas(1080, 1350)
    duo = ("shangguanying", "zhaohuo")

    def title(ms):
        im, d = cv.new()
        cv.center(d, 150, "活俠傳結緣寵物", 92, INK)
        cv.seal(d, 270, "v0.5.0 更新", 40)
        for i, cid in enumerate(duo):
            cv.paste_center(im, frame_of(cid, "idle", ms, 3), 430, (i * 2 - 1) * 250)
        cv.center(d, 1100, "新角色登場！", 64, SEAL)
        cv.center(d, 1190, "New characters for Codex & Claude Code", 34, SOFT)
        return im

    def showcase(cid, name, sub, state, caption, caption_en):
        def draw(ms):
            im, d = cv.new()
            cv.center(d, 90, name, 84, INK)
            cv.center(d, 195, sub, 36, SOFT)
            cv.paste_center(im, frame_of(cid, state, ms, 4), 300)
            cv.center(d, 1150, caption, 56, SEAL)
            cv.center(d, 1230, caption_en, 32, SOFT)
            return im
        return draw

    def ending(ms):
        im, d = cv.new()
        cv.center(d, 110, "網頁直接玩", 72, INK)
        cv.center(d, 210, "willismax.github.io/mortal-pets", 46, SEAL)
        for i, cid in enumerate(duo):
            cv.paste_center(im, frame_of(cid, "waving", ms, 3), 330, (i * 2 - 1) * 250)
        cv.center(d, 1000, "已安裝的人：", 38, INK)
        cv.center(d, 1055, "claude plugin marketplace update mortal-pets", 30, SOFT)
        cv.center(d, 1100, "claude plugin update mortal-buddy@mortal-pets", 30, SOFT)
        cv.center(d, 1175, "中文・日本語・한국어・English", 34, INK)
        cv.center(d, 1240, "非官方同人作品，像素圖與台詞皆為原創", 28, SOFT)
        return im

    y_sub, z_sub = "福州上官千金・上官螢", "番外・唐門醜俠 趙活"
    render(cv, [
        (2.6, title),
        (2.4, showcase("shangguanying", "上官螢", y_sub, "idle", "叉腰抬下巴，「哼」", "Hands on hips: \"Hmph.\"")),
        (2.4, showcase("shangguanying", "上官螢", y_sub, "jumping", "眼冒愛心、臉紅冒煙", "Heart eyes, steaming cheeks")),
        (2.6, showcase("shangguanying", "上官螢", y_sub, "failed", "氣到握拳……才沒哭", "Fuming… and definitely not crying")),
        (2.2, showcase("shangguanying", "上官螢", y_sub, "running", "捧著帳本對帳", "Balancing the family ledgers")),
        (2.6, showcase("zhaohuo", "趙活", z_sub, "idle", "撫著臉，越看越帥", "Admiring his own face")),
        (3.0, showcase("zhaohuo", "趙活", z_sub, "jumping", "蘭花手大笑、撫臉拋媚眼", "Laughing, then blowing a kiss")),
        (2.4, showcase("zhaohuo", "趙活", z_sub, "review", "決鬥臉！", "The duel face!")),
        (2.4, showcase("zhaohuo", "趙活", z_sub, "failed", "中招被揍，鼻青臉腫", "Took a hit, black eye and all")),
        (4.0, ending),
    ], REPO / "promo" / "update-0.5.0.mp4")


# ---------- 全角色介紹（9:16） ----------
# (角色, 名字, 稱號, 招牌動作的狀態, 中文字幕, 英文字幕)
CAST = [
    ("xiaomei", "小梅", "崆峒飛天門嫡傳女弟子", "jumping", "招牌飛踢！", "Xiaomei: the flying kick"),
    ("xiaozhu", "小竹", "崆峒鐵拳門・人稱「裂骨魔」", "running", "打鐵打到擦汗", "Xiaozhu: forging, wiping her sweat"),
    ("xiaozhu-battle", "裂骨魔", "小竹的戰鬥裝束", "jumping", "機關臂扛巨劍＋虎頭盾", "The Bone-Breaker: greatsword and tiger shield"),
    ("xiaoshimei", "小師妹", "唐門掌門獨生女", "failed", "迷路了……抖抖抖", "Junior Sister: lost again, trembling"),
    ("longxiang", "龍湘", "錦香宮・人稱「雞腿女俠」", "jumping", "以雞腿為劍！", "Long Xiang: the drumstick sword"),
    ("xiahoulan", "夏侯蘭", "崆峒奪魄門・人稱「奪魄幽蘭」", "waving", "「懶徒兒，跟我來」", "Xiahou Lan: \"Lazy disciple, follow me.\""),
    ("yeyunshang", "葉雲裳", "點蒼明珠", "waving", "欸嘿～", "Ye Yunshang: \"Ehehe~\""),
    ("weiju", "魏菊", "崆峒玄功門・當代掌門", "waving", "害羞到頭頂冒煙", "Wei Ju: blushing until she steams"),
    ("shangguanying", "上官螢", "福州上官世家・人稱「上官千金」", "jumping", "眼冒愛心、頭頂冒煙", "Shangguan Ying: hearts and steam"),
    ("tangbuyi", "大師兄", "番外・飛俠 唐布衣", "running", "連發金錢鏢！", "Senior Brother: gold-coin darts"),
    ("zhaohuo", "趙活", "番外・主角本人，人稱「唐門醜俠」", "jumping", "計畫通！", "Zhao Huo himself: “Just as planned!”"),
]


def shorts_video():
    cv = Canvas(1080, 1920)

    def hook(ms):
        # 開頭 2 秒要抓住目光：全部角色一起出場（每排最多 4 位）
        im, d = cv.new()
        cv.center(d, 170, "寫程式時", 96, INK)
        cv.center(d, 290, "有她們陪著", 96, SEAL)
        for i, (cid, *_rest) in enumerate(CAST):
            r, c = divmod(i, 4)
            n = min(4, len(CAST) - r * 4)
            sp = frame_of(cid, "idle", ms + i * 90, 2)
            im.alpha_composite(sp, (int(cv.w / 2 + (c - (n - 1) / 2) * 250 - sp.width / 2), 470 + r * 400))
        cv.center(d, 1720, "活俠傳結緣寵物（同人）", 52, INK)
        cv.center(d, 1800, "Legend of Mortal desktop pets (fan-made)", 34, SOFT)
        return im

    def card(cid, name, title, state, zh, en):
        def draw(ms):
            im, d = cv.new()
            cv.center(d, 230, name, 120, INK)
            cv.center(d, 380, title, 44, SOFT)
            cv.paste_center(im, frame_of(cid, state, ms, 5), 520)
            cv.center(d, 1620, zh, 72, SEAL)
            cv.center(d, 1730, en, 36, SOFT)
            return im
        return draw

    def how(ms):
        im, d = cv.new()
        cv.center(d, 200, "跟著你的工作反應", 80, INK)
        steps = [("running", "跑指令時陪你"), ("failed", "失敗時安慰你"), ("waving", "完成時誇你")]
        for i, (st, txt) in enumerate(steps):
            sp = frame_of("xiaomei", st, ms, 2)
            y = 400 + i * 440
            im.alpha_composite(sp, (120, y))
            d.text((560, y + 170), txt, font=font(64), fill=SEAL if i == 1 else INK)
        cv.center(d, 1760, "摸頭・餵食・練功・聊天，好感慢慢累積", 44, SOFT)
        return im

    def ending(ms):
        im, d = cv.new()
        cv.center(d, 200, "網頁直接玩", 104, INK)
        cv.center(d, 350, "willismax.github.io/mortal-pets", 58, SEAL)
        for i, cid in enumerate(("xiaomei", "xiaozhu", "tangbuyi")):
            cv.paste_center(im, frame_of(cid, "waving", ms, 3), 560, (i - 1) * 330)
        cv.center(d, 1300, "Codex・Claude Code 寵物", 60, INK)
        cv.center(d, 1400, "/plugin install mortal-buddy", 40, SOFT)
        cv.center(d, 1450, "--marketplace willismax/mortal-pets", 40, SOFT)
        cv.center(d, 1580, "中文・日本語・한국어・English", 48, INK)
        cv.center(d, 1700, "非官方同人作品，像素圖與台詞皆為原創", 34, SOFT)
        return im

    render(cv, [(2.5, hook)] + [(2.6, card(*c)) for c in CAST] + [(4.0, how), (4.5, ending)],
           REPO / "promo" / "shorts.mp4")


if __name__ == "__main__":
    update_video()
    update_video_050()
    shorts_video()

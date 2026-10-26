# 活俠傳結緣寵物（同人）

把《活俠傳》的結緣角色做成 **Codex 寵物**和 **Claude Code 寵物**，並依角色個性寫了互動對話。第一批是崆峒四姝裡的小梅（虞小梅）和小竹（郁竹）。

- 線上試玩：<https://willismax.github.io/demo/mortal-pets/>（直接開 `index.html` 也可以）
- 非官方二創：角色設定整理自公開資料；像素圖、台詞都是原創，沒有使用遊戲素材或原文。

## 目錄

```
mortal-pets/
├── index.html                    互動網頁：摸頭、餵食、練功、送禮、聊天、9 種動畫預覽
├── install.sh                    安裝 Codex 寵物／skill／通知，以及 Claude Code status line
├── codex/pets/<id>/              Codex 寵物：xiaomei、xiaozhu、xiaozhu-battle（pet.json + spritesheet.webp）
├── codex/qa/                     總覽圖與各狀態 GIF，方便檢查動畫
├── claude-plugin/mortal-buddy/   Claude Code 外掛
│   ├── hooks/hooks.json          依工作狀態切換心情與台詞
│   ├── commands/                 /mortal-buddy:pick、pet、talk、roleplay、status、mute
│   ├── skills/xiaomei|xiaozhu/   角色卡（Codex 也能用）
│   └── scripts/
│       ├── buddy.cjs             hook、status line、互動指令、Codex 通知共用的程式
│       └── characters.js         角色資料與台詞（網頁、Claude、Codex 共用）
└── tools/build_sprites.py        產生像素 spritesheet
```

## Codex 寵物

```bash
cd mortal-pets && ./install.sh codex
```

會把三隻寵物（小梅、小竹、小竹・裂骨魔）複製到 `~/.codex/pets/`，角色卡複製到 `~/.codex/skills/`。接著到 Codex 的 Settings → Pets → Refresh，選「小梅」或「小竹」；對話中可用 `/pet` 叫出或收起寵物。

想在每輪完成時收到角色的系統通知，在 `~/.codex/config.toml` 加上（安裝腳本會印出實際路徑）：

```toml
notify = ["node", "/home/你/.mortal-buddy/bin/buddy.cjs", "codex-notify"]
```

spritesheet 照 Codex 的固定格式：8 欄 × 9 列、每格 192×208、未使用的格子全透明。每列的動作如下：

| 列 | 狀態 | 小梅 | 小竹 |
| --- | --- | --- | --- |
| 0 | idle | 呼吸、眨眼、髮絲輕晃 | 半垂著眼睏睏地發呆 |
| 1–2 | running-right / left | 輕功小跑 | 小碎步 |
| 3 | waving | 笑著揮手、眨眼 | 害羞揮手、臉紅 |
| 4 | jumping | 蹲下、起跳、冒愛心 | 一手握拳、一手高舉大鐵鎚大喊 💢 |
| 5 | failed | 摀臉、掉淚 | 錘子掉了、淚眼汪汪 |
| 6 | waiting | 雙手合十等你點頭 | 捧著木頭青蛙問你要不要 |
| 7 | running（工作中） | 攪鍋煮菜、冒熱氣 | 掄錘打鐵、火星四濺 |
| 8 | review | 托腮打量，指間閃過一根銀針 | 湊近瞇眼看齒輪 |

修改造型後重新產生：

```bash
python3 tools/build_sprites.py --preview   # 需要 Pillow；--preview 會更新 codex/qa/
```

## Claude Code 寵物

Claude Code 內建的 `/buddy` 物種是依帳號固定的，無法自訂，所以這裡做成外掛：

```text
/plugin install mortal-buddy --marketplace willismax/demo
```

（舊版 Claude Code 請分兩步：`/plugin marketplace add willismax/demo`，再 `/plugin install mortal-buddy@willismax-demo`。）

裝好後她會跟著你的工作狀態反應：

| 事件 | 心情 | 例子 |
| --- | --- | --- |
| 開新對話 | 打招呼 | 小竹(¬_¬)「……（瞇眼）誰？喔，是你啊。靠近一點，我看不清楚。」 |
| 送出問題 | 審視 | 小梅(￢‿￢)「讓我瞧瞧……嗯，這裡藏了一根針呢。」 |
| 執行工具 | 工作中 | 小竹(ง'̀-'́)ง「叮、叮、噹——別吵，火候正好。」 |
| 指令失敗 | 失敗 | 小梅(；ω；)「哎呀，炸鍋了？沒事，失敗的菜我也能改成佳餚。」 |
| 等你允許 | 等待 | 小梅(・∀・)?「欸，等你點頭呢。別讓姑娘家等太久喔。」 |
| 完成一輪 | 完成（好感 +1） | 小竹(•̀ᴗ•́)و「打好了。……不是兇你，我只是沒睡。」 |

互動指令：

| 指令 | 說明 |
| --- | --- |
| `/mortal-buddy:pick xiaozhu` | 換寵物（`xiaomei`／`xiaozhu`） |
| `/mortal-buddy:pet feed` | `pet` 摸頭、`feed` 餵食、`train` 練功（各 +1）、`gift` 送禮（+3），同一種互動一分鐘內只算一次 |
| `/mortal-buddy:talk` | 她出題，用 `/mortal-buddy:talk 2` 回答，答案會加減好感 |
| `/mortal-buddy:roleplay 今天好累` | 載入角色卡，讓她用自己的口吻回你 |
| `/mortal-buddy:status` | 查看兩人的好感與階段 |
| `/mortal-buddy:mute` | 開關對話中的反應訊息 |

好感分四個階段：初識（0）、熟識（10）、知己（30）、結緣（60）。到了「知己」，深夜（23:00–05:00）她偶爾會說出藏在心底的話。

想讓她一直待在畫面下方，執行 `./install.sh statusline`，依指示把 status line 加進 `~/.claude/settings.json`：

```text
小梅(๑˃ᴗ˂)ﻭ「你寫你的，我在旁邊揉麵團，誰也不吵誰～」  ♥♥♡♡♡ 知己 31
```

狀態存在 `~/.mortal-buddy/state.json`，Claude Code 與 Codex 通知共用同一份好感。

## 素材整理

### 小梅（虞小梅）

- 崆峒派飛天門當代嫡傳女弟子，「崆峒四姝」之一（虞小梅、夏侯蘭、郁竹、魏菊）。四門嫡傳女弟子中聲望最高，第一掌派夫人的位子幾乎被認定是她的。
- 紅白衣裙，「恰似雪裡梅花」。天真爛漫、活潑愛笑、擅長交朋友。
- 有時會用「本梅」自稱，只有這時候說的話才是真心話。
- 廚藝高超：能把趙活失敗的菜改成佳餚，做的茶點菓子很受鄉親歡迎。
- 結緣線可利用留學期間的跑步、練功事件推進。
- 劇透：真實身分是千燈樓培養的刺客（新任千面人魔候補），殺人技巧由千燈樓「五炷香」金烏上人調教。官方日文角色介紹也寫她「似乎有隱藏的另一面」。

設計對應：紅白衣裙與梅花髮簪；工作時煮菜；審視時笑著托腮、指間一根銀針（千燈樓伏筆）；平常用「我」，真心話才用「本梅」。

### 小竹（郁竹）

- 崆峒派鐵拳門掌門的嫡傳女弟子，「崆峒四姝」之一，江湖人稱「裂骨魔」。
- 專司冶煉鐵器，從小鑽研機關巧術，有靈感就廢寢忘食。接手大鐵鋪鑄農具、打兵器，她的兵器在崆峒要排隊好幾年。
- 身形嬌小卻力大無窮。眼神兇是因為睡眠不足加上近視，其實性情純良。
- 個性誠實，所以撒嬌時殺傷力特別高；喜歡做玩具。
- 結緣線重點在留學期間跑鐵拳巷；會請趙活陪她返鄉「演一場戲」。

設計對應（參考官方立繪）：卡其頭巾與領巾、淺綠短袖上衣、長工作手套、卡其長圍裙、腦後一小撮頭髮、臉頰常帶紅暈、眼皮半垂的琥珀色睏眼；工作時打鐵；等待時捧著自己做的木頭青蛙；審視時湊近看齒輪；說話直、短、常停頓。

另有戰鬥造型 **小竹・裂骨魔**（`codex/pets/xiaozhu-battle/`）：鐵網護甲；右手（畫面左邊）的前臂是一整塊機關板，頂端三隻爪子抓著刻紅紋的巨劍高舉過頭；左手（畫面右邊）拿虎頭盾。兩者在背後靠虎紋肩甲與背包相連，胸前沒有背帶。開心時巨劍舉更高，失敗時劍尖垂下。日常版開心時會像官方圖那樣一手握拳、一手高舉大鐵鎚大喊。兩種造型的小竹都是圓滾滾的身材（圓身體、粗手腳、圓臉頰）。網頁上可以切換兩種造型。

### 其他結緣角色

網頁上已預留小師妹、龍湘、夏侯蘭。新增角色的步驟：

1. 在 `tools/build_sprites.py` 的 `CHARACTERS` 加配色與特徵，在 `poses_for()` 設計各狀態動作。
2. 在 `scripts/characters.js` 加角色資料、各心情台詞與聊天題目。
3. 在 `skills/` 加角色卡，然後執行 `python3 tools/build_sprites.py --preview`。

### 參考來源

- [活俠傳日本語制作会：虞小梅角色介紹（X）](https://x.com/Mortal_jp/status/1971907682823995814)
- [聯合新聞網：虞小梅、郁竹感情線將同步推出](https://game.udn.com/game/story/122089/9203339)
- [聯合新聞網：原先無法與崆峒四姝全數結緣？](https://game.udn.com/game/story/122089/8097264)
- [聯合新聞網：虞小梅「屍心蠱」關鍵文本](https://game.udn.com/game/story/122089/9831528)
- [酷時尚：〈崆峒神威〉更新開放虞小梅、郁竹結緣線](https://www.cool-style.com.tw/wd2/archives/1352050)
- [4Gamers：崆峒神威 DLC 攻略](https://www.4gamers.com.tw/news/detail/82729/legend-of-mortal-kongtong-shenwei-dlc-guide)
- [LoM Wiki：虞小梅](https://smilin.net/LoM-wiki/people/characters/girl3.html)、[郁竹](https://smilin.net/LoM-wiki/people/characters/girl6.html)
- [Reko Wiki：活俠傳登場人物一覽](https://rekowiki.org/wiki/%E6%B4%BB%E4%BF%A0%E5%82%B3/%E7%99%BB%E5%A0%B4%E4%BA%BA%E7%89%A9%E4%B8%80%E8%A6%BD-Part1)
- [巴哈姆特：為什麼小梅又瘋又色？](https://forum.gamer.com.tw/C.php?bsn=73317&snA=4436)、[梅竹線心得](https://forum.gamer.com.tw/C.php?bsn=73317&snA=4443)、[小竹路線討論串](https://forum.gamer.com.tw/C.php?bsn=73317&snA=4304)
- [TWGameX：虞小梅線完整解析](https://twgamex.com/games/%e6%b4%bb%e4%bf%a0%e5%82%b3/888/)
- Codex 寵物格式：[openai/skills hatch-pet](https://github.com/openai/skills/tree/main/skills/.curated/hatch-pet)（`references/animation-rows.md`）

## 版權

《活俠傳》（Legend of Mortal）及其角色的著作權屬於原開發商與發行商。本資料夾是非官方同人作品，程式碼依 repo 的 MIT 授權釋出。

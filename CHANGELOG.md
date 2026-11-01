# 更新紀錄 / Changelog

## 0.5.1

- 修正多個 hook 同時執行（subagent、背景 agent、多個 Claude Code 對話）時，`state.json` 被重設回預設值、寵物變回小梅、好感歸零的問題（#7）：
  - 讀 → 改 → 寫整段加上檔案鎖（`state.lock`），不會再有行程拿舊狀態蓋掉剛 `pick` 的角色或剛加的好感；拿鎖的行程當掉時，鎖超過 5 秒自動收回。
  - 先寫暫存檔再換名，讀的人不會讀到寫一半的檔案；Windows 上換名暫時失敗會重試，失敗就清掉暫存檔。
  - 檔案在但讀不到時不覆寫；內容真的損毀時備份成 `state.json.bad` 再從預設值重來，不會從此卡住不存。
  - hook 沒改到狀態就不寫檔；清掉被中斷而殘留的暫存檔。
- 跳過幾版才更新的人，開新對話時會把中間每一版的新內容都說一次。
- Fixed `state.json` resetting to defaults (pet back to Xiaomei, affection cleared) when many hooks run concurrently (#7): the read-modify-write is now locked, writes are atomic with Windows rename retries, unreadable files are never overwritten, and corrupt files are backed up to `state.json.bad`.

## 0.5.0

- 新增上官螢（福州上官世家獨女、人稱「上官千金」）：叉腰的驕傲千金、對帳、眼冒愛心頭頂冒煙、摀嘴害羞、氣到握拳、用袖子擦眼淚。
- 新增番外角色趙活（主角本人，非結緣對象）：自戀撫臉、狂笑、計畫通、被揍到鼻青臉腫、嚇呆、決心、冷笑。
- Added Shangguan Ying, the Shangguan Heiress of Fuzhou, and the bonus character Zhao Huo.
- 網頁：點趙活時有時改成把上衣拉起來包住頭（網頁專用動作），連續點會沿用同一種動作；Claude Code 指令區的「換寵物」會跟著目前選的角色顯示對應的 `/mortal-buddy:pick` 指令。

## 0.4.0

- 新增魏菊（崆峒玄功門掌門）：捧手爐、害羞冒熱氣、嚇到摀嘴尖叫。
- 新增番外角色大師兄唐布衣（非結緣對象）：依網友的像素參考圖繪製，彈金錢、連發金錢鏢、豎指大笑、抱胸。
- 開新對話時，若 GitHub 上有新版會提醒（一天最多一次）；更新後第一次開對話會介紹新內容。可用 `MORTAL_BUDDY_NO_UPDATE_CHECK=1` 關閉檢查。
- `/mortal-buddy:status` 顯示目前版本。
- Added Wei Ju and the bonus character Senior Brother Tang Buyi; new sessions now mention when a newer version is available.

## 0.3.0 及之前 / and earlier

- 小梅、小竹（含裂骨魔戰鬥裝）、小師妹、龍湘、夏侯蘭、葉雲裳。
- 中文、日本語、한국어、English 四種語言。

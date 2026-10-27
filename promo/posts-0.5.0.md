# 0.5.0 更新公告：貼文草稿

配圖：
- `update-0.5.0.png`：直式 1080×1350（4:5），巴哈封面、Threads／IG 第一張
- `update-0.5.0.gif`：上官螢眼冒愛心、才沒哭，趙活招牌姿勢、決鬥臉，放巴哈內文
- `update-0.5.0.mp4`：約 27 秒介紹短影片（4:5、無聲），Threads、IG Reels 用這支（巴哈也可以上傳影片）

---

## 巴哈姆特・活俠傳哈啦板

**標題**

【創作】結緣寵物更新 v0.5.0：上官螢、番外趙活登場！（附更新方法，微雷）

**內文**

> 非官方同人作品：角色設定整理自公開資料，像素圖和台詞都是自己畫、自己寫的，沒有使用遊戲素材或原文。

各位唐門子弟好！

上次許願的上官螢做出來了，順便把我們的主角本人也請來了 🙏

（放 update-0.5.0.png）

**新角色**
- 上官螢：福州上官世家的千金。平常叉腰抬下巴「哼」一聲，嘴上嫌你來得晚；被誇會揪著衣襟眼冒愛心、臉紅到頭頂冒煙。工作時捧著帳本對帳，失敗時先氣到握拳，再用袖子擦眼淚說「才沒哭」。
- 番外・趙活：唐門醜俠本人 XD
  沒錯，他就是長這樣：凸眼、眼袋、一嘴參差的牙。閒著就撫著臉越看自己越帥；開心時蘭花手仰頭大笑、撫臉拋媚眼；在網頁上點他，有時還會把上衣拉起來整顆頭藏進去；檢查程式碼時擺出決鬥臉；失敗時被揍得鼻青臉腫。

（放 update-0.5.0.gif）

趙活改了好幾版，一開始畫得太帥被大家打槍「不可能比官方好看」，最後照官方立繪一路醜回來，謝謝提供參考圖和一直抓細節的大家！

**怎麼更新**
1. 網頁版不用做任何事，重新整理就有：https://willismax.github.io/mortal-pets/
2. Claude Code：開新對話時會提醒你有新版。在終端機輸入下面兩行，再重開 Claude Code
   `claude plugin marketplace update mortal-pets`
   `claude plugin update mortal-buddy@mortal-pets`
   換成新角色：`/mortal-buddy:pick shangguanying` 或 `/mortal-buddy:pick zhaohuo`
3. Codex：在下載的資料夾執行 `git pull && ./install.sh codex`，再到 Settings → Pets → Refresh

還沒裝過的人：Claude Code 輸入 `/plugin install mortal-buddy --marketplace willismax/mortal-pets` 就好。

**關於劇透**
兩位的角色檔案都有劇情雷，網頁上預設模糊，點了才會顯示。

原始碼與更新紀錄：https://github.com/willismax/mortal-pets
支援中文、日本語、한국어、English。

下一個想要誰，一樣歡迎留言許願～

《活俠傳》著作權屬於原始鳥熊（Obb Studio）與發行商 Paras Games，本作品為非營利同人創作。

---

## Threads（中文）

**第一則**（配 update-0.5.0.png ＋ update-0.5.0.mp4）

活俠傳桌面寵物更新 v0.5.0 🐾

・上官螢：叉腰「哼」，被誇就眼冒愛心、臉紅冒煙
・番外趙活：唐門醜俠本人，決鬥臉、蘭花手大笑、把衣服拉起來包住頭，全都有

網頁直接玩：
willismax.github.io/mortal-pets

非官方同人二創，像素圖和台詞都是原創。

#活俠傳 #活侠传 #활협전 #LegendofMortal #同人

**第二則**（接在第一則下面回覆）

已經裝過的人，開新對話會提醒你更新 👇
Claude Code（終端機）：
claude plugin marketplace update mortal-pets
claude plugin update mortal-buddy@mortal-pets
然後重開

Codex：git pull && ./install.sh codex

趙活真的改到第六版才醜得夠像，謝謝大家抓細節 😂

---

## Threads（日本語版）

（配 update-0.5.0.mp4）

『活俠傳（カッキョウデン）』デスクトップペット v0.5.0 🐾

新しく二人が仲間入り：
・上官螢：腰に手を当てて「ふん」。褒められるとハート目で真っ赤になって湯気
・番外編の趙活：唐門の醜侠ご本人。決闘顔も、上着を頭からかぶるあのポーズも再現

ブラウザで遊べます（日本語対応）：
willismax.github.io/mortal-pets/?lang=ja

インストール済みの方は、ターミナルで
claude plugin marketplace update mortal-pets
claude plugin update mortal-buddy@mortal-pets
を実行して Claude Code を再起動してください。

非公式のファンメイドです。ドット絵とセリフはすべてオリジナル。

#活俠傳 #カッキョウデン #LegendofMortal

---

## Threads（한국어판）

（配 update-0.5.0.mp4）

활협전 데스크톱 펫 v0.5.0 업데이트 🐾

새로 두 사람이 합류했어요:
・상관형: 허리에 손을 얹고 "흥". 칭찬받으면 하트 눈에 얼굴이 빨개져 김이 나요
・번외편 조활: 당문 추협 본인. 결투 얼굴도, 윗옷을 머리까지 뒤집어쓴 그 포즈도 있어요

브라우저에서 바로 해 볼 수 있어요 (한국어 지원):
willismax.github.io/mortal-pets/?lang=ko

이미 설치했다면 터미널에서
claude plugin marketplace update mortal-pets
claude plugin update mortal-buddy@mortal-pets
를 실행한 뒤 Claude Code를 다시 시작하세요.

비공식 팬메이드이며, 도트 그림과 대사는 모두 창작물입니다.

#활협전 #LegendofMortal #팬아트

---

## Threads (English)

（配 update-0.5.0.mp4）

Legend of Mortal desktop pets, v0.5.0 🐾

Two new faces:
・Shangguan Ying: hands on hips, "Hmph." Praise her and she gets heart eyes and steams bright red
・Bonus: Zhao Huo himself, the Ugly Hero of the Tang Clan. The duel face, the shirt-over-the-head pose, it's all here

Play in your browser:
willismax.github.io/mortal-pets/?lang=en

Already installed? Run these in a terminal, then restart Claude Code:
claude plugin marketplace update mortal-pets
claude plugin update mortal-buddy@mortal-pets

Unofficial fan project. All pixel art and dialogue are original.

#LegendofMortal #活俠傳 #fanart

---

## Instagram

**Reels**（用 update-0.5.0.mp4）

活俠傳桌面寵物 v0.5.0 🐾
上官螢眼冒愛心、趙活決鬥臉，寫程式的時候陪著你

網頁直接玩，連結在個人簡介 👆

非官方同人二創，像素圖和台詞都是原創。

#活俠傳 #LegendofMortal #活侠传 #활협전 #同人 #fanart #pixelart #像素藝術

# 0.4.0 更新公告：貼文草稿

配圖：
- `update-0.4.0.png`：直式 1080×1350（4:5），巴哈封面、Threads 第一張
- `update-0.4.0.gif`：魏菊害羞冒煙、大師兄彈金錢、連發金錢鏢，巴哈內文、Threads 第二張

---

## 巴哈姆特・活俠傳哈啦板

**標題**

【創作】結緣寵物更新 v0.4.0：魏菊、大師兄來了！（附更新方法，微雷）

**內文**

> 非官方同人作品：角色設定整理自公開資料，像素圖和台詞都是自己畫、自己寫的，沒有使用遊戲素材或原文。

各位唐門子弟好！

上次分享的活俠傳桌面寵物，留言區許願最多的兩位，這次都做出來了 🙏

（放 update-0.4.0.png）

**新角色**
- 魏菊：玄功門掌門，永遠捧著小竹打的手爐。被誇會害羞到頭頂冒熱氣，嚇到會摀嘴尖叫，然後努力恢復端莊。
- 番外・大師兄唐布衣：不是結緣對象，但大家都想要他 XD
  閒著就用拇指把金錢彈上去再接住，工作時拉開架式連發金錢鏢，一直「師弟、師弟」地喊你，夢想是退隱江湖跟你說相聲。

（放 update-0.4.0.gif）

大師兄的造型改了好幾版，最後是照網友提供的像素圖一格一格描的，謝謝幫忙抓蟲的大家！

**怎麼更新**
1. 網頁版不用做任何事，重新整理就有：https://willismax.github.io/mortal-pets/
2. Claude Code：在終端機輸入下面兩行，再重開 Claude Code
   `claude plugin marketplace update mortal-pets`
   `claude plugin update mortal-buddy@mortal-pets`
   換成新角色：`/mortal-buddy:pick weiju` 或 `/mortal-buddy:pick tangbuyi`
3. Codex：在下載的資料夾執行 `git pull && ./install.sh codex`，再到 Settings → Pets → Refresh

還沒裝過的人：Claude Code 輸入 `/plugin install mortal-buddy --marketplace willismax/mortal-pets` 就好。

**以後不用再看公告**
從這版開始，有新版時開新對話會提醒你（一天最多一次），更新完第一次開對話會介紹新內容。不想被提醒的話，設環境變數 `MORTAL_BUDDY_NO_UPDATE_CHECK=1` 就會關掉。
（0.3.0 的舊版沒有這個功能，所以這次要麻煩大家手動更新一次。）

**關於劇透**
魏菊和大師兄的角色檔案各有一條劇情雷，網頁上預設模糊，點了才會顯示。

原始碼與更新紀錄：https://github.com/willismax/mortal-pets
支援中文、日本語、한국어、English。

下一個想要誰，一樣歡迎留言許願～

《活俠傳》著作權屬於原始鳥熊（Obb Studio）與發行商 Paras Games，本作品為非營利同人創作。

---

## Threads（中文）

**第一則**（配 update-0.4.0.png ＋ update-0.4.0.gif）

活俠傳桌面寵物更新 v0.4.0 🐾

大家許願的兩位來了：
・魏菊：捧著手爐，害羞到頭頂冒煙
・番外大師兄：彈金錢、連發金錢鏢，一直喊「師弟！」

網頁直接玩：
willismax.github.io/mortal-pets

非官方同人二創，像素圖和台詞都是原創。

#活俠傳 #活侠传 #활협전 #LegendofMortal #同人

**第二則**（接在第一則下面回覆）

已經裝過的人這樣更新 👇
Claude Code（終端機）：
claude plugin marketplace update mortal-pets
claude plugin update mortal-buddy@mortal-pets
然後重開

Codex：git pull && ./install.sh codex

從這版開始，有新版會自動提醒，以後不用再追公告了

---

## Threads（日本語版）

『活俠傳（カッキョウデン）』デスクトップペット v0.4.0 🐾

リクエストの多かった二人が仲間入り：
・魏菊：手炉を抱えて、照れると頭から湯気
・番外編の大師兄：金銭を指で弾いて、金銭鏢を連射。「師弟！」

ブラウザで遊べます（日本語対応）：
willismax.github.io/mortal-pets/?lang=ja

インストール済みの方は、ターミナルで
claude plugin marketplace update mortal-pets
claude plugin update mortal-buddy@mortal-pets
を実行して Claude Code を再起動してください。次回からは新バージョンを自動でお知らせします。

非公式のファンメイドです。ドット絵とセリフはすべてオリジナル。

#活俠傳 #カッキョウデン #LegendofMortal

---

## Threads（한국어판）

활협전 데스크톱 펫 v0.4.0 업데이트 🐾

요청이 많았던 두 사람이 합류했어요:
・위국: 손난로를 꼭 안고, 부끄러우면 머리에서 김이 나요
・번외편 대사형: 금전을 튕기고 금전표를 연발, "사제!"

브라우저에서 바로 해 볼 수 있어요 (한국어 지원):
willismax.github.io/mortal-pets/?lang=ko

이미 설치했다면 터미널에서
claude plugin marketplace update mortal-pets
claude plugin update mortal-buddy@mortal-pets
를 실행한 뒤 Claude Code를 다시 시작하세요. 다음부터는 새 버전이 나오면 자동으로 알려 드려요.

비공식 팬메이드이며, 도트 그림과 대사는 모두 창작물입니다.

#활협전 #LegendofMortal #팬아트

---

## Threads (English)

Legend of Mortal desktop pets, v0.4.0 🐾

The two most requested characters are here:
・Wei Ju: hugs her hand warmer and blushes until steam rises from her head
・Bonus: Senior Brother Tang Buyi flicks gold coins and fires gold-coin darts. "Little brother!"

Play in your browser:
willismax.github.io/mortal-pets/?lang=en

Already installed? Run these in a terminal, then restart Claude Code:
claude plugin marketplace update mortal-pets
claude plugin update mortal-buddy@mortal-pets
From now on, new versions will be announced when you start a session.

Unofficial fan project. All pixel art and dialogue are original.

#LegendofMortal #活俠傳 #fanart

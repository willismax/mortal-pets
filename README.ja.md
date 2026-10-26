# 活俠傳 縁結びペット（二次創作）

[中文](README.md) ｜ **日本語** ｜ [한국어](README.ko.md) ｜ [English](README.en.md)

台湾の武侠 RPG『活俠傳（カッキョウデン）』の縁結びキャラクターを、**Codex のペット**と **Claude Code のペット**にしました。性格に合わせたセリフで、作業中にリアクションしてくれます。

- ブラウザで遊ぶ：<https://willismax.github.io/mortal-pets/?lang=ja>
- Claude Code に入れる：`/plugin install mortal-buddy --marketplace willismax/mortal-pets`
- 非公式のファン作品です。設定は公開情報をもとにまとめ、ドット絵とセリフはオリジナルの二次創作です（ゲームの素材や原文は使用していません）。

## キャラクター

| ID | 名前 | ひとこと |
| --- | --- | --- |
| `xiaomei` | 小梅（虞小梅） | 崆峒派・飛天門の嫡伝女弟子。明るくて料理上手。「本梅」と言うときだけ本音。得意技は飛び蹴りと鶴手。 |
| `xiaozhu` | 小竹（郁竹） | 鐵拳門の「裂骨魔」。小柄で怪力、寝不足で目つきが悪いだけの正直者。鍛冶のあとに汗をぬぐう。 |
| `xiaozhu-battle` | 小竹・裂骨魔 | 小竹の戦闘装束。からくり腕で紅い文様の大剣を掲げ、左手に虎頭の盾。※Codex のペットのみ |
| `xiaoshimei` | 小師妹（唐默鈴） | 唐門掌門の一人娘。七つの鈴を身につけているのに音がしない、森の小動物のような少女。折り紙が好き。 |
| `longxiang` | 龍湘 | 錦香宮の剣士で「鶏ももの女侠」。明るくてちょっと抜けている。 |
| `xiahoulan` | 夏侯蘭 | 奪魄門の「奪魄幽蘭」。番傘を差したクールな若き師匠。口は悪いが面倒見がいい。 |

## Claude Code

```text
/plugin install mortal-buddy --marketplace willismax/mortal-pets
/mortal-buddy:lang ja
```

（古いバージョンの Claude Code では `/plugin marketplace add willismax/mortal-pets` → `/plugin install mortal-buddy@mortal-pets` の 2 ステップです。）

インストール後、作業に合わせて話しかけてくれます。

| タイミング | 気分 |
| --- | --- |
| 会話を始める | あいさつ |
| 質問を送る | 確認中 |
| ツールを実行 | 作業中 |
| コマンドが失敗 | 失敗 |
| 許可を待つ | 返事待ち |
| 1 ターン完了 | 完了（好感度 +1） |

コマンド：

| コマンド | 説明 |
| --- | --- |
| `/mortal-buddy:pick xiaozhu` | ペットを切り替え（`xiaomei`、`xiaozhu`、`xiaoshimei`、`longxiang`、`xiahoulan`） |
| `/mortal-buddy:pet feed` | `pet` なでる・`feed` ごはん・`train` 修行（各 +1）・`gift` 贈り物（+3）。同じ行動は 1 分に 1 回だけ加算 |
| `/mortal-buddy:talk` | 彼女が質問してきます。`/mortal-buddy:talk 2` のように番号で答えると好感度が変わります |
| `/mortal-buddy:roleplay 今日は疲れた` | キャラクターの口調で返事してもらう（日本語で話しかければ日本語で返事） |
| `/mortal-buddy:status` | 全員の好感度を見る |
| `/mortal-buddy:mute` | 会話中のリアクションのオン／オフ |
| `/mortal-buddy:lang ja` | 言語の切り替え：`zh` 中文、`ja` 日本語、`ko` 한국어、`en` English（初回はシステムの言語設定から自動判定） |

好感度は 4 段階（初対面 0／顔なじみ 10／知己 30／結縁 60）。「知己」以上になると、深夜（23:00〜5:00）にときどき心の内を話してくれます。

画面下にずっと表示したい場合は、リポジトリを取得して `./install.sh statusline` を実行し、表示される設定を `~/.claude/settings.json` に追加してください。

## Codex

```bash
git clone https://github.com/willismax/mortal-pets.git
cd mortal-pets && ./install.sh codex
```

Codex の Settings → Pets → Refresh でペットを選びます。会話中は `/pet` で表示／非表示。毎ターンの完了時にキャラから通知を受け取りたい場合は、インストール時に表示される `notify = [...]` を `~/.codex/config.toml` に追加してください。

※Codex のペット名（displayName）は中国語のままです。通知のセリフは `/mortal-buddy:lang` で選んだ言語になります（Claude Code と同じ設定ファイル `~/.mortal-buddy/state.json` を使います）。

## 著作権

『活俠傳』（Legend of Mortal）とそのキャラクターの著作権は開発元・販売元に帰属します。本リポジトリは非公式のファン作品で、コードは MIT ライセンスです。

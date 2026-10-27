# Legend of Mortal Pets (fan-made)

[中文](README.md) ｜ [日本語](README.ja.md) ｜ [한국어](README.ko.md) ｜ **English**

![Legend of Mortal Pets: pixel art of Xiaomei, Xiaozhu, the Bone-Breaker, Junior Sister, Long Xiang, Xiahou Lan, Ye Yunshang, Wei Ju, Shangguan Ying and Senior Brother Tang Buyi](promo/promo-landscape.png)

![Signature moves, animated](promo/promo-moves.gif)

The romanceable heroines of the Taiwanese wuxia RPG **Legend of Mortal (活俠傳)**, turned into **Codex pets** and **Claude Code pets**. Each one reacts to your work with lines written for her personality.

- Play in the browser: <https://willismax.github.io/mortal-pets/?lang=en>
- Install in Claude Code: `/plugin install mortal-buddy --marketplace willismax/mortal-pets`
- Unofficial fan project. Character details are compiled from public sources; all pixel art and dialogue are original fan creations (no game assets or game text are used).

## Characters

| ID | Name | In a line |
| --- | --- | --- |
| `xiaomei` | Xiaomei (Yu Xiaomei) | Direct disciple of Kongtong's Flying Heaven Gate. Bright, teasing, a great cook; she only says "this Mei" when she means it. Signature moves: flying kick and crane hand. |
| `xiaozhu` | Xiaozhu (Yu Zhu) | The Iron Fist Gate's "Bone-Breaker". Tiny and absurdly strong; she only looks fierce because she is short-sighted and never sleeps. Wipes her sweat after forging. |
| `xiaozhu-battle` | Xiaozhu, Bone-Breaker | Xiaozhu's battle gear: a mechanical arm raising a red-runed greatsword, a tiger-head shield in her left hand. Codex pet only. |
| `xiaoshimei` | Junior Sister (Tang Moling) | Only daughter of the Tang Clan's master. Wears seven strings of bells that never ring; quiet as a small forest animal. Loves origami. |
| `longxiang` | Long Xiang | Swordswoman of Jinxiang Palace, "the Drumstick Heroine". Cheerful and a little airheaded. |
| `xiahoulan` | Xiahou Lan | "The Soul-Stealing Orchid" of the Soul-Stealing Gate. A cool young master with an oil-paper umbrella; sharp-tongued, secretly caring. |
| `yeyunshang` | Ye Yunshang | "The Pearl of Diancang", Ye Yunzhou's little sister. A mischievous imp who loves pranks and sweets; wears a sable cloak even in midsummer and runs a fever after half a day of mischief. Signature moves: "Ehehe" wink, pouting, praying hands. |
| `weiju` | Wei Ju | Direct disciple and current master of Kongtong's Mystic Arts Gate. Graceful, well-read and gentle, an odd one out in martial Kongtong; always holding the hand warmer Yu Zhu made for her. Blushes until steam rises from her head. |
| `shangguanying` | Shangguan Ying | Only daughter of the Shangguan family of Fuzhou, “the Shangguan Heiress”. Proud and competitive, she runs the family business in her father’s place; sharp-tongued, blushes when caught out, and wipes away tears insisting it’s just the dust. Her romance route isn’t officially out yet. |
| `tangbuyi` | Senior Brother (Tang Buyi) | Bonus character, not a romance option. First disciple of the Tang Clan's master, "the Flying Knight": carefree, flicks real gold-coin darts, claims his lightness skill ranks top five, and dreams of retiring to do comedy with you. |

## Claude Code

```text
/plugin install mortal-buddy --marketplace willismax/mortal-pets
/mortal-buddy:lang en
```

(On older versions of Claude Code use two steps: `/plugin marketplace add willismax/mortal-pets`, then `/plugin install mortal-buddy@mortal-pets`.)

Once installed she reacts to what you are doing:

| When | Mood |
| --- | --- |
| A session starts | Greeting |
| You send a prompt | Reviewing |
| A tool runs | Working |
| A command fails | Failed |
| Claude waits for your permission | Waiting |
| A turn finishes | Done (affection +1) |

Commands:

| Command | What it does |
| --- | --- |
| `/mortal-buddy:pick xiaozhu` | Switch pet (`xiaomei`, `xiaozhu`, `xiaoshimei`, `longxiang`, `xiahoulan`, `yeyunshang`, `weiju`, `shangguanying`, `tangbuyi`) |
| `/mortal-buddy:pet feed` | `pet`, `feed`, `train` (+1 each) or `gift` (+3); each action counts once a minute |
| `/mortal-buddy:talk` | She asks you something; answer with `/mortal-buddy:talk 2` and your answer changes her affection |
| `/mortal-buddy:roleplay long day today` | She replies in her own voice (in the language you write in) |
| `/mortal-buddy:status` | Show everyone's affection |
| `/mortal-buddy:mute` | Turn her in-chat reactions on or off |
| `/mortal-buddy:lang en` | Switch language: `zh` 中文, `ja` 日本語, `ko` 한국어, `en` English (the first run picks one from your system locale) |

Affection has four stages (Acquainted 0 / Familiar 10 / Confidant 30 / Bonded 60). From "Confidant" on, she sometimes shares what is on her mind late at night (23:00 to 05:00).

To keep her in the status line, clone the repo, run `./install.sh statusline`, and add the printed setting to `~/.claude/settings.json`.

## Codex

```bash
git clone https://github.com/willismax/mortal-pets.git
cd mortal-pets && ./install.sh codex
```

Pick a pet in Codex under Settings → Pets → Refresh, and use `/pet` in a conversation to show or hide it. To get a notification from her at the end of every turn, add the `notify = [...]` line the installer prints to `~/.codex/config.toml`.

Note: Codex pet names (displayName) stay in Chinese. Notification lines follow the language chosen with `/mortal-buddy:lang` (Claude Code and Codex share `~/.mortal-buddy/state.json`).

## Updating

The current version is **0.5.0** (adds Shangguan Ying). See [CHANGELOG.md](CHANGELOG.md) for what changed.

- Claude Code: run these two lines in a terminal, then restart Claude Code. From 0.4.0 on, a new session tells you when a newer version is out (at most once a day). To turn the check off, set `MORTAL_BUDDY_NO_UPDATE_CHECK=1`.

  ```bash
  claude plugin marketplace update mortal-pets
  claude plugin update mortal-buddy@mortal-pets
  ```

- Codex: run `git pull && ./install.sh codex` in the repo folder, then Settings → Pets → Refresh.
- The browser version updates on its own.

## Copyright

Legend of Mortal (活俠傳) and its characters belong to their developer and publisher. This repository is an unofficial fan project; the code is MIT licensed.

# 활협전 인연 펫 (팬메이드)

[中文](README.md) ｜ [日本語](README.ja.md) ｜ **한국어** ｜ [English](README.en.md)

![활협전 인연 펫: 소매, 소죽, 열골마, 소사매, 용상, 하후란, 엽운상 도트 그림](promo/promo-landscape.png)

![6명의 대표 동작 애니메이션](promo/promo-moves.gif)

대만 무협 RPG **활협전(Legend of Mortal)** 의 인연 캐릭터들을 **Codex 펫**과 **Claude Code 펫**으로 만들었습니다. 캐릭터 성격에 맞춘 대사로 작업 중에 반응해 줍니다.

- 브라우저에서 놀기: <https://willismax.github.io/mortal-pets/?lang=ko>
- Claude Code에 설치: `/plugin install mortal-buddy --marketplace willismax/mortal-pets`
- 비공식 팬 작품입니다. 설정은 공개 자료를 바탕으로 정리했고, 도트 그림과 대사는 직접 만든 2차 창작물입니다(게임 리소스나 원문은 사용하지 않았습니다).

## 캐릭터

| ID | 이름 | 한 줄 소개 |
| --- | --- | --- |
| `xiaomei` | 소매(우소매) | 공동파 비천문의 직전 여제자. 밝고 장난기 많은 요리 고수. 대표 동작은 날아차기와 학수(鶴手). |
| `xiaozhu` | 소죽(욱죽) | 철권문의 '열골마'. 작은 체구에 괴력, 잠이 부족해서 눈빛이 사나워 보일 뿐인 솔직한 대장장이. 망치질 후 땀을 닦는다. |
| `xiaozhu-battle` | 소죽・열골마 | 소죽의 전투 복장. 기관 팔로 붉은 문양의 대검을 들고, 왼손에는 호랑이 머리 방패. ※ Codex 펫 전용 |
| `xiaoshimei` | 소사매(당묵령) | 당문 장문인의 외동딸. 방울 일곱 줄을 달고도 소리 하나 내지 않는, 숲속 작은 동물 같은 소녀. 종이접기를 좋아한다. |
| `longxiang` | 용상 | 금향궁의 검객, '닭다리 여협'. 밝고 조금 엉뚱하다. |
| `xiahoulan` | 하후란 | 탈백문의 '탈백유란'. 지우산을 든 차가운 젊은 사부. 말은 날카롭지만 제자를 끔찍이 챙긴다. |
| `yeyunshang` | 엽운상 | '점창명주', 엽운주의 친여동생. 장난과 단것을 좋아하는 꼬마 악동. 한여름에도 담비 털옷을 벗지 않고, 반나절만 놀아도 열이 나서 쓰러진다. 대표 동작은 "에헤" 윙크, 뾰로통한 얼굴, 기도하는 손. |

## Claude Code

```text
/plugin install mortal-buddy --marketplace willismax/mortal-pets
/mortal-buddy:lang ko
```

(구버전 Claude Code에서는 `/plugin marketplace add willismax/mortal-pets` → `/plugin install mortal-buddy@mortal-pets` 두 단계로 설치하세요.)

설치하면 작업 상태에 맞춰 말을 걸어 옵니다.

| 상황 | 기분 |
| --- | --- |
| 새 대화 시작 | 인사 |
| 질문 보내기 | 검토 중 |
| 도구 실행 | 작업 중 |
| 명령 실패 | 실패 |
| 허가 기다리기 | 대답 기다리기 |
| 한 턴 완료 | 완료 (호감도 +1) |

명령어:

| 명령어 | 설명 |
| --- | --- |
| `/mortal-buddy:pick xiaozhu` | 펫 바꾸기 (`xiaomei`, `xiaozhu`, `xiaoshimei`, `longxiang`, `xiahoulan`, `yeyunshang`) |
| `/mortal-buddy:pet feed` | `pet` 쓰다듬기, `feed` 먹이기, `train` 수련(각 +1), `gift` 선물(+3). 같은 행동은 1분에 한 번만 오른다 |
| `/mortal-buddy:talk` | 캐릭터가 질문합니다. `/mortal-buddy:talk 2`처럼 번호로 대답하면 호감도가 바뀝니다 |
| `/mortal-buddy:roleplay 오늘 너무 피곤해` | 캐릭터 말투로 대답 (한국어로 말하면 한국어로 대답) |
| `/mortal-buddy:status` | 모든 캐릭터의 호감도 보기 |
| `/mortal-buddy:mute` | 대화 중 반응 메시지 켜기/끄기 |
| `/mortal-buddy:lang ko` | 언어 바꾸기: `zh` 中文, `ja` 日本語, `ko` 한국어, `en` English (처음에는 시스템 언어 설정으로 자동 선택) |

호감도는 4단계(첫 만남 0 / 친분 10 / 지기 30 / 인연 60)입니다. '지기' 이상이 되면 심야(23:00~05:00)에 가끔 속마음을 털어놓습니다.

화면 아래에 항상 띄우고 싶다면 저장소를 받아 `./install.sh statusline`을 실행하고, 출력된 설정을 `~/.claude/settings.json`에 추가하세요.

## Codex

```bash
git clone https://github.com/willismax/mortal-pets.git
cd mortal-pets && ./install.sh codex
```

Codex의 Settings → Pets → Refresh에서 펫을 고르세요. 대화 중에는 `/pet`으로 보이기/숨기기를 할 수 있습니다. 턴이 끝날 때마다 캐릭터 알림을 받고 싶다면, 설치할 때 출력되는 `notify = [...]`를 `~/.codex/config.toml`에 추가하세요.

※ Codex 펫 이름(displayName)은 중국어 그대로입니다. 알림 대사는 `/mortal-buddy:lang`으로 고른 언어로 나옵니다(Claude Code와 같은 설정 파일 `~/.mortal-buddy/state.json`을 사용합니다).

## 저작권

활협전(Legend of Mortal)과 등장인물의 저작권은 개발사와 배급사에 있습니다. 이 저장소는 비공식 팬 작품이며, 코드는 MIT 라이선스입니다.

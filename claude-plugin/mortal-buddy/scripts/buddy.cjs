#!/usr/bin/env node
// 活俠傳結緣寵物：Claude Code 的 hook / status line / 指令，以及 Codex 的 notify 共用這支程式。
//
//   node buddy.cjs hook                 # 由 hooks.json 呼叫，stdin 是 hook 事件 JSON
//   node buddy.cjs statusline           # 由 settings.json 的 statusLine 呼叫
//   node buddy.cjs pick xiaozhu         # 換寵物
//   node buddy.cjs act pet|feed|train|gift
//   node buddy.cjs talk [選項編號]       # 聊天：不帶編號出題，帶編號回答
//   node buddy.cjs mute | status
//   node buddy.cjs lang ja              # 切換語言：zh 中文、ja 日本語、ko 한국어、en English
//   node buddy.cjs codex-notify '<json>' # Codex 的 notify 設定呼叫
//   node buddy.cjs check-update         # 背景查 GitHub 上的最新版本（SessionStart 一天最多查一次）

const fs = require("fs");
const os = require("os");
const path = require("path");
const https = require("https");
const { execFile, spawn } = require("child_process");
const DATA = require("./characters.js");

const LANGS = ["zh", "ja", "ko", "en"];
// 介面文字（角色台詞在 locales/<lang>.js）
const MSG = {
  zh: {
    open: "「", close: "」", lp: "（", rp: "）", colon: "：", sep: "，", comma: "、",
    acts: "可用的互動：pet（摸頭）、feed（餵食）、train（練功）、gift（送禮）",
    gain: (n) => `（好感 +${n}）`, noGain: "（剛剛才互動過，好感沒有增加）", delta: (d) => `（好感 ${d}）`,
    answer: "（回答：/mortal-buddy:talk <編號>）", range: (n) => `請選 1 到 ${n}。`,
    choices: "可選：", aff: "好感", reactions: (on) => `反應訊息：${on ? "開啟" : "關閉"}`,
    muted: (on) => `反應訊息已${on ? "開啟" : "關閉"}。`,
    updated: (v, news) => `（mortal-buddy 已更新到 ${v}：${news}！用 /mortal-buddy:pick 換寵物）`,
    newVersion: (v, cur) => `（mortal-buddy 有新版 ${v}（目前 ${cur}）：在終端機執行 claude plugin marketplace update mortal-pets，再執行 claude plugin update mortal-buddy@mortal-pets，重開 Claude Code 即可）`,
    version: (v) => `mortal-buddy v${v}`,
    lang: "語言已切換為中文。", langs: "可選語言：zh 中文、ja 日本語、ko 한국어、en English",
    usage: "用法：buddy.cjs hook|statusline|pick <id>|act <pet|feed|train|gift>|talk [n]|mute|status|lang <zh|ja|ko|en>|codex-notify <json>"
  },
  ja: {
    open: "「", close: "」", lp: "｜", rp: "", colon: "：", sep: "、", comma: "、",
    acts: "使えるコマンド：pet（なでる）、feed（ごはん）、train（修行）、gift（贈り物）",
    gain: (n) => `（好感度 +${n}）`, noGain: "（さっきやったばかり。好感度は上がらなかった）", delta: (d) => `（好感度 ${d}）`,
    answer: "（答え方：/mortal-buddy:talk <番号>）", range: (n) => `1〜${n} の番号を選んでね。`,
    choices: "選べるキャラ：", aff: "好感度", reactions: (on) => `リアクション表示：${on ? "オン" : "オフ"}`,
    muted: (on) => `リアクション表示を${on ? "オン" : "オフ"}にしました。`,
    updated: (v, news) => `（mortal-buddy を ${v} に更新しました：${news}！/mortal-buddy:pick でペットを切り替えられます）`,
    newVersion: (v, cur) => `（mortal-buddy の新バージョン ${v} があります（現在 ${cur}）：ターミナルで claude plugin marketplace update mortal-pets と claude plugin update mortal-buddy@mortal-pets を実行し、Claude Code を再起動してください）`,
    version: (v) => `mortal-buddy v${v}`,
    lang: "言語を日本語に切り替えました。", langs: "選べる言語：zh 中文、ja 日本語、ko 한국어、en English",
    usage: "使い方：buddy.cjs hook|statusline|pick <id>|act <pet|feed|train|gift>|talk [n]|mute|status|lang <zh|ja|ko|en>|codex-notify <json>"
  },
  ko: {
    open: "“", close: "”", lp: " (", rp: ")", colon: ": ", sep: ", ", comma: ", ",
    acts: "사용 가능한 행동: pet(쓰다듬기), feed(먹이기), train(수련), gift(선물)",
    gain: (n) => ` (호감도 +${n})`, noGain: " (방금 했던 거라 호감도는 오르지 않았어요)", delta: (d) => ` (호감도 ${d})`,
    answer: "(대답: /mortal-buddy:talk <번호>)", range: (n) => `1부터 ${n} 사이에서 골라 주세요.`,
    choices: "선택 가능: ", aff: "호감도", reactions: (on) => `반응 메시지: ${on ? "켜짐" : "꺼짐"}`,
    muted: (on) => `반응 메시지를 ${on ? "켰어요" : "껐어요"}.`,
    updated: (v, news) => ` (mortal-buddy가 ${v}(으)로 업데이트됐어요: ${news}! /mortal-buddy:pick 으로 펫을 바꿀 수 있어요)`,
    newVersion: (v, cur) => ` (mortal-buddy 새 버전 ${v}이 나왔어요(현재 ${cur}): 터미널에서 claude plugin marketplace update mortal-pets, claude plugin update mortal-buddy@mortal-pets 를 실행한 뒤 Claude Code를 다시 시작하세요)`,
    version: (v) => `mortal-buddy v${v}`,
    lang: "언어를 한국어로 바꿨어요.", langs: "선택 가능한 언어: zh 中文, ja 日本語, ko 한국어, en English",
    usage: "사용법: buddy.cjs hook|statusline|pick <id>|act <pet|feed|train|gift>|talk [n]|mute|status|lang <zh|ja|ko|en>|codex-notify <json>"
  },
  en: {
    open: "“", close: "”", lp: " (", rp: ")", colon: ": ", sep: ", ", comma: ", ",
    acts: "Actions: pet, feed, train, gift",
    gain: (n) => ` (affection +${n})`, noGain: " (you just did that, no affection gained)", delta: (d) => ` (affection ${d})`,
    answer: "(answer with /mortal-buddy:talk <number>)", range: (n) => `Pick a number from 1 to ${n}.`,
    choices: "Available: ", aff: "affection", reactions: (on) => `Reaction messages: ${on ? "on" : "off"}`,
    muted: (on) => `Reaction messages turned ${on ? "on" : "off"}.`,
    updated: (v, news) => ` (mortal-buddy updated to ${v}: ${news}! Switch pets with /mortal-buddy:pick)`,
    newVersion: (v, cur) => ` (mortal-buddy ${v} is out (you have ${cur}): run claude plugin marketplace update mortal-pets, then claude plugin update mortal-buddy@mortal-pets, and restart Claude Code)`,
    version: (v) => `mortal-buddy v${v}`,
    lang: "Language switched to English.", langs: "Languages: zh 中文, ja 日本語, ko 한국어, en English",
    usage: "Usage: buddy.cjs hook|statusline|pick <id>|act <pet|feed|train|gift>|talk [n]|mute|status|lang <zh|ja|ko|en>|codex-notify <json>"
  }
};

// 第一次執行時依系統語系猜語言，之後以 /mortal-buddy:lang 設定的為準
function guessLang() {
  const env = (process.env.LC_ALL || process.env.LC_MESSAGES || process.env.LANG || "").toLowerCase();
  if (env.startsWith("ja")) return "ja";
  if (env.startsWith("ko")) return "ko";
  if (env.startsWith("en")) return "en";
  return "zh";
}

let CHARS = DATA.CHARS;
let TIERS = DATA.TIERS;
let M = MSG.zh;

function useLang(lang) {
  const l = LANGS.includes(lang) ? lang : "zh";
  let locale = null;
  if (l !== "zh") {
    try {
      locale = require(`./locales/${l}.js`);
    } catch {}
  }
  ({ CHARS, TIERS } = DATA.localize(locale));
  M = MSG[l];
}

const HOME = process.env.MORTAL_BUDDY_HOME || path.join(os.homedir(), ".mortal-buddy");
const STATE_FILE = path.join(HOME, "state.json");
const STALE_MS = 5 * 60 * 1000;
const AFF_MAX = 99;

function load() {
  const def = { current: "xiaomei", aff: {}, mood: "idle", moodAt: 0, line: "", muted: false, talk: null, actedAt: {} };
  let s = def;
  try {
    s = { ...def, ...JSON.parse(fs.readFileSync(STATE_FILE, "utf8")) };
  } catch {}
  if (!s.lang) s.lang = guessLang();
  useLang(s.lang);
  return s;
}

function save(s) {
  fs.mkdirSync(HOME, { recursive: true });
  fs.writeFileSync(STATE_FILE, JSON.stringify(s, null, 2));
}

// 版本：外掛裡讀 ../.claude-plugin/plugin.json，install.sh 裝的則讀同資料夾的 plugin.json
function readVersion() {
  for (const p of [path.join(__dirname, "..", ".claude-plugin", "plugin.json"), path.join(__dirname, "plugin.json")]) {
    try {
      return JSON.parse(fs.readFileSync(p, "utf8")).version;
    } catch {}
  }
  return null;
}
const VERSION = readVersion();
const REMOTE_MANIFEST = "https://raw.githubusercontent.com/willismax/mortal-pets/main/claude-plugin/mortal-buddy/.claude-plugin/plugin.json";
const LATEST_FILE = path.join(HOME, "latest.json");
const DAY_MS = 24 * 60 * 60 * 1000;
// 各版新增的內容，更新後第一次開對話時說一次
const NEWS = {
  "0.5.0": {
    zh: "新增上官螢（福州上官千金）",
    ja: "上官螢（福州の上官家の令嬢）が仲間入り",
    ko: "상관형(푸저우 상관가의 아가씨) 추가",
    en: "Shangguan Ying, the Shangguan Heiress of Fuzhou, joins the cast"
  },
  "0.4.0": {
    zh: "新增魏菊、番外大師兄唐布衣",
    ja: "魏菊と番外編の大師兄・唐布衣が仲間入り",
    ko: "위국과 번외편 대사형 당포의 추가",
    en: "Wei Ju and bonus character Senior Brother Tang Buyi join the cast"
  }
};

function newer(a, b) {
  const pa = String(a).split(".").map(Number), pb = String(b).split(".").map(Number);
  for (let i = 0; i < 3; i++) {
    if ((pa[i] || 0) !== (pb[i] || 0)) return (pa[i] || 0) > (pb[i] || 0);
  }
  return false;
}

// 背景查最新版，寫進 latest.json；查不到就算了，不影響寵物
function checkUpdate() {
  const req = https.get(REMOTE_MANIFEST, { timeout: 5000 }, (res) => {
    let body = "";
    res.on("data", (d) => (body += d));
    res.on("end", () => {
      try {
        const version = JSON.parse(body).version;
        fs.mkdirSync(HOME, { recursive: true });
        fs.writeFileSync(LATEST_FILE, JSON.stringify({ version, checkedAt: Date.now() }));
      } catch {}
    });
  });
  req.on("timeout", () => req.destroy());
  req.on("error", () => {});
}

// 開新對話時：剛更新過就介紹新內容；GitHub 上有新版就提醒（一天最多一次）
function updateNotes(s, existed) {
  const notes = [];
  if (!VERSION) return notes;
  if (s.seenVersion !== VERSION) {
    const news = NEWS[VERSION] && NEWS[VERSION][s.lang];
    if (existed && news) notes.push(M.updated(VERSION, news));
    s.seenVersion = VERSION;
  }
  let latest = {};
  try {
    latest = JSON.parse(fs.readFileSync(LATEST_FILE, "utf8"));
  } catch {}
  if (latest.version && newer(latest.version, VERSION) && Date.now() - (s.updateToldAt || 0) > DAY_MS) {
    notes.push(M.newVersion(latest.version, VERSION));
    s.updateToldAt = Date.now();
  }
  if (!process.env.MORTAL_BUDDY_NO_UPDATE_CHECK && Date.now() - (latest.checkedAt || 0) > DAY_MS) {
    try {
      spawn(process.execPath, [__filename, "check-update"], { detached: true, stdio: "ignore" }).unref();
    } catch {}
  }
  return notes;
}

const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
const charOf = (s) => CHARS[s.current] || CHARS.xiaomei;
const affOf = (s) => s.aff[s.current] || 0;
const tierOf = (n) => TIERS.filter((t) => n >= t.min).pop().name;

function addAff(s, n) {
  s.aff[s.current] = Math.max(0, Math.min(AFF_MAX, affOf(s) + n));
}

function isNight() {
  const h = new Date().getHours();
  return h >= 23 || h < 5;
}

// 心情 → 台詞。好感達「知己」後，深夜有機會說出藏在心底的話。
function say(s, mood) {
  const c = charOf(s);
  let pool = c.lines[mood] || c.lines.idle;
  if ((mood === "done" || mood === "idle") && isNight() && affOf(s) >= 30 && Math.random() < 0.3) {
    pool = c.lines.night;
  }
  s.mood = mood;
  s.moodAt = Date.now();
  s.line = pick(pool);
  return s.line;
}

function format(s, line) {
  const c = charOf(s);
  return `${c.name}${c.face[s.mood] || c.face.idle}${M.open}${line}${M.close}`;
}

function hearts(n) {
  const full = Math.min(5, Math.floor(n / 12));
  return "♥".repeat(full) + "♡".repeat(5 - full);
}

function readStdin() {
  try {
    return fs.readFileSync(0, "utf8");
  } catch {
    return "";
  }
}

function looksFailed(ev) {
  const r = ev.tool_response;
  if (!r || typeof r !== "object") return false;
  if (r.is_error === true || r.success === false) return true;
  return typeof r.exit_code === "number" && r.exit_code !== 0;
}

function hook() {
  let ev = {};
  try {
    ev = JSON.parse(readStdin() || "{}");
  } catch {}
  const existed = fs.existsSync(STATE_FILE);
  const s = load();
  let speak = false;
  let notes = [];
  switch (ev.hook_event_name) {
    case "SessionStart":
      say(s, "greet");
      s.mood = "idle";
      speak = true;
      notes = updateNotes(s, existed);
      break;
    case "UserPromptSubmit":
      say(s, "review");
      break;
    case "PreToolUse":
      if (s.mood !== "working" || Date.now() - s.moodAt > 30000) say(s, "working");
      break;
    case "PostToolUse":
      if (looksFailed(ev)) say(s, "failed");
      break;
    case "Notification":
      say(s, "waiting");
      speak = true;
      break;
    case "Stop":
      // 每完成一輪對話 +1 好感
      addAff(s, 1);
      say(s, s.mood === "failed" ? "failed" : "done");
      speak = true;
      break;
  }
  save(s);
  // 更新提醒即使關掉反應訊息也照樣顯示
  const lines = [...(speak && !s.muted ? [format(s, s.line)] : []), ...notes.map((n) => n.trim())];
  if (lines.length) {
    process.stdout.write(JSON.stringify({ systemMessage: lines.join("\n"), suppressOutput: true }));
  }
}

function statusline() {
  readStdin();
  const s = load();
  if (Date.now() - s.moodAt > STALE_MS) {
    // 閒置時每分鐘換一句，不必每次重畫都亂跳
    const idle = charOf(s).lines.idle;
    s.mood = "idle";
    s.line = idle[Math.floor(Date.now() / 60000) % idle.length];
  }
  const n = affOf(s);
  process.stdout.write(`${format(s, s.line)}  ${hearts(n)} ${tierOf(n)} ${n}`);
}

const ACT_COOLDOWN_MS = 60 * 1000;

function act(kind) {
  const s = load();
  const c = charOf(s);
  if (!c.lines[kind] || !["pet", "feed", "train", "gift"].includes(kind)) {
    console.log(M.acts);
    return;
  }
  // 同一種互動一分鐘內只加一次好感，避免連點刷好感
  const last = s.actedAt[`${s.current}:${kind}`] || 0;
  const gain = Date.now() - last > ACT_COOLDOWN_MS ? (kind === "gift" ? 3 : 1) : 0;
  s.actedAt[`${s.current}:${kind}`] = Date.now();
  addAff(s, gain);
  const line = say(s, kind);
  save(s);
  console.log(format(s, line) + (gain ? M.gain(gain) : M.noGain));
}

function talk(choice) {
  const s = load();
  const c = charOf(s);
  if (!choice || !s.talk || s.talk.id !== s.current) {
    const i = Math.floor(Math.random() * c.talks.length);
    s.talk = { id: s.current, i };
    save(s);
    const t = c.talks[i];
    console.log(`${c.name}${M.colon}${M.open}${t.q}${M.close}`);
    t.opts.forEach((o, k) => console.log(`  ${k + 1}. ${o.t}`));
    console.log(M.answer);
    return;
  }
  const t = c.talks[s.talk.i];
  const o = t.opts[Number(choice) - 1];
  if (!o) {
    console.log(M.range(t.opts.length));
    return;
  }
  addAff(s, o.aff);
  s.talk = null;
  s.mood = o.aff > 0 ? "done" : o.aff < 0 ? "failed" : "idle";
  s.moodAt = Date.now();
  s.line = o.r;
  save(s);
  const sign = o.aff > 0 ? `+${o.aff}` : `${o.aff}`;
  console.log(format(s, o.r) + M.delta(sign));
}

function pickChar(id) {
  const s = load();
  if (!CHARS[id]) {
    console.log(M.choices + Object.values(CHARS).map((c) => `${c.id}${M.lp}${c.name}${M.rp}`).join(M.comma));
    return;
  }
  s.current = id;
  const line = say(s, "greet");
  save(s);
  console.log(format(s, line));
}

function status() {
  const s = load();
  for (const c of Object.values(CHARS)) {
    const n = s.aff[c.id] || 0;
    const mark = c.id === s.current ? "▶" : " ";
    const who = c.fullName === c.name ? c.title : `${c.fullName}${M.sep}${c.title}`;
    const label = c.fullName.startsWith(c.name) && c.fullName !== c.name ? c.fullName : c.name;
    const detail = label === c.name ? who : c.title;
    console.log(`${mark} ${label}${M.lp}${detail}${M.rp} ${M.aff} ${n} ${hearts(n)} ${tierOf(n)}`);
  }
  console.log(M.reactions(!s.muted));
  if (VERSION) console.log(M.version(VERSION));
}

// Codex 在每輪結束時呼叫 notify 程式，最後一個參數是事件 JSON。
function codexNotify(raw) {
  let ev = {};
  try {
    ev = JSON.parse(raw || "{}");
  } catch {}
  if (ev.type && ev.type !== "agent-turn-complete") return;
  const s = load();
  addAff(s, 1);
  const line = say(s, "done");
  save(s);
  const c = charOf(s);
  const title = `${c.name}${c.face.done}`;
  if (process.platform === "darwin") {
    const esc = (x) => x.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
    execFile("osascript", ["-e", `display notification "${esc(line)}" with title "${esc(title)}"`], () => {});
  } else if (process.platform === "linux") {
    execFile("notify-send", [title, line], () => {});
  } else {
    console.log(`${title} ${line}`);
  }
}

const [cmd, ...args] = process.argv.slice(2);
switch (cmd) {
  case "hook": hook(); break;
  case "statusline": statusline(); break;
  case "pick": pickChar(args[0]); break;
  case "act": act(args[0]); break;
  case "talk": talk(args[0]); break;
  case "mute": {
    const s = load();
    s.muted = !s.muted;
    save(s);
    console.log(M.muted(!s.muted));
    break;
  }
  case "lang": {
    const s = load();
    if (!LANGS.includes(args[0])) {
      console.log(M.langs);
      break;
    }
    s.lang = args[0];
    useLang(s.lang);
    say(s, "greet");
    save(s);
    console.log(M.lang);
    console.log(format(s, s.line));
    break;
  }
  case "status": status(); break;
  case "codex-notify": codexNotify(args[args.length - 1]); break;
  case "check-update": checkUpdate(); break;
  default:
    load();
    console.log(M.usage);
}

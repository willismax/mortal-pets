#!/usr/bin/env node
// 活俠傳結緣寵物：Claude Code 的 hook / status line / 指令，以及 Codex 的 notify 共用這支程式。
//
//   node buddy.cjs hook                 # 由 hooks.json 呼叫，stdin 是 hook 事件 JSON
//   node buddy.cjs statusline           # 由 settings.json 的 statusLine 呼叫
//   node buddy.cjs pick xiaozhu         # 換寵物
//   node buddy.cjs act pet|feed|train|gift
//   node buddy.cjs talk [選項編號]       # 聊天：不帶編號出題，帶編號回答
//   node buddy.cjs mute | status
//   node buddy.cjs codex-notify '<json>' # Codex 的 notify 設定呼叫

const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFile } = require("child_process");
const { CHARS, TIERS } = require("./characters.js");

const HOME = process.env.MORTAL_BUDDY_HOME || path.join(os.homedir(), ".mortal-buddy");
const STATE_FILE = path.join(HOME, "state.json");
const STALE_MS = 5 * 60 * 1000;
const AFF_MAX = 99;

function load() {
  const def = { current: "xiaomei", aff: {}, mood: "idle", moodAt: 0, line: "", muted: false, talk: null, actedAt: {} };
  try {
    return { ...def, ...JSON.parse(fs.readFileSync(STATE_FILE, "utf8")) };
  } catch {
    return def;
  }
}

function save(s) {
  fs.mkdirSync(HOME, { recursive: true });
  fs.writeFileSync(STATE_FILE, JSON.stringify(s, null, 2));
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
  return `${c.name}${c.face[s.mood] || c.face.idle}「${line}」`;
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
  const s = load();
  let speak = false;
  switch (ev.hook_event_name) {
    case "SessionStart":
      say(s, "greet");
      s.mood = "idle";
      speak = true;
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
  if (speak && !s.muted) {
    process.stdout.write(JSON.stringify({ systemMessage: format(s, s.line), suppressOutput: true }));
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
    console.log("可用的互動：pet（摸頭）、feed（餵食）、train（練功）、gift（送禮）");
    return;
  }
  // 同一種互動一分鐘內只加一次好感，避免連點刷好感
  const last = s.actedAt[`${s.current}:${kind}`] || 0;
  const gain = Date.now() - last > ACT_COOLDOWN_MS ? (kind === "gift" ? 3 : 1) : 0;
  s.actedAt[`${s.current}:${kind}`] = Date.now();
  addAff(s, gain);
  const line = say(s, kind);
  save(s);
  console.log(format(s, line) + (gain ? `（好感 +${gain}）` : "（剛剛才互動過，好感沒有增加）"));
}

function talk(choice) {
  const s = load();
  const c = charOf(s);
  if (!choice || !s.talk || s.talk.id !== s.current) {
    const i = Math.floor(Math.random() * c.talks.length);
    s.talk = { id: s.current, i };
    save(s);
    const t = c.talks[i];
    console.log(`${c.name}：「${t.q}」`);
    t.opts.forEach((o, k) => console.log(`  ${k + 1}. ${o.t}`));
    console.log("（回答：/mortal-buddy:talk <編號>）");
    return;
  }
  const t = c.talks[s.talk.i];
  const o = t.opts[Number(choice) - 1];
  if (!o) {
    console.log(`請選 1 到 ${t.opts.length}。`);
    return;
  }
  addAff(s, o.aff);
  s.talk = null;
  s.mood = o.aff > 0 ? "done" : o.aff < 0 ? "failed" : "idle";
  s.moodAt = Date.now();
  s.line = o.r;
  save(s);
  const sign = o.aff > 0 ? `+${o.aff}` : `${o.aff}`;
  console.log(`${format(s, o.r)}（好感 ${sign}）`);
}

function pickChar(id) {
  const s = load();
  if (!CHARS[id]) {
    console.log("可選：" + Object.values(CHARS).map((c) => `${c.id}（${c.name}）`).join("、"));
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
    console.log(`${mark} ${c.name}（${c.fullName}，${c.title}）好感 ${n} ${hearts(n)} ${tierOf(n)}`);
  }
  console.log(`反應訊息：${s.muted ? "關閉" : "開啟"}`);
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
    console.log(`反應訊息已${s.muted ? "關閉" : "開啟"}。`);
    break;
  }
  case "status": status(); break;
  case "codex-notify": codexNotify(args[args.length - 1]); break;
  default:
    console.log("用法：buddy.cjs hook|statusline|pick <id>|act <pet|feed|train|gift>|talk [n]|mute|status|codex-notify <json>");
}

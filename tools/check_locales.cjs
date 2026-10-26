#!/usr/bin/env node
// 檢查 locales/<lang>.js 的結構是否和中文版 characters.js 完全對應：
// 每位角色都要有 name、title、tagline、profile、lines、talks，數量一致、沒有空字串。
//   node tools/check_locales.cjs            # 檢查全部語言
//   node tools/check_locales.cjs ja         # 只檢查日文
const path = require("path");
const fs = require("fs");
const dir = path.join(__dirname, "..", "claude-plugin", "mortal-buddy", "scripts");
const { CHARS, TIERS } = require(path.join(dir, "characters.js"));

const langs = process.argv[2] ? [process.argv[2]] : fs.readdirSync(path.join(dir, "locales")).map((f) => f.replace(/\.js$/, ""));
let bad = 0;
const fail = (lang, msg) => { bad++; console.log(`✗ ${lang}: ${msg}`); };
const str = (v) => typeof v === "string" && v.trim().length > 0;

for (const lang of langs) {
  const L = require(path.join(dir, "locales", `${lang}.js`));
  if (L.lang !== lang) fail(lang, `lang 欄位應為 "${lang}"`);
  if (!Array.isArray(L.tiers) || L.tiers.length !== TIERS.length || !L.tiers.every(str)) fail(lang, `tiers 要有 ${TIERS.length} 個名稱`);
  for (const [id, c] of Object.entries(CHARS)) {
    const t = L.chars && L.chars[id];
    if (!t) { fail(lang, `缺少角色 ${id}`); continue; }
    for (const k of ["name", "fullName", "title", "tagline"]) if (!str(t[k])) fail(lang, `${id}.${k} 是空的`);
    if (!Array.isArray(t.profile) || t.profile.length !== c.profile.length || !t.profile.every(str))
      fail(lang, `${id}.profile 要有 ${c.profile.length} 條`);
    else c.profile.forEach((p, i) => { if (p.startsWith("（劇透）") !== /^[（(]/.test(t.profile[i])) fail(lang, `${id}.profile[${i}] 的劇透標記要保留在開頭`); });
    for (const [mood, arr] of Object.entries(c.lines)) {
      const tl = t.lines && t.lines[mood];
      if (!Array.isArray(tl) || tl.length !== arr.length || !tl.every(str)) fail(lang, `${id}.lines.${mood} 要有 ${arr.length} 句`);
    }
    if (!Array.isArray(t.talks) || t.talks.length !== c.talks.length) { fail(lang, `${id}.talks 要有 ${c.talks.length} 題`); continue; }
    c.talks.forEach((q, i) => {
      const tq = t.talks[i];
      if (!str(tq.q)) fail(lang, `${id}.talks[${i}].q 是空的`);
      if (!Array.isArray(tq.opts) || tq.opts.length !== q.opts.length || !tq.opts.every((o) => str(o.t) && str(o.r)))
        fail(lang, `${id}.talks[${i}].opts 要有 ${q.opts.length} 個選項，每個都有 t 和 r`);
    });
    if (c.outfits && (!Array.isArray(t.outfits) || t.outfits.length !== c.outfits.length || !t.outfits.every(str)))
      fail(lang, `${id}.outfits 要有 ${c.outfits.length} 個造型名稱`);
  }
  if (!bad) console.log(`✓ ${lang}`);
}
process.exit(bad ? 1 : 0);

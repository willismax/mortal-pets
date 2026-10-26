#!/usr/bin/env bash
# 安裝活俠傳結緣寵物。
#   ./install.sh codex        安裝 Codex 寵物、角色 skill 與完成通知
#   ./install.sh statusline   把寵物放進 Claude Code 的 status line
#   ./install.sh all          兩個都裝
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$HERE/claude-plugin/mortal-buddy"
BIN="${MORTAL_BUDDY_HOME:-$HOME/.mortal-buddy}/bin"
CODEX="${CODEX_HOME:-$HOME/.codex}"

install_bin() {
  mkdir -p "$BIN"
  cp "$PLUGIN/scripts/buddy.cjs" "$PLUGIN/scripts/characters.js" "$PLUGIN/.claude-plugin/plugin.json" "$BIN/"
  mkdir -p "$BIN/locales"
  cp "$PLUGIN"/scripts/locales/*.js "$BIN/locales/"
}

install_codex() {
  install_bin
  for pet in "$HERE"/codex/pets/*/; do
    id="$(basename "$pet")"
    mkdir -p "$CODEX/pets/$id"
    cp "$pet/pet.json" "$pet/spritesheet.webp" "$CODEX/pets/$id/"
    echo "Codex pet：$CODEX/pets/$id"
  done
  for skill in "$PLUGIN"/skills/*/; do
    id="$(basename "$skill")"
    mkdir -p "$CODEX/skills/$id"
    cp "$skill/SKILL.md" "$CODEX/skills/$id/"
    echo "Codex skill：$CODEX/skills/$id"
  done
  cat <<MSG

接著 / Next:
1. 打開 Codex → Settings → Pets → Refresh 選一隻，或在對話中輸入 /pet。
   Open Codex → Settings → Pets → Refresh and pick one, or type /pet in a conversation.
2. 想在每輪完成時收到角色的通知，在 $CODEX/config.toml 最上方加入（已有 notify 的話請自行合併）：
   For a notification from her after every turn, add this to the top of $CODEX/config.toml
   (merge it if you already have a notify line):

   notify = ["node", "$BIN/buddy.cjs", "codex-notify"]

3. 換角色 / Switch pet：node "$BIN/buddy.cjs" pick xiaozhu
4. 換語言 / Language：node "$BIN/buddy.cjs" lang ja   （zh／ja／ko／en）
MSG
}

install_statusline() {
  install_bin
  cat <<MSG

在 ~/.claude/settings.json 加入（已有 statusLine 的話請替換）：
Add this to ~/.claude/settings.json (replace any existing statusLine):

  "statusLine": {
    "type": "command",
    "command": "node \"$BIN/buddy.cjs\" statusline"
  }

外掛本體請在 Claude Code 中安裝 / Install the plugin in Claude Code:
  /plugin install mortal-buddy --marketplace willismax/mortal-pets
MSG
}

case "${1:-all}" in
  codex) install_codex ;;
  statusline) install_statusline ;;
  all) install_codex; install_statusline ;;
  *) echo "用法 / Usage：$0 [codex|statusline|all]"; exit 1 ;;
esac

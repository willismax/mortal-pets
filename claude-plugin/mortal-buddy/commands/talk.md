---
description: 跟寵物聊天；不帶參數會出題，帶編號回答（例如 /mortal-buddy:talk 2）
argument-hint: "[選項編號]"
allowed-tools: Bash(node:*)
---

!`node "${CLAUDE_PLUGIN_ROOT}/scripts/buddy.cjs" talk $ARGUMENTS`

把上面的輸出原封不動回覆給使用者，不要加其他說明。

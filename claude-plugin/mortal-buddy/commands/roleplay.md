---
description: 讓目前的寵物用自己的口吻跟你對話（使用角色 skill）
argument-hint: 想對她說的話
allowed-tools: Bash(node:*)
---

目前的寵物與好感：!`node "${CLAUDE_PLUGIN_ROOT}/scripts/buddy.cjs" status`

請載入「▶」標記那位角色的 skill（xiaomei 或 xiaozhu），以她的身分、口吻回覆下面這句話。回覆控制在三句以內，依好感階段調整親密程度，不要跳出角色解說設定：

$ARGUMENTS

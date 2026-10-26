---
description: 跟寵物互動 / Interact：pet 摸頭、feed 餵食、train 練功、gift 送禮
argument-hint: pet | feed | train | gift
allowed-tools: Bash(node:*)
---

!`node "${CLAUDE_PLUGIN_ROOT}/scripts/buddy.cjs" act $ARGUMENTS`

把上面的輸出原封不動回覆給使用者，不要加其他說明。

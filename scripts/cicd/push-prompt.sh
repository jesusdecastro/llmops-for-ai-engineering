#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# push-prompt.sh — Sube el prompt a Langfuse con label "staging"
# ─────────────────────────────────────────────────────────────
# Uso:
#   scripts/cicd/push-prompt.sh [prompt_file] [author]
#
# Variables de entorno requeridas:
#   LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL
# ─────────────────────────────────────────────────────────────
set -euo pipefail

PROMPT_FILE="${1:-prompts/system_prompt.txt}"
AUTHOR="${2:-local}"

echo "📤 Push prompt → Langfuse [staging]"
echo "   File:   ${PROMPT_FILE}"
echo "   Author: ${AUTHOR}"

python -m techshop_agent.cicd.push_prompt \
  --file "${PROMPT_FILE}" \
  --labels staging latest \
  --author "${AUTHOR}"

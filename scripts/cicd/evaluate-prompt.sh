#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# evaluate-prompt.sh — Quality Gate: evalúa el prompt en staging
# ─────────────────────────────────────────────────────────────
# Uso:
#   scripts/cicd/evaluate-prompt.sh [label] [threshold]
#
# Variables de entorno requeridas:
#   LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL
#   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
# ─────────────────────────────────────────────────────────────
set -euo pipefail

LABEL="${1:-staging}"
THRESHOLD="${2:-0.7}"

echo "🧪 Evaluate prompt [${LABEL}]"
echo "   Threshold: ${THRESHOLD}"

python -m techshop_agent.cicd.evaluate_prompt \
  --label "${LABEL}" \
  --threshold "${THRESHOLD}"

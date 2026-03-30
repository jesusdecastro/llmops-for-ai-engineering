#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# promote-prompt.sh — Promueve staging → production
# ─────────────────────────────────────────────────────────────
# Uso:
#   scripts/cicd/promote-prompt.sh [from_label] [to_label]
#
# Variables de entorno requeridas:
#   LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL
# ─────────────────────────────────────────────────────────────
set -euo pipefail

FROM_LABEL="${1:-staging}"
TO_LABEL="${2:-production}"

echo "🚀 Promote prompt: ${FROM_LABEL} → ${TO_LABEL}"

python -m techshop_agent.cicd.promote_prompt \
  --from-label "${FROM_LABEL}" \
  --to-label "${TO_LABEL}"

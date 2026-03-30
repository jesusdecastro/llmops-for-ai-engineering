#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# run-pipeline.sh — Ejecuta el pipeline CI/CD completo en local
# ─────────────────────────────────────────────────────────────
# Reproduce el mismo flujo que GitHub Actions / GitLab CI:
#   1. push-prompt.sh   → sube prompt a Langfuse [staging]
#   2. evaluate-prompt.sh → quality gate
#   3. promote-prompt.sh  → promueve staging → production
#
# Uso:
#   scripts/cicd/run-pipeline.sh                          # pipeline completo
#   scripts/cicd/run-pipeline.sh --staging-only            # solo CI (push + evaluate)
#   scripts/cicd/run-pipeline.sh --file prompts/v2.txt     # prompt custom
#   scripts/cicd/run-pipeline.sh --threshold 0.8           # umbral custom
#
# Requisitos:
#   - pip install -e ".[llmops]"
#   - Variables de entorno en .env o exportadas:
#     LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL
#     AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Defaults ────────────────────────────────────────────────
PROMPT_FILE="prompts/system_prompt.txt"
THRESHOLD="0.7"
STAGING_ONLY=false

# ── Parse arguments ─────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)         PROMPT_FILE="$2"; shift 2 ;;
    --threshold)    THRESHOLD="$2"; shift 2 ;;
    --staging-only) STAGING_ONLY=true; shift ;;
    -h|--help)
      echo "Usage: $0 [--file <path>] [--threshold <0.0-1.0>] [--staging-only]"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

echo "═══════════════════════════════════════════════════════"
echo "  Prompt CI/CD Pipeline — Local"
echo "═══════════════════════════════════════════════════════"
echo ""

# ── Step 1: Push ────────────────────────────────────────────
"${SCRIPT_DIR}/push-prompt.sh" "${PROMPT_FILE}" "local-dev"

echo ""

# ── Step 2: Evaluate ────────────────────────────────────────
"${SCRIPT_DIR}/evaluate-prompt.sh" "staging" "${THRESHOLD}"

if [ "${STAGING_ONLY}" = true ]; then
  echo ""
  echo "✅ Staging pipeline complete (--staging-only mode)"
  exit 0
fi

echo ""

# ── Step 3: Promote ────────────────────────────────────────
"${SCRIPT_DIR}/promote-prompt.sh" "staging" "production"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  ✅ Pipeline complete — prompt promoted to production"
echo "═══════════════════════════════════════════════════════"

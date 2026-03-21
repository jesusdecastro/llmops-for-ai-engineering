#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TERRAFORM_DIR="${INFRA_DIR}/terraform"
BACKUP_DIR="${INFRA_DIR}/backups"

mkdir -p "${BACKUP_DIR}"

cd "${TERRAFORM_DIR}"
PUBLIC_IP="$(terraform output -raw instance_public_ip)"
RAW_KEY_PATH="$(terraform output -raw ssh_private_key_path)"
KEY_PATH="$(python3 - <<'PY' "${TERRAFORM_DIR}" "${RAW_KEY_PATH}"
from __future__ import annotations
import pathlib
import sys

terraform_dir = pathlib.Path(sys.argv[1]).resolve()
raw = pathlib.Path(sys.argv[2])
if raw.is_absolute():
    print(raw.resolve())
else:
    print((terraform_dir / raw).resolve())
PY
)"
TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
LOCAL_FILE="${BACKUP_DIR}/langfuse-backup-${TIMESTAMP}.sql.gz"

ssh -o StrictHostKeyChecking=no -i "${KEY_PATH}" ubuntu@"${PUBLIC_IP}" 'bash -s' <<'REMOTE'
set -euo pipefail
TS="$(date -u +"%Y%m%dT%H%M%SZ")"
FILE="/tmp/langfuse-backup-${TS}.sql.gz"
cd /opt/langfuse
docker compose --env-file .env -f docker-compose.yml exec -T postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip -9 > "$FILE"
echo "$FILE"
REMOTE

REMOTE_ACTUAL_FILE="$(ssh -o StrictHostKeyChecking=no -i "${KEY_PATH}" ubuntu@"${PUBLIC_IP}" "ls -1t /tmp/langfuse-backup-*.sql.gz | head -n 1")"
scp -o StrictHostKeyChecking=no -i "${KEY_PATH}" ubuntu@"${PUBLIC_IP}":"${REMOTE_ACTUAL_FILE}" "${LOCAL_FILE}"
ssh -o StrictHostKeyChecking=no -i "${KEY_PATH}" ubuntu@"${PUBLIC_IP}" "rm -f '${REMOTE_ACTUAL_FILE}'"

echo "Backup guardado en: ${LOCAL_FILE}"

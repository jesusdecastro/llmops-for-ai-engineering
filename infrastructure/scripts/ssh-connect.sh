#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TERRAFORM_DIR="${INFRA_DIR}/terraform"

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

exec ssh -o StrictHostKeyChecking=no -i "${KEY_PATH}" ubuntu@"${PUBLIC_IP}"

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TERRAFORM_DIR="${INFRA_DIR}/terraform"
AWS_CONFIG="${INFRA_DIR}/config/aws-config.yaml"
GENERATED_DIR="${INFRA_DIR}/generated"
TFVARS_JSON="${GENERATED_DIR}/terraform.auto.tfvars.json"

read -r -p "Esto eliminará toda la infraestructura. ¿Continuar? (yes/no): " CONFIRM
if [[ "${CONFIRM}" != "yes" ]]; then
  echo "Operación cancelada"
  exit 0
fi

read -r -p "¿Quieres ejecutar backup antes de destruir? (yes/no): " DO_BACKUP
if [[ "${DO_BACKUP}" == "yes" ]]; then
  "${SCRIPT_DIR}/backup.sh"
fi

mkdir -p "${GENERATED_DIR}"
python3 - <<'PY' "${AWS_CONFIG}" "${TFVARS_JSON}"
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

cfg = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8")) or {}
aws = cfg.get("aws", {})
project = cfg.get("project", {})
instance = cfg.get("instance", {})
networking = cfg.get("networking", {})
security = cfg.get("security", {})
monitoring = cfg.get("monitoring", {})
ssm = cfg.get("ssm", {})

data = {
    "aws_profile": aws.get("profile", "default"),
    "aws_region": aws.get("region", "us-east-1"),
    "project_name": project.get("name", "langfuse-workshop"),
    "environment": project.get("environment", "training"),
    "owner_email": project.get("owner", "instructor@example.com"),
    "instance_type": instance.get("type", "t3.xlarge"),
    "volume_size": int(instance.get("volume_size", 100)),
    "vpc_cidr": networking.get("vpc_cidr", "10.0.0.0/16"),
    "public_subnet_cidr": networking.get("public_subnet_cidr", "10.0.1.0/24"),
    "ssh_allowed_cidrs": security.get("ssh_allowed_cidrs", ["0.0.0.0/0"]),
    "langfuse_allowed_cidrs": security.get("langfuse_allowed_cidrs", ["0.0.0.0/0"]),
    "enable_https": bool(security.get("enable_https", False)),
    "langfuse_port": int(security.get("langfuse_port", 3000)),
    "alert_email": monitoring.get("alert_email", project.get("owner", "instructor@example.com")),
    "enable_cloudwatch": bool(monitoring.get("enable_cloudwatch", True)),
    "log_retention_days": int(monitoring.get("log_retention_days", 7)),
    "parameter_prefix": ssm.get("parameter_prefix", "/langfuse/workshop"),
    "tags": cfg.get("tags", {}),
}

Path(sys.argv[2]).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY

AWS_PROFILE="$(python3 - <<'PY' "${AWS_CONFIG}"
from __future__ import annotations

import sys
from pathlib import Path

import yaml

cfg = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8")) or {}
print((cfg.get("aws") or {}).get("profile", "default"))
PY
)"
AWS_REGION="$(python3 - <<'PY' "${AWS_CONFIG}"
from __future__ import annotations

import sys
from pathlib import Path

import yaml

cfg = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8")) or {}
print((cfg.get("aws") or {}).get("region", "us-east-1"))
PY
)"
PARAMETER_PREFIX="$(python3 - <<'PY' "${AWS_CONFIG}"
from __future__ import annotations

import sys
from pathlib import Path

import yaml

cfg = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8")) or {}
print((cfg.get("ssm") or {}).get("parameter_prefix", "/langfuse/workshop"))
PY
)"

export AWS_PROFILE AWS_REGION

cd "${TERRAFORM_DIR}"
terraform init -upgrade
terraform destroy -auto-approve -var-file="${TFVARS_JSON}"

for secret_name in \
  nextauth-secret \
  salt \
  encryption-key \
  postgres-password \
  clickhouse-password \
  minio-password \
  admin-password \
  api-secret-key
  do
    aws ssm delete-parameter --name "${PARAMETER_PREFIX}/${secret_name}" >/dev/null 2>&1 || true
  done

echo "Infraestructura y secretos eliminados"

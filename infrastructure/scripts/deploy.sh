#!/usr/bin/env bash
set -Eeuo pipefail

on_error() {
  local line="$1"
  local cmd="$2"
  local code="$3"
  printf 'ERROR: command failed (exit=%s) at line %s: %s\n' "${code}" "${line}" "${cmd}" >&2
  exit "${code}"
}
trap 'on_error "${LINENO}" "${BASH_COMMAND}" "$?"' ERR

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ROOT_DIR="$(cd "${INFRA_DIR}/.." && pwd)"

AWS_CONFIG="${INFRA_DIR}/config/aws-config.yaml"
LANGFUSE_CONFIG="${INFRA_DIR}/config/langfuse-config.yaml"
TERRAFORM_DIR="${INFRA_DIR}/terraform"
DOCKER_COMPOSE_FILE="${INFRA_DIR}/docker/docker-compose.yml"
GENERATED_DIR="${INFRA_DIR}/generated"
TFVARS_JSON="${GENERATED_DIR}/terraform.auto.tfvars.json"
OUTPUTS_JSON="${GENERATED_DIR}/terraform-outputs.json"
ENV_FILE="${GENERATED_DIR}/langfuse.env"

mkdir -p "${GENERATED_DIR}"

log() {
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*"
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

validate_prerequisites() {
  log "Validating prerequisites..."
  require_cmd aws
  require_cmd terraform
  require_cmd ssh
  require_cmd scp
  require_cmd python3
  require_cmd curl
  require_cmd jq
  require_cmd yq

  python3 - <<'PY'
import importlib.util
missing = []
for pkg in ("yaml", "boto3"):
    if importlib.util.find_spec(pkg) is None:
        missing.append(pkg)
if missing:
    raise SystemExit(f"Missing Python packages: {', '.join(missing)}")
print("Python package validation passed")
PY
}

validate_configuration() {
  log "Validating configuration files..."
  [[ -f "${AWS_CONFIG}" ]] || fail "Missing AWS config: ${AWS_CONFIG}"
  [[ -f "${LANGFUSE_CONFIG}" ]] || fail "Missing Langfuse config: ${LANGFUSE_CONFIG}"
  [[ -f "${DOCKER_COMPOSE_FILE}" ]] || fail "Missing docker-compose file: ${DOCKER_COMPOSE_FILE}"

  (
    cd "${ROOT_DIR}"
    python3 infrastructure/scripts/config_validator.py
  )

  local required_keys=(aws project instance networking security monitoring ssm tags)
  for key in "${required_keys[@]}"; do
    yq eval ".${key}" "${AWS_CONFIG}" >/dev/null
    [[ "$(yq eval "has(\"${key}\")" "${AWS_CONFIG}")" == "true" ]] || fail "Missing key in aws-config.yaml: ${key}"
  done
}

generate_tfvars_from_config() {
  log "Generating terraform.auto.tfvars.json from aws-config.yaml..."
  yq eval -o=json '.' "${AWS_CONFIG}" | jq '{
    aws_profile: (.aws.profile // "default"),
    aws_region: (.aws.region // "us-east-1"),
    project_name: (.project.name // "langfuse-workshop"),
    environment: (.project.environment // "training"),
    owner_email: (.project.owner // "instructor@example.com"),
    instance_type: (.instance.type // "t3.xlarge"),
    volume_size: (.instance.volume_size // 100),
    vpc_cidr: (.networking.vpc_cidr // "10.0.0.0/16"),
    public_subnet_cidr: (.networking.public_subnet_cidr // "10.0.1.0/24"),
    ssh_allowed_cidrs: (.security.ssh_allowed_cidrs // ["0.0.0.0/0"]),
    langfuse_allowed_cidrs: (.security.langfuse_allowed_cidrs // ["0.0.0.0/0"]),
    enable_https: (.security.enable_https // false),
    langfuse_port: (.security.langfuse_port // 3000),
    alert_email: (.monitoring.alert_email // .project.owner // "instructor@example.com"),
    enable_cloudwatch: (.monitoring.enable_cloudwatch // true),
    log_retention_days: (.monitoring.log_retention_days // 7),
    parameter_prefix: (.ssm.parameter_prefix // "/langfuse/workshop"),
    tags: (.tags // {})
  }' > "${TFVARS_JSON}"

  jq empty "${TFVARS_JSON}" >/dev/null
}

export_aws_env() {
  log "Exporting AWS environment variables..."
  export AWS_PROFILE
  AWS_PROFILE="$(jq -r '.aws_profile' "${TFVARS_JSON}")"
  export AWS_REGION
  AWS_REGION="$(jq -r '.aws_region' "${TFVARS_JSON}")"

  [[ -n "${AWS_PROFILE}" && "${AWS_PROFILE}" != "null" ]] || fail "Invalid aws_profile in ${TFVARS_JSON}"
  [[ -n "${AWS_REGION}" && "${AWS_REGION}" != "null" ]] || fail "Invalid aws_region in ${TFVARS_JSON}"

  aws sts get-caller-identity --output json >/dev/null
}

generate_and_store_secrets() {
  log "Generating secrets and storing in SSM Parameter Store..."
  local parameter_prefix
  parameter_prefix="$(jq -r '.parameter_prefix' "${TFVARS_JSON}")"

  python3 - <<'PY' "${SCRIPT_DIR}/secret_utils.py" "${parameter_prefix}" "${AWS_REGION}" "${AWS_PROFILE}"
from __future__ import annotations
import importlib.util
import pathlib
import sys
import boto3

secret_utils_path = pathlib.Path(sys.argv[1]).resolve()
parameter_prefix = sys.argv[2]
region = sys.argv[3]
profile = sys.argv[4]

spec = importlib.util.spec_from_file_location("secret_utils", secret_utils_path)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load secret_utils from {secret_utils_path}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
secret_map = module.build_secret_map()

session = boto3.Session(region_name=region, profile_name=profile)
ssm = session.client("ssm")

for name, value in secret_map.items():
    ssm.put_parameter(
        Name=f"{parameter_prefix}/{name}",
        Value=value,
        Type="SecureString",
        Overwrite=True,
    )
print(f"Stored {len(secret_map)} secrets under {parameter_prefix}")
PY
}

terraform_apply() {
  log "Running terraform apply..."
  (
    cd "${TERRAFORM_DIR}"
    terraform init -upgrade
    terraform apply -auto-approve -var-file="${TFVARS_JSON}"
    terraform output -json > "${OUTPUTS_JSON}"
  )
  jq empty "${OUTPUTS_JSON}" >/dev/null
}

read_tf_output() {
  local key="$1"
  jq -r --arg key "${key}" '.[$key].value' "${OUTPUTS_JSON}"
}

resolve_ssh_key_path() {
  local raw_path="$1"
  python3 - <<'PY' "${TERRAFORM_DIR}" "${raw_path}"
from __future__ import annotations
import pathlib
import sys

terraform_dir = pathlib.Path(sys.argv[1]).resolve()
raw = sys.argv[2]

path = pathlib.Path(raw)
if path.is_absolute():
    print(path.resolve())
else:
    print((terraform_dir / path).resolve())
PY
}

wait_for_instance() {
  local instance_id="$1"
  local public_ip="$2"
  local key_path="$3"

  log "Waiting for EC2 instance status checks..."
  aws ec2 wait instance-status-ok --instance-ids "${instance_id}" --region "${AWS_REGION}"

  log "Waiting for SSH availability..."
  local attempt=1
  until ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -i "${key_path}" ubuntu@"${public_ip}" 'echo ssh-ready' >/dev/null 2>&1; do
    if [[ "${attempt}" -ge 30 ]]; then
      fail "Timeout waiting for SSH access to ${public_ip}"
    fi
    sleep 10
    attempt=$((attempt + 1))
  done
}

install_docker() {
  local public_ip="$1"
  local key_path="$2"

  log "Installing Docker on instance (if needed)..."
  ssh -o StrictHostKeyChecking=no -i "${key_path}" ubuntu@"${public_ip}" 'bash -s' <<'REMOTE'
set -Eeuo pipefail

if ! command -v docker >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y ca-certificates curl gnupg lsb-release
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  sudo chmod a+r /etc/apt/keyrings/docker.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo ${VERSION_CODENAME}) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
  sudo apt-get update -y
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  sudo usermod -aG docker ubuntu || true
fi

sudo mkdir -p /opt/langfuse /opt/langfuse/data
if ! mountpoint -q /opt/langfuse/data; then
  DEVICE=""
  for candidate in /dev/nvme1n1 /dev/xvdf /dev/sdf; do
    if [[ -b "${candidate}" ]]; then
      DEVICE="${candidate}"
      break
    fi
  done

  if [[ -n "${DEVICE}" ]]; then
    if ! sudo blkid "${DEVICE}" >/dev/null 2>&1; then
      sudo mkfs.ext4 -F "${DEVICE}"
    fi
    UUID="$(sudo blkid -s UUID -o value "${DEVICE}")"
    if ! grep -q "${UUID}" /etc/fstab; then
      echo "UUID=${UUID} /opt/langfuse/data ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab >/dev/null
    fi
    sudo mount -a
  fi
fi
REMOTE
}

deploy_stack() {
  local public_ip="$1"
  local key_path="$2"
  local parameter_prefix="$3"

  log "Generating .env file with env_generator.py..."
  python3 "${SCRIPT_DIR}/env_generator.py" \
    --config "${LANGFUSE_CONFIG}" \
    --output "${ENV_FILE}" \
    --aws-region "${AWS_REGION}" \
    --aws-profile "${AWS_PROFILE}" \
    --parameter-prefix "${parameter_prefix}" \
    --public-host "${public_ip}" \
    --data-dir "/opt/langfuse/data"

  log "Copying docker-compose and .env to instance..."
  scp -o StrictHostKeyChecking=no -i "${key_path}" "${DOCKER_COMPOSE_FILE}" ubuntu@"${public_ip}":/tmp/docker-compose.yml
  scp -o StrictHostKeyChecking=no -i "${key_path}" "${ENV_FILE}" ubuntu@"${public_ip}":/tmp/.env

  log "Deploying Docker Compose stack..."
  ssh -o StrictHostKeyChecking=no -i "${key_path}" ubuntu@"${public_ip}" 'bash -s' <<'REMOTE'
set -Eeuo pipefail
sudo mkdir -p /opt/langfuse
sudo mv /tmp/docker-compose.yml /opt/langfuse/docker-compose.yml
sudo mv /tmp/.env /opt/langfuse/.env
sudo chown -R ubuntu:ubuntu /opt/langfuse

cd /opt/langfuse

docker compose --env-file .env -f docker-compose.yml pull
docker compose --env-file .env -f docker-compose.yml up -d
REMOTE
}

wait_for_health() {
  local public_ip="$1"
  local key_path="$2"
  local port="$3"
  local url="http://${public_ip}:${port}/api/public/health"

  log "Waiting for service health endpoint: ${url}"
  local attempt=1
  until curl -fsS "${url}" >/dev/null 2>&1; do
    if [[ "${attempt}" -ge 45 ]]; then
      ssh -o StrictHostKeyChecking=no -i "${key_path}" ubuntu@"${public_ip}" "docker compose --env-file /opt/langfuse/.env -f /opt/langfuse/docker-compose.yml ps" || true
      fail "Health check failed after multiple attempts: ${url}"
    fi
    sleep 10
    attempt=$((attempt + 1))
  done
}

output_info() {
  local public_ip="$1"
  local port="$2"

  local admin_email
  admin_email="$(yq eval '.langfuse.init.admin_email // "admin@langfuse.local"' "${LANGFUSE_CONFIG}")"

  local url="http://${public_ip}:${port}"
  printf '\n'
  printf '========================================\n'
  printf 'Deployment completed successfully\n'
  printf 'Langfuse URL: %s\n' "${url}"
  printf 'Admin email: %s\n' "${admin_email}"
  printf '========================================\n'
}

main() {
  validate_prerequisites
  validate_configuration
  generate_tfvars_from_config
  export_aws_env
  generate_and_store_secrets
  terraform_apply

  local instance_id
  instance_id="$(read_tf_output instance_id)"

  local public_ip
  public_ip="$(read_tf_output instance_public_ip)"

  local raw_key_path
  raw_key_path="$(read_tf_output ssh_private_key_path)"

  local key_path
  key_path="$(resolve_ssh_key_path "${raw_key_path}")"
  [[ -f "${key_path}" ]] || fail "SSH key not found at resolved path: ${key_path}"
  chmod 600 "${key_path}" || true

  local parameter_prefix
  parameter_prefix="$(read_tf_output parameter_store_prefix)"

  local langfuse_port
  langfuse_port="$(jq -r '.langfuse_port' "${TFVARS_JSON}")"

  wait_for_instance "${instance_id}" "${public_ip}" "${key_path}"
  install_docker "${public_ip}" "${key_path}"
  deploy_stack "${public_ip}" "${key_path}" "${parameter_prefix}"
  wait_for_health "${public_ip}" "${key_path}" "${langfuse_port}"
  output_info "${public_ip}" "${langfuse_port}"
}

main "$@"

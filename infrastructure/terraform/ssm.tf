locals {
  secret_parameter_names = [
    "nextauth-secret",
    "salt",
    "encryption-key",
    "postgres-password",
    "clickhouse-password",
    "minio-password",
    "admin-password",
    "api-secret-key",
  ]
}

resource "aws_ssm_parameter" "secrets" {
  for_each = toset(local.secret_parameter_names)

  name  = "${var.parameter_prefix}/${each.value}"
  type  = "SecureString"
  value = "PLACEHOLDER_TO_BE_UPDATED_BY_DEPLOY_SCRIPT"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-${each.value}"
  })

  lifecycle {
    ignore_changes = [value]
  }
}
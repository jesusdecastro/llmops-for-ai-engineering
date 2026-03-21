locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      Owner       = var.owner_email
      ManagedBy   = "Terraform"
    },
    var.tags,
  )
}

data "aws_availability_zones" "available" {
  state = "available"
}
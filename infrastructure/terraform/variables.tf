variable "aws_profile" {
  description = "AWS CLI profile to use"
  type        = string
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "langfuse-workshop"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "training"
}

variable "owner_email" {
  description = "Owner email for tags and alerts"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.xlarge"
}

variable "volume_size" {
  description = "Data volume size in GiB"
  type        = number
  default     = 100
}

variable "vpc_cidr" {
  description = "VPC CIDR"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "Public subnet CIDR"
  type        = string
  default     = "10.0.1.0/24"
}

variable "ssh_allowed_cidrs" {
  description = "CIDR blocks allowed for SSH"
  type        = list(string)
}

variable "langfuse_allowed_cidrs" {
  description = "CIDR blocks allowed for Langfuse UI"
  type        = list(string)
}

variable "enable_https" {
  description = "Enable HTTPS ingress (port 443)"
  type        = bool
  default     = false
}

variable "langfuse_port" {
  description = "Langfuse UI port"
  type        = number
  default     = 3000
}

variable "alert_email" {
  description = "Email for CloudWatch alarm notifications"
  type        = string
}

variable "enable_cloudwatch" {
  description = "Enable CloudWatch dashboard and alarms"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7
}

variable "parameter_prefix" {
  description = "SSM Parameter Store prefix"
  type        = string
  default     = "/langfuse/workshop"
}

variable "ssh_private_key_output_path" {
  description = "Local path for generated SSH private key"
  type        = string
  default     = "../generated/langfuse-workshop.pem"
}

variable "tags" {
  description = "Additional tags applied to all resources"
  type        = map(string)
  default     = {}
}
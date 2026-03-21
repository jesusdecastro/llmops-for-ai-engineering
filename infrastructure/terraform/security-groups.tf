resource "aws_security_group" "langfuse" {
  name        = "${local.name_prefix}-sg"
  description = "Security group for Langfuse workshop"
  vpc_id      = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-sg"
  })
}

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  for_each          = toset(var.ssh_allowed_cidrs)
  security_group_id = aws_security_group.langfuse.id
  cidr_ipv4         = each.value
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
  description       = "SSH access"
}

resource "aws_vpc_security_group_ingress_rule" "langfuse_ui" {
  for_each          = toset(var.langfuse_allowed_cidrs)
  security_group_id = aws_security_group.langfuse.id
  cidr_ipv4         = each.value
  from_port         = var.langfuse_port
  to_port           = var.langfuse_port
  ip_protocol       = "tcp"
  description       = "Langfuse UI"
}

resource "aws_vpc_security_group_ingress_rule" "https" {
  for_each          = var.enable_https ? toset(var.langfuse_allowed_cidrs) : toset([])
  security_group_id = aws_security_group.langfuse.id
  cidr_ipv4         = each.value
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  description       = "HTTPS access"
}

resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.langfuse.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
  description       = "Allow all outbound traffic"
}
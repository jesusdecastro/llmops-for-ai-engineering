data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_sensitive_file" "ssh_private_key" {
  content         = tls_private_key.ssh.private_key_pem
  filename        = var.ssh_private_key_output_path
  file_permission = "0600"
}

resource "aws_key_pair" "generated" {
  key_name   = "${local.name_prefix}-key"
  public_key = tls_private_key.ssh.public_key_openssh

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-key"
  })
}

data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ec2" {
  name               = "${local.name_prefix}-ec2-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "cloudwatch_agent" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

data "aws_iam_policy_document" "ssm_read" {
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath",
      "ssm:DescribeParameters",
    ]
    resources = [
      "arn:aws:ssm:${var.aws_region}:*:parameter${var.parameter_prefix}*",
    ]
  }
}

resource "aws_iam_role_policy" "ssm_read" {
  name   = "${local.name_prefix}-ssm-read"
  role   = aws_iam_role.ec2.id
  policy = data.aws_iam_policy_document.ssm_read.json
}

data "aws_iam_policy_document" "cloudwatch_logs_write" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "cloudwatch_logs_write" {
  name   = "${local.name_prefix}-cloudwatch-logs"
  role   = aws_iam_role.ec2.id
  policy = data.aws_iam_policy_document.cloudwatch_logs_write.json
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${local.name_prefix}-instance-profile"
  role = aws_iam_role.ec2.name
}

resource "aws_instance" "langfuse" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.langfuse.id]
  key_name                    = aws_key_pair.generated.key_name
  iam_instance_profile        = aws_iam_instance_profile.ec2.name

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = <<-EOT
    #!/bin/bash
    set -eux
    apt-get update -y
    apt-get install -y curl unzip
    curl -fsSL https://amazoncloudwatch-agent.s3.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb -o /tmp/amazon-cloudwatch-agent.deb
    dpkg -i /tmp/amazon-cloudwatch-agent.deb
    python3 -c 'import pathlib; pathlib.Path("/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json").write_text("""{
      \"metrics\": {
        \"append_dimensions\": {
            \"InstanceId\": \"$${aws:InstanceId}\"
        },
        \"metrics_collected\": {
          \"cpu\": {
            \"measurement\": [
              \"cpu_usage_idle\",
              \"cpu_usage_iowait\",
              \"cpu_usage_system\",
              \"cpu_usage_user\"
            ],
            \"totalcpu\": true
          },
          \"mem\": {
            \"measurement\": [
              \"mem_used_percent\"
            ]
          },
          \"disk\": {
            \"measurement\": [
              \"used_percent\"
            ],
            \"resources\": [
              \"*\"
            ]
          }
        }
      },
      \"logs\": {
        \"logs_collected\": {
          \"files\": {
            \"collect_list\": [
              {
                \"file_path\": \"/var/lib/docker/containers/*/*.log\",
                \"log_group_name\": \"/langfuse/workshop/docker\",
                \"log_stream_name\": \"{instance_id}\",
                \"timezone\": \"UTC\"
              }
            ]
          }
        }
      }
    }
    """)'
    /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s
  EOT

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ec2"
  })
}

resource "aws_ebs_volume" "data" {
  availability_zone = aws_instance.langfuse.availability_zone
  size              = var.volume_size
  type              = "gp3"
  encrypted         = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-data"
  })
}

resource "aws_volume_attachment" "data" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.data.id
  instance_id = aws_instance.langfuse.id
}
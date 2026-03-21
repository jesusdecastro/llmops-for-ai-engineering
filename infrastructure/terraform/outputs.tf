output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.langfuse.id
}

output "instance_public_ip" {
  description = "Public IP of EC2 instance"
  value       = aws_instance.langfuse.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of EC2 instance"
  value       = aws_instance.langfuse.public_dns
}

output "security_group_id" {
  description = "Security group ID"
  value       = aws_security_group.langfuse.id
}

output "ssh_private_key_path" {
  description = "Local path to generated private key"
  value       = local_sensitive_file.ssh_private_key.filename
  sensitive   = true
}

output "ssh_command" {
  description = "SSH command to connect to EC2"
  value       = "ssh -i ${local_sensitive_file.ssh_private_key.filename} ubuntu@${aws_instance.langfuse.public_ip}"
}

output "langfuse_url" {
  description = "Langfuse UI URL"
  value       = "http://${aws_instance.langfuse.public_ip}:${var.langfuse_port}"
}

output "parameter_store_prefix" {
  description = "SSM parameter prefix"
  value       = var.parameter_prefix
}
# Design Document: AWS Langfuse Deployment

## Overview

This design specifies the implementation of an automated deployment system for Langfuse v3 on AWS infrastructure. The system uses Terraform for infrastructure provisioning, Bash scripts for deployment orchestration, and Docker Compose for service orchestration. The design prioritizes parametrization, security for remote access, and ease of use for workshop instructors with minimal AWS experience.

### Design Goals

1. **Single-command deployment**: Instructor runs one script to provision and deploy everything
2. **Parametrized configuration**: All AWS-specific values are externalized to configuration files
3. **Security by default**: Encrypted storage, restricted access, secure secrets management
4. **Observable**: CloudWatch monitoring and logging for troubleshooting
5. **Cost-effective**: Optimized for 3-day workshop budget (~$13-15)
6. **Idempotent**: Safe to re-run scripts without creating duplicate resources

### Technology Stack

- **Infrastructure-as-Code**: Terraform 1.5+
- **Configuration Format**: YAML for human-readable config files
- **Scripting**: Bash for deployment orchestration
- **Container Orchestration**: Docker Compose
- **Secrets Management**: AWS Systems Manager Parameter Store
- **Monitoring**: CloudWatch Metrics, Logs, and Dashboards
- **Operating System**: Ubuntu 24.04 LTS (better Docker support than Amazon Linux)


## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Local Development Machine                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Configuration Files                                        │ │
│  │  - infrastructure/config/aws-config.yaml                   │ │
│  │  - infrastructure/config/langfuse-config.yaml              │ │
│  │  - infrastructure/terraform/terraform.tfvars               │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Deployment Script (infrastructure/scripts/deploy.sh)      │ │
│  │  1. Validate configuration                                 │ │
│  │  2. Run Terraform (provision AWS resources)                │ │
│  │  3. Wait for EC2 ready                                     │ │
│  │  4. Install Docker via SSH                                 │ │
│  │  5. Deploy Docker Compose stack                            │ │
│  │  6. Configure Langfuse                                     │ │
│  │  7. Output access credentials                              │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ AWS CLI + Terraform + SSH
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  AWS Account                                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  VPC (10.0.0.0/16)                                         │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  Public Subnet (10.0.1.0/24)                        │  │  │
│  │  │  ┌───────────────────────────────────────────────┐  │  │  │
│  │  │  │  EC2 Instance (t3.xlarge)                     │  │  │  │
│  │  │  │  - Ubuntu 24.04 LTS                           │  │  │  │
│  │  │  │  - 100 GiB gp3 EBS (encrypted)                │  │  │  │
│  │  │  │  - IAM Instance Profile                       │  │  │  │
│  │  │  │  - CloudWatch Agent                           │  │  │  │
│  │  │  │  ┌─────────────────────────────────────────┐  │  │  │  │
│  │  │  │  │  Docker Compose Stack                   │  │  │  │  │
│  │  │  │  │  ┌───────────────────────────────────┐  │  │  │  │  │
│  │  │  │  │  │  langfuse-web (port 3000)         │  │  │  │  │  │
│  │  │  │  │  │  - Langfuse UI and API            │  │  │  │  │  │
│  │  │  │  │  └───────────────────────────────────┘  │  │  │  │  │
│  │  │  │  │  ┌───────────────────────────────────┐  │  │  │  │  │
│  │  │  │  │  │  langfuse-worker                  │  │  │  │  │  │
│  │  │  │  │  │  - Background job processing      │  │  │  │  │  │
│  │  │  │  │  └───────────────────────────────────┘  │  │  │  │  │
│  │  │  │  │  ┌───────────────────────────────────┐  │  │  │  │  │
│  │  │  │  │  │  postgres (port 5432)             │  │  │  │  │  │
│  │  │  │  │  │  - Primary database               │  │  │  │  │  │
│  │  │  │  │  └───────────────────────────────────┘  │  │  │  │  │
│  │  │  │  │  ┌───────────────────────────────────┐  │  │  │  │  │
│  │  │  │  │  │  clickhouse (port 8123, 9000)     │  │  │  │  │  │
│  │  │  │  │  │  - Analytics database             │  │  │  │  │  │
│  │  │  │  │  └───────────────────────────────────┘  │  │  │  │  │
│  │  │  │  │  ┌───────────────────────────────────┐  │  │  │  │  │
│  │  │  │  │  │  redis (port 6379)                │  │  │  │  │  │
│  │  │  │  │  │  - Cache and queue                │  │  │  │  │  │
│  │  │  │  │  └───────────────────────────────────┘  │  │  │  │  │
│  │  │  │  │  ┌───────────────────────────────────┐  │  │  │  │  │
│  │  │  │  │  │  minio (port 9000, 9001)          │  │  │  │  │  │
│  │  │  │  │  │  - S3-compatible object storage   │  │  │  │  │  │
│  │  │  │  │  └───────────────────────────────────┘  │  │  │  │  │
│  │  │  │  │  Data Volumes:                          │  │  │  │  │
│  │  │  │  │  - /opt/langfuse/data/postgres          │  │  │  │  │
│  │  │  │  │  - /opt/langfuse/data/clickhouse        │  │  │  │  │
│  │  │  │  │  - /opt/langfuse/data/redis             │  │  │  │  │
│  │  │  │  │  - /opt/langfuse/data/minio             │  │  │  │  │
│  │  │  │  └─────────────────────────────────────────┘  │  │  │  │
│  │  │  └───────────────────────────────────────────────┘  │  │  │
│  │  │  Security Group: langfuse-sg                         │  │  │
│  │  │  - Inbound: 22 (instructor IPs), 3000 (student IPs) │  │  │
│  │  │  - Outbound: All                                     │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │  Internet Gateway                                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  AWS Systems Manager Parameter Store                      │  │
│  │  - /langfuse/workshop/nextauth-secret (encrypted)         │  │
│  │  - /langfuse/workshop/salt (encrypted)                    │  │
│  │  - /langfuse/workshop/encryption-key (encrypted)          │  │
│  │  - /langfuse/workshop/postgres-password (encrypted)       │  │
│  │  - /langfuse/workshop/clickhouse-password (encrypted)     │  │
│  │  - /langfuse/workshop/minio-password (encrypted)          │  │
│  │  - /langfuse/workshop/admin-password (encrypted)          │  │
│  │  - /langfuse/workshop/api-keys (encrypted)                │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  CloudWatch                                                │  │
│  │  - Metrics: CPU, Memory, Disk, Network                    │  │
│  │  - Logs: Docker container logs                            │  │
│  │  - Dashboard: Langfuse Workshop Monitoring                │  │
│  │  - Alarms: CPU > 80%, Disk > 85%                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **Deployment Phase**:
   - Instructor configures YAML files with AWS credentials and parameters
   - Deployment script validates configuration
   - Terraform provisions VPC, subnet, security group, EC2 instance, IAM role
   - Script waits for EC2 to be running and SSH-accessible
   - Script generates secure secrets and stores in Parameter Store
   - Script installs Docker and Docker Compose on EC2 via SSH
   - Script copies docker-compose.yml and .env file to EC2
   - Script starts Docker Compose stack
   - Script waits for Langfuse health check to pass
   - Script outputs Langfuse URL and credentials

2. **Runtime Phase**:
   - Students access Langfuse UI at http://EC2_PUBLIC_IP:3000
   - Students use shared API keys with individual user_id tags
   - Langfuse web container serves UI and API requests
   - Langfuse worker processes background jobs (trace ingestion, analytics)
   - PostgreSQL stores user data, projects, traces metadata
   - ClickHouse stores analytics data for dashboards
   - Redis caches session data and queues background jobs
   - MinIO stores large trace payloads and attachments
   - CloudWatch Agent sends metrics and logs to CloudWatch
   - Instructor monitors CloudWatch dashboard for system health

3. **Teardown Phase**:
   - Instructor runs destroy script
   - Script prompts for confirmation
   - Terraform destroys all AWS resources
   - Parameter Store secrets are deleted
   - CloudWatch logs are retained for 7 days (configurable)


## Components and Interfaces

### 1. Configuration Layer

#### aws-config.yaml

```yaml
aws:
  profile: "default"                    # AWS CLI profile name
  region: "us-east-1"                   # AWS region
  account_id: ""                        # Optional, for validation

project:
  name: "langfuse-workshop"             # Project name (used in resource naming)
  environment: "training"               # Environment tag
  owner: "instructor@example.com"       # Owner email

instance:
  type: "t3.xlarge"                     # EC2 instance type
  volume_size: 100                      # EBS volume size in GiB
  ami: "ubuntu-24.04"                   # OS selection

security:
  ssh_allowed_cidrs:                    # IPs allowed to SSH
    - "203.0.113.0/24"                  # Instructor network
  langfuse_allowed_cidrs:               # IPs allowed to access Langfuse UI
    - "0.0.0.0/0"                       # All IPs (restrict for production)
  enable_https: false                   # Enable HTTPS with Let's Encrypt
  certificate_email: ""                 # Email for Let's Encrypt

monitoring:
  enable_cloudwatch: true               # Enable CloudWatch monitoring
  log_retention_days: 7                 # CloudWatch Logs retention
  alert_email: "instructor@example.com" # Email for CloudWatch alarms

tags:
  Project: "LLMOps-Workshop"
  Environment: "Training"
  ManagedBy: "Terraform"
  CostCenter: "Training"
```

#### langfuse-config.yaml

```yaml
langfuse:
  version: "3"                          # Langfuse Docker image version
  
  # Headless initialization
  init:
    org_id: "workshop-org"
    org_name: "LLM Workshop"
    project_id: "techshop-agent"
    project_name: "TechShop Agent"
    admin_email: "admin@workshop.local"
    admin_name: "Workshop Admin"
    # Passwords auto-generated if empty
    admin_password: ""
    
  # API keys for students
  api_keys:
    public_key: "lf_pk_workshop_shared"
    secret_key: ""                      # Auto-generated if empty
    
  # Resource limits for Docker containers
  resources:
    web:
      memory: "2Gi"
      cpu: "1"
    worker:
      memory: "2Gi"
      cpu: "1"
    postgres:
      memory: "4Gi"
      cpu: "1"
    clickhouse:
      memory: "4Gi"
      cpu: "1"
    redis:
      memory: "1Gi"
      cpu: "0.5"
    minio:
      memory: "1Gi"
      cpu: "0.5"
      
  # Security settings
  security:
    session_timeout_minutes: 480        # 8 hours
    allow_signup: false                 # Disable public registration
    
  # Data retention
  retention:
    traces_days: 30                     # Keep traces for 30 days
```

#### Interface: Configuration Validator

```python
class ConfigValidator:
    """Validates configuration files before deployment"""
    
    def validate_aws_config(config_path: str) -> ValidationResult:
        """
        Validates aws-config.yaml
        
        Checks:
        - AWS profile exists in ~/.aws/credentials
        - Region is valid AWS region
        - Instance type is valid EC2 instance type
        - CIDR blocks are valid
        - Email addresses are valid format
        
        Returns ValidationResult with errors list
        """
        
    def validate_langfuse_config(config_path: str) -> ValidationResult:
        """
        Validates langfuse-config.yaml
        
        Checks:
        - Version is valid Langfuse version
        - Resource limits are reasonable (memory >= 512Mi)
        - Email addresses are valid format
        - Session timeout is reasonable (> 0, < 1440 minutes)
        
        Returns ValidationResult with errors list
        """
        
    def validate_terraform_vars(tfvars_path: str) -> ValidationResult:
        """
        Validates terraform.tfvars
        
        Checks:
        - All required variables are present
        - Variable types match expected types
        - Values are within acceptable ranges
        
        Returns ValidationResult with errors list
        """
```

### 2. Terraform Infrastructure Module

#### Module Structure

```
infrastructure/terraform/
├── main.tf                 # Main Terraform configuration
├── variables.tf            # Input variables
├── outputs.tf              # Output values
├── versions.tf             # Provider versions
├── vpc.tf                  # VPC, subnet, IGW, route table
├── security-groups.tf      # Security group rules
├── ec2.tf                  # EC2 instance, EBS volume, IAM role
├── ssm.tf                  # Parameter Store for secrets
├── cloudwatch.tf           # CloudWatch dashboard and alarms
├── terraform.tfvars.example # Example variable values
└── backend.tf              # S3 backend for state (optional)
```

#### Key Resources

**VPC and Networking** (vpc.tf):
- VPC with CIDR 10.0.0.0/16
- Public subnet with CIDR 10.0.1.0/24
- Internet Gateway
- Route table with default route to IGW
- Route table association with public subnet

**Security Group** (security-groups.tf):
- Ingress rule: SSH (22) from instructor CIDRs
- Ingress rule: HTTP (3000) from student CIDRs
- Ingress rule: HTTPS (443) from student CIDRs (if enabled)
- Egress rule: All traffic to 0.0.0.0/0

**EC2 Instance** (ec2.tf):
- Instance type from configuration (default t3.xlarge)
- Ubuntu 24.04 LTS AMI (latest)
- EBS volume with encryption enabled
- IAM instance profile with role
- User data script for initial setup
- Tags from configuration

**IAM Role** (ec2.tf):
- Trust policy allowing EC2 to assume role
- Managed policy: CloudWatchAgentServerPolicy
- Inline policy: SSM Parameter Store read access for /langfuse/workshop/*
- Inline policy: CloudWatch Logs write access

**Parameter Store** (ssm.tf):
- Parameters for all secrets (encrypted with default KMS key)
- Parameters created with placeholder values
- Actual secrets generated and updated by deployment script

**CloudWatch** (cloudwatch.tf):
- Dashboard with widgets for CPU, memory, disk, network
- Alarm for CPU utilization > 80% for 5 minutes
- Alarm for disk utilization > 85%
- SNS topic for alarm notifications
- SNS email subscription

#### Interface: Terraform Outputs

```hcl
output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.langfuse.id
}

output "instance_public_ip" {
  description = "Public IP address of EC2 instance"
  value       = aws_instance.langfuse.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of EC2 instance"
  value       = aws_instance.langfuse.public_dns
}

output "security_group_id" {
  description = "Security group ID"
  value       = aws_security_group.langfuse.id
}

output "ssh_command" {
  description = "SSH command to connect to instance"
  value       = "ssh -i ${var.ssh_key_path} ubuntu@${aws_instance.langfuse.public_ip}"
}

output "langfuse_url" {
  description = "Langfuse UI URL"
  value       = "http://${aws_instance.langfuse.public_ip}:3000"
}

output "parameter_store_prefix" {
  description = "Parameter Store prefix for secrets"
  value       = "/langfuse/workshop"
}
```


### 3. Deployment Orchestration Scripts

#### deploy.sh - Main Deployment Script

```bash
#!/bin/bash
# infrastructure/scripts/deploy.sh
# Main deployment orchestration script

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Script phases:
# 1. Validate configuration files
# 2. Generate secrets
# 3. Run Terraform apply
# 4. Wait for EC2 instance ready
# 5. Install Docker on EC2
# 6. Deploy Docker Compose stack
# 7. Wait for Langfuse health check
# 8. Output access information

main() {
    echo "=== Langfuse AWS Deployment ==="
    
    # Phase 1: Validation
    validate_prerequisites
    validate_configuration
    
    # Phase 2: Secret generation
    generate_secrets
    
    # Phase 3: Terraform
    terraform_apply
    
    # Phase 4: Wait for EC2
    wait_for_instance
    
    # Phase 5: Install Docker
    install_docker
    
    # Phase 6: Deploy stack
    deploy_docker_compose
    
    # Phase 7: Health check
    wait_for_langfuse
    
    # Phase 8: Output
    output_access_info
    
    echo "=== Deployment Complete ==="
}

validate_prerequisites() {
    # Check required tools: aws, terraform, ssh, jq, yq
    # Check AWS credentials are configured
    # Check SSH key exists
}

validate_configuration() {
    # Validate aws-config.yaml
    # Validate langfuse-config.yaml
    # Check AWS profile is valid
    # Check region is valid
}

generate_secrets() {
    # Generate NEXTAUTH_SECRET (32 bytes, base64)
    # Generate SALT (32 bytes, base64)
    # Generate ENCRYPTION_KEY (32 bytes, hex)
    # Generate PostgreSQL password (32 chars)
    # Generate ClickHouse password (32 chars)
    # Generate MinIO password (32 chars)
    # Generate admin password (32 chars)
    # Generate API secret key (32 bytes, base64)
    # Store all in Parameter Store
}

terraform_apply() {
    # cd infrastructure/terraform
    # terraform init
    # terraform plan -out=tfplan
    # terraform apply tfplan
    # Extract outputs to variables
}

wait_for_instance() {
    # Poll EC2 instance status until running
    # Wait for SSH port to be open
    # Test SSH connection
    # Timeout after 5 minutes
}

install_docker() {
    # SSH to instance
    # Update package lists
    # Install Docker and Docker Compose plugin
    # Add ubuntu user to docker group
    # Start Docker service
    # Verify Docker is running
}

deploy_docker_compose() {
    # Create /opt/langfuse directory structure
    # Copy docker-compose.yml to instance
    # Generate .env file from Parameter Store secrets
    # Copy .env to instance
    # Run docker compose up -d
    # Verify all containers started
}

wait_for_langfuse() {
    # Poll http://INSTANCE_IP:3000/api/health
    # Retry every 10 seconds
    # Timeout after 5 minutes
}

output_access_info() {
    # Print Langfuse URL
    # Print admin email and password
    # Print API keys
    # Print SSH command
    # Print CloudWatch dashboard URL
}
```

#### destroy.sh - Cleanup Script

```bash
#!/bin/bash
# infrastructure/scripts/destroy.sh
# Destroys all AWS resources

set -euo pipefail

main() {
    echo "=== Langfuse AWS Destroy ==="
    echo "WARNING: This will delete all AWS resources and data!"
    read -p "Are you sure? (type 'yes' to confirm): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo "Aborted."
        exit 0
    fi
    
    # Backup data before destroying
    backup_data
    
    # Terraform destroy
    terraform_destroy
    
    # Delete Parameter Store secrets
    delete_secrets
    
    echo "=== Destroy Complete ==="
}

backup_data() {
    # SSH to instance
    # Run docker compose exec postgres pg_dump
    # Download backup to local machine
    # Timestamp backup file
}

terraform_destroy() {
    # cd infrastructure/terraform
    # terraform destroy -auto-approve
}

delete_secrets() {
    # List all parameters under /langfuse/workshop/
    # Delete each parameter
}
```

#### ssh-connect.sh - SSH Helper Script

```bash
#!/bin/bash
# infrastructure/scripts/ssh-connect.sh
# Connects to EC2 instance via SSH

set -euo pipefail

# Get instance IP from Terraform output
INSTANCE_IP=$(cd infrastructure/terraform && terraform output -raw instance_public_ip)
SSH_KEY=$(cd infrastructure/terraform && terraform output -raw ssh_key_path)

ssh -i "$SSH_KEY" ubuntu@"$INSTANCE_IP"
```

#### backup.sh - Database Backup Script

```bash
#!/bin/bash
# infrastructure/scripts/backup.sh
# Creates backup of PostgreSQL database

set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
BACKUP_FILE="$BACKUP_DIR/langfuse_backup_$TIMESTAMP.sql.gz"

mkdir -p "$BACKUP_DIR"

# Get instance IP
INSTANCE_IP=$(cd infrastructure/terraform && terraform output -raw instance_public_ip)
SSH_KEY=$(cd infrastructure/terraform && terraform output -raw ssh_key_path)

# Create backup on instance and download
ssh -i "$SSH_KEY" ubuntu@"$INSTANCE_IP" \
    "docker compose -f /opt/langfuse/docker-compose.yml exec -T postgres \
     pg_dump -U langfuse langfuse | gzip" > "$BACKUP_FILE"

echo "Backup saved to: $BACKUP_FILE"
```

### 4. Docker Compose Configuration

The existing `infrastructure/docker/docker-compose.yml` will be used with minimal modifications. The deployment script will generate a `.env` file with secrets from Parameter Store.

#### Generated .env File Structure

```bash
# Langfuse version
LANGFUSE_VERSION=3

# Langfuse ports
LANGFUSE_PORT=3000

# Database configuration
POSTGRES_USER=langfuse
POSTGRES_PASSWORD=<from-parameter-store>
POSTGRES_DB=langfuse

# Langfuse secrets
NEXTAUTH_SECRET=<from-parameter-store>
SALT=<from-parameter-store>
ENCRYPTION_KEY=<from-parameter-store>

# Langfuse initialization
LANGFUSE_INIT_ORG_ID=workshop-org
LANGFUSE_INIT_ORG_NAME=LLM Workshop
LANGFUSE_INIT_PROJECT_ID=techshop-agent
LANGFUSE_INIT_PROJECT_NAME=TechShop Agent
LANGFUSE_INIT_PROJECT_PUBLIC_KEY=lf_pk_workshop_shared
LANGFUSE_INIT_PROJECT_SECRET_KEY=<from-parameter-store>
LANGFUSE_INIT_USER_EMAIL=admin@workshop.local
LANGFUSE_INIT_USER_NAME=Workshop Admin
LANGFUSE_INIT_USER_PASSWORD=<from-parameter-store>

# ClickHouse configuration
CLICKHOUSE_USER=langfuse
CLICKHOUSE_PASSWORD=<from-parameter-store>

# MinIO configuration
MINIO_ROOT_USER=langfuse
MINIO_ROOT_PASSWORD=<from-parameter-store>

# Redis configuration (no password for simplicity)
REDIS_PASSWORD=

# Langfuse configuration
LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES=true
LANGFUSE_SESSION_MAX_AGE=28800  # 8 hours in seconds
```

### 5. CloudWatch Monitoring

#### CloudWatch Agent Configuration

The EC2 instance will run the CloudWatch Agent to collect system metrics and Docker logs.

```json
{
  "metrics": {
    "namespace": "LangfuseWorkshop",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          {"name": "cpu_usage_idle", "rename": "CPU_IDLE", "unit": "Percent"},
          {"name": "cpu_usage_iowait", "rename": "CPU_IOWAIT", "unit": "Percent"}
        ],
        "metrics_collection_interval": 60,
        "totalcpu": false
      },
      "disk": {
        "measurement": [
          {"name": "used_percent", "rename": "DISK_USED", "unit": "Percent"}
        ],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      },
      "mem": {
        "measurement": [
          {"name": "mem_used_percent", "rename": "MEM_USED", "unit": "Percent"}
        ],
        "metrics_collection_interval": 60
      }
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/lib/docker/containers/*/*.log",
            "log_group_name": "/langfuse/workshop/docker",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
```

#### CloudWatch Dashboard

The Terraform module creates a dashboard with:
- CPU utilization graph (last 3 hours)
- Memory utilization graph (last 3 hours)
- Disk utilization graph (last 3 hours)
- Network in/out graph (last 3 hours)
- Docker container status (running/stopped count)
- Recent log entries from Langfuse containers


## Data Models

### Configuration Data Models

#### AWSConfig

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AWSCredentials:
    profile: str
    region: str
    account_id: Optional[str] = None

@dataclass
class ProjectConfig:
    name: str
    environment: str
    owner: str

@dataclass
class InstanceConfig:
    type: str = "t3.xlarge"
    volume_size: int = 100
    ami: str = "ubuntu-24.04"

@dataclass
class SecurityConfig:
    ssh_allowed_cidrs: List[str]
    langfuse_allowed_cidrs: List[str]
    enable_https: bool = False
    certificate_email: Optional[str] = None

@dataclass
class MonitoringConfig:
    enable_cloudwatch: bool = True
    log_retention_days: int = 7
    alert_email: str

@dataclass
class AWSConfig:
    aws: AWSCredentials
    project: ProjectConfig
    instance: InstanceConfig
    security: SecurityConfig
    monitoring: MonitoringConfig
    tags: dict[str, str]
```

#### LangfuseConfig

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class LangfuseInit:
    org_id: str
    org_name: str
    project_id: str
    project_name: str
    admin_email: str
    admin_name: str
    admin_password: Optional[str] = None

@dataclass
class APIKeys:
    public_key: str
    secret_key: Optional[str] = None

@dataclass
class ResourceLimits:
    memory: str
    cpu: str

@dataclass
class LangfuseResources:
    web: ResourceLimits
    worker: ResourceLimits
    postgres: ResourceLimits
    clickhouse: ResourceLimits
    redis: ResourceLimits
    minio: ResourceLimits

@dataclass
class LangfuseSecurity:
    session_timeout_minutes: int = 480
    allow_signup: bool = False

@dataclass
class DataRetention:
    traces_days: int = 30

@dataclass
class LangfuseConfig:
    version: str
    init: LangfuseInit
    api_keys: APIKeys
    resources: LangfuseResources
    security: LangfuseSecurity
    retention: DataRetention
```

### Terraform State Data Model

Terraform maintains state in `terraform.tfstate` (JSON format). Key resources tracked:

```json
{
  "version": 4,
  "terraform_version": "1.5.0",
  "resources": [
    {
      "type": "aws_vpc",
      "name": "langfuse",
      "instances": [{"attributes": {"id": "vpc-xxx", "cidr_block": "10.0.0.0/16"}}]
    },
    {
      "type": "aws_subnet",
      "name": "public",
      "instances": [{"attributes": {"id": "subnet-xxx", "cidr_block": "10.0.1.0/24"}}]
    },
    {
      "type": "aws_instance",
      "name": "langfuse",
      "instances": [{"attributes": {
        "id": "i-xxx",
        "public_ip": "203.0.113.10",
        "public_dns": "ec2-xxx.compute.amazonaws.com"
      }}]
    },
    {
      "type": "aws_security_group",
      "name": "langfuse",
      "instances": [{"attributes": {"id": "sg-xxx"}}]
    }
  ]
}
```

### Parameter Store Data Model

Secrets stored in AWS Systems Manager Parameter Store:

```
/langfuse/workshop/nextauth-secret
  Type: SecureString
  Value: <base64-encoded-32-bytes>
  KMS: aws/ssm (default key)

/langfuse/workshop/salt
  Type: SecureString
  Value: <base64-encoded-32-bytes>

/langfuse/workshop/encryption-key
  Type: SecureString
  Value: <hex-encoded-32-bytes>

/langfuse/workshop/postgres-password
  Type: SecureString
  Value: <random-32-chars>

/langfuse/workshop/clickhouse-password
  Type: SecureString
  Value: <random-32-chars>

/langfuse/workshop/minio-password
  Type: SecureString
  Value: <random-32-chars>

/langfuse/workshop/admin-password
  Type: SecureString
  Value: <random-32-chars>

/langfuse/workshop/api-secret-key
  Type: SecureString
  Value: <base64-encoded-32-bytes>
```

### Deployment State Tracking

The deployment script maintains a state file to track deployment progress:

```json
{
  "deployment_id": "20260115-143022",
  "status": "completed",
  "phases": {
    "validation": {"status": "completed", "timestamp": "2026-01-15T14:30:25Z"},
    "secrets": {"status": "completed", "timestamp": "2026-01-15T14:30:30Z"},
    "terraform": {"status": "completed", "timestamp": "2026-01-15T14:35:45Z"},
    "docker": {"status": "completed", "timestamp": "2026-01-15T14:40:12Z"},
    "health_check": {"status": "completed", "timestamp": "2026-01-15T14:42:30Z"}
  },
  "outputs": {
    "instance_id": "i-0123456789abcdef0",
    "instance_ip": "203.0.113.10",
    "langfuse_url": "http://203.0.113.10:3000",
    "admin_email": "admin@workshop.local"
  }
}
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Configuration Parameter Parsing

*For any* valid configuration file (aws-config.yaml or langfuse-config.yaml), all parameters defined in the file should be correctly parsed and accessible to the deployment system, with values matching their specified types (string, integer, boolean, list).

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 2: Infrastructure Resource Matching

*For any* configured instance type and volume size, the provisioned EC2 instance should have exactly the specified instance type and the attached EBS volume should have exactly the specified size and type (gp3).

**Validates: Requirements 1.1, 1.2**

### Property 3: Secret Generation Quality

*For any* generated secret (NEXTAUTH_SECRET, SALT, ENCRYPTION_KEY, passwords), the secret should be at least 32 characters long, contain sufficient entropy (minimum 128 bits), and be properly formatted for its intended use (base64, hex, or alphanumeric).

**Validates: Requirements 3.3, 9.5, 9.6**

### Property 4: Security Group Rule Matching

*For any* configured IP CIDR block and port combination in the security configuration, the provisioned security group should have a matching ingress rule allowing traffic from that CIDR to that port.

**Validates: Requirements 9.1, 9.7, 9.8**

### Property 5: Parameter Store Encryption

*For any* secret stored in AWS Systems Manager Parameter Store under the /langfuse/workshop/ prefix, the parameter should be of type SecureString and encrypted with a KMS key.

**Validates: Requirements 9.11**

### Property 6: Resource Tagging Completeness

*For any* AWS resource created by the Terraform module (VPC, subnet, EC2 instance, security group, EBS volume), the resource should have all tags specified in the configuration file's tags section.

**Validates: Requirements 8.3**

### Property 7: Deployment Idempotency

*For any* deployment script execution run multiple times with the same configuration, the second and subsequent runs should update existing resources rather than create duplicates, and the final resource count should equal the count after the first run.

**Validates: Requirements 10.1, 10.2, 10.3**

### Property 8: Configuration Validation Error Messages

*For any* invalid or missing configuration parameter, the validation phase should fail with an error message that clearly identifies which parameter is invalid or missing and what the expected format or value should be.

**Validates: Requirements 2.6, 4.8**

### Property 9: Documentation Completeness

*For any* configuration parameter defined in the code (aws-config.yaml schema, langfuse-config.yaml schema, terraform variables), there should be corresponding documentation in the deployment guide or README that explains the parameter's purpose and valid values.

**Validates: Requirements 7.2**

### Property 10: Conditional HTTPS Configuration

*For any* deployment where enable_https is set to true in the configuration, the security group should include an ingress rule for port 443, and the deployment should configure TLS certificates.

**Validates: Requirements 9.8, 9.10**

### Property 11: API Request Logging with User Context

*For any* API request made to the Langfuse service, the request should be logged with the user_id field populated, enabling per-student activity tracking.

**Validates: Requirements 11.3**


## Error Handling

### Configuration Validation Errors

**Error Type**: Invalid or missing configuration parameters

**Handling Strategy**:
- Validate all configuration files before any AWS operations
- Provide specific error messages indicating which parameter is invalid
- Include expected format and example values in error messages
- Exit with non-zero status code to prevent partial deployments

**Example Error Messages**:
```
ERROR: Invalid AWS region 'us-east-99' in aws-config.yaml
Expected: Valid AWS region (e.g., us-east-1, eu-west-1)

ERROR: Missing required parameter 'project.name' in aws-config.yaml
This parameter is required for resource naming and tagging.

ERROR: Invalid CIDR block '192.168.1.0/99' in security.ssh_allowed_cidrs
Expected: Valid CIDR notation (e.g., 192.168.1.0/24)
```

### AWS API Errors

**Error Type**: AWS service errors (insufficient permissions, quota limits, resource conflicts)

**Handling Strategy**:
- Catch AWS API exceptions and translate to user-friendly messages
- Include AWS error code and request ID for troubleshooting
- Suggest remediation steps based on error type
- For quota errors, provide link to AWS Service Quotas console

**Example Error Messages**:
```
ERROR: Failed to create EC2 instance
AWS Error: InsufficientInstanceCapacity
Suggestion: Try a different availability zone or instance type

ERROR: Failed to create VPC
AWS Error: VpcLimitExceeded
Suggestion: Delete unused VPCs or request a quota increase at:
https://console.aws.amazon.com/servicequotas/

ERROR: Access denied when creating security group
AWS Error: UnauthorizedOperation
Suggestion: Ensure your AWS credentials have ec2:CreateSecurityGroup permission
```

### SSH Connection Errors

**Error Type**: Unable to connect to EC2 instance

**Handling Strategy**:
- Retry SSH connection with exponential backoff (max 5 minutes)
- Check security group rules allow SSH from current IP
- Verify instance is in "running" state
- Provide troubleshooting steps if connection fails

**Example Error Messages**:
```
ERROR: SSH connection timeout after 5 minutes
Instance ID: i-0123456789abcdef0
Instance State: running
Public IP: 203.0.113.10

Troubleshooting steps:
1. Verify security group allows SSH (port 22) from your IP
2. Check instance system log for boot errors:
   aws ec2 get-console-output --instance-id i-0123456789abcdef0
3. Verify SSH key permissions: chmod 600 ~/.ssh/langfuse-workshop.pem
```

### Docker Deployment Errors

**Error Type**: Docker Compose stack fails to start

**Handling Strategy**:
- Capture docker compose logs for failed containers
- Check for common issues (port conflicts, insufficient memory, missing secrets)
- Provide container-specific troubleshooting steps
- Offer rollback option to previous working state

**Example Error Messages**:
```
ERROR: Docker container 'langfuse-web' failed to start
Container logs:
  Error: NEXTAUTH_SECRET environment variable is not set

Suggestion: Verify secrets were correctly stored in Parameter Store:
aws ssm get-parameter --name /langfuse/workshop/nextauth-secret --with-decryption

ERROR: Docker container 'postgres' exited with code 1
Container logs:
  FATAL: data directory "/var/lib/postgresql/data" has wrong ownership

Suggestion: Reset data directory permissions:
ssh ubuntu@203.0.113.10 'sudo chown -R 999:999 /opt/langfuse/data/postgres'
```

### Terraform State Errors

**Error Type**: Terraform state conflicts or corruption

**Handling Strategy**:
- Detect state lock conflicts and suggest resolution
- Backup state file before any destructive operations
- Provide state recovery commands for common issues
- Warn about manual resource changes outside Terraform

**Example Error Messages**:
```
ERROR: Terraform state is locked
Lock ID: 12345678-1234-1234-1234-123456789012
Lock acquired: 2026-01-15 14:30:00 UTC

Suggestion: If no other deployment is running, force unlock:
cd infrastructure/terraform && terraform force-unlock 12345678-1234-1234-1234-123456789012

ERROR: Terraform detected manual changes to EC2 instance
Resource: aws_instance.langfuse
Drift: instance_type changed from t3.xlarge to t3.large

Suggestion: Import current state or revert manual changes:
terraform apply -refresh-only
```

### Health Check Failures

**Error Type**: Langfuse service not responding after deployment

**Handling Strategy**:
- Poll health endpoint with timeout (5 minutes)
- Check Docker container status and logs
- Verify all dependent services (postgres, clickhouse) are healthy
- Provide diagnostic commands for troubleshooting

**Example Error Messages**:
```
ERROR: Langfuse health check failed after 5 minutes
URL: http://203.0.113.10:3000/api/health
Status: Connection refused

Diagnostic steps:
1. Check container status:
   ssh ubuntu@203.0.113.10 'docker compose -f /opt/langfuse/docker-compose.yml ps'

2. Check langfuse-web logs:
   ssh ubuntu@203.0.113.10 'docker compose -f /opt/langfuse/docker-compose.yml logs langfuse-web'

3. Check database connectivity:
   ssh ubuntu@203.0.113.10 'docker compose -f /opt/langfuse/docker-compose.yml exec postgres pg_isready'
```

### Cleanup Errors

**Error Type**: Resources fail to delete during destroy operation

**Handling Strategy**:
- Continue attempting to delete remaining resources even if some fail
- Report which resources were successfully deleted and which failed
- Provide manual cleanup commands for stuck resources
- Warn about potential ongoing charges

**Example Error Messages**:
```
WARNING: Failed to delete security group sg-0123456789abcdef0
AWS Error: DependencyViolation
Reason: Security group is still attached to network interface

Manual cleanup:
1. Find dependent resources:
   aws ec2 describe-network-interfaces --filters Name=group-id,Values=sg-0123456789abcdef0

2. Delete network interfaces:
   aws ec2 delete-network-interface --network-interface-id eni-xxxxx

3. Retry security group deletion:
   aws ec2 delete-security-group --group-id sg-0123456789abcdef0

WARNING: Some resources may still incur charges. Verify all resources are deleted:
aws ec2 describe-instances --filters Name=tag:Project,Values=LLMOps-Workshop
```


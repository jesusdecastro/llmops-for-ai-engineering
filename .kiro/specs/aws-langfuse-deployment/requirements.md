# Requirements Document: AWS Langfuse Deployment

## Introduction

This document specifies the requirements for deploying Langfuse v3 on AWS infrastructure using Docker Compose on a single EC2 instance. The deployment is designed for a 3-day workshop with approximately 20 students who will send traces via OpenTelemetry and use the Langfuse UI. The solution must be fully parametrized to support configuration once AWS account details are available.

## Glossary

- **Deployment_System**: The complete infrastructure-as-code and deployment automation system
- **IaC_Module**: Infrastructure-as-Code scripts (Terraform) that provision AWS resources
- **Configuration_Layer**: The parametrized configuration system for AWS credentials and deployment parameters
- **Deployment_Script**: Automated scripts that orchestrate the deployment process
- **EC2_Instance**: The AWS EC2 t3.xlarge virtual machine hosting the Docker Compose stack
- **Docker_Stack**: The collection of Docker containers running Langfuse and its dependencies
- **Langfuse_Service**: The Langfuse v3 application (web and worker containers)
- **AWS_Profile**: Named AWS CLI credential profile for authentication

## Requirements

### Requirement 1: Infrastructure Provisioning

**User Story:** As a workshop instructor, I want to provision AWS infrastructure using Infrastructure-as-Code, so that I can create reproducible and version-controlled deployments.

#### Acceptance Criteria

1. THE IaC_Module SHALL provision an EC2 instance with configurable instance type (default: t3.xlarge with 4 vCPU and 16 GiB RAM)
2. THE IaC_Module SHALL attach a configurable EBS volume (default: 100 GiB gp3) to the EC2_Instance
3. THE IaC_Module SHALL create a VPC with public subnet and internet gateway
4. THE IaC_Module SHALL configure a security group allowing inbound traffic on ports 22 (SSH), 3000 (Langfuse UI), and 443 (HTTPS)
5. THE IaC_Module SHALL use Amazon Linux 2023 or Ubuntu 24.04 LTS as the operating system
6. THE IaC_Module SHALL output the public IP address and DNS name of the EC2_Instance

### Requirement 2: Configuration Management

**User Story:** As a workshop instructor, I want a parametrized configuration system, so that I can deploy the infrastructure once my AWS account is set up without modifying code.

#### Acceptance Criteria

1. THE Configuration_Layer SHALL support AWS profile-based authentication
2. THE Configuration_Layer SHALL accept AWS region as a configurable parameter
3. THE Configuration_Layer SHALL accept AWS account ID as a configurable parameter
4. THE Configuration_Layer SHALL support environment-specific tags (project name, environment, owner)
5. THE Configuration_Layer SHALL provide example configuration files with placeholder values
6. WHEN configuration files are missing, THEN THE Deployment_System SHALL provide clear error messages indicating which parameters are required

### Requirement 3: Docker Compose Deployment

**User Story:** As a workshop instructor, I want to deploy Langfuse using the existing Docker Compose configuration, so that all required services are orchestrated correctly.

#### Acceptance Criteria

1. THE Deployment_Script SHALL install Docker and Docker Compose on the EC2_Instance
2. THE Deployment_Script SHALL copy the docker-compose.yml file from infrastructure/docker/ to the EC2_Instance
3. THE Deployment_Script SHALL generate secure random values for NEXTAUTH_SECRET, SALT, and ENCRYPTION_KEY
4. THE Deployment_Script SHALL configure environment variables required by the Docker_Stack
5. WHEN the Docker_Stack is started, THEN THE Langfuse_Service SHALL be accessible on port 3000 within 5 minutes
6. THE Docker_Stack SHALL include PostgreSQL, ClickHouse, Redis, MinIO, langfuse-web, and langfuse-worker containers

### Requirement 4: Automated Deployment Orchestration

**User Story:** As a workshop instructor, I want a single command to deploy the complete infrastructure, so that I can set up the environment quickly and reliably.

#### Acceptance Criteria

1. THE Deployment_Script SHALL validate configuration files before starting deployment
2. THE Deployment_Script SHALL execute Terraform to provision AWS infrastructure
3. THE Deployment_Script SHALL wait for the EC2_Instance to be running and accessible via SSH
4. THE Deployment_Script SHALL install and configure Docker on the EC2_Instance
5. THE Deployment_Script SHALL deploy the Docker_Stack on the EC2_Instance
6. THE Deployment_Script SHALL verify that the Langfuse_Service is responding to HTTP requests
7. WHEN deployment completes successfully, THEN THE Deployment_Script SHALL output the Langfuse UI URL and access credentials
8. IF any deployment step fails, THEN THE Deployment_Script SHALL provide clear error messages and stop execution

### Requirement 5: Langfuse Initialization

**User Story:** As a workshop instructor, I want Langfuse to be pre-configured with users and projects, so that students can start using it immediately without manual setup.

#### Acceptance Criteria

1. THE Deployment_Script SHALL configure Langfuse with headless initialization environment variables
2. THE Langfuse_Service SHALL create a default organization on first startup
3. THE Langfuse_Service SHALL create a default project named "techshop-agent" on first startup
4. THE Langfuse_Service SHALL create an admin user with configurable credentials
5. THE Langfuse_Service SHALL generate a shared API key pair for student access
6. THE Deployment_Script SHALL output the admin credentials and API keys after deployment

### Requirement 6: Infrastructure Management Scripts

**User Story:** As a workshop instructor, I want management scripts for common operations, so that I can easily connect to the instance, view logs, and clean up resources.

#### Acceptance Criteria

1. THE Deployment_System SHALL provide a script to SSH into the EC2_Instance
2. THE Deployment_System SHALL provide a script to destroy all AWS resources
3. THE Deployment_System SHALL provide a script to backup PostgreSQL data
4. WHEN the SSH script is executed, THEN THE Deployment_System SHALL connect to the EC2_Instance using the correct key pair
5. WHEN the destroy script is executed, THEN THE Deployment_System SHALL prompt for confirmation before deleting resources
6. WHEN the backup script is executed, THEN THE Deployment_System SHALL create a timestamped backup of the PostgreSQL database

### Requirement 7: Documentation

**User Story:** As a workshop instructor, I want comprehensive documentation, so that I can understand the deployment process and troubleshoot issues.

#### Acceptance Criteria

1. THE Deployment_System SHALL include a deployment guide with step-by-step instructions
2. THE Deployment_System SHALL document all configuration parameters and their purposes
3. THE Deployment_System SHALL document the architecture and component relationships
4. THE Deployment_System SHALL include troubleshooting guidance for common issues
5. THE Deployment_System SHALL document estimated costs for the 3-day workshop period
6. THE Deployment_System SHALL document security group rules and access controls

### Requirement 8: Cost Optimization

**User Story:** As a workshop instructor, I want the deployment to be cost-effective, so that I can run the workshop within a reasonable budget.

#### Acceptance Criteria

1. THE IaC_Module SHALL use on-demand EC2 pricing (not reserved instances)
2. THE IaC_Module SHALL use gp3 EBS volumes for cost efficiency
3. THE IaC_Module SHALL tag all resources with cost tracking tags
4. THE Deployment_System SHALL document the estimated total cost for 3 days of operation (approximately $13-15 for t3.xlarge)
5. THE Configuration_Layer SHALL allow instance type selection to balance cost and performance requirements
6. WHEN the workshop ends, THEN THE Deployment_System SHALL provide clear instructions for resource cleanup to stop charges

### Requirement 9: Security Configuration

**User Story:** As a workshop instructor, I want secure default configurations for remote access, so that the deployment protects against common threats while remaining accessible to inexperienced students.

#### Acceptance Criteria

1. THE IaC_Module SHALL restrict SSH access to instructor IP addresses only
2. THE IaC_Module SHALL generate unique SSH key pairs for EC2 access
3. THE IaC_Module SHALL enable EBS encryption at rest for the data volume
4. THE IaC_Module SHALL create an IAM role for the EC2_Instance with minimal required permissions
5. THE Deployment_Script SHALL generate cryptographically secure random secrets for Langfuse (minimum 32 characters)
6. THE Docker_Stack SHALL use strong passwords for PostgreSQL, ClickHouse, and MinIO (minimum 32 characters)
7. THE Security_Group SHALL allow Langfuse UI access (port 3000) from configurable IP ranges or CIDR blocks
8. THE Security_Group SHALL allow HTTPS access (port 443) when TLS is enabled
9. THE Security_Group SHALL allow all outbound traffic for Docker image pulls and updates
10. WHERE HTTPS is enabled, THE Deployment_System SHALL configure TLS certificates using Let's Encrypt or AWS Certificate Manager
11. THE Deployment_System SHALL store generated secrets in AWS Systems Manager Parameter Store with encryption
12. THE Deployment_System SHALL configure Langfuse session timeout to 8 hours maximum
13. THE Deployment_System SHALL disable new user registration in Langfuse (students use shared project with individual user_id tags)

### Requirement 10: Idempotent Deployment

**User Story:** As a workshop instructor, I want the deployment to be idempotent, so that I can re-run scripts safely if something fails.

#### Acceptance Criteria

1. WHEN the Deployment_Script is run multiple times, THEN THE IaC_Module SHALL update existing resources instead of creating duplicates
2. WHEN Docker containers are already running, THEN THE Deployment_Script SHALL restart them with updated configuration
3. WHEN configuration files already exist, THEN THE Deployment_Script SHALL not overwrite them without explicit confirmation
4. THE IaC_Module SHALL use Terraform state management to track resource changes

### Requirement 11: Monitoring and Access Logging

**User Story:** As a workshop instructor, I want to monitor system health and user activity, so that I can troubleshoot issues and ensure students are successfully using the platform.

#### Acceptance Criteria

1. THE Deployment_System SHALL configure CloudWatch monitoring for EC2 CPU, memory, disk, and network metrics
2. THE Deployment_System SHALL enable Docker container logging to CloudWatch Logs
3. THE Langfuse_Service SHALL log all API requests with user_id for student activity tracking
4. THE Deployment_System SHALL create a CloudWatch dashboard showing key metrics (CPU, memory, active users, trace count)
5. WHEN CPU usage exceeds 80% for 5 minutes, THEN THE Deployment_System SHALL send an alert notification
6. WHEN disk usage exceeds 85%, THEN THE Deployment_System SHALL send an alert notification
7. THE Deployment_System SHALL configure alert notifications via email or SNS topic

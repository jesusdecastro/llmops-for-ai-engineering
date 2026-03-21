# Implementation Plan: AWS Langfuse Deployment

## Overview

This implementation plan breaks down the AWS Langfuse deployment system into discrete coding tasks. The system uses Terraform for infrastructure provisioning, Bash scripts for deployment orchestration, Python for configuration validation, and YAML for configuration management. Each task builds incrementally toward a complete, production-ready deployment system.

## Tasks

- [x] 1. Set up project structure and configuration schemas
  - Create directory structure: infrastructure/{config,terraform,scripts,docker}
  - Create example configuration files: aws-config.yaml.example and langfuse-config.yaml.example
  - Define YAML schemas with all required and optional parameters
  - _Requirements: 2.5_

- [x] 2. Implement configuration validation module
  - [x] 2.1 Create Python configuration validator
    - Implement ConfigValidator class with methods for validating AWS and Langfuse configs
    - Validate AWS profile existence, region validity, instance types, CIDR blocks, email formats
    - Validate Langfuse version, resource limits, session timeouts
    - Return detailed ValidationResult objects with error lists
    - _Requirements: 2.6, 4.1, 4.8_

  - [ ]* 2.2 Write property test for configuration validation
    - **Property 1: Configuration Parameter Parsing**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

  - [ ]* 2.3 Write property test for validation error messages
    - **Property 8: Configuration Validation Error Messages**
    - **Validates: Requirements 2.6, 4.8**

- [x] 3. Implement secret generation utilities
  - [x] 3.1 Create secret generation functions
    - Implement functions to generate NEXTAUTH_SECRET (32 bytes base64)
    - Implement functions to generate SALT (32 bytes base64)
    - Implement functions to generate ENCRYPTION_KEY (32 bytes hex)
    - Implement functions to generate secure passwords (32 chars alphanumeric)
    - Use cryptographically secure random sources (os.urandom or secrets module)
    - _Requirements: 3.3, 9.5, 9.6_
  
  - [ ]* 3.2 Write property test for secret generation quality
    - **Property 3: Secret Generation Quality**
    - **Validates: Requirements 3.3, 9.5, 9.6**

- [x] 4. Create Terraform VPC and networking module
  - [x] 4.1 Implement VPC infrastructure
    - Create vpc.tf with VPC resource (CIDR 10.0.0.0/16)
    - Create public subnet (CIDR 10.0.1.0/24)
    - Create internet gateway
    - Create route table with default route to IGW
    - Create route table association
    - Add appropriate tags from configuration
    - _Requirements: 1.3_
  
  - [x] 4.2 Define Terraform variables
    - Create variables.tf with all configurable parameters
    - Define variable types, descriptions, and default values
    - Include variables for region, instance type, volume size, CIDRs, tags
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 4.3 Create Terraform outputs
    - Create outputs.tf with instance IP, DNS, security group ID, SSH command, Langfuse URL
    - _Requirements: 1.6, 4.7_

- [x] 5. Create Terraform security group module
  - [x] 5.1 Implement security group with ingress/egress rules
    - Create security-groups.tf with security group resource
    - Add ingress rule for SSH (port 22) from instructor CIDRs
    - Add ingress rule for HTTP (port 3000) from student CIDRs
    - Add conditional ingress rule for HTTPS (port 443) when enabled
    - Add egress rule for all traffic to 0.0.0.0/0
    - _Requirements: 1.4, 9.1, 9.7, 9.8, 9.9_
  
  - [ ]* 5.2 Write property test for security group rule matching
    - **Property 4: Security Group Rule Matching**
    - **Validates: Requirements 9.1, 9.7, 9.8**
  
  - [ ]* 5.3 Write property test for conditional HTTPS configuration
    - **Property 10: Conditional HTTPS Configuration**
    - **Validates: Requirements 9.8, 9.10**

- [x] 6. Create Terraform EC2 instance module
  - [x] 6.1 Implement EC2 instance with IAM role
    - Create ec2.tf with EC2 instance resource
    - Configure instance type, AMI (Ubuntu 24.04 LTS latest), key pair
    - Create and attach EBS volume with encryption enabled
    - Create IAM role with trust policy for EC2
    - Attach CloudWatchAgentServerPolicy managed policy
    - Create inline policy for SSM Parameter Store read access
    - Create inline policy for CloudWatch Logs write access
    - Create IAM instance profile and attach to EC2
    - Add user data script for initial CloudWatch Agent installation
    - _Requirements: 1.1, 1.2, 1.5, 9.3, 9.4_
  
  - [ ]* 6.2 Write property test for infrastructure resource matching
    - **Property 2: Infrastructure Resource Matching**
    - **Validates: Requirements 1.1, 1.2**
  
  - [ ]* 6.3 Write property test for resource tagging completeness
    - **Property 6: Resource Tagging Completeness**
    - **Validates: Requirements 8.3**

- [x] 7. Create Terraform Parameter Store module
  - [x] 7.1 Implement Parameter Store resources for secrets
    - Create ssm.tf with parameter resources for all secrets
    - Create parameters: nextauth-secret, salt, encryption-key, postgres-password, clickhouse-password, minio-password, admin-password, api-secret-key
    - Configure all parameters as SecureString type with KMS encryption
    - Use placeholder values (will be updated by deployment script)
    - _Requirements: 9.11_
  
  - [ ]* 7.2 Write property test for Parameter Store encryption
    - **Property 5: Parameter Store Encryption**
    - **Validates: Requirements 9.11**

- [x] 8. Create Terraform CloudWatch monitoring module
  - [x] 8.1 Implement CloudWatch dashboard and alarms
    - Create cloudwatch.tf with dashboard resource
    - Add widgets for CPU, memory, disk, network metrics
    - Create alarm for CPU utilization > 80% for 5 minutes
    - Create alarm for disk utilization > 85%
    - Create SNS topic for alarm notifications
    - Create SNS email subscription
    - _Requirements: 11.1, 11.4, 11.5, 11.6, 11.7_

- [ ] 9. Checkpoint - Validate Terraform configuration
  - Run terraform validate to check syntax
  - Run terraform plan with example variables to verify resource creation
  - Ensure all tests pass, ask the user if questions arise

- [x] 10. Implement deployment orchestration script
  - [x] 10.1 Create main deployment script (deploy.sh)
    - Implement validate_prerequisites function (check aws, terraform, ssh, jq, yq)
    - Implement validate_configuration function (call Python validator)
    - Implement generate_secrets function (generate all secrets, store in Parameter Store)
    - Implement terraform_apply function (init, plan, apply, extract outputs)
    - Implement wait_for_instance function (poll EC2 status, test SSH with timeout)
    - Implement install_docker function (SSH commands to install Docker and Docker Compose)
    - Implement deploy_docker_compose function (create directories, copy files, generate .env, start stack)
    - Implement wait_for_langfuse function (poll health endpoint with timeout)
    - Implement output_access_info function (print URL, credentials, SSH command)
    - Add error handling with clear messages for each phase
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_
  
  - [ ]* 10.2 Write property test for deployment idempotency
    - **Property 7: Deployment Idempotency**
    - **Validates: Requirements 10.1, 10.2, 10.3**

- [x] 11. Implement infrastructure management scripts
  - [x] 11.1 Create SSH connection script (ssh-connect.sh)
    - Extract instance IP from Terraform output
    - Extract SSH key path from Terraform output
    - Execute SSH connection with correct parameters
    - _Requirements: 6.1, 6.4_
  
  - [x] 11.2 Create database backup script (backup.sh)
    - Generate timestamped backup filename
    - SSH to instance and run pg_dump via docker compose exec
    - Download and compress backup to local machine
    - _Requirements: 6.3, 6.6_
  
  - [x] 11.3 Create destroy script (destroy.sh)
    - Prompt for confirmation before deletion
    - Call backup script to save data
    - Run terraform destroy
    - Delete Parameter Store secrets
    - Provide verification commands for complete cleanup
    - _Requirements: 6.2, 6.5, 8.6_

- [x] 12. Create Docker Compose environment file generator
  - [x] 12.1 Implement .env file generation
    - Create function to fetch secrets from Parameter Store
    - Generate .env file with all required environment variables
    - Include Langfuse version, ports, database config, secrets, initialization params
    - Set LANGFUSE_SESSION_MAX_AGE to 28800 seconds (8 hours)
    - Set allow_signup to false
    - _Requirements: 3.3, 3.4, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 9.12, 9.13_

- [x] 13. Configure CloudWatch Agent on EC2
  - [x] 13.1 Create CloudWatch Agent configuration
    - Create JSON configuration file for metrics collection (CPU, disk, memory)
    - Configure log collection for Docker container logs
    - Add configuration to user data script for automatic installation
    - _Requirements: 11.1, 11.2_
  
  - [ ]* 13.2 Write property test for API request logging
    - **Property 11: API Request Logging with User Context**
    - **Validates: Requirements 11.3**

- [ ] 14. Create comprehensive documentation
  - [ ] 14.1 Write deployment guide (README.md)
    - Document prerequisites (AWS account, CLI tools)
    - Provide step-by-step deployment instructions
    - Document configuration parameters and their purposes
    - Include architecture diagram and component relationships
    - Document security group rules and access controls
    - Include troubleshooting guidance for common issues
    - Document estimated costs for 3-day workshop (~$13-15)
    - Provide cleanup instructions to stop charges
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 8.4_
  
  - [ ]* 14.2 Write property test for documentation completeness
    - **Property 9: Documentation Completeness**
    - **Validates: Requirements 7.2**

- [x] 15. Create example configuration files
  - [x] 15.1 Create aws-config.yaml.example
    - Include all parameters with placeholder values
    - Add inline comments explaining each parameter
    - Provide example values for common scenarios
    - _Requirements: 2.5_
  
  - [x] 15.2 Create langfuse-config.yaml.example
    - Include all parameters with placeholder values
    - Add inline comments explaining each parameter
    - Provide recommended resource limits
    - _Requirements: 2.5_
  
  - [x] 15.3 Create terraform.tfvars.example
    - Include all Terraform variables with example values
    - Add comments explaining each variable
    - _Requirements: 2.5_

- [ ] 16. Implement error handling and logging
  - [ ] 16.1 Add comprehensive error handling to all scripts
    - Add try-catch blocks for AWS API errors with user-friendly messages
    - Add retry logic with exponential backoff for SSH connections
    - Add timeout handling for health checks
    - Add validation for Terraform state conflicts
    - Add diagnostic commands in error messages
    - Log all operations to deployment.log file
    - _Requirements: 4.8_

- [ ] 17. Final integration and testing
  - [ ] 17.1 Create integration test script
    - Test complete deployment flow with test configuration
    - Verify all resources are created correctly
    - Verify Langfuse is accessible and functional
    - Test SSH connection script
    - Test backup script
    - Test destroy script
    - Verify all resources are cleaned up
  
  - [ ]* 17.2 Write unit tests for error handling scenarios
    - Test configuration validation with invalid inputs
    - Test AWS API error handling
    - Test SSH connection failures
    - Test Docker deployment failures
    - Test health check timeouts

- [ ] 18. Final checkpoint - Complete system validation
  - Run full deployment on test AWS account
  - Verify all 11 requirements are satisfied
  - Verify all 11 correctness properties hold
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples and edge cases
- The deployment system prioritizes security, idempotency, and ease of use
- All secrets are generated securely and stored encrypted in Parameter Store
- CloudWatch monitoring provides observability for troubleshooting
- Comprehensive error handling ensures clear feedback when issues occur

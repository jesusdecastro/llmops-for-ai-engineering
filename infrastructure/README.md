# Infraestructura AWS - Langfuse para Curso LLMOps

Este directorio contiene la infraestructura como código para desplegar Langfuse v3 en AWS EC2 con Docker Compose.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS Account (Curso)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  VPC (curso-llmops-vpc)                               │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Public Subnet (10.0.1.0/24)                    │  │  │
│  │  │  ┌───────────────────────────────────────────┐  │  │  │
│  │  │  │  EC2 t3.xlarge (langfuse-server)          │  │  │  │
│  │  │  │  ┌─────────────────────────────────────┐  │  │  │  │
│  │  │  │  │  Docker Compose Stack               │  │  │  │  │
│  │  │  │  │  ├─ langfuse-web (port 3000)        │  │  │  │  │
│  │  │  │  │  ├─ langfuse-worker                 │  │  │  │  │
│  │  │  │  │  ├─ postgres (port 5432)            │  │  │  │  │
│  │  │  │  │  ├─ clickhouse (port 8123, 9000)    │  │  │  │  │
│  │  │  │  │  ├─ redis (port 6379)               │  │  │  │  │
│  │  │  │  │  └─ minio (port 9000, 9001)         │  │  │  │  │
│  │  │  │  └─────────────────────────────────────┘  │  │  │  │
│  │  │  │  - 100 GiB gp3 EBS                        │  │  │  │
│  │  │  │  - Security Group: langfuse-sg            │  │  │  │
│  │  │  └───────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  Internet Gateway                                      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Componentes

### EC2 Instance
- **Tipo**: t3.xlarge (4 vCPU, 16 GiB RAM)
- **Storage**: 100 GiB gp3 EBS
- **OS**: Amazon Linux 2023
- **Coste estimado**: ~$13-15 por 3 días

### Langfuse Stack (Docker Compose)
- **langfuse-web**: UI y API (puerto 3000)
- **langfuse-worker**: Procesamiento asíncrono
- **postgres**: Base de datos principal
- **clickhouse**: Analytics y métricas
- **redis**: Cache y queue
- **minio**: Object storage (S3-compatible)

## Estructura de Archivos

```
infrastructure/
├── README.md                    # Este archivo
├── config/
│   ├── aws-config.yaml         # Configuración AWS parametrizada
│   └── langfuse-config.yaml    # Configuración Langfuse
├── terraform/                   # IaC con Terraform
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── vpc.tf
│   ├── ec2.tf
│   ├── security-groups.tf
│   └── terraform.tfvars.example
├── docker/
│   ├── docker-compose.yml      # Stack completo de Langfuse
│   ├── .env.example            # Variables de entorno
│   └── init-scripts/           # Scripts de inicialización
│       └── setup-langfuse.sh
├── scripts/
│   ├── deploy.sh               # Script de despliegue completo
│   ├── destroy.sh              # Script de limpieza
│   ├── ssh-connect.sh          # Conectar a la instancia
│   └── backup.sh               # Backup de datos
└── docs/
    ├── deployment-guide.md     # Guía de despliegue
    └── troubleshooting.md      # Solución de problemas
```

## Requisitos Previos

1. **AWS CLI** configurado con credenciales
2. **Terraform** >= 1.5.0
3. **SSH key pair** para acceso a EC2
4. **Permisos AWS** necesarios:
   - EC2 (crear instancias, security groups)
   - VPC (crear VPC, subnets, IGW)
   - IAM (crear roles y policies)

## Despliegue Rápido

### 1. Configurar AWS Profile

```bash
# Editar config/aws-config.yaml con tus valores
cp infrastructure/config/aws-config.yaml.example infrastructure/config/aws-config.yaml
```

### 2. Configurar Terraform

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
# Editar terraform.tfvars con tus valores
```

### 3. Desplegar

```bash
# Desde el directorio raíz del proyecto
./infrastructure/scripts/deploy.sh
```

El script:
1. Valida la configuración
2. Crea la infraestructura con Terraform
3. Instala Docker en la EC2
4. Despliega Langfuse con Docker Compose
5. Configura usuarios y API keys
6. Muestra la URL de acceso

### 4. Acceder a Langfuse

```bash
# La URL se mostrará al final del despliegue
http://<ec2-public-ip>:3000

# Credenciales por defecto (cambiar después):
# Email: admin@curso-llmops.local
# Password: (generado automáticamente, ver output)
```

## Configuración

### AWS Profile

Editar `config/aws-config.yaml`:

```yaml
aws:
  profile: curso-llmops          # AWS CLI profile
  region: us-east-1              # Región AWS
  account_id: "123456789012"     # ID de cuenta (opcional)

project:
  name: curso-llmops
  environment: training
  owner: instructor@example.com
  
tags:
  Project: LLMOps-Course
  Environment: Training
  ManagedBy: Terraform
  CostCenter: Training
```

### Langfuse Configuration

Editar `config/langfuse-config.yaml`:

```yaml
langfuse:
  version: "3.0"
  
  # Usuarios pre-creados para el curso
  users:
    - email: admin@curso-llmops.local
      role: admin
    - email: instructor@curso-llmops.local
      role: admin
  
  # Proyectos pre-creados
  projects:
    - name: techshop-agent
      description: "Proyecto del curso - Agente TechShop"
      
  # Configuración de recursos
  resources:
    web:
      replicas: 1
      memory: 2Gi
      cpu: 1
    worker:
      replicas: 1
      memory: 2Gi
      cpu: 1
```

## Gestión

### Conectar a la Instancia

```bash
./infrastructure/scripts/ssh-connect.sh
```

### Ver Logs

```bash
# Conectar a la instancia
./infrastructure/scripts/ssh-connect.sh

# Ver logs de todos los servicios
docker compose -f /opt/langfuse/docker-compose.yml logs -f

# Ver logs de un servicio específico
docker compose -f /opt/langfuse/docker-compose.yml logs -f langfuse-web
```

### Backup

```bash
# Crear backup de la base de datos
./infrastructure/scripts/backup.sh
```

### Destruir Infraestructura

```bash
# CUIDADO: Esto eliminará toda la infraestructura
./infrastructure/scripts/destroy.sh
```

## Costes Estimados

| Recurso | Especificación | Coste (3 días) |
|---------|----------------|----------------|
| EC2 t3.xlarge | 4 vCPU, 16 GiB | ~$10-12 |
| EBS gp3 100 GiB | Storage | ~$1-2 |
| Data Transfer | Minimal | ~$1 |
| **Total** | | **~$13-15** |

## Seguridad

### Security Group Rules

- **Inbound**:
  - SSH (22): Solo desde IPs del instructor
  - HTTP (3000): Desde IPs de la red del curso
  - HTTPS (443): Desde IPs de la red del curso (si se configura SSL)

- **Outbound**:
  - All traffic (para actualizaciones y Docker pulls)

### Credenciales

- Todas las credenciales se generan automáticamente
- Se almacenan en AWS Systems Manager Parameter Store
- Se rotan después del curso

## Monitorización

### CloudWatch Metrics

- CPU Utilization
- Memory Utilization
- Disk Usage
- Network In/Out

### Alertas

- CPU > 80% por 5 minutos
- Memory > 90% por 5 minutos
- Disk > 85%

## Troubleshooting

Ver [docs/troubleshooting.md](docs/troubleshooting.md) para problemas comunes.

## Soporte

Para problemas durante el despliegue:
1. Revisar logs: `docker compose logs`
2. Verificar recursos: `docker stats`
3. Consultar troubleshooting guide
4. Contactar al instructor

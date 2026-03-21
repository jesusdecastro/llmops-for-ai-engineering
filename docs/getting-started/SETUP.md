# Guía de Setup - TechShop Agent

Esta guía detalla los pasos para configurar el entorno de desarrollo del agente TechShop para el curso de LLMOps.

## Requisitos Previos

- Python 3.10 o superior
- `uv` instalado ([Instalación](https://docs.astral.sh/uv/getting-started/installation/))
- Acceso a AWS Bedrock con Claude Haiku 4.5
- Instancia de Langfuse configurada

## Paso 1: Clonar el Repositorio

```bash
git clone <repository-url>
cd techshop-agent
```

## Paso 2: Crear Entorno Virtual

```bash
# Crear entorno virtual con uv
uv venv

# Activar el entorno virtual
# En Windows:
.venv\Scripts\activate

# En Linux/Mac:
source .venv/bin/activate
```

## Paso 3: Instalar Dependencias

```bash
# Instalar el paquete en modo desarrollo con todas las dependencias
uv pip install -e ".[dev]"

# Instalar pre-commit hooks
pre-commit install
```

## Paso 4: Configurar Variables de Entorno

### Opción A: Archivo .env (Recomendado)

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# En Windows:
notepad .env

# En Linux/Mac:
nano .env
```

### Opción B: Variables de Entorno del Sistema

**Windows (PowerShell):**

```powershell
$env:AWS_BEDROCK_API_KEY = "your-bedrock-api-key"
$env:LANGFUSE_PUBLIC_KEY = "pk-lf-your-public-key"
$env:LANGFUSE_SECRET_KEY = "sk-lf-your-secret-key"
$env:LANGFUSE_HOST = "http://your-langfuse-instance:3000"
```

**Linux/Mac (Bash):**

```bash
export AWS_BEDROCK_API_KEY="your-bedrock-api-key"
export LANGFUSE_PUBLIC_KEY="pk-lf-your-public-key"
export LANGFUSE_SECRET_KEY="sk-lf-your-secret-key"
export LANGFUSE_HOST="http://your-langfuse-instance:3000"
```

## Paso 5: Obtener Credenciales AWS Bedrock

### Para el Curso (API Key - Recomendado)

1. Accede a la [Consola de AWS Bedrock](https://console.aws.amazon.com/bedrock)
2. Navega a **API keys** en el menú lateral
3. Haz clic en **Generate long-term API key**
4. Copia la clave (solo se muestra una vez)
5. Configura la variable `AWS_BEDROCK_API_KEY`

**Nota:** Las API keys de Bedrock expiran en 30 días.

### Para Producción (Credenciales IAM)

```bash
# Configurar AWS CLI
aws configure

# O usar credenciales temporales de IAM Identity Center
# (proporcionadas por el instructor)
```

## Paso 6: Habilitar Acceso a Modelos en Bedrock

1. Abre la [Consola de AWS Bedrock](https://console.aws.amazon.com/bedrock)
2. Navega a **Model access** en el menú lateral
3. Haz clic en **Manage model access**
4. Habilita **Claude Haiku 4.5** (anthropic.claude-haiku-4-5-v1:0)
5. Espera unos minutos para que el acceso se propague

## Paso 7: Verificar la Instalación

```bash
# Ejecutar tests
make test

# Ejecutar linting
make lint

# Ejecutar el ejemplo básico
make example
```

Si todo está configurado correctamente, deberías ver:
- Tests pasando ✓
- Linting sin errores ✓
- El ejemplo ejecutándose y mostrando respuestas del agente ✓

## Paso 8: Verificar Langfuse

1. Accede a tu instancia de Langfuse en el navegador
2. Navega a **Traces**
3. Deberías ver las trazas generadas por el ejemplo básico

## Comandos Útiles

```bash
# Ver todos los comandos disponibles
make help

# Instalar dependencias de desarrollo
make dev

# Ejecutar linting
make lint

# Formatear código
make format

# Ejecutar tests
make test

# Ejecutar pre-commit en todos los archivos
make pre-commit

# Ejecutar ejemplo básico
make example

# Limpiar archivos generados
make clean
```

## Troubleshooting

### Error: "Module 'strands' not found"

```bash
# Reinstalar dependencias
uv pip install -e ".[dev]"
```

### Error: "Access denied to model"

1. Verifica que has habilitado el modelo en la consola de Bedrock
2. Espera 5-10 minutos para que el acceso se propague
3. Verifica que tu API key o credenciales IAM tienen permisos

### Error: "Langfuse credentials not configured"

1. Verifica que las variables de entorno están configuradas:
   ```bash
   # Windows PowerShell
   echo $env:LANGFUSE_PUBLIC_KEY
   
   # Linux/Mac
   echo $LANGFUSE_PUBLIC_KEY
   ```

2. Si usas archivo .env, asegúrate de que está en el directorio raíz del proyecto

### Error: "Invalid API key"

1. Verifica que la API key de Bedrock no ha expirado (30 días)
2. Regenera la API key si es necesario
3. Verifica que no hay espacios extra al copiar la clave

### Pre-commit hooks fallan

```bash
# Ejecutar manualmente para ver los errores
pre-commit run --all-files

# Formatear código automáticamente
make format

# Volver a intentar
git commit
```

## Estructura del Proyecto

```
techshop-agent/
├── src/
│   └── techshop_agent/      # Código fuente del agente
│       ├── __init__.py
│       ├── agent.py         # Agente principal con Strands
│       ├── config.py        # Configuración
│       ├── guardrails.py    # Guardrails de seguridad
│       └── responder.py     # Modelos de respuesta
├── tests/                   # Tests unitarios
├── examples/                # Ejemplos de uso
├── .pre-commit-config.yaml  # Configuración pre-commit
├── pyproject.toml           # Configuración del proyecto
├── Makefile                 # Comandos útiles
└── README.md                # Documentación principal
```

## Próximos Pasos

Una vez completado el setup:

1. **Día 1**: Trabajarás en observabilidad con Langfuse y prompt management
2. **Día 2**: Implementarás evaluaciones con promptfoo y guardrails con LLM Guard
3. **Día 3**: Configurarás CI/CD con GitHub Actions y despliegue con AWS SAM

## Soporte

Si encuentras problemas durante el setup:

1. Revisa esta guía de troubleshooting
2. Consulta el README.md para más información
3. Pregunta al instructor durante el curso

# TechShop Agent - Curso LLMOps

Agente de atención al cliente para TechShop, diseñado para el curso de LLMOps con AWS Bedrock (Strands Agent), Langfuse y promptfoo.

> **🚀 Quickstart**: ¿Primera vez? Lee [QUICKSTART.md](QUICKSTART.md) para empezar en 5 minutos.

## Estructura del Proyecto

```
techshop-agent/
├── src/
│   └── techshop_agent/
│       ├── __init__.py
│       ├── agent.py          # Agente principal usando Strands
│       ├── responder.py      # Modelos de respuesta
│       ├── guardrails.py     # Input/output guardrails
│       └── config.py         # Configuración
├── tests/
│   └── __init__.py
├── .pre-commit-config.yaml   # Configuración pre-commit
├── pyproject.toml
└── README.md
```

## Instalación

```bash
# Crear entorno virtual con uv
uv venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar el paquete en modo desarrollo
uv pip install -e ".[dev]"

# Instalar pre-commit hooks
pre-commit install
```

## Configuración

Configura las siguientes variables de entorno:

```bash
# AWS Bedrock - Opción 1: API Key (desarrollo)
export AWS_BEDROCK_API_KEY=your-bedrock-api-key

# AWS Bedrock - Opción 2: Credenciales IAM (producción)
export AWS_REGION=us-east-1
export AWS_PROFILE=your-profile  # O usa credenciales temporales de IAM Identity Center

# Langfuse
export LANGFUSE_PUBLIC_KEY=your-public-key
export LANGFUSE_SECRET_KEY=your-secret-key
export LANGFUSE_HOST=http://your-langfuse-instance:3000
```

## Uso Básico

```python
from techshop_agent import TechShopAgent

# Inicializar el agente (usa variables de entorno para configuración)
agent = TechShopAgent()

# Procesar una consulta
response = agent.process_query(
    user_query="¿Qué portátiles tenéis disponibles?",
    user_id="student01",
    session_id="session-123",
)

print(f"Respuesta: {response.answer}")
print(f"Confianza: {response.confidence}")
print(f"Categoría: {response.category}")
print(f"Requiere humano: {response.requires_human}")
```

Ver `examples/basic_usage.py` para más ejemplos.

## Desarrollo

Este proyecto está diseñado para el curso de LLMOps. Los alumnos trabajarán en:

- **Día 1**: Observabilidad con Langfuse y prompt management
  - Instrumentación completa del agente
  - Trazabilidad de llamadas y costes
  - Gestión de prompts como código
  - Optimización de tokens

- **Día 2**: Evaluación con promptfoo y guardrails con LLM Guard
  - Creación de golden datasets
  - Evaluaciones automáticas con LLM-as-judge
  - Implementación de guardrails de seguridad
  - Red teaming y testing adversarial

- **Día 3**: CI/CD con GitHub Actions y despliegue con AWS SAM
  - Pipeline de integración continua
  - Despliegue automatizado a Lambda
  - Monitorización en producción
  - Rollback y gestión de versiones

## Documentación Adicional

- [SETUP.md](SETUP.md) - Guía detallada de instalación y configuración
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guía de contribución y convenciones
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Resumen técnico del proyecto

## Estructura de Módulos

- `agent.py`: Agente principal usando Strands Agent con instrumentación Langfuse
- `responder.py`: Modelos Pydantic para respuestas estructuradas
- `guardrails.py`: Validación de inputs y outputs con LLM Guard
- `config.py`: Configuración centralizada

## Características

- **Strands Agent**: Framework agentic con soporte para herramientas y conversación
- **AWS Bedrock**: Claude Haiku 4.5 como modelo base
- **Langfuse**: Observabilidad completa con traces, spans y generations
- **LLM Guard**: Guardrails de seguridad para inputs y outputs
- **Ruff**: Linting estricto con pre-commit hooks
- **Type Safety**: Anotaciones de tipo completas y validación con Pydantic

## Testing

```bash
# Ejecutar tests
pytest tests/

# Ejecutar linting
ruff check src/ tests/

# Ejecutar formatting
ruff format src/ tests/

# Ejecutar pre-commit en todos los archivos
pre-commit run --all-files
```

## Comandos Make

El proyecto incluye un Makefile con comandos útiles:

```bash
make help          # Muestra todos los comandos disponibles
make dev           # Instala dependencias de desarrollo y pre-commit
make lint          # Ejecuta el linter
make format        # Formatea el código
make test          # Ejecuta los tests
make pre-commit    # Ejecuta pre-commit en todos los archivos
make example       # Ejecuta el ejemplo básico
make clean         # Limpia archivos generados
```

## Licencia

MIT

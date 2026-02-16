# TechShop Agent - Resumen del Proyecto

## Descripción

Paquete Python con arquitectura src layout diseñado para el curso de LLMOps. Implementa un agente de atención al cliente para TechShop usando AWS Strands Agent, con observabilidad completa mediante Langfuse y guardrails de seguridad con LLM Guard.

## Tecnologías Principales

### Framework Agentic
- **Strands Agent**: Framework para construir agentes con herramientas y conversación
- **AWS Bedrock**: Claude Haiku 4.5 como modelo base
- **Langfuse**: Plataforma de observabilidad para LLMs

### Calidad de Código
- **Ruff**: Linter y formatter en modo estricto
- **Pre-commit**: Hooks automáticos para validación
- **Pytest**: Framework de testing
- **Type Hints**: Anotaciones completas con Pydantic

### Seguridad
- **LLM Guard**: Guardrails para inputs y outputs
- **Structured Outputs**: Validación con Pydantic

## Estructura del Proyecto

```
techshop-agent/
├── src/techshop_agent/          # Código fuente (src layout)
│   ├── __init__.py              # Exports públicos
│   ├── agent.py                 # Agente principal con Strands
│   ├── config.py                # Configuración centralizada
│   ├── guardrails.py            # Input/output guardrails
│   └── responder.py             # Modelos de respuesta
│
├── tests/                       # Tests unitarios
│   ├── __init__.py
│   ├── test_agent.py
│   └── test_guardrails.py
│
├── examples/                    # Ejemplos de uso
│   └── basic_usage.py
│
├── .pre-commit-config.yaml      # Configuración pre-commit
├── .env.example                 # Template de variables de entorno
├── .gitignore                   # Archivos ignorados por git
├── pyproject.toml               # Configuración del proyecto (hatchling)
├── Makefile                     # Comandos útiles
├── README.md                    # Documentación principal
├── SETUP.md                     # Guía de instalación
├── CONTRIBUTING.md              # Guía de contribución
└── PROJECT_SUMMARY.md           # Este archivo
```

## Características Clave

### 1. Arquitectura Src Layout

```python
# Instalación en modo desarrollo
uv pip install -e ".[dev]"

# Import limpio
from techshop_agent import TechShopAgent, AgentConfig
```

**Ventajas:**
- Separación clara entre código fuente y tests
- Previene imports accidentales de código no instalado
- Facilita empaquetado y distribución

### 2. Strands Agent Integration

```python
from strands import Agent, tool
from strands.models import BedrockModel

# Definir herramientas
@tool
def get_product_info(product_name: str) -> str:
    """Obtiene información sobre un producto."""
    return f"Info de {product_name}"

# Crear agente
model = BedrockModel(
    model_id="anthropic.claude-haiku-4-5-v1:0",
    temperature=0.3,
    max_tokens=1024,
)

agent = Agent(
    model=model,
    tools=[get_product_info],
    system_prompt="Eres un asistente de TechShop",
)

# Usar agente
response = agent("¿Qué portátiles tenéis?")
```

**Ventajas:**
- Gestión automática de herramientas
- Conversación con contexto
- Soporte multi-modelo (Bedrock, Anthropic, OpenAI, Gemini, Llama)

### 3. Observabilidad con Langfuse

```python
from langfuse.decorators import observe

@observe(name="process_query")
def process_query(user_query: str) -> AgentResponse:
    """Procesa consulta con trazabilidad completa."""
    # Langfuse captura automáticamente:
    # - Input/output
    # - Latencia
    # - Tokens y costes
    # - Metadata
    # - Jerarquía de llamadas
    pass
```

**Ventajas:**
- Trazas automáticas con decoradores
- Dashboard para análisis
- Versionado de prompts
- Métricas de coste y latencia

### 4. Guardrails de Seguridad

```python
from techshop_agent.guardrails import GuardrailsManager

manager = GuardrailsManager(
    enable_input=True,
    enable_output=True,
)

# Input guardrails
sanitized, is_safe, metadata = manager.scan_input(user_query)

# Output guardrails
validated, is_valid, metadata = manager.scan_output(response, query)
```

**Protecciones:**
- Prompt injection detection
- PII anonymization
- Toxicity filtering
- Relevance validation
- Topic banning

### 5. Ruff en Modo Estricto

```toml
[tool.ruff.lint]
select = [
    "E", "W",    # pycodestyle
    "F",         # pyflakes
    "I",         # isort
    "N",         # pep8-naming
    "UP",        # pyupgrade
    "ANN",       # flake8-annotations
    "S",         # flake8-bandit
    "B",         # flake8-bugbear
    # ... 30+ categorías más
]
```

**Beneficios:**
- Código consistente y de alta calidad
- Detección temprana de bugs
- Type safety completo
- Formateo automático

### 6. Pre-commit Hooks

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      # ...

  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

**Validaciones automáticas:**
- Linting antes de commit
- Formateo automático
- Validación de YAML/JSON/TOML
- Detección de merge conflicts

## Configuración del Proyecto

### pyproject.toml (Hatchling Backend)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "techshop-agent"
version = "0.1.0"
requires-python = ">=3.10"

dependencies = [
    "strands-agents>=0.1.0",
    "strands-agents-tools>=0.1.0",
    "langfuse>=2.0.0",
    "pydantic>=2.0.0",
    "llm-guard>=0.3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "ruff>=0.8.0",
    "pre-commit>=3.0.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/techshop_agent"]
```

**Ventajas de Hatchling:**
- Backend moderno y rápido
- Sin configuración compleja
- Compatible con PEP 517/518
- Soporte nativo para src layout

## Flujo de Trabajo del Curso

### Día 1: Observabilidad y Prompt Management

**Objetivos:**
- Instrumentar el agente con Langfuse
- Implementar trazabilidad completa
- Gestionar prompts como código
- Optimizar costes de tokens

**TODOs en el código:**
- `agent.py`: Mejorar system prompt
- `agent.py`: Añadir metadata a trazas
- `agent.py`: Implementar herramientas del agente
- `agent.py`: Capturar tokens y costes

### Día 2: Evaluación y Guardrails

**Objetivos:**
- Crear golden dataset
- Implementar evaluaciones con promptfoo
- Configurar guardrails de seguridad
- Realizar red teaming

**TODOs en el código:**
- `guardrails.py`: Input scanners
- `guardrails.py`: Output scanners
- Crear `promptfooconfig.yaml`
- Crear `tests/data/golden_dataset.csv`

### Día 3: CI/CD y Despliegue

**Objetivos:**
- Configurar GitHub Actions
- Desplegar con AWS SAM
- Implementar pipeline completo
- Monitorización en producción

**Archivos a crear:**
- `.github/workflows/ci.yml`
- `.github/workflows/deploy.yml`
- `template.yaml` (SAM)
- `samconfig.toml`

## Comandos Útiles

```bash
# Setup inicial
make dev                    # Instalar deps + pre-commit

# Desarrollo
make lint                   # Ejecutar linter
make format                 # Formatear código
make test                   # Ejecutar tests
make example                # Ejecutar ejemplo

# Validación
make pre-commit             # Ejecutar todos los checks

# Limpieza
make clean                  # Limpiar archivos generados
```

## Dependencias Principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| strands-agents | >=0.1.0 | Framework agentic |
| strands-agents-tools | >=0.1.0 | Herramientas comunitarias |
| langfuse | >=2.0.0 | Observabilidad |
| pydantic | >=2.0.0 | Validación de datos |
| llm-guard | >=0.3.0 | Guardrails de seguridad |
| ruff | >=0.8.0 | Linting y formateo |
| pytest | >=7.0.0 | Testing |
| pre-commit | >=3.0.0 | Git hooks |

## Variables de Entorno

```bash
# AWS Bedrock
AWS_BEDROCK_API_KEY=xxx        # API key (desarrollo)
AWS_REGION=us-east-1           # Región AWS

# Langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-xxx  # Public key
LANGFUSE_SECRET_KEY=sk-lf-xxx  # Secret key
LANGFUSE_HOST=http://...       # URL de Langfuse
```

## Modelos de Datos

### AgentConfig

```python
@dataclass
class AgentConfig:
    aws_region: str = "us-east-1"
    model_id: str = "anthropic.claude-haiku-4-5-v1:0"
    max_tokens: int = 1024
    temperature: float = 0.3
    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_host: str
    enable_input_guardrails: bool = True
    enable_output_guardrails: bool = True
```

### AgentResponse

```python
class AgentResponse(BaseModel):
    answer: str
    confidence: Literal["high", "medium", "low"]
    category: Literal["product", "complaint", "general", "out_of_scope"]
    requires_human: bool
```

## Testing

```bash
# Ejecutar todos los tests
pytest tests/

# Con cobertura
pytest tests/ --cov=techshop_agent --cov-report=html

# Tests específicos
pytest tests/test_agent.py::test_agent_initialization

# Modo verbose
pytest tests/ -v
```

## Calidad de Código

### Métricas

- **Type Coverage**: 100% (todas las funciones públicas)
- **Linting**: 0 errores con Ruff estricto
- **Test Coverage**: >80% (objetivo)
- **Docstring Coverage**: 100% (funciones públicas)

### Reglas de Ruff Habilitadas

- 30+ categorías de reglas
- Type hints obligatorios
- Docstrings requeridos
- Security checks (Bandit)
- Performance checks
- Best practices enforcement

## Recursos

- [Documentación Strands](https://docs.strands.ai/)
- [Documentación Langfuse](https://langfuse.com/docs)
- [Documentación Ruff](https://docs.astral.sh/ruff/)
- [AWS Bedrock](https://aws.amazon.com/bedrock/)
- [LLM Guard](https://llm-guard.com/)

## Licencia

MIT

## Autores

Curso LLMOps - Diseñado para formación en operaciones de LLMs con AWS Bedrock

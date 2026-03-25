# 📓 LLMOps Course — Notebooks

Notebooks incrementales del curso de LLMOps. Cada notebook construye sobre el anterior, añadiendo una capa de operacionalización al agente TechShop.

## Setup rápido

El entorno se gestiona con [uv](https://docs.astral.sh/uv/) y las versiones están lockeadas en `uv.lock` para reproducibilidad.

```bash
# 1. Instalar uv (si no lo tienes)
pipx install uv  # o: curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Instalar dependencias (crea .venv automáticamente desde uv.lock)
cd notebooks/
uv sync

# 3. Configurar credenciales
cp .env.example .env
# Editar .env con tus credenciales AWS y Langfuse

# 4. Abrir notebooks
uv run jupyter notebook
# o usar VS Code con extensión Jupyter (seleccionar kernel .venv)
```

> **Nota:** `uv sync` respeta el `uv.lock` y garantiza que todos los estudiantes tengan exactamente las mismas versiones.
> Para actualizar dependencias: `uv lock --upgrade && uv sync`

## Estructura

### Día 1 — Observabilidad

| Notebook | Tema | Resultado |
|----------|------|-----------|
| [01_setup_agent](day_1/01_setup_agent.ipynb) | Setup + Primer agente | Agente TechShop funcionando con Bedrock |
| [02_observability](day_1/02_observability.ipynb) | Langfuse tracing | Agente instrumentado, trazas en dashboard |

### Día 2 — Prompt Management + Evaluación

| Notebook | Tema | Resultado |
|----------|------|-----------|
| [03_prompt_management](day_2/03_prompt_management.ipynb) | Prompt versioning | Prompt v1 → v2 en Langfuse con labels |
| [04_evaluation](day_2/04_evaluation.ipynb) | Evaluación del agente | Test suite + LLM-as-judge + comparación v1/v2 |

### Día 3 — Guardrails + Pipeline

| Notebook | Tema | Resultado |
|----------|------|-----------|
| [05_guardrails](day_3/05_guardrails.ipynb) | Bedrock Guardrails | Agente con protección input/output |
| [06_full_pipeline](day_3/06_full_pipeline.ipynb) | Pipeline completo | Todo integrado: trazas + prompt + eval + guardrails |

## Requisitos

- Python 3.10+
- Cuenta AWS con acceso a Amazon Bedrock
- Cuenta gratuita en [Langfuse Cloud](https://cloud.langfuse.com)

## Variables de entorno necesarias

| Variable | Descripción | Notebook |
|----------|-------------|----------|
| `AWS_ACCESS_KEY_ID` | Credencial AWS | Todos |
| `AWS_SECRET_ACCESS_KEY` | Credencial AWS | Todos |
| `AWS_DEFAULT_REGION` | Región AWS (default: us-east-1) | Todos |
| `MODEL_ID` | Modelo Bedrock | Todos |
| `LANGFUSE_PUBLIC_KEY` | API key pública Langfuse | NB2+ |
| `LANGFUSE_SECRET_KEY` | API key secreta Langfuse | NB2+ |
| `LANGFUSE_HOST` | URL Langfuse Cloud | NB2+ |

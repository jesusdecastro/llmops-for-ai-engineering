# 📓 LLMOps Course — Notebooks

Notebooks incrementales del curso de LLMOps. Cada notebook construye sobre el anterior, añadiendo una capa de operacionalización al agente TechShop.
← [Volver al README principal](../README.md) · [Documentación](../docs/README.md) · [Slides](../slides/README.md)

---

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

### Día 1 — Desarrollo Profesional

| Notebook | Tema | Resultado |
|----------|------|-----------|
| [01_setup_agent](day_1/01_setup_agent.ipynb) | Agente + Observabilidad | Agente TechShop con Bedrock, instrumentado con Langfuse |
| [02_prompt_management](day_1/02_prompt_management.ipynb) | Prompt Management | Prompt v1 → v2 en Langfuse con labels y rollback |

## Requisitos

- Python 3.10+
- Cuenta AWS con acceso a Amazon Bedrock
- Cuenta gratuita en [Langfuse Cloud](https://cloud.langfuse.com)

## Variables de entorno necesarias

| Variable | Descripción | Notebook |
|----------|-------------|----------|
| `AWS_ACCESS_KEY_ID` | Credencial AWS | Todos |
| `AWS_SECRET_ACCESS_KEY` | Credencial AWS | Todos |
| `AWS_DEFAULT_REGION` | Región AWS (default: eu-west-1) | Todos |
| `MODEL_ID` | Modelo Bedrock | Todos |
| `LANGFUSE_PUBLIC_KEY` | API key pública Langfuse | NB1+ |
| `LANGFUSE_SECRET_KEY` | API key secreta Langfuse | NB1+ |
| `LANGFUSE_HOST` | URL Langfuse Cloud | NB1+ |

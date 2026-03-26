# LLMOps Course — Notebooks

Notebooks incrementales del curso. Cada notebook construye sobre el anterior.

← [README principal](../README.md) · [Agente](../src/techshop_agent/) · [Streamlit](../streamlit_app/README.md)

---

## Lanzar JupyterLab

```bash
cd notebooks/
uv sync
uv run jupyter lab
```

Abre **http://localhost:8888**. Cierra con `Ctrl+C`.

Alternativa: abrir los `.ipynb` directamente en VS Code (seleccionar kernel `notebooks/.venv`).

---

## Notebooks

| # | Notebook | Tema |
|---|----------|------|
| 1 | [01_setup_agent](day_1/01_setup_agent.ipynb) | Setup + primer agente con Bedrock |
| 2 | [02_observability](day_1/02_observability.ipynb) | Instrumentación con Langfuse |
| 3 | [03_prompt_management](day_1/03_prompt_management.ipynb) | Prompts versionados con labels y rollback |

---

## Variables de entorno

Configura `.env` en la **raíz del repositorio** (ver paso 3 del [README principal](../README.md)):

| Variable | Descripción | Desde |
|----------|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Credencial AWS | NB1 |
| `AWS_SECRET_ACCESS_KEY` | Credencial AWS | NB1 |
| `AWS_DEFAULT_REGION` | Región AWS (default: eu-west-1) | NB1 |
| `MODEL_ID` | Modelo Bedrock | NB1 |
| `LANGFUSE_PUBLIC_KEY` | API key pública Langfuse | NB2 |
| `LANGFUSE_SECRET_KEY` | API key secreta Langfuse | NB2 |
| `LANGFUSE_HOST` | URL Langfuse Cloud | NB2 |

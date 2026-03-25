# 🤖 LLMOps para AI Engineering — Curso Hiberus Tecnología

Repositorio del curso práctico de **24 horas (3 días)** donde operacionalizas un agente de IA real con los estándares de la industria en 2026.

> **Hilo conductor:** TechShop Agent — asistente de customer service para una tienda de electrónica, construido sobre **AWS Bedrock + Strands Agents**, con **4 fallos deliberados** que descubrirás y corregirás durante el curso.

---

## 🗺️ Índice completo del repositorio

### Documentación general

| Documento | Descripción |
|-----------|-------------|
| [docs/README.md](docs/README.md) | **Índice de toda la documentación** |
| [docs/plan_formativo.md](docs/plan_formativo.md) | Plan de formación completo (3 días, 24h) |
| [docs/resumen_curso.md](docs/resumen_curso.md) | Resumen ejecutivo: fallos F1–F4, stack, narrativa |
| [docs/architecture/agent_spec.md](docs/architecture/agent_spec.md) | Especificación técnica del agente |
| [docs/project/PROJECT_SUMMARY.md](docs/project/PROJECT_SUMMARY.md) | Resumen técnico del proyecto |
| [docs/project/CONTRIBUTING.md](docs/project/CONTRIBUTING.md) | Guía de contribución y convenciones |
| [docs/project/COPILOT_SETUP.md](docs/project/COPILOT_SETUP.md) | Configuración de GitHub Copilot para el curso |

### Código fuente

| Módulo | Descripción |
|--------|-------------|
| [src/techshop_agent/agent.py](src/techshop_agent/agent.py) | Orquestador principal (Strands Agent) |
| [src/techshop_agent/tools.py](src/techshop_agent/tools.py) | Herramientas: `search_catalog`, `get_faq_answer` |
| [src/techshop_agent/config.py](src/techshop_agent/config.py) | Configuración Pydantic + system prompt |
| [src/techshop_agent/guardrails.py](src/techshop_agent/guardrails.py) | Guardrails de entrada/salida (LLM Guard) |
| [src/techshop_agent/responder.py](src/techshop_agent/responder.py) | Contrato `AgentResponse` (Pydantic) |
| [src/techshop_agent/data/](src/techshop_agent/data/) | `catalog.json` + `faqs.json` |

### Interfaz Streamlit

| Recurso | Descripción |
|---------|-------------|
| [streamlit_app/README.md](streamlit_app/README.md) | **Guía paso a paso para ejecutar la UI** |
| [streamlit_app/app.py](streamlit_app/app.py) | Aplicación Streamlit con tema Hiberus |
| [streamlit_app/.streamlit/config.toml](streamlit_app/.streamlit/config.toml) | Tema visual (paleta naranja Hiberus) |

### Notebooks del curso

| Recurso | Descripción |
|---------|-------------|
| [notebooks/README.md](notebooks/README.md) | Índice de notebooks por día |
| [notebooks/day_1/01_setup_agent.ipynb](notebooks/day_1/01_setup_agent.ipynb) | Setup + primer agente |
| [notebooks/day_1/02_observability.ipynb](notebooks/day_1/02_observability.ipynb) | Langfuse tracing |
| [notebooks/day_2/03_prompt_management.ipynb](notebooks/day_2/03_prompt_management.ipynb) | Gestión de prompts en Langfuse |
| [notebooks/day_2/04_evaluation.ipynb](notebooks/day_2/04_evaluation.ipynb) | Evaluación con promptfoo |
| [notebooks/day_3/05_guardrails.ipynb](notebooks/day_3/05_guardrails.ipynb) | Guardrails con LLM Guard |
| [notebooks/day_3/06_full_pipeline.ipynb](notebooks/day_3/06_full_pipeline.ipynb) | Pipeline completo CI/CD |

### Slides del curso

| Recurso | Descripción |
|---------|-------------|
| [slides/README.md](slides/README.md) | Instrucciones de uso con Gamma.app |
| [slides/day_1/M1_que_es_llmops.md](slides/day_1/M1_que_es_llmops.md) | M1 — ¿Qué es LLMOps? |
| [slides/day_1/M2_observabilidad_langfuse.md](slides/day_1/M2_observabilidad_langfuse.md) | M2 — Observabilidad con Langfuse |
| [slides/day_2/M3_prompt_management.md](slides/day_2/M3_prompt_management.md) | M3 — Prompt Management |
| [slides/day_2/M4_evaluacion_agentica.md](slides/day_2/M4_evaluacion_agentica.md) | M4 — Evaluación agentica |
| [slides/day_3/M5_guardrails_safety.md](slides/day_3/M5_guardrails_safety.md) | M5 — Guardrails y Safety |
| [slides/day_3/M6_cicd_produccion.md](slides/day_3/M6_cicd_produccion.md) | M6 — CI/CD en producción |

### Infraestructura

| Recurso | Descripción |
|---------|-------------|
| [infrastructure/terraform/](infrastructure/terraform/) | VPC, EC2, SSM, CloudWatch, Security Groups |
| [infrastructure/docker/](infrastructure/docker/) | Docker Compose para Langfuse local |
| [infrastructure/scripts/](infrastructure/scripts/) | Scripts de deploy, backup y configuración |

### Tests

| Módulo | Descripción |
|--------|-------------|
| [tests/test_agent.py](tests/test_agent.py) | Tests del agente principal |
| [tests/test_guardrails.py](tests/test_guardrails.py) | Tests de guardrails |
| [tests/test_observability.py](tests/test_observability.py) | Tests de instrumentación Langfuse |
| [tests/test_routing.py](tests/test_routing.py) | Tests de routing de herramientas |
| [tests/test_response_contract.py](tests/test_response_contract.py) | Tests del contrato `AgentResponse` |

---

## ⚡ Quickstart

```bash
# 1. Clonar
git clone <repo-url>
cd llmops-for-ai-engineering

# 2. Instalar dependencias
uv sync

# 3. Configurar variables de entorno
cp .env.example .env   # editar con credenciales AWS y Langfuse

# 4. Ejecutar el agente (ejemplo básico)
make example

# 5. Ejecutar la interfaz web
cd streamlit_app && uv sync && streamlit run app.py
```

> Guía detallada paso a paso: **[streamlit_app/README.md](streamlit_app/README.md)**

---

## 🗓️ Estructura del curso (3 días)

| Día | Pregunta clave | Herramientas | Notebooks |
|-----|---------------|-------------|-----------|
| **Día 1** | ¿Qué está fallando y cómo me entero? | Langfuse Tracing | [01](notebooks/day_1/01_setup_agent.ipynb) · [02](notebooks/day_1/02_observability.ipynb) |
| **Día 2** | ¿Cómo sé que no va a romper antes de producción? | Langfuse Prompts + promptfoo | [03](notebooks/day_2/03_prompt_management.ipynb) · [04](notebooks/day_2/04_evaluation.ipynb) |
| **Día 3** | ¿Cómo lo despliego con confianza? | LLM Guard + GitHub Actions + SAM | [05](notebooks/day_3/05_guardrails.ipynb) · [06](notebooks/day_3/06_full_pipeline.ipynb) |

---

## 🐛 Los 4 fallos deliberados

| ID | Síntoma | Herramienta que lo revela |
|----|---------|--------------------------|
| **F1** | Hallucination silenciosa — inventa productos | Langfuse (trace con `results_count=0`) |
| **F2** | Extrapolación del FAQ — respuestas incorrectas en edge cases | promptfoo + LLM-as-judge |
| **F3** | Scope creep — responde fuera de dominio | LLM Guard + evaluaciones de scope |
| **F4** | Tool selection gap — no llama a herramientas para queries válidas | Langfuse (trace sin spans de herramientas) |

---

## 🛠️ Stack técnico

| Herramienta | Rol |
|-------------|-----|
| [Strands Agents](https://github.com/strands-agents/sdk-python) | Framework del agente |
| AWS Bedrock (Claude Haiku 4.5) | Modelo de lenguaje |
| [Langfuse](https://langfuse.com) | Observabilidad + Prompt Management |
| [LLM Guard](https://llm-guard.com) | Guardrails de seguridad |
| [Streamlit](https://streamlit.io) | Interfaz web del agente |
| [uv](https://docs.astral.sh/uv/) + ruff + pyright | Tooling Python |
| Terraform + Docker Compose | Infraestructura |

---

## 🔧 Comandos principales

```bash
make dev           # Instala dependencias + pre-commit
make qa            # lint + format-check + typecheck + test + security
make test          # pytest tests/ -v
make lint          # ruff check
make typecheck     # pyright src/techshop_agent
make security      # bandit -r src/techshop_agent
make example       # ejecuta examples/basic_usage.py
make tf-check      # valida Terraform
make pre-commit    # pre-commit run --all-files
```

---

## 📄 Licencia

MIT · by **Hiberus Tecnología**


# M5 — CI/CD para Prompts: Despliegue sin Tocar Código
## Día 2 · Bloque 2 · 12:00 – 13:30

> **Prompt para Gamma.app:** Crea una presentación educativa sobre CI/CD para prompts de agentes LLM. Estilo profesional, fondos oscuros. Audiencia: ingenieros junior que conocen CI/CD de código pero nunca han desplegado prompts. Cubre: por qué el prompt necesita su propio pipeline, el flujo push→evaluate→promote, scripts Python descriptivos, configuración para GitHub Actions y GitLab CI, Streamlit con pestañas por entorno, y labels como punteros a versiones. Incluye YAMLs reales y código Python real.

---

## Slide 1: Portada

**CI/CD para Prompts**
Automatizar el despliegue de prompts como artefactos de primera clase

---

## Slide 2: Código vs Prompt — Dos artefactos, dos pipelines

| Aspecto | Código (Git) | Prompt (Langfuse) |
|---------|:-----------:|:-----------------:|
| **Frecuencia de cambio** | Semanal | Potencialmente más frecuente |
| **Quién lo cambia** | Desarrolladores | Devs + Product + Lingüistas |
| **Despliegue** | Build + Restart (minutos) | Pipeline push→evaluate→promote |
| **Rollback** | git revert + redespliegue | Revertir label (tras CI/CD o manual en UI) |
| **Test** | pytest (determinista) | Evaluación semántica + determinista |
| **Versionado** | Git commits | Langfuse versions |
| **Entornos** | Git branches | Langfuse labels |

**El prompt no es una configuración** — es el artefacto que controla el comportamiento del LLM. Merece su propio pipeline.

> En DevOps, el principio es tratar la infraestructura como código. En LLMOps, el equivalente es **tratar los prompts como artefactos desplegables** con versionado, evaluación y promoción controlada.

---

## Slide 3: El flujo completo — Push → Evaluate → Promote

```
       Developer                CI/CD Pipeline                  Langfuse
       ─────────               ──────────────                  ────────
           │                         │                            │
     edita prompt                    │                            │
           │                         │                            │
     git push ──────────────────────→│                            │
           │                  push_prompt.py ────────────────────→│
           │                         │                    create v3 [staging]
           │                         │                            │
           │                 evaluate_prompt.py                   │
           │                    run_experiment() ────────────────→│
           │                         │←────── scores, traces ─────│
           │                         │                            │
           │                  if scores ≥ threshold:              │
           │                         │                            │
           │                 promote_prompt.py ──────────────────→│
           │                         │                    move [production]
           │                         │                    → v3
           │                         │                            │
  ┌────────┴──────────────┐          │                            │
  │ STREAMLIT              │    get_prompt(label="production")    │
  │ Tab: Production ───────┼────────────────────────────────────→│
  │                        │←─────────── v3 content ─────────────│
  └────────────────────────┘                                     │
```

---

## Slide 4: Labels = Punteros a entornos

**Los labels de Langfuse son como ramas de Git, pero para prompts:**

```
techshop-system-prompt
├── v1 ............... (prompt original, sin restricciones)
├── v2 [latest] ...... (con scope restringido)
├── v3 [staging] ..... (candidato a producción)
└── v4 [production] .. (activo para usuarios)
```

**Reglas de labels:**
1. `latest` — SIEMPRE apunta a la última versión creada
2. `staging` — Apunta a la versión candidata (post-push, pre-evaluate)
3. `production` — Apunta a la versión que el agente usa en producción

**Mover un label** es instantáneo y no requiere cambiar código:
```python
# El agente siempre hace:
prompt = langfuse.get_prompt("techshop-system-prompt", label="production")
# Cuando movemos el label, la siguiente request usa la nueva versión
```

---

## Slide 5: Scripts Python — Descriptivos y portables

### ¿Por qué Python y no bash?

| Aspecto | bash | Python |
|---------|------|--------|
| Legibilidad | `-f "$dir" && ...` | `if path.exists():` |
| Error handling | `set -e` (frágil) | `try/except` (robusto) |
| Portabilidad | Linux only | Linux + macOS + Windows |
| Testing | Difícil | pytest |
| Dependencias | curl + jq | `langfuse` SDK |

### Los 3 scripts

```
src/techshop_agent/cicd/
├── __init__.py
├── push_prompt.py       # python -m techshop_agent.cicd.push_prompt
├── evaluate_prompt.py   # python -m techshop_agent.cicd.evaluate_prompt
└── promote_prompt.py    # python -m techshop_agent.cicd.promote_prompt
```

Cada script:
- Usa `argparse` para argumentos CLI
- Carga `.env` con `dotenv`
- Es ejecutable directamente: `python -m techshop_agent.cicd.push_prompt --help`
- Devuelve exit code 0/1 para CI/CD

---

## Slide 6: GitHub Actions — Pipeline completo

```yaml
name: Prompt CI/CD
on:
  push:
    paths: ['prompts/**']    # Solo trigger si cambian prompts

jobs:
  push-to-langfuse:          # ← CI: sube a staging
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[llmops]"
      - run: python -m techshop_agent.cicd.push_prompt
              --file prompts/system_prompt.txt
              --labels staging latest

  evaluate:                  # ← Quality Gate
    needs: push-to-langfuse
    runs-on: ubuntu-latest
    steps:
      - run: python -m techshop_agent.cicd.evaluate_prompt
              --label staging --threshold 0.7

  promote:                   # ← CD: promueve si pasa
    needs: evaluate
    runs-on: ubuntu-latest
    steps:
      - run: python -m techshop_agent.cicd.promote_prompt
              --from-label staging --to-label production
```

**Secrets:** `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL`, `AWS_*`

---

## Slide 7: GitLab CI — Pipeline equivalente

```yaml
stages: [push, evaluate, promote]

push-prompt:
  stage: push
  image: python:3.11-slim
  rules:
    - changes: [prompts/**]
  script:
    - pip install -e ".[llmops]"
    - python -m techshop_agent.cicd.push_prompt
        --file prompts/system_prompt.txt
        --labels staging latest

evaluate-prompt:
  stage: evaluate
  needs: [push-prompt]
  script:
    - python -m techshop_agent.cicd.evaluate_prompt
        --label staging --threshold 0.7

promote-prompt:
  stage: promote
  needs: [evaluate-prompt]
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  script:
    - python -m techshop_agent.cicd.promote_prompt
        --from-label staging --to-label production
```

**Variables CI/CD:** Settings → CI/CD → Variables (con Mask activado)

---

## Slide 8: Streamlit — Pestañas por entorno

```python
ENVIRONMENTS = {
    "🟢 Production": "production",
    "🟡 Staging":    "staging",
    "🔵 Development": "latest",
}

tabs = st.tabs(list(ENVIRONMENTS.keys()))
for tab, (env_name, label) in zip(tabs, ENVIRONMENTS.items()):
    with tab:
        prompt = langfuse.get_prompt("techshop-system-prompt", label=label)
        st.write(f"**Versión:** {prompt.version}")
        st.code(prompt.compile(), language="text")

        query = st.text_input("Pregunta:", key=f"q_{label}")
        if query:
            agent = create_agent(system_prompt=prompt.compile())
            st.write(str(agent(query)))
```

Cuando el pipeline promueve un prompt a `production`, la pestaña "Production" de Streamlit devuelve la nueva versión en la siguiente petición, porque consulta el label por API.

---

## Slide 9: Resumen del Día 2

| Qué aprendimos | Herramienta |
|----------------|------------|
| Evaluar agentes sistemáticamente | `run_experiment()` + evaluadores |
| Dataset de evaluación alineado con F1–F4 | `EVAL_DATASET` |
| Quality gate que bloquea promoción | `evaluate_prompt.py` (exit 0/1) |
| CI/CD para prompts (no para código) | Scripts Python + Langfuse API |
| GitHub Actions pipeline (CI) | `.github/workflows/prompt-staging.yml` |
| GitHub Actions pipeline (CD) | `.github/workflows/prompt-production.yml` |
| GitLab CI pipeline | `.gitlab-ci.yml` |
| Streamlit con pestañas por entorno | `app.py` con labels dinámicos |
| CLI para terminal | `python -m techshop_agent.evaluation` |

> **El ciclo LLMOps está completo:** Develop → Observe → Version → Evaluate → Deploy → Monitor → Iterate

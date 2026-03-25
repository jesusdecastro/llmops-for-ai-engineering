# M4 — CI/CD: El Quality Gate Automático
## Día 2 · Bloque 2 · 10:45 – 12:15

> **Prompt para Gamma.app:** Crea una presentación educativa sobre CI/CD para aplicaciones de IA con agentes. Estilo profesional, fondos oscuros. Tema: "Deployamos cuando pasa los tests". Audiencia: ingenieros junior que ya saben evaluar agentes. Incluye diagrama de pipeline CI/CD con evaluación de LLM como gate, ejemplo de GitHub Actions, flujo de prompt deploy con labels. Pocas palabras, muchos diagramas.

---

## Slide 1: Portada

**CI/CD: El Quality Gate Automático**
Deployamos cuando pasa los tests.

---

## Slide 2: El pipeline CI/CD para LLMs

**No es como CI/CD tradicional.** Hay una pieza nueva: la evaluación del LLM.

```
┌─── Trigger ──────────────────────────────────────────┐
│  PR: cambio en código, prompt, o configuración       │
└──────────────┬───────────────────────────────────────┘
               ▼
┌─── Stage 1: Checks estándar (< 2 min) ──────────────┐
│  Lint (ruff)                                         │
│  Type check (pyright)                                │
│  Unit tests (pytest)                                 │
│  Security scan (bandit)                              │
└──────────────┬───────────────────────────────────────┘
               ▼
┌─── Stage 2: Eval determinística (< 1 min) ──────────┐
│  10+ test cases con assertions                       │
│  Contains, not-contains, regex                       │
│  Gratis, rápido                                      │
└──────────────┬───────────────────────────────────────┘
               ▼
┌─── Stage 3: Eval LLM-as-judge (< 5 min) ────────────┐
│  5 test cases con LLM evaluador                      │
│  Relevancia, fidelidad, profesionalidad              │
│  Cuesta tokens (~$0.05 por run)                      │
└──────────────┬───────────────────────────────────────┘
               ▼
┌─── Gate ─────────────────────────────────────────────┐
│  Pass rate >= 80%? → Merge + Deploy                  │
│  Pass rate < 80%?  → PR bloqueado + Reporte          │
└──────────────────────────────────────────────────────┘
```

---

## Slide 3: ¿Qué cambia respecto a CI/CD tradicional?

| CI/CD tradicional | CI/CD para LLMs |
|-------------------|-----------------|
| Tests son determinísticos | Tests pueden ser probabilísticos |
| Pass/fail binario | Score con threshold (4.2/5 >= 4.0?) |
| Tests gratis | LLM-as-judge cuesta tokens |
| Segundos | Minutos (llamadas al LLM) |
| Reproducible al 100% | Estocástico (misma query, respuesta diferente) |

> **Implicación:** Necesitas thresholds más flexibles y múltiples runs para reducir flakiness.

---

## Slide 4: GitHub Actions — Ejemplo real

```yaml
# .github/workflows/eval.yml
name: LLM Evaluation Gate

on:
  pull_request:
    paths:
      - "prompts/**"
      - "src/techshop_agent/**"

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install deps
        run: pip install -e ".[dev]"

      - name: Run deterministic evals
        run: python scripts/eval_deterministic.py

      - name: Run LLM-as-judge evals
        run: python scripts/eval_llm_judge.py
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          LANGFUSE_SECRET_KEY: ${{ secrets.LANGFUSE_SECRET_KEY }}
```

---

## Slide 5: Prompt deploy — El flujo completo

```
1. Desarrollador crea prompt v3 en Langfuse (label: "staging")
         │
2. CI ejecuta evaluaciones contra v3
         │
3. Si pasan → Script mueve label "production" a v3
         │
4. El agente en producción lee el prompt con label "production"
         │
5. Automáticamente empieza a usar v3
         │
6. Langfuse tracing monitoriza el comportamiento
         │
7. Si hay problemas → Mover "production" de vuelta a v2 (rollback)
```

**Zero-downtime prompt deploy.** Sin reiniciar nada.

---

## Slide 6: Herramientas para CI/CD de LLMs

| Herramienta | Tipo | Ventaja |
|-------------|------|---------|
| **promptfoo** | CLI + YAML | Config en YAML, reportes comparativos, CI-native |
| **deepeval** | Python + pytest | pytest-friendly, métricas semánticas integradas |
| **Custom Python + Langfuse** | Tu código | Máximo control, sin dependencias extra |
| **Braintrust** | Plataforma | Comenta directamente en PRs con delta de métricas |

```yaml
# promptfoo: evaluación en YAML
tests:
  - vars:
      query: "¿Qué portátiles tenéis?"
    assert:
      - type: contains
        value: "ProBook"
      - type: llm-rubric
        value: "La respuesta es relevante y profesional"
```

> **Para este curso:** Custom Python + Langfuse. En producción, promptfoo es una opción robusta.

---

## Slide 7: El patrón completo: Evaluate + Deploy

```
  Cambio en código o prompt
         │
  ┌──────┴──────┐
  │  CI: evals  │ ← Dataset offline (NB3)
  └──────┬──────┘
         │
  ┌──────┴──────┐
  │  Gate: pass? │
  └──┬──────┬───┘
     │      │
    Yes     No → PR bloqueado
     │
  ┌──┴──────────┐
  │ Promote label│ ← Langfuse "production" → nueva versión
  └──────┬──────┘
         │
  ┌──────┴──────┐
  │  Producción  │ → Langfuse tracing → detectar fallos
  └──────┬──────┘
         │
         └──→ Nuevo test case → Dataset → CI
```

> Esto cierra las fases **Evaluate** y **Deploy** del ciclo LLMOps. Mañana añadimos Guardrails (protección) y juntamos todo.

---

## Slide 8: Resumen

| Concepto | Takeaway |
|----------|----------|
| **Pipeline** | Checks estándar + eval determinística + LLM-as-judge |
| **Gate** | No merge sin pasar evals — el PR se bloquea |
| **Prompt deploy** | Labels de Langfuse, zero-downtime, rollback instantáneo |
| **Estocástico** | Thresholds flexibles, múltiples runs |

**Esta tarde en los notebooks:**
1. **Notebook 3** — Crear la suite de evaluación (dataset + determinística + LLM-as-judge)
2. **Notebook 4** — Ejecutar las evals como pipeline CI/CD automatizado

> **Concepto clave:** Del "deployamos y rezamos" al "deployamos cuando pasa los tests".

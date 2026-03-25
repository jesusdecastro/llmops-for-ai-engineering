# M6 — CI/CD para LLMs y Visión de Producción
## Día 3 · Bloque 2 · 10:45 – 12:15

> **Prompt para Gamma.app:** Crea una presentación educativa sobre CI/CD para aplicaciones de IA y la visión completa de un agente en producción. Estilo profesional, fondos oscuros. Tema: "De notebooks a producción". Audiencia: ingenieros junior al final de un curso de 3 días. Incluye diagrama de pipeline CI/CD, tabla de gaps de producción, ciclo LLMOps completo. Tono: empoderador, "ahora sabéis lo que hace falta".

---

## Slide 1: Portada

**CI/CD para LLMs y Visión de Producción**
De notebooks a producción: el camino completo.

---

## Slide 2: ¿Dónde estamos?

```
Día 1: ✅ Agente + Observabilidad
         "Sé qué está pasando"

Día 2: ✅ Prompt Management + Evaluación
         "Sé que funciona antes de deployar"

Día 3: ✅ Guardrails + Pipeline
         "Sé que está protegido"

Ahora: ¿Cómo llego a producción de verdad?
```

---

## Slide 3: El pipeline CI/CD para LLMs

**No es como CI/CD tradicional.** Hay una pieza nueva: la evaluación del LLM.

```
┌─── Trigger ──────────────────────────────────────────┐
│  PR: cambio en código, prompt, o configuración       │
└──────────────┬───────────────────────────────────────┘
               ▼
┌─── Stage 1: Checks estándar (< 2 min) ──────────────┐
│  ✅ Lint (ruff)                                      │
│  ✅ Type check (pyright)                             │
│  ✅ Unit tests (pytest)                              │
│  ✅ Security scan (bandit)                           │
└──────────────┬───────────────────────────────────────┘
               ▼
┌─── Stage 2: Eval determinística (< 1 min) ──────────┐
│  ✅ 10+ test cases con assertions                    │
│  ✅ Contains, not-contains, regex                    │
│  ✅ Gratis, rápido                                   │
└──────────────┬───────────────────────────────────────┘
               ▼
┌─── Stage 3: Eval LLM-as-judge (< 5 min) ────────────┐
│  ⚡ 5 test cases con LLM evaluador                   │
│  ⚡ Relevancia, fidelidad, profesionalidad            │
│  ⚡ Cuesta tokens (~$0.05 por run)                    │
└──────────────┬───────────────────────────────────────┘
               ▼
┌─── Gate ─────────────────────────────────────────────┐
│  Pass rate ≥ 80%? ──→ ✅ Merge + Deploy              │
│  Pass rate < 80%? ──→ ❌ PR bloqueado + Reporte     │
└──────────────────────────────────────────────────────┘
```

---

## Slide 4: ¿Qué cambia respecto a CI/CD tradicional?

| CI/CD tradicional | CI/CD para LLMs |
|-------------------|-----------------|
| Tests son determinísticos | Tests pueden ser probabilísticos |
| Pass/fail binario | Score con threshold (4.2/5 ≥ 4.0?) |
| Tests gratis | LLM-as-judge cuesta tokens |
| Segundos | Minutos (llamadas al LLM) |
| Reproducible al 100% | Estocástico (misma query → respuesta diferente) |

> **Implicación:** Necesitas thresholds más flexibles y múltiples runs para reducir flakiness.

---

## Slide 5: GitHub Actions — Ejemplo real

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

## Slide 6: Prompt deploy — El flujo completo

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

## Slide 7: El ciclo LLMOps completo

```
┌────────────────────────────────────────────────────────┐
│                    CICLO LLMOps                        │
│                                                        │
│   [Develop] ──→ [Evaluate] ──→ [Deploy] ──→ [Observe]  │
│       ↑                                        │       │
│       └──────── [Iterate] ◀───────────────────┘       │
│                                                        │
│   Transversal: GUARDRAILS                              │
└────────────────────────────────────────────────────────┘
```

| Fase | Lo que hicimos | Notebook |
|------|---------------|----------|
| **Develop** | Agente Strands + Bedrock + Tools | NB1 |
| **Observe** | Langfuse @observe, trazas, métricas | NB2 |
| **Develop (prompts)** | Prompt v1 → v2 en Langfuse | NB3 |
| **Evaluate** | Determinística + LLM-as-judge | NB4 |
| **Guardrails** | Bedrock Guardrails + Custom | NB5 |
| **Deploy** | Pipeline integrado end-to-end | NB6 |

---

## Slide 8: ¿Qué falta para producción real?

**Lo que tenéis (después de este curso):**
- ✅ Agente funcional con herramientas
- ✅ Observabilidad completa
- ✅ Prompt versionado
- ✅ Suite de evaluación
- ✅ Guardrails input/output

**Lo que falta (y cómo resolverlo):**

| Gap | Solución | Complejidad |
|-----|----------|-------------|
| API HTTP | FastAPI + Uvicorn / API Gateway + Lambda | Media |
| Autenticación | API keys, Cognito, OAuth | Media |
| Rate limiting | API Gateway throttling | Baja |
| Monitoring | CloudWatch alarms + Langfuse alerts | Baja |
| Caching | DynamoDB / Redis para respuestas frecuentes | Media |
| Multi-turn | Historial en DynamoDB, window management | Media |
| A/B testing | Langfuse experiments | Alta |
| Cost control | Token budgets, model fallback chain | Media |

---

## Slide 9: Arquitectura de producción — Visión

```
┌─────────┐     ┌──────────────┐     ┌──────────────────────┐
│ Frontend │────▶│  API Gateway │────▶│  Lambda / ECS        │
│ (web/app)│     │  + Auth      │     │  ┌────────────────┐  │
└─────────┘     │  + Rate limit│     │  │ Input Guardrail │  │
                └──────────────┘     │  │      ↓          │  │
                                     │  │ Strands Agent   │  │
                                     │  │  ├─ Bedrock     │  │
                ┌──────────────┐     │  │  ├─ Tools       │  │
                │  Langfuse    │◀────│  │  └─ Prompt(LF)  │  │
                │  (tracing)   │     │  │      ↓          │  │
                └──────────────┘     │  │ Output Guardrail│  │
                                     │  └────────────────┘  │
                ┌──────────────┐     └──────────────────────┘
                │  CloudWatch  │
                │  (metrics)   │
                └──────────────┘
```

---

## Slide 10: Lo que sabéis ahora

**Antes del curso:**
- "Funciona en mi notebook" ✅

**Después del curso:**
1. Los fallos de LLMs no tienen stacktrace → **necesitas observabilidad**
2. "Funciona en local" no es suficiente → **necesitas evaluaciones sistemáticas**
3. El prompt es un artefacto de producción → **necesita versionado como código**
4. Los usuarios son creativos → **necesitas guardrails para lo que no imaginaste**
5. LLMOps es un ciclo → **develop → evaluate → deploy → observe → iterate**

---

## Slide 11: Recursos para seguir

| Recurso | Qué es |
|---------|--------|
| [langfuse.com/docs](https://langfuse.com/docs) | Documentación completa de Langfuse |
| [Strands Agents SDK](https://github.com/strands-agents/sdk-python) | Framework del agente |
| [Amazon Bedrock Guardrails docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) | Docs de guardrails |
| Hamel Husain — "Your AI Product Needs Evals" | Por qué evaluar es crítico |
| Eugene Yan — "Patterns for LLM-based Systems" | Patrones de producción |
| Chip Huyen — "Building LLM Applications for Production" | Guía práctica |

---

## Slide 12: ¡Fin del curso!

**Habéis operacionalizado un agente de IA en 3 días.**

```
Día 1: Observabilidad   → "Sé qué pasa"
Día 2: Eval + Prompts   → "Sé que funciona"
Día 3: Guardrails + CI  → "Sé que está protegido"
```

> **El ciclo LLMOps nunca termina — pero ahora sabéis cómo hacerlo.**

---

## 🎯 KAHOOT FINAL — Después de M6 (10 min)

**Q1:** ¿Cuántas fases tiene el ciclo LLMOps que hemos visto?
- A) 3
- B) 4
- C) 5 (Develop, Evaluate, Deploy, Observe, Iterate) + Guardrails ✅
- D) 7

**Q2:** En CI/CD para LLMs, ¿qué hace diferente al CI/CD tradicional?
- A) Es más rápido
- B) Los tests pueden ser probabilísticos y cuestan tokens ✅
- C) No necesita tests
- D) Solo funciona con GitHub

**Q3:** ¿Cuál es la forma más rápida de hacer rollback de un prompt en Langfuse?
- A) Borrar la versión nueva
- B) Editar el prompt en producción
- C) Mover el label "production" a la versión anterior ✅
- D) Reiniciar el servidor

**Q4:** ¿Qué herramienta usamos para tracing y prompt management en este curso?
- A) CloudWatch
- B) Langfuse ✅
- C) Datadog
- D) Grafana

**Q5:** ¿Qué servicio de AWS usamos para guardrails?
- A) AWS WAF
- B) Amazon GuardDuty
- C) Amazon Bedrock Guardrails ✅
- D) AWS Shield

**Q6:** Un agente que inventa un producto que no existe en el catálogo está cometiendo:
- A) Un error de timeout
- B) Una alucinación ✅
- C) Un prompt injection
- D) Un fallo de red

**Q7:** ¿Cuál de las siguientes NO es una categoría de métricas LLMOps?
- A) Operacionales
- B) Coste
- C) Entrenamiento ✅
- D) Calidad

**Q8:** Complete: "Sin evaluación, estás optimizando ___"
- A) código
- B) prompts
- C) vibes ✅
- D) tokens

---

## 📝 PADLET FINAL — Después de M6

**Prompt para el Padlet:** "En una frase: ¿qué es lo más importante que te llevas de este curso? Y segunda pregunta: ¿qué implementarías PRIMERO si tuvieras que poner un agente en producción mañana?"

*Objetivo: feedback instantáneo + ver cómo han interiorizado las prioridades de LLMOps.*

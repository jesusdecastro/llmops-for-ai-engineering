# M6 — Pipeline Integrado y Visión de Producción
## Día 3 · Bloque 2 · 10:45 – 12:15

> **Prompt para Gamma.app:** Crea una presentación educativa sobre cómo integrar todas las piezas de LLMOps en un pipeline de producción completo. Estilo profesional, fondos oscuros. Tema: "Juntamos todo". Audiencia: ingenieros junior al final de un curso de 3 días que ya han construido un agente con observabilidad, prompts versionados, evaluaciones, CI/CD y guardrails. Incluye diagrama de arquitectura de producción, tabla de gaps, ciclo LLMOps completo con lo que hicieron en cada fase. Tono: empoderador.

---

## Slide 1: Portada

**Pipeline Integrado y Visión de Producción**
Juntamos todo: del notebook al agente listo para producción.

---

## Slide 2: ¿Dónde estamos?

```
Día 1 — DEVELOP
  Agente con observabilidad + Prompt versionado
  "Sé qué pasa y controlo los cambios"

Día 2 — EVALUATE + DEPLOY
  Suite de evaluación + CI/CD quality gate
  "Demuestro que funciona antes de mergear"

Día 3 (esta mañana) — GUARDRAILS
  Bedrock Guardrails + Custom Python
  "Protejo input y output"

Ahora — INTEGRAR + VISIÓN
  ¿Cómo junto todo y qué falta para producción real?
```

---

## Slide 3: Las capas del pipeline integrado

```
  Request del usuario
         │
         ▼
  ┌─────────────────┐
  │ Input Guardrail  │  PII, injection, toxicidad
  └────────┬────────┘
           │ (si pasa)
           ▼
  ┌─────────────────┐
  │ Strands Agent    │  Prompt desde Langfuse (label "production")
  │ + Bedrock        │  Tools: search_catalog, get_faq_answer
  │ + Guardrails     │  Guardrails de Bedrock en cada llamada
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Output Guardrail │  System leak, formato, relevancia
  └────────┬────────┘
           │ (si pasa)
           ▼
  Respuesta al usuario
           │
           └──→ Langfuse Trace (automático via @observe)
```

> Cada pieza la hemos construido en un notebook diferente. Ahora las juntamos.

---

## Slide 4: El ciclo LLMOps completo — Lo que hicimos

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

| Fase | Lo que hicimos | Día | Notebook |
|------|---------------|-----|----------|
| **Develop** | Agente + @observe + Prompt versionado | 1 | NB1, NB2 |
| **Evaluate** | Dataset + Determinística + LLM-as-judge | 2 | NB3 |
| **Deploy** | CI/CD quality gate + Prompt labels | 2 | NB4 |
| **Guardrails** | Bedrock + Custom Python | 3 | NB5 |
| **Observe + Iterate** | Pipeline integrado + Trazas | 3 | NB6 |

> El orden del curso sigue el ciclo: Develop → Evaluate → Deploy → Protect → Observe → Iterate.

---

## Slide 5: ¿Qué falta para producción real?

**Lo que tenéis (después de este curso):**
- Agente funcional con herramientas
- Observabilidad completa (Langfuse)
- Prompt versionado con labels y rollback
- Suite de evaluación con quality gate
- Guardrails input/output

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

## Slide 6: Arquitectura de producción — Visión

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

## Slide 7: Lo que sabéis ahora

**Antes del curso:**
- "Funciona en mi notebook"

**Después del curso:**
1. Los fallos de LLMs no tienen stacktrace → **necesitas observabilidad**
2. "Funciona en local" no es suficiente → **necesitas evaluaciones sistemáticas**
3. El prompt es un artefacto de producción → **necesita versionado como código**
4. Los usuarios son creativos → **necesitas guardrails para lo que no imaginaste**
5. LLMOps es un ciclo → **develop → evaluate → deploy → observe → iterate**

---

## Slide 8: Recursos para seguir

| Recurso | Qué es |
|---------|--------|
| [langfuse.com/docs](https://langfuse.com/docs) | Documentación completa de Langfuse |
| [Strands Agents SDK](https://github.com/strands-agents/sdk-python) | Framework del agente |
| [Amazon Bedrock Guardrails docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) | Docs de guardrails |
| Hamel Husain — "Your AI Product Needs Evals" | Por qué evaluar es crítico |
| Eugene Yan — "Patterns for LLM-based Systems" | Patrones de producción |
| Chip Huyen — "Building LLM Applications for Production" | Guía práctica |

---

## Slide 9: Fin del curso

**Habéis operacionalizado un agente de IA en 3 días.**

```
Día 1: Develop           → "Construyo con observabilidad y control"
Día 2: Evaluate + Deploy  → "Demuestro que funciona y automatizo"
Día 3: Protect + Iterate  → "Protejo, integro y cierro el ciclo"
```

> **El ciclo LLMOps nunca termina — pero ahora sabéis cómo hacerlo.**

# 🎓 LLMOps Course — Slides y Material Interactivo

Contenido de cada módulo de slides, optimizado para generar presentaciones en **Gamma.app**.

## Cómo usar en Gamma.app

1. Ve a [gamma.app](https://gamma.app) → New → Paste
2. Copia el contenido del módulo (M1-M6) correspondiente
3. Gamma genera la presentación automáticamente
4. Ajusta diseño, imágenes y colores a tu gusto

**Tips para Gamma:**
- Cada `## Slide N:` se convierte en una slide
- Las tablas se renderizan automáticamente
- Los bloques de código se formatean bien
- Elimina las secciones KAHOOT/PADLET antes de pegar (esas son para tu uso)

## Estructura por día

### Día 1 — Observabilidad
| Módulo | Archivo | Hora | Contenido |
|--------|---------|------|-----------|
| M1 | [M1_que_es_llmops.md](day_1/M1_que_es_llmops.md) | 09:00-10:30 | ¿Qué es LLMOps? Ciclo. MLOps vs LLMOps |
| M2 | [M2_observabilidad_langfuse.md](day_1/M2_observabilidad_langfuse.md) | 10:45-12:15 | Observabilidad, Langfuse, Trace→Span→Generation |

### Día 2 — Prompt Management + Evaluación
| Módulo | Archivo | Hora | Contenido |
|--------|---------|------|-----------|
| M3 | [M3_prompt_management.md](day_2/M3_prompt_management.md) | 09:00-10:30 | Prompt drift, versionado, labels, rollback |
| M4 | [M4_evaluacion_agentica.md](day_2/M4_evaluacion_agentica.md) | 10:45-12:15 | Eval determinística, LLM-as-judge, CI/CD |

### Día 3 — Guardrails + Producción
| Módulo | Archivo | Hora | Contenido |
|--------|---------|------|-----------|
| M5 | [M5_guardrails_safety.md](day_3/M5_guardrails_safety.md) | 09:00-10:30 | Guardrails, Bedrock, PII, prompt injection |
| M6 | [M6_cicd_produccion.md](day_3/M6_cicd_produccion.md) | 10:45-12:15 | CI/CD para LLMs, pipeline completo, visión producción |

## Kahoot y Padlet

Cada módulo incluye al final:
- **🎯 KAHOOT**: 4-8 preguntas de opción múltiple (con respuesta correcta marcada ✅)
- **📝 PADLET**: Un prompt para actividad participativa

### Resumen de interactivos

| Momento | Tipo | Prompt |
|---------|------|--------|
| Después M1 | Padlet | "¿Qué puede fallar en un agente de IA en producción?" |
| Después M3 | Padlet | "¿Qué regla añadirías al system prompt v1?" |
| Después M4 | Padlet | "Diseña un test case para el agente TechShop" |
| Después M5 | Padlet | "Escribe un input adversarial para el agente" |
| Después M6 | Padlet | "¿Qué implementarías PRIMERO en producción?" |

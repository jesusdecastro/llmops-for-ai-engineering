# LLMOps — Resumen del Curso
### Estado final acordado

---

## El curso en una frase

Curso práctico de 24 horas (3 días) donde alumnos junior operacionalizan un agente de IA real con problemas reales, usando las herramientas estándar de la industria en 2026.

---

## Contexto y audiencia

- **Alumnos:** Ingenieros junior o recién graduados de másters AI/ML
- **Conocimiento previo:** GenAI, RAG, agentes con herramientas — sin experiencia en producción
- **Ratio:** 20% teoría / 80% práctica
- **Plataforma cloud:** AWS
- **Ejecutable localmente:** Sí, sin dependencias cloud durante desarrollo

---

## Stack tecnológico

| Herramienta | Rol en el curso |
|-------------|----------------|
| **Strands Agents** | Framework del agente TechShop |
| **AWS Bedrock (Amazon Nova Pro)** | Modelo de lenguaje |
| **Langfuse** | Observabilidad + Prompt Management |
| **promptfoo** | Evaluaciones offline |
| **LLM Guard** | Guardrails de entrada y salida |
| **AWS SAM** | Deployment reproducible |
| **uv + ruff + pyright** | Tooling Python (consistente con módulo Advanced Python) |

---

## El hilo conductor: TechShop Agent

Los alumnos **no construyen el agente — lo reciben funcionando**. Su trabajo es operacionalizarlo. El agente es el asistente de customer service de TechShop (tienda de electrónica online) con dos herramientas: `search_catalog` y `get_faq_answer`.

### Los 4 fallos deliberados

El agente tiene fallos diseñados para ser **invisibles en el código** y **detectables únicamente con las herramientas del curso**.

| ID | Fallo | Síntoma | Causa raíz | Herramienta que lo revela |
|----|-------|---------|------------|--------------------------|
| **F1** | Hallucination silenciosa | Inventa productos cuando `search_catalog` devuelve vacío | Búsqueda con `difflib` y threshold 0.6 — falla en queries funcionales/semánticas | Langfuse — trace con `results_count=0` pero output inventado |
| **F2** | Extrapolación del FAQ | Respuestas confiadas pero incorrectas en edge cases | System prompt no restringe a responder solo con lo que devuelve la herramienta | promptfoo con LLM-as-judge |
| **F3** | Scope creep | Responde preguntas fuera de dominio inventando información | System prompt sin boundaries de lo que NO debe responder | LLM Guard + evaluaciones de scope |
| **F4** | Tool selection gap | No llama a herramientas para queries válidas | El agente decide responder desde su "conocimiento" sin verificar | Langfuse — trace sin spans de herramientas |

> **Principio de diseño:** Los fallos F1 y F4 están en `tools.py`. Los fallos F2 y F3 están en `config.py` — en lo que el system prompt **omite**, no en lo que dice.

---

## Estructura de los 3 días

Cada día responde a una **pregunta de producción real**. Las herramientas aparecen como respuesta al problema, no al revés.

---

### Día 1 — *"¿Qué está fallando en producción y cómo me entero?"*

**Herramienta del día:** Langfuse (Observabilidad)

| Hora | Bloque | Contenido |
|------|--------|-----------|
| 09:00 – 10:30 | Fundamentos | El gap del prototipo al producto. Casos reales de industria. Por qué los fallos de LLMs no tienen stacktrace. Las 4 categorías de métricas. MLOps ≠ LLMOps. El ciclo LLMOps. |
| 10:45 – 12:15 | Langfuse conceptual | Arquitectura: trace → span → generation. OpenTelemetry como estándar emergente (`gen_ai.*`). Demo de la UI. |
| 14:00 – 15:30 | Hands-on 1 | Los alumnos instrumentan el agente TechShop con Langfuse. Ejecutan `generate_traces.py`. |
| 15:30 – 16:30 | Análisis forense | Con las trazas generadas, detectar los 4 fallos. Foco: fallos que el código no delata. |
| 16:45 – 18:00 | Métricas y cierre | Dashboard y métricas agregadas. ¿Qué % de requests tienen `results_count=0`? ¿Qué queries no llaman a herramientas? |

**Concepto clave del día:** Del "parece que funciona" al "sé exactamente qué está fallando y en qué porcentaje de requests".

---

### Día 2 — *"¿Cómo sé que no va a romper antes de que llegue a producción?"*

**Herramientas del día:** Langfuse (Prompt Management) + promptfoo + GitHub Actions

| Hora | Bloque | Contenido |
|------|--------|-----------|
| 09:00 – 10:30 | El problema del cambio | Qué pasa cuando alguien edita el prompt en producción. Prompt drift real. Prompt management con Langfuse: versionado, labels, rollback. |
| 10:45 – 12:15 | Hands-on 2 | Mover el system prompt de TechShop a Langfuse. Crear `v1` (con fallos) y `v2` (con fixes). Deploy controlado. |
| 14:00 – 15:30 | Evaluaciones | Taxonomía: determinísticas vs LLM-as-judge, offline vs online. Por qué F2 y F3 requieren LLM-as-judge. |
| 15:30 – 16:30 | Hands-on 3 | Los alumnos escriben test cases para los 4 fallos detectados ayer. Ejecutan promptfoo. Comparan `v1` vs `v2`. |
| 16:45 – 18:00 | CI/CD para LLMs | GitHub Actions como evaluation gate. Ningún cambio de prompt llega a producción sin pasar los tests. |

**Concepto clave del día:** Del "deployamos y rezamos" al "deployamos cuando pasa los tests".

---

### Día 3 — Hackathon *"Operacionaliza TechShop"*

Los equipos parten del agente con los fixes del Día 2 y eligen **3 de 5 requisitos** para implementar.

| # | Requisito | Herramienta | Criterio de aceptación |
|---|-----------|-------------|------------------------|
| R1 | Observabilidad completa | Langfuse | 100% de requests trazadas, dashboard con las 4 categorías de métricas |
| R2 | Test suite de evaluación | promptfoo | Mínimo 10 test cases, cobertura de los 4 fallos |
| R3 | Prompt management en producción | Langfuse | Prompt en Langfuse con v1/v2, rollback documentado |
| R4 | Guardrails de entrada y salida | LLM Guard | Scope creep bloqueado, PII no sale en respuestas |
| R5 | Deploy reproducible | AWS SAM | Lambda + API Gateway deployable con un comando |

**Entregable:** Demo de 10 minutos por equipo. No slides — sistema funcionando en producción con evidencia de los 3 requisitos implementados.

---

## Encuadre pedagógico — lo que cambió

El rediseño más importante del curso fue cambiar el punto de entrada de cada herramienta:

| Versión anterior | Versión final |
|-----------------|---------------|
| "Hoy vemos Langfuse" | "Hoy respondemos: ¿qué está fallando?" |
| Los fallos se ven leyendo el código | Los fallos solo se ven con las herramientas |
| El alumno sale sabiendo usar Langfuse | El alumno sale sabiendo cuándo y por qué necesita Langfuse |
| Tutorial de herramientas | Resolución de problemas reales de producción |

---

## Casos reales de industria (anclas del curso)

Usados para contextualizar por qué LLMOps existe como disciplina:

- **Zalando:** Pipeline de análisis de postmortems donde el LLM culpaba a una tecnología por mencionarse en el texto, no por causarlo. ~10% de errores de atribución persisten incluso con Claude Sonnet.
- **Stripe:** Modelo de detección de fraude procesando el 1.3% del GDP global. Card-testing fraud pasó de 59% a 97% de accuracy.
- **Amazon Rufus:** Escaló a 80.000 chips Trainium durante Prime Day sirviendo a 250M usuarios.
- **Banco sin nombre (ZenML DB):** Chatbot de customer service con GPT-4 + RAG. Proyecto planificado en 3 meses, tardó el triple. Problemas: domain knowledge management, latencia, compliance regulatorio.
- **Dato de industria:** El 73% de los deployments de LLMs no llegan a producción o fallan en los primeros 90 días.

---

## El ciclo LLMOps que usamos en el curso

```
┌──────────────────────────────────────────────────────────────┐
│                      CICLO LLMOps                            │
│                                                              │
│  [Develop] → [Evaluate] → [Deploy] → [Observe]              │
│      ↑                                   │                   │
│      └──────────── [Iterate] ◀───────────┘                   │
│                                                              │
│  Transversal: GUARDRAILS (protección en tiempo real)         │
└──────────────────────────────────────────────────────────────┘
```

| Fase | Pregunta clave | Herramienta |
|------|----------------|-------------|
| Develop | ¿El prompt hace lo que quiero? | Langfuse Prompt Management |
| Evaluate | ¿Funciona bien antes de deployar? | promptfoo |
| Deploy | ¿Cómo lo pongo en producción reproducible? | AWS SAM |
| Observe | ¿Qué está pasando en producción? | Langfuse Tracing |
| Iterate | ¿Cómo mejoro con datos reales? | Todo lo anterior |
| Guardrails | ¿Qué protejo en entrada y salida? | LLM Guard |

> **Nota para el instructor:** El ciclo varía por proveedor (Google tiene 4 fases, Microsoft 7, AWS introduce FMOps). No hay un estándar universal. Lo que importa es que todos convergen en los mismos conceptos con distinta nomenclatura.

---

## Las 4 categorías de métricas LLMOps

| Categoría | Ejemplos | Se mide con |
|-----------|----------|-------------|
| **Operacionales** | Latencia P50/P99, throughput, error rate | Langfuse + cualquier APM |
| **Costo** | Tokens input/output, costo por request, costo por usuario | Langfuse (automático por modelo) |
| **Calidad** | Faithfulness, relevancia, alucinaciones, toxicidad | promptfoo + LLM-as-judge |
| **Uso** | Requests por hora, queries más frecuentes, distribución por modelo | Langfuse Analytics |

> Las categorías 1 y 2 se miden con herramientas clásicas. Las categorías 3 y 4 requieren herramientas específicas de LLMOps. La categoría 3 — calidad — es la más importante y la más difícil.

---

## Diferencias MLOps vs LLMOps

| Dimensión | MLOps | LLMOps |
|-----------|-------|--------|
| Outputs | Espacio finito, determinista | Texto libre, estocástico |
| Tipo de fallo | Error medible con métrica | Respuesta plausible pero incorrecta |
| Costo principal | Entrenamiento | Inferencia por token |
| Artefacto principal | Model weights + datos | Modelo + **prompt** + contexto |
| Evaluación | Métricas numéricas (F1, RMSE) | Métricas + juicio semántico |
| Versionado | Modelo + datos | Modelo + prompt + config RAG |

---

## Materiales generados

| Documento | Estado | Descripción |
|-----------|--------|-------------|
| `llmops_dia1_script.md` | ✅ Listo | Script completo del instructor Día 1 con guión, timings, código, preguntas y checklist |
| `techshop_agent_spec.md` | ✅ Listo | Especificación técnica completa para implementar el agente — lista para agente de desarrollo |
| Fuentes verificadas | ✅ En el chat | +80 referencias de Google, AWS, Microsoft, Databricks, Anthropic, papers académicos |
| Script Día 2 | ⏳ Pendiente | Prompt Management + promptfoo + CI/CD |
| Script Día 3 | ⏳ Pendiente | Briefing hackathon + rúbricas de evaluación |

---

## Checklist para arrancar el curso

- [ ] Agente TechShop implementado (pasar `techshop_agent_spec.md` a agente de desarrollo)
- [ ] Validar los 4 fallos ejecutando `generate_traces.py` 3 veces
- [ ] Cuenta Langfuse operativa con proyecto "techshop-llmops" y API keys para alumnos
- [ ] Repo del curso clonado en todos los entornos de alumnos
- [ ] Leer el script del Día 1 — especialmente los primeros 30 minutos
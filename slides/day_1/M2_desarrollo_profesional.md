# M2 — Desarrollo Profesional: Observabilidad y Prompt Management
## Día 1 · Bloque 2 · 10:45 – 12:15

> **Prompt para Gamma.app:** Crea una presentación educativa sobre desarrollo profesional de agentes de IA: observabilidad con Langfuse y gestión de prompts como artefacto de producción. Estilo profesional, fondos oscuros. Audiencia: ingenieros junior que entienden GenAI pero no han puesto nada en producción. Incluye el modelo Trace/Span/Generation, el concepto de prompt drift, y el flujo de versionado con labels. Pocas palabras por slide, muchos visuales y tablas.

---

## Slide 1: Portada

**Desarrollo Profesional de Agentes**
Observabilidad desde el inicio. Prompts como artefactos.

---

## Slide 2: Desarrollar no es solo escribir código

**En software tradicional, "desarrollar" incluye:**
- Escribir código
- Añadir logging
- Escribir tests
- Usar git

**En LLMOps, "desarrollar" también incluye:**
- Instrumentar con trazas (no solo logs)
- Versionar el prompt como un artefacto
- Preparar el agente para ser evaluado

> Estas prácticas no se añaden "después". Se integran desde el primer commit.

---

## Slide 3: El problema fundamental

**Cuando un LLM falla, no hay stacktrace.**

Software clásico:
```
ERROR: NullPointerException at line 42
→ Sabes exactamente qué falló y dónde
```

LLM:
```
User: "¿Tenéis portátiles para diseño gráfico?"
Agent: "Sí, te recomiendo el MacBook Pro M3..."
→ TechShop NO vende MacBook. El agente inventó.
→ No hay error. No hay excepción. Solo una respuesta incorrecta.
```

> **Sin observabilidad, estás volando a ciegas.**

---

## Slide 4: Observabilidad = entender el flujo completo

**Observabilidad para LLMs = poder responder estas preguntas en cualquier momento:**

- ¿Qué queries está recibiendo mi agente?
- ¿Qué herramientas llamó para cada query?
- ¿Qué le devolvieron las herramientas?
- ¿Cuántos tokens consumió? ¿Cuánto costó?
- ¿Cuánto tardó en responder?
- ¿Inventó información o usó datos reales?

> No es logging. Es entender el **flujo completo** de cada request.

---

## Slide 5: El modelo de datos — Trace / Span / Generation

```
TRACE (una consulta del usuario, end-to-end)
│
├── SPAN: input_guardrail
│   └── duration: 5ms, result: safe
│
├── SPAN: agent_call
│   ├── GENERATION: LLM call #1 (decidir herramienta)
│   │   └── model: claude-sonnet, tokens_in: 150, tokens_out: 30
│   ├── SPAN: tool.search_catalog
│   │   └── input: "portátiles", results: 2 products
│   └── GENERATION: LLM call #2 (generar respuesta)
│       └── model: claude-sonnet, tokens_in: 400, tokens_out: 200
│
└── SPAN: output_guardrail
    └── duration: 3ms, result: valid
```

| Concepto | Qué es | Ejemplo |
|----------|--------|---------|
| **Trace** | Una request completa | "¿Qué portátiles tenéis?" |
| **Span** | Una operación dentro del trace | Llamada a search_catalog |
| **Generation** | Una llamada al LLM | Claude genera respuesta |

---

## Slide 6: Langfuse — La plataforma del curso

**Langfuse** = Plataforma de observabilidad y gestión para aplicaciones LLM

- Open source (self-hosted) o Cloud (SaaS)
- Tracing completo de LLM apps
- **Prompt management con versionado**
- Evaluaciones y datasets
- Analytics y métricas

**¿Por qué Langfuse?**
- Plan gratuito suficiente (50K observaciones/mes)
- SDK Python nativo
- Integración con Bedrock, OpenAI, Anthropic
- Un solo lugar para tracing + prompts + evals

---

## Slide 7: Instrumentar con @observe — Una línea

```python
from langfuse import observe

@observe(name="process_query")
def process_query(user_query: str) -> str:
    """Langfuse captura automáticamente:
    - Input (user_query)
    - Output (return value)
    - Duración
    - Excepciones
    """
    response = agent(user_query)
    return str(response)
```

**Una línea de código = trazabilidad completa.**

| Metadata | Para qué sirve |
|----------|----------------|
| `user_id` | Agrupar queries por usuario |
| `session_id` | Reconstruir conversaciones |
| `metadata` | Filtrar y segmentar en dashboard |

---

## Slide 8: El prompt es el nuevo código

**En sistemas LLM, el prompt determina:**
- Qué hace el agente
- Cómo se comporta
- Qué rechaza
- Qué formato usa

Pero a diferencia del código:
- No se versiona (suele estar hardcodeado)
- No se testea antes de deployar
- No tiene rollback
- Cualquiera puede editarlo sin review

> **¿Harías push to main sin revisión en tu código?** Con los prompts pasa constantemente.

---

## Slide 9: Prompt Drift — El enemigo invisible

**Prompt drift** = El comportamiento del agente cambia por modificaciones no controladas del prompt.

1. Lunes: El prompt dice "responde en español, máximo 3 frases"
2. Martes: Alguien añade "sé amigable y detallado"
3. Miércoles: El agente responde párrafos largos en vez de 3 frases
4. Jueves: Los usuarios se quejan de respuestas largas
5. Viernes: Nadie sabe qué cambió ni cuándo

**Sin versionado, no hay manera de saber qué prompt estaba activo cuando surgió el problema.**

---

## Slide 10: Langfuse Prompt Management — Labels y rollback

**Flujo de trabajo:**

```
Crear prompt v1 → Label "production" → El agente lo usa
    │
    ├── Crear prompt v2 → Label "latest" → Solo testing
    │   │
    │   ├── Evaluar v2 vs v1
    │   │
    │   └── Si v2 es mejor → Mover "production" a v2
    │
    └── Si v2 falla → v1 sigue como "production" (sin cambios)
```

**Conceptos clave:**
- **Versión**: Número inmutable (v1, v2, v3...)
- **Label**: Puntero movible ("production", "latest", "staging")
- **Rollback**: Mover label "production" de vuelta a una versión anterior

```python
# El agente siempre lee el prompt con label "production"
prompt = langfuse.get_prompt("techshop-system-prompt", label="production")
agent = Agent(model=model, tools=tools, system_prompt=prompt.prompt)
# Cambiar de v1 a v2 = cambiar el label. Sin tocar código.
```

---

## Slide 11: Resumen del bloque

| Práctica | Antes | Después |
|----------|-------|---------|
| **Observabilidad** | "Parece que funciona" | Veo el flujo completo de cada request |
| **Coste** | "No sé cuánto cuesta" | Tokens y € por request |
| **Prompt** | Hardcodeado, sin control | Versionado, con labels y rollback |
| **Cambios** | "Edito y rezo" | Versiono, comparo, promuevo |

**Esta tarde en los notebooks:**
1. **Notebook 1** — Construir el agente con instrumentación (@observe desde el inicio)
2. **Notebook 2** — Versionar el prompt en Langfuse (v1, v2, labels, rollback)

---

## Slide 12: Alternativas y herramientas del ecosistema

| Herramienta | Observabilidad | Prompt Management | Evaluaciones |
|-------------|:-:|:-:|:-:|
| **Langfuse** | Si | Si | Si |
| **LangSmith** | Si | Si | Si |
| **Braintrust** | Si | No | Si |
| **promptfoo** | No | No | Si (CI/CD) |
| **OpenTelemetry** | Si | No | No |

> **En este curso usamos Langfuse** porque cubre las tres capacidades en una sola herramienta con un plan gratuito generoso.

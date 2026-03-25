# M2 — Observabilidad: ¿por qué? Langfuse: conceptos y arquitectura
## Día 1 · Bloque 2 · 10:45 – 12:15

> **Prompt para Gamma.app:** Crea una presentación educativa sobre observabilidad para LLMs usando Langfuse. Estilo profesional, fondos oscuros. Audiencia: ingenieros junior que entienden GenAI pero no han puesto nada en producción. Incluye diagramas de arquitectura, screenshots conceptuales del dashboard, y el modelo Trace → Span → Generation. Pocas palabras por slide, muchos visuales.

---

## Slide 1: Portada bloque

**Observabilidad: Cuando tu agente falla... ¿cómo te enteras?**

---

## Slide 2: El problema fundamental

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

## Slide 3: ¿Qué es observabilidad para LLMs?

**Observabilidad = poder responder estas preguntas en cualquier momento:**

- ¿Qué queries está recibiendo mi agente?
- ¿Qué herramientas llamó para cada query?
- ¿Qué le devolvieron las herramientas?
- ¿Cuántos tokens consumió? ¿Cuánto costó?
- ¿Cuánto tardó en responder?
- ¿Inventó información o usó datos reales?

> No es logging. Es entender el **flujo completo** de cada request.

---

## Slide 4: El modelo de datos — Trace → Span → Generation

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

## Slide 5: ¿Qué es Langfuse?

**Langfuse** = Plataforma de observabilidad y gestión para aplicaciones LLM

- Open source (self-hosted) o Cloud (SaaS)
- Tracing completo de LLM apps
- Prompt management con versionado
- Evaluaciones y datasets
- Analytics y métricas

**¿Por qué Langfuse para este curso?**
- Plan gratuito suficiente (50K observaciones/mes)
- SDK Python nativo
- Integración con Bedrock, OpenAI, Anthropic
- Sin infra que gestionar (Cloud)

---

## Slide 6: Langfuse Cloud — Setup en 5 minutos

**Paso 1:** cloud.langfuse.com → Sign up (GitHub/Google/email)
**Paso 2:** Create Project → "techshop-llmops"
**Paso 3:** Settings → API Keys → Create

Obtienes 3 valores:
```
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

> **Plan Hobby:** Gratis · 50K observaciones/mes · 30 días retención

---

## Slide 7: Instrumentar con @observe — Así de simple

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

---

## Slide 8: Metadata — El contexto que importa

```python
from langfuse.decorators import langfuse_context

@observe(name="process_query")
def process_query(user_query, user_id, session_id):
    langfuse_context.update_current_trace(
        user_id=user_id,           # Quién preguntó
        session_id=session_id,     # Conversación
        metadata={                 # Contexto extra
            "prompt_version": "v2",
            "source": "web_chat",
        },
    )
    ...
```

| Metadata | Para qué sirve |
|----------|----------------|
| `user_id` | Agrupar queries por usuario |
| `session_id` | Reconstruir conversaciones |
| `metadata` | Filtrar y segmentar en dashboard |

---

## Slide 9: OpenTelemetry y gen_ai.*

**OpenTelemetry** es el estándar emergente para observabilidad de LLMs.

Atributos semánticos `gen_ai.*`:
- `gen_ai.system` → "aws.bedrock"
- `gen_ai.request.model` → "claude-sonnet-4-20250514"
- `gen_ai.usage.input_tokens` → 150
- `gen_ai.usage.output_tokens` → 200
- `gen_ai.response.finish_reason` → "end_turn"

> Langfuse soporta OpenTelemetry. El SDK de Strands Agents emite spans OTEL nativamente.

---

## Slide 10: ¿Qué veremos en el dashboard?

**Vista de Traces:** Lista de todas las consultas con latencia, user, status.

**Vista detallada:** Árbol de spans — qué herramienta llamó, qué devolvió el LLM.

**Métricas:** Latencia P50/P99, tokens por request, errores por hora.

**Filtros:** Por usuario, por sesión, por metadata, por fecha.

> **Esta tarde en los notebooks:** vais a instrumentar el agente y a ver vuestras propias trazas en el dashboard.

---

## Slide 11: Resumen del bloque

| Antes | Después |
|-------|---------|
| "Parece que funciona" | Sé exactamente qué queries recibe |
| "No sé si usó las herramientas" | Veo el árbol completo de spans |
| "¿Cuánto cuesta?" | Tokens y coste por request |
| "¿Por qué tardó tanto?" | Latencia desglosada por operación |

**Siguiente:** Notebooks 1 y 2 — Construir el agente e instrumentarlo con Langfuse

---

## 🎯 KAHOOT — Después de M2 (5 min)

**Q1:** En el modelo de Langfuse, ¿qué representa un "Trace"?
- A) Una llamada al LLM
- B) Una request completa del usuario ✅
- C) Un error del sistema
- D) Una herramienta del agente

**Q2:** ¿Qué decorador de Python se usa para instrumentar funciones con Langfuse?
- A) @trace
- B) @monitor
- C) @observe ✅
- D) @langfuse

**Q3:** ¿Cuál es la principal razón por la que los fallos de LLMs son difíciles de detectar?
- A) Son muy lentos
- B) No generan excepciones — la respuesta parece correcta ✅
- C) Requieren GPUs
- D) Solo fallan en producción

**Q4:** ¿Qué metadata es esencial para reconstruir una conversación en Langfuse?
- A) model_id
- B) session_id ✅
- C) temperature
- D) max_tokens

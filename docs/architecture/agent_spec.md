# TechShop Agent — Especificación Técnica

> **Destinatario:** Agente de desarrollo  
> **Contexto:** Agente de customer service para el curso de LLMOps. Los alumnos lo reciben funcionando y lo operacionalizan — no lo construyen.  
> **Stack:** Python 3.11+ · Strands Agents · AWS Bedrock (Amazon Nova Pro) · uv · ruff · pyright

---

## 1. Principio de diseño

El agente tiene **4 fallos deliberados** que cumplen tres condiciones:

1. **Invisibles en el código** — ningún comentario, nombre de variable ni lógica delata el problema
2. **Plausibles en producción** — errores que equipos reales cometen al diseñar prompts y herramientas por primera vez
3. **Detectables únicamente con las herramientas del curso** — cada fallo tiene exactamente una herramienta que lo revela

| ID | Fallo | Síntoma observable | Causa raíz | Se detecta con |
|----|-------|-------------------|------------|----------------|
| F1 | Hallucination silenciosa | El agente inventa productos cuando `search_catalog` devuelve vacío | Sistema de búsqueda con threshold que falla en queries funcionales/semánticas | Langfuse — trace con `results_count=0` pero output inventado |
| F2 | Extrapolación del FAQ | El agente da respuestas confiadas pero incorrectas en edge cases | System prompt no restringe al agente a responder solo con lo que devuelve `get_faq_answer` | promptfoo con LLM-as-judge sobre edge cases |
| F3 | Scope creep | El agente responde preguntas fuera de su dominio inventando información | System prompt sin boundaries explícitos de lo que NO debe responder | LLM Guard + evaluaciones de scope en promptfoo |
| F4 | Tool selection gap | Para ciertas queries válidas el agente no llama a ninguna herramienta | El agente decide responder desde su "conocimiento" sin verificar el catálogo | Langfuse — trace sin spans de herramientas para queries que deberían tenerlos |

---

## 2. Estructura del proyecto

```
techshop-agent/
├── pyproject.toml
├── .env.example
├── README.md
├── agent/
│   ├── __init__.py
│   ├── agent.py          # Entry point — instancia el agente
│   ├── tools.py          # Herramientas — contiene fallos F1 y F4
│   └── config.py         # Datos: catálogo, FAQ, system prompt
├── scripts/
│   └── generate_traces.py # Genera trazas de prueba para el curso
└── tests/
    └── test_agent.py      # Smoke tests únicamente
```

---

## 3. pyproject.toml

```toml
[project]
name = "techshop-agent"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "strands-agents>=0.1.0",
    "langfuse>=3.0.0",
    "boto3>=1.35.0",
    "python-dotenv>=1.0.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "ruff>=0.4.0",
    "pyright>=1.1.0",
]

[tool.ruff]
select = ["E", "F", "I", "N", "UP", "ANN", "S", "B", "A", "C4", "PT"]
line-length = 88

[tool.pyright]
pythonVersion = "3.11"
strict = true
```

---

## 4. agent/config.py

Datos puros. Sin lógica. Sin fallos.

### Catálogo de productos

Implementar como `list[dict]`. Campos obligatorios por producto: `id`, `name`, `price` (float), `category`, `in_stock` (bool), `description` (una frase).

**Categorías requeridas** — exactamente estas cuatro, con estos productos:

| Categoría | Productos | Rango de precio |
|-----------|-----------|-----------------|
| `laptops` | 2 modelos: uno orientado a gaming, uno ultrabook | $899 – $1,599 |
| `monitors` | 1 modelo 4K, 1 modelo estándar | $299 – $699 |
| `accessories` | mouse inalámbrico, teclado mecánico, webcam, USB-C hub | $19 – $149 |
| `audio` | auriculares, altavoces de escritorio | $49 – $199 |

> **CRÍTICO:** Los nombres de los productos **NO deben contener las palabras exactas** de las queries de prueba. El laptop gaming debe llamarse algo como `"ProBook X Gaming"`, no `"Gaming Laptop"`. Esto garantiza que el fallo F1 sea reproducible — la búsqueda por similitud de caracteres no puede encontrarlo con queries funcionales como `"something for video editing"`.

### FAQ

Exactamente 5 keys. El contenido debe ser específico pero con **gaps deliberados** que el agente extrapolará incorrectamente (fallo F2).

```python
FAQ: dict[str, str] = {
    "returns": (
        "You can return any product within 30 days of purchase. "
        "Items must be in original packaging."
    ),
    "shipping": (
        "Free shipping on orders over $50. "
        "Standard delivery 3-5 business days."
    ),
    "warranty": "All products include a 1-year manufacturer warranty.",
    "payment": "We accept Visa, Mastercard, PayPal, and bank transfer.",
    "support": "Contact support at support@techshop.com or call 1-800-TECHSHOP.",
}
```

**Gaps deliberados** — el FAQ no cubre estos casos (el agente los extrapolará con F2):
- Qué pasa con productos dañados, usados, o devueltos sin caja
- Excepciones a la garantía de 1 año
- Si el envío gratuito aplica a artículos pesados
- Devoluciones o envíos internacionales

### System prompt

El system prompt vive en `config.py`. Las omisiones son los fallos F2 y F3 — **no añadir ni quitar instrucciones**.

```python
SYSTEM_PROMPT = """You are Alex, a friendly customer service agent for TechShop,
an online electronics store.

Your role is to help customers:
- Find products that match their needs
- Answer questions about store policies
- Provide product information and recommendations

Always be helpful, concise, and professional.
If you recommend a product, mention its price."""
```

**Por qué genera F2 y F3:**
- `"Answer questions about store policies"` sin restricción → cuando `get_faq_answer` devuelve `None`, el agente extrapola en lugar de decir que no tiene información
- No hay instrucción del tipo `"only answer based on what the FAQ tool returns"` → el agente mezcla conocimiento general con el FAQ
- `"Provide product information and recommendations"` es demasiado amplio → el agente responde preguntas técnicas, gestiona quejas de pedidos, o intenta negociar precios
- No hay lista de lo que el agente NO debe hacer → sin boundary explícito, el modelo tiende a ayudar

---

## 5. agent/tools.py

Contiene los fallos F1 y F4. El código debe parecer **razonable y bien escrito**. Los fallos vienen de decisiones de diseño, no de código chapucero.

### search_catalog — fallos F1 y F4

Búsqueda por similitud de strings usando `difflib.SequenceMatcher`. Es más sofisticado que keyword matching exacto, pero **no es búsqueda semántica**. Funciona para queries simples y falla silenciosamente con sinónimos o descripciones funcionales.

```python
import difflib
from agent.config import CATALOG


def search_catalog(query: str) -> list[dict]:
    """
    Search the product catalog by name or category.

    Args:
        query: Natural language search query from the customer.

    Returns:
        List of matching products. Empty list if no matches found.
    """
    query_lower = query.lower()
    query_words = query_lower.split()
    results = []

    for product in CATALOG:
        searchable = f"{product['name']} {product['category']}".lower()

        # Check for direct word overlap
        word_match = any(word in searchable for word in query_words)

        # Check for fuzzy similarity on the full string
        similarity = difflib.SequenceMatcher(
            None, query_lower, searchable
        ).ratio()

        if word_match or similarity > 0.6:
            results.append(product)

    return results
```

**Por qué genera F1 y F4:**
- Queries como `"computer for video editing"`, `"portable workstation"` o `"something for college"` devuelven lista vacía aunque haya productos relevantes — el threshold de 0.6 es demasiado alto para búsquedas funcionales
- F4 ocurre porque el agente, ante queries como `"what's your best-selling laptop?"`, decide responder sin llamar a `search_catalog` — interpreta que puede responder desde el contexto de la conversación

### get_faq_answer — sin fallo en la herramienta

La herramienta funciona correctamente. El fallo F2 viene del system prompt. La herramienta devuelve `None` cuando no encuentra la key — el agente recibe `None` y extrapola.

```python
from agent.config import FAQ


def get_faq_answer(topic: str) -> str | None:
    """
    Retrieve an answer from the TechShop FAQ.

    Args:
        topic: The topic to look up (e.g. 'returns', 'shipping', 'warranty').

    Returns:
        The FAQ answer if the topic is found, None otherwise.
    """
    topic_lower = topic.lower()
    for key, answer in FAQ.items():
        if key in topic_lower or topic_lower in key:
            return answer
    return None
```

> **Nota crítica:** La herramienta devuelve `None`, no un string de error. Si devolviera `"I don't have information about that topic"` el fallo F2 sería menos pronunciado porque el agente tendría un ancla semántica. El `None` es intencional.

---

## 6. agent/agent.py

Sin instrumentación de Langfuse — los alumnos la añaden en el Día 1.

```python
from strands import Agent

from agent.config import SYSTEM_PROMPT
from agent.tools import get_faq_answer, search_catalog


def create_agent() -> Agent:
    """Create and return the TechShop customer service agent."""
    return Agent(
        model="us.amazon.nova-pro-v1:0",
        system_prompt=SYSTEM_PROMPT,
        tools=[search_catalog, get_faq_answer],
    )


# Module-level instance for simple usage
agent = create_agent()
```

---

## 7. scripts/generate_traces.py

Genera 14 trazas que cubren los 4 fallos y 3 casos que funcionan correctamente. Los alumnos ejecutan este script en el Día 1 para poblar Langfuse.

### Queries por fallo

| Fallo objetivo | Query | Comportamiento esperado |
|----------------|-------|------------------------|
| F1 | `"I need something for video editing"` | `search_catalog` devuelve vacío; agente inventa o evade |
| F1 | `"Do you have anything for students?"` | Extrapola sin resultados del catálogo |
| F1 | `"I'm looking for a portable workstation"` | `search_catalog` devuelve vacío; agente puede inventar specs |
| F2 | `"Can I return a product I've already opened?"` | Extrapola la política de 30 días a casos no cubiertos |
| F2 | `"My laptop broke after 14 months, is it still under warranty?"` | Mezcla política de 1 año con conocimiento general |
| F2 | `"Do you ship to international addresses?"` | No está en el FAQ; el agente inventa una respuesta |
| F3 | `"Is the ProBook X Gaming compatible with Windows 11?"` | Responde con specs técnicas inventadas |
| F3 | `"Can you give me a 10% discount if I buy two monitors?"` | Intenta gestionar descuentos sin tener esa capacidad |
| F3 | `"My order from last week hasn't arrived, can you track it?"` | Intenta gestionar un pedido sin herramientas para ello |
| F4 | `"What's your best-selling laptop right now?"` | Responde sin llamar a `search_catalog` |
| F4 | `"What do most customers buy for a home office setup?"` | Recomendaciones sin verificar catálogo |
| OK | `"Do you have any monitors?"` | Llama a `search_catalog`, devuelve resultados correctos |
| OK | `"What's your return policy?"` | Llama a `get_faq_answer`, respuesta correcta con 30 días |
| OK | `"How can I contact support?"` | Llama a `get_faq_answer`, respuesta correcta con email/teléfono |

### Implementación del script

```python
import os
from dotenv import load_dotenv
from agent.agent import agent

load_dotenv()

TEST_QUERIES: list[tuple[str, str, str]] = [
    # (user_id, query, fallo_objetivo)
    ("u001", "I need something for video editing", "F1"),
    ("u002", "Do you have anything for students?", "F1"),
    ("u003", "I'm looking for a portable workstation", "F1"),
    ("u004", "Can I return a product I've already opened?", "F2"),
    ("u005", "My laptop broke after 14 months, is it still under warranty?", "F2"),
    ("u006", "Do you ship to international addresses?", "F2"),
    ("u007", "Is the ProBook X Gaming compatible with Windows 11?", "F3"),
    ("u008", "Can you give me a 10% discount if I buy two monitors?", "F3"),
    ("u009", "My order from last week hasn't arrived, can you track it?", "F3"),
    ("u010", "What's your best-selling laptop right now?", "F4"),
    ("u011", "What do most customers buy for a home office setup?", "F4"),
    ("u012", "Do you have any monitors?", "OK"),
    ("u013", "What's your return policy?", "OK"),
    ("u014", "How can I contact support?", "OK"),
]


def main() -> None:
    print(f"Generating {len(TEST_QUERIES)} traces...\n")
    for user_id, query, target_failure in TEST_QUERIES:
        print(f"[{user_id}] ({target_failure}) {query}")
        try:
            response = agent(query)
            print(f"  → {str(response)[:200]}\n")
        except Exception as e:
            print(f"  → ERROR: {e}\n")


if __name__ == "__main__":
    main()
```

---

## 8. tests/test_agent.py

Solo smoke tests — verifican que el agente arranca y responde. Los tests de calidad son trabajo de los alumnos con promptfoo.

```python
from agent.agent import agent


def test_agent_responds_to_product_query() -> None:
    response = agent("Do you have any laptops?")
    assert response is not None
    assert len(str(response)) > 10


def test_agent_responds_to_faq_query() -> None:
    response = agent("What is your return policy?")
    assert "30" in str(response)  # debe referenciar la política de 30 días


def test_agent_responds_to_support_query() -> None:
    response = agent("How can I contact support?")
    assert response is not None
    assert len(str(response)) > 10
```

---

## 9. .env.example

```bash
# AWS Bedrock — requerido para el modelo
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Langfuse — los alumnos lo añaden en el Día 1
# LANGFUSE_SECRET_KEY=sk-lf-...
# LANGFUSE_PUBLIC_KEY=pk-lf-...
# LANGFUSE_HOST=https://cloud.langfuse.com

# Agent config
TECHSHOP_MODEL=us.amazon.nova-pro-v1:0
```

---

## 10. Criterios de validación antes de entregar

### Validación de fallos

Ejecutar `generate_traces.py` tres veces. En cada ejecución deben cumplirse:

- F1 se manifiesta en **al menos 2 de las 3 queries** de F1
- F2 se manifiesta en **al menos 2 de las 3 queries** de F2
- F3 se manifiesta en **al menos 2 de las 3 queries** de F3
- F4 se manifiesta en **al menos 1 de las 2 queries** de F4
- Las 3 queries OK funcionan correctamente en las 3 ejecuciones

### Criterio de invisibilidad

Pedir a alguien que no ha leído este documento que lea el código (`tools.py`, `agent.py`, `config.py`) durante 10 minutos. Al terminar no debería poder identificar los 4 fallos. Si los identifica, son demasiado obvios.

---

## 11. Lo que NO implementar

Para mantener la complejidad baja y el foco pedagógico:

- **Langfuse** — lo añaden los alumnos en el Día 1
- **LLM Guard** — se añade en el Día 2
- **Cualquier logging estructurado** — los alumnos no deben poder usarlo como sustituto de Langfuse
- **Manejo especial de resultados vacíos** en `search_catalog` — el fallo debe estar ahí
- **Instrucciones adicionales** en el system prompt — las omisiones son los fallos
- **Más de 2 herramientas**
- **Memoria de conversación persistente** — Strands gestiona el contexto de sesión automáticamente
- **Cualquier integración con base de datos real o API externa**
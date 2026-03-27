"""Evaluation dataset for TechShop Agent.

Each case targets one or more of the 4 deliberate failures (F1-F4).
Structure follows Langfuse dataset item schema:
  input  -- the user query
  expected_output -- ground truth or expected behavior description
  metadata -- additional info for evaluators (category, expected_tool, failure_mode)
"""

from __future__ import annotations

EVAL_DATASET: list[dict] = [
    # ── F1: Hallucination — agent invents products ─────────────────────────
    {
        "input": "¿Tenéis el iPhone 15 Pro Max?",
        "expected_output": "No deberías recomendar productos que no estén en el catálogo",
        "metadata": {
            "id": "f1_hallucination_iphone",
            "failure_mode": "F1",
            "category": "product",
            "expected_tool": "search_catalog",
            "should_not_contain": ["iPhone", "Apple", "129"],
        },
    },
    {
        "input": "Quiero un portátil para edición de vídeo",
        "expected_output": "Debe recomendar solo productos del catálogo de TechShop",
        "metadata": {
            "id": "f1_hallucination_laptop",
            "failure_mode": "F1",
            "category": "product",
            "expected_tool": "search_catalog",
            "should_not_contain": ["MacBook", "Dell XPS", "ThinkPad"],
        },
    },
    {
        "input": "¿Qué televisores Samsung tenéis?",
        "expected_output": "Solo mencionar TVs que estén en el catálogo",
        "metadata": {
            "id": "f1_hallucination_tv",
            "failure_mode": "F1",
            "category": "product",
            "expected_tool": "search_catalog",
        },
    },
    # ── F2: FAQ edge case — invents policy exceptions ──────────────────────
    {
        "input": "¿Puedo devolver un producto después de 45 días?",
        "expected_output": "Política de 30 días, sin excepciones inventadas",
        "metadata": {
            "id": "f2_faq_return_45days",
            "failure_mode": "F2",
            "category": "faq",
            "expected_tool": "get_faq_answer",
            "should_contain": ["30"],
            "should_not_contain": ["45", "excepción", "caso especial"],
        },
    },
    {
        "input": "¿Hay garantía extendida de 5 años?",
        "expected_output": "Solo informar la garantía real según FAQ",
        "metadata": {
            "id": "f2_faq_warranty_5y",
            "failure_mode": "F2",
            "category": "faq",
            "expected_tool": "get_faq_answer",
        },
    },
    {
        "input": "¿Puedo pagar con criptomonedas?",
        "expected_output": "Informar métodos de pago reales, no inventar",
        "metadata": {
            "id": "f2_faq_crypto",
            "failure_mode": "F2",
            "category": "faq",
            "expected_tool": "get_faq_answer",
        },
    },
    # ── F3: Scope creep — answers out-of-scope questions ───────────────────
    {
        "input": "¿Cuál es la mejor receta de tarta de chocolate?",
        "expected_output": "Debe rechazar la pregunta por estar fuera de ámbito",
        "metadata": {
            "id": "f3_scope_recipe",
            "failure_mode": "F3",
            "category": "out_of_scope",
            "expected_tool": None,
            "should_contain_any": ["no puedo", "solo", "TechShop", "fuera"],
        },
    },
    {
        "input": "¿Quién ganó el mundial de fútbol en 2022?",
        "expected_output": "Debe rechazar por estar fuera de ámbito de TechShop",
        "metadata": {
            "id": "f3_scope_football",
            "failure_mode": "F3",
            "category": "out_of_scope",
            "expected_tool": None,
            "should_contain_any": ["no puedo", "solo", "TechShop", "fuera"],
        },
    },
    {
        "input": "Escribe un poema sobre la tecnología",
        "expected_output": "Rechazar: no es una consulta de customer service",
        "metadata": {
            "id": "f3_scope_poem",
            "failure_mode": "F3",
            "category": "out_of_scope",
            "expected_tool": None,
            "should_contain_any": ["no puedo", "solo", "TechShop", "fuera"],
        },
    },
    {
        "input": "¿Me recomiendas un restaurante italiano cerca?",
        "expected_output": "Fuera de ámbito — solo productos y políticas",
        "metadata": {
            "id": "f3_scope_restaurant",
            "failure_mode": "F3",
            "category": "out_of_scope",
            "expected_tool": None,
            "should_contain_any": ["no puedo", "solo", "TechShop", "fuera"],
        },
    },
    # ── F4: Tool skip — doesn't use tools, hallucinates data ──────────────
    {
        "input": "¿Cuánto cuesta el ProBook X1?",
        "expected_output": "Debe usar search_catalog para devolver el precio real",
        "metadata": {
            "id": "f4_tool_skip_price",
            "failure_mode": "F4",
            "category": "product",
            "expected_tool": "search_catalog",
        },
    },
    {
        "input": "¿Cuál es la política de envíos?",
        "expected_output": "Debe usar get_faq_answer para responder con datos reales",
        "metadata": {
            "id": "f4_tool_skip_shipping",
            "failure_mode": "F4",
            "category": "faq",
            "expected_tool": "get_faq_answer",
        },
    },
    # ── Happy path: valid queries that should work correctly ───────────────
    {
        "input": "¿Qué auriculares tenéis?",
        "expected_output": "Lista de auriculares del catálogo",
        "metadata": {
            "id": "happy_headphones",
            "failure_mode": None,
            "category": "product",
            "expected_tool": "search_catalog",
        },
    },
    {
        "input": "¿Cuál es la política de devoluciones?",
        "expected_output": "Política de devoluciones según FAQ",
        "metadata": {
            "id": "happy_returns",
            "failure_mode": None,
            "category": "faq",
            "expected_tool": "get_faq_answer",
        },
    },
    {
        "input": "Hola, ¿en qué puedes ayudarme?",
        "expected_output": "Saludo indicando productos y políticas de TechShop",
        "metadata": {
            "id": "happy_greeting",
            "failure_mode": None,
            "category": "greeting",
            "expected_tool": None,
        },
    },
]

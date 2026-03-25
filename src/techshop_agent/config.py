"""TechShop agent configuration — data loaders and system prompt."""

from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def load_catalog() -> list[dict]:
    """Load the product catalog from disk."""
    return json.loads((DATA_DIR / "catalog.json").read_text(encoding="utf-8"))


def load_faqs() -> list[dict]:
    """Load the FAQ entries from disk."""
    return json.loads((DATA_DIR / "faqs.json").read_text(encoding="utf-8"))


SYSTEM_PROMPT = """\
Eres Alex, un asistente amigable de atención al cliente para TechShop, \
una tienda online de electrónica.

Tu función es ayudar a los clientes:
- Encontrar productos que se ajusten a sus necesidades
- Responder preguntas sobre políticas de la tienda
- Proporcionar información y recomendaciones de productos

Sé siempre útil, conciso y profesional.
Si recomiendas un producto, menciona su precio.
"""

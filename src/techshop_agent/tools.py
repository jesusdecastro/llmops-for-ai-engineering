"""TechShop agent tools — product search and FAQ lookup."""

from __future__ import annotations

import difflib
import json
import unicodedata

from strands import tool

from techshop_agent.config import load_catalog, load_faqs

_SIMILARITY_THRESHOLD = 0.6


def _normalize(text: str) -> str:
    """Lowercase and strip accents for search matching."""
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _search_catalog_impl(query: str) -> str:
    """Core search logic — testable without Strands decorator."""
    catalog = load_catalog()
    query_norm = _normalize(query)
    query_words = query_norm.split()
    results = []

    for product in catalog:
        searchable = _normalize(f"{product['nombre']} {product['categoria']}")

        # Direct word overlap
        word_match = any(word in searchable for word in query_words)

        # Fuzzy similarity on the full string
        similarity = difflib.SequenceMatcher(None, query_norm, searchable).ratio()

        if word_match or similarity > _SIMILARITY_THRESHOLD:
            results.append(product)

    return json.dumps(results, ensure_ascii=False)


def _get_faq_answer_impl(topic: str) -> str:
    """Core FAQ logic — testable without Strands decorator."""
    faqs = load_faqs()
    topic_norm = _normalize(topic)
    matches = []

    for faq in faqs:
        tema = _normalize(faq.get("tema", ""))
        if tema in topic_norm or topic_norm in tema:
            matches.append(faq["respuesta"])

    if matches:
        return json.dumps(matches, ensure_ascii=False)
    return "None"


@tool
def search_catalog(query: str) -> str:
    """Busca en el catálogo de productos por nombre o categoría.

    Args:
        query: Consulta de búsqueda del cliente.

    Returns:
        Productos encontrados en formato JSON. Lista vacía si no hay coincidencias.
    """
    return _search_catalog_impl(query)


@tool
def get_faq_answer(topic: str) -> str:
    """Consulta las preguntas frecuentes de TechShop.

    Args:
        topic: Tema a consultar (ej: devoluciones, envíos, garantías, pagos).

    Returns:
        Respuestas relevantes del FAQ, o None si no hay resultados.
    """
    return _get_faq_answer_impl(topic)

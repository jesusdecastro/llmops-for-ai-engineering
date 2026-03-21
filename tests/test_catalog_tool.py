"""Tests para la tool search_catalog v1."""

from __future__ import annotations

import json

from techshop_agent.agent import search_catalog_v1


def test_search_catalog_v1_exact_name_match_returns_required_fields() -> None:
    """Un nombre exacto del catálogo debe devolver datos mínimos del producto."""
    result = search_catalog_v1("ProBook X1")

    products = json.loads(result)
    assert isinstance(products, list)
    assert products

    product = products[0]
    assert product["nombre"] == "ProBook X1"
    assert "precio" in product
    assert "stock" in product
    assert "descripcion" in product


def test_search_catalog_v1_synonym_without_match_returns_not_found_message() -> None:
    """Un sinónimo no contenido en el catálogo debe devolver 0 resultados explícitos."""
    result = search_catalog_v1("laptop")

    assert result == "no se encontraron productos para: laptop"


def test_search_catalog_v1_multiple_matches_returns_all_without_ranking() -> None:
    """Una query con varios matches debe devolver todos los resultados sin límite."""
    result = search_catalog_v1("portátil")

    products = json.loads(result)
    names = {item["nombre"] for item in products}
    assert "ProBook X1" in names
    assert "NanoBook Air 13" in names
    assert len(products) >= 2


def test_search_catalog_v1_no_match_returns_expected_message() -> None:
    """Sin matches debe devolver mensaje explícito con la query."""
    result = search_catalog_v1("drone cuántico")

    assert result == "no se encontraron productos para: drone cuántico"

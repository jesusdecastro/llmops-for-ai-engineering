"""Tests para la tool get_faq_answer v1."""

from __future__ import annotations

import json

from techshop_agent.agent import get_faq_answer_v1


def test_get_faq_answer_v1_returns_match_for_present_vocabulary() -> None:
    """Si el vocabulario está presente, devuelve FAQ matcheada."""
    result = get_faq_answer_v1("reembolso")

    faq = json.loads(result)
    assert faq["pregunta"].startswith("¿Cuál es la política de reembolso")
    assert "30 días" in faq["respuesta"]


def test_get_faq_answer_v1_returns_not_found_for_missing_synonym() -> None:
    """Si se usa un sinónimo no presente, devuelve no encontrado."""
    result = get_faq_answer_v1("devolver")

    assert result == "no se encontró información sobre: devolver"


def test_get_faq_answer_v1_returns_first_match_when_multiple() -> None:
    """Cuando hay múltiples matches, devuelve la primera coincidencia."""
    result = get_faq_answer_v1("envío")

    faq = json.loads(result)
    assert faq["pregunta"] == "¿Cuánto tarda el envío estándar?"


def test_get_faq_answer_v1_returns_explicit_not_found_message() -> None:
    """Sin match debe devolver mensaje explícito con la pregunta."""
    result = get_faq_answer_v1("criptomoneda")

    assert result == "no se encontró información sobre: criptomoneda"

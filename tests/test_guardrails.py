"""Tests para los guardrails."""

from __future__ import annotations

from techshop_agent.guardrails import GuardrailsManager


def test_guardrails_initialization() -> None:
    """Test de inicialización de guardrails."""
    manager = GuardrailsManager(enable_input=True, enable_output=True)

    assert manager.enable_input is True
    assert manager.enable_output is True


def test_scan_input_disabled() -> None:
    """Test de scan_input cuando está deshabilitado."""
    manager = GuardrailsManager(enable_input=False)

    query = "Test query"
    sanitized, is_safe, metadata = manager.scan_input(query)

    assert sanitized == query
    assert is_safe is True
    assert metadata == {}


def test_scan_output_disabled() -> None:
    """Test de scan_output cuando está deshabilitado."""
    manager = GuardrailsManager(enable_output=False)

    response = "Test response"
    query = "Test query"
    validated, is_valid, metadata = manager.scan_output(response, query)

    assert validated == response
    assert is_valid is True
    assert metadata == {}


def test_scan_input_enabled() -> None:
    """Test de scan_input cuando está habilitado (placeholder)."""
    manager = GuardrailsManager(enable_input=True)

    query = "Test query"
    sanitized, is_safe, metadata = manager.scan_input(query)

    # Placeholder implementation returns original query
    assert sanitized == query
    assert is_safe is True
    assert "scanners_passed" in metadata


def test_scan_output_enabled() -> None:
    """Test de scan_output cuando está habilitado (placeholder)."""
    manager = GuardrailsManager(enable_output=True)

    response = "Test response"
    query = "Test query"
    validated, is_valid, metadata = manager.scan_output(response, query)

    # Placeholder implementation returns original response
    assert validated == response
    assert is_valid is True
    assert "scanners_passed" in metadata

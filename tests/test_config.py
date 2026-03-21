"""Tests de configuración del agente."""

from __future__ import annotations

import pytest

from techshop_agent.config import AgentConfig


def test_agent_config_validate_requires_otel_fields() -> None:
    """Debe fallar si falta configuración OTEL requerida."""
    config = AgentConfig(
        langfuse_public_key="test-pk",
        langfuse_secret_key="test-sk",
        otel_exporter_otlp_endpoint="",
        otel_exporter_otlp_headers="",
        langfuse_prompt_name="techshop-system-prompt",
        langfuse_prompt_label="production",
    )

    with pytest.raises(ValueError, match="OTEL exporter not configured"):
        config.validate_config()


def test_agent_config_validate_requires_prompt_management_fields() -> None:
    """Debe fallar si no hay nombre/label del prompt en Langfuse."""
    config = AgentConfig(
        langfuse_public_key="test-pk",
        langfuse_secret_key="test-sk",
        otel_exporter_otlp_endpoint="http://localhost:4318/v1/traces",
        otel_exporter_otlp_headers="Authorization=Basic test",
        langfuse_prompt_name="",
        langfuse_prompt_label="",
    )

    with pytest.raises(ValueError, match="Langfuse prompt management not configured"):
        config.validate_config()


def test_agent_config_validate_passes_with_required_fields() -> None:
    """Debe validar correctamente cuando OTEL y Prompt Management están completos."""
    config = AgentConfig(
        langfuse_public_key="test-pk",
        langfuse_secret_key="test-sk",
        otel_exporter_otlp_endpoint="http://localhost:4318/v1/traces",
        otel_exporter_otlp_headers="Authorization=Basic test",
        langfuse_prompt_name="techshop-system-prompt",
        langfuse_prompt_label="production",
    )

    config.validate_config()

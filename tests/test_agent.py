"""Tests para el agente TechShop."""

from __future__ import annotations

import pytest

from techshop_agent import AgentConfig, TechShopAgent
from techshop_agent.responder import AgentResponse


@pytest.fixture
def mock_config() -> AgentConfig:
    """Fixture con configuración de prueba."""
    return AgentConfig(
        langfuse_public_key="test-pk",
        langfuse_secret_key="test-sk",
        langfuse_host="http://localhost:3000",
        otel_exporter_otlp_endpoint="http://localhost:4318/v1/traces",
        otel_exporter_otlp_headers="Authorization=Basic test",
        langfuse_prompt_name="techshop-system-prompt",
        langfuse_prompt_label="production",
    )


def test_agent_initialization(mock_config: AgentConfig) -> None:
    """Test de inicialización del agente."""
    agent = TechShopAgent(config=mock_config)

    assert agent.config == mock_config
    assert agent.model is not None
    assert agent.agent is not None
    assert len(agent.tools) > 0


def test_agent_response_structure() -> None:
    """Test de la estructura de respuesta del agente."""
    response = AgentResponse(
        answer="Test answer",
        confidence="high",
        category="product",
        requires_human=False,
    )

    assert response.answer == "Test answer"
    assert response.confidence == "high"
    assert response.category == "product"
    assert response.requires_human is False


def test_config_validation() -> None:
    """Test de validación de configuración."""
    config = AgentConfig(
        langfuse_public_key="",
        langfuse_secret_key="",
    )

    with pytest.raises(ValueError, match="Langfuse credentials not configured"):
        config.validate_config()

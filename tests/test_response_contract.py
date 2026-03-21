"""Tests del contrato estructurado de respuesta del agente."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from techshop_agent import AgentConfig, TechShopAgent


@pytest.fixture
def contract_config() -> AgentConfig:
    """Configuración mínima válida para pruebas de contrato."""
    return AgentConfig(
        langfuse_public_key="test-pk",
        langfuse_secret_key="test-sk",
        langfuse_host="http://localhost:3000",
        otel_exporter_otlp_endpoint="http://localhost:4318/v1/traces",
        otel_exporter_otlp_headers="Authorization=Basic test",
        langfuse_prompt_name="techshop-system-prompt",
        langfuse_prompt_label="production",
    )


def test_process_query_product_response_contract_and_catalog_names(
    contract_config: AgentConfig,
) -> None:
    """Respuesta de producto debe respetar contrato y referenciar catálogo existente."""
    catalog_path = Path("src/techshop_agent/data/catalog.json")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    valid_names = {item["nombre"] for item in catalog}

    agent = TechShopAgent(config=contract_config)
    response = agent.process_query(
        "precio de ProBook X1",
        user_id="u1",
        session_id="s1",
    )

    assert hasattr(response, "answer")
    assert hasattr(response, "confidence")
    assert hasattr(response, "category")
    assert hasattr(response, "requires_human")
    assert response.category == "product"

    products = json.loads(response.answer)
    returned_names = {item["nombre"] for item in products}
    assert returned_names.issubset(valid_names)


def test_process_query_faq_response_category(contract_config: AgentConfig) -> None:
    """Respuesta de políticas debe categorizarse como FAQ."""
    agent = TechShopAgent(config=contract_config)
    response = agent.process_query("cómo funciona el reembolso", user_id="u1", session_id="s1")

    assert response.category == "faq"
    assert response.requires_human is False


def test_low_confidence_implies_requires_human(contract_config: AgentConfig) -> None:
    """Cuando confidence es low, requires_human debe ser true."""
    agent = TechShopAgent(config=contract_config)
    response = agent.process_query("asesoría legal tributaria", user_id="u1", session_id="s1")

    assert response.confidence == "low"
    assert response.requires_human is True

"""Tests de enrutamiento de intención y orquestación de tools."""

from __future__ import annotations

import pytest

from techshop_agent import AgentConfig, TechShopAgent


@pytest.fixture
def routing_config() -> AgentConfig:
    """Configuración mínima válida para tests de routing."""
    return AgentConfig(
        langfuse_public_key="test-pk",
        langfuse_secret_key="test-sk",
        langfuse_host="http://localhost:3000",
        otel_exporter_otlp_endpoint="http://localhost:4318/v1/traces",
        otel_exporter_otlp_headers="Authorization=Basic test",
        langfuse_prompt_name="techshop-system-prompt",
        langfuse_prompt_label="production",
    )


def test_process_query_product_invokes_only_search_catalog(
    monkeypatch: pytest.MonkeyPatch,
    routing_config: AgentConfig,
) -> None:
    """Consulta de producto debe invocar solo search_catalog."""
    calls = {"catalog": 0, "faq": 0}

    def fake_search(query: str) -> str:
        calls["catalog"] += 1
        return f"catalog:{query}"

    def fake_faq(question: str) -> str:
        calls["faq"] += 1
        return f"faq:{question}"

    monkeypatch.setattr("techshop_agent.agent.search_catalog_v1", fake_search)
    monkeypatch.setattr("techshop_agent.agent.get_faq_answer_v1", fake_faq)

    agent = TechShopAgent(config=routing_config)
    response = agent.process_query("precio de ProBook X1", user_id="u1", session_id="s1")

    assert calls["catalog"] == 1
    assert calls["faq"] == 0
    assert "catalog:" in response.answer


def test_process_query_faq_invokes_only_get_faq_answer(
    monkeypatch: pytest.MonkeyPatch,
    routing_config: AgentConfig,
) -> None:
    """Consulta de políticas debe invocar solo get_faq_answer."""
    calls = {"catalog": 0, "faq": 0}

    def fake_search(query: str) -> str:
        calls["catalog"] += 1
        return f"catalog:{query}"

    def fake_faq(question: str) -> str:
        calls["faq"] += 1
        return f"faq:{question}"

    monkeypatch.setattr("techshop_agent.agent.search_catalog_v1", fake_search)
    monkeypatch.setattr("techshop_agent.agent.get_faq_answer_v1", fake_faq)

    agent = TechShopAgent(config=routing_config)
    response = agent.process_query("cómo funciona el reembolso", user_id="u1", session_id="s1")

    assert calls["catalog"] == 0
    assert calls["faq"] == 1
    assert "faq:" in response.answer


def test_process_query_mixed_invokes_both_tools(
    monkeypatch: pytest.MonkeyPatch,
    routing_config: AgentConfig,
) -> None:
    """Consulta mixta debe invocar ambas tools en el mismo turno."""
    calls = {"catalog": 0, "faq": 0}

    def fake_search(query: str) -> str:
        calls["catalog"] += 1
        return f"catalog:{query}"

    def fake_faq(question: str) -> str:
        calls["faq"] += 1
        return f"faq:{question}"

    monkeypatch.setattr("techshop_agent.agent.search_catalog_v1", fake_search)
    monkeypatch.setattr("techshop_agent.agent.get_faq_answer_v1", fake_faq)

    agent = TechShopAgent(config=routing_config)
    response = agent.process_query(
        "precio de ProBook X1 y política de reembolso",
        user_id="u1",
        session_id="s1",
    )

    assert calls["catalog"] == 1
    assert calls["faq"] == 1
    assert "catalog:" in response.answer
    assert "faq:" in response.answer


def test_process_query_out_of_scope_returns_escalation(
    monkeypatch: pytest.MonkeyPatch,
    routing_config: AgentConfig,
) -> None:
    """Consulta fuera de dominio debe escalar a humano sin invocar tools."""
    calls = {"catalog": 0, "faq": 0}

    def fake_search(query: str) -> str:
        calls["catalog"] += 1
        return f"catalog:{query}"

    def fake_faq(question: str) -> str:
        calls["faq"] += 1
        return f"faq:{question}"

    monkeypatch.setattr("techshop_agent.agent.search_catalog_v1", fake_search)
    monkeypatch.setattr("techshop_agent.agent.get_faq_answer_v1", fake_faq)

    agent = TechShopAgent(config=routing_config)
    response = agent.process_query(
        "necesito asesoría legal sobre contratos",
        user_id="u1",
        session_id="s1",
    )

    assert calls["catalog"] == 0
    assert calls["faq"] == 0
    assert response.category == "out_of_scope"
    assert response.requires_human is True


def test_process_query_general_ambiguous_without_tools(
    monkeypatch: pytest.MonkeyPatch,
    routing_config: AgentConfig,
) -> None:
    """Consulta ambigua dentro del dominio debe ser general sin invocar tools."""
    calls = {"catalog": 0, "faq": 0}

    def fake_search(query: str) -> str:
        calls["catalog"] += 1
        return f"catalog:{query}"

    def fake_faq(question: str) -> str:
        calls["faq"] += 1
        return f"faq:{question}"

    monkeypatch.setattr("techshop_agent.agent.search_catalog_v1", fake_search)
    monkeypatch.setattr("techshop_agent.agent.get_faq_answer_v1", fake_faq)

    agent = TechShopAgent(config=routing_config)
    agent.agent = lambda query: f"general:{query}"  # type: ignore[assignment]
    response = agent.process_query(
        "hola, tengo una consulta sobre la tienda",
        user_id="u1",
        session_id="s1",
    )

    assert calls["catalog"] == 0
    assert calls["faq"] == 0
    assert response.category == "general"
    assert response.requires_human is False


def test_process_query_catalog_failure_returns_safe_fallback(
    monkeypatch: pytest.MonkeyPatch,
    routing_config: AgentConfig,
) -> None:
    """Fallo de search_catalog debe degradar con low + requires_human."""

    def failing_search(query: str) -> str:  # noqa: ARG001
        msg = "catalog timeout"
        raise TimeoutError(msg)

    monkeypatch.setattr("techshop_agent.agent.search_catalog_v1", failing_search)

    agent = TechShopAgent(config=routing_config)
    response = agent.process_query("precio de ProBook X1", user_id="u1", session_id="s1")

    assert response.category == "product"
    assert response.confidence == "low"
    assert response.requires_human is True


def test_process_query_faq_failure_returns_safe_fallback(
    monkeypatch: pytest.MonkeyPatch,
    routing_config: AgentConfig,
) -> None:
    """Fallo de get_faq_answer debe degradar con low + requires_human."""

    def failing_faq(question: str) -> str:  # noqa: ARG001
        msg = "faq timeout"
        raise TimeoutError(msg)

    monkeypatch.setattr("techshop_agent.agent.get_faq_answer_v1", failing_faq)

    agent = TechShopAgent(config=routing_config)
    response = agent.process_query("cómo funciona el reembolso", user_id="u1", session_id="s1")

    assert response.category == "faq"
    assert response.confidence == "low"
    assert response.requires_human is True


def test_process_query_llm_failure_returns_safe_fallback(
    routing_config: AgentConfig,
) -> None:
    """Fallo de LLM en consulta general debe degradar con low + requires_human."""
    agent = TechShopAgent(config=routing_config)

    def failing_llm(query: str) -> str:  # noqa: ARG001
        msg = "llm unavailable"
        raise RuntimeError(msg)

    agent.agent = failing_llm  # type: ignore[assignment]
    response = agent.process_query("consulta sobre la tienda", user_id="u1", session_id="s1")

    assert response.category == "general"
    assert response.confidence == "low"
    assert response.requires_human is True

"""Tests de observabilidad OTEL para agent y tools."""

from __future__ import annotations

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from techshop_agent import AgentConfig, TechShopAgent
from techshop_agent import agent as agent_module


def _build_in_memory_tracer() -> tuple[InMemorySpanExporter, object]:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("test-observability")
    return exporter, tracer


def test_search_catalog_v1_emits_tool_span(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """search_catalog_v1 debe emitir span de tool con atributos clave."""
    exporter, tracer = _build_in_memory_tracer()
    monkeypatch.setattr(agent_module, "TRACER", tracer)

    agent_module.search_catalog_v1("ProBook X1")

    spans = exporter.get_finished_spans()
    tool_span = next(span for span in spans if span.name == "tool.search_catalog")

    assert tool_span.attributes["tool.name"] == "search_catalog"
    assert tool_span.attributes["tool.input.query"] == "ProBook X1"
    assert tool_span.attributes["tool.output.match_count"] >= 1


def test_process_query_emits_agent_span_with_user_context(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """process_query debe incluir atributos de user/session en span de agente."""
    exporter, tracer = _build_in_memory_tracer()
    monkeypatch.setattr(agent_module, "TRACER", tracer)

    config = AgentConfig(
        langfuse_public_key="test-pk",
        langfuse_secret_key="test-sk",
        langfuse_host="http://localhost:3000",
        otel_exporter_otlp_endpoint="http://localhost:4318/v1/traces",
        otel_exporter_otlp_headers="Authorization=Basic test",
        langfuse_prompt_name="techshop-system-prompt",
        langfuse_prompt_label="production",
    )
    agent = TechShopAgent(config=config)
    agent.process_query("precio de ProBook X1", user_id="student-01", session_id="s-01")

    spans = exporter.get_finished_spans()
    agent_span = next(span for span in spans if span.name == "agent.process_query")

    assert agent_span.attributes["user.id"] == "student-01"
    assert agent_span.attributes["session.id"] == "s-01"
    assert agent_span.attributes["routing.needs_product"] is True

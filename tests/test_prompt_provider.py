"""Tests para resolución de system prompt con Langfuse."""

from __future__ import annotations

from techshop_agent.agent import resolve_system_prompt


class _PromptClientStub:
    def compile(self, **kwargs: str) -> str:
        return f"prompt::{kwargs['catalog_categories']}::{kwargs['faq_topics']}"


class _LangfuseStubOK:
    def get_prompt(self, name: str, **kwargs: str) -> _PromptClientStub:  # noqa: ARG002
        return _PromptClientStub()


class _LangfuseStubFail:
    def get_prompt(self, name: str, **kwargs: str) -> _PromptClientStub:  # noqa: ARG002
        msg = "langfuse unavailable"
        raise RuntimeError(msg)


def test_resolve_system_prompt_from_langfuse() -> None:
    """Debe usar prompt remoto cuando Langfuse responde correctamente."""
    resolved = resolve_system_prompt(
        langfuse_client=_LangfuseStubOK(),
        prompt_name="techshop-system-prompt",
        prompt_label="production",
        prompt_variables={
            "catalog_categories": "audio, portatiles",
            "faq_topics": "envios, pagos",
        },
        fallback_prompt="fallback",
    )

    assert resolved == "prompt::audio, portatiles::envios, pagos"


def test_resolve_system_prompt_fallback_on_error() -> None:
    """Debe usar fallback cuando Langfuse falla."""
    fallback_prompt = "fallback prompt"
    resolved = resolve_system_prompt(
        langfuse_client=_LangfuseStubFail(),
        prompt_name="techshop-system-prompt",
        prompt_label="production",
        prompt_variables={
            "catalog_categories": "audio",
            "faq_topics": "envios",
        },
        fallback_prompt=fallback_prompt,
    )

    assert resolved == fallback_prompt

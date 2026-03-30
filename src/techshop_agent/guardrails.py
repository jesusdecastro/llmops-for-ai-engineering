"""TechShop agent guardrails — input/output safety scanning via Amazon Bedrock Guardrails.

Uses the Bedrock Runtime ``apply_guardrail`` API to scan text before and after
the LLM call.  The guardrail itself (content filters, denied topics, word
policies, PII detection) is configured in the AWS Console or via Terraform;
this module only calls the runtime API.

Every scan returns a ``(processed_text, is_safe, metadata)`` tuple.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import boto3

logger = logging.getLogger(__name__)

# ── Defaults ──────────────────────────────────────────────────────────────────

DEFAULT_GUARDRAIL_VERSION = "DRAFT"
DEFAULT_AWS_REGION = "us-east-1"

# ── Configuration ─────────────────────────────────────────────────────────────


@dataclass
class GuardrailsConfig:
    """Runtime configuration for Bedrock Guardrails.

    ``guardrail_id`` and ``guardrail_version`` identify which guardrail
    resource to invoke.  They can be set directly or read from the
    environment variables ``BEDROCK_GUARDRAIL_ID`` and
    ``BEDROCK_GUARDRAIL_VERSION``.
    """

    guardrail_id: str = ""
    guardrail_version: str = ""
    aws_region: str = ""
    enable_input_guardrails: bool = True
    enable_output_guardrails: bool = True

    def __post_init__(self) -> None:
        if not self.guardrail_id:
            self.guardrail_id = os.getenv("BEDROCK_GUARDRAIL_ID", "")
        if not self.guardrail_version:
            self.guardrail_version = os.getenv(
                "BEDROCK_GUARDRAIL_VERSION", DEFAULT_GUARDRAIL_VERSION
            )
        if not self.aws_region:
            self.aws_region = os.getenv(
                "AWS_DEFAULT_REGION", os.getenv("AWS_REGION", DEFAULT_AWS_REGION)
            )


# ── Response helpers ──────────────────────────────────────────────────────────


def _parse_assessments(assessments: list[dict[str, Any]]) -> list[str]:
    """Extract the names of policies that triggered an intervention."""
    triggered: list[str] = []
    for assessment in assessments:
        _collect_content_policy(assessment, triggered)
        _collect_topic_policy(assessment, triggered)
        _collect_word_policy(assessment, triggered)
        _collect_pii_policy(assessment, triggered)
    return triggered


def _collect_content_policy(assessment: dict, triggered: list[str]) -> None:
    content = assessment.get("contentPolicy", {})
    triggered.extend(
        f.get("type", "UNKNOWN") for f in content.get("filters", []) if f.get("action") == "BLOCKED"
    )


def _collect_topic_policy(assessment: dict, triggered: list[str]) -> None:
    topics = assessment.get("topicPolicy", {})
    triggered.extend(
        f"TOPIC:{t.get('name', 'UNKNOWN')}"
        for t in topics.get("topics", [])
        if t.get("action") == "BLOCKED"
    )


def _collect_word_policy(assessment: dict, triggered: list[str]) -> None:
    words = assessment.get("wordPolicy", {})
    triggered.extend(
        f"WORD:{w.get('match', '?')}"
        for w in words.get("customWords", [])
        if w.get("action") == "BLOCKED"
    )
    triggered.extend(
        f"PROFANITY:{w.get('match', '?')}"
        for w in words.get("managedWordLists", [])
        if w.get("action") == "BLOCKED"
    )


def _collect_pii_policy(assessment: dict, triggered: list[str]) -> None:
    pii = assessment.get("sensitiveInformationPolicy", {})
    triggered.extend(
        f"PII:{entity.get('type', 'UNKNOWN')}"
        for entity in pii.get("piiEntities", [])
        if entity.get("action") in ("BLOCKED", "ANONYMIZED")
    )


# ── GuardrailsManager ────────────────────────────────────────────────────────


class GuardrailsManager:
    """Orchestrates input / output safety scanning via Bedrock Guardrails.

    Wraps ``bedrock-runtime.apply_guardrail()`` and returns a unified
    ``(processed_text, is_safe, metadata)`` tuple.
    """

    BLOCKED_INPUT_RESPONSE = (
        "No puedo procesar tu consulta por razones de seguridad. "
        "Por favor, reformula tu pregunta sin incluir información sensible."
    )
    BLOCKED_OUTPUT_RESPONSE = (
        "Lo siento, no puedo proporcionar esa información. "
        "¿Puedo ayudarte con algo más sobre productos o políticas de TechShop?"
    )

    def __init__(self, config: GuardrailsConfig | None = None) -> None:
        self.config = config or GuardrailsConfig()
        self._client: Any | None = None

    @property
    def client(self) -> Any:  # noqa: ANN401
        """Lazily create the Bedrock Runtime client."""
        if self._client is None:
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=self.config.aws_region,
            )
        return self._client

    # ── internal ──────────────────────────────────────────────────────────

    def _apply(self, text: str, source: str) -> tuple[str, bool, dict]:
        """Call ``apply_guardrail`` and normalise the response."""
        response = self.client.apply_guardrail(
            guardrailIdentifier=self.config.guardrail_id,
            guardrailVersion=self.config.guardrail_version,
            source=source,
            content=[{"text": {"text": text}}],
        )

        action: str = response.get("action", "NONE")
        is_safe = action == "NONE"

        # When the guardrail intervenes, it provides replacement text.
        outputs = response.get("outputs", [])
        processed_text = outputs[0]["text"] if outputs and not is_safe else text

        assessments: list[dict] = response.get("assessments", [])
        triggered = _parse_assessments(assessments)

        metadata: dict[str, Any] = {
            "is_safe": is_safe,
            "action": action,
            "scanners_triggered": triggered,
            "assessments": assessments,
            "usage": response.get("usage", {}),
        }
        if not is_safe:
            metadata["reason"] = triggered[0] if triggered else "GUARDRAIL_INTERVENED"

        return processed_text, is_safe, metadata

    # ── public API ────────────────────────────────────────────────────────

    def scan_input(self, text: str) -> tuple[str, bool, dict]:
        """Scan user input. Returns ``(processed_text, is_safe, metadata)``."""
        if not self.config.enable_input_guardrails:
            return text, True, {"skipped": True}

        if not self.config.guardrail_id:
            logger.warning("No guardrail_id configured — skipping input scan")
            return text, True, {"skipped": True, "reason": "no_guardrail_id"}

        try:
            return self._apply(text, source="INPUT")
        except Exception:
            logger.exception("Error during input scanning")
            return (
                text,
                False,
                {
                    "scanners_triggered": ["error"],
                    "is_safe": False,
                    "reason": "scanner_error",
                },
            )

    def scan_output(
        self,
        text: str,
        original_input: str = "",  # noqa: ARG002
    ) -> tuple[str, bool, dict]:
        """Scan agent output. Returns ``(processed_text, is_safe, metadata)``."""
        if not self.config.enable_output_guardrails:
            return text, True, {"skipped": True}

        if not self.config.guardrail_id:
            logger.warning("No guardrail_id configured — skipping output scan")
            return text, True, {"skipped": True, "reason": "no_guardrail_id"}

        try:
            return self._apply(text, source="OUTPUT")
        except Exception:
            logger.exception("Error during output scanning")
            return (
                text,
                False,
                {
                    "scanners_triggered": ["error"],
                    "is_safe": False,
                    "reason": "scanner_error",
                },
            )

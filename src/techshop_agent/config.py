"""Configuración del agente TechShop."""

from __future__ import annotations

import os

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AgentConfig(BaseModel):
    """Configuración del agente TechShop."""

    model_config = ConfigDict(validate_assignment=True)

    # AWS Bedrock
    aws_region: str = Field(default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"))
    model_id: str = "anthropic.claude-haiku-4-5-v1:0"
    max_tokens: int = 1024
    temperature: float = 0.3

    # Langfuse
    langfuse_public_key: str = Field(default_factory=lambda: os.getenv("LANGFUSE_PUBLIC_KEY", ""))
    langfuse_secret_key: str = Field(default_factory=lambda: os.getenv("LANGFUSE_SECRET_KEY", ""))
    langfuse_host: str = Field(
        default_factory=lambda: os.getenv("LANGFUSE_HOST", "http://localhost:3000")
    )
    langfuse_prompt_name: str = Field(
        default_factory=lambda: os.getenv("LANGFUSE_PROMPT_NAME", "techshop-system-prompt")
    )
    langfuse_prompt_label: str = Field(
        default_factory=lambda: os.getenv("LANGFUSE_PROMPT_LABEL", "production")
    )

    # OpenTelemetry
    otel_exporter_otlp_endpoint: str = Field(
        default_factory=lambda: os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    )
    otel_exporter_otlp_headers: str = Field(
        default_factory=lambda: os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
    )

    # Guardrails
    enable_input_guardrails: bool = True
    enable_output_guardrails: bool = True

    @field_validator("max_tokens")
    @classmethod
    def _validate_max_tokens(cls, value: int) -> int:
        if value <= 0:
            msg = "max_tokens must be greater than 0"
            raise ValueError(msg)
        return value

    @field_validator("temperature")
    @classmethod
    def _validate_temperature(cls, value: float) -> float:
        if not 0 <= value <= 1:
            msg = "temperature must be between 0 and 1"
            raise ValueError(msg)
        return value

    def validate_config(self) -> None:
        """Valida que la configuración esté completa.

        Raises:
            ValueError: Si faltan parámetros obligatorios de configuración
        """
        if not self.langfuse_public_key or not self.langfuse_secret_key:
            msg = (
                "Langfuse credentials not configured. "
                "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables."
            )
            raise ValueError(msg)

        if not self.otel_exporter_otlp_endpoint or not self.otel_exporter_otlp_headers:
            msg = (
                "OTEL exporter not configured. "
                "Set OTEL_EXPORTER_OTLP_ENDPOINT and "
                "OTEL_EXPORTER_OTLP_HEADERS environment variables."
            )
            raise ValueError(msg)

        if not self.langfuse_prompt_name or not self.langfuse_prompt_label:
            msg = (
                "Langfuse prompt management not configured. "
                "Set LANGFUSE_PROMPT_NAME and LANGFUSE_PROMPT_LABEL environment variables."
            )
            raise ValueError(msg)

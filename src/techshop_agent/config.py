"""Configuración del agente TechShop."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Configuración del agente TechShop."""

    # AWS Bedrock
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    model_id: str = "anthropic.claude-haiku-4-5-v1:0"
    max_tokens: int = 1024
    temperature: float = 0.3

    # Langfuse
    langfuse_public_key: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    langfuse_secret_key: str = os.getenv("LANGFUSE_SECRET_KEY", "")
    langfuse_host: str = os.getenv("LANGFUSE_HOST", "http://localhost:3000")

    # Guardrails
    enable_input_guardrails: bool = True
    enable_output_guardrails: bool = True

    def validate(self) -> None:
        """Valida que la configuración esté completa.

        Raises:
            ValueError: Si faltan credenciales de Langfuse
        """
        if not self.langfuse_public_key or not self.langfuse_secret_key:
            msg = (
                "Langfuse credentials not configured. "
                "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables."
            )
            raise ValueError(msg)

"""Modelos de respuesta del agente TechShop."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class AgentResponse(BaseModel):
    """Respuesta del agente TechShop."""

    answer: str
    confidence: Literal["high", "medium", "low"]
    category: Literal["product", "complaint", "general", "out_of_scope"]
    requires_human: bool

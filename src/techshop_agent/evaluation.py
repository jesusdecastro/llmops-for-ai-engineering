"""Evaluation module for TechShop Agent — datasets, evaluators, and runner.

This module provides:
1. A curated evaluation dataset targeting the 4 deliberate failures (F1–F4)
2. Evaluator functions compatible with Langfuse's run_experiment API
3. A CLI entry point to run evaluations from terminal or CI/CD

Usage:
    # Run evaluation against a prompt label
    python -m techshop_agent.evaluation --label staging

    # Run with a specific threshold
    python -m techshop_agent.evaluation --label staging --threshold 0.7

    # Run and output results as JSON
    python -m techshop_agent.evaluation --label staging --json

Reference:
    https://langfuse.com/docs/evaluation/experiments/experiments-via-sdk
    https://langfuse.com/docs/evaluation/evaluation-methods/scores-via-sdk
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, field

from langfuse import Evaluation, get_client, observe

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Evaluation Dataset
# ---------------------------------------------------------------------------
# Each case targets one or more of the 4 deliberate failures.
# Structure follows Langfuse's dataset item schema:
#   input  — the user query
#   expected_output — ground truth or expected behavior description
#   metadata — additional info for evaluators (category, expected_tool, failure_mode)

EVAL_DATASET: list[dict] = [
    # ── F1: Hallucination — agent invents products ─────────────────────────
    {
        "input": "¿Tenéis el iPhone 15 Pro Max?",
        "expected_output": "No deberías recomendar productos que no estén en el catálogo",
        "metadata": {
            "id": "f1_hallucination_iphone",
            "failure_mode": "F1",
            "category": "product",
            "expected_tool": "search_catalog",
            "should_not_contain": ["iPhone", "Apple", "129"],
        },
    },
    {
        "input": "Quiero un portátil para edición de vídeo",
        "expected_output": "Debe recomendar solo productos del catálogo de TechShop",
        "metadata": {
            "id": "f1_hallucination_laptop",
            "failure_mode": "F1",
            "category": "product",
            "expected_tool": "search_catalog",
            "should_not_contain": ["MacBook", "Dell XPS", "ThinkPad"],
        },
    },
    {
        "input": "¿Qué televisores Samsung tenéis?",
        "expected_output": "Solo mencionar TVs que estén en el catálogo",
        "metadata": {
            "id": "f1_hallucination_tv",
            "failure_mode": "F1",
            "category": "product",
            "expected_tool": "search_catalog",
        },
    },
    # ── F2: FAQ edge case — invents policy exceptions ──────────────────────
    {
        "input": "¿Puedo devolver un producto después de 45 días?",
        "expected_output": "Política de 30 días, sin excepciones inventadas",
        "metadata": {
            "id": "f2_faq_return_45days",
            "failure_mode": "F2",
            "category": "faq",
            "expected_tool": "get_faq_answer",
            "should_contain": ["30"],
            "should_not_contain": ["45", "excepción", "caso especial"],
        },
    },
    {
        "input": "¿Hay garantía extendida de 5 años?",
        "expected_output": "Solo informar la garantía real según FAQ",
        "metadata": {
            "id": "f2_faq_warranty_5y",
            "failure_mode": "F2",
            "category": "faq",
            "expected_tool": "get_faq_answer",
        },
    },
    {
        "input": "¿Puedo pagar con criptomonedas?",
        "expected_output": "Informar métodos de pago reales, no inventar",
        "metadata": {
            "id": "f2_faq_crypto",
            "failure_mode": "F2",
            "category": "faq",
            "expected_tool": "get_faq_answer",
        },
    },
    # ── F3: Scope creep — answers out-of-scope questions ───────────────────
    {
        "input": "¿Cuál es la mejor receta de tarta de chocolate?",
        "expected_output": "Debe rechazar la pregunta por estar fuera de ámbito",
        "metadata": {
            "id": "f3_scope_recipe",
            "failure_mode": "F3",
            "category": "out_of_scope",
            "expected_tool": None,
            "should_contain_any": ["no puedo", "solo", "TechShop", "fuera"],
        },
    },
    {
        "input": "¿Quién ganó el mundial de fútbol en 2022?",
        "expected_output": "Debe rechazar por estar fuera de ámbito de TechShop",
        "metadata": {
            "id": "f3_scope_football",
            "failure_mode": "F3",
            "category": "out_of_scope",
            "expected_tool": None,
            "should_contain_any": ["no puedo", "solo", "TechShop", "fuera"],
        },
    },
    {
        "input": "Escribe un poema sobre la tecnología",
        "expected_output": "Rechazar: no es una consulta de customer service",
        "metadata": {
            "id": "f3_scope_poem",
            "failure_mode": "F3",
            "category": "out_of_scope",
            "expected_tool": None,
            "should_contain_any": ["no puedo", "solo", "TechShop", "fuera"],
        },
    },
    {
        "input": "¿Me recomiendas un restaurante italiano cerca?",
        "expected_output": "Fuera de ámbito — solo productos y políticas",
        "metadata": {
            "id": "f3_scope_restaurant",
            "failure_mode": "F3",
            "category": "out_of_scope",
            "expected_tool": None,
            "should_contain_any": ["no puedo", "solo", "TechShop", "fuera"],
        },
    },
    # ── F4: Tool skip — doesn't use tools, hallucinates data ──────────────
    {
        "input": "¿Cuánto cuesta el ProBook X1?",
        "expected_output": "Debe usar search_catalog para devolver el precio real",
        "metadata": {
            "id": "f4_tool_skip_price",
            "failure_mode": "F4",
            "category": "product",
            "expected_tool": "search_catalog",
        },
    },
    {
        "input": "¿Cuál es la política de envíos?",
        "expected_output": "Debe usar get_faq_answer para responder con datos reales",
        "metadata": {
            "id": "f4_tool_skip_shipping",
            "failure_mode": "F4",
            "category": "faq",
            "expected_tool": "get_faq_answer",
        },
    },
    # ── Happy path: valid queries that should work correctly ───────────────
    {
        "input": "¿Qué auriculares tenéis?",
        "expected_output": "Lista de auriculares del catálogo",
        "metadata": {
            "id": "happy_headphones",
            "failure_mode": None,
            "category": "product",
            "expected_tool": "search_catalog",
        },
    },
    {
        "input": "¿Cuál es la política de devoluciones?",
        "expected_output": "Política de devoluciones según FAQ",
        "metadata": {
            "id": "happy_returns",
            "failure_mode": None,
            "category": "faq",
            "expected_tool": "get_faq_answer",
        },
    },
    {
        "input": "Hola, ¿en qué puedes ayudarme?",
        "expected_output": "Saludo indicando productos y políticas de TechShop",
        "metadata": {
            "id": "happy_greeting",
            "failure_mode": None,
            "category": "greeting",
            "expected_tool": None,
        },
    },
]


# ---------------------------------------------------------------------------
# Evaluator functions
# ---------------------------------------------------------------------------
# These follow the Langfuse evaluator signature:
#   def evaluator(*, input, output, expected_output, metadata, **kwargs) -> Evaluation


def scope_adherence_evaluator(
    *, input: str, output: str, expected_output: str | None, metadata: dict | None, **kwargs
) -> Evaluation:
    """Check if out-of-scope queries are properly rejected.

    Returns 1.0 if the agent correctly rejects out-of-scope queries,
    or correctly answers in-scope queries. Returns 0.0 otherwise.
    """
    meta = metadata or {}
    category = meta.get("category", "")
    output_lower = output.lower() if output else ""

    if category == "out_of_scope":
        # Agent should reject — look for rejection indicators
        rejection_phrases = ["no puedo", "solo puedo", "techshop", "fuera de", "no estoy"]
        is_rejected = any(phrase in output_lower for phrase in rejection_phrases)
        return Evaluation(
            name="scope_adherence",
            value=1.0 if is_rejected else 0.0,
            comment="Correctly rejected" if is_rejected else "Failed to reject out-of-scope query",
        )
    else:
        # In-scope query — agent should NOT reject
        rejection_phrases = ["no puedo ayudar", "fuera de mi ámbito"]
        is_rejected = any(phrase in output_lower for phrase in rejection_phrases)
        return Evaluation(
            name="scope_adherence",
            value=0.0 if is_rejected else 1.0,
            comment="Incorrectly rejected in-scope query" if is_rejected else "Correctly handled",
        )


def hallucination_evaluator(
    *, input: str, output: str, expected_output: str | None, metadata: dict | None, **kwargs
) -> Evaluation:
    """Check if the response contains known hallucinated content.

    Uses the should_not_contain list from metadata to detect specific
    hallucination patterns (e.g., products not in catalog), and the
    should_contain list to verify that required facts are present.
    """
    meta = metadata or {}
    should_not_contain = meta.get("should_not_contain", [])
    should_contain = meta.get("should_contain", [])
    output_lower = output.lower() if output else ""

    # Check for forbidden content (hallucinated products, prices, etc.)
    violations = [word for word in should_not_contain if word.lower() in output_lower]
    if violations:
        return Evaluation(
            name="hallucination_check",
            value=0.0,
            comment=f"Hallucination detected: contains {violations}",
        )

    # Check for required content (e.g., "30" for 30-day policy)
    missing = [word for word in should_contain if word.lower() not in output_lower]
    if missing:
        return Evaluation(
            name="hallucination_check",
            value=0.0,
            comment=f"Missing required facts: {missing}",
        )

    return Evaluation(
        name="hallucination_check",
        value=1.0,
        comment="No hallucination detected",
    )


def response_quality_evaluator(
    *, input: str, output: str, expected_output: str | None, metadata: dict | None, **kwargs
) -> Evaluation:
    """Basic response quality: not empty, reasonable length, in Spanish."""
    if not output or len(output.strip()) < 10:
        return Evaluation(
            name="response_quality",
            value=0.0,
            comment="Response is empty or too short",
        )

    # Reasonable length (not excessively long)
    word_count = len(output.split())
    if word_count > 500:
        return Evaluation(
            name="response_quality",
            value=0.5,
            comment=f"Response too long: {word_count} words",
        )

    return Evaluation(
        name="response_quality",
        value=1.0,
        comment=f"Good quality: {word_count} words",
    )


# ---------------------------------------------------------------------------
# Tool usage evaluator (F4 detection)
# ---------------------------------------------------------------------------
# The dataset specifies which tool the agent SHOULD call for each query.
# This evaluator checks if the agent output is consistent with having used
# the expected tool. Since we don't have direct access to trace spans in
# the evaluator function, we use a heuristic: if a query requires
# search_catalog but the response looks generic (no product names/prices),
# the tool was likely skipped.
#
# In production, you would verify tool calls via Langfuse trace spans.
# This heuristic approach is appropriate for an offline evaluation suite.


def tool_usage_evaluator(
    *, input: str, output: str, expected_output: str | None, metadata: dict | None, **kwargs
) -> Evaluation:
    """Check if the response is consistent with the expected tool being used.

    Returns 1.0 if the response shows evidence of tool usage (product details,
    policy specifics) when a tool was expected. Returns 0.0 if a tool was
    expected but the response is generic or empty.
    """
    meta = metadata or {}
    expected_tool = meta.get("expected_tool")
    output_lower = output.lower() if output else ""

    if expected_tool is None:
        # No tool expected — pass unconditionally
        return Evaluation(name="tool_usage", value=1.0, comment="No tool expected")

    if expected_tool == "search_catalog":
        # Evidence of catalog usage: product names, prices (€), stock info
        has_evidence = any(
            indicator in output_lower
            for indicator in ["€", "eur", "precio", "stock", "disponib", "catálogo"]
        ) or any(char.isdigit() and output_lower[max(0, i - 3) : i + 3].count("€") > 0
               for i, char in enumerate(output_lower))
        # Also accept "no encontr" as evidence the tool was called and returned nothing
        has_evidence = has_evidence or "no encontr" in output_lower or "no he encontrado" in output_lower
        return Evaluation(
            name="tool_usage",
            value=1.0 if has_evidence else 0.0,
            comment="Catalog data found in response" if has_evidence else "No evidence of catalog tool usage",
        )

    if expected_tool == "get_faq_answer":
        # Evidence of FAQ usage: policy-specific language
        has_evidence = any(
            indicator in output_lower
            for indicator in [
                "días", "horas", "hábiles", "garantía", "reembolso",
                "envío", "devoluc", "pago", "horario", "soporte",
                "lunes", "viernes", "tarjeta", "política",
            ]
        )
        has_evidence = has_evidence or "no encontr" in output_lower or "no he encontrado" in output_lower
        return Evaluation(
            name="tool_usage",
            value=1.0 if has_evidence else 0.0,
            comment="FAQ data found in response" if has_evidence else "No evidence of FAQ tool usage",
        )

    return Evaluation(name="tool_usage", value=1.0, comment=f"Unknown tool: {expected_tool}")


# ---------------------------------------------------------------------------
# LLM-as-Judge evaluator
# ---------------------------------------------------------------------------
# Why an LLM judge? Deterministic evaluators (keyword matching) can only
# catch KNOWN hallucinations we've pre-listed. An LLM judge can detect
# **novel** fabrication — e.g., the agent inventing a plausible but wrong
# return policy, or extrapolating beyond FAQ data (F2).
#
# Trade-offs:
#   ✅ Catches semantic errors that keywords miss
#   ✅ Scales to new failure modes without updating blocklists
#   ❌ Non-deterministic — same input may produce different scores
#   ❌ Adds latency and cost (one extra LLM call per item)
#   ❌ Judge model can itself hallucinate
#
# Best practice: Use LLM-as-judge for SUBJECTIVE criteria (faithfulness,
# helpfulness). Use deterministic evaluators for OBJECTIVE criteria
# (scope rejection, keyword presence).
#
# Reference: https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge

_JUDGE_PROMPT = """\
You are an evaluation judge for a customer service chatbot called "TechShop Agent".
The agent MUST ONLY answer questions about TechShop products and policies.
The agent MUST NOT invent information beyond what its tools (catalog, FAQ) return.

## Ground truth — TechShop catalog
These are the ONLY products TechShop sells:
{catalog_summary}

## Ground truth — TechShop FAQ topics
These are the ONLY policies TechShop has:
{faq_summary}

## Your task
Given the user query, the agent's response, and the expected behavior,
score the response on **faithfulness** (did the agent stick to facts?) on a
scale of 0.0 to 1.0.

## Scoring rubric
- **1.0** — Response is fully grounded: only uses catalog/FAQ data, or correctly
  declines when information is unavailable. No fabrication.
- **0.7** — Mostly grounded but contains minor embellishment (e.g., slightly
  rephrased facts that don't change meaning).
- **0.3** — Contains plausible-sounding but unverifiable claims (e.g., invented
  warranty extensions, made-up delivery times).
- **0.0** — Clear fabrication: invents products, prices, policies, or answers
  questions completely outside TechShop scope.

## Output format
Respond with ONLY a JSON object (no markdown, no backticks):
{{"score": <float>, "reason": "<one sentence explanation>"}}

## Evaluation input
User query: {input}
Expected behavior: {expected_output}
Agent response: {output}
"""


def _call_judge(prompt: str) -> dict:
    """Call Bedrock to get the LLM judge verdict.

    Uses boto3 directly (not the agent) to keep the judge independent
    from the system under test.
    """
    import os

    import boto3

    client = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "eu-west-1")),
    )
    model_id = os.getenv(
        "JUDGE_MODEL_ID",
        "eu.anthropic.claude-haiku-4-5-20251001-v1:0",
    )

    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 150, "temperature": 0.0},
    )
    text = response["output"]["message"]["content"][0]["text"]

    # Parse JSON — handle common LLM formatting quirks
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return json.loads(text)


def _build_ground_truth_summaries() -> tuple[str, str]:
    """Build compact summaries of catalog and FAQs for the judge prompt.

    Loaded once and cached. Provides the judge with the complete source of
    truth so it can detect fabrication vs real data.
    """
    from techshop_agent.config import load_catalog, load_faqs

    catalog = load_catalog()
    catalog_lines = [
        f"- {p['nombre']}: {p['precio']}€, category={p['categoria']}"
        for p in catalog
    ]
    catalog_summary = "\n".join(catalog_lines)

    faqs = load_faqs()
    faq_lines = [
        f"- Q: {f['pregunta']} → A: {f['respuesta']}"
        for f in faqs
    ]
    faq_summary = "\n".join(faq_lines)

    return catalog_summary, faq_summary


# Module-level cache for ground truth (loaded once per process)
_catalog_summary: str | None = None
_faq_summary: str | None = None


def _get_ground_truth() -> tuple[str, str]:
    global _catalog_summary, _faq_summary  # noqa: PLW0603
    if _catalog_summary is None:
        _catalog_summary, _faq_summary = _build_ground_truth_summaries()
    return _catalog_summary, _faq_summary


def faithfulness_evaluator(
    *, input: str, output: str, expected_output: str | None, metadata: dict | None, **kwargs
) -> Evaluation:
    """LLM-as-Judge: score response faithfulness to ground truth.

    Uses a separate LLM call to judge whether the agent's response is
    grounded in real data or contains fabrication. This catches F1
    (hallucination) and F2 (extrapolation) failures that keyword-based
    evaluators miss.

    The judge receives the full catalog and FAQ data as ground truth,
    following the RAGAS faithfulness evaluation pattern. This allows
    the judge to verify whether specific products, prices, and policies
    mentioned in the response actually exist.

    Returns 0.0–1.0 faithfulness score with an explanation.
    Falls back to None (skip) if the judge call fails, so a network
    error doesn't break the entire evaluation run.
    """
    catalog_summary, faq_summary = _get_ground_truth()

    prompt = _JUDGE_PROMPT.format(
        input=input,
        output=output or "(empty)",
        expected_output=expected_output or "Respond accurately using only catalog/FAQ data",
        catalog_summary=catalog_summary,
        faq_summary=faq_summary,
    )

    try:
        verdict = _call_judge(prompt)
        score = float(verdict.get("score", 0.5))
        reason = str(verdict.get("reason", "No reason provided"))
        # Clamp to [0, 1]
        score = max(0.0, min(1.0, score))
    except Exception as exc:
        logger.warning("LLM judge failed, skipping faithfulness score: %s", exc)
        return Evaluation(
            name="faithfulness",
            value=None,
            comment=f"Judge error: {exc}",
        )

    return Evaluation(
        name="faithfulness",
        value=round(score, 2),
        comment=reason,
    )


# ---------------------------------------------------------------------------
# Run-level evaluators
# ---------------------------------------------------------------------------


def average_score_evaluator(*, item_results, **kwargs) -> Evaluation:
    """Calculate average across all scope_adherence scores."""
    scores = [
        ev.value
        for result in item_results
        for ev in result.evaluations
        if ev.name == "scope_adherence" and ev.value is not None
    ]
    if not scores:
        return Evaluation(name="avg_scope_adherence", value=None)
    avg = sum(scores) / len(scores)
    return Evaluation(
        name="avg_scope_adherence",
        value=round(avg, 3),
        comment=f"Average over {len(scores)} items: {avg:.1%}",
    )


def average_hallucination_evaluator(*, item_results, **kwargs) -> Evaluation:
    """Calculate average hallucination check score."""
    scores = [
        ev.value
        for result in item_results
        for ev in result.evaluations
        if ev.name == "hallucination_check" and ev.value is not None
    ]
    if not scores:
        return Evaluation(name="avg_hallucination", value=None)
    avg = sum(scores) / len(scores)
    return Evaluation(
        name="avg_hallucination",
        value=round(avg, 3),
        comment=f"Average over {len(scores)} items: {avg:.1%}",
    )


def average_faithfulness_evaluator(*, item_results, **kwargs) -> Evaluation:
    """Calculate average faithfulness (LLM-as-judge) score."""
    scores = [
        ev.value
        for result in item_results
        for ev in result.evaluations
        if ev.name == "faithfulness" and ev.value is not None
    ]
    if not scores:
        return Evaluation(name="avg_faithfulness", value=None)
    avg = sum(scores) / len(scores)
    return Evaluation(
        name="avg_faithfulness",
        value=round(avg, 3),
        comment=f"LLM-as-judge average over {len(scores)} items: {avg:.1%}",
    )


def average_tool_usage_evaluator(*, item_results, **kwargs) -> Evaluation:
    """Calculate average tool_usage score."""
    scores = [
        ev.value
        for result in item_results
        for ev in result.evaluations
        if ev.name == "tool_usage" and ev.value is not None
    ]
    if not scores:
        return Evaluation(name="avg_tool_usage", value=None)
    avg = sum(scores) / len(scores)
    return Evaluation(
        name="avg_tool_usage",
        value=round(avg, 3),
        comment=f"Average over {len(scores)} items: {avg:.1%}",
    )


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------


@dataclass
class EvalResult:
    """Container for evaluation results with quality gate logic."""

    label: str
    total_cases: int = 0
    passed_cases: int = 0
    avg_scope_adherence: float | None = None
    avg_hallucination: float | None = None
    avg_response_quality: float | None = None
    avg_tool_usage: float | None = None
    avg_faithfulness: float | None = None
    details: list[dict] = field(default_factory=list)
    duration_seconds: float = 0.0

    def passes_threshold(self, threshold: float = 0.7) -> bool:
        """Check if all average scores meet the minimum threshold."""
        scores = [
            s
            for s in [
                self.avg_scope_adherence,
                self.avg_hallucination,
                self.avg_response_quality,
                self.avg_tool_usage,
                self.avg_faithfulness,
            ]
            if s is not None
        ]
        return all(s >= threshold for s in scores) if scores else False

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "avg_scope_adherence": self.avg_scope_adherence,
            "avg_hallucination": self.avg_hallucination,
            "avg_response_quality": self.avg_response_quality,
            "avg_tool_usage": self.avg_tool_usage,
            "avg_faithfulness": self.avg_faithfulness,
            "passes_threshold": self.passes_threshold(),
            "duration_seconds": round(self.duration_seconds, 2),
        }

    def summary(self) -> str:
        lines = [
            f"{'=' * 60}",
            f"  Evaluation Results — label: {self.label}",
            f"{'=' * 60}",
            f"  Total cases:          {self.total_cases}",
            f"  Duration:             {self.duration_seconds:.1f}s",
            f"{'─' * 60}",
            f"  DETERMINISTIC EVALUATORS",
            f"  Scope adherence:      {self._fmt(self.avg_scope_adherence)}",
            f"  Hallucination check:  {self._fmt(self.avg_hallucination)}",
            f"  Response quality:     {self._fmt(self.avg_response_quality)}",
            f"  Tool usage:           {self._fmt(self.avg_tool_usage)}",
            f"{'─' * 60}",
            f"  LLM-AS-JUDGE",
            f"  Faithfulness:         {self._fmt(self.avg_faithfulness)}",
            f"{'─' * 60}",
            f"  Quality Gate:         {'✅ PASS' if self.passes_threshold() else '❌ FAIL'}",
            f"{'=' * 60}",
        ]
        return "\n".join(lines)

    @staticmethod
    def _fmt(val: float | None) -> str:
        return f"{val:.1%}" if val is not None else "N/A"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


@observe(name="prompt_evaluation")
def run_evaluation(
    *,
    label: str = "staging",
    threshold: float = 0.7,
    dataset: list[dict] | None = None,
) -> EvalResult:
    """Run the full evaluation suite against a prompt label.

    This function:
    1. Creates or reuses the TechShop agent with the specified prompt label
    2. Runs every case in the evaluation dataset
    3. Applies all evaluators to each response
    4. Computes aggregate scores
    5. Returns an EvalResult with quality gate verdict

    Args:
        label: Langfuse prompt label to evaluate ("staging", "production", etc.)
        threshold: Minimum score to pass the quality gate (0.0–1.0)
        dataset: Override the default EVAL_DATASET (useful for testing)

    Returns:
        EvalResult with scores and quality gate verdict.
    """
    from techshop_agent.solution.prompt_provider import get_system_prompt

    eval_data = dataset or EVAL_DATASET
    start = time.monotonic()

    # Get the system prompt for this label
    system_prompt = get_system_prompt(label, cache_ttl_seconds=0)

    # Create agent with this prompt
    from techshop_agent.agent import create_agent

    agent = create_agent(system_prompt=system_prompt)

    # Define task function for Langfuse experiment runner
    def agent_task(*, item, **kwargs):
        query = item["input"] if isinstance(item, dict) else item.input
        return str(agent(query))

    # Run with Langfuse experiment runner
    langfuse = get_client()

    result = langfuse.run_experiment(
        name=f"techshop-eval-{label}",
        description=f"Evaluation of prompt label '{label}'",
        data=eval_data,
        task=agent_task,
        evaluators=[
            # Deterministic evaluators — fast, reproducible, keyword-based
            scope_adherence_evaluator,
            hallucination_evaluator,
            response_quality_evaluator,
            tool_usage_evaluator,
            # LLM-as-Judge — semantic, catches novel fabrication (F1, F2)
            faithfulness_evaluator,
        ],
        run_evaluators=[
            average_score_evaluator,
            average_hallucination_evaluator,
            average_tool_usage_evaluator,
            average_faithfulness_evaluator,
        ],
        metadata={"prompt_label": label, "threshold": threshold},
    )

    duration = time.monotonic() - start

    # Parse results
    eval_result = EvalResult(
        label=label,
        total_cases=len(eval_data),
        duration_seconds=duration,
    )

    # Extract run-level scores
    for ev in result.run_evaluations:
        if ev.name == "avg_scope_adherence":
            eval_result.avg_scope_adherence = ev.value
        elif ev.name == "avg_hallucination":
            eval_result.avg_hallucination = ev.value
        elif ev.name == "avg_faithfulness":
            eval_result.avg_faithfulness = ev.value
        elif ev.name == "avg_tool_usage":
            eval_result.avg_tool_usage = ev.value

    # Calculate average response quality from item results
    quality_scores = [
        ev.value
        for item_result in result.item_results
        for ev in item_result.evaluations
        if ev.name == "response_quality" and ev.value is not None
    ]
    if quality_scores:
        eval_result.avg_response_quality = round(sum(quality_scores) / len(quality_scores), 3)

    # Count passed cases (all evaluators returned 1.0)
    for item_result in result.item_results:
        all_passed = all(ev.value == 1.0 for ev in item_result.evaluations if ev.value is not None)
        if all_passed:
            eval_result.passed_cases += 1

    langfuse.flush()
    return eval_result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point for running evaluations."""
    parser = argparse.ArgumentParser(
        description="Run TechShop Agent evaluation suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m techshop_agent.evaluation --label staging
  python -m techshop_agent.evaluation --label staging --threshold 0.8
  python -m techshop_agent.evaluation --label production --json
        """,
    )
    parser.add_argument(
        "--label",
        default="staging",
        help="Langfuse prompt label to evaluate (default: staging)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Minimum score threshold for quality gate (default: 0.7)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output results as JSON instead of human-readable",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Load environment
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv(usecwd=True))

    print(f"\n🧪 Running evaluation against label: {args.label}")
    print(f"   Threshold: {args.threshold:.0%}\n")

    result = run_evaluation(label=args.label, threshold=args.threshold)

    if args.output_json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result.summary())

    # Exit with appropriate code for CI/CD
    sys.exit(0 if result.passes_threshold(args.threshold) else 1)


if __name__ == "__main__":
    main()

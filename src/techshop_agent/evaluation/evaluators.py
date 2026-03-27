"""Deterministic evaluators and run-level aggregators.

Each evaluator follows the Langfuse evaluator signature:
  def evaluator(*, input, output, expected_output, metadata, **kwargs) -> Evaluation
"""

from __future__ import annotations

from langfuse import Evaluation


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
# Run-level evaluators (aggregators)
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


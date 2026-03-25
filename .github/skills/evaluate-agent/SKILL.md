---
name: evaluate-agent
description: "Design and run evaluation suites for the TechShop agent to detect failures F1-F4 and guard against regressions. USE FOR: creating test datasets, running evaluations, analyzing results, setting up CI evaluation pipelines. DO NOT USE FOR: adding tracing (use langfuse-tracing), prompt changes (use prompt-versioning)."
---

# Evaluate Agent Skill

Design, implement, and run evaluation suites for the TechShop agent.

## When to use this skill
- Creating evaluation datasets for the four deliberate failures (F1–F4).
- Running evaluation suites and analyzing results.
- Setting up automated evaluation in CI/CD.
- Defining evaluation criteria and metrics.

## Evaluation framework

### Test dataset structure
```python
# tests/eval/test_dataset.py
EVAL_CASES = [
    {
        "id": "f1_semantic_search",
        "query": "I need a laptop for video editing",
        "failure_mode": "F1",
        "expected_behavior": "Uses catalog data only, no invented products",
        "expected_category": "product",
        "should_call_tool": "search_catalog",
    },
    {
        "id": "f2_faq_edge_case",
        "query": "Can I return a product after 45 days?",
        "failure_mode": "F2",
        "expected_behavior": "States 30-day policy, does not invent exceptions",
        "expected_category": "faq",
        "should_call_tool": "get_faq_answer",
    },
    {
        "id": "f3_out_of_scope",
        "query": "What's the best recipe for chocolate cake?",
        "failure_mode": "F3",
        "expected_behavior": "Declines, redirects to TechShop scope",
        "expected_category": "out_of_scope",
        "should_call_tool": None,
    },
    {
        "id": "f4_tool_skip",
        "query": "How much does the ProBook X1 cost?",
        "failure_mode": "F4",
        "expected_behavior": "Calls search_catalog, returns real price",
        "expected_category": "product",
        "should_call_tool": "search_catalog",
    },
]
```

### Evaluation criteria

| Criterion | How to measure | Failure mode |
|-----------|---------------|--------------|
| Factual accuracy | Response matches catalog/FAQ data | F1, F2 |
| Scope adherence | Out-of-domain queries get `out_of_scope` | F3 |
| Tool usage | Expected tool spans present in trace | F4 |
| Confidence calibration | High confidence only when grounded | F1, F2 |
| Safety | Guardrails catch adversarial inputs | All |

### Running evaluations with pytest
```python
import pytest
from techshop_agent.agent import TechShopAgent
from techshop_agent.responder import AgentResponse

@pytest.mark.parametrize("case", EVAL_CASES, ids=lambda c: c["id"])
def test_agent_evaluation(case, agent: TechShopAgent):
    response: AgentResponse = agent.process_query(case["query"])

    # Category check
    assert response.category == case["expected_category"]

    # Confidence check for out-of-scope
    if case["expected_category"] == "out_of_scope":
        assert response.requires_human or response.confidence == "low"
```

### Evaluation metrics
Track these metrics across evaluation runs:
- **Accuracy**: % of queries where response matches expected behavior.
- **Tool usage rate**: % of queries where expected tool was called.
- **Scope adherence**: % of out-of-domain queries correctly classified.
- **False positive rate**: % of valid queries incorrectly rejected by guardrails.
- **Latency p50/p95**: response time distribution.

## CI integration
Add to `Makefile`:
```makefile
eval:  ## Run evaluation suite
	pytest tests/eval/ -v --tb=short
```

## Verification
After creating evaluations:
1. Run `make test` to ensure eval tests integrate with existing suite.
2. Verify each failure mode has at least 3 test cases.
3. Check that evaluations are deterministic (no flaky tests from LLM non-determinism).

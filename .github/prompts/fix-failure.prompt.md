---
name: fix-failure
description: 'Diagnose and fix one of the four deliberate agent failures (F1-F4)'
agent: 'implementer-python'
tools:
  - search
  - read
  - editFiles
  - runInTerminal
  - terminalLastCommand
---

# Fix Deliberate Agent Failure

Diagnose and implement a fix for one of the four deliberate failures in the TechShop agent.

## Input

Which failure to fix: ${input:failure:F1, F2, F3, or F4}

## Failure Reference

### F1 — Hallucination (invents products)
- **Root cause**: `search_catalog` threshold too high (0.6) for semantic queries; returns empty results, agent hallucinates.
- **Fix direction**: Lower threshold or improve matching logic; add "no results found" guard.
- **Verify**: Trace shows `results_count > 0` for valid queries; agent never invents products.

### F2 — Extrapolation (confident wrong answers)
- **Root cause**: System prompt doesn't restrict to FAQ data; agent uses general knowledge.
- **Fix direction**: Add explicit instruction to only answer from FAQ data; admit uncertainty otherwise.
- **Verify**: LLM-as-judge confirms answers are grounded in FAQ content.

### F3 — Scope creep (answers out-of-domain)
- **Root cause**: System prompt too broad; lacks explicit scope boundaries.
- **Fix direction**: Add scope boundary in system prompt; add BanTopics guardrail.
- **Verify**: Out-of-domain queries get `out_of_scope` category in response.

### F4 — Tool selection gap (skips tool call)
- **Root cause**: Agent decides to answer from "knowledge" without calling catalog tool.
- **Fix direction**: Improve routing logic or add explicit tool-use instruction in system prompt.
- **Verify**: Trace shows tool spans for all product-related queries.

## Steps
1. Read the [agent spec](docs/architecture/agent_spec.md) for full failure details.
2. Identify the root cause in the code.
3. Write a failing test that demonstrates the failure.
4. Implement the fix.
5. Verify the test passes.
6. Run `make qa` for full validation.

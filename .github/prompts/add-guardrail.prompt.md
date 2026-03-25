---
name: add-guardrail
description: 'Add a new input or output guardrail scanner to the agent'
agent: 'guardian'
tools:
  - search
  - read
  - editFiles
  - runInTerminal
---

# Add Guardrail Scanner

Add a new guardrail scanner to the TechShop agent's `GuardrailsManager`.

## Input

Describe which scanner to add: ${input:scanner_type:e.g. PromptInjection, Toxicity, BanTopics, Anonymize, Relevance}

## Steps

1. **Read current state**: Review `src/techshop_agent/guardrails.py` and `src/techshop_agent/config.py`.
2. **Add scanner import**: Import the scanner from `llm_guard` (input scanners from `llm_guard.input_scanners`, output scanners from `llm_guard.output_scanners`).
3. **Configure scanner**: Add initialization in `GuardrailsManager.__init__()` with configurable thresholds.
4. **Add to scan pipeline**: Add the scanner call in `scan_input()` or `scan_output()` as appropriate.
5. **Add `@observe`**: Ensure the scanner call is traced with Langfuse.
6. **Add config flag**: Add enable/disable flag in `AgentConfig` if not already present.
7. **Write tests**: Add test cases in `tests/test_guardrails.py`:
   - Normal input passes the scanner.
   - Adversarial input is caught by the scanner.
   - Scanner disabled via config skips the check.
8. **Run QA**: Execute `make qa` to verify.

## Output
Summarize what was added and the test results.

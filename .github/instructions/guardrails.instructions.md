---
name: 'Guardrails Safety'
description: 'Rules for LLM Guard input/output safety scanners'
applyTo: "src/techshop_agent/guardrails.py"
---

Guardrails implementation rules:

- Input scanners: PromptInjection, Anonymize, Toxicity, BanTopics (competitor mentions), Secrets.
- Output validators: Relevance, BanTopics, NoRefusal, FactualConsistency (when context available).
- All scanners must be configurable via `GuardrailsManager` enable/disable flags from `AgentConfig`.
- Return a tuple of `(processed_text, is_safe: bool, metadata: dict)` from both `scan_input` and `scan_output`.
- Never silently swallow scanner exceptions — log them and return `is_safe=False` with the error in metadata.
- Include adversarial test cases: prompt injection attempts, PII in input, toxic language, off-topic queries.
- Wrap all scanner calls with `@observe` for traceability in Langfuse.
- Keep scanner thresholds conservative for a customer-facing agent (prefer false positives over false negatives).

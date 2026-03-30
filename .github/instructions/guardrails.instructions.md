---
name: 'Guardrails Safety'
description: 'Rules for Amazon Bedrock Guardrails input/output safety'
applyTo: "src/techshop_agent/guardrails.py"
---

Guardrails implementation rules:

- Use Amazon Bedrock Guardrails via the `apply_guardrail` API (boto3 `bedrock-runtime` client).
- Input scanning (`source='INPUT'`): content filters (PROMPT_ATTACK, INSULTS, HATE, SEXUAL, VIOLENCE), denied topics, word policy, sensitive information (PII).
- Output scanning (`source='OUTPUT'`): content filters, word policy (competitor brands), sensitive information.
- Guardrail policies are configured in AWS (Console or Terraform), not in Python code.
- Configuration via environment variables: `BEDROCK_GUARDRAIL_ID`, `BEDROCK_GUARDRAIL_VERSION` (default "DRAFT"), `AWS_DEFAULT_REGION`.
- All scanning must be configurable via `GuardrailsManager` enable/disable flags from `GuardrailsConfig`.
- Return a tuple of `(processed_text, is_safe: bool, metadata: dict)` from both `scan_input` and `scan_output`.
- When `action='GUARDRAIL_INTERVENED'`, set `is_safe=False` and use the replacement text from `outputs`.
- Parse `assessments` to extract triggered policy names into `metadata['scanners_triggered']`.
- Never silently swallow API exceptions — log them and return `is_safe=False` with the error in metadata.
- Include adversarial test cases: prompt injection attempts, PII in input, toxic language, off-topic queries.
- Wrap all API calls with `@observe` for traceability in Langfuse.
- Keep filter strengths conservative for a customer-facing agent (prefer false positives over false negatives).
- Skip gracefully when `guardrail_id` is not configured (return `is_safe=True, skipped=True`).

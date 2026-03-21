# Copilot Operating Constitution for this Repository

## Mission
Build and evolve a Strands Agent project in Python with AWS Bedrock, Langfuse observability, and Terraform-managed infrastructure, using strict Spec-Driven Development (SDD).

## Non-negotiable workflow
1. Plan first, code later: Requirements -> Design -> Tasks -> Implementation.
2. Do not implement when requirements/design/tasks are missing or unapproved.
3. Keep requirement-to-task-to-test traceability explicit in every implementation change.
4. Make atomic changes; avoid broad refactors unless explicitly requested.

## Implementation rules
- Prefer minimal, testable, reversible changes.
- Never hardcode secrets, tokens, credentials, or private endpoints.
- For Python changes, include or update tests in the same task.
- For Terraform changes, ensure formatting, validation, and security checks are considered.
- Preserve existing architecture boundaries in `src/techshop_agent/` and `infrastructure/terraform/`.

## Quality gates to run before finishing
- `ruff check src/ tests/ examples/`
- `ruff format --check src/ tests/ examples/`
- `pyright src/techshop_agent`
- `pytest tests/ -v`
- `bandit -q -r src/techshop_agent`
- `terraform -chdir=infrastructure/terraform fmt -recursive -check`
- `terraform -chdir=infrastructure/terraform validate`

## AI/RAG robustness expectations
- Add or maintain guardrails for input/output safety.
- Prefer deterministic structured responses where possible.
- Include observability metadata in design and implementation decisions.
- Include adversarial and regression tests for safety-sensitive behaviors.

## Cost and safety controls
- Keep conservative token limits for model calls.
- Avoid adding infrastructure resources without explicit need and justification.
- Require confirmation before destructive infrastructure actions.

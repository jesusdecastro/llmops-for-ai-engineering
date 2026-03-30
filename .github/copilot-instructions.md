# Copilot Operating Constitution for this Repository

## Project overview
TechShop Agent — a pedagogical AI customer-service agent for an electronics store, built with Python 3.11+, [Strands Agents](https://github.com/strands-agents/sdk-python) on AWS Bedrock, Langfuse observability, Bedrock Guardrails safety, and Terraform-managed infrastructure. The agent includes **four deliberate failures** (F1–F4) that students discover and fix through the LLMOps cycle.

## Repository layout
- `src/techshop_agent/` — agent source: `agent.py` (orchestrator), `config.py` (Pydantic settings), `guardrails.py` (input/output safety), `responder.py` (response contract), `data/` (catalog + FAQs JSON).
- `tests/` — pytest suite covering agent, catalog, FAQ, config, guardrails, observability, routing, response contract.
- `infrastructure/terraform/` — AWS VPC, EC2, SSM, CloudWatch, security groups.
- `infrastructure/docker/` — docker-compose for local Langfuse.
- `infrastructure/scripts/` — deploy, backup, config validation utilities.
- `examples/` — `basic_usage.py` for quick demo.
- `docs/` — architecture, deployment, project guides.
- `.kiro/` — Spec-Driven Development specs and steering.
- `.github/` — Copilot instructions, agents, prompts, skills, hooks.

## Build and validation commands
Always use `make` targets. Run these from the repository root:
- `make dev` — install package with dev dependencies (`uv sync`)
- `make lint` — `ruff check src/ tests/ examples/`
- `make format-check` — `ruff format --check src/ tests/ examples/`
- `make typecheck` — `pyright src/techshop_agent`
- `make test` — `pytest tests/ -v`
- `make security` — `bandit -q -r src/techshop_agent`
- `make qa` — all Python checks in sequence (lint + format-check + typecheck + test + security)
- `make tf-fmt` — `terraform -chdir=infrastructure/terraform fmt -recursive -check`
- `make tf-validate` — `terraform -chdir=infrastructure/terraform validate`
- `make tf-check` — both Terraform checks
- `make pre-commit` — `pre-commit run --all-files`
- `make example` — run `examples/basic_usage.py`

## Non-negotiable workflow (Spec-Driven Development)
1. Plan first, code later: Requirements → Design → Tasks → Implementation.
2. Do not implement when requirements/design/tasks are missing or unapproved.
3. Keep requirement-to-task-to-test traceability explicit in every implementation change.
4. Make atomic changes; avoid broad refactors unless explicitly requested.

## Implementation rules
- Prefer minimal, testable, reversible changes.
- Never hardcode secrets, tokens, credentials, or private endpoints.
- For Python changes, include or update tests in the same task.
- For Terraform changes, ensure formatting, validation, and security checks are considered.
- Preserve existing architecture boundaries in `src/techshop_agent/` and `infrastructure/terraform/`.
- Run `make qa` (Python) or `make tf-check` (Terraform) before marking any task done.

## Quality gates to run before finishing
- `ruff check src/ tests/ examples/`
- `ruff format --check src/ tests/ examples/`
- `pyright src/techshop_agent`
- `pytest tests/ -v`
- `bandit -q -r src/techshop_agent`
- `terraform -chdir=infrastructure/terraform fmt -recursive -check`
- `terraform -chdir=infrastructure/terraform validate`

## LLMOps expectations
- Wrap every LLM call and tool invocation with Langfuse `@observe` decorators.
- Version prompts in Langfuse; reference by name and label, never inline long prompts.
- Include trace metadata: `session_id`, `user_id`, `input_tokens`, `output_tokens`, `latency_ms`.
- Use structured `AgentResponse` (Pydantic) for all agent outputs.
- Add or maintain guardrails for input/output safety via Amazon Bedrock Guardrails.
- Include adversarial and regression tests for safety-sensitive behaviors.
- Prefer deterministic structured responses where possible.

## Cost and safety controls
- Keep conservative token limits for model calls (default max_tokens: 1024).
- Avoid adding infrastructure resources without explicit need and justification.
- Require confirmation before destructive infrastructure actions.

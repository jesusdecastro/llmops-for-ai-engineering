# Copilot Agent Operating Model

This document defines how to use Copilot agents, prompts, skills, and hooks in this LLMOps course repository.

## Agent roles

### Planning
- **`planner`**: Plans only (`requirements.md`, `design.md`, `tasks.md`). Read-only tools. Identifies LLMOps concerns early. Hands off to implementers.

### Implementation
- **`implementer-python`**: Implements approved Python tasks with TDD. References LLMOps and Python instructions. Hands off to reviewer or observer.
- **`implementer-terraform`**: Implements approved infrastructure tasks. Hands off to reviewer.
- **`observer`**: Langfuse instrumentation specialist. Adds `@observe` decorators, trace metadata, prompt versioning.
- **`guardian`**: LLM Guard specialist. Implements input/output safety scanners. Hands off to reviewer.
- **`evaluator`**: Evaluation specialist. Designs and runs test suites for F1–F4 failure detection.

### Review
- **`reviewer-security`**: Strict security/robustness review. Read-only. GO/NO-GO decision.

## Agent handoff topology

```
planner ──────┬──► implementer-python ──┬──► reviewer-security
              │                         └──► observer
              ├──► implementer-terraform ──► reviewer-security
              │
              └──► (evaluator, guardian used directly)

guardian ──────────────────────────────────► reviewer-security
```

## Workflow: Standard SDD cycle

1. **Plan**: Run `planner` → approve `requirements.md`, `design.md`, `tasks.md`.
2. **Implement**: Execute one task at a time with `implementer-python` or `implementer-terraform`.
3. **Instrument**: Use `observer` to add/verify Langfuse tracing.
4. **Evaluate**: Use `evaluator` to verify against failure modes.
5. **Review**: Run `reviewer-security` before merge.

## Workflow: LLMOps improvement cycle

1. **Observe**: Use `/trace-debug` to analyze agent behavior from Langfuse traces.
2. **Diagnose**: Identify failure mode (F1–F4) from trace patterns.
3. **Fix**: Use `/fix-failure` to implement the fix with TDD.
4. **Guard**: Use `/add-guardrail` to add safety scanners if needed.
5. **Evaluate**: Use `evaluator` to verify the fix and check for regressions.
6. **Deploy**: Use `/deploy-check` for pre-deployment validation.

## Skills (auto-loaded capabilities)

| Skill | Loaded when... |
|-------|---------------|
| `langfuse-tracing` | Working on Langfuse instrumentation |
| `prompt-versioning` | Managing system prompts in Langfuse |
| `evaluate-agent` | Creating or running evaluation suites |

## Required quality gates

**Python** (`make qa`):
- `ruff check src/ tests/ examples/`
- `ruff format --check src/ tests/ examples/`
- `pyright src/techshop_agent`
- `pytest tests/ -v`
- `bandit -q -r src/techshop_agent`

**Terraform** (`make tf-check`):
- `terraform -chdir=infrastructure/terraform fmt -recursive -check`
- `terraform -chdir=infrastructure/terraform validate`

## Hook guardrails

- **PreToolUse**: Blocks secrets in patches; asks confirmation for `terraform destroy`, `aws iam`, `rm -rf`.
- **PostToolUse**: Runs lint, format, and test after Python edits; runs fmt and validate after Terraform edits.

## Safety defaults

- No hardcoded secrets or credentials.
- Conservative token limits (default max_tokens: 1024).
- Explicit fallback behavior for all external services.
- Observability metadata on all critical AI flows.
- Guardrails enabled by default for customer-facing agent.

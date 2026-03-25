# Copilot Setup for LLMOps-Guided Development

This repository includes a comprehensive Copilot governance setup for Spec-Driven Development, LLMOps practices, Python AI agent work, and Terraform infrastructure safety.

## Configuration inventory

### Global rules (always-on)
- `.github/copilot-instructions.md` — project constitution, SDD workflow, build commands, quality gates, LLMOps expectations.

### Scope-specific instructions (applied by file pattern)

| File | Applies to |
|------|-----------|
| `python.instructions.md` | `src/**/*.py` — type hints, Pydantic, guardrails |
| `tests.instructions.md` | `tests/**/*.py` — TDD, adversarial cases, naming |
| `terraform.instructions.md` | `infrastructure/terraform/**/*.tf` — least privilege, no secrets |
| `docs.instructions.md` | `docs/**/*.md` — alignment, checklists |
| `llmops.instructions.md` | `src/**/*.py` — Langfuse `@observe`, tracing, prompt versioning |
| `guardrails.instructions.md` | `src/techshop_agent/guardrails.py` — LLM Guard scanners |
| `config.instructions.md` | `src/techshop_agent/config.py`, `infrastructure/config/**` — Pydantic config |
| `examples.instructions.md` | `examples/**/*.py` — self-contained, no hardcoded keys |
| `scripts.instructions.md` | `infrastructure/scripts/**` — safe bash, no secret leaks |

### Custom agents

| Agent | Role | Tools |
|-------|------|-------|
| `planner` | Plan-first SDD: requirements, design, tasks | read-only + web |
| `implementer-python` | Implement approved Python tasks with TDD | read + edit + terminal |
| `implementer-terraform` | Implement approved infrastructure tasks | read + edit + terminal |
| `reviewer-security` | Security/robustness review before merge | read-only |
| `observer` | Langfuse instrumentation and trace analysis | read + edit + terminal |
| `evaluator` | Evaluation suites for F1–F4 failure detection | read + edit + terminal |
| `guardian` | LLM Guard guardrails implementation | read + edit + terminal |

### Prompt files (slash commands)

| Command | Purpose | Agent |
|---------|---------|-------|
| `/qa` | Run all quality gates | default |
| `/trace-debug` | Analyze Langfuse traces for failures | observer |
| `/add-guardrail` | Add input/output guardrail scanner | guardian |
| `/deploy-check` | Pre-deployment validation checklist | default |
| `/fix-failure` | Diagnose and fix F1–F4 failures | implementer-python |
| `/instrument` | Add Langfuse instrumentation | observer |
| `/kiro-spec-*` | Spec-Driven Development workflow | see SDD docs |

### Skills (portable capabilities)

| Skill | Purpose |
|-------|---------|
| `langfuse-tracing` | Patterns and conventions for `@observe` decorators |
| `prompt-versioning` | Langfuse prompt management and versioning workflow |
| `evaluate-agent` | Evaluation framework for F1–F4 failure detection |

### Hooks (lifecycle guardrails)
- `pretooluse-risk-guard.json` — blocks secrets in patches, asks confirmation for destructive commands.
- `posttooluse-quality-gates.json` — runs lint/format/test after edits, Terraform checks for `.tf` files.

## Recommended workflows

### Standard development
1. `planner` → generate requirements/design/tasks.
2. `implementer-python` → implement one task at a time with TDD.
3. `/qa` → run all quality gates.
4. `reviewer-security` → security review before merge.

### LLMOps cycle
1. `observer` → instrument code with Langfuse tracing.
2. `evaluator` → create evaluation datasets and run suites.
3. `/trace-debug` → analyze traces to identify F1–F4 failures.
4. `/fix-failure` → implement fixes with TDD.
5. `/deploy-check` → pre-deployment validation.

### Adding guardrails
1. `guardian` → implement scanner using `/add-guardrail`.
2. `reviewer-security` → review guardrail changes.
3. `/qa` → validate all quality gates pass.

## Local quality gates

```bash
make qa          # Python: lint + format + typecheck + test + security
make tf-check    # Terraform: fmt + validate
make pre-commit  # All pre-commit hooks
```

## Notes

- Hooks in `.github/hooks/` run automatically during agent workflows.
- For destructive cloud actions, explicit human confirmation is required.
- Agent handoffs provide guided transitions between workflow steps.
- Skills load on-demand when Copilot detects relevant tasks.

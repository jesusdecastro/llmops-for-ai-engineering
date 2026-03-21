# Copilot setup for guided development

This repository includes a baseline Copilot governance setup for SDD, Python AI/RAG work, and Terraform safety.

## Included configuration

- Global rules: `.github/copilot-instructions.md`
- Scope rules:
  - `.github/instructions/python.instructions.md`
  - `.github/instructions/tests.instructions.md`
  - `.github/instructions/terraform.instructions.md`
  - `.github/instructions/docs.instructions.md`
- Custom agents:
  - `.github/agents/planner.agent.md`
  - `.github/agents/implementer-python.agent.md`
  - `.github/agents/implementer-terraform.agent.md`
  - `.github/agents/reviewer-security.agent.md`
- Hook templates (preview): `.github/hooks/`

## Recommended workflow

1. Use `planner` for requirements/design/tasks.
2. Use `implementer-python` for approved Python tasks.
3. Use `implementer-terraform` for approved IaC tasks.
4. Run `reviewer-security` before merge.

## Local quality gates

Run the following before merge:

```bash
make qa
make tf-check
pre-commit run --all-files
```

## Notes

- Hooks in `.github/hooks/` are templates for Copilot Hooks preview; load them with `/hooks` and adapt to your environment.
- For destructive cloud actions, require explicit human confirmation.

# Copilot Agent Operating Model (MVP)

This document defines how to use Copilot agents in this repository to keep SDD discipline, quality, and safety controls for Python + AI/RAG + Terraform.

## Agent roles

- `planner`: plans only (`requirements.md`, `design.md`, `tasks.md`) with traceability and done criteria.
- `implementer-python`: implements approved Python tasks, including tests and quality checks.
- `implementer-terraform`: implements approved Terraform tasks with least-privilege and validation gates.
- `reviewer-security`: performs security/robustness review and prioritizes findings by severity.

## Workflow

1. Plan phase: run planner and approve artifacts.
2. Implementation phase: execute one task at a time with the matching implementer.
3. Review phase: run reviewer-security before merge.

## Required quality gates

Python:
- `ruff check src/ tests/ examples/`
- `ruff format --check src/ tests/ examples/`
- `pyright src/techshop_agent`
- `pytest tests/ -v`
- `bandit -q -r src/techshop_agent`

Terraform:
- `terraform -chdir=infrastructure/terraform fmt -recursive -check`
- `terraform -chdir=infrastructure/terraform validate`

## Hook guardrails

- `PreToolUse` blocks or asks confirmation for risky/destructive operations.
- `PostToolUse` runs quality gates after file edits.

## Safety defaults

- No hardcoded secrets or credentials.
- Prefer conservative token limits and explicit fallback behavior.
- Keep observability metadata for critical AI/RAG flows.

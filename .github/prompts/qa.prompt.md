---
name: qa
description: 'Run all quality gates (lint, format, typecheck, test, security)'
agent: 'agent'
tools:
  - runInTerminal
  - terminalLastCommand
---

# Run All Quality Gates

Execute the full quality assurance pipeline for this project. Run each step sequentially and report results.

## Steps

1. **Lint**: `make lint`
2. **Format check**: `make format-check`
3. **Type check**: `make typecheck`
4. **Tests**: `make test`
5. **Security scan**: `make security`
6. **Terraform format** (if Terraform files changed): `make tf-fmt`
7. **Terraform validate** (if Terraform files changed): `make tf-validate`

## Output

Report a summary table:

| Check | Status | Details |
|-------|--------|---------|
| Lint | PASS/FAIL | errors found |
| Format | PASS/FAIL | files needing format |
| Types | PASS/FAIL | type errors |
| Tests | PASS/FAIL | passed/failed count |
| Security | PASS/FAIL | issues found |
| TF Format | PASS/FAIL/SKIP | |
| TF Validate | PASS/FAIL/SKIP | |

If any check fails, provide actionable guidance to fix the issues.

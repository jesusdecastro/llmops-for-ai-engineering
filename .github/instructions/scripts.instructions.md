---
name: 'Infrastructure Scripts'
description: 'Rules for deployment, backup, and utility scripts'
applyTo: "infrastructure/scripts/**"
---

Infrastructure script rules:

- All scripts must include `set -euo pipefail` (bash) for safe execution.
- Never echo secrets or credentials to stdout/logs.
- Include `--dry-run` or equivalent preview mode where possible.
- Validate prerequisites (CLI tools, credentials, env vars) before executing destructive actions.
- Use meaningful exit codes: 0 = success, 1 = validation failure, 2 = runtime error.
- Log operations with timestamps for auditability.

---
applyTo: "infrastructure/terraform/**/*.tf"
---

Terraform rules for this project:

- Prefer least-privilege security defaults.
- Keep modules/resources explicit and tagged with project/environment metadata.
- Never hardcode secrets; use variables, SSM, or secret managers.
- Ensure every change passes `terraform fmt` and `terraform validate`.
- Call out blast radius and rollback path in commit/PR notes.
- Avoid destructive changes unless explicitly requested and acknowledged.

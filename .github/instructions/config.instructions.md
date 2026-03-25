---
name: 'Configuration and Environment'
description: 'Rules for Pydantic config, environment variables, and secrets'
applyTo: "src/techshop_agent/config.py,infrastructure/config/**"
---

Configuration rules for this project:

- All configuration flows through `AgentConfig` (Pydantic `BaseModel` in `config.py`).
- Load secrets exclusively from environment variables; never hardcode or commit them.
- Use Pydantic field validators for constraints: `max_tokens > 0`, `temperature` in `[0, 1]`.
- `validate_config()` must check that mandatory env vars are present before agent startup.
- Group config by concern: AWS Bedrock, Langfuse, OpenTelemetry, Guardrails.
- Keep `.env.example` or `*.yaml.example` files updated when adding new config fields.
- For infrastructure config, use SSM Parameter Store or Secrets Manager references in Terraform.

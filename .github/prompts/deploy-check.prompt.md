---
name: deploy-check
description: 'Pre-deployment validation checklist for the TechShop agent'
agent: 'agent'
tools:
  - search
  - read
  - runInTerminal
  - terminalLastCommand
---

# Pre-Deployment Validation Checklist

Run a comprehensive pre-deployment check before releasing the TechShop agent.

## Checklist

### 1. Code Quality
- [ ] `make lint` passes
- [ ] `make format-check` passes
- [ ] `make typecheck` passes
- [ ] `make security` passes (no bandit findings)

### 2. Tests
- [ ] `make test` passes (all tests green)
- [ ] Adversarial guardrail tests included
- [ ] Edge-case catalog/FAQ tests pass

### 3. Configuration
- [ ] All required env vars documented in `.env.example` or config docs
- [ ] No hardcoded secrets in `src/` or `infrastructure/`
- [ ] `AgentConfig.validate_config()` covers all mandatory fields

### 4. Observability
- [ ] All LLM calls have `@observe` decorators
- [ ] System prompt resolved from Langfuse (with fallback)
- [ ] Trace metadata includes token counts and session info
- [ ] Guardrail results traced

### 5. Infrastructure (if deploying)
- [ ] `make tf-check` passes
- [ ] Security groups are restrictive
- [ ] SSM parameters configured for secrets
- [ ] CloudWatch alarms set for critical metrics

### 6. LLMOps Readiness
- [ ] Prompt versioned in Langfuse with name and label
- [ ] Evaluation dataset prepared for F1–F4 failure detection
- [ ] Guardrails enabled for both input and output
- [ ] Cost controls: max_tokens set conservatively

## Output
Report pass/fail for each section with details on any failures.

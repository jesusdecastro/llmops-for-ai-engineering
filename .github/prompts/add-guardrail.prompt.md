---
name: add-guardrail
description: 'Add a new input or output guardrail scanner to the agent'
agent: 'guardian'
tools:
  - search
  - read
  - editFiles
  - runInTerminal
---

# Add Guardrail Scanner

Add a new guardrail policy to the TechShop agent's Bedrock Guardrails configuration.

## Input

Describe which policy to add: ${input:policy_type:e.g. content filter, denied topic, word policy, sensitive information}

## Steps

1. **Read current state**: Review `src/techshop_agent/guardrails.py` and the guardrail configuration in AWS.
2. **Update AWS guardrail**: Add the new policy to the guardrail in the AWS Console or via `boto3.client('bedrock').update_guardrail()`.
3. **Update assessment parsing**: If the new policy introduces a new assessment type, update `_parse_assessments()` in `guardrails.py` to extract the triggered names.
4. **Add `@observe`**: Ensure the scan calls remain traced with Langfuse.
5. **Write tests**: Add test cases in `tests/test_guardrails.py`:
   - Normal input passes the guardrail.
   - Adversarial input is caught by the new policy.
   - Scanner disabled via config skips the check.
6. **Run QA**: Execute `make qa` to verify.

## Output
Summarize what was added and the test results.

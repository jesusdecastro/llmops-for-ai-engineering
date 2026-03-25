---
name: prompt-versioning
description: "Manage and version system prompts in Langfuse for the TechShop agent. USE FOR: creating new prompt versions, updating prompt content, switching active prompts by label, implementing fallback logic. DO NOT USE FOR: adding tracing (use langfuse-tracing skill)."
---

# Prompt Versioning Skill

Manage system prompts in Langfuse with proper versioning, labeling, and fallback strategies.

## When to use this skill
- Creating a new version of the TechShop agent's system prompt.
- Updating prompt content to fix agent failures (F1–F4).
- Switching which prompt version is active via labels (`latest`, `production`, `staging`).
- Implementing prompt resolution with hardcoded fallback.

## How prompt versioning works in this project

### Architecture
```
Langfuse Prompt Registry
├── techshop-system-prompt (name)
│   ├── v1 (label: production) ← currently active
│   ├── v2 (label: staging)   ← being tested
│   └── v3 (label: latest)    ← newest version
```

### Prompt resolution in code
```python
from langfuse import Langfuse

FALLBACK_SYSTEM_PROMPT = """You are a helpful customer service agent for TechShop..."""

def get_system_prompt(config: AgentConfig) -> str:
    """Resolve system prompt from Langfuse with fallback."""
    try:
        client = Langfuse()
        prompt = client.get_prompt(
            name=config.langfuse_prompt_name,
            label=config.langfuse_prompt_label,
        )
        return prompt.compile()
    except Exception:
        return FALLBACK_SYSTEM_PROMPT
```

### Configuration
- `AgentConfig.langfuse_prompt_name` — prompt name in Langfuse (default: `"techshop-system-prompt"`).
- `AgentConfig.langfuse_prompt_label` — which label to fetch (default: `"production"`).

## Prompt versioning workflow

### 1. Create initial prompt
Upload the baseline system prompt to Langfuse with label `production`.

### 2. Iterate on a fix
When fixing a failure (e.g., F3 scope creep):
1. Create a new prompt version with the fix.
2. Label it `staging`.
3. Update `AgentConfig.langfuse_prompt_label` to `staging` in test environment.
4. Run evaluation suite to verify the fix.
5. If pass, relabel as `production`.

### 3. Rollback
If a new prompt version causes regressions:
1. Change the `production` label back to the previous version in Langfuse.
2. No code change needed — the agent resolves by label.

## Prompt content guidelines
- Include explicit scope boundaries: "You are a customer service agent for TechShop, an electronics store."
- List what the agent should NOT do: "Do not answer questions about politics, health, or competitors."
- Require tool usage: "Always search the catalog before answering product questions."
- Require grounding: "Only answer FAQ questions using the provided FAQ data."
- Specify response format: "Respond with a structured answer including confidence level."

## Verification
After changing prompts:
1. Verify the prompt is resolvable: test with `langfuse_client.get_prompt(name, label)`.
2. Run evaluation suite for the relevant failure mode.
3. Check that fallback still works when Langfuse is unreachable.

# Copilot Hooks (Preview)

This folder contains baseline hook definitions for operational guardrails.

Suggested setup in VS Code:
1. Open Copilot Chat and run `/hooks`.
2. Import or replicate rules from the JSON files in this folder.
3. Start in `ask` mode for risky operations, then tighten to `block` where appropriate.

Included policies:
- `pretooluse-risk-guard.json`: protects destructive/high-risk operations.
- `posttooluse-quality-gates.json`: suggests quality checks after edits.

Adjust commands to your local environment and CI strategy.

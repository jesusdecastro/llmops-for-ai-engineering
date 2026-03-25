# GitHub Copilot Customization Guide for LLMOps Projects

> **Reference guide** synthesized from official VS Code docs (March 2026) and applied to this LLMOps course repository.

## 1. Customization Primitives

GitHub Copilot in VS Code provides five customization primitives. Each serves a distinct purpose and they compose together.

### 1.1 Instructions (always-on rules)

| File | Scope | Applied |
|------|-------|---------|
| `.github/copilot-instructions.md` | Repository-wide | Every request automatically |
| `AGENTS.md` (root) | Repository-wide | Every request automatically |
| `.github/instructions/*.instructions.md` | File-specific via `applyTo` glob | When working on matching files |

**Best practices:**
- Keep `copilot-instructions.md` under 2 pages — it is prepended to every request.
- Use `applyTo` globs in `.instructions.md` files to target specific file types (e.g., `src/**/*.py`, `tests/**/*.py`).
- Include the *reasoning* behind rules (e.g., "Use `date-fns` because `moment.js` is deprecated").
- Show preferred/avoided patterns with concrete code examples.
- Focus on non-obvious rules; skip what linters already enforce.
- Reference instructions from agents and prompts via Markdown links to avoid duplication.

### 1.2 Agents (specialized personas)

| File | Location | Purpose |
|------|----------|---------|
| `*.agent.md` | `.github/agents/` | Task-specific personas with tool/model restrictions |

**Key frontmatter fields:**
- `description` — shown in chat; helps agent discovery.
- `tools` — restrict available tools (principle of least privilege).
- `agents` — list subagents this agent can invoke.
- `model` — preferred model for this agent.
- `handoffs` — sequential workflow transitions between agents.
- `user-invocable` / `disable-model-invocation` — control visibility.

**Best practices:**
- Give each agent a single well-defined responsibility.
- Restrict tools: planning agents get read-only tools; implementation agents get editing tools.
- Reference instruction files in the body via Markdown links instead of duplicating rules.
- Use handoffs for workflows: Planner → Implementer → Reviewer.
- Set `model` when a task benefits from a specific model's strengths.

### 1.3 Prompts (reusable slash commands)

| File | Location | Purpose |
|------|----------|---------|
| `*.prompt.md` | `.github/prompts/` | Repeatable tasks invoked via `/command-name` |

**Key frontmatter fields:**
- `agent` — which agent runs this prompt (`ask`, `agent`, `plan`, or custom agent name).
- `tools` — override the agent's tool list for this specific prompt.
- `model` — override the model for this prompt.

**Best practices:**
- One prompt per workflow step (e.g., `/deploy-check`, `/trace-analyze`).
- Link to instruction files for standards; keep prompt body focused on the task.
- Use `${input:variableName}` for user-supplied parameters.
- Use `#tool:<tool-name>` to reference specific tools.
- Tool priority: prompt tools > agent tools > default tools.

### 1.4 Skills (portable capabilities)

| File | Location | Purpose |
|------|----------|---------|
| `SKILL.md` | `.github/skills/<name>/` | Reusable capabilities with scripts, examples, resources |

**Key differences from instructions:**
- Skills can include scripts, templates, and other resources alongside instructions.
- Skills load progressively (only when relevant).
- Skills are portable across VS Code, Copilot CLI, and Copilot coding agent.
- Skills are invocable as `/skill-name` slash commands.

**Best practices:**
- One skill per capability (e.g., `langfuse-tracing`, `prompt-versioning`).
- Directory name must match the `name` field in SKILL.md.
- Include runnable scripts and examples in the skill directory.
- Use `description` to help Copilot auto-discover the skill.

### 1.5 Hooks (lifecycle guardrails)

| File | Location | Purpose |
|------|----------|---------|
| `*.json` | `.github/hooks/` | Automated checks at PreToolUse / PostToolUse events |

**Best practices:**
- PreToolUse: block/ask for dangerous operations (secrets in patches, destructive commands).
- PostToolUse: run quality gates after edits (lint, format, test).
- Keep hooks fast to avoid slowing down the agent loop.

## 2. How Primitives Compose

```
┌─────────────────────────────────────────────────────────────────┐
│                    User invokes Agent                           │
│                                                                 │
│  copilot-instructions.md  ← always injected                    │
│  AGENTS.md                ← always injected                    │
│  *.instructions.md        ← injected when applyTo matches      │
│  agent.md body            ← agent-specific instructions         │
│                                                                 │
│  User types /prompt-name  → prompt body injected                │
│  Agent auto-loads skill   → SKILL.md body loaded on-demand      │
│                                                                 │
│  PreToolUse hooks         ← before each tool call               │
│  PostToolUse hooks        ← after each tool call                │
└─────────────────────────────────────────────────────────────────┘
```

**Key principle:** Instructions define WHAT rules to follow. Agents define WHO (persona + tools). Prompts define WHEN (specific task trigger). Skills define HOW (portable capabilities). Hooks enforce GUARDRAILS (automated safety).

## 3. Architecture for This LLMOps Course

### Agent Topology

```
                    ┌──────────┐
                    │  planner │ (read-only)
                    └────┬─────┘
                         │ handoff
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
   ┌──────────┐  ┌──────────────┐  ┌──────────────┐
   │impl-py   │  │impl-terraform│  │impl-langfuse │
   └────┬─────┘  └──────┬───────┘  └──────┬───────┘
        │               │                 │
        └───────────────┼─────────────────┘
                        │ handoff
                  ┌─────▼──────┐
                  │  reviewer  │ (read-only)
                  │  security  │
                  └────────────┘
```

### Instruction Layers

| Layer | File | Scope |
|-------|------|-------|
| Constitution | `copilot-instructions.md` | SDD workflow, quality gates, security |
| Python rules | `python.instructions.md` | Type hints, Pydantic, guardrails |
| Test rules | `tests.instructions.md` | TDD, adversarial, naming |
| Terraform rules | `terraform.instructions.md` | Least privilege, no secrets |
| Docs rules | `docs.instructions.md` | Alignment, checklists |
| LLMOps rules | `llmops.instructions.md` | Langfuse, prompts, tracing |
| Guardrails rules | `guardrails.instructions.md` | LLM Guard, safety |
| Config/YAML rules | `config.instructions.md` | Environment, Pydantic config |

### Skills

| Skill | Purpose |
|-------|---------|
| `langfuse-tracing` | Instrument code with Langfuse decorators and traces |
| `prompt-versioning` | Version and manage prompts in Langfuse |
| `evaluate-agent` | Run evaluation suites with promptfoo or custom harness |

### Prompts

| Prompt | Purpose |
|--------|---------|
| `/qa` | Run all quality gates |
| `/trace-debug` | Analyze a Langfuse trace for issues |
| `/add-guardrail` | Add input/output guardrail to agent |
| `/deploy-check` | Pre-deployment validation checklist |

## 4. Naming Conventions

- **Instructions:** `<domain>.instructions.md` — descriptive, kebab-case
- **Agents:** `<role>.agent.md` — role-based naming
- **Prompts:** `<verb>-<noun>.prompt.md` — action-oriented
- **Skills:** `<domain>-<capability>/SKILL.md` — capability-based
- **Hooks:** `<event>-<purpose>.json` — event-prefixed

## 5. Anti-patterns to Avoid

1. **Duplicating instructions** across agents and prompts — use Markdown links instead.
2. **Overloading copilot-instructions.md** — it's injected in every request; keep it concise.
3. **Unrestricted tool lists** in agents — always scope tools to what the agent needs.
4. **Skipping hooks** — they provide automated safety nets that catch mistakes early.
5. **Monolithic prompts** — split complex workflows into agent handoffs.
6. **Missing `applyTo`** in instructions — without it, the file is never auto-applied.

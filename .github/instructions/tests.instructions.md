---
applyTo: "tests/**/*.py"
---

Testing rules for this project:

- Tests must map to explicit behavior, not implementation details.
- Cover success path, edge cases, and failure path.
- Keep tests deterministic and isolated (no hidden network dependencies).
- Prefer fixtures over duplicated setup.
- For safety-critical logic (guardrails, validation), include adversarial cases.
- Name tests clearly: `test_<unit>_<behavior>`.

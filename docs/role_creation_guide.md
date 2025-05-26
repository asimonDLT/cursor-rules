# Cursor Persona Creation Kit (v1.0)

This document provides a standardized framework for creating new executive or specialist personas in Cursor. By following this guidance, your team can develop clean, lightweight, and scalable roles that enhance AI collaboration without bloating prompts or creating conflicts.

---

## A. Governance Checklist

To ensure consistency and efficiency, please adhere to the following rules when creating a new role file.

1.  **File Name:** Choose a short, unique, and descriptive name for the role (e.g., `cso`, `frontend_designer`, `qa_lead`). This name will be used to invoke the persona. Start at `v1.0`; bump minor (`v1.1`) for wording tweaks, major (`v2.0`) for changed mandates.
2.  **Define Its Logic:** The file should exclusively contain the persona's perspective, decision-making logic, and guiding principles. Rules related to tooling (e.g., linters, compilers) or cloud environments should be defined in separate, appropriate rule files.
3.  **Use Essential Front-Matter:** Every role file must begin with the following YAML front-matter to be recognized by Cursor as an on-demand agent.
    ```yaml
    ---
    rule_type: Agent Requested
    description: <A one-sentence summary of the role's purpose and scope.>
    # Example: description: Senior security perspective for risk & compliance.
    ---
    ```
    > **Important:** Project-level rules override persona rules if directives clash.

    Save the file under `.cursor/rules/roles/`.
4.  **Avoid Globs (Usually):** Do not include file `glob` patterns unless the role should automatically attach to specific file types. This is a rare requirement for persona-based rules.
5.  **Keep It Lean:** To protect your token budget and ensure fast performance, limit the file to under 150 lines (~3 KB / <150 lines). A pre-commit hook will enforce this limit.
6.  **Add a Precedence Note:** To prevent ambiguity, explicitly state that project-level rules will override the persona's rules if they conflict.
7.  **End with an Output Template:** Conclude the file with a short, standardized output template to ensure the persona's responses are predictable and actionable.
8.  **No Undocumented Fields:** Do not use internal or undocumented fields like `alwaysApply` or `@context`, as these can break with future updates.

---

## B. Reusable Role Template

Copy the contents of this template to create a new role. Save the new file as `<role_name>.mdc` in your repository's `.cursor/rules/roles/` directory.

```markdown
---
rule_type: Agent Requested              # ← Do not change this value.
description: |-
  {{ROLE_NAME}} perspective for {{PRIMARY_SCOPE}}. Opt-in via @{{ROLE_NAME}}.
---

# {{ROLE_DISPLAY_TITLE}} (v{{VERSION}})

**Purpose**
{{PURPOSE_1_SENTENCE}}

**Decision charter**
1.  **Primary mandate** – {{MANDATE_LINE}}
2.  **Scope boundaries** – *In:* {{IN_SCOPE}} / *Out:* {{OUT_OF_SCOPE}}
3.  **Success =** {{SUCCESS_METRIC_OR_EXIT_CRITERIA}}

**Guiding principles**
- {{PRINCIPLE_1}}
- {{PRINCIPLE_2}}
- {{PRINCIPLE_3}}

**Preferred evidence & inputs**
- {{EVIDENCE_TYPE_1}} (e.g., threat model, Figma mockup, ROI calculation)
- {{EVIDENCE_TYPE_2}}

> *Project Rules override this Role if they conflict.*
> *Last reviewed: YYYY-MM-DD; next scheduled review in 90 days.*

## Output Template

{{ROLE_DISPLAY_TITLE}} feedback:

{{POINT_1}}
{{POINT_2}}

---
Decision: <GO / NO-GO / REVISE>
Next Steps:

{{NEXT_STEP_1}}
{{NEXT_STEP_2}}

| Placeholder         | Example             |
| ------------------- | ------------------- |
| `{{ROLE_NAME}}`     | `cso`               |
| `{{PRIMARY_SCOPE}}` | "risk & compliance" |

---

## C. Maintenance

- **Review Quarterly:** Add a "Last reviewed" note to each persona. Schedule a quarterly review to keep personas relevant as team strategies evolve.

---

## D. Pre-commit Hook

Add the following script to your repository as `.lint-mdc.sh`:

```bash
# .lint-mdc.sh
lines=$(wc -l < "$1")
if [ "$lines" -gt 150 ]; then
  echo "❌ $1 exceeds 150 lines."
  exit 1
fi
```

Then, reference it in your `.pre-commit-config.yaml`.

---
name: commit-message
description: Generate a structured git commit message (type/scope subject, what, why, how, traceability footer).
---

You generate a single git commit message using the template below. Each section answers a different question — no section should repeat information from another.

## Rules

- Output ONLY the final commit message. Do not include these instructions or any surrounding explanation.
- The subject line MUST be 50 characters or fewer (hard limit: 72).
- Capitalize the first word after the colon in the subject line.
- Do not end the subject line with a period.
- Use present tense, imperative mood ("Add feature" not "Added feature" or "Adds feature").
- Separate each section with a blank line.
- Wrap all body lines at 72 characters.
- Do not mention test-only changes in the bullet list.
- Omit the footer section entirely if there are no issues, breaking changes, or co-authors to reference.

## Subject line types

Use one of these prefixes:

- `feat` - New feature or capability
- `fix` - Bug fix
- `refactor` - Code restructuring without behavior change
- `docs` - Documentation only
- `test` - Adding or updating tests only
- `build` - Build system or dependency changes
- `ci` - CI/CD configuration changes
- `perf` - Performance improvement
- `style` - Formatting, whitespace, linting (no logic change)
- `chore` - Maintenance tasks that don't fit above

## Output format (exact structure)

```
<type>(<scope>): <subject, imperative, ≤50 chars>

<WHAT: 2-3 lines expanding on the subject — what this
change does in full detail>

<WHY: 2-3 lines explaining the problem or motivation
that made this change necessary>

- <HOW: implementation detail + rationale for that choice>
- <HOW: implementation detail + rationale for that choice>

<Footer: Fixes #, Closes #, BREAKING CHANGE, Co-authored-by>
```

## Section details

1. **Subject** — `type(scope): description` in imperative mood. The scope is the module, component, or area affected (e.g., `auth`, `dashboard`, `orders`). Target 50 characters. This answers WHAT at a glance.

2. **What** — 2-3 sentences expanding the subject into a full description of the change. A reader should understand the complete scope of the change from this paragraph alone. Do not explain why or how here.

3. **Why** — 2-3 sentences explaining the problem, motivation, or context that made this change necessary. What was broken, missing, or suboptimal? Do not describe the change itself here.

4. **How** — A bullet list (use `-` bullets) of notable implementation details. Each bullet pairs a specific change with the rationale behind that choice. Skip trivial or obvious changes. Skip test-only items.

5. **Footer** — Issue references (`Fixes #123`, `Closes #456`), `BREAKING CHANGE: description`, or `Co-authored-by: Name <email>`. Omit entirely if none apply.

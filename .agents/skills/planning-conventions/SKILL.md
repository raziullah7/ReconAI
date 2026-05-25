---
name: planning-conventions
description: Shared conventions for the feature planning agent chain (@product-manager, @bdd-designer, @architect, @spec-designer, @plan-designer, @phase-designer, and their domain subagents). Load this at the start of any planning agent session.
compatibility: opencode
metadata:
  audience: engineers
  workflow: planning
---

Shared conventions for the feature planning document chain.
Individual planning agents define what each document creates;
this file defines how they coexist.

## Planning Agents

| Agent                 | Mode     | Owns                          |
| --------------------- | -------- | ----------------------------- |
| `@product-manager`    | primary  | `FEATURE_NAME-PRD.md`         |
| `@bdd-designer`       | primary  | `FEATURE_NAME-BDD.md`         |
| `@architect`          | primary  | `FEATURE_NAME-ARCH.md`        |
| `@spec-designer`      | primary  | `FEATURE_NAME-SPEC.md`        |
| `@plan-designer`      | primary  | `FEATURE_NAME-PLAN.md`        |
| `@phase-designer`     | primary  | `FEATURE_NAME-PHASE-{N}.md`   |
| `@data-modeler`       | subagent | `FEATURE_NAME-MODELS.md`      |
| `@config-designer`    | subagent | `FEATURE_NAME-CONFIG.md`      |
| `@api-designer`       | subagent | `FEATURE_NAME-API.md`         |
| `@interface-designer` | subagent | `FEATURE_NAME-DEFINITIONS.md` |
| `@ui-flow-designer`   | subagent | `FEATURE_NAME-UI_UX.md`       |
| `@test-strategist`    | subagent | `FEATURE_NAME-TESTING.md`     |

Subagents are invoked only by the primary orchestrators, never
directly by the user.

## Planning Document Hierarchy

**PRD + BDD → ARCH → SPEC → PLAN → PHASE PLAN**

PRD captures product intent. BDD formulates product intent into
concrete business-readable examples before technical design begins.
Each later document deepens the one before it into progressively more technical detail. Information flows
forward through requirement IDs and markdown references, not
duplication.

## Document Ownership

Each fact has exactly one canonical owner. If a fact would need
updates in multiple planning files when it changes, it is in
the wrong place.

| Document       | Canonical Owner Of                                                                                                                                                                                              |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PRD.md`       | Product intent: problem, target users/personas, product goals, non-goals, user stories, functional requirements, acceptance criteria, success metrics, product constraints, and product open questions          |
| `BDD.md`       | Business-readable examples: Gherkin Feature/Rule/Scenario content, concrete acceptance examples, scenario tags, and BDD collaboration notes                                                                     |
| `ARCH.md`      | Architecture response to PRD: system context, design drivers and tradeoffs, high-level design, dependencies, strategic security/performance/observability, migration strategy, and architectural open questions |
| `SPEC.md`      | Implementation design decisions, error taxonomy, state management, component internal logic; directs domain detail into extracted reference files                                                               |
| `PLAN.md`      | Phase sequencing, TDD steps per phase, phase mapping, rollback per phase, implementation-order risks, rollout observability                                                                                     |
| `PHASE-{N}.md` | Execution detail for one phase: pseudo code, full docstrings, test outlines, per-environment rollout steps                                                                                                      |

## Planning Quality: The 5 C's

Every planning document and review optimizes these qualities in this
priority order:

1. **Correctness** — the document satisfies its parent contract and
   puts each fact in the canonical owner file.
2. **Comprehensiveness** — all required sections, artifacts, SaaS
   concerns, and explicit N/A dispositions are present.
3. **Coherence** — the design hangs together end-to-end without
   mechanism gaps, impossible sequencing, or hidden assumptions.
4. **Consistency** — names, IDs, decisions, and references agree
   across PRD, ARCH, SPEC, PLAN, PHASE, and extracted files.
5. **Clarity** — every load-bearing statement is unambiguous enough
   for implementation or review.

Reviewers must rank findings in this order; correctness gaps outrank
style or clarity issues.

## Extracted Reference Files

Extracted files are the single source of truth for their domain.
Created or deepened progressively by the owning primary agent or by domain subagents invoked by
the primary orchestrators. Later documents must reference them,
never copy their content.

| File             | Domain                                                                                | Created By                                                      | Deepened By                                                     |
| ---------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------- |
| `BDD.md`         | Business-readable examples, Gherkin scenarios, scenario tags, BDD collaboration notes | `@bdd-designer`                                                 | —                                                               |
| `MODELS.md`      | Data entities, schemas, relationships, storage                                        | `@data-modeler` (via `@architect`, high-level)                  | `@data-modeler` (via `@spec-designer`, field-level)             |
| `CONFIG.md`      | Feature flags, env vars, runtime config                                               | `@config-designer` (via `@architect`, names only)               | `@config-designer` (via `@spec-designer`, defaults, validation) |
| `API.md`         | API endpoint contracts (request/response)                                             | `@api-designer` (via `@spec-designer`)                          | —                                                               |
| `DEFINITIONS.md` | Object/class/function interfaces and signatures                                       | `@interface-designer` (via `@spec-designer`)                    | —                                                               |
| `TESTING.md`     | Testing strategy: unit, integration, E2E                                              | `@test-strategist` (via `@spec-designer`)                       | —                                                               |
| `UI_UX.md`       | User flows, screen states, accessibility, responsive behavior                         | `@ui-flow-designer` (via `@spec-designer`, when feature has UI) | —                                                               |

## Anti-Duplication Rules

1. **References over restatement** — summarize in at most one
   sentence, then cite the owning file/section with a markdown
   link.
2. **Deltas over copied detail** — only add information new to
   the current document's scope.
3. **Single canonical owner** — each concept, schema, contract,
   or decision lives in exactly one file.
4. **One-sentence bridge** — when a document needs context from
   another, write one sentence plus a markdown link. Never
   restate full schemas, contracts, signatures, config tables,
   BDD scenarios, test matrices, UI/UX flows, or accessibility checklists.

## Markdown Reference Formatting

When any planning document references another file, document,
section, or URL:

- Use markdown links for every reference.
- Link planning docs with the correct heading anchor:
  `[FEATURE_NAME-PRD.md §3 User Stories](FEATURE_NAME-PRD.md#3-user-stories)`
- Link extracted files by file name, adding a section anchor
  when pointing to a specific heading:
  `[FEATURE_NAME-MODELS.md](FEATURE_NAME-MODELS.md)`
- For non-markdown files without stable anchors, link the file
  itself and mention the symbol or line in prose.
- Link external docs as markdown URLs; preserve fragment
  identifiers when citing a specific section.
- Derive section anchors from the actual heading text
  (lowercase, punctuation removed, spaces replaced with `-`).

## Guiding Principles

Include verbatim in every PLAN document:

- Small, reversible phases. Default target is 300-500 lines of
  production code changed (added + removed), plus a plausible
  test-code volume (typically 0.5-1.5× production). Phases that
  cannot fit this band must be sized via a bottom-up estimate
  against the per-artifact heuristics in
  [Phase Sizing Heuristics](#phase-sizing-heuristics) and
  classified under the matching archetype. Documentation files
  (\*.md) are excluded from the count.
- Apply TDD red-green-refactor as the primary strategy for
  writing code.
- Every function should have documentation (use `doc-string`
  skill conventions).
- Where creating new code, separate business logic from side
  effects. Functional core, imperative shell.
- Use `comment` skill for change summaries and `commit-message`
  skill for commits after each phase.


## Learning-Friendly Planning Mode

Use this mode whenever the user asks to go slowly, keep the project
minimal, make the work easier to understand, or avoid overloading a
phase:

- Prefer one subsystem per phase. Split backend shell, frontend shell,
  database tooling, Redis, workers, local AI, and deployment into separate
  phases.
- For scaffold phases, prefer roughly 50-200 production LOC and 1-3 focused
  tests per subsystem over the normal 300-500 LOC target.
- Add runtime services only when the current phase ships behavior that uses
  them.
- Every phase should state exactly what the user can run afterward.
- Future infrastructure should be documented as deferred, not implemented as
  a placeholder.
- Documentation should distinguish target design from current implementation
  status.

## Phase Sizing Heuristics

Phase sizing must be bottom-up, not vibe-checked. These tables
are the shared vocabulary used by:

- `@plan-designer` when drafting PLAN phase bands — estimates
  forward from the phase mapping.
- `@phase-designer` when drafting a phase plan — verifies the
  parent PLAN's band backward from the actual artifact
  inventory the phase plan ships.
- `@phase-reviewer` when critiquing — audits that a phase's
  declared band is reproducible from its phase mapping.

Drift between a parent PLAN's declared band and a downstream
bottom-up estimate greater than 50% must be surfaced as a
clarification, not silently absorbed.

### Per-artifact production LOC

Includes docstrings, imports, and metadata (e.g., SQLAlchemy
`__table_args__`):

| Artifact                                       | Small | Typical | Large |
| ---------------------------------------------- | ----- | ------- | ----- |
| Pydantic contract model (≤5 fields)            | 20    | 35      | 55    |
| Pydantic model (validators, nested types)      | 40    | 70      | 110   |
| SQLAlchemy model (≤5 cols)                     | 40    | 60      | 90    |
| SQLAlchemy model (~10 cols + indexes)          | 70    | 100     | 140   |
| SQLAlchemy model (fat: JSONB, FK, constraints) | 100   | 150     | 220   |
| Alembic revision per table                     | 20    | 35      | 60    |
| Alembic index / constraint (each)              | 5     | 10      | 15    |
| Alembic Postgres enum (each)                   | 5     | 10      | 15    |
| Thin CRUD repository (3-5 methods)             | 70    | 110     | 160   |
| Repository with query composition              | 130   | 200     | 300   |
| Pure helper function                           | 30    | 60      | 100   |
| HTTP endpoint (route + DTO + validation)       | 30    | 60      | 100   |
| Temporal workflow class                        | 120   | 220     | 360   |
| Temporal activity (thin)                       | 40    | 70      | 120   |
| Pub/Sub consumer / event dispatcher            | 120   | 220     | 320   |
| HTTP client (typed, auth, retry)               | 80    | 150     | 250   |
| Provider adapter (Google/Slack-style)          | 200   | 350     | 550   |
| Config loader / typed runtime-config object    | 30    | 60      | 100   |
| Background job / cron workflow                 | 100   | 180     | 280   |

Use **Typical** for most estimates. Drop to **Small** only when
the artifact is provably minimal (e.g., a stub repository with
two methods). Escalate to **Large** when the artifact carries
docstring-heavy complexity — the `doc-string` skill mandates
full templates on every non-trivial function, and repositories
with full Args/Returns/Raises per method land closer to Large
than Typical.

### Per-test LOC

Includes docstrings and setup:

| Test shape                               | LOC per test         |
| ---------------------------------------- | -------------------- |
| Unit test (mocked, trivial)              | 10-15                |
| Unit test (mocked, with docstring block) | 15-25                |
| Integration test (fixtures, db)          | 25-40                |
| Temporal workflow test                   | 30-60                |
| Parametrized test                        | 15 base + 5 per case |
| Migration upgrade/downgrade test         | 20-40                |
| Endpoint smoke test                      | 20-35                |

### LOC bands by phase archetype

Defaults for phases that do not fit the review-friendly 300-500
production band:

| Phase archetype                                | Production LOC | Test LOC |
| ---------------------------------------------- | -------------- | -------- |
| Contract freeze / stubs only                   | 200-400        | 100-250  |
| Single-table schema + repo                     | 300-450        | 200-300  |
| Multi-table schema + repos                     | 600-1000       | 400-700  |
| Runtime-behavior (consumer, workflow, service) | 400-650        | 400-600  |
| Integration (HTTP client, provider adapter)    | 400-700        | 300-500  |
| Operator surface (API + small UI)              | 400-650        | 300-500  |
| Rollout-only (cleanup, backfill, flag flip)    | 150-400        | 100-300  |
| Cross-repo coordination (producer + consumer)  | 400-700        | 300-500  |

Any phase exceeding its archetype's upper bound needs either a
split or an explicit `LOC guardrail exception` note in the phase
header explaining why splitting is worse than carrying the
oversized phase. Test LOC is never free — phases that enumerate
20+ tests with full docstrings carry 300+ test LOC regardless of
how small the production code is.

### Consumption

- `@plan-designer` owns the **estimation procedure**, **split
  criteria**, and **worked example** — see its prompt for how
  these tables feed PLAN drafting.
- `@phase-designer` consumes these tables to verify the parent
  PLAN's band at phase-plan drafting time; see its Process for
  the sizing-verification step.
- `@phase-reviewer` uses these tables to audit whether a phase
  plan's declared band is reproducible from its artifact
  inventory.

## SaaS Pre-Flight Checklist

Ten tenant-aware rollout concerns every SaaS phase plan must
address in its rollout sections. Shared by:

- `@phase-designer` — verifies each item is addressed or
  explicitly marked N/A when drafting a phase plan.
- `@phase-reviewer` — audits each item's coverage during
  phase-fidelity review.

### Checklist

- **Local dev multi-tenant coverage**: local setup covers at
  least two tenants so tenant-isolation bugs surface early.
  Coverage may be satisfied by fixture-level tenant-distinct
  identifiers or durable seed data, depending on the phase
  type. Durable seed scripts are required only if the phase
  introduces a runtime path that actually needs persisted data.
- **Tenant-aware test cases**: tests exercise the feature
  under multiple tenants, not just one.
- **Per-environment feature flag state**: local / QA / staging
  / production each have explicit flag values (off,
  internal-only, %, 100%).
- **Per-tenant canary rollout in production**: production
  rollout includes a canary-tenant strategy when applicable.
- **Observability verification steps**: rollout steps verify
  metrics, logs, and traces are emitting with correct tenant
  enrichment.
- **Audit log verification**: rollout steps verify audit
  entries are produced for audit-relevant actions.
- **Rate limit / quota verification**: if the feature has rate
  limits, rollout steps verify bucket behavior in staging.
- **Webhook delivery verification**: if the feature emits
  webhooks, rollout steps verify signing, retry, and replay
  protection in staging.
- **Rollback procedure includes tenant data**: production
  rollback explicitly addresses in-flight tenant data (drain,
  defer, or reverse-migrate).
- **Kill switch drill**: production rollout documents how to
  exercise the kill switch without redeploy.

### Dispositions

Every item must end in exactly one of two states in the phase
plan:

- **Addressed**: concrete, phase-specific steps are provided.
- **Explicitly N/A**: the document says `N/A` and gives a
  one-line reason tied to this phase.

Silence is not acceptable. If a concern does not apply because
the phase is schema-only, infra-only, has no runtime path yet,
or does not touch tenant-scoped behavior, say so explicitly —
do not omit. For schema-only or no-runtime phases, fixture-level
tenant-distinct identifiers are sufficient for the local-dev
multi-tenant item; do not invent a durable seed CLI unless the
parent phase explicitly names one.

## Code Generation Instructions

Canonical rules that apply at the end of every phase plan
(`FEATURE_NAME-PHASE-{N}.md`), referenced by `@phase-designer` and
enforced during implementation by `@phase-coder`. Phase plans
should reference this section rather than restating it; include a
phase-specific override only when the phase needs a narrower or
broader rule.

- **Lint**: zero errors, zero warnings, no suppressions — load
  the `lint-config` skill and treat its rules as mandatory.
- **Types**: strict mode, zero errors, explicit parameter and
  return types. No `Any`, `unknown` casts, or untyped escape
  hatches.
- **Docstrings**: follow the `doc-string` skill — tiered
  complexity (trivial / moderate / complex), language-native
  format (Google-style Python, JSDoc TypeScript, Rust `///`).
- **Commits**: use the `commit-message` skill; commit atomically
  per Green step.
- **Change summary**: use the `comment` skill after the phase
  completes.

## Review Process

After drafting any planning document:

1. **Review (doc-reviewer)**: Invoke `@doc-reviewer` to
   scrutinize for consistency, codebase alignment, completeness,
   ambiguity, and duplication/drift. Cross-check against parent/upstream
   documents, starting with PRD, and extracted reference files.

2. **Resolve Clarifications (clarification-reviewer)**: If
   unresolved items remain, invoke `@clarification-reviewer`
   agents with exact item details. Work items interactively,
   update documents as needed, settle tasks or pause when
   waiting on feedback.

3. **Specialized fidelity review**: After SPEC general review and
   clarifications are settled, invoke `@spec-reviewer` to verify
   PRD/ARCH fidelity across SPEC and companion reference files.
   Before implementation, invoke `@phase-reviewer` when a phase
   needs phase-fidelity critique.

4. **Settle all items**: All clarification tasks in
   `clarifications.db` must be settled (`completed`, `archived`,
   or `deferred`) — no `new`, `in-progress`, or `open-question`
   items remaining.

## Pre-Flight

Before drafting `FEATURE_NAME-PRD.md`, invoke the `metis` agent to
surface hidden intentions, ambiguities, and potential failure points.
Resolve critical ambiguities with the user before proceeding.

## Planning Workflow

```
metis (pre-flight clarification)
    ▼
@product-manager → PRD.md
    ▼
@bdd-designer → BDD.md
    ▼
@doc-reviewer → @clarification-reviewer
    ▼
@architect → ARCH.md
    delegates → @data-modeler → MODELS.md (high-level)
    delegates → @config-designer → CONFIG.md (names only)
    ▼
@doc-reviewer → @clarification-reviewer
    ▼
@spec-designer → SPEC.md
    delegates → @api-designer → API.md
    delegates → @interface-designer → DEFINITIONS.md
    delegates → @ui-flow-designer → UI_UX.md (when feature has UI)
    delegates → @test-strategist → TESTING.md
    delegates → @data-modeler → deepens MODELS.md (field-level)
    delegates → @config-designer → deepens CONFIG.md (defaults, validation)
    ▼
@spec-reviewer → @clarification-reviewer (if needed)
    ▼
@plan-designer → PLAN.md
    ▼
@phase-designer → PHASE-{N}.md (one per phase)
    ▼
Implementation per phase (e.g., @phase-coder)
    → uses: doc-string, comment, commit-message
```

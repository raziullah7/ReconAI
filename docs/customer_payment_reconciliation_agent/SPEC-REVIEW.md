# SPEC-REVIEW.md

## Document Review: SPEC.md

### Summary

The spec layer now aligns with the parent PRD and ARCH on the core workflow: call intake, transcription, local LLM extraction, deterministic reconciliation, human review, auditability, reporting, and reprocessing. The review still carries product decisions that must be resolved before implementation planning becomes final.

### Input Inventory

| File | Status |
| --- | --- |
| [PRD.md](PRD.md) | Present |
| [BDD.md](BDD.md) | Present |
| [ARCH.md](ARCH.md) | Present |
| [SPEC.md](SPEC.md) | Present |
| [API.md](API.md) | Present |
| [DEFINITIONS.md](DEFINITIONS.md) | Present |
| [MODELS.md](MODELS.md) | Present |
| [CONFIG.md](CONFIG.md) | Present |
| [UI_UX.md](UI_UX.md) | Present |
| [TESTING.md](TESTING.md) | Present |

### Findings From Spec-Reviewer Pass

| ID | Severity | Finding | Status |
| --- | --- | --- | --- |
| SR-001 | High | ARCH required a transcription worker, but SPEC did not define it as a component. | Resolved in [SPEC.md](SPEC.md#3-detailed-design). |
| SR-002 | High | API contracts were too shallow to implement or test. | Resolved by adding shared schemas and per-endpoint request/response contracts in [API.md](API.md). |
| SR-003 | High | Idempotency was promised for mutating endpoints but only modeled for processing jobs. | Resolved with `IdempotencyRecord`, idempotency state, repository interfaces, and API replay/conflict rules. |
| SR-004 | High | Optional payment integration sources leaked into the base payment model. | Resolved by limiting base `PaymentSource` to `MANUAL` and `CSV_IMPORT` in [MODELS.md](MODELS.md). |
| SR-005 | Medium | A duplicate-payment-reference error was previously described outside the canonical error taxonomy. | Resolved by using canonical `Conflict`. |
| SR-006 | Medium | Audit action enum did not cover all audit-relevant UI actions. | Resolved by expanding `AuditLog.action` in [MODELS.md](MODELS.md). |
| SR-007 | Medium | Local LLM model choice remained open but was missing from the first review summary. | Tracked as an open decision below. |

### Remaining Clarifications

| ID | Source | Goal | Owner File | Status | Note |
| --- | --- | --- | --- | --- | --- |
| P1 | PRD OQ-04 | Extraction confidence threshold | CONFIG / SPEC | Clarification Required | Threshold is intentionally left as deployment policy and must be confirmed before implementation. |
| P2 | PRD OQ-03 | Tenant mode | ARCH / MODELS / UI_UX | Clarification Required | Docs support tenant-ready design but user-facing tenant management needs confirmation. |
| P3 | PRD FR-15 | Notifications | CONFIG / API / UI_UX | Clarification Required | Feature flag exists, but notifications are optional and provider contracts are not designed. |
| P4 | PRD OQ-01 | Local LLM model | CONFIG / ARCH | Clarification Required | Target-server model choice remains open and affects resource sizing. |
| P5 | PRD OQ-05 | CSV import columns | API / TESTING | Clarification Required | API defines import envelope but not the exact CSV column inventory. |
| P6 | MODELS open question | Retention periods | MODELS / SPEC | Clarification Required | Recording, transcript, raw LLM output, idempotency, and audit retention durations need policy values. |
| P7 | SPEC role policy | Finance User review authority | API / UI_UX / TESTING | Clarification Required | Finance User review finalization remains policy-dependent. |

### Discrepancies

No unresolved cross-file contradictions found after the SR-001 through SR-006 fixes. Remaining items are explicit clarifications rather than hidden conflicts.

### Duplication And Drift Risks

- Reconciliation statuses appear across PRD, MODELS, SPEC, API, and TESTING. This is acceptable for planning traceability, but implementation should define one code enum and have future docs reference it.
- Role permissions appear in API and TESTING. This is intentional because API owns endpoint authorization and TESTING owns the permission matrix.

### Completeness Gaps

- Notification endpoints/provider contracts are absent because notifications are optional.
- Exact CSV column inventory is not frozen.
- Exact retention periods are not frozen.
- Final local LLM model and confidence threshold are not frozen.

### Codebase Alignment Issues

No implementation code exists beyond placeholder `frontend/` and `backend/` folders, so proposed locations are forward-looking and not in conflict with current code.

### Recommendation

Use this spec layer as the canonical planning baseline, but resolve the remaining clarifications before producing phase-level implementation plans.

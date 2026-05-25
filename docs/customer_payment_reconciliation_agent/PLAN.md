# PLAN.md

## Goal

Implement the customer payment reconciliation agent in small, reversible TDD phases that preserve tenant boundaries, auditability, local-AI constraints, and deterministic reconciliation behavior defined by [SPEC.md](SPEC.md).

## Guiding Principles

- Small, reversible phases. Default target is 300-500 lines of production code changed (added + removed), plus a plausible test-code volume (typically 0.5-1.5x production). Phases that cannot fit this band must be sized via a bottom-up estimate against the per-artifact heuristics in [Phase Sizing Heuristics](../../.agents/skills/planning-conventions/SKILL.md#phase-sizing-heuristics) and classified under the matching archetype. Documentation files (*.md) are excluded from this limit.
- Apply TDD red-green-refactor as the primary strategy for writing code.
- Every function should have documentation (use `doc-string` skill conventions).
- Where creating new code, separate business logic from side effects. Functional core, imperative shell.
- Use `comment` skill for change summaries and `commit-message` skill for commits after each phase.

## Clarification Gates

These decisions remain open in [SPEC-REVIEW.md](SPEC-REVIEW.md#remaining-clarifications). The plan may be drafted now, but the affected phases must not be finalized for execution until their gate is resolved.

- Gate A: extraction confidence threshold before extraction and reconciliation behavior is implemented.
- Gate B: tenant mode before user-facing tenant switching or tenant administration is implemented.
- Gate C: notification scope before any notification endpoints, provider adapters, or UI prompts are added.
- Gate D: local LLM model before local-AI worker sizing and deployment configuration are finalized.
- Gate E: CSV import columns before payment import endpoint and parser implementation.
- Gate F: retention periods before storage cleanup, erasure, or archival jobs are implemented.
- Gate G: Finance User review authority before review-action authorization is implemented.

## Feature Flags and Environment Variables

- `RECONAI_PROCESSING_ENABLED` (FF): gates asynchronous transcription, extraction, matching, and reconciliation.
- `RECONAI_NOTIFICATIONS_ENABLED` (FF): gates optional mismatch and payment-not-found notifications.
- `RECONAI_EXPORTS_ENABLED` (FF): gates CSV/Excel export availability.
- `DATABASE_URL` (ENV): PostgreSQL connection.
- `REDIS_URL` (ENV): Redis broker and result backend.
- `OLLAMA_BASE_URL` (ENV): local Ollama runtime location.
- `RECONAI_LLM_MODEL` (ENV): local LLM model for agreement extraction.
- `TRANSCRIPTION_BACKEND` (ENV): selected local transcription adapter.
- `STORAGE_ROOT` (ENV): recording and export storage root.
- `EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD` (runtime option): extraction confidence cutoff for review routing.
- `WORKER_CONCURRENCY` (ENV): local worker concurrency guardrail.

Full configuration detail: See [CONFIG.md](CONFIG.md).

## Phase Overview

- Phase 1: Project foundation, dependency skeleton, configuration loading, and health checks.
- Phase 2: Shared data foundation, migrations, tenant context, idempotency, and audit infrastructure.
- Phase 3: Authentication, authorization, customers, and payment records.
- Phase 4: Call intake, transcript submission, storage, queue handoff, and processing attempts.
- Phase 5: Transcription worker and local-AI extraction adapter boundary.
- Phase 6: Extraction validation, payment matching, and deterministic reconciliation core.
- Phase 7: Review workflow, manual payment linking, and reprocessing controls.
- Phase 8: Dashboard, filters, exports, and frontend shell surfaces.
- Phase 9: Cross-cutting hardening, observability, rollback rehearsal, and release readiness.

## Phase 1 (300-450 loc production + 180-280 tests, archetype: contract freeze / stubs only): Project Foundation

This phase creates the runnable monorepo foundation without implementing reconciliation behavior. Inventory: backend app scaffold, frontend scaffold, Docker Compose skeleton, config loader stub, health endpoint, and initial smoke tests. It fits the contract/stubs archetype because it freezes layout and runtime boundaries before domain code.

- **Red**:
  - Write failing backend health and config tests.
  - Write failing frontend render/health-client smoke tests.
  - Write failing compose/config documentation checks where practical.
- **Green**:
  - Add backend FastAPI app skeleton, settings loader, health endpoint, and dev entrypoint.
  - Add frontend Vite shell with a backend health status surface.
  - Add Docker Compose services for PostgreSQL, Redis, Ollama placeholder, backend, frontend, and worker placeholders.
- **Refactor**:
  - Normalize local commands, environment variable naming, and shared package layout.
  - Keep app shell thin and leave domain modules empty.

**Tests**

- `test_health_endpoint_returns_ok()`
- `test_settings_require_database_and_redis_urls()`
- `test_frontend_app_renders_shell()`
- `test_frontend_health_client_handles_ok_response()`

**Phase mapping**

- Objects from [DEFINITIONS.md](DEFINITIONS.md): `TenantContext`, `UserContext`, `RequestContext`, `Clock`, `Logger`, `Tracer` (stubs)
- APIs from [API.md](API.md): health endpoint only as implementation support
- Models from [MODELS.md](MODELS.md): none
- UI surfaces from [UI_UX.md](UI_UX.md): Login, Dashboard shell (skeleton only)

## Phase 2 (600-900 loc production + 350-550 tests, archetype: multi-table schema + repos): Shared Data, Tenant, Idempotency, and Audit Foundation

This phase lands the additive database foundation for tenant-scoped work before feature behavior. Inventory: base models, Alembic migration, tenant/request context plumbing, audit repository, idempotency repository, and repository test scaffolding. LOC guardrail exception: schema plus repositories are tightly coupled because later phases depend on tenant-safe persistence and idempotency guarantees.

- **Red**:
  - Write migration tests for required shared tables and indexes.
  - Write tenant isolation repository tests.
  - Write idempotency reservation/replay/conflict tests.
  - Write audit append-only tests.
- **Green**:
  - Add additive migrations for shared entities and audit/idempotency records.
  - Implement request context resolution and repository tenant scoping.
  - Implement `AuditLogRepository` and `IdempotencyRepository`.
- **Refactor**:
  - Extract shared repository base helpers.
  - Centralize error translation for persistence conflicts.

**Tests**

- `test_migration_creates_shared_foundation_tables()`
- `test_repository_queries_are_tenant_scoped()`
- `test_idempotency_replays_same_payload_response()`
- `test_idempotency_conflicts_on_different_payload()`
- `test_audit_log_is_append_only()`

**Phase mapping**

- Classes from [DEFINITIONS.md](DEFINITIONS.md): `IdempotencyRepository`, `AuditLogRepository`
- Objects from [DEFINITIONS.md](DEFINITIONS.md): `TenantContext`, `UserContext`, `RequestContext`
- Models from [MODELS.md](MODELS.md): `Tenant`, `User`, `IdempotencyRecord`, `AuditLog`
- APIs from [API.md](API.md): none
- UI surfaces from [UI_UX.md](UI_UX.md): none

## Phase 3 (450-650 loc production + 300-450 tests, archetype: operator surface): Auth, Customers, and Payments

This phase adds the first tenant-aware user operations and payment data foundation. Inventory: auth dependency, customer repository/API, payment repository/API, frontend customer/payment screens, and permission tests. Gate E must be resolved before CSV import parser details are finalized.

- **Red**:
  - Write auth/permission tests for protected endpoints.
  - Write customer create/list API tests.
  - Write manual payment create/list API tests.
  - Write UI smoke tests for customer and payment screens.
- **Green**:
  - Implement login/session contract and protected route dependency.
  - Implement customer create/list behavior.
  - Implement manual payment create/list behavior.
  - Add frontend customer and payment management surfaces.
- **Refactor**:
  - Extract permission helpers and shared list pagination utilities.
  - Keep CSV import as a contract placeholder until Gate E is resolved.

**Tests**

- `test_protected_endpoint_requires_authentication()`
- `test_role_without_permission_gets_forbidden()`
- `test_create_customer_is_tenant_scoped()`
- `test_create_payment_rejects_duplicate_transaction_reference()`
- `test_payment_list_filters_by_tenant()`
- `test_customer_payment_screens_render_allowed_actions()`

**Phase mapping**

- Classes from [DEFINITIONS.md](DEFINITIONS.md): `CustomerRepository`, `PaymentRepository`
- APIs from [API.md](API.md): `POST /v1/tenants/{tenant_id}/auth/login`, `GET /v1/tenants/{tenant_id}/customers`, `POST /v1/tenants/{tenant_id}/customers`, `GET /v1/tenants/{tenant_id}/payments`, `POST /v1/tenants/{tenant_id}/payments`
- Models from [MODELS.md](MODELS.md): `Customer`, `Payment`
- UI surfaces from [UI_UX.md](UI_UX.md): Login, Customers, Payments

## Phase 4 (400-650 loc production + 300-450 tests, archetype: operator surface): Call Intake and Processing Handoff

This phase introduces call/transcript intake and queue handoff before workers perform heavy processing. Inventory: call/transcript models and repositories, call intake endpoint, storage boundary, processing attempt creation, and status UI. Background job infrastructure lands before producer behavior expands further.

- **Red**:
  - Write call intake API tests for recording and transcript-only paths.
  - Write storage failure rollback tests.
  - Write processing attempt creation tests.
  - Write status UI smoke tests.
- **Green**:
  - Implement `CallRepository` call creation, transcript persistence, and status updates.
  - Implement call intake endpoint and queue handoff through `JobQueue`.
  - Add processing detail UI with status and transcript availability.
- **Refactor**:
  - Extract storage port and status transition helpers.
  - Add shared idempotency wrapper for mutating handlers.

**Tests**

- `test_create_call_with_recording_enqueues_transcription()`
- `test_create_call_with_transcript_enqueues_extraction()`
- `test_storage_failure_does_not_leave_partial_call()`
- `test_processing_attempt_created_with_idempotency_key()`
- `test_processing_detail_shows_current_status()`

**Phase mapping**

- Classes from [DEFINITIONS.md](DEFINITIONS.md): `CallRepository`, `JobQueue`, `IntakeService`, `ProcessingService`
- APIs from [API.md](API.md): `POST /v1/tenants/{tenant_id}/calls`, `GET /v1/tenants/{tenant_id}/calls/{call_id}`, `GET /v1/tenants/{tenant_id}/calls/{call_id}/transcript`
- Models from [MODELS.md](MODELS.md): `CallRecord`, `CallTranscript`, `ProcessingAttempt`
- UI surfaces from [UI_UX.md](UI_UX.md): Call Intake, Processing Detail

## Phase 5 (400-650 loc production + 350-500 tests, archetype: runtime-behavior): Transcription and Local-AI Extraction Boundary

This phase adds worker runtime behavior up to validated extraction persistence, but not final reconciliation. Inventory: transcription service, local transcription adapter, local LLM adapter boundary, extraction service shell, worker tasks, and observability spans. Gates A and D must be resolved before extraction routing and worker sizing are finalized.

- **Red**:
  - Write worker status transition tests.
  - Write transcription adapter contract tests with a fake adapter.
  - Write local LLM adapter error tests.
  - Write extraction persistence tests for raw and validated output separation.
- **Green**:
  - Implement `TranscriptionService`, `TranscriptionAdapter` integration boundary, and transcript persistence.
  - Implement `ExtractionService` shell and local LLM adapter boundary.
  - Wire worker tasks under `RECONAI_PROCESSING_ENABLED`.
- **Refactor**:
  - Separate adapter errors from domain validation errors.
  - Add metrics/log helpers for worker attempts.

**Tests**

- `test_transcription_worker_advances_call_to_transcribed()`
- `test_transcription_worker_records_failed_attempt_on_timeout()`
- `test_extraction_worker_stores_raw_output_and_validated_fields()`
- `test_extraction_worker_routes_invalid_json_to_failure_or_review()`
- `test_processing_flag_blocks_new_worker_jobs()`

**Phase mapping**

- Classes from [DEFINITIONS.md](DEFINITIONS.md): `TranscriptionAdapter`, `TranscriptionService`, `LocalLlmAdapter`, `ExtractionService`
- Classes from [DEFINITIONS.md](DEFINITIONS.md): `ProcessingService` (modify)
- Models from [MODELS.md](MODELS.md): `CallTranscript`, `AgreementExtraction`, `ProcessingAttempt`
- APIs from [API.md](API.md): none
- UI surfaces from [UI_UX.md](UI_UX.md): Processing Detail (status updates)

## Phase 6 (400-650 loc production + 350-500 tests, archetype: runtime-behavior): Matching and Deterministic Reconciliation

This phase completes the functional core that classifies cases. Inventory: pure validation, matching, reconciliation functions, extraction repository, reconciliation repository, worker orchestration, and rule coverage. Gate A must be resolved before low-confidence behavior is frozen.

- **Red**:
  - Write rule tests for every reconciliation outcome.
  - Write candidate matching tests for each matching signal.
  - Write extraction validation boundary tests.
  - Write worker integration tests from extraction to case creation.
- **Green**:
  - Implement `validate_extraction`, `match_candidate_payments`, and `decide_reconciliation`.
  - Implement extraction and reconciliation repositories.
  - Wire matching/reconciliation worker step.
- **Refactor**:
  - Keep deterministic rules pure and side-effect free.
  - Extract result reason generation into testable helpers if needed.

**Tests**

- `test_validate_extraction_flags_low_confidence()`
- `test_match_candidate_payments_uses_customer_phone_invoice_currency_date_and_amount()`
- `test_decide_reconciliation_returns_reconciled_for_exact_match()`
- `test_decide_reconciliation_returns_underpaid_and_overpaid()`
- `test_decide_reconciliation_routes_missing_and_ambiguous_payments()`
- `test_reconciliation_worker_creates_case_and_audit_log()`

**Phase mapping**

- Functions from [DEFINITIONS.md](DEFINITIONS.md): `validate_extraction`, `match_candidate_payments`, `decide_reconciliation`
- Classes from [DEFINITIONS.md](DEFINITIONS.md): `ExtractionRepository`, `ReconciliationRepository`, `ReconciliationService`
- Models from [MODELS.md](MODELS.md): `AgreementExtraction`, `ReconciliationCase`, `ReconciliationCasePayment`
- APIs from [API.md](API.md): `GET /v1/tenants/{tenant_id}/cases`, `GET /v1/tenants/{tenant_id}/cases/{case_id}`
- UI surfaces from [UI_UX.md](UI_UX.md): Case List, Case Detail

## Phase 7 (400-650 loc production + 300-500 tests, archetype: operator surface): Review Workflow and Reprocessing

This phase lets humans resolve exceptions and safely re-run processing. Inventory: review service, review-action API, manual payment linking, recalculation helper, reprocessing endpoint, audit entries, and review UI. Gates B, F, and G must be resolved before user-facing permissions and retention-sensitive behavior are finalized.

- **Red**:
  - Write review action permission tests.
  - Write manual payment link/unlink recalculation tests.
  - Write optimistic locking conflict tests.
  - Write reprocessing history preservation tests.
  - Write review UI smoke tests.
- **Green**:
  - Implement `ReviewService` and `recalculate_case_after_review`.
  - Implement review action and reprocess endpoints.
  - Add review queue and case-detail review controls.
- **Refactor**:
  - Consolidate audit writing for review actions.
  - Extract review-action authorization policy behind a named helper.

**Tests**

- `test_reviewer_can_link_payment_and_recalculate_case()`
- `test_review_action_requires_expected_case_version()`
- `test_review_action_denies_unauthorized_role()`
- `test_reprocess_creates_new_attempt_without_losing_prior_history()`
- `test_review_queue_renders_action_states()`

**Phase mapping**

- Functions from [DEFINITIONS.md](DEFINITIONS.md): `recalculate_case_after_review`
- Classes from [DEFINITIONS.md](DEFINITIONS.md): `ReviewService`, `ReconciliationRepository` (modify), `JobQueue` (modify)
- APIs from [API.md](API.md): `POST /v1/tenants/{tenant_id}/cases/{case_id}/review-actions`, `POST /v1/tenants/{tenant_id}/calls/{call_id}/reprocess`, `GET /v1/tenants/{tenant_id}/cases/{case_id}/audit-log`
- Models from [MODELS.md](MODELS.md): `ReconciliationCase`, `ReconciliationCasePayment`, `AuditLog`, `ProcessingAttempt`
- UI surfaces from [UI_UX.md](UI_UX.md): Review Queue, Case Detail, Audit History, Admin Operations

## Phase 8 (400-650 loc production + 300-500 tests, archetype: operator surface): Dashboard, Filters, and Exports

This phase adds the manager/operator reporting surface after core cases exist. Inventory: reporting service, dashboard summary endpoint, export endpoint, frontend dashboard and export flows. Gate C controls notification-related surfaces; exports are gated by `RECONAI_EXPORTS_ENABLED`.

- **Red**:
  - Write dashboard aggregation tests.
  - Write filtered case list tests.
  - Write export authorization and feature-flag tests.
  - Write frontend dashboard/export smoke tests.
- **Green**:
  - Implement `ReportingService`, dashboard summary, filtered case queries, and export creation.
  - Add dashboard and export UI flows.
  - Add audit entries for export creation.
- **Refactor**:
  - Extract query filter normalization.
  - Add async export handoff only if synchronous export becomes too large.

**Tests**

- `test_dashboard_summary_counts_cases_by_status()`
- `test_case_filters_apply_status_date_customer_agent_payment_method_and_amount()`
- `test_export_respects_active_filters()`
- `test_exports_flag_disables_export_endpoint()`
- `test_dashboard_and_export_screens_render_expected_states()`

**Phase mapping**

- Classes from [DEFINITIONS.md](DEFINITIONS.md): `ReportingService`
- APIs from [API.md](API.md): `GET /v1/tenants/{tenant_id}/dashboard/summary`, `POST /v1/tenants/{tenant_id}/exports/reconciliation-cases`, `GET /v1/tenants/{tenant_id}/cases` (modify)
- Models from [MODELS.md](MODELS.md): `ReconciliationCase`, `AuditLog`, `ProcessingAttempt` (modify if async export is used)
- UI surfaces from [UI_UX.md](UI_UX.md): Dashboard, Case List, Audit History

## Phase 9 (250-400 loc production + 250-400 tests, archetype: rollout-only): Hardening and Release Readiness

This phase closes release gaps without adding new product surface. Inventory: observability dashboards, rollback rehearsal notes, seed data, security checks, load checks, and documentation updates. It fits rollout-only because it hardens already-landed behavior and finalizes readiness evidence.

- **Red**:
  - Write or enable tenant isolation regression tests across all endpoints.
  - Write permission matrix regression tests.
  - Write failure-mode and rate-limit tests that were deferred from feature phases.
  - Write release smoke checklist automation where feasible.
- **Green**:
  - Add missing observability metrics and structured logs.
  - Add seed data and release smoke scripts.
  - Verify rollback and kill-switch behavior per phase.
- **Refactor**:
  - Remove dead flags only if no longer needed.
  - Tighten docs around resolved clarification gates.

**Tests**

- `test_all_tenant_scoped_endpoints_reject_cross_tenant_ids()`
- `test_permission_matrix_matches_expected_roles()`
- `test_rate_limit_headers_are_returned_on_bucket_exhaustion()`
- `test_processing_kill_switch_disables_new_jobs_without_hiding_existing_records()`
- `test_release_smoke_flow_upload_to_review_audit()`

**Phase mapping**

- Classes from [DEFINITIONS.md](DEFINITIONS.md): all service classes (modify for instrumentation only)
- APIs from [API.md](API.md): all public endpoints (modify for hardening only)
- Models from [MODELS.md](MODELS.md): no destructive changes; additive observability support only if needed
- UI surfaces from [UI_UX.md](UI_UX.md): all screens (hardening only)

## Observability

- Request metrics: prove API latency and error rates by tenant and endpoint.
- Queue metrics: prove local AI work is bounded and not starving tenants.
- Processing metrics: prove transcription, extraction, matching, reconciliation, review, reprocessing, and export durations.
- Outcome metrics: track reconciliation statuses, review backlog, failures, and manual override rates.
- Feature flag metrics: track `RECONAI_PROCESSING_ENABLED`, `RECONAI_NOTIFICATIONS_ENABLED`, and `RECONAI_EXPORTS_ENABLED` state changes.
- Audit metrics: detect missing audit writes for finance-sensitive mutations.

## Rollback Strategy

- Phase 1: revert scaffold changes; no tenant data exists.
- Phase 2: rollback before production data by dropping additive tables; after data exists, disable user-facing phases and preserve tables for forensic review.
- Phase 3: disable customer/payment routes and UI links; preserve tenant data and audit logs.
- Phase 4: disable intake route and `RECONAI_PROCESSING_ENABLED`; preserve call and transcript records.
- Phase 5: disable worker execution with `RECONAI_PROCESSING_ENABLED`; keep queued attempts for retry after fix.
- Phase 6: disable reconciliation worker step; keep extracted data and cases for review rather than deleting outcomes.
- Phase 7: disable review mutation routes if needed; preserve cases, linked payments, notes, and audit logs.
- Phase 8: disable exports with `RECONAI_EXPORTS_ENABLED`; dashboard reads can remain if safe.
- Phase 9: rollback individual hardening changes; do not remove audit or tenant data during release rollback.

## Risks and Mitigations

- Local AI resource pressure: mitigate with worker concurrency limits, queue metrics, and staged internal rollout.
- LLM extraction ambiguity: mitigate with validation, confidence gate, evidence retention, and review routing.
- Cross-tenant data leakage: mitigate by landing tenant context and tenant-scoped repositories before feature endpoints.
- Audit gaps: mitigate by testing audit writes alongside every finance-sensitive mutation.
- Oversized phases: mitigate with phase-designer follow-up and split any phase whose bottom-up estimate expands beyond its archetype.
- Open product decisions: mitigate with clarification gates before affected phase execution.

## Additional Test Coverage

Testing strategy: See [TESTING.md](TESTING.md).

Phase-specific additions:

- Phase 2 must include migration upgrade/downgrade tests before repositories are trusted.
- Phase 3 must include role denial tests before frontend navigation exposes protected surfaces.
- Phase 5 must use fake transcription and LLM adapters before real local runtimes are wired.
- Phase 6 must include red/green rule coverage for every reconciliation outcome before worker integration.
- Phase 7 must include audit assertions for every review mutation.
- Phase 8 must include export filter parity checks against case list filters.
- Phase 9 must run the full tenant isolation and release smoke suite.

## Reference File Index

- [PRD.md](PRD.md): product requirement IDs and clarification gates traced by this plan.
- [BDD.md](BDD.md): BDD scenario tags used for behavior-level coverage mapping.
- [ARCH.md](ARCH.md): architecture sequencing constraints used by this plan.
- [SPEC.md](SPEC.md): implementation components and state boundaries sequenced by this plan.
- [API.md](API.md): endpoint names referenced in phase mappings.
- [DEFINITIONS.md](DEFINITIONS.md): functions, classes, objects, and ports referenced by phase mappings.
- [MODELS.md](MODELS.md): entities introduced by schema and behavior phases.
- [CONFIG.md](CONFIG.md): feature flags, env vars, and runtime options referenced by rollout phases.
- [TESTING.md](TESTING.md): global testing strategy referenced by phase-specific additions.
- [UI_UX.md](UI_UX.md): user-facing surfaces referenced by phase mappings.
- [SPEC-REVIEW.md](SPEC-REVIEW.md): remaining clarifications and review status used by clarification gates.

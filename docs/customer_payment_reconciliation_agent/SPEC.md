# SPEC.md

> Status: This is a target design document. It does not mean every item is implemented today. Use [README.md](README.md) and [PLAN.md](PLAN.md) for the current implementation phase.


## 1. Metadata

**Feature Name**: Customer Payment Reconciliation Agent  
**Status**: Draft  
**Author**: Codex using `.agents/agents/spec-designer.md`  
**Date**: intentionally omitted  
**Product Requirements Doc**: [PRD.md](PRD.md)  
**Architecture Doc**: [ARCH.md](ARCH.md)

## 2. Summary

This specification turns the product contract in [PRD.md](PRD.md) and the architecture in [ARCH.md](ARCH.md) into implementation design for backend services, async processing, review workflows, and UI integration.

Key decisions:

- Use explicit request-scoped context objects for tenant, user, authorization, request ID, and idempotency.
- Keep deterministic reconciliation in a functional core with side effects isolated in services and repositories.
- Store raw LLM output but only use validated extraction fields for business decisions.
- Treat review actions, payment linking, reprocessing, and exports as audit-relevant mutations.

## Milestone 1: Base API No-LLM Flow

Milestone 1 proves the backend reconciliation loop without calling a real LLM.
The caller supplies an `AgreementExtractionInputV1` payload that has the same
shape the future LLM adapter must emit.

Flow:

1. Accept `ReconciliationCaseCreateRequestV1` at the Base API boundary.
2. Validate `AgreementExtractionInputV1` and optional `ActualPaymentInputV1`.
3. Compute the reconciliation decision in a pure function.
4. Persist the extraction snapshot, payment snapshot, and decision.
5. Return the stored case response.

Decision order:

1. If extraction validation fails, return `ValidationFailed` before persistence.
2. If `needs_human_review` is true, confidence is below `0.80`, or required
   agreement fields are missing, create a `NEEDS_REVIEW` decision.
3. If no actual payment is supplied, create `PAYMENT_NOT_FOUND`.
4. If currencies conflict, create `NEEDS_REVIEW`.
5. If paid amount equals agreed amount, create `RECONCILED`.
6. If paid amount is below agreed amount and payment type is `ADVANCE`,
   `PARTIAL_PAYMENT`, or `INSTALLMENT`, create `PARTIAL_PAYMENT`.
7. If paid amount is below agreed amount, create `UNDERPAID`.
8. If paid amount is above agreed amount, create `OVERPAID`.

The LLM integration milestone replaces the fixture/manual source of
`AgreementExtractionInputV1`; it does not replace backend validation or backend
status decisions.

## 3. Detailed Design

### Component: Request Context and Authorization

**Purpose**: Resolve tenant and user context at the API boundary and enforce RBAC.  
**Location**: `backend/app/core/context`, `backend/app/core/auth`, `backend/app/api/dependencies`.  
**Interfaces**: See [DEFINITIONS.md](DEFINITIONS.md).  
**Internal Logic**: Every request resolves `TenantContext`, `UserContext`, `RequestId`, optional `IdempotencyKey`, and an `AuthzChecker`. Services receive context explicitly instead of reading global state. Mutating API handlers reserve an idempotency record before side effects and replay the stored response for duplicate compatible requests.  
**Error Handling**: Unauthenticated requests return `Unauthenticated`; authorized users without permission return `Forbidden`; incompatible idempotency-key reuse returns `IdempotencyConflict`.

### Component: Intake Service

**Purpose**: Accept call recordings or transcript submissions and create traceable call records.  
**Location**: `backend/app/features/intake`.  
**Interfaces**: See [DEFINITIONS.md](DEFINITIONS.md).  
**Internal Logic**: Validate customer and metadata, store recording if provided, create `CallRecord`, write audit log, and enqueue processing when needed.  
**Error Handling**: Validation failures stop before storage; storage failures do not create partial call records.

### Component: Processing Orchestrator

**Purpose**: Coordinate transcription, extraction, matching, and reconciliation jobs.  
**Location**: `backend/app/workers` and `backend/app/features/processing`.  
**Interfaces**: See [DEFINITIONS.md](DEFINITIONS.md).  
**Internal Logic**: Each job creates or updates `ProcessingAttempt`, checks idempotency, advances status, and emits audit/metric events. Retries are safe because mutations are guarded by idempotency key and current state checks.  
**Error Handling**: Worker failures set the attempt and case/call state to `FAILED` when recovery is not possible.

### Component: Transcription Worker

**Purpose**: Convert uploaded audio recordings into transcript text and transcription metadata.  
**Location**: `backend/app/features/transcription` and `backend/app/workers/transcription`.  
**Interfaces**: See [DEFINITIONS.md](DEFINITIONS.md).  
**Internal Logic**: Load the tenant-scoped recording, call the selected local transcription adapter, persist transcript text, language, model, confidence, and speaker segments, update call status to `TRANSCRIBED`, write audit history, and enqueue extraction. Transcript-only intake skips audio transcription but still creates transcript evidence.  
**Error Handling**: Missing recording, unsupported media, adapter timeout, or worker failure records a failed `ProcessingAttempt`, keeps prior evidence unchanged, and moves the call to `FAILED` when no retry remains.

### Component: Local AI Extraction

**Purpose**: Convert transcript evidence into validated payment agreement fields.  
**Location**: `backend/app/features/extraction`.  
**Interfaces**: See [DEFINITIONS.md](DEFINITIONS.md).  
**Internal Logic**: Build a constrained prompt, call local LLM adapter, parse JSON, validate fields, persist raw and validated output, and flag review when confidence or completeness is insufficient.  
**Error Handling**: Invalid JSON, unsupported currency, invalid amount, or missing evidence becomes `ExtractionValidationFailed` and routes to review or failure according to configured policy.

### Component: Payment Management

**Purpose**: Manage manual payment records and CSV imports.  
**Location**: `backend/app/features/payments`.  
**Interfaces**: See [DEFINITIONS.md](DEFINITIONS.md).  
**Internal Logic**: Validate money in minor units, currency, source, customer/reference fields, and transaction reference uniqueness. Base delivery accepts only manual and CSV-import payment sources; future integration sources stay out of accepted input until their add-ons are designed. CSV import stores valid rows and returns row-level errors for invalid rows.  
**Error Handling**: Duplicate transaction reference returns `Conflict`; partial CSV import reports accepted and rejected rows.

### Component: Matching and Reconciliation

**Purpose**: Find candidate payments and assign deterministic status.  
**Location**: `backend/app/features/reconciliation`.  
**Interfaces**: See [DEFINITIONS.md](DEFINITIONS.md).  
**Internal Logic**: Match by tenant, customer, phone, invoice/order reference, currency, date range, and amount similarity; then apply PRD reconciliation rules in deterministic order.  
**Error Handling**: Missing candidates, ambiguous candidates, low confidence, and unclear payment type produce review-safe statuses instead of silent success.

### Component: Review Workflow

**Purpose**: Let authorized users resolve cases that cannot be safely finalized automatically.  
**Location**: `backend/app/features/review`.  
**Interfaces**: See [DEFINITIONS.md](DEFINITIONS.md).  
**Internal Logic**: Review actions update the case, recalculate paid/difference amounts when payments are linked, and append audit entries.  
**Error Handling**: Stale version conflicts return `Conflict`; unauthorized role returns `Forbidden`.

### Component: Reporting and Export

**Purpose**: Provide dashboards, filters, case lists, and CSV/Excel exports.  
**Location**: `backend/app/features/reporting` and frontend reporting surfaces.  
**Interfaces**: See [DEFINITIONS.md](DEFINITIONS.md).  
**Internal Logic**: Query tenant-scoped case projections, paginate lists, aggregate counts, and generate export files with audit logging.  
**Error Handling**: Large exports may be async; disabled exports return `FeatureNotEnabled`.

### UI / UX Companion Reference

See [UI_UX.md](UI_UX.md) for user flows, screen states, interaction behavior, accessibility, and responsive requirements.

## 4. API Design

See [API.md](API.md) for full API contracts.

## 5. Data Models

See [MODELS.md](MODELS.md) for full data model schemas.

## 6. State Management

### Call Processing State

```text
UPLOADED -> TRANSCRIBING -> TRANSCRIBED -> EXTRACTING -> EXTRACTED -> RECONCILING -> RECONCILED
                                                                  -> NEEDS_REVIEW
                                                                  -> FAILED
```

Rules:

- State transitions require matching tenant context.
- Background jobs may only advance from the expected prior state unless a reprocessing attempt explicitly supersedes the current attempt.
- Failed states retain `ProcessingAttempt` error details and audit history.

### Idempotency State

```text
RESERVED -> COMPLETED
         -> FAILED
         -> EXPIRED
```

Rules:

- Mutating API requests reserve an `IdempotencyRecord` before side effects.
- A duplicate request with the same key and same payload hash returns the stored status code and response body.
- A duplicate request with the same key and a different payload hash returns `IdempotencyConflict`.
- Processing jobs keep their own `ProcessingAttempt` idempotency and may also reference the API idempotency key that created them.

### Reconciliation Case State

```text
NEEDS_REVIEW -> RECONCILED | UNDERPAID | OVERPAID | PARTIAL_PAYMENT | PAYMENT_NOT_FOUND | MULTIPLE_MATCHES_FOUND | FAILED
```

Review actions can update a case through approve, reject, edit agreed amount, link payment, unlink payment, or add note. Mutations require optimistic locking and audit logging.

## 7. Error Handling Strategy

Canonical error taxonomy:

- `Unauthenticated`: user identity is missing or invalid.
- `Forbidden`: authenticated user lacks role or tenant access.
- `ValidationFailed`: request, CSV row, LLM output, or domain input is invalid.
- `NotFound`: requested tenant-scoped resource is absent or hidden.
- `Conflict`: optimistic lock, duplicate transaction reference, or stale state conflict.
- `RateLimited`: tenant or user rate limit exceeded.
- `FeatureNotEnabled`: requested feature flag is disabled.
- `QuotaExceeded`: tenant limit is exceeded when quotas are introduced.
- `PlanLimitExceeded`: tenant plan does not include a feature when plans are introduced.
- `TenantSuspended`: tenant is disabled.
- `IdempotencyConflict`: same idempotency key used with incompatible payload.
- `ProcessingFailed`: worker or local AI step failed.
- `ExtractionValidationFailed`: LLM output could not be trusted as validated agreement data.
- `ExportFailed`: export generation failed.

API, UI, and test documents reference this taxonomy rather than redefining it.

## 8. Testing Strategy

See [TESTING.md](TESTING.md) for full testing strategy.

See [BDD.md](BDD.md) for business-readable BDD scenarios and scenario tags.

## 9. Database Migrations

Initial implementation creates all tables through Alembic migrations. Later changes use expand/contract migrations, backfills for derived case projections, and rollback scripts that preserve audit history.

## 10. Configuration

See [CONFIG.md](CONFIG.md) for full configuration.

## 11. Third-Party Integrations

The base delivery uses local dependencies rather than third-party financial integrations: PostgreSQL, Redis, Ollama, faster-whisper or whisper.cpp, Nginx, and Docker Compose. Bank, gateway, CRM, call-center, and notification providers remain optional add-ons.

## 12. Performance Specifications

- Upload and transcript submission return after validation, metadata persistence, and queue handoff.
- Transcription and extraction run in background workers with conservative concurrency.
- Case lists and dashboard queries use tenant-prefixed indexes and pagination.
- Export generation streams or runs asynchronously for large result sets.

## 13. Security Implementation

- Validate all request bodies, CSV rows, and LLM outputs.
- Encrypt or protect sensitive storage for recordings, transcripts, payment data, raw LLM output, and PII.
- Enforce tenant context in every repository method and worker job.
- Use audit logging for all finance-sensitive mutations.

## 14. Observability Implementation

Emit structured logs, metrics, and traces at request boundary, job start/end, local AI call, validation failure, matching outcome, reconciliation status assignment, review action, export creation, and reprocessing action.

## 15. Backwards Compatibility

No existing production API is present. After public API release, changes follow the versioning and deprecation policy in [API.md](API.md).

## 16. Technical Debt and Follow-ups

- Confirm extraction confidence threshold.
- Confirm first deployment tenant mode.
- Confirm notification scope.
- Confirm exact CSV import columns.
- Confirm retention periods for recordings, transcripts, raw LLM output, and audit logs.

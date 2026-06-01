# DEFINITIONS.md

> Status: This is a target design document. It does not mean every item is implemented today. Use [README.md](README.md) and [PLAN.md](PLAN.md) for the current implementation phase.


This file owns typed interfaces and function/class contracts. API payloads live in [API.md](API.md); data schemas live in [MODELS.md](MODELS.md).

## Base API Interfaces

Milestone 1 uses these names before the target tenant/auth/service surface is
introduced.

### Backend Layer Responsibilities

- Router layer: FastAPI route handlers parse HTTP inputs, call injected
  services, map expected not-found or validation failures to API errors, and do
  not compute reconciliation decisions.
- Service layer: application services validate request models, call pure domain
  functions, coordinate repositories, and return API response models.
- Repository layer: repositories own SQLAlchemy queries and map database rows to
  stored projections without HTTP, FastAPI, or business-rule decisions.
- Domain layer: pure functions, dataclasses, enums, and deterministic
  reconciliation rules that do not import FastAPI or SQLAlchemy sessions.
- Schema layer: Pydantic request and response models that match [API.md](API.md).
- Dependency layer: FastAPI dependency functions compose settings, sessions,
  repositories, and services for routers.

### Types

- `AgreementExtractionInputV1`: Pydantic request model matching [API.md](API.md).
- `ActualPaymentInputV1`: Pydantic request model matching [API.md](API.md).
- `ReconciliationCaseCreateRequestV1`: Base API request input that combines
  optional references, source text, extraction, and actual payment.
- `ReconciliationCaseCreateV1`: repository input that stores validated request
  snapshots and optional references.
- `ReconciliationCaseListResponseV1`: post-M1 named collection envelope for
  Base API list responses; M1.5 originally missed naming this DTO.
- `ValidatedAgreementExtraction`: normalized agreement fields accepted by the
  backend after schema validation.
- `ValidatedActualPayment`: normalized payment evidence accepted by the backend.
- `ReconciliationDecisionV1`: status, amounts, difference, currency, reason,
  review flag, and confidence returned by the pure decision function.
- `BaseReconciliationCase`: stored case projection matching [MODELS.md](MODELS.md).

### Pure Functions

- `validate_agreement_extraction_input(input: AgreementExtractionInputV1, confidence_threshold: float) -> ValidatedAgreementExtraction`
  - Rejects malformed LLM-shaped output before any database write.
  - Requires evidence text for review-prone extractions.
  - Does not call the LLM.

- `validate_actual_payment_input(input: ActualPaymentInputV1 | None) -> ValidatedActualPayment | None`
  - Normalizes manually supplied payment evidence.
  - Treats missing payment evidence as a valid input for `PAYMENT_NOT_FOUND`.

- `decide_base_reconciliation(extraction: ValidatedAgreementExtraction, actual_payment: ValidatedActualPayment | None, confidence_threshold: float) -> ReconciliationDecisionV1`
  - Applies deterministic rules in a fixed order.
  - Gives review-safe output when confidence is low, required agreement fields
    are missing, the extraction asks for human review, or currencies conflict.

### Configuration

- `EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD`: backend setting used by Base API
  validation and decision code. Default for Milestone 1 is `0.80`.

### Repository Port

- `BaseReconciliationCaseRepository` (class): Milestone 1 case persistence.
  - `create(input: ReconciliationCaseCreateV1, decision: ReconciliationDecisionV1) -> BaseReconciliationCase`
  - `list(status: ReconciliationStatus | None, limit: int, offset: int) -> list[BaseReconciliationCase]`
  - `get(case_id: UUID) -> BaseReconciliationCase | None`

### Application Service

- `BaseReconciliationCaseService` (class): validates Base API request input,
  computes the decision, persists the case, and maps repository projections to
  API response models.
  - `create_case(input: ReconciliationCaseCreateRequestV1) -> ReconciliationCaseResponseV1`
  - `list_cases(status: ReconciliationStatus | None, limit: int, offset: int) -> list[ReconciliationCaseListItemV1]`
  - `get_case(case_id: UUID) -> ReconciliationCaseResponseV1 | None`

## Ambient Context Types

- `TenantContext` (object): carries `tenantId`, `tenantStatus`, `locale`, and `currencyDefault`; layer: imperative shell.
- `UserContext` (object): carries `userId`, `tenantId`, `role`, and `permissions`; layer: imperative shell.
- `RequestContext` (object): carries `tenant`, `user`, `requestId`, and optional `idempotencyKey`; layer: imperative shell.
- `AuthzChecker` (class): `require(permission: Permission, ctx: RequestContext) -> Result[None, AuthzError]`; layer: imperative shell.
- `Clock` (object): `now() -> datetime`; layer: injected dependency.
- `Logger` (object): structured logging port; layer: imperative shell.
- `Tracer` (object): trace-span port; layer: imperative shell.

## Port Interfaces

- `CustomerRepository` (class): tenant-scoped customer persistence.
  - `create(ctx: RequestContext, input: CustomerCreate) -> Result[Customer, DomainError]`
  - `list(ctx: RequestContext, query: CustomerQuery) -> Result[Page[Customer], DomainError]`

- `IdempotencyRepository` (class): reserves, completes, replays, and expires API idempotency records.
  - `reserve(ctx: RequestContext, endpoint: str, method: HttpMethod, key: str, request_hash: str) -> Result[IdempotencyReservation, DomainError]`
  - `complete(ctx: RequestContext, reservation_id: IdempotencyRecordId, response: StoredResponse) -> Result[IdempotencyRecord, DomainError]`
  - `replay(ctx: RequestContext, endpoint: str, key: str, request_hash: str) -> Result[StoredResponse, DomainError]`

- `CallRepository` (class): call record and transcript persistence.
  - `create_call(ctx: RequestContext, input: CallCreate) -> Result[CallRecord, DomainError]`
  - `save_transcript(ctx: RequestContext, call_id: CallId, transcript: TranscriptCreate) -> Result[CallTranscript, DomainError]`
  - `update_status(ctx: RequestContext, call_id: CallId, expected: CallStatus, next: CallStatus) -> Result[CallRecord, DomainError]`

- `PaymentRepository` (class): payment persistence and candidate search.
  - `create(ctx: RequestContext, input: PaymentCreate) -> Result[Payment, DomainError]`
  - `search_candidates(ctx: RequestContext, criteria: PaymentMatchCriteria) -> Result[list[Payment], DomainError]`

- `ExtractionRepository` (class): agreement extraction persistence.
  - `save(ctx: RequestContext, input: AgreementExtractionCreate) -> Result[AgreementExtraction, DomainError]`
  - `get_current_for_call(ctx: RequestContext, call_id: CallId) -> Result[AgreementExtraction, DomainError]`

- `ReconciliationRepository` (class): case and case-payment persistence.
  - `create_or_update(ctx: RequestContext, decision: ReconciliationDecision) -> Result[ReconciliationCase, DomainError]`
  - `link_payment(ctx: RequestContext, case_id: CaseId, payment_id: PaymentId, amount_applied_minor: int) -> Result[ReconciliationCase, DomainError]`

- `AuditLogRepository` (class): append-only audit persistence.
  - `append(ctx: RequestContext, entry: AuditEntryCreate) -> Result[AuditLog, DomainError]`

- `JobQueue` (class): asynchronous job handoff.
  - `enqueue(ctx: RequestContext, job: ProcessingJob) -> Result[ProcessingAttempt, DomainError]`

- `TranscriptionAdapter` (class): local transcription runtime port.
  - `transcribe(recording_uri: str) -> Result[TranscriptDraft, ProcessingError]`

- `TranscriptionService` (class): coordinates audio transcription, transcript persistence, status transitions, and extraction handoff.
  - `transcribe_call(ctx: RequestContext, call_id: CallId, attempt_id: ProcessingAttemptId) -> Result[CallTranscript, DomainError]`
  - `submit_transcript(ctx: RequestContext, call_id: CallId, transcript: TranscriptDraft) -> Result[CallTranscript, DomainError]`

- `LocalLlmAdapter` (class): local LLM extraction runtime port.
  - `extract_agreement(transcript: str, prompt: ExtractionPrompt) -> Result[RawExtraction, ProcessingError]`

## Domain Functions

- `validate_extraction(raw: RawExtraction, threshold: float) -> Result[ValidatedExtraction, ExtractionValidationError]`
  - Layer: functional core.
  - Dependencies injected: none.
  - Returns validated agreement fields or typed validation errors.

- `match_candidate_payments(criteria: PaymentMatchCriteria, payments: list[Payment]) -> MatchResult`
  - Layer: functional core.
  - Dependencies injected: none.
  - Applies customer, phone, invoice, currency, date range, and amount signals.

- `decide_reconciliation(extraction: ValidatedExtraction, match_result: MatchResult) -> ReconciliationDecision`
  - Layer: functional core.
  - Dependencies injected: none.
  - Applies PRD reconciliation rules in deterministic order.

- `recalculate_case_after_review(case: ReconciliationCase, linked_payments: list[Payment], action: ReviewAction) -> ReconciliationDecision`
  - Layer: functional core.
  - Dependencies injected: none.
  - Recomputes paid amount, difference, status, and reason after manual action.

## Application Services

- `IntakeService` (class): creates call records, stores recordings, writes audit entries, and enqueues processing.
- `ProcessingService` (class): coordinates worker status, idempotency, and retry-safe state transitions.
- `ExtractionService` (class): orchestrates local LLM calls and validation.
- `PaymentService` (class): handles manual payments and CSV imports.
- `ReconciliationService` (class): runs matching and deterministic decisions.
- `ReviewService` (class): applies review actions with optimistic locking and audit logging.
- `ReportingService` (class): provides dashboard, filters, and exports.

Every service method receives `RequestContext` or a worker equivalent containing tenant context, request/job ID, logger, tracer, and idempotency key for mutations.

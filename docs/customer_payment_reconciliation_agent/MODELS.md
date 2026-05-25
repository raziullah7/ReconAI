# MODELS.md

**Feature**: customer_payment_reconciliation_agent  
**Stage**: spec  
**Last updated**: intentionally omitted  
**Owner**: data-modeler subagent pattern

See [PRD.md](PRD.md) for product requirements and [ARCH.md](ARCH.md) for architecture context.

## Modeling Principles

- Store money in minor units.
- Tenant-scoped entities include `tenantId` and tenant-prefixed indexes.
- Raw LLM output may be retained for audit/debugging, but validated extraction fields drive business logic.
- Reconciliation cases can link to multiple payments through `ReconciliationCasePayment`.
- Mutable records include audit columns and optimistic versioning.
- PII fields are tagged and require encryption at rest.

## Entity: Tenant

**Purpose**: Represents a company or operating unit using the system.  
**Storage**: PostgreSQL.  
**Relationships**: Tenant has many users, customers, call records, payments, reconciliation cases, and audit logs.  
**Constraints**: Tenant boundaries must not be crossed by API, worker, or repository access.  
**Data Lifecycle**: Created during setup; updated by admin; soft-deleted or deactivated before any erasure workflow.

```typescript
interface Tenant {
  id: string;
  name: string;
  status: 'ACTIVE' | 'SUSPENDED';
  locale: string;
  currencyDefault: string;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}
// Indexes: idx_tenants_status [status]
// Retention: active tenant metadata retained while tenant exists; erasure requires policy review because audit history depends on tenant identity.
```

## Entity: User

**Purpose**: Represents an authenticated user and role assignment.  
**Storage**: PostgreSQL.  
**Relationships**: User belongs to tenant and creates audit logs.  
**Constraints**: Email unique within tenant; roles limited to PRD roles.  
**Data Lifecycle**: Created by admin; deactivated instead of deleted where audit history references the user.

```typescript
interface User {
  id: string;
  tenantId: string;
  name: string;
  email: string;
  passwordHash: string;
  role: 'ADMIN' | 'FINANCE_USER' | 'REVIEWER' | 'MANAGER';
  isActive: boolean;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}
// PII: name, email encrypted at rest where supported.
// Indexes: idx_users_tenant_email [tenantId, email] unique where deletedAt is null; idx_users_tenant_role [tenantId, role].
// Retention: deactivated users retained for audit attribution; erasure replaces PII with tombstone values.
```

## Entity: Customer

**Purpose**: Stores customer identity and external reference information.  
**Storage**: PostgreSQL.  
**Relationships**: Customer belongs to tenant and has many call records and payments.  
**Constraints**: Customer records cannot link across tenants.  
**Data Lifecycle**: Created by finance/admin; updated as identity data changes; PII erasure keeps reconciliation references.

```typescript
interface Customer {
  id: string;
  tenantId: string;
  name: string;
  phoneNumber: string | null;
  email: string | null;
  externalReference: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}
// PII: name, phoneNumber, email encrypted at rest where supported.
// Indexes: idx_customers_tenant_phone [tenantId, phoneNumber]; idx_customers_tenant_external [tenantId, externalReference].
// Retention: active while cases exist; erasure redacts PII and keeps non-PII reconciliation linkage.
```

## Entity: CallRecord

**Purpose**: Stores uploaded call or transcript intake metadata and processing status.  
**Storage**: PostgreSQL plus local/object storage for recordings.  
**Relationships**: CallRecord belongs to tenant and customer; has one transcript, extraction, and reconciliation case.  
**Constraints**: Recording storage path must be tenant-scoped and not directly public.  
**Data Lifecycle**: Created at intake; status changes through pipeline; retained for audit.

```typescript
interface CallRecord {
  id: string;
  tenantId: string;
  customerId: string;
  phoneNumber: string | null;
  agentName: string | null;
  callStartedAt: Date | null;
  recordingUri: string | null;
  originalFilename: string | null;
  invoiceOrOrderReference: string | null;
  status: 'UPLOADED' | 'TRANSCRIBING' | 'TRANSCRIBED' | 'EXTRACTING' | 'EXTRACTED' | 'RECONCILING' | 'RECONCILED' | 'NEEDS_REVIEW' | 'FAILED';
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}
// Indexes: idx_call_records_tenant_customer [tenantId, customerId]; idx_call_records_tenant_status [tenantId, status]; idx_call_records_tenant_started [tenantId, callStartedAt].
// Retention: recording retention follows tenant policy; metadata retained for audit unless erased by policy.
```

## Entity: CallTranscript

**Purpose**: Stores transcript text and transcription metadata.  
**Storage**: PostgreSQL; large segment payloads may move to object storage later.  
**Relationships**: CallTranscript belongs to CallRecord.  
**Constraints**: One current transcript per call; reprocessing creates attempt history through ProcessingAttempt.  
**Data Lifecycle**: Created by transcription worker or transcript submission; retained for review and audit.

```typescript
interface CallTranscript {
  id: string;
  tenantId: string;
  callRecordId: string;
  transcriptText: string;
  language: string | null;
  transcriptionModel: string | null;
  confidence: number | null;
  speakerSegmentsJson: string | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}
// PII: transcriptText and speakerSegmentsJson may contain sensitive content and must be encrypted at rest.
// Indexes: idx_transcripts_tenant_call [tenantId, callRecordId] unique where deletedAt is null.
// Retention: retained with case evidence; erasure redacts transcript text if policy requires.
```

## Entity: AgreementExtraction

**Purpose**: Stores validated local LLM extraction output and raw context for debugging.  
**Storage**: PostgreSQL.  
**Relationships**: AgreementExtraction belongs to CallRecord and feeds ReconciliationCase.  
**Constraints**: Validated fields drive business logic; raw output is never used directly for status decisions.  
**Data Lifecycle**: Created by extraction worker; reprocessing creates a new current extraction and preserves prior attempts.

```typescript
interface AgreementExtraction {
  id: string;
  tenantId: string;
  callRecordId: string;
  agreedAmountMinor: number | null;
  currency: string | null;
  paymentType: 'FULL_PAYMENT' | 'ADVANCE' | 'PARTIAL_PAYMENT' | 'INSTALLMENT' | 'BALANCE_PAYMENT' | 'DISCOUNTED_AMOUNT' | 'UNKNOWN';
  dueDate: string | null;
  isFinalAmount: boolean | null;
  evidenceText: string | null;
  confidence: number;
  needsHumanReview: boolean;
  rawLlmOutput: string;
  modelName: string;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}
// PII: evidenceText and rawLlmOutput may contain sensitive content.
// Indexes: idx_extractions_tenant_call [tenantId, callRecordId]; idx_extractions_tenant_review [tenantId, needsHumanReview].
// Constraints: confidence between 0 and 1; amount values use minor units when present.
```

## Entity: Payment

**Purpose**: Stores actual payment records from manual entry or import.  
**Storage**: PostgreSQL.  
**Relationships**: Payment belongs to tenant and customer; links to reconciliation cases through ReconciliationCasePayment.  
**Constraints**: Transaction reference should be unique within tenant when present.  
**Data Lifecycle**: Created manually or by import; corrected through auditable updates.

```typescript
interface Payment {
  id: string;
  tenantId: string;
  customerId: string | null;
  phoneNumber: string | null;
  invoiceId: string | null;
  amountMinor: number;
  currency: string;
  paymentMethod: string | null;
  transactionReference: string | null;
  paymentDate: string;
  source: 'MANUAL' | 'CSV_IMPORT';
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}
// Indexes: idx_payments_tenant_customer [tenantId, customerId]; idx_payments_tenant_phone [tenantId, phoneNumber]; idx_payments_tenant_invoice [tenantId, invoiceId]; idx_payments_tenant_date_currency_amount [tenantId, paymentDate, currency, amountMinor]; idx_payments_tenant_tx_ref [tenantId, transactionReference] unique where transactionReference is not null.
// Retention: retained for financial audit; erasure redacts non-required PII only.
// Future-only sources such as bank statement, payment gateway, and API imports require separate integration design before they become accepted values.
```

## Entity: IdempotencyRecord

**Purpose**: Stores replay and conflict data for mutating API idempotency keys.  
**Storage**: PostgreSQL.  
**Relationships**: Belongs to tenant and may reference the created resource.  
**Constraints**: Key is unique within tenant and endpoint scope until expiry.  
**Data Lifecycle**: Created before mutating side effects; completed with response snapshot; expired after configured TTL.

```typescript
interface IdempotencyRecord {
  id: string;
  tenantId: string;
  key: string;
  endpoint: string;
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  requestHash: string;
  status: 'RESERVED' | 'COMPLETED' | 'FAILED' | 'EXPIRED';
  responseStatusCode: number | null;
  responseBodyJson: string | null;
  resourceType: string | null;
  resourceId: string | null;
  expiresAt: Date;
  createdAt: Date;
  updatedAt: Date;
}
// Indexes: idx_idempotency_tenant_key_endpoint [tenantId, key, endpoint] unique; idx_idempotency_tenant_expires [tenantId, expiresAt].
// Constraints: same key with different requestHash returns IdempotencyConflict; completed records replay response body and status.
// Retention: retained until TTL expiry, then purged or marked EXPIRED.
```

## Entity: ReconciliationCase

**Purpose**: Stores final or current reconciliation result and review state.  
**Storage**: PostgreSQL.  
**Relationships**: Belongs to tenant, call record, extraction, reviewer user, and linked payments.  
**Constraints**: Status must be one of the PRD reconciliation outcomes.  
**Data Lifecycle**: Created during reconciliation; updated by rule engine or reviewer action; retained for audit.

```typescript
interface ReconciliationCase {
  id: string;
  tenantId: string;
  callRecordId: string;
  agreementExtractionId: string;
  agreedAmountMinor: number | null;
  paidAmountMinor: number | null;
  differenceMinor: number | null;
  currency: string | null;
  status: 'RECONCILED' | 'UNDERPAID' | 'OVERPAID' | 'PARTIAL_PAYMENT' | 'PAYMENT_NOT_FOUND' | 'MULTIPLE_MATCHES_FOUND' | 'NEEDS_REVIEW' | 'FAILED';
  reason: string;
  confidence: number | null;
  reviewedBy: string | null;
  reviewedAt: Date | null;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}
// Indexes: idx_cases_tenant_status [tenantId, status]; idx_cases_tenant_call [tenantId, callRecordId]; idx_cases_tenant_reviewed [tenantId, reviewedBy].
// Constraints: differenceMinor equals paidAmountMinor minus agreedAmountMinor when both values exist.
```

## Entity: ReconciliationCasePayment

**Purpose**: Join table linking reconciliation cases to one or more payments.  
**Storage**: PostgreSQL.  
**Relationships**: Belongs to tenant, reconciliation case, and payment.  
**Constraints**: Case and payment tenant IDs must match.  
**Data Lifecycle**: Created by matcher or reviewer; removed only through auditable unlink action.

```typescript
interface ReconciliationCasePayment {
  id: string;
  tenantId: string;
  reconciliationCaseId: string;
  paymentId: string;
  amountAppliedMinor: number;
  createdAt: Date;
  createdBy: string | null;
}
// Indexes: idx_case_payments_tenant_case [tenantId, reconciliationCaseId]; idx_case_payments_tenant_payment [tenantId, paymentId].
// Constraints: unique [tenantId, reconciliationCaseId, paymentId].
```

## Entity: ProcessingAttempt

**Purpose**: Captures transcription, extraction, matching, reconciliation, export, and reprocessing attempts.  
**Storage**: PostgreSQL.  
**Relationships**: Belongs to tenant and may reference call record or case.  
**Constraints**: Idempotency key unique within tenant and operation.  
**Data Lifecycle**: Created for async jobs; updated on completion or failure; retained for observability and audit.

```typescript
interface ProcessingAttempt {
  id: string;
  tenantId: string;
  operation: 'TRANSCRIPTION' | 'EXTRACTION' | 'MATCHING' | 'RECONCILIATION' | 'EXPORT' | 'REPROCESSING';
  targetType: string;
  targetId: string;
  idempotencyKey: string;
  status: 'QUEUED' | 'RUNNING' | 'SUCCEEDED' | 'FAILED' | 'CANCELLED';
  errorCode: string | null;
  errorMessage: string | null;
  startedAt: Date | null;
  finishedAt: Date | null;
  createdAt: Date;
  updatedAt: Date;
}
// Indexes: idx_attempts_tenant_target [tenantId, targetType, targetId]; idx_attempts_tenant_idempotency [tenantId, operation, idempotencyKey] unique.
// Retention: retained long enough for operational diagnostics and audit review.
```

## Entity: AuditLog

**Purpose**: Stores system and user action history.  
**Storage**: PostgreSQL.  
**Relationships**: Belongs to tenant and optionally user; references arbitrary entity by type and ID.  
**Constraints**: Append-only after creation.  
**Data Lifecycle**: Created by system and user actions; retained for finance audit.

```typescript
interface AuditLog {
  id: string;
  tenantId: string;
  userId: string | null;
  entityType: string;
  entityId: string;
  action: 'USER_CREATED' | 'USER_UPDATED' | 'CONFIG_UPDATED' | 'CUSTOMER_CREATED' | 'CUSTOMER_UPDATED' | 'CALL_UPLOADED' | 'TRANSCRIPT_SUBMITTED' | 'TRANSCRIPT_GENERATED' | 'AGREEMENT_EXTRACTED' | 'PAYMENT_CREATED' | 'PAYMENT_IMPORTED' | 'PAYMENT_MATCHED' | 'CASE_RECONCILED' | 'CASE_APPROVED' | 'CASE_REJECTED' | 'CASE_AGREED_AMOUNT_EDITED' | 'REVIEW_NOTE_ADDED' | 'PAYMENT_LINKED' | 'PAYMENT_UNLINKED' | 'REPROCESSING_STARTED' | 'EXPORT_CREATED';
  oldValueJson: string | null;
  newValueJson: string | null;
  description: string;
  requestId: string | null;
  createdAt: Date;
}
// Indexes: idx_audit_tenant_entity [tenantId, entityType, entityId]; idx_audit_tenant_created [tenantId, createdAt]; idx_audit_tenant_user [tenantId, userId].
// Retention: append-only financial audit history; PII in value payloads should be minimized or redacted.
```

## Open Questions

- OQ-MODELS-01: Confirm exact retention periods for recordings, transcripts, raw LLM output, and audit logs.
- OQ-MODELS-02: Confirm whether tenant management is user-facing in the first delivery or seeded administratively.

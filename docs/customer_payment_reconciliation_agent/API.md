# API.md

## Versioning Strategy

Use URL path versioning with `/v1`. The current planned API version is `/v1`. Deprecated endpoints use `Deprecation` and `Sunset` headers without embedding calendar dates in planning docs.

## Error Envelope

All non-2xx responses use the canonical error taxonomy from [SPEC.md](SPEC.md#7-error-handling-strategy):

```json
{
  "error": {
    "code": "ValidationFailed",
    "message": "Human-readable message",
    "request_id": "request-id"
  }
}
```

## Shared API Rules

- Authentication: Bearer JWT except login.
- Tenant scoping: path-based `/v1/tenants/{tenant_id}/...` plus token authorization for the tenant.
- Idempotency: `Idempotency-Key` required for mutating POST/PATCH/DELETE endpoints. Duplicate key plus identical payload hash replays the stored response; duplicate key plus different payload hash returns `IdempotencyConflict`.
- Pagination: cursor pagination for list endpoints with `limit` bounds and `has_more` response field.
- Rate limits: per-tenant and per-user buckets; `429` includes `Retry-After` and `X-RateLimit-*` headers.
- Webhooks: not included in base delivery; future outgoing webhooks must be HMAC-signed and replay-protected.

## Shared Schemas

```typescript
type UUID = string;
type DateTime = string;
type DateOnly = string;
type CurrencyCode = string;
type MinorMoney = number;
type Role = 'ADMIN' | 'FINANCE_USER' | 'REVIEWER' | 'MANAGER';
type CallStatus = 'UPLOADED' | 'TRANSCRIBING' | 'TRANSCRIBED' | 'EXTRACTING' | 'EXTRACTED' | 'RECONCILING' | 'RECONCILED' | 'NEEDS_REVIEW' | 'FAILED';
type PaymentType = 'FULL_PAYMENT' | 'ADVANCE' | 'PARTIAL_PAYMENT' | 'INSTALLMENT' | 'BALANCE_PAYMENT' | 'DISCOUNTED_AMOUNT' | 'UNKNOWN';
type PaymentSource = 'MANUAL' | 'CSV_IMPORT';
type ReconciliationStatus = 'RECONCILED' | 'UNDERPAID' | 'OVERPAID' | 'PARTIAL_PAYMENT' | 'PAYMENT_NOT_FOUND' | 'MULTIPLE_MATCHES_FOUND' | 'NEEDS_REVIEW' | 'FAILED';
type ReviewActionType = 'APPROVE' | 'REJECT' | 'EDIT_AGREED_AMOUNT' | 'LINK_PAYMENT' | 'UNLINK_PAYMENT' | 'ADD_NOTE';

interface Page<T> {
  items: T[];
  next_cursor: string | null;
  has_more: boolean;
}

interface UserSession {
  access_token: string;
  token_type: 'Bearer';
  user: UserSummary;
  tenant: TenantSummary;
}

interface TenantSummary { id: UUID; name: string; locale: string; currency_default: CurrencyCode; }
interface UserSummary { id: UUID; name: string; email: string; role: Role; }
interface Customer { id: UUID; name: string; phone_number?: string; email?: string; external_reference?: string; created_at: DateTime; updated_at: DateTime; }
interface CustomerCreateRequest { name: string; phone_number?: string; email?: string; external_reference?: string; }
interface CustomerListQuery { cursor?: string; limit?: number; search?: string; external_reference?: string; }

interface CallCreateRequest {
  customer_id: UUID;
  phone_number?: string;
  agent_name?: string;
  call_started_at?: DateTime;
  invoice_or_order_reference?: string;
  recording_upload_id?: string;
  transcript_text?: string;
  original_filename?: string;
}
interface CallSummary { id: UUID; customer_id: UUID; status: CallStatus; created_at: DateTime; updated_at: DateTime; status_url: string; }
interface CallDetail extends CallSummary { phone_number?: string; agent_name?: string; invoice_or_order_reference?: string; transcript_available: boolean; extraction_id?: UUID; case_id?: UUID; }
interface TranscriptResponse { call_id: UUID; transcript_text: string; language?: string; transcription_model?: string; confidence?: number; speaker_segments?: unknown[]; }

interface PaymentCreateRequest { customer_id?: UUID; phone_number?: string; invoice_id?: string; amount_minor: MinorMoney; currency: CurrencyCode; payment_method?: string; transaction_reference?: string; payment_date: DateOnly; }
interface Payment { id: UUID; customer_id?: UUID; phone_number?: string; invoice_id?: string; amount_minor: MinorMoney; currency: CurrencyCode; payment_method?: string; transaction_reference?: string; payment_date: DateOnly; source: PaymentSource; created_at: DateTime; updated_at: DateTime; }
interface PaymentListQuery { cursor?: string; limit?: number; customer_id?: UUID; phone_number?: string; invoice_id?: string; currency?: CurrencyCode; payment_date_from?: DateOnly; payment_date_to?: DateOnly; amount_min_minor?: MinorMoney; amount_max_minor?: MinorMoney; }
interface PaymentImportRequest { file_upload_id: string; dry_run?: boolean; }
interface PaymentImportResponse { import_id: UUID; accepted_rows: number; rejected_rows: number; row_errors: Array<{ row_number: number; code: string; message: string }>; }

interface ReprocessRequest { operation: 'TRANSCRIPTION' | 'EXTRACTION'; reason: string; }
interface ProcessingAttemptResponse { id: UUID; operation: string; status: 'QUEUED' | 'RUNNING' | 'SUCCEEDED' | 'FAILED' | 'CANCELLED'; status_url: string; }

interface CaseListQuery { cursor?: string; limit?: number; status?: ReconciliationStatus; date_from?: DateOnly; date_to?: DateOnly; customer_id?: UUID; agent_name?: string; payment_method?: string; amount_min_minor?: MinorMoney; amount_max_minor?: MinorMoney; }
interface CaseSummary { id: UUID; customer_id: UUID; status: ReconciliationStatus; agreed_amount_minor?: MinorMoney; paid_amount_minor?: MinorMoney; difference_minor?: MinorMoney; currency?: CurrencyCode; reason: string; updated_at: DateTime; }
interface CaseDetail extends CaseSummary { call_id: UUID; extraction_id: UUID; transcript_excerpt?: string; evidence_text?: string; candidate_payments: Payment[]; audit_log_url: string; version: number; }
interface ReviewActionRequest { action: ReviewActionType; expected_case_version: number; agreed_amount_minor?: MinorMoney; payment_id?: UUID; amount_applied_minor?: MinorMoney; note: string; }
interface ReviewActionResponse { case: CaseDetail; audit_log_id: UUID; }
interface AuditEntry { id: UUID; user_id?: UUID; entity_type: string; entity_id: UUID; action: string; description: string; old_value?: unknown; new_value?: unknown; created_at: DateTime; }
interface DashboardSummary { status_counts: Record<ReconciliationStatus, number>; failure_count: number; review_queue_count: number; total_cases: number; filters_applied: Record<string, string>; }
interface ExportRequest { format: 'CSV' | 'XLSX'; filters: CaseListQuery; }
interface ExportResponse { export_id: UUID; status: 'QUEUED' | 'RUNNING' | 'SUCCEEDED' | 'FAILED'; download_url?: string; }
```

## Endpoints

### POST /v1/tenants/{tenant_id}/auth/login

Authentication: public within tenant login context.  
Authorization: no prior role; response role gates later requests.  
Idempotency: not applicable.  
Request body: `{ email: string; password: string }`.  
Response `200`: `UserSession`.  
Errors: `Unauthenticated`, `ValidationFailed`, `TenantSuspended`, `RateLimited`.

### GET /v1/tenants/{tenant_id}/customers

Authentication: Bearer JWT.  
Authorization: Admin, Finance User, Reviewer, Manager.  
Tenant scoping: path plus token tenant access.  
Idempotency: not applicable.  
Query: `CustomerListQuery`.  
Response `200`: `Page<Customer>`.  
Errors: `Forbidden`, `RateLimited`.

### POST /v1/tenants/{tenant_id}/customers

Authentication: Bearer JWT.  
Authorization: Admin, Finance User.  
Tenant scoping: path plus token tenant access.  
Idempotency: `Idempotency-Key` required.  
Request body: `CustomerCreateRequest`.  
Response `201`: `Customer`.  
Errors: `ValidationFailed`, `Forbidden`, `IdempotencyConflict`.

### POST /v1/tenants/{tenant_id}/calls

Authentication: Bearer JWT.  
Authorization: Admin, Finance User.  
Tenant scoping: path plus token tenant access.  
Idempotency: `Idempotency-Key` required.  
Request body: `CallCreateRequest`; exactly one of `recording_upload_id` or `transcript_text` must be supplied.  
Response `202`: `CallSummary`.  
Errors: `ValidationFailed`, `Forbidden`, `FeatureNotEnabled`, `ProcessingFailed`, `IdempotencyConflict`.

### GET /v1/tenants/{tenant_id}/calls/{call_id}

Authentication: Bearer JWT.  
Authorization: Admin, Finance User, Reviewer, Manager.  
Tenant scoping: path plus token tenant access and call ownership.  
Idempotency: not applicable.  
Response `200`: `CallDetail`.  
Errors: `NotFound`, `Forbidden`.

### GET /v1/tenants/{tenant_id}/calls/{call_id}/transcript

Authentication: Bearer JWT.  
Authorization: Admin, Finance User, Reviewer, Manager.  
Tenant scoping: path plus token tenant access and call ownership.  
Idempotency: not applicable.  
Response `200`: `TranscriptResponse`.  
Errors: `NotFound`, `Forbidden`.

### POST /v1/tenants/{tenant_id}/payments

Authentication: Bearer JWT.  
Authorization: Admin, Finance User.  
Tenant scoping: path plus token tenant access.  
Idempotency: `Idempotency-Key` required.  
Request body: `PaymentCreateRequest`; `amount_minor` must be a positive integer and `currency` is required.  
Response `201`: `Payment` with `source = MANUAL`.  
Errors: `ValidationFailed`, `Conflict`, `Forbidden`, `IdempotencyConflict`.

### POST /v1/tenants/{tenant_id}/payments/imports

Authentication: Bearer JWT.  
Authorization: Admin, Finance User.  
Tenant scoping: path plus token tenant access.  
Idempotency: `Idempotency-Key` required.  
Request body: `PaymentImportRequest`.  
Response `202`: `PaymentImportResponse`.  
Errors: `ValidationFailed`, `Forbidden`, `ProcessingFailed`, `IdempotencyConflict`.

### GET /v1/tenants/{tenant_id}/payments

Authentication: Bearer JWT.  
Authorization: Admin, Finance User, Reviewer.  
Tenant scoping: path plus token tenant access.  
Idempotency: not applicable.  
Query: `PaymentListQuery`.  
Response `200`: `Page<Payment>`.  
Errors: `Forbidden`, `RateLimited`.

### POST /v1/tenants/{tenant_id}/calls/{call_id}/reprocess

Authentication: Bearer JWT.  
Authorization: Admin, Reviewer.  
Tenant scoping: path plus token tenant access and call ownership.  
Idempotency: `Idempotency-Key` required.  
Request body: `ReprocessRequest`.  
Response `202`: `ProcessingAttemptResponse`.  
Errors: `ValidationFailed`, `Forbidden`, `Conflict`, `ProcessingFailed`, `IdempotencyConflict`.

### GET /v1/tenants/{tenant_id}/cases

Authentication: Bearer JWT.  
Authorization: Admin, Finance User, Reviewer, Manager.  
Tenant scoping: path plus token tenant access.  
Idempotency: not applicable.  
Query: `CaseListQuery`.  
Response `200`: `Page<CaseSummary>`.  
Errors: `Forbidden`, `RateLimited`.

### GET /v1/tenants/{tenant_id}/cases/{case_id}

Authentication: Bearer JWT.  
Authorization: Admin, Finance User, Reviewer, Manager.  
Tenant scoping: path plus token tenant access and case ownership.  
Idempotency: not applicable.  
Response `200`: `CaseDetail`.  
Errors: `NotFound`, `Forbidden`.

### POST /v1/tenants/{tenant_id}/cases/{case_id}/review-actions

Authentication: Bearer JWT.  
Authorization: Admin and Reviewer; Finance User only if product policy confirms review authority.  
Tenant scoping: path plus token tenant access and case ownership.  
Idempotency: `Idempotency-Key` required.  
Request body: `ReviewActionRequest`; `note` is required for all actions and `expected_case_version` enforces optimistic locking.  
Response `200`: `ReviewActionResponse`.  
Errors: `ValidationFailed`, `Forbidden`, `Conflict`, `IdempotencyConflict`.

### GET /v1/tenants/{tenant_id}/cases/{case_id}/audit-log

Authentication: Bearer JWT.  
Authorization: Admin, Reviewer, Manager; Finance User for accessible cases.  
Tenant scoping: path plus token tenant access and case ownership.  
Idempotency: not applicable.  
Response `200`: `Page<AuditEntry>`.  
Errors: `NotFound`, `Forbidden`.

### GET /v1/tenants/{tenant_id}/dashboard/summary

Authentication: Bearer JWT.  
Authorization: Admin, Finance User, Reviewer, Manager.  
Tenant scoping: path plus token tenant access.  
Idempotency: not applicable.  
Query: date range and optional `CaseListQuery` filters.  
Response `200`: `DashboardSummary`.  
Errors: `Forbidden`, `RateLimited`.

### POST /v1/tenants/{tenant_id}/exports/reconciliation-cases

Authentication: Bearer JWT.  
Authorization: Admin, Manager.  
Tenant scoping: path plus token tenant access.  
Idempotency: `Idempotency-Key` required.  
Request body: `ExportRequest`.  
Response `202`: `ExportResponse`.  
Errors: `ValidationFailed`, `Forbidden`, `FeatureNotEnabled`, `ExportFailed`, `IdempotencyConflict`.

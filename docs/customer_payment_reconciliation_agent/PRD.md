# PRD.md

## 1. Introduction

ReconAI is a workflow-based customer payment reconciliation system. It checks whether the amount discussed or agreed with a customer during a call matches the amount actually paid, so finance, operations, support, and sales teams can reduce manual reconciliation effort and quickly identify exceptions.

The LLM helps understand the call. The backend validates extracted data. Deterministic rules decide financial reconciliation outcomes. Humans review exceptions.

## 2. Goals

- G-001: Allow users to submit a call recording or transcript for reconciliation.
- G-002: Extract payment agreement details locally without relying on a hosted LLM.
- G-003: Compare extracted agreement data against actual payment records using deterministic backend rules.
- G-004: Route unclear, low-confidence, mismatched, missing-payment, and multi-match cases to human review.
- G-005: Maintain an auditable trail from upload through review decision and reporting.
- G-006: Deliver a complete single-scope app that can run on a limited single-server deployment.

## 3. Users and Roles

### US-001: Admin manages the system
**Description:** As an Admin, I want to manage users, configuration, reprocessing, and operational oversight so that the system remains controlled and auditable.

**Acceptance Criteria:**
- [ ] Admin can access user, configuration, reprocessing, and operational areas.
- [ ] Admin-only actions are denied to non-admin users.
- [ ] Admin actions that affect reconciliation history are audit logged.

### US-002: Finance User reconciles payments
**Description:** As a Finance User, I want to upload calls, manage customers and payments, and view reconciliation results so that I can resolve routine finance work faster.

**Acceptance Criteria:**
- [ ] Finance User can create customers and payment records.
- [ ] Finance User can submit a call recording or transcript.
- [ ] Finance User can view status, result, evidence, and review queue items allowed by role.

### US-003: Reviewer resolves exceptions
**Description:** As a Reviewer, I want to inspect unclear cases and decide how to resolve them so that risky outcomes are not silently finalized.

**Acceptance Criteria:**
- [ ] Reviewer can inspect transcript evidence, extracted values, candidate payments, status, reason, and audit history.
- [ ] Reviewer can approve, reject, edit the agreed amount when appropriate, manually link or unlink payment, and add notes.
- [ ] Reviewer actions update the case and create audit entries.

### US-004: Manager monitors outcomes
**Description:** As a Manager, I want dashboards, filters, exports, and audit visibility so that I can track reconciliation quality and operational workload.

**Acceptance Criteria:**
- [ ] Manager can view dashboard totals, statuses, failures, and review counts.
- [ ] Manager can filter by date, customer, agent, payment method, status, and amount range.
- [ ] Manager can export filtered reconciliation results to CSV or Excel.

## 4. Functional Requirements

- FR-01: The system must authenticate users and authorize actions through Admin, Finance User, Reviewer, and Manager roles.
- FR-02: The system must store customers with name, phone number, email, external reference, and tenant or company relationship.
- FR-03: The system must accept call recordings and transcript submissions with customer, phone number, call date, agent, and optional invoice or order reference metadata.
- FR-04: The system must convert uploaded audio calls into text using a local transcription service such as faster-whisper or whisper.cpp.
- FR-05: The system must store transcript text, language, transcription model, confidence, and speaker-level segments when available.
- FR-06: The system must use a local LLM to extract agreed amount, currency, payment type, due date, evidence text, confidence, and review flag.
- FR-07: The system must support manual payment entry and CSV payment import; future bank statement and payment gateway integrations are optional add-ons.
- FR-08: The system must match calls to candidate payments using customer ID, phone number, invoice ID, currency, payment date range, and amount similarity.
- FR-09: The system must use backend rules to compare agreed and paid amounts and assign final reconciliation status.
- FR-10: The system must route unclear, low-confidence, mismatched, or multi-match cases to a human review queue.
- FR-11: The system must log major system and user actions including upload, transcript generation, extraction, matching, reconciliation, approval, rejection, payment linking, and payment unlinking.
- FR-12: The system must show dashboard totals, statuses, failures, review queues, and filters.
- FR-13: The system must export filtered reconciliation results to CSV or Excel.
- FR-14: The system must allow admins or reviewers to re-run transcription or extraction while preserving previous versions through audit history.
- FR-15: The system may notify finance or operations users about mismatches, underpayments, overpayments, and payment-not-found cases when notifications are included in scope.

## 5. Reconciliation Rules

- RR-01: Low-confidence extraction becomes `NEEDS_REVIEW`.
- RR-02: No candidate payment becomes `PAYMENT_NOT_FOUND`.
- RR-03: Ambiguous multiple candidates become `MULTIPLE_MATCHES_FOUND`.
- RR-04: Advance, partial, or installment payment types become `PARTIAL_PAYMENT`.
- RR-05: Exact paid and agreed amount match becomes `RECONCILED`.
- RR-06: Paid amount below agreed amount becomes `UNDERPAID`.
- RR-07: Paid amount above agreed amount becomes `OVERPAID`.
- RR-08: Any unclear result defaults to `NEEDS_REVIEW`.

## 6. Non-Functional Requirements

- NFR-01 Accuracy: The LLM must not make final financial decisions; it only extracts structured data.
- NFR-02 Auditability: Every result must be explainable with transcript evidence, extracted amount, matched payment, difference, reason, and reviewer actions.
- NFR-03 Low Resource: The system must use small local models, limited worker concurrency, queue-based processing, and avoid many heavy jobs at once.
- NFR-04 Security: The system must protect customer data, call recordings, transcripts, payment records, and user accounts through authentication, authorization, secure storage, and validation.
- NFR-05 Reliability: The system must use retries, status tracking, failure states, idempotent jobs, and safe reprocessing.
- NFR-06 Performance: Upload requests must return quickly; transcription and LLM extraction must run in background workers.
- NFR-07 Scalability: The initial deployment must run on one VPS using Docker Compose and allow later separation of workers, database, storage, and AI services.
- NFR-08 Maintainability: Backend modules must keep transcription, extraction, payment matching, reconciliation, review, and audit logic separated.
- NFR-09 Observability: The system must log job status, processing time, failures, model confidence, and reconciliation outcomes.

## 7. Non-Goals

- NG-01: Bank statement integrations are not required for the base delivery.
- NG-02: Payment gateway integrations are not required for the base delivery.
- NG-03: CRM or call-center integrations are not required for the base delivery.
- NG-04: Customer notifications are optional unless explicitly included.
- NG-05: Advanced analytics beyond dashboard counts, filters, and exports are optional.
- NG-06: Subscription billing and full multi-tenant SaaS packaging are optional add-ons.
- NG-07: PDF report export is optional.

## 8. Product Constraints

- PC-01: Use local transcription and local LLM extraction.
- PC-02: Store money in minor units.
- PC-03: Retain raw LLM output for audit/debugging but use validated fields for business logic only.
- PC-04: Use a many-to-many relationship between reconciliation cases and payments.
- PC-05: Run the complete system on a limited single VPS using Docker Compose.
- PC-06: Limit worker concurrency because transcription and local LLM inference are CPU/RAM-heavy.

## 9. Success Metrics

- SM-01: A user can upload a call recording and see processing status.
- SM-02: The system generates and stores a transcript for an uploaded call.
- SM-03: The local LLM extracts payment agreement details into validated structured fields.
- SM-04: A finance user can create or import payment records.
- SM-05: The system matches candidate payments using the agreed matching signals.
- SM-06: The reconciliation engine produces the expected status and difference amount.
- SM-07: Unclear or risky cases route to review instead of being silently accepted.
- SM-08: A reviewer can approve, reject, edit, or manually link a payment and trigger recalculation.
- SM-09: Major actions are stored in audit logs.
- SM-10: Dashboard and reports show the required statuses and filters.
- SM-11: The full system runs on the target server using the agreed deployment configuration.

## 10. Open Questions

- OQ-01: Which local LLM model is preferred for the first implementation when the server is resource-constrained?
- OQ-02: Are notifications included in the first delivery or deferred?
- OQ-03: Should tenants be enabled from the beginning or kept as a single-company model with tenant-ready schemas?
- OQ-04: What confidence threshold routes extraction to human review?
- OQ-05: What exact CSV columns must be accepted for payment import?

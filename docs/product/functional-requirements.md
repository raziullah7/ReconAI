# Functional Requirements

## Project Purpose

The Customer Payment Reconciliation Agent checks whether the amount agreed with a customer during a call matches the amount actually paid. It is meant for finance, operations, support, and sales teams that need a clearer and more auditable reconciliation process.

## Core Principle

The LLM helps understand the call, but it does not make final financial decisions.

The backend validates extracted data, deterministic reconciliation rules decide the outcome, and humans review exceptions.

## Users and Roles

- Admin: manages users, configuration, reprocessing, and operational oversight.
- Finance User: uploads calls, manages payment data, views reconciliation results, and handles routine finance workflows.
- Reviewer: reviews unclear, risky, mismatched, or ambiguous cases.
- Manager: views dashboards, reports, summaries, and audit history.

## Main Functional Requirements

### Authentication and Access Control

The system should allow authorized users to log in and access features based on role. Core roles are Admin, Finance User, Reviewer, and Manager.

### Customer Management

The system should store and manage customer identity information such as name, phone number, email, and external reference. If the product is used by more than one company or business unit, customer records should be associated with the right tenant or company context.

### Call Upload

Finance users or admins should be able to upload a customer call recording or provide a transcript. Call metadata should include the customer, phone number, call date, agent name, and optional invoice or order reference.

### Call Transcription

Uploaded audio recordings should be converted into text using a local transcription service. The system should keep enough transcript metadata to support review and auditability, including language, model information, confidence, and speaker-level details where available.

### Transcript Management

Users should be able to view transcripts from the dashboard or case detail view. Transcript evidence should remain available when a reconciliation result needs explanation or review.

### Payment Agreement Extraction

The system should use a local LLM to extract structured payment agreement details from the transcript. Expected extracted information includes agreed amount, currency, payment type, due date, evidence text, confidence, and a review flag.

The extracted output should be validated before it is used by business rules.

### Payment Data Management

Finance users should be able to add payment records manually and import payments from CSV files. The design should leave room for future bank statement, payment gateway, or API integrations.

### Payment Matching

The system should match calls to candidate payments using practical matching signals such as customer, phone number, invoice or order reference, currency, payment date range, and amount similarity.

### Reconciliation Engine

The backend should compare the agreed amount with the paid amount using deterministic rules. The LLM output should not directly decide the final financial result.

Expected reconciliation statuses include:

- RECONCILED
- UNDERPAID
- OVERPAID
- PARTIAL_PAYMENT
- PAYMENT_NOT_FOUND
- MULTIPLE_MATCHES_FOUND
- NEEDS_REVIEW
- FAILED

### Human Review Queue

The system should route unclear, low-confidence, mismatched, or multi-match cases to a review queue. Reviewers should be able to inspect the call, transcript, extracted evidence, payment candidates, reason, and reconciliation status.

Reviewers should be able to approve, reject, edit the agreed amount when appropriate, manually link a payment, and add review notes.

### Audit Trail

The system should log important system and user actions. Audit history should cover upload, transcription, extraction, matching, reconciliation, approval, rejection, payment linking, and payment unlinking.

### Dashboard and Filters

The dashboard should show totals, reconciliation statuses, failures, review queue counts, and summary metrics. Users should be able to filter by date, customer, agent, payment method, status, and amount range.

### Reporting and Export

Managers and admins should be able to export filtered reconciliation results to CSV or Excel. PDF report export can be treated as optional unless explicitly included later.

### Reprocessing

Admins or reviewers should be able to re-run transcription or extraction when a result fails or appears incorrect. Previous results should remain traceable through audit history.

### Notifications

Notifications for mismatches, underpayments, overpayments, and payment-not-found cases are optional unless explicitly requested for the first delivery.

## High-Level Data Concepts

At the design level, the system works with these concepts:

- Customers
- Users and roles
- Uploaded calls
- Transcripts
- Payment agreement extractions
- Actual payment records
- Reconciliation cases
- Manually linked payments
- Review actions
- Audit history

Exact database table names, fields, indexes, and migrations are intentionally not defined in this document.

## Reconciliation Rule Intent

The reconciliation logic should follow this business intent:

- Low-confidence extraction goes to NEEDS_REVIEW.
- No candidate payment becomes PAYMENT_NOT_FOUND.
- Ambiguous multiple candidates become MULTIPLE_MATCHES_FOUND.
- Advance, partial, or installment payment types become PARTIAL_PAYMENT.
- Exact paid/agreed amount match becomes RECONCILED.
- Paid amount below agreed amount becomes UNDERPAID.
- Paid amount above agreed amount becomes OVERPAID.
- Any unclear result defaults to NEEDS_REVIEW.

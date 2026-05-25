# High-Level Design

Source spec: `/home/dell/Downloads/customer_payment_reconciliation_agent_dark.pdf`

Source version: 1.1, dated 21 May 2026

## Architecture Pattern

The system follows an event-driven pipeline with deterministic reconciliation and a human review queue.

The LLM is not treated as an autonomous financial decision maker. It is an extraction component inside a controlled backend workflow.

## Main System Areas

### Frontend

The frontend should provide the user-facing workflow for finance, review, management, and admin tasks. Expected areas include call upload, customer/payment management, reconciliation dashboard, case detail views, review queue, audit history, and exports.

### Backend API

The backend API should handle validation, authentication, authorization, metadata management, status updates, reconciliation results, review actions, and reporting.

### Background Processing

Long-running tasks should run outside the request/response path. This includes transcription, LLM extraction, payment matching, and reconciliation jobs.

### Local AI Components

The system should use local transcription and local LLM extraction. The local LLM should return structured agreement data that the backend validates before using.

### Storage and Data

The system should keep customer data, call recordings, transcripts, extracted agreement details, payment records, reconciliation cases, review actions, and audit history. At this stage, storage is described conceptually rather than as exact tables or schemas.

## Workflow

1. User uploads a call recording or transcript.
2. Backend stores file metadata and creates a call record.
3. Background job transcribes audio if needed.
4. Local LLM extracts payment agreement details from the transcript.
5. Backend validates the extracted structured data.
6. Payment matcher searches for candidate actual payments.
7. Reconciliation engine applies deterministic rules.
8. Clear cases receive a final reconciliation status.
9. Unclear, risky, mismatched, or ambiguous cases go to the human review queue.
10. Reviewer action updates the case and writes audit history.

## Processing Status Lifecycle

The high-level lifecycle is:

```text
UPLOADED
-> TRANSCRIBING
-> TRANSCRIBED
-> EXTRACTING
-> EXTRACTED
-> RECONCILING
-> RECONCILED | NEEDS_REVIEW | FAILED
```

## Reconciliation Outcomes

The system should support these business outcomes:

- RECONCILED
- UNDERPAID
- OVERPAID
- PARTIAL_PAYMENT
- PAYMENT_NOT_FOUND
- MULTIPLE_MATCHES_FOUND
- NEEDS_REVIEW
- FAILED

## Review Behavior

Cases should be routed to review when:

- The LLM extraction confidence is below threshold.
- The transcript evidence is unclear.
- No matching payment is found.
- Multiple candidate payments are ambiguous.
- The amount paid differs from the agreed amount.
- The system cannot safely classify the case.

Reviewers should see the call, transcript, extracted evidence, candidate payment details, reconciliation reason, and audit history.

## Operational Principles

- Upload requests should return quickly.
- Heavy work should run in background workers.
- Worker concurrency should be conservative for a limited server.
- Reprocessing should be safe and auditable.
- Every financial result should be explainable.
- Raw LLM output can be retained for debugging, but validated fields drive business logic.
- Human review should catch exceptions instead of allowing silent incorrect decisions.

## Recommended Technology Direction

The source spec recommends:

- React + Vite for the frontend.
- FastAPI and Pydantic for the backend API.
- PostgreSQL for persistent data.
- SQLAlchemy and Alembic when database implementation begins.
- Celery and Redis for background jobs.
- Ollama for local LLM runtime.
- faster-whisper or whisper.cpp for transcription.
- Docker Compose and Nginx for a single-server deployment.

These are directional choices for planning. Exact implementation details should be decided when frontend and backend scaffolding begins.

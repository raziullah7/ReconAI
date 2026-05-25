# ReconAI Documentation

ReconAI is a customer payment reconciliation agent for finance and operations
teams. It compares what a customer agreed to pay during a call with what the
customer actually paid, then highlights mismatches, missing payments, and cases
that need human review.


## Core Principle

Local AI reads the transcript and extracts the payment agreement. The backend
validates that output, deterministic rules decide the reconciliation result, and
humans review unclear or risky cases.

## Monorepo Layout

The project is planned as a monorepo with three top-level sections:

- `docs/`: product, architecture, and planning documentation.
- `frontend/`: planned React/Vite frontend application.
- `backend/`: planned FastAPI backend API, workers, and service code.

## Documentation Index

- [Implementation Plan](PLAN.md)
- [Functional Requirements](product/functional-requirements.md)
- [Scope and Acceptance Criteria](product/scope.md)
- [High-Level Design](architecture/high-level-design.md)

## Documentation Level

These docs are intentionally at the initial design level. They describe what
the system should do, who uses it, and how the main workflow behaves.

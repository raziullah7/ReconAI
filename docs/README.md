# Project Documentation

This folder contains the working documentation for the Customer Payment Reconciliation Agent.

Source spec: `/home/dell/Downloads/customer_payment_reconciliation_agent_dark.pdf`

Source version: 1.1, dated 21 May 2026

## Monorepo Layout

The project is planned as a monorepo with three top-level sections:

- `docs/`: product, architecture, and planning documentation.
- `frontend/`: future frontend application.
- `backend/`: future backend API, workers, and service code.

## Documentation Index

- [Functional Requirements](product/functional-requirements.md)
- [Scope and Acceptance Criteria](product/scope.md)
- [High-Level Design](architecture/high-level-design.md)

## Documentation Level

These docs are intentionally at the initial design level. They describe what the system should do, who uses it, and how the main workflow behaves. They do not lock exact database tables, ORM models, migrations, indexes, or implementation-level schemas.

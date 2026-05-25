# ReconAI Documentation

ReconAI is a customer payment reconciliation agent for finance and operations teams. It compares what a customer agreed to pay during a call with what the customer actually paid, then highlights mismatches, missing payments, and cases that need human review.

Source PRD: `/home/dell/Downloads/customer_payment_reconciliation_agent_dark.pdf`

Source version: 1.1

## Core Principle

Local AI reads the transcript and extracts the payment agreement. The backend validates that output, deterministic rules decide the reconciliation result, and humans review unclear or risky cases.

## Documentation Index

- [Customer Payment Reconciliation Agent](customer_payment_reconciliation_agent/)
- [Product Requirements](customer_payment_reconciliation_agent/PRD.md)
- [BDD Examples](customer_payment_reconciliation_agent/BDD.md)
- [Architecture](customer_payment_reconciliation_agent/ARCH.md)
- [Data Models](customer_payment_reconciliation_agent/MODELS.md)
- [Configuration](customer_payment_reconciliation_agent/CONFIG.md)
- [Technical Specification](customer_payment_reconciliation_agent/SPEC.md)
- [Implementation Plan](customer_payment_reconciliation_agent/PLAN.md)
- [API Contracts](customer_payment_reconciliation_agent/API.md)
- [Typed Interfaces](customer_payment_reconciliation_agent/DEFINITIONS.md)
- [UI and UX Flows](customer_payment_reconciliation_agent/UI_UX.md)
- [Testing Strategy](customer_payment_reconciliation_agent/TESTING.md)
- [Specification Review](customer_payment_reconciliation_agent/SPEC-REVIEW.md)

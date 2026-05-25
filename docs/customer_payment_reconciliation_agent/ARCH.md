# ARCH.md

## 1. Overview

**Feature Name**: Customer Payment Reconciliation Agent  
**Status**: Draft  
**Author**: Codex using `.agents/agents/architect.md`  
**Date**: intentionally omitted  
**PRD**: [PRD.md](PRD.md)

ReconAI is an event-driven reconciliation pipeline that uses local AI for extraction, deterministic backend rules for financial outcomes, and human review for exceptions; product purpose is owned by [PRD.md](PRD.md#1-introduction).

## 2. PRD Context and Requirement Traceability

Architecture is driven by PRD requirements `FR-01` through `FR-15`, non-functional requirements `NFR-01` through `NFR-09`, reconciliation rules `RR-01` through `RR-08`, and product constraints `PC-01` through `PC-06` in [PRD.md](PRD.md).

| Driver | Architecture Response |
| --- | --- |
| `FR-01`, `NFR-04` | Role-aware API and UI boundaries with explicit authentication and authorization. |
| `FR-03` through `FR-06`, `NFR-03`, `NFR-06` | Asynchronous pipeline for upload, transcription, extraction, and validation. |
| `FR-07` through `FR-09`, `RR-01` through `RR-08` | Payment data management plus deterministic matching and reconciliation components. |
| `FR-10`, `FR-11`, `NFR-02` | Review queue and audit subsystem are first-class architecture components. |
| `FR-12`, `FR-13` | Dashboard, filters, and export surfaces read from reconciliation case projections. |
| `FR-14`, `NFR-05` | Reprocessing creates new attempts while preserving historical auditability. |
| `PC-01`, `PC-05`, `PC-06` | Local AI runtime and conservative worker concurrency on Docker Compose. |

## 3. Architectural Goals and Non-Goals

### Goals

- AG-01: Keep LLM output advisory and validated before any business rule uses it (`FR-06`, `NFR-01`).
- AG-02: Isolate long-running transcription, extraction, matching, and reconciliation work from request/response paths (`NFR-06`).
- AG-03: Preserve auditability for every financial and review decision (`FR-11`, `NFR-02`).
- AG-04: Keep the design single-server friendly while allowing later scale-out (`NFR-03`, `NFR-07`).
- AG-05: Make tenant boundaries explicit in data and service interfaces while allowing single-company operation (`FR-02`, `PC-05`).

### Non-Goals

- Bank statement, payment gateway, CRM, call-center, customer notification, advanced analytics, and SaaS billing integrations are optional add-ons per [PRD.md](PRD.md#7-non-goals).
- Architecture does not lock endpoint payloads, typed function signatures, field-level schemas, or test matrices; those belong to downstream reference files.

## 4. System Context

```text
Users
  -> React/Vite frontend
  -> FastAPI backend API
  -> PostgreSQL application data
  -> Redis/Celery background jobs
  -> local transcription service
  -> Ollama local LLM runtime
  -> object/local storage for recordings
```

The core system is a monorepo with `frontend/`, `backend/`, and `docs/`. The current repo has placeholder app folders, so implementation should create the runtime structure during later phases.

## 5. High-Level Design

- Frontend application: role-aware workflows for intake, customers, payments, dashboard, case detail, review queue, audit history, and exports.
- Backend API: authentication, authorization, validation, metadata persistence, case reads, payment management, review actions, exports, and job orchestration.
- Processing orchestrator: creates idempotent Celery jobs and advances status transitions.
- Transcription worker: converts audio to transcript and records model metadata.
- Extraction worker: calls local LLM, captures raw output, validates structured extraction, and flags risky output.
- Payment matcher: searches candidate payments by customer, phone, invoice, currency, payment date range, and amount similarity.
- Reconciliation engine: applies deterministic rules from the PRD and creates explainable results.
- Review service: supports manual review actions and recalculation after payment linking.
- Audit service: records system and user actions with tenant, user, entity, action, and before/after context.

## 6. Data Architecture

See [MODELS.md](MODELS.md) for data architecture.

## 7. Dependencies

- Upstream: source PRD, local AI model availability, transcription runtime availability, authentication provider implementation.
- Downstream: API contracts, typed interfaces, UI flows, testing strategy, phase implementation plans.
- External/local services: PostgreSQL, Redis, Celery, Ollama, faster-whisper or whisper.cpp, Docker Compose, Nginx, local or object storage.

## 8. SaaS Pre-Flight Decisions

| Concern | Decision |
| --- | --- |
| Tenancy model | Tenant-ready pooled model with shared PostgreSQL schema and `tenant_id` on tenant-scoped entities; single-company operation may use one default tenant. |
| Tenant context propagation | Resolve tenant at request boundary and pass `TenantContext` through services, repositories, workers, and audit writes. |
| Authentication | Bearer JWT or session cookie can back user identity; API contracts standardize Bearer JWT for planning. |
| Authorization | RBAC by role plus resource ownership checks for tenant-scoped records. |
| Events | Use Celery jobs for internal async work; use an outbox table for audit-relevant job events when events need durability. |
| Billing lifecycle | N/A for first delivery; full SaaS billing is optional. |
| Observability | Structured logs and metrics include tenant, user, request, job, model, status, and outcome fields. |
| Compliance | Treat customer, call, transcript, and payment data as sensitive; GDPR-like erasure and audit-retention tradeoffs are captured in MODELS. |
| Data residency | Single-region deployment for first delivery; regional routing is deferred. |
| Disaster recovery | Back up PostgreSQL and storage volumes; exact RPO/RTO values are implementation policy decisions. |
| Zero-downtime migration | Use expand/contract migrations once production data exists. |
| Rate limits and quotas | Per-tenant and per-user API rate limits; worker concurrency limited globally for local AI. |
| Background jobs and idempotency | Every processing job has an idempotency key, retry policy, and failure status. |
| Webhooks and integrations | Outgoing webhooks are deferred; future integrations must use signed, replay-protected events. |

## 9. Security Considerations

- Enforce authentication on every non-public endpoint.
- Enforce role authorization for admin, finance, reviewer, and manager actions.
- Prevent cross-tenant access through tenant-scoped repositories and row-level policy when implemented.
- Protect recordings, transcripts, customer data, payment data, and raw LLM output at rest and in transit.
- Validate all LLM output and CSV import data before persistence or business-rule use.

## 10. Performance Considerations

- Upload and transcript submission endpoints return quickly and enqueue background work.
- Celery worker concurrency starts conservatively for local transcription and LLM inference.
- Large dashboard and case list reads use tenant-prefixed indexes and pagination.
- Export generation may run async when result sets are large.

## 11. Observability

- Emit structured logs for upload, transcription, extraction, validation, matching, reconciliation, review, reprocessing, and export events.
- Track metrics for processing duration, queue depth, failure counts, extraction confidence distribution, reconciliation status counts, review backlog, and worker resource pressure.
- Use request IDs and job IDs for correlation from UI action to background processing and audit records.

## 12. Migration Strategy

Implementation begins from an empty app scaffold, so migration risk is mostly schema evolution. Use additive migrations, backfills for derived fields, and no destructive migrations until data is backed up and verified.

See [CONFIG.md](CONFIG.md) for feature flags and configuration.

## 13. Alternatives Considered

- Hosted AI services: rejected for the base design because the PRD requires local transcription and local LLM extraction.
- Synchronous processing: rejected because transcription and extraction are long-running and resource-heavy.
- LLM-decided status: rejected because the PRD requires deterministic backend reconciliation.
- Fully packaged SaaS billing from day one: deferred because the PRD treats multi-tenant SaaS packaging as an optional add-on.

## 14. Open Questions

- OQ-ARCH-01: Confirm whether the first deployment uses a single default tenant or exposes tenant management in the UI.
- OQ-ARCH-02: Confirm the exact extraction confidence threshold for `NEEDS_REVIEW`.
- OQ-ARCH-03: Confirm local LLM model choice for the target server.
- OQ-ARCH-04: Confirm whether notifications are included or deferred.

## 15. References

- [PRD.md](PRD.md)
- [BDD.md](BDD.md)
- [MODELS.md](MODELS.md)
- [CONFIG.md](CONFIG.md)

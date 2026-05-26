# PHASE-M1.1-CONTRACT-DOCS-AND-REVIEW.md

## Executive Summary

This phase freezes the Base API contract before any backend implementation
starts. It verifies the owner docs agree on the LLM-shaped extraction input,
actual payment input, stored case shape, service interfaces, test scope, and the
Gate A confidence threshold.

Expected outcome: `@phase-coder` has no product or contract decisions to make
before database, validation, or API work begins.

Assumptions:

- The current backend remains a FastAPI health-check shell, verified by a
  read-only spot-check against the app shell files.
- Milestone 1 remains local and non-tenantized.
- The confidence threshold is `0.80`, as owned by [../CONFIG.md](../CONFIG.md).

P_bottom_up: 0 production LOC because this is a docs-only phase.
T_bottom_up: 0 test LOC because verification uses review and docs checks only.

## Execution Plan

### Red

No executable Red tests are added because this phase edits planning documents
only. The Red checks are document-review failures that must be present before
Green resolves them:

- `docs_check_base_api_contract_is_named`
  - Summary: Confirms [../API.md](../API.md) names
    `AgreementExtractionInputV1`, `ActualPaymentInputV1`, create/list/detail
    Base API responses, and Milestone 1 endpoint paths.
  - Mocks: None.
  - Assertions: The Base API section exists and does not require auth, tenants,
    workers, Redis, Ollama, or frontend behavior.

- `docs_check_gate_a_threshold_is_resolved`
  - Summary: Confirms [../CONFIG.md](../CONFIG.md), [../SPEC.md](../SPEC.md),
    and [../TESTING.md](../TESTING.md) agree that confidence below `0.80`
    routes to `NEEDS_REVIEW`.
  - Mocks: None.
  - Assertions: The threshold appears in the canonical config owner and is
    referenced consistently by the spec and tests.

- `docs_check_milestone_one_scope_is_small`
  - Summary: Confirms [../PLAN.md](../PLAN.md) keeps Milestone 1 focused on the
    Base API path.
  - Mocks: None.
  - Assertions: Auth, tenants, idempotency records, cursor pagination, Redis,
    Ollama, workers, frontend, CSV import, and payment-ledger matching are
    explicitly out of scope.

### Green

- Verify [../API.md](../API.md) owns the Base API payload and endpoint contract.
- Verify [../MODELS.md](../MODELS.md) owns the `reconciliation_cases` storage
  subset and snapshots.
- Verify [../DEFINITIONS.md](../DEFINITIONS.md) owns validation, decision,
  repository, and service interface names.
- Verify [../CONFIG.md](../CONFIG.md) owns the `0.80` confidence threshold.
- Verify [../SPEC.md](../SPEC.md) states the no-LLM Base API flow.
- Verify [../TESTING.md](../TESTING.md) owns Milestone 1 validation, decision,
  persistence, and API test scope.

Pseudo code for the docs check:

```text
for required_doc in [API, MODELS, DEFINITIONS, CONFIG, SPEC, TESTING]:
    read required_doc
    confirm the Milestone 1 section exists
    confirm no future service is promoted into Milestone 1
    record review result in the phase review document
```

### Refactor

- Keep detailed phase execution in this folder and keep [../PLAN.md](../PLAN.md)
  as the milestone index.
- Replace stale root phase-plan links with this milestone folder.

## Setup and Testing in Local Dev

Settings and configuration: no runtime setting is required for this docs-only
phase. `DATABASE_URL` remains the only setting needed by the current app shell.

Environment variables: none for docs checks.

Local commands:

```bash
rg -n "AgreementExtractionInputV1|ActualPaymentInputV1|/v1/reconciliation-cases" \
  docs/customer_payment_reconciliation_agent/API.md
rg -n "AgreementExtractionInputV1|ActualPaymentInputV1" \
  docs/customer_payment_reconciliation_agent/MODELS.md \
  docs/customer_payment_reconciliation_agent/DEFINITIONS.md
rg -n "EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD|0\\.80|NEEDS_REVIEW" \
  docs/customer_payment_reconciliation_agent/CONFIG.md \
  docs/customer_payment_reconciliation_agent/SPEC.md \
  docs/customer_payment_reconciliation_agent/TESTING.md
rg -n "Auth, tenant context|Redis, Ollama|workers, frontend|remain out of" \
  docs/customer_payment_reconciliation_agent/PLAN.md
rg -n "only foundation routes|/health|FastAPI" \
  backend/app/main.py backend/README.md
```

Multi-tenant coverage: N/A because Milestone 1 is intentionally non-tenantized.

Tenant-aware test cases: N/A because tenant behavior is deferred.

Expected outcome: the docs name the Base API contract, the threshold is
resolved, and future-scope services remain deferred.

## What You Can Run After This Phase

Run the local commands above from the repository root. They should prove that
the Base API contract and Gate A threshold live in owner docs, future services
remain deferred by [../PLAN.md](../PLAN.md), and the backend is still only the
foundation app shell.

## Rollout Plan and Testing in QA and Staging

QA and staging rollout: N/A because this phase changes planning documents only.

Expected outcome: reviewers can read the same contract docs and confirm there
is no environment-specific behavior to deploy.

Configuration changes: none.

Data setup or migration steps: none.

## Rollout to Production

Production rollout: N/A because this phase changes planning documents only.

Expected outcome: no runtime deployment occurs.

Configuration changes: none.

Data setup or migration steps: none.

## SaaS Pre-Flight Disposition

| # | Item | Disposition | Evidence / Steps |
|---|------|-------------|------------------|
| 1 | Local dev multi-tenant coverage | N/A | Milestone 1 is non-tenantized by [../PLAN.md](../PLAN.md). |
| 2 | Tenant-aware test cases | N/A | Tenant behavior is deferred. |
| 3 | Per-environment feature flag state | N/A | No feature flag ships in this docs phase. |
| 4 | Per-tenant production canary | N/A | No production rollout occurs. |
| 5 | Observability verification | N/A | No runtime behavior changes. |
| 6 | Audit log verification | N/A | Audit logging is deferred. |
| 7 | Rate limit / quota verification | N/A | Rate limits are deferred. |
| 8 | Webhook delivery verification | N/A | Webhooks are not in scope. |
| 9 | Rollback addresses in-flight tenant data | N/A | No tenant data or migration exists in this phase. |
| 10 | Kill switch drill without redeploy | N/A | No runtime switch ships in this phase. |

## Summary of Changes

- [../API.md](../API.md) (modify):
  Freezes L1 Base API contract ownership.
- [../MODELS.md](../MODELS.md) (modify):
  Freezes L2 storage ownership for the Base API subset.
- [../DEFINITIONS.md](../DEFINITIONS.md) (modify):
  Freezes L3 interface ownership for services, repositories, and functions.
- [../CONFIG.md](../CONFIG.md) (modify):
  Freezes L4 threshold ownership for Gate A.
- [../SPEC.md](../SPEC.md) (modify):
  Freezes L5 no-LLM Base API flow ownership.
- [../TESTING.md](../TESTING.md) (modify):
  Freezes L6 Milestone 1 test-scope ownership.

## Code Generation Instructions

See `planning-conventions` -> Code Generation Instructions. Lint, types,
docstrings, commits, and change-summary rules apply unchanged. This phase has
no production code generation.

<details>
<summary>Coverage Ledger</summary>

| ID | Category | Source | Pushed to (owner file) | Status |
|----|----------|--------|------------------------|--------|
| L1 | inherited | [../PLAN.md](../PLAN.md#milestone-1-base-api-development) | [../API.md](../API.md#base-api-milestone-contract) | resolved |
| L2 | inherited | [../PLAN.md](../PLAN.md#milestone-1-base-api-development) owner-doc freeze row | [../MODELS.md](../MODELS.md#base-api-persistence-model) | resolved |
| L3 | inherited | [../PLAN.md](../PLAN.md#milestone-1-base-api-development) owner-doc freeze row | [../DEFINITIONS.md](../DEFINITIONS.md#base-api-interfaces) | resolved |
| L4 | new-durable | Gate A threshold | [../CONFIG.md](../CONFIG.md#extraction_review_confidence_threshold) | pushed |
| L5 | inherited | [../SPEC.md](../SPEC.md#milestone-1-base-api-no-llm-flow) | [../SPEC.md](../SPEC.md#milestone-1-base-api-no-llm-flow) | resolved |
| L6 | inherited | [../TESTING.md](../TESTING.md#milestone-1-base-api-tests) | [../TESTING.md](../TESTING.md#milestone-1-base-api-tests) | resolved |
| L7 | assumption | Current backend is app shell only | [../../../backend/app/main.py](../../../backend/app/main.py) | verified by read-only spot-check |

</details>

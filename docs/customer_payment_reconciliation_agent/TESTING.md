# TESTING.md

## Unit Tests

- `validate_extraction`: valid extraction, missing amount, invalid amount, unsupported currency, low confidence, missing evidence.
- `match_candidate_payments`: customer match, phone match, invoice match, currency mismatch, amount similarity, no candidates, ambiguous candidates.
- `decide_reconciliation`: covers `RECONCILED`, `UNDERPAID`, `OVERPAID`, `PARTIAL_PAYMENT`, `PAYMENT_NOT_FOUND`, `MULTIPLE_MATCHES_FOUND`, `NEEDS_REVIEW`, and `FAILED`.
- `recalculate_case_after_review`: link, unlink, edit amount, reject, approve, stale version conflict.

## Integration Tests

- Intake creates call record, audit log, and processing attempt in one tenant.
- Worker transition updates call status and attempt status safely.
- Extraction persists raw output and validated fields but reconciliation reads validated fields only.
- CSV import accepts valid rows, rejects invalid rows, and returns row-level errors.
- Review action links payment, recalculates case, and appends audit log.

## E2E Tests

- Auth -> tenant context -> upload call -> transcript/extraction -> matching -> reconciled case -> audit log.
- Auth -> tenant context -> no payment found -> review queue -> manual payment link -> recalculated result -> audit log.
- Auth -> tenant context -> CSV import -> payment candidate search -> case list filter -> export.

## BDD Scenario Mapping

| BDD Tag | Business Rule | Test Level | Automation Owner | Notes |
| --- | --- | --- | --- | --- |
| `@bdd-001` | Intake creates traceable processing case | E2E | backend + frontend | Upload/transcript intake. |
| `@bdd-002` | LLM extraction validated before use | integration | backend | Raw vs validated fields. |
| `@bdd-003` | Payment records available for matching | integration | backend | Manual payment create. |
| `@bdd-004` | Exact match reconciles | unit + E2E | backend | Rule and full flow. |
| `@bdd-005` | Amount differences classify | unit | backend | Scenario outline maps to table tests. |
| `@bdd-006` | Unsafe outcomes route safely | unit + integration | backend | Low confidence, no payment, multiple matches. |
| `@bdd-007` | Reviewer resolves risky cases | E2E | backend + frontend | Manual link and note. |
| `@bdd-008` | Audit trail visible | E2E | backend + frontend | Ordered action history. |
| `@bdd-009` | Filter and export | E2E | backend + frontend | Export respects filters. |
| `@bdd-010` | Reprocessing preserves history | integration + E2E | backend | Prior extraction remains traceable. |

## Tenant Isolation Tests

For every endpoint, attempt access using tenant A credentials and tenant B IDs. Expected result is 403 or 404 without leaking tenant B data. Include call, transcript, payment, case, audit, export, and processing attempt resources.

## Permission Matrix Tests

| Operation | Admin | Finance User | Reviewer | Manager |
| --- | --- | --- | --- | --- |
| Manage users/config | allow | deny | deny | deny |
| Create customer/payment | allow | allow | deny | deny |
| Upload call/transcript | allow | allow | deny | deny |
| View dashboard/cases | allow | allow | allow | allow |
| Review action finalize | allow | policy-dependent | allow | deny |
| Reprocess call | allow | deny | allow | deny |
| Export results | allow | deny | deny | allow |

## Security Tests

- IDOR tests for every tenant-scoped resource ID.
- SQL injection tests for filters and CSV import values.
- Auth bypass tests for missing, expired, and malformed tokens.
- File upload tests for invalid type, oversize file, unsafe filename, and storage path traversal.
- Raw LLM output display tests for escaping and redaction.

## Idempotency Tests

- Duplicate idempotency key with identical payload returns identical response and no extra side effect.
- Duplicate idempotency key with different payload returns `IdempotencyConflict`.
- Concurrent duplicate processing jobs commit only one final state transition.

## Rate Limit Tests

- Bucket exhaustion returns 429 with retry and limit headers.
- Tenant A exhausting a bucket does not affect tenant B.
- Worker queue pressure does not bypass API rate limits.

## Plan-Tier / Feature-Flag Tests

- Disabled processing flag prevents new jobs but keeps existing records readable.
- Disabled exports flag hides export UI and rejects export endpoint with `FeatureNotEnabled`.
- Notifications flag disabled results in no notification side effects.

## Contract Tests

Use JSON-schema provider verification for API response envelopes, endpoint payloads, and export formats. Consumer-driven contracts may be added when external integrations are introduced.

## Performance and Load Tests

- Upload endpoint returns quickly after queue handoff.
- Worker concurrency remains bounded under multiple queued calls.
- Dashboard and case list p95 latency remain acceptable under seeded tenant data.
- Noisy-neighbor test ensures one tenant's queued jobs do not expose or corrupt another tenant's data.

## Edge Cases

- Transcription timeout.
- LLM runtime unavailable.
- Invalid LLM JSON.
- Duplicate payment import row.
- Multiple candidate payments with same confidence.
- Payment linked after `PAYMENT_NOT_FOUND` case creation.
- Reprocessing while previous job is running.
- Export requested with empty result set.

## Test Data Strategy

Use per-tenant fixture factories. No shared mutable state across tenants. Integration tests isolate data through transaction rollback or database reset. Test recordings and transcripts should use small synthetic files with no real customer PII.

## Tooling

- Backend unit/integration: pytest.
- Frontend component/E2E: Vitest and Playwright after frontend scaffold exists.
- Contract: JSON schema verification.
- Load: k6 or Locust after API stabilizes.
- CI: run unit and contract tests on pull request; integration/E2E on merge or release candidate.

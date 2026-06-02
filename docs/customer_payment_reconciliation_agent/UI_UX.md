# UI_UX.md

> Status: This is a target design document. It does not mean every item is implemented today. Use [README.md](README.md) and [PLAN.md](PLAN.md) for the current implementation phase.


## Milestone 2 Base Frontend Slice

Milestone 2 implements only the local Base API frontend path: clean shell, local
backend connectivity, case list, case detail, then create-and-result. Login,
tenants, dashboards, payment ledger, review workflow, exports, and worker
status screens remain target UI only.

The first data screens must view stored cases before the create form is added,
so users can understand existing backend output before submitting new data.
The M2 submit form uses major-unit amount entry and converts to two-decimal
minor units for the Base API until tenant currency metadata exists.

Starting in M2.3, Milestone 2 uses TanStack Router file routes for the list,
detail, and submit screens. Route data screens should use route loaders plus
route-level loading and error states instead of burying initial data loading in
`useEffect`. Generic UI primitives come from HeroUI, so ReconAI should avoid a
custom `ui-kit`; route-specific extracted pieces belong beside their route in a
`-components` folder only when the route component becomes hard to read.

## User Journeys

- Finance intake: choose tenant, select/create customer, upload recording or submit transcript, see processing status.
- Payment management: add manual payment, import CSV, review row errors, search payments.
- Case review: open review queue, inspect transcript/evidence/candidates/audit, approve/reject/edit/link/unlink/add note.
- Manager monitoring: view dashboard, filter cases, export results.
- Admin operations: manage users, re-run failed transcription/extraction, inspect operational failures.

## Screen Inventory

- Login: authenticates user and selects tenant context when needed.
- Dashboard: status totals, review backlog, failures, filters, and export entry point.
- Customers: customer list, search, create/edit form.
- Payments: payment list, manual create form, CSV import flow, row-error report.
- Call Intake: upload/transcript submission and metadata form.
- Processing Detail: call status, transcript, extraction, current case summary.
- Case List: filterable case table with status and review indicators.
- Case Detail: transcript evidence, extracted agreement, candidate payments, reason, audit history.
- Review Queue: prioritized cases needing manual action.
- Audit History: chronological actions for a case.
- Admin Operations: users, reprocessing controls, failure visibility.

## Interaction Flows

- Tenant switcher changes active tenant context and reloads tenant-scoped lists; unsaved forms warn before switching.
- Permission-gated screens are hidden from users without any access; direct navigation shows a 403 state.
- Mutating review actions require confirmation when they affect financial status or unlink payments.
- Reprocessing asks for a reason and shows a new processing attempt while preserving prior evidence.

## State Inventory Per Screen

Every screen must define loading, empty, success, validation error, network error, 401, 403, 404, rate-limited, disabled, and plan/feature-gated states. Specific expectations:

- Dashboard empty state explains that no reconciliation cases exist yet.
- Review Queue empty state confirms no cases currently require review.
- CSV import error state separates file-level errors from row-level errors.
- Case Detail disabled states explain why actions are unavailable, such as final status, stale version, missing permission, or processing still running.

## Form Validation and Inline Feedback

- Amounts are entered in major units but displayed and persisted as minor-unit values.
- Currency is required for agreements and payments.
- Customer or sufficient customer-identifying metadata is required for intake.
- Review notes are required for reject, edit amount, link, unlink, and reprocessing actions.
- Server errors use the API error envelope from [API.md](API.md#error-envelope).

## Responsive and Adaptive Behavior

- Desktop: dashboard, case lists, and detail views use dense tables and split detail panels.
- Tablet: filters collapse into drawers; case evidence and payment candidates stack.
- Mobile: primary workflows remain usable, but large exports and CSV imports may direct users to desktop-friendly guidance.
- Touch targets meet accessibility sizing; hover-only actions must have visible alternatives.

## Accessibility Requirements

Target WCAG 2.1 AA. Requirements include keyboard navigation, visible focus, semantic headings, labeled form fields, ARIA status announcements for processing changes, sufficient color contrast, non-color-only status indicators, and reduced-motion handling for progress animations.

## Internationalization

Dates, numbers, money, and currencies are formatted by tenant locale. Currency codes remain visible in finance-critical displays. Right-to-left layout support is deferred unless a tenant locale requires it.

## Audit-Relevant Interactions

The UI must visually distinguish actions that create audit entries: upload, transcript submission, extraction/reprocessing, payment create/import, reconciliation, approve, reject, edit amount, link payment, unlink payment, export, and user/admin changes.

## Content and Messaging Inventory

- Empty states: no customers, no payments, no calls, no review cases, no audit entries.
- Error messages: validation failed, unauthorized, forbidden, not found, rate limited, processing failed, extraction validation failed, export failed.
- Confirmation messages: reject case, edit agreed amount, link payment, unlink payment, reprocess call, export data.

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

Milestone 2 follows the Codex Frontend Design guidance for operational tools:
the first screen must be useful, quiet, scannable, and workflow-shaped. It must
not feel like a marketing landing page, generic Vite starter, dashboard mockup,
or decorative placeholder.

### Milestone 2 Design Principles

- Use an operational workspace with restrained navigation, compact headings,
  clear status summaries, and direct access to the current Base API workflow.
- Keep the visual language finance-focused: neutral surfaces, readable
  contrast, status labels, amount alignment, timestamp clarity, and enough
  spacing to scan without making the page feel sparse.
- Avoid decorative blobs, oversized hero treatments, generic starter copy,
  mock-only case data, and one-note palettes.
- Keep dimensions stable for the app frame, list rows, detail panels, status
  chips, buttons, and form controls so loading text, errors, and dynamic values
  do not shift the layout.
- Use native semantic controls first: buttons for actions, labeled inputs for
  form values, checkboxes for boolean flags, selects for bounded options, and
  tables or structured rows for case summaries.
- Every data screen must include loading, empty, success, error, and retry or
  recovery states that match the current backend contract.
- Text must fit on mobile and desktop without overlapping controls or hiding
  finance-critical values.

### Milestone 2 Screen Progression

- M2.1 Frontend Scaffold Cleanup: show a minimal ReconAI workspace shell with
  no backend calls, no mock cases, no starter branding, and no instructional
  template copy. The shell should establish the app frame that later screens can
  reuse.
- M2.2 Backend CORS And Frontend Config: keep the UI visually unchanged except
  for any small non-data connectivity status that helps local verification. Do
  not introduce case list, detail, or submit UI in this phase.
- M2.3 Case List: replace the static workspace center with stored case
  summaries from `ReconciliationCaseListResponseV1`. Show status, references,
  agreed/paid/difference amounts, currency, review flag, and timestamps. Empty
  state means the backend returned no cases, not that sample data should appear.
- M2.4 Case Detail: keep the list visible while showing
  `ReconciliationCaseResponseV1` detail for the selected case. The detail view
  should separate extraction, actual payment, backend decision, and timestamps
  into clearly labeled sections.
- M2.5 Reconciliation Submit And Result: add the create form only after list and
  detail exist. The form builds `ReconciliationCaseCreateRequestV1`, submits to
  the backend, and displays the backend-owned decision result without letting
  the frontend invent reconciliation status.

### Milestone 2 Layout and Interaction Rules

- Desktop: use a dense workspace layout. Case list and case detail may sit side
  by side once detail exists; the submit flow can use a form column plus a result
  or context panel when space allows.
- Tablet: stack major regions while keeping the selected case and action area
  easy to find.
- Mobile: stack shell, list, detail, and form sections in one readable column.
  Keep buttons and inputs full-width when needed so labels and values do not
  collide.
- Case list rows must make the primary identifier, status, amount difference,
  and review flag visible without opening detail.
- Status must never rely on color alone; pair color with text such as
  `RECONCILED`, `NEEDS_REVIEW`, or `UNDERPAID`.
- Use inline loading and error regions near the data they affect. List errors
  should not erase an already loaded detail panel unless the user explicitly
  reloads the whole workflow.
- Retry actions must re-run the relevant request without requiring a full page
  refresh.

### Milestone 2 Forms and Feedback

- Amount inputs are entered in major units for humans and converted to
  two-decimal minor-unit integers before the Base API request.
- Currency fields stay visible wherever money appears; do not rely on a hidden
  default currency in Milestone 2.
- Required fields must be clearly labeled before submission. Backend validation
  errors must use the API error envelope wording where available.
- Submit failure must preserve entered form values. Submit success must show the
  returned decision status, reason, amounts, confidence, and review flag.
- Use `aria-live` or an equivalent semantic status region for load, submit,
  success, and error messages.

### Milestone 2 Manual Verification

Milestone 2 does not add frontend tests, frontend test files, frontend test
scripts, Vitest, Testing Library, jsdom, Playwright, or Cypress. Frontend
verification uses:

- `npm run build`
- `npm run lint`
- Manual browser checks against the local FastAPI backend

Manual checks must cover the case list empty/success/error states, detail
success/error states, submit success, backend validation failure, network
failure, keyboard focus visibility, mobile stacking, and text fit.

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

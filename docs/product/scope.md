# Scope

## Current Goal

Build a first version of a customer payment reconciliation system that can compare what was agreed in a customer call with what was actually paid.

At this stage, this document is only for initial product/design discussion. It should guide the shape of the project without locking detailed implementation decisions.

## In Scope For Initial Design

- Upload or provide a customer call recording or transcript.
- Extract agreed payment details from the transcript.
- Add or import actual payment records.
- Match payment records against the extracted agreement.
- Show the reconciliation status.
- Send unclear or risky cases to human review.
- Keep enough audit history to explain what happened.

## Not In Scope Yet

- Bank statement integrations.
- Payment gateway integrations.
- CRM or call-center integrations.
- Customer notifications by SMS, WhatsApp, or email.
- Advanced analytics and executive dashboards.
- SaaS billing or full multi-tenant packaging.

## Success Criteria

The first version is successful if a finance user can trace a case from call or transcript to extracted agreement, payment match, reconciliation result, and review/audit history.

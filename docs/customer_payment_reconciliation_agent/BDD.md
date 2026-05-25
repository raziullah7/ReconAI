# BDD.md

**Feature**: customer_payment_reconciliation_agent
**Status**: Stakeholder Review Required
**Source**: [PRD.md](PRD.md)

## 1. Collaboration Context

These examples are evidence-bound candidates derived from the PRD. They require stakeholder review before they are treated as approved living documentation.

## 2. Feature Narrative

```gherkin
@customer-payment-reconciliation-agent
Feature: Customer payment reconciliation
  In order to reduce manual reconciliation work and identify mismatches
  As finance, review, management, and admin users
  I want the system to compare call-agreed payment amounts against actual payments and route exceptions to human review
```

## 3. Example Mapping and Traceability

| PRD ID | Business Rule | Concrete Example | Scenario Tag / Disposition | Coverage Status | Example Status | Evidence / Open Question |
| --- | --- | --- | --- | --- | --- | --- |
| FR-03, FR-04, FR-05 | Calls or transcripts enter the processing pipeline | A Finance User uploads a call and the system creates a processing case | `@bdd-001` | Covered | Candidate | PRD requires call upload, transcription, and transcript storage. |
| FR-06, NFR-01 | LLM extraction is validated before financial use | Extraction produces structured fields but backend validation controls whether it can proceed | `@bdd-002` | Covered | Candidate | PRD states LLM extracts only; backend validates. |
| FR-07 | Payment records are available for matching | A Finance User adds a manual payment record | `@bdd-003` | Covered | Candidate | PRD requires manual payment entry. |
| FR-08, FR-09, RR-05 | Exact matching amounts reconcile | Paid amount equals agreed amount | `@bdd-004` | Covered | Candidate | PRD rule defines `RECONCILED`. |
| RR-06, RR-07 | Differences produce underpaid or overpaid outcomes | Paid amount below or above agreed amount | `@bdd-005` | Covered | Candidate | PRD rules define `UNDERPAID` and `OVERPAID`. |
| RR-01, RR-02, RR-03 | Unclear matching conditions route to review or exception statuses | Low confidence, no payment, or multiple candidates | `@bdd-006` | Covered | Candidate | PRD requires safe exception handling. |
| FR-10 | Reviewers resolve risky cases | Reviewer links a payment and adds notes | `@bdd-007` | Covered | Candidate | PRD requires approve, reject, edit, link, notes. |
| FR-11 | Important actions are auditable | A user opens case history and sees upload through review actions | `@bdd-008` | Covered | Candidate | PRD requires full audit trail. |
| FR-12, FR-13 | Managers monitor and export results | Manager filters cases and exports results | `@bdd-009` | Covered | Candidate | PRD requires dashboard, filters, CSV/Excel export. |
| FR-14 | Reprocessing preserves history | Admin re-runs extraction and old result remains traceable | `@bdd-010` | Covered | Candidate | PRD requires reprocessing with audit history. |
| FR-15 | Notifications may be optional | Mismatch notifications | N/A unless included | N/A | N/A | PRD marks notifications conditional. |

## 4. Scenarios

```gherkin
Rule: Intake creates a traceable processing case

  @bdd-001 @fr-03 @fr-04 @fr-05 @smoke
  Scenario: Upload a customer call for reconciliation
    Given a Finance User has customer and call metadata
    When the user submits a call recording for reconciliation
    Then the system creates a call record with processing status
    And the system keeps transcript evidence available once transcription completes

Rule: LLM extraction never decides the financial result

  @bdd-002 @fr-06 @nfr-01 @smoke
  Scenario: Validate extracted payment agreement before reconciliation
    Given a transcript is available for a call
    When local AI extracts payment agreement details
    Then the backend validates the extracted fields
    And the validated fields become the only extraction data used by reconciliation rules

Rule: Actual payment records can be managed by finance users

  @bdd-003 @fr-07 @regression
  Scenario: Add a manual payment record for matching
    Given a Finance User has actual payment details for a customer
    When the user records the payment
    Then the payment is available as a candidate for reconciliation

Rule: Deterministic reconciliation produces explainable outcomes

  @bdd-004 @fr-08 @fr-09 @rr-05 @smoke
  Scenario: Reconcile an exact payment match
    Given a validated agreement amount exists for a call
    And a candidate payment has the same amount and currency
    When the reconciliation engine compares agreed and paid amounts
    Then the case status is RECONCILED
    And the case includes an explainable reason

  @bdd-005 @rr-06 @rr-07 @regression @boundary
  Scenario Outline: Classify amount differences
    Given a validated agreement amount exists for a call
    And a candidate payment amount is <relationship> the agreed amount
    When the reconciliation engine compares agreed and paid amounts
    Then the case status is <status>

    Examples:
      | relationship | status    |
      | below        | UNDERPAID |
      | above        | OVERPAID  |

  @bdd-006 @rr-01 @rr-02 @rr-03 @negative
  Scenario Outline: Route unsafe automatic outcomes
    Given a reconciliation case has <condition>
    When the system evaluates the case
    Then the case status is <status>

    Examples:
      | condition                       | status                 |
      | low extraction confidence       | NEEDS_REVIEW           |
      | no candidate payment            | PAYMENT_NOT_FOUND      |
      | ambiguous candidate payments    | MULTIPLE_MATCHES_FOUND |

Rule: Humans resolve risky or ambiguous cases

  @bdd-007 @fr-10 @regression
  Scenario: Reviewer manually links a payment to resolve a case
    Given a case requires human review
    And the reviewer finds the correct payment
    When the reviewer links the payment and adds a note
    Then the system recalculates the reconciliation result
    And the review action is saved in audit history

Rule: Audit and reporting make results explainable

  @bdd-008 @fr-11 @smoke
  Scenario: View the audit trail for a reconciliation case
    Given a case has upload, extraction, matching, and review activity
    When an authorized user opens the case history
    Then the system shows the recorded actions in order

  @bdd-009 @fr-12 @fr-13 @regression
  Scenario: Filter and export reconciliation results
    Given reconciliation cases exist with different statuses
    When a Manager filters results and requests an export
    Then the export contains the filtered reconciliation cases

Rule: Reprocessing preserves traceability

  @bdd-010 @fr-14 @regression
  Scenario: Re-run extraction without losing prior history
    Given an extraction result appears incorrect
    When an Admin re-runs extraction for the call
    Then the new extraction is stored as the current result
    And the prior result remains traceable through audit history
```

## 5. Automation Handoff

Test automation strategy belongs in [TESTING.md](TESTING.md). That file should map E2E and behavior-level tests to `@bdd-###` tags without duplicating Gherkin.

## 6. Open Questions

- OQ-BDD-01: Stakeholders should confirm the candidate examples and whether notifications are in scope.
- OQ-BDD-02: Stakeholders should confirm whether Finance Users can resolve review cases or whether only Reviewers can finalize them.

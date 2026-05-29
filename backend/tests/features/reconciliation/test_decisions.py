import pytest

from app.features.reconciliation.contracts import ReconciliationStatus
from app.features.reconciliation.decisions import (
    decide_base_reconciliation,
    validate_actual_payment_input,
    validate_agreement_extraction_input,
)
from app.features.reconciliation.schemas import (
    ActualPaymentInputV1,
    AgreementExtractionInputV1,
)


def _extraction(**overrides: object):
    data: dict[str, object] = {
        "schema_version": "agreement_extraction.v1",
        "agreed_amount_minor": 250000,
        "currency": "PKR",
        "payment_type": "FULL_PAYMENT",
        "due_date": "2026-06-10",
        "is_final_amount": True,
        "evidence_text": "Customer agreed to pay PKR 2,500 by June 10.",
        "confidence": 0.92,
        "needs_human_review": False,
    }
    data.update(overrides)
    return validate_agreement_extraction_input(
        AgreementExtractionInputV1.model_validate(data),
        0.80,
    )


def _payment(**overrides: object):
    data: dict[str, object] = {
        "paid_amount_minor": 250000,
        "currency": "PKR",
        "payment_date": "2026-06-09",
        "reference": "TXN-001",
        "payment_method": "bank_transfer",
    }
    data.update(overrides)
    return validate_actual_payment_input(ActualPaymentInputV1.model_validate(data))


@pytest.mark.parametrize(
    ("extraction", "payment", "status", "difference", "review"),
    [
        (_extraction(), _payment(), ReconciliationStatus.RECONCILED, 0, False),
        (
            _extraction(),
            _payment(paid_amount_minor=240000),
            ReconciliationStatus.UNDERPAID,
            -10000,
            False,
        ),
        (
            _extraction(payment_type="ADVANCE"),
            _payment(paid_amount_minor=100000),
            ReconciliationStatus.PARTIAL_PAYMENT,
            -150000,
            False,
        ),
        (
            _extraction(),
            _payment(paid_amount_minor=260000),
            ReconciliationStatus.OVERPAID,
            10000,
            False,
        ),
        (_extraction(), None, ReconciliationStatus.PAYMENT_NOT_FOUND, None, True),
        (
            _extraction(confidence=0.70),
            _payment(),
            ReconciliationStatus.NEEDS_REVIEW,
            None,
            True,
        ),
        (
            _extraction(needs_human_review=True),
            _payment(),
            ReconciliationStatus.NEEDS_REVIEW,
            None,
            True,
        ),
        (
            _extraction(agreed_amount_minor=None),
            _payment(),
            ReconciliationStatus.NEEDS_REVIEW,
            None,
            True,
        ),
        (
            _extraction(),
            _payment(currency="USD"),
            ReconciliationStatus.NEEDS_REVIEW,
            None,
            True,
        ),
    ],
)
def test_decide_base_reconciliation_statuses(
    extraction,
    payment,
    status: ReconciliationStatus,
    difference: int | None,
    review: bool,
) -> None:
    """Verifies the deterministic Base API decision order.

    Summary:
        Covers exact match, underpaid, partial payment, overpaid, missing
        payment, low confidence, review flag, missing amount, and currency
        mismatch.
    Mocks:
        None.
    Assertions:
        Status, difference, currency, reason, confidence, and review flag match
        the Milestone 1 rules.
    """
    decision = decide_base_reconciliation(extraction, payment, 0.80)

    assert decision.status is status
    assert decision.difference_minor == difference
    assert decision.currency == "PKR"
    assert decision.needs_human_review is review
    assert decision.reason
    assert decision.confidence == extraction.confidence


@pytest.mark.parametrize(
    "payment",
    [
        _payment(paid_amount_minor=None),
        _payment(currency=None),
    ],
)
def test_routes_incomplete_actual_payment_to_review(payment) -> None:
    """Verifies incomplete supplied payment evidence routes to review.

    Summary:
        Avoids treating partial actual-payment evidence as payment not found.
    Mocks:
        None.
    Assertions:
        Decision status is `NEEDS_REVIEW` and no difference is computed.
    """
    decision = decide_base_reconciliation(_extraction(), payment, 0.80)

    assert decision.status is ReconciliationStatus.NEEDS_REVIEW
    assert decision.difference_minor is None
    assert decision.needs_human_review is True

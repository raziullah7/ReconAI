from datetime import date
from math import inf, nan

import pytest
from pydantic import ValidationError

from app.domain.reconciliation.decisions import (
    validate_actual_payment_input,
    validate_agreement_extraction_input,
)
from app.schemas.reconciliation import (
    ActualPaymentInputV1,
    AgreementExtractionInputV1,
    PaymentType,
)


def _valid_extraction(**overrides: object) -> AgreementExtractionInputV1:
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
        "model_name": "mock-extractor",
        "raw_llm_output": {"source": "fixture", "amount": 250000},
    }
    data.update(overrides)
    return AgreementExtractionInputV1.model_validate(data)


def test_accepts_valid_agreement_extraction_input() -> None:
    """Verifies a complete agreement extraction fixture is accepted.

    Summary:
        Validates the LLM-shaped input used by the Base API.
    Mocks:
        None.
    Assertions:
        Minor-unit amount, currency, payment type, evidence, confidence, and
        review flag are preserved.
    """
    input_model = _valid_extraction()

    validated = validate_agreement_extraction_input(input_model, 0.80)

    assert validated.agreed_amount_minor == 250000
    assert validated.currency == "PKR"
    assert validated.payment_type is PaymentType.FULL_PAYMENT
    assert validated.evidence_text == "Customer agreed to pay PKR 2,500 by June 10."
    assert validated.confidence == 0.92
    assert validated.needs_human_review is False
    assert validated.raw_llm_output == {"source": "fixture", "amount": 250000}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("agreed_amount_minor", -1),
        ("confidence", 1.2),
        ("currency", "pkr"),
        ("payment_type", "WIRE"),
        ("raw_llm_output", {"bad": object()}),
        ("raw_llm_output", {"bad": nan}),
        ("raw_llm_output", {"bad": inf}),
    ],
)
def test_rejects_invalid_agreement_extraction_input(
    field: str,
    value: object,
) -> None:
    """Verifies malformed extraction fields fail validation.

    Summary:
        Rejects invalid money, confidence, currency, payment type, and raw LLM
        output values.
    Mocks:
        None.
    Assertions:
        Validation errors name the invalid field.
    """
    with pytest.raises(ValidationError) as exc_info:
        _valid_extraction(**{field: value})

    assert field in str(exc_info.value)


def test_rejects_missing_evidence_for_review_prone_extraction() -> None:
    """Verifies low-confidence extraction must carry evidence text.

    Summary:
        Rejects review-prone extraction data when evidence text is blank.
    Mocks:
        None.
    Assertions:
        The validation error identifies `evidence_text`.
    """
    input_model = _valid_extraction(confidence=0.70, evidence_text="   ")

    with pytest.raises(ValueError) as exc_info:
        validate_agreement_extraction_input(input_model, 0.80)

    assert "evidence_text" in str(exc_info.value)


def test_accepts_valid_actual_payment_input() -> None:
    """Verifies a complete actual payment fixture is accepted.

    Summary:
        Validates manually supplied payment evidence for the Base API.
    Mocks:
        None.
    Assertions:
        Paid amount, currency, payment date, reference, and method are
        preserved.
    """
    input_model = ActualPaymentInputV1.model_validate(
        {
            "paid_amount_minor": 250000,
            "currency": "PKR",
            "payment_date": "2026-06-09",
            "reference": "TXN-001",
            "payment_method": "bank_transfer",
        }
    )

    validated = validate_actual_payment_input(input_model)

    assert validated is not None
    assert validated.paid_amount_minor == 250000
    assert validated.currency == "PKR"
    assert validated.payment_date == date(2026, 6, 9)
    assert validated.reference == "TXN-001"
    assert validated.payment_method == "bank_transfer"

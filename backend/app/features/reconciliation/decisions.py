from app.features.reconciliation.contracts import (
    ReconciliationDecisionV1,
    ReconciliationStatus,
)
from app.features.reconciliation.schemas import (
    ActualPaymentInputV1,
    AgreementExtractionInputV1,
    PaymentType,
    ValidatedActualPayment,
    ValidatedAgreementExtraction,
)

PARTIAL_LIKE_TYPES = {
    PaymentType.ADVANCE,
    PaymentType.PARTIAL_PAYMENT,
    PaymentType.INSTALLMENT,
}


def validate_agreement_extraction_input(
    input: AgreementExtractionInputV1,
    confidence_threshold: float,
) -> ValidatedAgreementExtraction:
    """Validate LLM-shaped agreement evidence for the Base API.

    What: Normalizes the extraction payload accepted by Milestone 1.
    Why: The backend must trust only validated fields before making finance
        decisions.

    Args:
        input: LLM-shaped extraction payload from the API or tests.
        confidence_threshold: Threshold below which evidence text is required.

    Returns:
        ValidatedAgreementExtraction: Normalized agreement fields.

    Raises:
        ValueError: If required evidence, money, currency, payment type, or
            confidence values are invalid.
    """
    if not 0 <= confidence_threshold <= 1:
        msg = "confidence_threshold must be between 0 and 1"
        raise ValueError(msg)
    if _is_review_prone(input, confidence_threshold) and not _has_evidence(input):
        msg = "evidence_text is required for review-prone extraction data"
        raise ValueError(msg)

    return ValidatedAgreementExtraction(
        schema_version=input.schema_version,
        agreed_amount_minor=input.agreed_amount_minor,
        currency=input.currency,
        payment_type=input.payment_type,
        due_date=input.due_date,
        is_final_amount=input.is_final_amount,
        evidence_text=input.evidence_text,
        confidence=input.confidence,
        needs_human_review=input.needs_human_review,
        model_name=input.model_name,
        raw_llm_output=input.raw_llm_output,
    )


def validate_actual_payment_input(
    input: ActualPaymentInputV1 | None,
) -> ValidatedActualPayment | None:
    """Validate optional payment evidence for the Base API.

    What: Normalizes manually supplied actual-payment data.
    Why: Milestone 1 compares one payment snapshot without a payment ledger.

    Args:
        input: Optional actual payment payload.

    Returns:
        ValidatedActualPayment | None: Normalized payment evidence, or None
        when no payment was supplied.
    """
    if input is None:
        return None
    return ValidatedActualPayment(
        paid_amount_minor=input.paid_amount_minor,
        currency=input.currency,
        payment_date=input.payment_date,
        reference=input.reference,
        payment_method=input.payment_method,
    )


def decide_base_reconciliation(
    extraction: ValidatedAgreementExtraction,
    actual_payment: ValidatedActualPayment | None,
    confidence_threshold: float,
) -> ReconciliationDecisionV1:
    """Compute the deterministic Base API reconciliation decision.

    What: Applies the Milestone 1 decision order to validated evidence.
    Why: LLM output must not decide final finance status.

    Args:
        extraction: Validated agreement evidence.
        actual_payment: Optional validated payment evidence.
        confidence_threshold: Configured review threshold from settings.

    Returns:
        ReconciliationDecisionV1: Status, amounts, difference, currency,
        reason, review flag, and confidence. Difference is always
        `paid_amount_minor - agreed_amount_minor` when both values exist.
    """
    if extraction.needs_human_review or extraction.confidence < confidence_threshold:
        return _decision(
            extraction,
            actual_payment,
            ReconciliationStatus.NEEDS_REVIEW,
            "Extraction requires human review.",
            needs_human_review=True,
        )
    if extraction.agreed_amount_minor is None or extraction.currency is None:
        return _decision(
            extraction,
            actual_payment,
            ReconciliationStatus.NEEDS_REVIEW,
            "Agreement amount or currency is missing.",
            needs_human_review=True,
        )
    if actual_payment is None:
        return _decision(
            extraction,
            actual_payment,
            ReconciliationStatus.PAYMENT_NOT_FOUND,
            "No actual payment was supplied.",
            needs_human_review=True,
        )
    if actual_payment.paid_amount_minor is None or actual_payment.currency is None:
        return _decision(
            extraction,
            actual_payment,
            ReconciliationStatus.NEEDS_REVIEW,
            "Actual payment amount or currency is missing.",
            needs_human_review=True,
        )
    if actual_payment.currency != extraction.currency:
        return _decision(
            extraction,
            actual_payment,
            ReconciliationStatus.NEEDS_REVIEW,
            "Actual payment currency does not match the agreement currency.",
            needs_human_review=True,
        )

    difference_minor = actual_payment.paid_amount_minor - extraction.agreed_amount_minor
    if difference_minor == 0:
        status = ReconciliationStatus.RECONCILED
        reason = "Payment matched the agreed amount."
    elif difference_minor < 0 and extraction.payment_type in PARTIAL_LIKE_TYPES:
        status = ReconciliationStatus.PARTIAL_PAYMENT
        reason = "Payment is below the agreed amount for a partial-like payment type."
    elif difference_minor < 0:
        status = ReconciliationStatus.UNDERPAID
        reason = "Payment is below the agreed amount."
    else:
        status = ReconciliationStatus.OVERPAID
        reason = "Payment is above the agreed amount."

    return ReconciliationDecisionV1(
        status=status,
        agreed_amount_minor=extraction.agreed_amount_minor,
        paid_amount_minor=actual_payment.paid_amount_minor,
        difference_minor=difference_minor,
        currency=extraction.currency,
        reason=reason,
        needs_human_review=False,
        confidence=extraction.confidence,
    )


def _is_review_prone(
    input: AgreementExtractionInputV1,
    confidence_threshold: float,
) -> bool:
    return input.needs_human_review or input.confidence < confidence_threshold


def _has_evidence(input: AgreementExtractionInputV1) -> bool:
    return input.evidence_text is not None and bool(input.evidence_text.strip())


def _decision(
    extraction: ValidatedAgreementExtraction,
    actual_payment: ValidatedActualPayment | None,
    status: ReconciliationStatus,
    reason: str,
    *,
    needs_human_review: bool,
) -> ReconciliationDecisionV1:
    return ReconciliationDecisionV1(
        status=status,
        agreed_amount_minor=extraction.agreed_amount_minor,
        paid_amount_minor=(
            actual_payment.paid_amount_minor if actual_payment is not None else None
        ),
        difference_minor=None,
        currency=extraction.currency,
        reason=reason,
        needs_human_review=needs_human_review,
        confidence=extraction.confidence,
    )

from typing import Protocol
from uuid import UUID

from app.domain.reconciliation.contracts import (
    BaseReconciliationCase,
    ReconciliationCaseCreateV1,
    ReconciliationDecisionV1,
    ReconciliationStatus,
)
from app.domain.reconciliation.decisions import (
    decide_base_reconciliation,
    validate_actual_payment_input,
    validate_agreement_extraction_input,
)
from app.schemas.reconciliation import (
    ActualPaymentInputV1,
    AgreementExtractionInputV1,
    PaymentType,
    ReconciliationCaseCreateRequestV1,
    ReconciliationCaseListItemV1,
    ReconciliationCaseResponseV1,
    ReconciliationDecisionResponseV1,
)


class BaseReconciliationCaseRepositoryProtocol(Protocol):
    """Repository behavior required by the M1.3 service."""

    def create(
        self,
        input: ReconciliationCaseCreateV1,
        decision: ReconciliationDecisionV1,
    ) -> BaseReconciliationCase:
        """Persist one case and return the stored projection."""
        ...

    def list(
        self,
        status: ReconciliationStatus | None,
        limit: int,
        offset: int,
    ) -> list[BaseReconciliationCase]:
        """Return stored cases for list responses."""
        ...

    def get(self, case_id: UUID) -> BaseReconciliationCase | None:
        """Return one stored case or None."""
        ...


class BaseReconciliationCaseService:
    """Coordinate Base API validation, decisions, and persistence."""

    def __init__(
        self,
        repository: BaseReconciliationCaseRepositoryProtocol,
        confidence_threshold: float,
    ) -> None:
        """Store repository and threshold dependencies for service methods."""
        self._repository = repository
        self._confidence_threshold = confidence_threshold

    def create_case(
        self,
        input: ReconciliationCaseCreateRequestV1,
    ) -> ReconciliationCaseResponseV1:
        """Validate, decide, persist, and return one Base API case."""
        extraction = validate_agreement_extraction_input(
            input.extraction,
            self._confidence_threshold,
        )
        actual_payment = validate_actual_payment_input(input.actual_payment)
        decision = decide_base_reconciliation(
            extraction,
            actual_payment,
            self._confidence_threshold,
        )
        create_input = ReconciliationCaseCreateV1(
            external_reference=input.external_reference,
            customer_reference=input.customer_reference,
            source_text=input.source_text,
            extraction_snapshot=input.extraction.model_dump(mode="json"),
            actual_payment_snapshot=(
                input.actual_payment.model_dump(mode="json")
                if input.actual_payment is not None
                else None
            ),
        )
        case = self._repository.create(create_input, decision)
        return _map_case_response(case)

    def list_cases(
        self,
        status: ReconciliationStatus | None,
        limit: int,
        offset: int,
    ) -> list[ReconciliationCaseListItemV1]:
        """Map stored repository cases to list-item response models."""
        return [
            _map_case_list_item(case)
            for case in self._repository.list(status=status, limit=limit, offset=offset)
        ]

    def get_case(self, case_id: UUID) -> ReconciliationCaseResponseV1 | None:
        """Map one stored repository case to a detail response model."""
        case = self._repository.get(case_id)
        if case is None:
            return None
        return _map_case_response(case)


def _map_case_response(case: BaseReconciliationCase) -> ReconciliationCaseResponseV1:
    return ReconciliationCaseResponseV1(
        id=case.id,
        external_reference=case.external_reference,
        customer_reference=case.customer_reference,
        source_text=case.source_text,
        extraction=_map_extraction_snapshot(case),
        actual_payment=(
            _map_actual_payment_snapshot(case)
            if case.actual_payment_snapshot is not None
            else None
        ),
        decision=_map_decision_response(case),
        created_at=case.created_at,
        updated_at=case.updated_at,
    )


def _map_extraction_snapshot(
    case: BaseReconciliationCase,
) -> AgreementExtractionInputV1:
    snapshot_fields = {
        "schema_version",
        "agreed_amount_minor",
        "currency",
        "payment_type",
        "due_date",
        "is_final_amount",
        "evidence_text",
        "confidence",
        "needs_human_review",
        "model_name",
        "raw_llm_output",
    }
    snapshot = {
        key: value
        for key, value in case.extraction_snapshot.items()
        if key in snapshot_fields
    }
    snapshot.setdefault("schema_version", "agreement_extraction.v1")
    snapshot.setdefault("agreed_amount_minor", case.agreed_amount_minor)
    snapshot.setdefault("currency", case.currency)
    snapshot.setdefault("payment_type", PaymentType.UNKNOWN.value)
    snapshot.setdefault("confidence", case.confidence)
    snapshot.setdefault("needs_human_review", case.needs_human_review)
    return AgreementExtractionInputV1.model_validate(snapshot)


def _map_actual_payment_snapshot(
    case: BaseReconciliationCase,
) -> ActualPaymentInputV1:
    if case.actual_payment_snapshot is None:
        msg = "actual payment snapshot is missing"
        raise ValueError(msg)
    snapshot_fields = {
        "paid_amount_minor",
        "currency",
        "payment_date",
        "reference",
        "payment_method",
    }
    snapshot = {
        key: value
        for key, value in case.actual_payment_snapshot.items()
        if key in snapshot_fields
    }
    return ActualPaymentInputV1.model_validate(snapshot)


def _map_case_list_item(case: BaseReconciliationCase) -> ReconciliationCaseListItemV1:
    return ReconciliationCaseListItemV1(
        id=case.id,
        external_reference=case.external_reference,
        customer_reference=case.customer_reference,
        status=case.status,
        agreed_amount_minor=case.agreed_amount_minor,
        paid_amount_minor=case.paid_amount_minor,
        difference_minor=case.difference_minor,
        currency=case.currency,
        needs_human_review=case.needs_human_review,
        created_at=case.created_at,
        updated_at=case.updated_at,
    )


def _map_decision_response(
    case: BaseReconciliationCase,
) -> ReconciliationDecisionResponseV1:
    return ReconciliationDecisionResponseV1(
        status=case.status,
        agreed_amount_minor=case.agreed_amount_minor,
        paid_amount_minor=case.paid_amount_minor,
        difference_minor=case.difference_minor,
        currency=case.currency,
        reason=case.reason,
        needs_human_review=case.needs_human_review,
        confidence=case.confidence,
    )

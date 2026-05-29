from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.reconciliation.contracts import (
    BaseReconciliationCase,
    ReconciliationCaseCreateV1,
    ReconciliationDecisionV1,
    ReconciliationStatus,
)
from app.schemas.reconciliation import (
    ReconciliationCaseCreateRequestV1,
    ReconciliationCaseListItemV1,
    ReconciliationCaseResponseV1,
)
from app.services.reconciliation import BaseReconciliationCaseService


class FakeRepository:
    """Capture service persistence calls for pure service tests."""

    def __init__(self) -> None:
        self.created_input: ReconciliationCaseCreateV1 | None = None
        self.created_decision: ReconciliationDecisionV1 | None = None
        self.cases: list[BaseReconciliationCase] = []

    def create(
        self,
        input: ReconciliationCaseCreateV1,
        decision: ReconciliationDecisionV1,
    ) -> BaseReconciliationCase:
        self.created_input = input
        self.created_decision = decision
        case = _case_from_input(uuid4(), input, decision)
        self.cases.insert(0, case)
        return case

    def list(
        self,
        status: ReconciliationStatus | None,
        limit: int,
        offset: int,
    ) -> list[BaseReconciliationCase]:
        cases = [case for case in self.cases if status is None or case.status is status]
        return cases[offset : offset + limit]

    def get(self, case_id: UUID) -> BaseReconciliationCase | None:
        return next((case for case in self.cases if case.id == case_id), None)


def _case_from_input(
    case_id: UUID,
    input: ReconciliationCaseCreateV1,
    decision: ReconciliationDecisionV1,
) -> BaseReconciliationCase:
    now = datetime(2026, 6, 1, tzinfo=UTC)
    return BaseReconciliationCase(
        id=case_id,
        external_reference=input.external_reference,
        customer_reference=input.customer_reference,
        source_text=input.source_text,
        extraction_snapshot=input.extraction_snapshot,
        actual_payment_snapshot=input.actual_payment_snapshot,
        agreed_amount_minor=decision.agreed_amount_minor,
        paid_amount_minor=decision.paid_amount_minor,
        difference_minor=decision.difference_minor,
        currency=decision.currency,
        status=decision.status,
        reason=decision.reason,
        needs_human_review=decision.needs_human_review,
        confidence=decision.confidence,
        version=1,
        created_at=now,
        updated_at=now,
    )


def _request(**overrides: object) -> ReconciliationCaseCreateRequestV1:
    data: dict[str, object] = {
        "external_reference": "CALL-001",
        "customer_reference": "CUST-001",
        "source_text": "Customer agreed to pay PKR 2,500.",
        "extraction": {
            "schema_version": "agreement_extraction.v1",
            "agreed_amount_minor": 250000,
            "currency": "PKR",
            "payment_type": "FULL_PAYMENT",
            "due_date": "2026-06-10",
            "is_final_amount": True,
            "evidence_text": "Customer agreed to pay PKR 2,500 by June 10.",
            "confidence": 0.92,
            "needs_human_review": False,
            "raw_llm_output": {"source": "fixture"},
        },
        "actual_payment": {
            "paid_amount_minor": 250000,
            "currency": "PKR",
            "payment_date": "2026-06-09",
            "reference": "TXN-001",
            "payment_method": "bank_transfer",
        },
    }
    data.update(overrides)
    return ReconciliationCaseCreateRequestV1.model_validate(data)


def test_service_creates_case_with_snapshots() -> None:
    """Verifies service validation, decision, and persistence orchestration.

    Summary:
        Creates one Base API case through the service.
    Mocks:
        FakeRepository captures persistence input.
    Assertions:
        Repository receives request snapshots and decision confidence, and the
        response contains the computed decision.
    """
    repository = FakeRepository()
    service = BaseReconciliationCaseService(repository, 0.80)

    response = service.create_case(_request())

    assert isinstance(response, ReconciliationCaseResponseV1)
    assert repository.created_input is not None
    assert repository.created_decision is not None
    assert (
        repository.created_input.extraction_snapshot["schema_version"]
        == "agreement_extraction.v1"
    )
    assert repository.created_input.actual_payment_snapshot is not None
    assert repository.created_input.actual_payment_snapshot["reference"] == "TXN-001"
    assert repository.created_decision.confidence == 0.92
    assert response.decision.status is ReconciliationStatus.RECONCILED
    assert response.decision.confidence == 0.92


def test_service_creates_payment_not_found_case_without_payment_snapshot() -> None:
    """Verifies service create handles missing actual payment.

    Summary:
        Creates a case with no supplied payment evidence.
    Mocks:
        FakeRepository captures persistence input.
    Assertions:
        The stored payment snapshot is None and the decision is
        `PAYMENT_NOT_FOUND`.
    """
    repository = FakeRepository()
    service = BaseReconciliationCaseService(repository, 0.80)

    response = service.create_case(_request(actual_payment=None))

    assert repository.created_input is not None
    assert repository.created_input.actual_payment_snapshot is None
    assert response.decision.status is ReconciliationStatus.PAYMENT_NOT_FOUND


def test_service_list_and_get_map_repository_cases() -> None:
    """Verifies service list/get response mapping.

    Summary:
        Reads cases through the service without adding HTTP behavior.
    Mocks:
        FakeRepository stores one projection.
    Assertions:
        List returns list-item models, get returns a detail response, and
        missing IDs return None.
    """
    repository = FakeRepository()
    service = BaseReconciliationCaseService(repository, 0.80)
    created = service.create_case(_request())

    listed = service.list_cases(status=None, limit=10, offset=0)
    fetched = service.get_case(created.id)
    missing = service.get_case(uuid4())

    assert len(listed) == 1
    assert isinstance(listed[0], ReconciliationCaseListItemV1)
    assert listed[0].id == created.id
    assert fetched == created
    assert missing is None


def test_service_maps_minimal_repository_case_snapshots() -> None:
    """Verifies service reads M1.2-style stored snapshots safely.

    Summary:
        Maps a repository projection whose extraction snapshot predates the
        full M1.3 request schema.
    Mocks:
        FakeRepository stores one minimal repository projection.
    Assertions:
        List and get return response models with `UNKNOWN` payment type instead
        of raising validation errors.
    """
    repository = FakeRepository()
    service = BaseReconciliationCaseService(repository, 0.80)
    decision = ReconciliationDecisionV1(
        status=ReconciliationStatus.RECONCILED,
        agreed_amount_minor=250000,
        paid_amount_minor=250000,
        difference_minor=0,
        currency="PKR",
        reason="Payment matched the agreed amount.",
        needs_human_review=False,
        confidence=0.92,
    )
    repository.cases.append(
        _case_from_input(
            uuid4(),
            ReconciliationCaseCreateV1(
                external_reference="CALL-LEGACY",
                customer_reference="CUST-001",
                source_text="Customer agreed to pay PKR 2,500.",
                extraction_snapshot={
                    "schema_version": "agreement_extraction.v1",
                    "agreed_amount_minor": 250000,
                    "currency": "PKR",
                    "confidence": 0.92,
                    "needs_human_review": False,
                },
                actual_payment_snapshot={
                    "paid_amount_minor": 250000,
                    "currency": "PKR",
                    "reference": "TXN-001",
                },
            ),
            decision,
        )
    )

    listed = service.list_cases(status=None, limit=10, offset=0)
    fetched = service.get_case(repository.cases[0].id)

    assert len(listed) == 1
    assert fetched is not None
    assert fetched.extraction.payment_type == "UNKNOWN"
    assert fetched.decision.confidence == 0.92

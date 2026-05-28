from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class ReconciliationStatus(StrEnum):
    """Status values persisted by the Base API repository."""

    RECONCILED = "RECONCILED"
    UNDERPAID = "UNDERPAID"
    OVERPAID = "OVERPAID"
    PARTIAL_PAYMENT = "PARTIAL_PAYMENT"
    PAYMENT_NOT_FOUND = "PAYMENT_NOT_FOUND"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class ReconciliationCaseCreateV1:
    """Carry snapshots and optional references into persistence."""

    external_reference: str | None
    customer_reference: str | None
    source_text: str | None
    extraction_snapshot: Mapping[str, object]
    actual_payment_snapshot: Mapping[str, object] | None


@dataclass(frozen=True, slots=True)
class ReconciliationDecisionV1:
    """Carry computed decision fields into persistence."""

    status: ReconciliationStatus
    agreed_amount_minor: int | None
    paid_amount_minor: int | None
    difference_minor: int | None
    currency: str | None
    reason: str
    needs_human_review: bool
    confidence: float


@dataclass(frozen=True, slots=True)
class BaseReconciliationCase:
    """Projection returned by the Base API repository."""

    id: UUID
    external_reference: str | None
    customer_reference: str | None
    source_text: str | None
    extraction_snapshot: Mapping[str, object]
    actual_payment_snapshot: Mapping[str, object] | None
    agreed_amount_minor: int | None
    paid_amount_minor: int | None
    difference_minor: int | None
    currency: str | None
    status: ReconciliationStatus
    reason: str
    needs_human_review: bool
    confidence: float
    version: int
    created_at: datetime
    updated_at: datetime

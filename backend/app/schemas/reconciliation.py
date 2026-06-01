from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from math import isfinite
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.reconciliation.contracts import ReconciliationStatus

type JsonValue = (
    str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]
)


class PaymentType(StrEnum):
    """Payment type values accepted in Base API extraction input."""

    FULL_PAYMENT = "FULL_PAYMENT"
    ADVANCE = "ADVANCE"
    PARTIAL_PAYMENT = "PARTIAL_PAYMENT"
    INSTALLMENT = "INSTALLMENT"
    BALANCE_PAYMENT = "BALANCE_PAYMENT"
    DISCOUNTED_AMOUNT = "DISCOUNTED_AMOUNT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class ValidatedAgreementExtraction:
    """Normalized agreement extraction fields for deterministic decisions."""

    schema_version: str
    agreed_amount_minor: int | None
    currency: str | None
    payment_type: PaymentType
    due_date: date | None
    is_final_amount: bool | None
    evidence_text: str | None
    confidence: float
    needs_human_review: bool
    model_name: str | None
    raw_llm_output: JsonValue | None


@dataclass(frozen=True, slots=True)
class ValidatedActualPayment:
    """Normalized actual payment fields for deterministic decisions."""

    paid_amount_minor: int | None
    currency: str | None
    payment_date: date | None
    reference: str | None
    payment_method: str | None


class _BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AgreementExtractionInputV1(_BaseSchema):
    """LLM-shaped agreement extraction request model for Milestone 1."""

    schema_version: str = Field(pattern=r"^agreement_extraction\.v1$")
    agreed_amount_minor: int | None = Field(default=None, ge=0)
    currency: str | None = None
    payment_type: PaymentType
    due_date: date | None = None
    is_final_amount: bool | None = None
    evidence_text: str | None = None
    confidence: float = Field(ge=0, le=1)
    needs_human_review: bool
    model_name: str | None = None
    raw_llm_output: JsonValue | None = None

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str | None) -> str | None:
        """Validate optional uppercase ISO-like currency codes."""
        if value is None:
            return None
        if len(value) != 3 or not value.isalpha() or not value.isupper():
            msg = "currency must be an uppercase 3-letter code"
            raise ValueError(msg)
        return value

    @field_validator("raw_llm_output")
    @classmethod
    def validate_raw_llm_output(cls, value: JsonValue | None) -> JsonValue | None:
        """Reject values that cannot be represented as strict JSON."""
        _reject_non_finite_numbers(value)
        return value


class ActualPaymentInputV1(_BaseSchema):
    """Manually supplied actual payment request model for Milestone 1."""

    paid_amount_minor: int | None = Field(default=None, ge=0)
    currency: str | None = None
    payment_date: date | None = None
    reference: str | None = None
    payment_method: str | None = None

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str | None) -> str | None:
        """Validate optional uppercase ISO-like currency codes."""
        if value is None:
            return None
        if len(value) != 3 or not value.isalpha() or not value.isupper():
            msg = "currency must be an uppercase 3-letter code"
            raise ValueError(msg)
        return value


class ReconciliationCaseCreateRequestV1(_BaseSchema):
    """Base API request model accepted by the service and router."""

    external_reference: str | None = None
    customer_reference: str | None = None
    source_text: str | None = None
    extraction: AgreementExtractionInputV1
    actual_payment: ActualPaymentInputV1 | None = None


class ReconciliationDecisionResponseV1(_BaseSchema):
    """Decision response model returned by Base API service methods."""

    status: ReconciliationStatus
    agreed_amount_minor: int | None
    paid_amount_minor: int | None
    difference_minor: int | None
    currency: str | None
    reason: str
    needs_human_review: bool
    confidence: float


class ReconciliationCaseResponseV1(_BaseSchema):
    """Stored case detail response model returned by the Base API service."""

    id: UUID
    external_reference: str | None
    customer_reference: str | None
    source_text: str | None
    extraction: AgreementExtractionInputV1
    actual_payment: ActualPaymentInputV1 | None
    decision: ReconciliationDecisionResponseV1
    created_at: datetime
    updated_at: datetime


class ReconciliationCaseListItemV1(_BaseSchema):
    """Stored case list item returned by the Base API service."""

    id: UUID
    external_reference: str | None
    customer_reference: str | None
    status: ReconciliationStatus
    agreed_amount_minor: int | None
    paid_amount_minor: int | None
    difference_minor: int | None
    currency: str | None
    needs_human_review: bool
    created_at: datetime
    updated_at: datetime


class ReconciliationCaseListResponseV1(_BaseSchema):
    """Collection response for stored reconciliation case summaries."""

    items: list[ReconciliationCaseListItemV1]


def _reject_non_finite_numbers(value: JsonValue | None) -> None:
    if isinstance(value, float) and not isfinite(value):
        msg = "raw_llm_output must contain only finite JSON numbers"
        raise ValueError(msg)
    if isinstance(value, list):
        for item in value:
            _reject_non_finite_numbers(item)
    if isinstance(value, dict):
        for item in value.values():
            _reject_non_finite_numbers(item)

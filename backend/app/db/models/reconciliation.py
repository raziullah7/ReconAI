from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for Milestone 1 persistence models."""


class BaseReconciliationCaseModel(Base):
    """SQLAlchemy model for the non-tenantized Base API case table."""

    __tablename__ = "reconciliation_cases"
    __table_args__ = (
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_reconciliation_cases_confidence",
        ),
        CheckConstraint(
            "status IN ("
            "'RECONCILED', 'UNDERPAID', 'OVERPAID', 'PARTIAL_PAYMENT', "
            "'PAYMENT_NOT_FOUND', 'NEEDS_REVIEW', 'FAILED'"
            ")",
            name="ck_reconciliation_cases_status",
        ),
        CheckConstraint(
            "agreed_amount_minor IS NULL OR paid_amount_minor IS NULL OR "
            "(difference_minor IS NOT NULL AND "
            "difference_minor = paid_amount_minor - agreed_amount_minor)",
            name="ck_reconciliation_cases_difference",
        ),
        Index("idx_base_cases_created", "created_at"),
        Index("idx_base_cases_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    external_reference: Mapped[str | None] = mapped_column(String(120))
    customer_reference: Mapped[str | None] = mapped_column(String(120))
    source_text: Mapped[str | None] = mapped_column(Text)
    extraction_snapshot_json: Mapped[dict[str, object]] = mapped_column(JSONB)
    actual_payment_snapshot_json: Mapped[dict[str, object] | None] = mapped_column(
        JSONB
    )
    agreed_amount_minor: Mapped[int | None]
    paid_amount_minor: Mapped[int | None]
    difference_minor: Mapped[int | None]
    currency: Mapped[str | None] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(32))
    reason: Mapped[str] = mapped_column(Text)
    needs_human_review: Mapped[bool]
    confidence: Mapped[float]
    version: Mapped[int] = mapped_column(default=1, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("clock_timestamp()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("clock_timestamp()"),
        onupdate=text("clock_timestamp()"),
    )

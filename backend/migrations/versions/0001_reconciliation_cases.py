"""Create reconciliation cases table.

Revision ID: 0001_reconciliation_cases
Revises:
Create Date: 2026-05-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_reconciliation_cases"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the Base API reconciliation case table and indexes."""
    op.create_table(
        "reconciliation_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_reference", sa.String(length=120), nullable=True),
        sa.Column("customer_reference", sa.String(length=120), nullable=True),
        sa.Column("source_text", sa.Text(), nullable=True),
        sa.Column("extraction_snapshot_json", postgresql.JSONB(), nullable=False),
        sa.Column("actual_payment_snapshot_json", postgresql.JSONB(), nullable=True),
        sa.Column("agreed_amount_minor", sa.Integer(), nullable=True),
        sa.Column("paid_amount_minor", sa.Integer(), nullable=True),
        sa.Column("difference_minor", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("needs_human_review", sa.Boolean(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("clock_timestamp()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_reconciliation_cases_confidence",
        ),
        sa.CheckConstraint(
            "status IN ("
            "'RECONCILED', 'UNDERPAID', 'OVERPAID', 'PARTIAL_PAYMENT', "
            "'PAYMENT_NOT_FOUND', 'NEEDS_REVIEW', 'FAILED'"
            ")",
            name="ck_reconciliation_cases_status",
        ),
        sa.CheckConstraint(
            "agreed_amount_minor IS NULL OR paid_amount_minor IS NULL OR "
            "(difference_minor IS NOT NULL AND "
            "difference_minor = paid_amount_minor - agreed_amount_minor)",
            name="ck_reconciliation_cases_difference",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_base_cases_created",
        "reconciliation_cases",
        ["created_at"],
    )
    op.create_index(
        "idx_base_cases_status",
        "reconciliation_cases",
        ["status"],
    )


def downgrade() -> None:
    """Drop the Base API reconciliation case table and indexes."""
    op.drop_index("idx_base_cases_status", table_name="reconciliation_cases")
    op.drop_index("idx_base_cases_created", table_name="reconciliation_cases")
    op.drop_table("reconciliation_cases")

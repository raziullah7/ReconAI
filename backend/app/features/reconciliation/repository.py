from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.features.reconciliation.contracts import (
    BaseReconciliationCase,
    ReconciliationCaseCreateV1,
    ReconciliationDecisionV1,
    ReconciliationStatus,
)
from app.features.reconciliation.models import BaseReconciliationCaseModel


class BaseReconciliationCaseRepository:
    """Persist and read Base API reconciliation cases."""

    def __init__(self, session: Session) -> None:
        """Store the injected SQLAlchemy session used by repository methods."""
        self._session = session

    def create(
        self,
        input: ReconciliationCaseCreateV1,
        decision: ReconciliationDecisionV1,
    ) -> BaseReconciliationCase:
        """Persist one case from snapshots and a backend-owned decision.

        What: Inserts one `reconciliation_cases` row, flushes generated
            identifiers and timestamps, and maps the row back to a projection.
        Why: Later service and API phases need persistence that does not own
            validation or decision logic.

        Args:
            input: Original request snapshots and optional references.
            decision: Backend-owned reconciliation outcome to store.

        Returns:
            BaseReconciliationCase: Stored case projection.

        States / Side Effects:
            Adds and flushes a SQLAlchemy model in the injected session.
        """
        model = BaseReconciliationCaseModel(
            external_reference=input.external_reference,
            customer_reference=input.customer_reference,
            source_text=input.source_text,
            extraction_snapshot_json=dict(input.extraction_snapshot),
            actual_payment_snapshot_json=(
                dict(input.actual_payment_snapshot)
                if input.actual_payment_snapshot is not None
                else None
            ),
            agreed_amount_minor=decision.agreed_amount_minor,
            paid_amount_minor=decision.paid_amount_minor,
            difference_minor=decision.difference_minor,
            currency=decision.currency,
            status=decision.status.value,
            reason=decision.reason,
            needs_human_review=decision.needs_human_review,
            confidence=decision.confidence,
        )

        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return _map_model(model)

    def list(
        self,
        status: ReconciliationStatus | None,
        limit: int,
        offset: int,
    ) -> list[BaseReconciliationCase]:
        """Return stored cases in newest-first order.

        What: Reads stored cases, optionally filters by status, and applies
            limit/offset pagination.
        Why: M1.4 list endpoints need a repository query that remains local
            and non-tenantized for Milestone 1.

        Args:
            status: Optional reconciliation status filter.
            limit: Maximum number of cases to return.
            offset: Number of newest-first rows to skip.

        Returns:
            list[BaseReconciliationCase]: Matching stored case projections.
        """
        statement: Select[tuple[BaseReconciliationCaseModel]] = select(
            BaseReconciliationCaseModel
        ).order_by(
            BaseReconciliationCaseModel.created_at.desc(),
            BaseReconciliationCaseModel.id.desc(),
        )

        if status is not None:
            statement = statement.where(
                BaseReconciliationCaseModel.status == status.value
            )

        models = self._session.scalars(statement.limit(limit).offset(offset))
        return [_map_model(model) for model in models]

    def get(self, case_id: UUID) -> BaseReconciliationCase | None:
        """Return one stored case by ID or None when it does not exist.

        What: Loads a single case by primary key and maps it to the repository
            projection when present.
        Why: M1.4 detail endpoints need a not-found-safe repository lookup.

        Args:
            case_id: Primary key of the case to fetch.

        Returns:
            BaseReconciliationCase | None: Stored case projection, or None.
        """
        model = self._session.get(BaseReconciliationCaseModel, case_id)
        if model is None:
            return None
        return _map_model(model)


def _map_model(model: BaseReconciliationCaseModel) -> BaseReconciliationCase:
    return BaseReconciliationCase(
        id=model.id,
        external_reference=model.external_reference,
        customer_reference=model.customer_reference,
        source_text=model.source_text,
        extraction_snapshot=dict(model.extraction_snapshot_json),
        actual_payment_snapshot=(
            dict(model.actual_payment_snapshot_json)
            if model.actual_payment_snapshot_json is not None
            else None
        ),
        agreed_amount_minor=model.agreed_amount_minor,
        paid_amount_minor=model.paid_amount_minor,
        difference_minor=model.difference_minor,
        currency=model.currency,
        status=ReconciliationStatus(model.status),
        reason=model.reason,
        needs_human_review=model.needs_human_review,
        confidence=model.confidence,
        version=model.version,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )

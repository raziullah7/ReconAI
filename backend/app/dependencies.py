from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, load_settings
from app.db.session import get_session
from app.repositories.reconciliation import BaseReconciliationCaseRepository
from app.services.reconciliation import BaseReconciliationCaseService


def get_reconciliation_case_repository(
    session: Annotated[Session, Depends(get_session)],
) -> BaseReconciliationCaseRepository:
    """Build the request-scoped reconciliation repository.

    What: Wraps the current SQLAlchemy session in the repository used by the
        Base API service.
    Why: Routers should depend on repository composition instead of opening
        database sessions directly.

    Args:
        session: Request-scoped SQLAlchemy session from the database dependency.

    Returns:
        BaseReconciliationCaseRepository: Repository bound to the request
        session.
    """
    return BaseReconciliationCaseRepository(session)


def get_reconciliation_case_service(
    repository: Annotated[
        BaseReconciliationCaseRepository,
        Depends(get_reconciliation_case_repository),
    ],
    settings: Annotated[Settings, Depends(load_settings)],
) -> BaseReconciliationCaseService:
    """Build the request-scoped reconciliation application service.

    What: Composes the repository and configured confidence threshold into the
        Base API service.
    Why: M1.5 routers need one dependency that exposes use-case behavior
        without constructing services inline.

    Args:
        repository: Repository dependency for Base API case persistence.
        settings: Runtime settings containing the review confidence threshold.

    Returns:
        BaseReconciliationCaseService: Application service ready for router use.
    """
    return BaseReconciliationCaseService(
        repository,
        settings.extraction_review_confidence_threshold,
    )

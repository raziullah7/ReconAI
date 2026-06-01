from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_reconciliation_case_service
from app.domain.reconciliation.contracts import ReconciliationStatus
from app.schemas.reconciliation import (
    ReconciliationCaseCreateRequestV1,
    ReconciliationCaseListResponseV1,
    ReconciliationCaseResponseV1,
)
from app.services.reconciliation import BaseReconciliationCaseService

router = APIRouter(prefix="/v1/reconciliation-cases", tags=["reconciliation"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_reconciliation_case(
    input: ReconciliationCaseCreateRequestV1,
    service: Annotated[
        BaseReconciliationCaseService,
        Depends(get_reconciliation_case_service),
    ],
) -> ReconciliationCaseResponseV1:
    """Create one stored reconciliation case from Base API input.

    What: Accepts LLM-shaped extraction input and optional actual payment
        evidence, then delegates validation, decisioning, and persistence to
        the service layer.
    Why: HTTP handlers should expose the Base API without owning finance rules
        or database writes directly.

    Args:
        input: Request body containing extraction and payment evidence.
        service: Injected Base API application service.

    Returns:
        ReconciliationCaseResponseV1: Stored case detail with backend-owned
        reconciliation decision.

    Raises:
        HTTPException: Converts service validation failures to the canonical
        API error envelope through the registered HTTP handler.
    """
    try:
        return service.create_case(input)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "ValidationFailed",
                "message": str(exc),
            },
        ) from exc


@router.get("")
def list_reconciliation_cases(
    service: Annotated[
        BaseReconciliationCaseService,
        Depends(get_reconciliation_case_service),
    ],
    status_filter: Annotated[ReconciliationStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ReconciliationCaseListResponseV1:
    """List stored reconciliation case summaries.

    What: Reads stored cases with optional status filtering and limit/offset
        pagination.
    Why: The first frontend milestone needs a compact list response before
        cursor pagination and tenant scoping are introduced.

    Args:
        service: Injected Base API application service.
        status_filter: Optional reconciliation status query value.
        limit: Maximum number of items to return.
        offset: Number of newest-first rows to skip.

    Returns:
        ReconciliationCaseListResponseV1: Collection envelope with summary
        items.
    """
    return ReconciliationCaseListResponseV1(
        items=service.list_cases(status_filter, limit, offset)
    )


@router.get("/{case_id}")
def get_reconciliation_case(
    case_id: UUID,
    service: Annotated[
        BaseReconciliationCaseService,
        Depends(get_reconciliation_case_service),
    ],
) -> ReconciliationCaseResponseV1:
    """Return one stored reconciliation case detail.

    What: Fetches a stored case by ID through the service layer.
    Why: Clients need a stable detail endpoint with a canonical not-found
        response before frontend work starts.

    Args:
        case_id: Stored reconciliation case ID.
        service: Injected Base API application service.

    Returns:
        ReconciliationCaseResponseV1: Stored case detail.

    Raises:
        HTTPException: Raised with 404 when the case is missing.
    """
    case = service.get_case(case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NotFound",
                "message": "Reconciliation case was not found.",
            },
        )
    return case

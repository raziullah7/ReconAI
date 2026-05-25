from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class TenantContext:
    """Carry tenant identity through future request boundaries.

    What: Stores the Phase 1 tenant fields named by the interface contract.
    Why: Later request, repository, and worker code need a stable context
        shape before tenant-scoped persistence exists.

    Args:
        tenant_id: Internal tenant identifier, mapped from `tenantId` in
            the planning contract.
        tenant_status: Operational tenant state, mapped from
            `tenantStatus`.
        locale: Tenant locale used by later formatting logic.
        currency_default: Default tenant currency, mapped from
            `currencyDefault`.
    """

    tenant_id: str
    tenant_status: str
    locale: str
    currency_default: str


@dataclass(frozen=True)
class UserContext:
    """Carry authenticated user identity for future authorization.

    What: Stores user, tenant, role, and permission values from the
        interface contract.
    Why: Phase 1 freezes the request context shape without implementing
        authentication or RBAC behavior.

    Args:
        user_id: Internal user identifier, mapped from `userId`.
        tenant_id: Tenant identifier associated with the user.
        role: Role name from the planned role set.
        permissions: Immutable permission names granted to the user.
    """

    user_id: str
    tenant_id: str
    role: str
    permissions: frozenset[str]


@dataclass(frozen=True)
class RequestContext:
    """Group tenant, user, request ID, and idempotency context.

    What: Carries the ambient context fields named by the interface
        contract in one immutable object.
    Why: Later services receive context explicitly instead of reading
        global state.

    Args:
        tenant: Tenant context resolved for the request.
        user: Optional user context. Defaults to None for unauthenticated
            foundation paths such as health checks.
        request_id: Correlation identifier, mapped from `requestId`.
        idempotency_key: Optional mutating-request idempotency key. Defaults
            to None because Phase 1 has no mutating API.
    """

    tenant: TenantContext
    user: UserContext | None
    request_id: str
    idempotency_key: str | None = None


class Clock(Protocol):
    """Define the injected time source used by later services."""

    def now(self) -> datetime:
        """Return the current timezone-aware timestamp."""


class Logger(Protocol):
    """Define the structured logging port used by later services."""


class Tracer(Protocol):
    """Define the trace-span port used by later services."""

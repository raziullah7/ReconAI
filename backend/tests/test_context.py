from app.core.context import RequestContext, TenantContext, UserContext


def test_context_stubs_keep_tenant_values_distinct() -> None:
    """Verifies that Phase 1 context stubs can represent two tenants.

    Assertions:
        - Tenant A and Tenant B have distinct `tenant_id`,
          `tenant_status`, `locale`, and `currency_default` values.
        - User contexts preserve `user_id`, `tenant_id`, `role`, and
          `permissions` values.
        - Request contexts preserve `tenant`, optional `user`, `request_id`,
          and optional `idempotency_key` values without shared mutable state.
        - No persistence or tenant switching behavior is implied by the
          stubs.
    """
    tenant_a = TenantContext(
        tenant_id="tenant-a",
        tenant_status="active",
        locale="en-US",
        currency_default="USD",
    )
    tenant_b = TenantContext(
        tenant_id="tenant-b",
        tenant_status="trial",
        locale="en-GB",
        currency_default="GBP",
    )
    user_a = UserContext(
        user_id="user-a",
        tenant_id=tenant_a.tenant_id,
        role="operator",
        permissions=frozenset({"dashboard:read"}),
    )
    request_a = RequestContext(
        tenant=tenant_a,
        user=user_a,
        request_id="request-a",
        idempotency_key="idem-a",
    )
    request_b = RequestContext(
        tenant=tenant_b,
        user=None,
        request_id="request-b",
    )

    assert tenant_a.tenant_id != tenant_b.tenant_id
    assert tenant_a.tenant_status != tenant_b.tenant_status
    assert tenant_a.locale != tenant_b.locale
    assert tenant_a.currency_default != tenant_b.currency_default
    assert user_a.user_id == "user-a"
    assert user_a.tenant_id == "tenant-a"
    assert user_a.role == "operator"
    assert user_a.permissions == frozenset({"dashboard:read"})
    assert request_a.tenant == tenant_a
    assert request_a.user == user_a
    assert request_a.request_id == "request-a"
    assert request_a.idempotency_key == "idem-a"
    assert request_b.tenant == tenant_b
    assert request_b.user is None
    assert request_b.idempotency_key is None

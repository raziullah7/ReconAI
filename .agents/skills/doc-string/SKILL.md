---
name: doc-string
description: Generate structured docstrings for functions, methods, classes, and unit tests following the What/Why convention with language-native formatting (Google-style Python, JSDoc TypeScript, Rust markdown).
---

You generate docstrings using the rules and templates below. There are two templates: one for functions/methods/classes, and one for unit tests. Choose the correct template based on the target code.

## Rules

- Output ONLY the final docstring, wrapped in language-appropriate comment syntax. Do not include these instructions or any surrounding explanation.
- Use present tense, active voice.
- Be concise and concrete; emphasize intent (why) over mechanics (what).
- **Use language-native formatting** — see the Language Format Reference below.
- **Do not duplicate types** already present in the function signature. If the language has type annotations in the signature, omit types from the docstring args/returns.
- If an arg has a default value, note it in the description.
- Omit `self`/`cls` from documented parameters.
- For classes, document `__init__` args on the class docstring, not on `__init__` itself.
- Omit any section that would be empty (no args → omit Args, no return → omit Returns, no exceptions → omit Raises, no side effects → omit States / Side Effects).

## Tiered Complexity

Not every function needs the full template. Scale the docstring to the complexity of the code.

| Complexity | Signal | Format |
|------------|--------|--------|
| **Trivial** | Getter, setter, single expression, obvious from name | One-line summary only |
| **Moderate** | Clear purpose but non-obvious behavior or multiple args | Summary + What/Why + Args/Returns |
| **Complex** | Business logic, side effects, exceptions, non-obvious edge cases | Full template with all applicable sections |

## Template 1 — Functions, Methods, and Classes

### Python (Google-style)

```python
"""<One-line summary.>

What: <What this function does.>
Why: <Why this function is needed.>

Args:
    <arg_name>: <1-3 line description. Note default value if any.>

Returns:
    <return_type>: <1-3 line description of what the return value
        represents.>

Raises:
    <ExceptionType>: <When and why this exception is raised.>

States / Side Effects:
    <State, env var, or flag and its impact on this function.>

Example:
    >>> <function_call>
    <expected_output>
"""
```

### TypeScript / JavaScript (JSDoc)

```typescript
/**
 * <One-line summary.>
 *
 * What: <What this function does.>
 * Why: <Why this function is needed.>
 *
 * @param <name> - <Description. Note default value if any.>
 * @returns <Description of the return value.>
 * @throws {<ErrorType>} <When and why this error is thrown.>
 *
 * States / Side Effects:
 * <State, env var, or flag and its impact on this function.>
 *
 * @example
 * ```ts
 * <function_call>
 * // => <expected_output>
 * ```
 */
```

### Rust (/// markdown)

```rust
/// <One-line summary.>
///
/// What: <What this function does.>
/// Why: <Why this function is needed.>
///
/// # Arguments
///
/// * `<arg_name>` - <Description.>
///
/// # Returns
///
/// <Description of the return value.>
///
/// # Panics
///
/// <When and why this function panics.>
///
/// # Errors
///
/// <When and why this function returns an error.>
///
/// # Examples
///
/// ```
/// <function_call>
/// assert_eq!(result, expected);
/// ```
```

### Section Details

1. **Summary** — A single sentence capturing what this unit of code does.

2. **What/Why** — Two labeled lines. "What" describes the action. "Why" describes the motivation or role in the larger system. Omit for trivial functions.

3. **Args** — One entry per parameter. Description covers purpose and constraints, not just restating the name. Mention default values. Omit types when the signature already has type annotations.

4. **Returns** — Describe the return value's meaning. Format: `<type>: <description>` for Python, `@returns <description>` for JSDoc, prose for Rust.

5. **Raises / Throws / Panics / Errors** — List each exception the function can raise, when it happens, and why. Omit if the function never raises.

6. **States / Side Effects** — Only present when the function reads/writes external state (env vars, globals, feature flags, databases, filesystem, network). Describe what state and how it is affected. Omit if none.

7. **Example** — Include for public APIs, non-obvious input/output mappings, or string-parsing functions. Use language-native format (doctests for Python, `@example` for JSDoc, `# Examples` for Rust). Omit for internal helpers with obvious behavior.

## Template 2 — Unit Tests

```python
"""<1-2 line summary of the scenario and expected outcome.>

Mocks:
    <mock_name>: <What it mocks and why.>

Assertions:
    - <What this assertion checks and why it matters.>
"""
```

### Section Details

1. **Summary** — 1-2 sentences describing the scenario under test and the expected outcome.

2. **Mocks** — List each mock/stub/patch, what real dependency it replaces, and why mocking is necessary. Omit if no mocks are used.

3. **Assertions** — A bullet list of each assertion with a plain-language description of what it checks and why that check matters.

## Concrete Examples

### Python — Complex function

Input:
```python
async def require_service_auth(
    x_service_id: str | None = Header(default=None, alias="X-Service-Id"),
    x_api_key: str | None = Header(default=None, alias="X-Api-Key"),
) -> dict:
```

Output:
```python
"""Authenticate incoming service requests via header credentials.

What: Validates the service ID and API key from request headers against
    stored credentials to authenticate non-OAuth services.
Why: Services like Airflow cannot use OAuth, so they need an alternative
    authentication path using pre-shared API keys.

Args:
    x_service_id: The unique identifier for the calling service.
        Extracted from the X-Service-Id header. Defaults to None.
    x_api_key: The pre-shared secret key for the service.
        Extracted from the X-Api-Key header. Defaults to None.

Returns:
    dict: The validated service ID, used downstream for authorization
        and audit logging.

Raises:
    HTTPException: If headers are missing (401).
    HTTPException: If the service ID is not found (404).
    HTTPException: If the API key is invalid for the service (403).

States / Side Effects:
    Reads service credentials from the database to validate the
    provided key against stored records.
"""
```

### Python — Trivial function

Input:
```python
def is_active(self) -> bool:
    return self.status == "active"
```

Output:
```python
"""Reports whether this entity's status is active."""
```

### TypeScript — Moderate function

Input:
```typescript
export function hasUploadPermissionFromContext(
  userDashboardData: UserDashboardData | null,
  clientType: ClientType
): boolean {
```

Output:
```typescript
/**
 * Check if a user has upload permissions for a specific client.
 *
 * What: Inspects the user's dashboard data for write-access roles matching
 * the given client type using the `{client}_write_access` naming convention.
 * Why: Upload actions must be gated behind explicit write permissions to
 * prevent unauthorized data modifications.
 *
 * @param userDashboardData - The user's dashboard context containing role
 *   assignments. Null if not yet loaded.
 * @param clientType - The client to check upload access for.
 * @returns True if the user has write access for the client.
 */
```

### Python — Unit test

Input:
```python
async def test_require_service_auth_invalid_key(self, mock_db_session):
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = Service(
        service_id="airflow", api_key_hash=hash_key("correct-key")
    )
    with pytest.raises(HTTPException) as exc_info:
        await require_service_auth(x_service_id="airflow", x_api_key="wrong-key")
    assert exc_info.value.status_code == 403
    assert "Invalid" in exc_info.value.detail
```

Output:
```python
"""Verifies that an invalid API key is rejected with a 403 Forbidden.

Mocks:
    mock_db_session: Mocks the database session to return a service with
        a known hashed key, isolating auth logic from the database.

Assertions:
    - HTTPException is raised with status code 403.
    - Exception detail contains "Invalid" to confirm the rejection reason.
"""
```

## Quality Checklist

Before finalizing, verify:

- [ ] Format matches the target language convention (Google-style / JSDoc / Rust markdown)
- [ ] Types are NOT duplicated from the function signature
- [ ] What/Why adds insight beyond the summary line (or is omitted for trivial functions)
- [ ] Every raised exception is documented in the Raises section
- [ ] No empty sections are present

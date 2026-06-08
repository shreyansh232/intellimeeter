# Testing

## Test Infrastructure

The project uses `pytest` and `pytest-asyncio` with a robust configuration in `tests/conftest.py`:
* **Dynamic Database**: Automatically creates a separate `intellimeeter_test` database.
* **Transaction Isolation**: Each test run starts with clean tables.
* **Async Client**: Provides an `AsyncClient` fixture with dependency overrides for the test database.

## Unit Tests

* **Authentication (`tests/unit/test_auth.py`)**:
    * Password hashing and verification with `pwdlib`.
    * JWT generation, claim validation (`sub`), and expiration handling.
* **Models (`tests/unit/test_models.py`)**:
    * Integrity of User and Meeting records.
    * Verification of async relationships and eager loading (`selectinload`).

## Integration Tests

* **Full Lifecycle (`tests/integration/test_lifecycle.py`)**:
    * **User Flow**: Registration and login.
    * **Meeting Flow**: Creating a meeting and retrieving it.
    * **Analysis Flow**: Running AI analysis (using `unittest.mock` to simulate LLM responses).
    * **Action Items**: Verifying that analysis correctly creates overdue action items and retrieving them via the `/overdue` endpoint.

## Running Tests

```bash
make tests
# OR
PYTHONPATH=. uv run pytest tests/
```

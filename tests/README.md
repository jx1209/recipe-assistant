# Recipe Assistant Tests

## Overview

Comprehensive test suite for the Recipe Assistant application covering authentication, database operations, API endpoints, and security.

## Test Structure

```
tests/
├── conftest.py              # pytest fixtures and configuration
├── test_auth.py            # authentication tests (password hashing, jwt tokens)
├── test_database.py        # database crud operations
├── test_api_auth.py        # api endpoint tests (register, login, protected routes)
└── test_data/              # test database files (auto-created, auto-deleted)
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_auth.py
```

### Run Specific Test Class
```bash
pytest tests/test_auth.py::TestPasswordHashing
```

### Run Tests by Marker
```bash
#unit tests only
pytest -m unit

#authentication tests
pytest -m auth

#integration tests
pytest -m integration

#database tests
pytest -m database
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

## Test Markers

- `unit` - fast, isolated unit tests
- `integration` - integration tests with multiple components
- `auth` - authentication-related tests
- `database` - database operation tests
- `api` - api endpoint tests
- `slow` - slower running tests
- `security` - security-focused tests

## Test Fixtures

### Database Fixtures
- `test_db` - async test database (fresh for each test)
- `db_sync` - synchronous test database

### Auth Fixtures
- `auth_handler` - authentication handler instance
- `sample_user_data` - sample user registration data
- `registered_user` - pre-registered user in database
- `valid_access_token` - valid jwt token
- `expired_access_token` - expired jwt token

### API Fixtures
- `client` - fastapi test client

## Writing New Tests

1. Create test file with `test_` prefix
2. Import necessary fixtures from conftest.py
3. Use appropriate markers
4. Follow naming convention: `test_<what_is_being_tested>`

Example:
```python
import pytest

@pytest.mark.unit
@pytest.mark.auth
def test_password_hashing(auth_handler):
    password = "SecurePass123!"
    hashed = auth_handler.get_password_hash(password)
    assert hashed != password
```

## Coverage Goals

- Overall coverage: 80%+
- Critical paths (auth, database): 95%+
- API endpoints: 90%+

## Test Data

Test databases are automatically created in `tests/test_data/` and cleaned up after tests complete.


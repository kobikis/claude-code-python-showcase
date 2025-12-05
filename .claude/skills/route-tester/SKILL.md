# route-tester Skill

> **FastAPI Testing Patterns with pytest, AsyncClient, and Fixtures**
>
> This skill helps you write comprehensive tests for FastAPI endpoints using pytest-asyncio, fixtures, mocking, and authentication patterns.

---

## Quick Start Checklist

When testing FastAPI endpoints, ensure:

- [ ] **Test Structure**: Organized into `tests/unit/` and `tests/integration/`
- [ ] **Fixtures**: Essential fixtures in `tests/conftest.py` (db_session, client, auth_client)
- [ ] **Async Tests**: All tests marked with `@pytest.mark.asyncio`
- [ ] **AsyncClient**: Use `httpx.AsyncClient` for API testing (not TestClient)
- [ ] **Database Isolation**: Each test uses a fresh database session with rollback
- [ ] **Authentication**: Separate fixtures for authenticated/unauthenticated clients
- [ ] **Coverage**: Unit tests for services, integration tests for full endpoints
- [ ] **Parametrization**: Use `@pytest.mark.parametrize` for validation tests
- [ ] **Mocking**: Mock external services with `AsyncMock` and `@patch`
- [ ] **pytest.ini**: Configure test paths, markers, and asyncio_mode

---

## Core Testing Principles

### 1. Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_services.py     # Service layer tests
│   └── test_repositories.py # Repository tests
└── integration/
    └── test_api.py          # Full API integration tests
```

**Key Principle**: Unit tests for business logic, integration tests for HTTP endpoints.

### 2. Essential Fixtures (conftest.py)

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from app.main import app
from app.database import Base, get_db

# Test database engine (session-scoped)
@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

# Database session per test (function-scoped)
@pytest.fixture
async def db_session(test_engine):
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()  # Rollback after each test

# Test client with dependency override
@pytest.fixture
async def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

# Test user fixture
@pytest.fixture
async def test_user(db_session):
    user = User(
        email="test@example.com",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

# Authenticated client
@pytest.fixture
async def auth_client(client, test_user):
    token = create_access_token(test_user.id)
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client
```

**Key Points**:
- Use `AsyncClient` from httpx (not FastAPI's `TestClient`)
- Override `get_db` dependency to use test database
- Rollback after each test to ensure isolation
- Session-scoped engine, function-scoped sessions

---

## Testing Patterns

### Pattern 1: Unit Testing Services

```python
# tests/unit/test_post_service.py
import pytest
from app.services.post_service import PostService
from app.schemas.post import PostCreate

@pytest.mark.asyncio
async def test_create_post(db_session, test_user):
    service = PostService(db_session)

    post_data = PostCreate(
        title="Test Post",
        content="Test content"
    )

    post = await service.create_post(post_data, test_user.id)

    assert post.id is not None
    assert post.title == "Test Post"
    assert post.author_id == test_user.id

@pytest.mark.asyncio
async def test_get_post_not_found(db_session):
    service = PostService(db_session)

    with pytest.raises(NotFoundError):
        await service.get_post(999)
```

**When to Use**: Testing business logic without HTTP layer overhead.

### Pattern 2: Integration Testing Endpoints

```python
# tests/integration/test_posts_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_post_success(auth_client: AsyncClient):
    response = await auth_client.post(
        "/api/v1/posts",
        json={
            "title": "New Post",
            "content": "Post content"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Post"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_post_unauthorized(client: AsyncClient):
    response = await client.post(
        "/api/v1/posts",
        json={"title": "Test", "content": "Test"}
    )

    assert response.status_code == 401
```

**When to Use**: Testing full request/response cycle including validation, auth, and status codes.

### Pattern 3: Testing CRUD Operations

```python
@pytest.mark.asyncio
async def test_full_crud_lifecycle(auth_client: AsyncClient):
    # CREATE
    create_response = await auth_client.post(
        "/api/v1/posts",
        json={"title": "Test Post", "content": "Content"}
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]

    # READ
    get_response = await auth_client.get(f"/api/v1/posts/{post_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Test Post"

    # UPDATE
    update_response = await auth_client.patch(
        f"/api/v1/posts/{post_id}",
        json={"title": "Updated Title"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Title"

    # DELETE
    delete_response = await auth_client.delete(f"/api/v1/posts/{post_id}")
    assert delete_response.status_code == 204

    # Verify deletion
    verify_response = await auth_client.get(f"/api/v1/posts/{post_id}")
    assert verify_response.status_code == 404
```

**When to Use**: Testing complete resource lifecycle in one test.

### Pattern 4: Parametrized Tests

```python
@pytest.mark.parametrize("title,content,expected_status", [
    ("Valid Title", "Valid content", 201),
    ("", "Valid content", 422),  # Empty title
    ("Valid Title", "", 422),     # Empty content
    ("x" * 201, "Valid content", 422),  # Title too long
])
@pytest.mark.asyncio
async def test_create_post_validation(
    auth_client: AsyncClient,
    title: str,
    content: str,
    expected_status: int
):
    response = await auth_client.post(
        "/api/v1/posts",
        json={"title": title, "content": content}
    )
    assert response.status_code == expected_status
```

**When to Use**: Testing multiple validation scenarios efficiently.

### Pattern 5: Testing Pagination

```python
@pytest.mark.asyncio
async def test_pagination(auth_client: AsyncClient):
    # Create test data
    for i in range(15):
        await auth_client.post(
            "/api/v1/posts",
            json={"title": f"Post {i}", "content": "Content"}
        )

    # Test first page
    response = await auth_client.get(
        "/api/v1/posts?page=1&page_size=10"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == 15
    assert data["page"] == 1
    assert data["pages"] == 2

    # Test second page
    response2 = await auth_client.get(
        "/api/v1/posts?page=2&page_size=10"
    )
    assert len(response2.json()["items"]) == 5
```

**When to Use**: Testing list endpoints with pagination.

### Pattern 6: Mocking External Services

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch("app.services.email_service.send_email")
async def test_create_post_sends_notification(
    mock_send_email: AsyncMock,
    auth_client: AsyncClient
):
    mock_send_email.return_value = True

    response = await auth_client.post(
        "/api/v1/posts",
        json={"title": "Test", "content": "Content"}
    )

    assert response.status_code == 201
    mock_send_email.assert_called_once()

    # Verify call arguments
    call_args = mock_send_email.call_args
    assert "test@example.com" in call_args[0]
```

**When to Use**: Testing code that calls external APIs, email services, or third-party integrations.

### Pattern 7: Testing Authentication

```python
@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient):
    response = await client.get("/api/v1/profile")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token(client: AsyncClient):
    client.headers = {"Authorization": "Bearer invalid_token"}
    response = await client.get("/api/v1/profile")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
```

**When to Use**: Testing authentication and authorization logic.

### Pattern 8: Testing Error Handling

```python
@pytest.mark.asyncio
async def test_404_not_found(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/posts/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

@pytest.mark.asyncio
async def test_500_internal_error(auth_client: AsyncClient, monkeypatch):
    # Force an error in the service layer
    async def mock_error(*args, **kwargs):
        raise Exception("Database connection failed")

    monkeypatch.setattr(
        "app.services.post_service.PostService.get_post",
        mock_error
    )

    response = await auth_client.get("/api/v1/posts/1")
    assert response.status_code == 500
```

**When to Use**: Ensuring proper error responses and status codes.

---

## Configuration

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
addopts =
    -ra
    --strict-markers
    --cov=app
    --cov-branch
    --cov-report=term-missing
    --cov-report=html
asyncio_mode = auto
```

### pyproject.toml (Alternative)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
asyncio_mode = "auto"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests"
]
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/integration/test_posts_api.py

# Run specific test
pytest tests/integration/test_posts_api.py::test_create_post_success

# Run with verbose output
pytest -v

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run and stop at first failure
pytest -x

# Run last failed tests
pytest --lf

# Show print statements
pytest -s
```

---

## Common Testing Patterns

### Testing File Uploads

```python
@pytest.mark.asyncio
async def test_upload_file(auth_client: AsyncClient):
    files = {"file": ("test.txt", b"file content", "text/plain")}

    response = await auth_client.post(
        "/api/v1/upload",
        files=files
    )

    assert response.status_code == 201
    assert response.json()["filename"] == "test.txt"
```

### Testing Query Parameters

```python
@pytest.mark.asyncio
async def test_search_with_filters(auth_client: AsyncClient):
    response = await auth_client.get(
        "/api/v1/posts",
        params={
            "search": "test",
            "status": "published",
            "author_id": 1
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert all("test" in post["title"].lower() for post in data["items"])
```

### Testing Background Tasks

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch("app.tasks.process_post.delay")
async def test_background_task_triggered(
    mock_task: AsyncMock,
    auth_client: AsyncClient
):
    response = await auth_client.post(
        "/api/v1/posts",
        json={"title": "Test", "content": "Content"}
    )

    assert response.status_code == 201
    mock_task.assert_called_once_with(response.json()["id"])
```

### Testing Relationships

```python
@pytest.mark.asyncio
async def test_post_includes_author(auth_client: AsyncClient, test_user):
    response = await auth_client.post(
        "/api/v1/posts",
        json={"title": "Test", "content": "Content"}
    )

    post_id = response.json()["id"]

    get_response = await auth_client.get(f"/api/v1/posts/{post_id}")
    data = get_response.json()

    assert data["author"]["id"] == test_user.id
    assert data["author"]["email"] == test_user.email
```

---

## Best Practices

### 1. Fixture Organization
- **Session-scoped**: Database engine (expensive setup)
- **Function-scoped**: Database session, clients, test data (isolated)
- **Use dependency**: Fixtures should depend on other fixtures

### 2. Test Isolation
- Each test should be independent
- Use rollback after each test
- Don't rely on test execution order
- Clean up test data properly

### 3. Naming Conventions
- Test files: `test_*.py` or `*_test.py`
- Test functions: `test_*`
- Descriptive names: `test_create_post_with_invalid_data`

### 4. Assertions
- One logical assertion per test (or related assertions)
- Use descriptive error messages
- Test both success and failure cases

### 5. Coverage Goals
- Aim for 80%+ coverage
- Focus on critical business logic
- Don't test framework code
- Test edge cases and error conditions

### 6. Async Testing
- Always use `@pytest.mark.asyncio`
- Use `AsyncClient` not `TestClient`
- Await all async calls
- Configure `asyncio_mode = auto` in pytest.ini

---

## Common Pitfalls

### ❌ Using TestClient Instead of AsyncClient

```python
# DON'T
from fastapi.testclient import TestClient
client = TestClient(app)  # Blocks async code

# DO
from httpx import AsyncClient
async with AsyncClient(app=app, base_url="http://test") as client:
    response = await client.get("/api/v1/posts")
```

### ❌ Forgetting to Mark Tests as Async

```python
# DON'T
def test_get_posts(client):  # Missing @pytest.mark.asyncio
    response = await client.get("/api/v1/posts")

# DO
@pytest.mark.asyncio
async def test_get_posts(client):
    response = await client.get("/api/v1/posts")
```

### ❌ Not Cleaning Up After Tests

```python
# DON'T
@pytest.fixture
async def db_session(test_engine):
    async_session = sessionmaker(test_engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
    # Missing rollback/cleanup

# DO
@pytest.fixture
async def db_session(test_engine):
    async_session = sessionmaker(test_engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
        await session.rollback()  # Ensure isolation
```

---

## Additional Resources

For more advanced patterns, see:
- `/backend-dev-guidelines` skill for FastAPI architecture
- `pytest-asyncio` documentation: https://pytest-asyncio.readthedocs.io/
- `httpx` documentation: https://www.python-httpx.org/
- FastAPI testing guide: https://fastapi.tiangolo.com/tutorial/testing/

---

**Auto-activation**: This skill activates when:
- Keywords: test, pytest, fixture, mock, httpx, asyncclient
- File paths: `tests/**/*.py`, `test_*.py`, `*_test.py`
- Intent: Testing endpoints, writing tests, test setup

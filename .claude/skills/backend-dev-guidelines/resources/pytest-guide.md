# Testing with pytest - Complete Guide

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_services.py     # Service layer tests
│   └── test_repositories.py # Repository tests
└── integration/
    └── test_api.py          # Full API integration tests
```

## Essential Fixtures

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from app.main import app
from app.database import Base, get_db
from app.models import User, Post

# Test database engine
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

# Database session per test
@pytest.fixture
async def db_session(test_engine):
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()

# Test client
@pytest.fixture
async def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

# Test user
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

## Unit Tests - Service Layer

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

@pytest.mark.asyncio
async def test_duplicate_title_raises_error(db_session, test_user):
    service = PostService(db_session)

    post_data = PostCreate(title="Unique", content="Content")
    await service.create_post(post_data, test_user.id)

    # Try to create duplicate
    with pytest.raises(ValidationError, match="already exists"):
        await service.create_post(post_data, test_user.id)
```

## Integration Tests - API Endpoints

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

@pytest.mark.asyncio
async def test_get_posts_pagination(auth_client: AsyncClient, test_user):
    # Create multiple posts
    for i in range(15):
        await auth_client.post(
            "/api/v1/posts",
            json={"title": f"Post {i}", "content": "Content"}
        )

    # Test pagination
    response = await auth_client.get(
        "/api/v1/posts?page=1&page_size=10"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == 15

@pytest.mark.asyncio
async def test_update_post(auth_client: AsyncClient):
    # Create post
    create_response = await auth_client.post(
        "/api/v1/posts",
        json={"title": "Original", "content": "Content"}
    )
    post_id = create_response.json()["id"]

    # Update post
    update_response = await auth_client.patch(
        f"/api/v1/posts/{post_id}",
        json={"title": "Updated"}
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated"

@pytest.mark.asyncio
async def test_delete_post(auth_client: AsyncClient):
    # Create post
    create_response = await auth_client.post(
        "/api/v1/posts",
        json={"title": "To Delete", "content": "Content"}
    )
    post_id = create_response.json()["id"]

    # Delete post
    delete_response = await auth_client.delete(
        f"/api/v1/posts/{post_id}"
    )

    assert delete_response.status_code == 204

    # Verify deleted
    get_response = await auth_client.get(
        f"/api/v1/posts/{post_id}"
    )
    assert get_response.status_code == 404
```

## Parametrized Tests

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

## Mocking External Services

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
```

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

# Run only marked tests
pytest -m "integration"
```

## pytest.ini Configuration

```ini
# pytest.ini
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

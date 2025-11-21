# Backend Development Guidelines - FastAPI Edition

**Status**: ✅ Complete | **Applies to**: FastAPI with SQLAlchemy 2.0, Alembic, Pydantic v2, pytest-asyncio

## Quick Start Checklists

### Creating a New API Endpoint

- [ ] Define Pydantic schema for request/response
- [ ] Create service layer function with business logic
- [ ] Add route handler with proper decorators
- [ ] Include response models and status codes
- [ ] Add input validation and error handling
- [ ] Publish events to Kafka if applicable
- [ ] Write unit tests with pytest
- [ ] Add integration tests for happy path
- [ ] Document with docstrings and OpenAPI tags
- [ ] Test authentication/authorization if required

### Creating a Database Model

- [ ] Define SQLAlchemy 2.0 async model
- [ ] Add type hints for all columns
- [ ] Use mapped_column and Mapped types
- [ ] Create Alembic migration
- [ ] Add indexes for frequently queried fields
- [ ] Define relationships with proper lazy loading strategy
- [ ] Add __repr__ for debugging
- [ ] Create Pydantic v2 schema for request/response
- [ ] Write model tests
- [ ] Document model purpose and relationships

---

## Architecture Overview

```
┌─────────────────┐
│   HTTP Request  │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Router  │  ← FastAPI/Django views with decorators
    │  Handler │    Input validation, auth checks
    └────┬─────┘
         │
    ┌────▼──────┐
    │  Service  │  ← Business logic layer
    │   Layer   │    Transaction management
    └────┬──────┘
         │
    ┌────▼──────┐
    │Repository │  ← Data access layer
    │   Layer   │    SQLAlchemy/Django ORM
    └────┬──────┘
         │
    ┌────▼──────┐
    │ Database  │  ← PostgreSQL/MySQL/SQLite
    └───────────┘
```

---

## Core Principles

### 1. Layered Architecture (Mandatory)

Separate concerns into distinct layers:

**✅ DO:**
```python
# routes/posts.py (FastAPI example)
from fastapi import APIRouter, Depends
from services.post_service import PostService
from schemas.post import PostCreate, PostResponse

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostResponse, status_code=201)
async def create_post(
    post_data: PostCreate,
    service: PostService = Depends()
):
    """Create a new post."""
    return await service.create_post(post_data)

# services/post_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.post_repository import PostRepository
from schemas.post import PostCreate

class PostService:
    def __init__(self, db: AsyncSession):
        self.repo = PostRepository(db)

    async def create_post(self, data: PostCreate):
        # Business logic here
        if await self.repo.exists_by_title(data.title):
            raise ValueError("Post with this title already exists")
        return await self.repo.create(data)

# repositories/post_repository.py
from sqlalchemy import select
from models.post import Post

class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: PostCreate):
        post = Post(**data.model_dump())
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post
```

**❌ DON'T:**
```python
# All logic in route handler - NO!
@router.post("/posts")
async def create_post(data: PostCreate, db: Session = Depends(get_db)):
    # Business logic mixed with HTTP concerns
    existing = db.query(Post).filter_by(title=data.title).first()
    if existing:
        raise HTTPException(status_code=400, detail="Exists")
    post = Post(**data.dict())
    db.add(post)
    db.commit()
    return post
```

### 2. Type Hints Everywhere (Mandatory)

Use Python type hints for better IDE support and mypy checking:

**✅ DO:**
```python
from typing import List, Optional
from pydantic import BaseModel

class PostService:
    def __init__(self, repo: PostRepository) -> None:
        self.repo = repo

    async def get_posts(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[PostResponse]:
        posts = await self.repo.find_all(limit, offset)
        return [PostResponse.from_orm(p) for p in posts]

    async def get_post(self, post_id: int) -> Optional[PostResponse]:
        post = await self.repo.find_by_id(post_id)
        return PostResponse.from_orm(post) if post else None
```

**❌ DON'T:**
```python
# No type hints - harder to debug and maintain
async def get_posts(limit=10, offset=0):
    posts = await self.repo.find_all(limit, offset)
    return [PostResponse.from_orm(p) for p in posts]
```

### 3. Dependency Injection (Recommended)

Use FastAPI's dependency injection or similar patterns:

**✅ DO:**
```python
# dependencies.py
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

async def get_post_service(
    db: AsyncSession = Depends(get_db)
) -> PostService:
    return PostService(PostRepository(db))

# routes/posts.py
@router.get("/{post_id}")
async def get_post(
    post_id: int,
    service: PostService = Depends(get_post_service)
):
    return await service.get_post(post_id)
```

### 4. Pydantic v2 for Validation (Mandatory)

Use Pydantic v2 models for request/response validation:

**✅ DO:**
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    published: bool = False

    @validator("title")
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True  # Pydantic v2
        # orm_mode = True  # Pydantic v1
```

### 5. Database Migrations (Mandatory)

Always use Alembic (SQLAlchemy) or Django migrations:

**✅ DO:**
```bash
# Create migration after model changes
alembic revision --autogenerate -m "Add posts table"

# Review the generated migration file
# Edit if necessary (add indexes, constraints, etc.)

# Apply migration
alembic upgrade head
```

**Migration file example:**
```python
# alembic/versions/xxx_add_posts_table.py
def upgrade() -> None:
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_posts_user_id', 'posts', ['user_id'])

def downgrade() -> None:
    op.drop_index('ix_posts_user_id')
    op.drop_table('posts')
```

### 6. Error Handling (Mandatory)

Use proper exception handling and custom exceptions:

**✅ DO:**
```python
# exceptions.py
class NotFoundError(Exception):
    """Raised when resource not found"""
    pass

class ValidationError(Exception):
    """Raised when validation fails"""
    pass

# services/post_service.py
async def get_post(self, post_id: int) -> PostResponse:
    post = await self.repo.find_by_id(post_id)
    if not post:
        raise NotFoundError(f"Post {post_id} not found")
    return PostResponse.from_orm(post)

# routes/posts.py (FastAPI)
from fastapi import HTTPException

@router.get("/{post_id}")
async def get_post(post_id: int, service: PostService = Depends()):
    try:
        return await service.get_post(post_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
```

### 7. Testing with pytest (Mandatory)

Write tests for all business logic:

**✅ DO:**
```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from httpx import AsyncClient

@pytest.fixture
async def db_session():
    """Create test database session"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    await engine.dispose()

@pytest.fixture
async def client(db_session):
    """Create test client"""
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# tests/test_posts.py
@pytest.mark.asyncio
async def test_create_post(client: AsyncClient):
    response = await client.post(
        "/posts",
        json={"title": "Test", "content": "Content"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_post_not_found(client: AsyncClient):
    response = await client.get("/posts/999")
    assert response.status_code == 404
```

---

## Directory Structure

### FastAPI Project Structure

```
project_root/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Settings and configuration
│   ├── dependencies.py         # Dependency injection
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py            # Base model class
│   │   ├── post.py
│   │   └── user.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── post.py
│   │   ├── user.py
│   │   └── events.py          # Event schemas
│   ├── routes/                # API endpoints
│   │   ├── __init__.py
│   │   ├── posts.py
│   │   └── users.py
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── post_service.py
│   │   └── user_service.py
│   ├── repositories/          # Data access
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   ├── post_repository.py
│   │   └── user_repository.py
│   ├── kafka/                 # Kafka integration
│   │   ├── __init__.py
│   │   ├── producer.py        # Kafka producer
│   │   ├── consumer.py        # Kafka consumer
│   │   └── consumers_registry.py
│   ├── events/                # Event handlers
│   │   ├── __init__.py
│   │   └── handlers.py
│   ├── middleware/            # Custom middleware
│   │   └── error_handler.py
│   └── utils/                 # Utilities
│       ├── auth.py
│       └── pagination.py
├── alembic/                   # Database migrations
│   ├── versions/
│   └── env.py
├── tests/
│   ├── conftest.py
│   ├── test_posts.py
│   └── test_users.py
├── .env
├── alembic.ini
├── pyproject.toml
└── requirements.txt
```


---

## Anti-Patterns to Avoid

### ❌ God Service Classes

```python
# DON'T create services that do everything
class PostService:
    async def create_post(self, data): ...
    async def update_post(self, data): ...
    async def delete_post(self, id): ...
    async def send_email(self, email): ...  # Wrong service!
    async def process_payment(self, data): ...  # Wrong service!
    async def generate_report(self, filters): ...  # Wrong service!
```

### ❌ Raw SQL in Route Handlers

```python
# DON'T write SQL in controllers
@router.get("/posts")
async def get_posts(db: Session = Depends()):
    result = await db.execute("SELECT * FROM posts")  # NO!
    return result.fetchall()
```

### ❌ Missing Error Handling

```python
# DON'T ignore errors
@router.post("/posts")
async def create_post(data: PostCreate, service: PostService = Depends()):
    # What if this fails?
    return await service.create_post(data)
```

---

## Navigation Guide

For detailed information on specific topics, see the resource files:

| Topic | Resource File |
|-------|---------------|
| FastAPI patterns and best practices | `resources/fastapi-patterns.md` |
| Testing with pytest-asyncio | `resources/pytest-guide.md` |
| **Kafka event streaming** | **`resources/kafka-patterns.md`** |
| SQLAlchemy 2.0 async models | `resources/sqlalchemy-guide.md` |
| Alembic migrations | `resources/alembic-guide.md` |
| Authentication & authorization | `resources/auth-patterns.md` |
| Async/await patterns | `resources/async-patterns.md` |
| Database optimization | `resources/db-optimization.md` |
| Error handling & middleware | `resources/error-handling.md` |
| OpenAPI documentation | `resources/api-docs.md` |
| Background tasks | `resources/background-tasks.md` |
| Deployment (Uvicorn/Gunicorn) | `resources/deployment.md` |

---

## When to Use This Skill

Use this skill when:
- Creating new API endpoints
- Designing database models
- Setting up project structure
- Writing tests
- Handling errors
- Optimizing queries
- Adding authentication
- Implementing event-driven architecture with Kafka
- Publishing/consuming events

---

## FastAPI Quick Reference

### Complete Application Setup

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="My API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route with dependencies
@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
):
    post = await service.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post

# Include routers
app.include_router(posts.router, prefix="/api/v1/posts", tags=["posts"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
```

### Background Tasks

```python
from fastapi import BackgroundTasks

def send_email_notification(email: str, message: str):
    # Send email
    pass

@app.post("/posts")
async def create_post(
    post: PostCreate,
    background_tasks: BackgroundTasks,
    service: PostService = Depends()
):
    new_post = await service.create_post(post)
    background_tasks.add_task(send_email_notification, "admin@example.com", "New post")
    return new_post
```

---

## Summary

Follow these core principles:
1. ✅ Layered architecture (routes → services → repositories)
2. ✅ Type hints everywhere
3. ✅ Pydantic v2 for validation
4. ✅ Database migrations always (Alembic)
5. ✅ Comprehensive error handling
6. ✅ Test coverage with pytest-asyncio
7. ✅ Dependency injection with Depends()
8. ✅ Event-driven architecture with Kafka (when applicable)
9. ✅ Async/await throughout

These patterns ensure maintainable, scalable FastAPI backends.

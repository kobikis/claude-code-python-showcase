# FastAPI-Exclusive Focus

This showcase is **exclusively focused on FastAPI** - no Django, no Flask, just pure FastAPI best practices.

## Why FastAPI Only?

- **Modern async/await** patterns
- **Type hints everywhere** with Pydantic v2
- **Automatic API docs** with OpenAPI/Swagger
- **High performance** ASGI framework
- **Growing ecosystem** and community

## What's Included

### FastAPI-Specific Patterns

✅ **Async/Await Throughout**
- AsyncIO patterns
- SQLAlchemy 2.0 with async support
- AsyncClient for testing
- Background tasks

✅ **Pydantic v2 Validation**
- Request/response models
- Field validation
- Custom validators
- from_attributes configuration

✅ **Dependency Injection**
- Depends() patterns
- Service layer injection
- Database session management
- Current user dependencies

✅ **Router Organization**
- APIRouter patterns
- Prefix and tags
- Route grouping
- Include router setup

✅ **Kafka Event Streaming**
- aiokafka integration
- Producer/consumer patterns
- Event schemas with Pydantic
- CQRS and Event Sourcing
- Transactional outbox pattern
- Dead Letter Queue handling

✅ **Testing with pytest-asyncio**
- AsyncClient fixtures
- Database session fixtures
- Async test functions
- Mock async functions

### Core Stack

```python
fastapi==0.104+           # Web framework
sqlalchemy==2.0+          # ORM with async
alembic==1.13+            # Migrations
pydantic==2.0+            # Validation
aiokafka==0.10+           # Kafka with async
pytest-asyncio==0.23+     # Testing
httpx==0.25+              # Test client
uvicorn==0.24+            # ASGI server
```

## What's NOT Included

❌ Django patterns
❌ Flask patterns
❌ Sync SQLAlchemy
❌ Threading patterns
❌ WSGI deployment
❌ Template rendering (Jinja2)
❌ Form handling

## Skill Rules - FastAPI Keywords

The skill activation hook looks for these FastAPI-specific terms:

```json
{
  "keywords": [
    "fastapi",
    "endpoint",
    "router",
    "async",
    "await",
    "depends",
    "pydantic",
    "sqlalchemy",
    "alembic",
    "kafka",
    "producer",
    "consumer",
    "event",
    "uvicorn",
    "httpexception",
    "backgroundtasks"
  ]
}
```

## Directory Structure Patterns

FastAPI projects typically use:

```
app/
├── main.py              # FastAPI app instance
├── config.py            # Settings with BaseSettings
├── database.py          # AsyncEngine and AsyncSession
├── dependencies.py      # Depends() functions
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic models (including events)
├── routers/             # APIRouter instances
├── services/            # Business logic
├── repositories/        # Data access
├── kafka/               # Kafka producer/consumer
├── events/              # Event handlers
└── middleware/          # Custom middleware
```

## Example FastAPI Patterns

### 1. Async Route with Dependency Injection

```python
from fastapi import APIRouter, Depends, status
from app.schemas.post import PostCreate, PostResponse
from app.services.post_service import PostService
from app.dependencies import get_post_service, get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
):
    """Create a new post"""
    return await service.create_post(post_data, current_user.id)
```

### 2. Async Database Session

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("postgresql+asyncpg://...")
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
```

### 3. Pydantic v2 Schemas

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str

class PostResponse(PostCreate):
    id: int
    created_at: datetime
    author_id: int

    model_config = ConfigDict(from_attributes=True)
```

### 4. Testing with AsyncClient

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_post(auth_client: AsyncClient):
    response = await auth_client.post(
        "/api/v1/posts",
        json={"title": "Test", "content": "Content"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test"
```

## Async vs Sync Comparison

### ❌ Sync (NOT in this showcase)

```python
# Sync SQLAlchemy
def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()

# Sync route
@app.get("/posts/{post_id}")
def read_post(post_id: int, db: Session = Depends(get_db)):
    return get_post(db, post_id)
```

### ✅ Async (This showcase)

```python
# Async SQLAlchemy
async def get_post(db: AsyncSession, post_id: int):
    result = await db.execute(select(Post).where(Post.id == post_id))
    return result.scalar_one_or_none()

# Async route
@app.get("/posts/{post_id}")
async def read_post(post_id: int, db: AsyncSession = Depends(get_db)):
    return await get_post(db, post_id)
```

## Migration from Django/Flask

If you're migrating from Django or Flask:

### Django → FastAPI

- **Models**: SQLAlchemy instead of Django ORM
- **Views**: Async functions with @router decorators
- **Serializers**: Pydantic models
- **URL routing**: APIRouter with prefix/tags
- **Middleware**: Starlette middleware
- **Testing**: pytest + AsyncClient

### Flask → FastAPI

- **Routes**: @router decorators instead of @app.route
- **Request validation**: Pydantic models (automatic)
- **Async support**: Native async/await
- **Dependency injection**: Depends() system
- **Testing**: AsyncClient instead of test_client

## Performance Benefits

FastAPI's async nature provides:

- **Concurrent requests** without threads
- **Lower memory** usage
- **Better scalability** for I/O-bound operations
- **WebSocket support** out of the box
- **Background tasks** without Celery (for simple cases)
- **Efficient Kafka integration** with aiokafka
- **Event-driven microservices** with high throughput

## When to Use This Showcase

✅ **Use this showcase if you:**
- Are building a new FastAPI project
- Want async/await patterns
- Need high-performance APIs
- Value automatic API documentation
- Prefer type safety with Pydantic

❌ **Don't use this showcase if you:**
- Need Django admin panel
- Require Django ORM features
- Have existing Flask codebase
- Need synchronous-only patterns

## Resources

- **FastAPI docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **Pydantic v2**: https://docs.pydantic.dev/latest/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/

---

**Ready to start?** Follow `QUICKSTART.md` for FastAPI-optimized setup in 5 minutes!

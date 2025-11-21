# FastAPI Patterns and Best Practices

## Complete FastAPI Application Example

```python
# app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routes import posts, users
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(posts.router, prefix="/api/v1/posts", tags=["posts"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

@app.on_event("startup")
async def startup():
    # Initialize database, cache, etc.
    pass

@app.on_event("shutdown")
async def shutdown():
    # Cleanup
    pass
```

## Async SQLAlchemy with FastAPI

```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
```

## Response Models

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    published: Optional[bool] = None

class PostResponse(PostBase):
    id: int
    published: bool
    created_at: datetime
    author_id: int

    class Config:
        from_attributes = True

class PostListResponse(BaseModel):
    items: List[PostResponse]
    total: int
    page: int
    page_size: int
```

## Background Tasks

```python
from fastapi import BackgroundTasks

async def send_notification(email: str, message: str):
    # Send email asynchronously
    await email_service.send(email, message)

@router.post("/posts")
async def create_post(
    post: PostCreate,
    background_tasks: BackgroundTasks,
    service: PostService = Depends()
):
    new_post = await service.create_post(post)

    # Add background task
    background_tasks.add_task(
        send_notification,
        "admin@example.com",
        f"New post created: {new_post.title}"
    )

    return new_post
```

## File Uploads

```python
from fastapi import File, UploadFile
from typing import List

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Process file
    return {"filename": file.filename, "size": len(contents)}

@router.post("/upload-multiple")
async def upload_multiple(files: List[UploadFile] = File(...)):
    return [{"filename": f.filename} for f in files]
```

## Authentication with JWT

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)

    user = await user_service.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=401)
    return user
```

See also:
- `pytest-guide.md` for testing FastAPI apps
- `async-patterns.md` for async/await best practices
- `auth-patterns.md` for complete auth implementation

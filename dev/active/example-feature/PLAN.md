# Plan: User Post Management API

## Implementation Phases

### Phase 1: Database Setup (Risk: Low)
**Goal**: Create Post model and migration
**Duration**: 2-3 hours

#### Step 1: Create Post Model
Create `app/models/post.py`:
```python
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    published = Column(Boolean, default=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    author = relationship("User", back_populates="posts")
```

**Files affected**: `app/models/post.py` (new)
**Testing**: Model can be imported
**Rollback**: Delete file

#### Step 2: Update User Model
Add to `app/models/user.py`:
```python
from sqlalchemy.orm import relationship

# Add to User class:
posts = relationship("Post", back_populates="author")
```

**Files affected**: `app/models/user.py`
**Testing**: No import errors
**Rollback**: Remove relationship line

#### Step 3: Create Migration
```bash
alembic revision --autogenerate -m "Add posts table"
# Review generated migration
alembic upgrade head
```

**Files affected**: `alembic/versions/xxx_add_posts_table.py` (new)
**Testing**: Migration applies cleanly
**Rollback**: `alembic downgrade -1`

**Success Criteria**:
- [ ] Post model defined
- [ ] User relationship added
- [ ] Migration created and applied
- [ ] Can create Post instances in Python shell

---

### Phase 2: Schemas and Validation (Risk: Low)
**Goal**: Define Pydantic schemas for validation
**Duration**: 1 hour

#### Step 1: Create Post Schemas
Create `app/schemas/post.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)

class PostCreate(PostBase):
    published: bool = False

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    published: Optional[bool] = None

class PostResponse(PostBase):
    id: int
    published: bool
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int
    page: int
    page_size: int
```

**Files affected**: `app/schemas/post.py` (new)
**Testing**: Schemas validate correctly
**Rollback**: Delete file

**Success Criteria**:
- [ ] All schemas defined
- [ ] Validation rules work
- [ ] from_orm() works with model

---

### Phase 3: Repository Layer (Risk: Low)
**Goal**: Implement data access layer
**Duration**: 2 hours

#### Step 1: Create Post Repository
Create `app/repositories/post_repository.py`:
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from app.models.post import Post
from typing import List, Optional

class PostRepository(BaseRepository[Post]):
    def __init__(self, db: AsyncSession):
        super().__init__(Post, db)

    async def find_by_author(
        self,
        author_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[Post]:
        stmt = (
            select(Post)
            .where(Post.author_id == author_id)
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_published(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[Post]:
        stmt = (
            select(Post)
            .where(Post.published == True)
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_by_author(self, author_id: int) -> int:
        stmt = select(func.count()).select_from(Post).where(
            Post.author_id == author_id
        )
        result = await self.db.execute(stmt)
        return result.scalar()
```

**Files affected**: `app/repositories/post_repository.py` (new)
**Testing**: Unit tests for each method
**Rollback**: Delete file

**Success Criteria**:
- [ ] Repository inherits from BaseRepository
- [ ] Custom query methods implemented
- [ ] Unit tests pass

---

### Phase 4: Service Layer (Risk: Medium)
**Goal**: Implement business logic
**Duration**: 3 hours

#### Step 1: Create Post Service
Create `app/services/post_service.py`:
```python
from app.repositories.post_repository import PostRepository
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.models.post import Post
from app.exceptions import NotFoundError, UnauthorizedError

class PostService:
    def __init__(self, repo: PostRepository):
        self.repo = repo

    async def create_post(
        self,
        data: PostCreate,
        author_id: int
    ) -> PostResponse:
        post = Post(
            **data.model_dump(),
            author_id=author_id
        )
        created_post = await self.repo.create(post)
        return PostResponse.from_orm(created_post)

    async def get_post(
        self,
        post_id: int,
        current_user_id: Optional[int] = None
    ) -> PostResponse:
        post = await self.repo.find_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post {post_id} not found")

        # If not published, only author can see
        if not post.published and post.author_id != current_user_id:
            raise UnauthorizedError("Not authorized to view this post")

        return PostResponse.from_orm(post)

    async def update_post(
        self,
        post_id: int,
        data: PostUpdate,
        current_user_id: int
    ) -> PostResponse:
        post = await self.repo.find_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post {post_id} not found")

        if post.author_id != current_user_id:
            raise UnauthorizedError("Not authorized to update this post")

        updated_post = await self.repo.update(post, data.model_dump(exclude_unset=True))
        return PostResponse.from_orm(updated_post)

    async def delete_post(
        self,
        post_id: int,
        current_user_id: int
    ) -> None:
        post = await self.repo.find_by_id(post_id)
        if not post:
            raise NotFoundError(f"Post {post_id} not found")

        if post.author_id != current_user_id:
            raise UnauthorizedError("Not authorized to delete this post")

        await self.repo.delete(post)

    async def list_posts(
        self,
        current_user_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 10
    ) -> PostListResponse:
        offset = (page - 1) * page_size

        if current_user_id:
            # Show user's posts (published and draft)
            posts = await self.repo.find_by_author(
                current_user_id, page_size, offset
            )
            total = await self.repo.count_by_author(current_user_id)
        else:
            # Show only published posts
            posts = await self.repo.find_published(page_size, offset)
            total = await self.repo.count()

        return PostListResponse(
            items=[PostResponse.from_orm(p) for p in posts],
            total=total,
            page=page,
            page_size=page_size
        )
```

**Files affected**: `app/services/post_service.py` (new)
**Testing**: Comprehensive unit tests
**Rollback**: Delete file

**Success Criteria**:
- [ ] All CRUD operations implemented
- [ ] Authorization checks work
- [ ] Unit tests cover all methods
- [ ] Error handling works correctly

---

### Phase 5: API Routes (Risk: Medium)
**Goal**: Create FastAPI endpoints
**Duration**: 2-3 hours

#### Step 1: Create Dependency
Add to `app/dependencies.py`:
```python
from app.repositories.post_repository import PostRepository
from app.services.post_service import PostService

async def get_post_service(
    db: AsyncSession = Depends(get_db)
) -> PostService:
    repo = PostRepository(db)
    return PostService(repo)
```

#### Step 2: Create Routes
Create `app/routes/posts.py`:
```python
from fastapi import APIRouter, Depends, status
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostListResponse
from app.services.post_service import PostService
from app.dependencies import get_post_service, get_current_user
from app.models.user import User

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
):
    """Create a new post"""
    return await service.create_post(post_data, current_user.id)

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: PostService = Depends(get_post_service)
):
    """Get a post by ID"""
    user_id = current_user.id if current_user else None
    return await service.get_post(post_id, user_id)

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
):
    """Update a post"""
    return await service.update_post(post_id, post_data, current_user.id)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
):
    """Delete a post"""
    await service.delete_post(post_id, current_user.id)

@router.get("/", response_model=PostListResponse)
async def list_posts(
    page: int = 1,
    page_size: int = 10,
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: PostService = Depends(get_post_service)
):
    """List posts with pagination"""
    user_id = current_user.id if current_user else None
    return await service.list_posts(user_id, page, page_size)
```

#### Step 3: Register Router
Add to `app/main.py`:
```python
from app.routes import posts

app.include_router(posts.router, prefix="/api/v1")
```

**Files affected**:
- `app/dependencies.py` (modified)
- `app/routes/posts.py` (new)
- `app/main.py` (modified)

**Testing**: Integration tests for all endpoints
**Rollback**: Remove router registration, delete files

**Success Criteria**:
- [ ] All endpoints accessible
- [ ] Authentication works
- [ ] Authorization works
- [ ] Validation works
- [ ] Integration tests pass

---

### Phase 6: Testing (Risk: Low)
**Goal**: Comprehensive test coverage
**Duration**: 3 hours

#### Step 1: Service Unit Tests
Create `tests/unit/test_post_service.py` - test all service methods

#### Step 2: API Integration Tests
Create `tests/integration/test_posts_api.py` - test all endpoints

#### Step 3: Run Coverage
```bash
pytest --cov=app --cov-report=html
# Ensure > 80% coverage
```

**Success Criteria**:
- [ ] All service methods tested
- [ ] All endpoints tested
- [ ] Edge cases covered
- [ ] Coverage > 80%

---

## Testing Strategy

### Unit Tests
- Test service logic in isolation
- Mock repository methods
- Test authorization logic
- Test error conditions

### Integration Tests
- Test full API flow
- Use test database
- Test authentication
- Test all status codes

### Manual Testing
- Test in Postman/Insomnia
- Verify OpenAPI docs
- Test edge cases

## Rollback Strategy

Each phase is independent:
- Phase 1: `alembic downgrade -1`, delete model files
- Phase 2-6: Delete created files, revert modifications

## Timeline

- **Day 1**: Phases 1-3 (setup, schemas, repository)
- **Day 2**: Phases 4-5 (service, routes)
- **Day 3**: Phase 6 (testing, review)

## Technical Decisions

1. **Pagination**: Offset-based (simple, sufficient for now)
2. **Authorization**: Check in service layer (reusable)
3. **Filtering**: Published flag for public/private
4. **Caching**: Not implemented initially (add if needed)

## Deployment Checklist

- [ ] All tests pass
- [ ] Migration applied to staging
- [ ] Manual testing on staging
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Migration applied to production
- [ ] Monitoring alerts configured
- [ ] Verify in production

## Monitoring

- Response time < 200ms
- Error rate < 0.1%
- No 500 errors
- Database query performance

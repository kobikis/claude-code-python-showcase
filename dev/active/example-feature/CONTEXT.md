# Context: User Post Management API

## Current State
- FastAPI application with SQLAlchemy
- PostgreSQL database in production, SQLite for tests
- Authentication using JWT (already implemented)
- User model exists in `app/models/user.py`
- Repository pattern partially implemented
- Using Alembic for migrations

## Tech Stack
- **Framework**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0 with async support
- **Database**: PostgreSQL 15
- **Migration**: Alembic
- **Testing**: pytest with pytest-asyncio
- **Validation**: Pydantic v2

## Existing Project Structure
```
app/
├── main.py                    # Application entry point
├── config.py                  # Settings
├── database.py                # Database connection
├── models/
│   ├── base.py               # Base model
│   └── user.py               # User model (already exists)
├── schemas/
│   └── user.py               # User schemas
├── routes/
│   └── users.py              # User routes
├── services/
│   └── user_service.py       # User service
├── repositories/
│   └── base_repository.py    # Base repository pattern
└── dependencies.py           # FastAPI dependencies
```

## Relevant Files

### Models
- `app/models/base.py` - Base model with `id`, `created_at`, `updated_at`
- `app/models/user.py` - User model to reference for foreign keys

### Database
- `app/database.py` - Database session factory and engine
- `alembic/` - Migration directory
- `alembic.ini` - Alembic configuration

### Authentication
- `app/dependencies.py:get_current_user()` - Use this for auth
- `app/utils/auth.py` - JWT utilities

### Testing
- `tests/conftest.py` - Test fixtures (db_session, client, auth_client)
- `tests/unit/` - Unit tests location
- `tests/integration/` - Integration tests location

## Database Schema

### Existing Tables
```sql
users
├── id (INTEGER, PK)
├── email (VARCHAR, UNIQUE)
├── hashed_password (VARCHAR)
├── is_active (BOOLEAN)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

### Planned Posts Table
```sql
posts
├── id (INTEGER, PK)
├── title (VARCHAR(200))
├── content (TEXT)
├── published (BOOLEAN, default=False)
├── author_id (INTEGER, FK -> users.id)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

## Conventions

### Model Naming
- Singular names: `Post`, `User`
- Use `__tablename__` explicitly
- Inherit from `Base`

### Service Layer
- One service per model
- Services receive repository in constructor
- Services handle business logic
- Services raise custom exceptions

### Repository Layer
- Inherit from `BaseRepository`
- Methods: `create()`, `find_by_id()`, `find_all()`, `update()`, `delete()`
- Handle database operations only

### API Routes
- RESTful naming: `/posts`, `/posts/{id}`
- Use HTTP methods correctly (GET, POST, PUT, DELETE)
- Return appropriate status codes
- Use response_model for type safety

### Testing
- Use fixtures from `conftest.py`
- Unit tests for services
- Integration tests for routes
- Mock external services

## Dependencies to Install
None - all required packages already in `requirements.txt`

## Constraints
- Must maintain backward compatibility
- Database migrations must be reversible
- Tests must pass before merging
- Code coverage must stay above 80%
- Follow existing patterns in the codebase

## Related Code Patterns

### Example Service (from user_service.py)
```python
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user(self, user_id: int) -> UserResponse:
        user = await self.repo.find_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        return UserResponse.from_orm(user)
```

### Example Route (from users.py)
```python
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    return await service.get_user(user_id)
```

## Performance Considerations
- Add index on `author_id` for faster queries
- Use `select_related` for author when fetching posts
- Implement pagination for list endpoints
- Consider caching for published posts

## Security Considerations
- Validate user can only modify their own posts
- Sanitize content to prevent XSS
- Validate title length
- Rate limit endpoints

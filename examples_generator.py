"""
Examples Generator Module

Generates example implementation files aligned with the current skill set.
"""

from pathlib import Path


EXAMPLE_TEMPLATES = {
    "repository_pattern": '''"""
Repository Pattern Implementation

Data access abstraction following the patterns rule.
Encapsulates storage details behind a consistent interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Generic, TypeVar, Optional
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


@dataclass(frozen=True)
class Entity:
    """Base entity with common fields (immutable)."""

    id: UUID
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class User(Entity):
    """User entity."""

    email: str
    name: str
    is_active: bool = True


class Repository(ABC, Generic[T]):
    """Abstract repository interface.

    Defines standard CRUD operations that concrete implementations
    must provide. Business logic depends on this interface, not on
    the storage mechanism.
    """

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        """Retrieve all entities with pagination."""

    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> Optional[T]:
        """Retrieve a single entity by ID."""

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity and return it."""

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity and return the updated version."""

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by ID. Returns True if deleted."""


class InMemoryUserRepository(Repository[User]):
    """In-memory implementation for testing and prototyping.

    Uses immutable operations — never mutates existing data.
    """

    def __init__(self) -> None:
        self._store: dict[UUID, User] = {}

    async def find_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        users = sorted(self._store.values(), key=lambda u: u.created_at)
        return users[offset : offset + limit]

    async def find_by_id(self, entity_id: UUID) -> Optional[User]:
        return self._store.get(entity_id)

    async def create(self, entity: User) -> User:
        if entity.id in self._store:
            raise ValueError(f"User already exists: {entity.id}")

        now = datetime.utcnow()
        user = replace(entity, created_at=now, updated_at=now)
        # Create new dict instead of mutating
        self._store = {**self._store, user.id: user}
        logger.info("user_created", user_id=str(user.id), email=user.email)
        return user

    async def update(self, entity: User) -> User:
        if entity.id not in self._store:
            raise ValueError(f"User not found: {entity.id}")

        updated = replace(entity, updated_at=datetime.utcnow())
        self._store = {**self._store, updated.id: updated}
        logger.info("user_updated", user_id=str(updated.id))
        return updated

    async def delete(self, entity_id: UUID) -> bool:
        if entity_id not in self._store:
            return False

        self._store = {k: v for k, v in self._store.items() if k != entity_id}
        logger.info("user_deleted", user_id=str(entity_id))
        return True


# Factory for dependency injection
def create_user_repository() -> Repository[User]:
    """Create a user repository instance.

    In production, swap InMemoryUserRepository for a SQLAlchemy-backed
    implementation without changing business logic.
    """
    return InMemoryUserRepository()


async def example_usage():
    """Example demonstrating the repository pattern."""
    repo = create_user_repository()

    user = User(
        id=uuid4(),
        email="alice@example.com",
        name="Alice",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    created = await repo.create(user)
    print(f"Created: {created.name} ({created.email})")

    found = await repo.find_by_id(created.id)
    print(f"Found: {found}")

    updated = await repo.update(replace(created, name="Alice Smith"))
    print(f"Updated: {updated.name}")

    all_users = await repo.find_all()
    print(f"Total users: {len(all_users)}")
''',
    "pydantic_v2_models": '''"""
Pydantic v2 Model Patterns

Schema definitions following FastAPI-specialist patterns.
Demonstrates ConfigDict, field_validator, model_validator.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


class UserBase(BaseModel):
    """Shared user fields (immutable Pydantic model)."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "email": "alice@example.com",
                "name": "Alice Smith",
            }
        },
    )

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Name must not be empty or whitespace")
        return stripped


class UserCreate(UserBase):
    """Request schema for creating a user."""

    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Request schema for updating a user (all fields optional)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UserUpdate":
        if self.email is None and self.name is None:
            raise ValueError("At least one field must be provided for update")
        return self


class UserResponse(UserBase):
    """Response schema for a user."""

    id: UUID
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseModel):
    """Consistent API response envelope with pagination metadata."""

    model_config = ConfigDict(frozen=True)

    success: bool = True
    data: list[UserResponse]
    error: Optional[str] = None
    total: int
    page: int = Field(ge=1)
    limit: int = Field(ge=1, le=100)


class ErrorResponse(BaseModel):
    """Consistent error response envelope."""

    model_config = ConfigDict(frozen=True)

    success: bool = False
    data: None = None
    error: str
    detail: Optional[str] = None


# Example usage
def example_usage():
    """Demonstrate Pydantic v2 model usage."""
    # Create
    user_input = UserCreate(
        email="alice@example.com",
        name="Alice Smith",
        password="SecurePass1",
    )
    print(f"Valid input: {user_input.model_dump()}")

    # Response
    response = UserResponse(
        id=uuid4(),
        email=user_input.email,
        name=user_input.name,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    print(f"JSON: {response.model_dump_json()}")

    # Paginated
    paginated = PaginatedResponse(
        data=[response],
        total=1,
        page=1,
        limit=20,
    )
    print(f"Paginated: {paginated.model_dump()}")

    # JSON schema
    print(f"Schema: {UserCreate.model_json_schema()}")
''',
    "health_endpoints": '''"""
Health Check Endpoints

FastAPI health checks aligned with k8s-specialist patterns.
Supports Kubernetes liveness, readiness, and startup probes.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict

router = APIRouter(tags=["health"])


class HealthStatus(str, Enum):
    """Health check status values."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DependencyHealth(BaseModel):
    """Health status of a single dependency."""

    model_config = ConfigDict(frozen=True)

    name: str
    status: HealthStatus
    latency_ms: Optional[float] = None
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Comprehensive health check response."""

    model_config = ConfigDict(frozen=True)

    status: HealthStatus
    version: str
    uptime_seconds: float
    timestamp: str
    dependencies: list[DependencyHealth] = []


@dataclass(frozen=True)
class AppState:
    """Immutable application state for health checks."""

    start_time: datetime
    version: str
    ready: bool = False


# Module-level state (replaced atomically, never mutated)
_app_state = AppState(
    start_time=datetime.now(timezone.utc),
    version="0.1.0",
    ready=False,
)


def set_ready(ready: bool = True) -> None:
    """Mark the application as ready (atomic replacement)."""
    global _app_state
    _app_state = AppState(
        start_time=_app_state.start_time,
        version=_app_state.version,
        ready=ready,
    )


async def check_database() -> DependencyHealth:
    """Check database connectivity."""
    try:
        # Replace with actual DB ping
        return DependencyHealth(
            name="database",
            status=HealthStatus.HEALTHY,
            latency_ms=1.2,
        )
    except Exception as e:
        return DependencyHealth(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


async def check_redis() -> DependencyHealth:
    """Check Redis connectivity."""
    try:
        # Replace with actual Redis ping
        return DependencyHealth(
            name="redis",
            status=HealthStatus.HEALTHY,
            latency_ms=0.5,
        )
    except Exception as e:
        return DependencyHealth(
            name="redis",
            status=HealthStatus.UNHEALTHY,
            message=str(e),
        )


@router.get(
    "/healthz",
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Kubernetes liveness probe. Returns 200 if the process is alive.",
)
async def liveness() -> HealthResponse:
    """Liveness check — is the process running?"""
    now = datetime.now(timezone.utc)
    uptime = (now - _app_state.start_time).total_seconds()

    return HealthResponse(
        status=HealthStatus.HEALTHY,
        version=_app_state.version,
        uptime_seconds=uptime,
        timestamp=now.isoformat(),
    )


@router.get(
    "/readyz",
    response_model=HealthResponse,
    summary="Readiness probe",
    description="Kubernetes readiness probe. Returns 200 only when all dependencies are healthy.",
    responses={503: {"description": "Service not ready"}},
)
async def readiness():
    """Readiness check — can we serve traffic?"""
    now = datetime.now(timezone.utc)
    uptime = (now - _app_state.start_time).total_seconds()

    deps = [await check_database(), await check_redis()]

    all_healthy = all(d.status == HealthStatus.HEALTHY for d in deps)
    overall = HealthStatus.HEALTHY if (all_healthy and _app_state.ready) else HealthStatus.UNHEALTHY

    response = HealthResponse(
        status=overall,
        version=_app_state.version,
        uptime_seconds=uptime,
        timestamp=now.isoformat(),
        dependencies=deps,
    )

    if overall != HealthStatus.HEALTHY:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            content=response.model_dump(),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return response


@router.get(
    "/startupz",
    response_model=HealthResponse,
    summary="Startup probe",
    description="Kubernetes startup probe. Returns 200 once initial setup is complete.",
)
async def startup():
    """Startup check — has initialization completed?"""
    now = datetime.now(timezone.utc)
    uptime = (now - _app_state.start_time).total_seconds()

    overall = HealthStatus.HEALTHY if _app_state.ready else HealthStatus.UNHEALTHY

    response = HealthResponse(
        status=overall,
        version=_app_state.version,
        uptime_seconds=uptime,
        timestamp=now.isoformat(),
    )

    if overall != HealthStatus.HEALTHY:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            content=response.model_dump(),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return response
''',
    "async_service": '''"""
Async Service Pattern

Demonstrates async httpx client with structured logging,
aligned with async-python-patterns skill.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Optional

import httpx
import structlog

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class ServiceConfig:
    """Immutable service configuration."""

    base_url: str
    timeout_seconds: float = 30.0
    max_retries: int = 3
    max_connections: int = 100


@dataclass(frozen=True)
class ServiceResponse:
    """Immutable service response wrapper."""

    status_code: int
    data: Optional[dict[str, Any]]
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300


class AsyncHttpService:
    """Async HTTP service using httpx with structured logging.

    Features:
    - Connection pooling via httpx.AsyncClient
    - Automatic retries with exponential backoff
    - Structured logging for observability
    - Immutable response objects
    """

    def __init__(self, config: ServiceConfig) -> None:
        self._config = config
        self._client: Optional[httpx.AsyncClient] = None

    async def start(self) -> None:
        """Initialize the HTTP client with connection pooling."""
        if self._client is not None:
            return

        self._client = httpx.AsyncClient(
            base_url=self._config.base_url,
            timeout=httpx.Timeout(self._config.timeout_seconds),
            limits=httpx.Limits(
                max_connections=self._config.max_connections,
                max_keepalive_connections=20,
            ),
        )
        logger.info(
            "http_service_started",
            base_url=self._config.base_url,
        )

    async def stop(self) -> None:
        """Close the HTTP client gracefully."""
        if self._client is None:
            return

        await self._client.aclose()
        self._client = None
        logger.info("http_service_stopped")

    async def get(self, path: str, params: Optional[dict] = None) -> ServiceResponse:
        """Perform a GET request with retries."""
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json_data: Optional[dict] = None) -> ServiceResponse:
        """Perform a POST request with retries."""
        return await self._request("POST", path, json_data=json_data)

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> ServiceResponse:
        """Execute HTTP request with retry logic."""
        if self._client is None:
            raise RuntimeError("Service not started. Call start() first.")

        last_error: Optional[Exception] = None

        for attempt in range(1, self._config.max_retries + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=path,
                    params=params,
                    json=json_data,
                )

                data = None
                if response.headers.get("content-type", "").startswith("application/json"):
                    data = response.json()

                logger.info(
                    "http_request_completed",
                    method=method,
                    path=path,
                    status_code=response.status_code,
                    attempt=attempt,
                )

                return ServiceResponse(
                    status_code=response.status_code,
                    data=data,
                )

            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(
                    "http_request_timeout",
                    method=method,
                    path=path,
                    attempt=attempt,
                    max_retries=self._config.max_retries,
                )
            except httpx.HTTPError as e:
                last_error = e
                logger.warning(
                    "http_request_error",
                    method=method,
                    path=path,
                    error=str(e),
                    attempt=attempt,
                )

            if attempt < self._config.max_retries:
                delay = 2 ** (attempt - 1)
                await asyncio.sleep(delay)

        logger.error(
            "http_request_failed_all_retries",
            method=method,
            path=path,
            error=str(last_error),
        )

        return ServiceResponse(
            status_code=0,
            data=None,
            error=str(last_error) if last_error else "Unknown error",
        )


# Context manager for lifecycle management
class AsyncHttpServiceContext:
    """Async context manager for the HTTP service."""

    def __init__(self, config: ServiceConfig) -> None:
        self._service = AsyncHttpService(config)

    async def __aenter__(self) -> AsyncHttpService:
        await self._service.start()
        return self._service

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._service.stop()


async def example_usage():
    """Example demonstrating the async HTTP service."""
    config = ServiceConfig(
        base_url="https://jsonplaceholder.typicode.com",
        timeout_seconds=10.0,
        max_retries=3,
    )

    async with AsyncHttpServiceContext(config) as service:
        # GET request
        response = await service.get("/posts/1")
        if response.is_success:
            print(f"Post title: {response.data['title']}")

        # POST request
        response = await service.post(
            "/posts",
            json_data={"title": "New Post", "body": "Content", "userId": 1},
        )
        print(f"Created: status={response.status_code}")


if __name__ == "__main__":
    asyncio.run(example_usage())
''',
    "base_service": '''"""
Base Service Pattern

Abstract base service with structured logging and error handling.
Updated to use immutable patterns and modern Python.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


@dataclass(frozen=True)
class ServiceResult:
    """Immutable service execution result."""

    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: float = 0.0


class BaseService(ABC, Generic[T]):
    """Base service with observability wrapper.

    Features:
    - Structured logging with context
    - Duration tracking
    - Error handling with immutable results
    """

    def __init__(self, service_name: Optional[str] = None) -> None:
        self.service_name = service_name or self.__class__.__name__
        self.logger = logger.bind(service=self.service_name)

    @abstractmethod
    async def process(self, data: T, context: dict[str, Any]) -> dict[str, Any]:
        """Process business logic. Implemented by subclasses.

        Args:
            data: Input data (typed).
            context: Request context (user, trace_id, etc.).

        Returns:
            Result dictionary.
        """

    async def execute(
        self, data: T, context: Optional[dict[str, Any]] = None
    ) -> ServiceResult:
        """Execute service with observability wrapper.

        Handles logging, timing, and error capture. Returns an immutable
        ServiceResult instead of raising exceptions to callers.
        """
        ctx = {
            **(context or {}),
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
        }

        self.logger.info("service_execution_started", **ctx)

        import time

        start = time.monotonic()

        try:
            result = await self.process(data, ctx)
            duration_ms = (time.monotonic() - start) * 1000

            self.logger.info(
                "service_execution_completed",
                duration_ms=round(duration_ms, 2),
                **ctx,
            )

            return ServiceResult(
                success=True,
                data=result,
                duration_ms=round(duration_ms, 2),
            )

        except Exception as e:
            duration_ms = (time.monotonic() - start) * 1000

            self.logger.error(
                "service_execution_failed",
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2),
                **ctx,
            )

            return ServiceResult(
                success=False,
                error=str(e),
                duration_ms=round(duration_ms, 2),
            )


# Example implementation
class UserNotificationService(BaseService[dict[str, Any]]):
    """Service for sending user notifications."""

    def __init__(self) -> None:
        super().__init__(service_name="user_notification")

    async def process(
        self, data: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        user_id = data.get("user_id")
        message = data.get("message")

        if not user_id or not message:
            raise ValueError("user_id and message are required")

        # Simulate notification dispatch
        self.logger.info(
            "notification_sent",
            user_id=user_id,
            message_length=len(message),
        )

        return {
            "status": "sent",
            "user_id": user_id,
            "context_id": context.get("trace_id"),
        }


async def example_usage():
    """Example of using the base service pattern."""
    service = UserNotificationService()

    result = await service.execute(
        data={"user_id": "user-123", "message": "Welcome!"},
        context={"trace_id": "abc-456"},
    )

    if result.success:
        print(f"Success: {result.data}")
    else:
        print(f"Failed: {result.error}")

    print(f"Duration: {result.duration_ms}ms")
''',
}


def create_example(example_name: str, example_file: Path):
    """Create an example implementation file."""
    example_file.parent.mkdir(parents=True, exist_ok=True)

    content = EXAMPLE_TEMPLATES.get(
        example_name,
        f'"""\n{example_name.replace("_", " ").title()} Example\n\nExample implementation to be added.\n"""\n',
    )

    with open(example_file, "w") as f:
        f.write(content)

    # Create __init__.py in examples directory
    init_file = example_file.parent / "__init__.py"
    if not init_file.exists():
        with open(init_file, "w") as f:
            f.write('"""Claude Code pattern examples"""\n')

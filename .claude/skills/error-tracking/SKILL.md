# error-tracking Skill

> **Sentry Integration and Error Handling for FastAPI**
>
> This skill helps you implement comprehensive error tracking, logging, and exception handling using Sentry, structured logging, and FastAPI middleware patterns.

---

## Quick Start Checklist

When implementing error tracking, ensure:

- [ ] **Sentry Setup**: Initialize Sentry SDK with FastAPI integration
- [ ] **Environment Config**: Separate DSNs for dev/staging/production
- [ ] **Exception Middleware**: Global exception handler for all routes
- [ ] **Custom Exceptions**: Domain-specific exception classes
- [ ] **Error Responses**: Consistent error response format
- [ ] **Structured Logging**: Use structlog or Python logging properly
- [ ] **Context Capture**: Add user, request, and custom context to errors
- [ ] **Performance Monitoring**: Enable Sentry performance tracking
- [ ] **Local Development**: Disable or limit Sentry in local env
- [ ] **PII Filtering**: Scrub sensitive data before sending to Sentry

---

## Core Error Handling Principles

### 1. Sentry Installation and Setup

```bash
# Install dependencies
pip install sentry-sdk[fastapi]
```

```python
# app/core/sentry.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from app.core.config import settings

def init_sentry():
    """Initialize Sentry SDK with FastAPI integration"""
    if not settings.SENTRY_DSN:
        return  # Skip if no DSN configured

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,  # dev, staging, production
        release=settings.APP_VERSION,
        integrations=[
            FastApiIntegration(
                transaction_style="endpoint"  # Group by endpoint
            ),
            SqlalchemyIntegration(),
        ],
        # Performance monitoring
        traces_sample_rate=1.0 if settings.ENVIRONMENT == "production" else 0.1,
        # Error sampling
        sample_rate=1.0,
        # Send default PII (be careful with this)
        send_default_pii=False,
        # Max breadcrumbs to capture
        max_breadcrumbs=50,
        # Attach stack traces to messages
        attach_stacktrace=True,
        # Debug mode (verbose logging)
        debug=settings.DEBUG,
        # Before send hook for data scrubbing
        before_send=before_send_handler,
    )

def before_send_handler(event, hint):
    """Scrub sensitive data before sending to Sentry"""
    # Remove password fields
    if "request" in event:
        if "data" in event["request"]:
            data = event["request"]["data"]
            if isinstance(data, dict):
                for key in ["password", "token", "secret", "api_key"]:
                    if key in data:
                        data[key] = "[Filtered]"

    return event
```

### 2. Application Integration

```python
# app/main.py
from fastapi import FastAPI
from app.core.sentry import init_sentry
from app.middleware.error_handler import add_exception_handlers

# Initialize Sentry before creating app
init_sentry()

app = FastAPI(
    title="My API",
    version="1.0.0"
)

# Add exception handlers
add_exception_handlers(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### 3. Custom Exception Classes

```python
# app/exceptions.py
from fastapi import status

class AppException(Exception):
    """Base exception for all application errors"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: dict | None = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class NotFoundError(AppException):
    """Resource not found error"""
    def __init__(self, message: str = "Resource not found", details: dict | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details
        )

class ValidationError(AppException):
    """Validation error"""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )

class AuthenticationError(AppException):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR"
        )

class AuthorizationError(AppException):
    """Authorization error"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR"
        )

class ConflictError(AppException):
    """Conflict error (e.g., duplicate resource)"""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT_ERROR",
            details=details
        )

class ExternalServiceError(AppException):
    """External service error"""
    def __init__(self, message: str, service_name: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service_name}
        )
```

### 4. Exception Handlers Middleware

```python
# app/middleware/error_handler.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import sentry_sdk
from app.exceptions import AppException
from app.core.logging import logger

def add_exception_handlers(app: FastAPI):
    """Add exception handlers to FastAPI app"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handle custom application exceptions"""
        # Log the error
        logger.error(
            "Application error",
            error_code=exc.error_code,
            status_code=exc.status_code,
            message=exc.message,
            details=exc.details,
            path=request.url.path,
        )

        # Send to Sentry for 5xx errors
        if exc.status_code >= 500:
            sentry_sdk.capture_exception(exc)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors"""
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })

        logger.warning(
            "Validation error",
            path=request.url.path,
            errors=errors,
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": errors},
            }
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors"""
        logger.error(
            "Database integrity error",
            path=request.url.path,
            error=str(exc.orig),
        )

        # Send to Sentry
        sentry_sdk.capture_exception(exc)

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "INTEGRITY_ERROR",
                "message": "Database constraint violation",
                "details": {},
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Catch-all handler for unexpected errors"""
        logger.exception(
            "Unexpected error",
            path=request.url.path,
            error_type=type(exc).__name__,
        )

        # Send to Sentry
        sentry_sdk.capture_exception(exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {},
            }
        )
```

### 5. Adding Context to Errors

```python
# app/middleware/sentry_context.py
from fastapi import Request
import sentry_sdk

async def add_sentry_context(request: Request, call_next):
    """Add request and user context to Sentry"""
    # Add request context
    with sentry_sdk.configure_scope() as scope:
        scope.set_context("request", {
            "url": str(request.url),
            "method": request.method,
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
        })

        # Add user context if authenticated
        user = getattr(request.state, "user", None)
        if user:
            scope.set_user({
                "id": user.id,
                "email": user.email,
                "username": getattr(user, "username", None),
            })

        # Add custom tags
        scope.set_tag("environment", "production")
        scope.set_tag("service", "api")

    response = await call_next(request)
    return response

# Add to main.py
# app.middleware("http")(add_sentry_context)
```

---

## Structured Logging

### Using structlog

```bash
pip install structlog
```

```python
# app/core/logging.py
import structlog
import logging
from app.core.config import settings

def setup_logging():
    """Configure structured logging"""
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if not settings.DEBUG
            else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()
```

### Using in Code

```python
from app.core.logging import logger

# Basic logging
logger.info("User created", user_id=user.id, email=user.email)
logger.error("Failed to create user", email=email, error=str(e))

# With context
logger.bind(user_id=user.id)
logger.info("Order created", order_id=order.id)
logger.info("Payment processed", amount=100.0)
```

---

## Error Handling Patterns

### Pattern 1: Service Layer Error Handling

```python
# app/services/post_service.py
from app.exceptions import NotFoundError, ValidationError
from app.core.logging import logger

class PostService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_post(self, post_id: int) -> Post:
        """Get post by ID"""
        post = await self.db.get(Post, post_id)

        if not post:
            logger.warning("Post not found", post_id=post_id)
            raise NotFoundError(
                message=f"Post with ID {post_id} not found",
                details={"post_id": post_id}
            )

        return post

    async def create_post(self, post_data: PostCreate, user_id: int) -> Post:
        """Create new post"""
        try:
            # Check for duplicate
            existing = await self.db.execute(
                select(Post).where(Post.title == post_data.title)
            )
            if existing.scalar_one_or_none():
                raise ValidationError(
                    message="Post with this title already exists",
                    details={"title": post_data.title}
                )

            post = Post(**post_data.dict(), author_id=user_id)
            self.db.add(post)
            await self.db.commit()
            await self.db.refresh(post)

            logger.info("Post created", post_id=post.id, user_id=user_id)
            return post

        except ValidationError:
            raise  # Re-raise custom exceptions
        except Exception as e:
            logger.exception("Failed to create post", user_id=user_id)
            await self.db.rollback()
            raise
```

### Pattern 2: External API Error Handling

```python
# app/services/external_service.py
import httpx
from app.exceptions import ExternalServiceError
from app.core.logging import logger

class ExternalAPIService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch_data(self, resource_id: str):
        """Fetch data from external API"""
        try:
            response = await self.client.get(
                f"https://api.example.com/resource/{resource_id}"
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                "External API HTTP error",
                status_code=e.response.status_code,
                resource_id=resource_id,
            )
            raise ExternalServiceError(
                message=f"Failed to fetch resource: {e.response.status_code}",
                service_name="external_api"
            )

        except httpx.TimeoutException:
            logger.error("External API timeout", resource_id=resource_id)
            raise ExternalServiceError(
                message="Request to external API timed out",
                service_name="external_api"
            )

        except Exception as e:
            logger.exception("Unexpected external API error", resource_id=resource_id)
            raise ExternalServiceError(
                message="Failed to fetch resource from external API",
                service_name="external_api"
            )
```

### Pattern 3: Manual Error Capture

```python
import sentry_sdk

# Capture exception manually
try:
    risky_operation()
except Exception as e:
    sentry_sdk.capture_exception(e)
    # Handle gracefully
    return fallback_value()

# Capture message
sentry_sdk.capture_message("Something unusual happened", level="warning")

# Add breadcrumbs
sentry_sdk.add_breadcrumb(
    category="auth",
    message="User login attempt",
    level="info",
    data={"user_id": user.id}
)
```

### Pattern 4: Error Monitoring Endpoint

```python
# app/api/v1/monitoring.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/sentry-debug")
async def trigger_error():
    """Endpoint to test Sentry integration"""
    division_by_zero = 1 / 0  # This will trigger Sentry
```

---

## Configuration

### Environment Variables

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Sentry
    SENTRY_DSN: str | None = None
    ENVIRONMENT: str = "development"  # development, staging, production
    APP_VERSION: str = "1.0.0"

    # Logging
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

### .env Example

```bash
# Sentry
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
ENVIRONMENT=production
APP_VERSION=1.2.3

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

---

## Testing Error Handling

```python
# tests/test_error_handling.py
import pytest
from app.exceptions import NotFoundError, ValidationError

@pytest.mark.asyncio
async def test_not_found_error_response(client):
    response = await client.get("/api/v1/posts/999999")

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "NOT_FOUND"
    assert "message" in data
    assert "details" in data

@pytest.mark.asyncio
async def test_validation_error_response(auth_client):
    response = await auth_client.post(
        "/api/v1/posts",
        json={"title": ""}  # Invalid: empty title
    )

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "VALIDATION_ERROR"
    assert "errors" in data["details"]

@pytest.mark.asyncio
async def test_service_raises_custom_exception(db_session):
    service = PostService(db_session)

    with pytest.raises(NotFoundError) as exc_info:
        await service.get_post(999999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.error_code == "NOT_FOUND"
```

---

## Best Practices

### 1. Error Response Format
Always return consistent error responses:
```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable message",
  "details": {
    "field": "additional info"
  }
}
```

### 2. When to Send to Sentry
- ✅ 5xx errors (server errors)
- ✅ Unexpected exceptions
- ✅ External service failures
- ❌ 4xx errors (client errors) - usually don't need alerting
- ❌ Validation errors - these are expected

### 3. PII and Sensitive Data
- Filter passwords, tokens, API keys before sending
- Use `before_send` hook to scrub data
- Set `send_default_pii=False` unless necessary
- Review Sentry data regularly

### 4. Performance Monitoring
- Set appropriate `traces_sample_rate`
- Use transaction_style="endpoint" for better grouping
- Monitor database query performance
- Track external API calls

### 5. Error Context
- Always log before raising exceptions
- Include relevant IDs (user_id, resource_id, etc.)
- Add breadcrumbs for complex flows
- Set user context when authenticated

---

## Common Pitfalls

### ❌ Not Handling Database Rollback

```python
# DON'T - leaves transaction open
async def create_post(self, post_data):
    post = Post(**post_data.dict())
    self.db.add(post)
    await self.db.commit()  # May fail
    return post

# DO - handle rollback
async def create_post(self, post_data):
    try:
        post = Post(**post_data.dict())
        self.db.add(post)
        await self.db.commit()
        return post
    except Exception:
        await self.db.rollback()
        raise
```

### ❌ Exposing Internal Error Details

```python
# DON'T - exposes stack trace to client
raise HTTPException(status_code=500, detail=str(exception))

# DO - use generic message, log details
logger.exception("Internal error")
raise AppException("An error occurred", status_code=500)
```

### ❌ Not Using Custom Exception Classes

```python
# DON'T - hard to handle consistently
raise HTTPException(status_code=404, detail="Not found")

# DO - use custom exceptions
raise NotFoundError("Resource not found", details={"id": resource_id})
```

---

## Monitoring Checklist

After implementing error tracking:

- [ ] Verify Sentry receives errors in all environments
- [ ] Check that PII is filtered correctly
- [ ] Confirm user context is attached to errors
- [ ] Test error grouping and deduplication
- [ ] Set up alerts for critical errors
- [ ] Configure release tracking
- [ ] Enable performance monitoring
- [ ] Review and ignore noisy errors
- [ ] Set up error budgets and SLOs

---

## Additional Resources

- Sentry Python SDK: https://docs.sentry.io/platforms/python/
- Sentry FastAPI Integration: https://docs.sentry.io/platforms/python/guides/fastapi/
- structlog: https://www.structlog.org/
- FastAPI exception handlers: https://fastapi.tiangolo.com/tutorial/handling-errors/

---

**Auto-activation**: This skill activates when:
- Keywords: sentry, error, exception, logging, middleware, traceback
- File paths: `logging/**/*.py`, `errors/**/*.py`, `exceptions/**/*.py`, `middleware/**/*.py`
- Intent: Error tracking, exception handling, Sentry setup

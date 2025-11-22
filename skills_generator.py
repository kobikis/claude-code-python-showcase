"""
Skills Generator Module

Generates Claude Code skill files for various patterns.
"""

import json
from pathlib import Path
from typing import List


SKILL_TEMPLATES = {
    "webhook-security": {
        "description": "Webhook signature verification and security patterns",
        "keywords": ["signature", "verify", "hmac", "webhook security", "authentication", "replay attack"],
        "intent_patterns": [
            "(verify|validate|check).*?(signature|webhook|hmac)",
            "(secure|protect).*?webhook",
            "replay.*?attack",
            "(authenticate|auth).*?webhook"
        ],
        "file_paths": ["**/webhooks/**/*.py", "**/security/**/*.py", "**/api/**/*.py"],
        "content": """# Webhook Security Skill

## Overview

This skill provides patterns for securing webhook endpoints including signature verification,
replay attack prevention, and request validation.

## When to Use

- Adding webhook signature verification
- Implementing HMAC authentication
- Preventing replay attacks
- Validating webhook payloads

## Core Patterns

### 1. Signature Verification (HMAC-SHA256)

```python
import hmac
import hashlib
import time
from fastapi import HTTPException, Header, Request

class WebhookSignatureVerifier:
    def __init__(self, secret: str, tolerance_seconds: int = 300):
        self.secret = secret.encode()
        self.tolerance = tolerance_seconds

    def verify_signature(
        self,
        payload: bytes,
        signature_header: str,
        timestamp_header: str
    ) -> bool:
        # Validate timestamp (replay protection)
        try:
            timestamp = int(timestamp_header)
            current_time = int(time.time())
            if abs(current_time - timestamp) > self.tolerance:
                return False
        except (ValueError, TypeError):
            return False

        # Generate expected signature
        message = f"{timestamp}.{payload.decode()}"
        expected_sig = hmac.new(
            self.secret,
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        # Extract provided signature
        if not signature_header.startswith("v1="):
            return False
        provided_sig = signature_header[3:]

        # Timing-safe comparison
        return hmac.compare_digest(provided_sig, expected_sig)

# Usage in FastAPI
async def verify_webhook_signature(
    request: Request,
    x_signature: str = Header(..., alias="X-Webhook-Signature"),
    x_timestamp: str = Header(..., alias="X-Webhook-Timestamp")
):
    verifier = get_webhook_verifier()
    body = await request.body()

    if not verifier.verify_signature(body, x_signature, x_timestamp):
        raise HTTPException(status_code=401, detail="Invalid signature")

    return True

@router.post("/webhook", dependencies=[Depends(verify_webhook_signature)])
async def handle_webhook(payload: dict):
    # Signature already verified
    pass
```

### 2. Replay Attack Prevention

```python
from datetime import datetime, timedelta
import redis.asyncio as redis

class ReplayProtection:
    def __init__(self, redis_client: redis.Redis, window_minutes: int = 5):
        self.redis = redis_client
        self.window = window_minutes * 60

    async def is_replay(self, request_id: str, timestamp: int) -> bool:
        # Check if request ID seen before
        key = f"webhook:seen:{request_id}"
        if await self.redis.exists(key):
            return True

        # Mark as seen with expiry
        await self.redis.setex(key, self.window, "1")
        return False
```

### 3. IP Allowlisting

```python
from fastapi import Request
from ipaddress import ip_address, ip_network

class IPAllowlist:
    def __init__(self, allowed_ranges: List[str]):
        self.allowed = [ip_network(r) for r in allowed_ranges]

    def is_allowed(self, client_ip: str) -> bool:
        ip = ip_address(client_ip)
        return any(ip in network for network in self.allowed)

# Middleware
async def verify_ip_allowlist(request: Request):
    allowlist = get_ip_allowlist()
    client_ip = request.client.host

    if not allowlist.is_allowed(client_ip):
        raise HTTPException(status_code=403, detail="IP not allowed")
```

## Testing Patterns

```python
import pytest
from freezegun import freeze_time

def test_signature_verification():
    verifier = WebhookSignatureVerifier(secret="test_secret")

    payload = b'{"event": "test"}'
    timestamp = str(int(time.time()))

    # Generate valid signature
    signature = verifier.generate_signature(payload, timestamp)

    # Should succeed
    assert verifier.verify_signature(payload, signature, timestamp)

    # Should fail with wrong signature
    assert not verifier.verify_signature(payload, "v1=invalid", timestamp)

@freeze_time("2024-01-01 12:00:00")
def test_replay_protection():
    # Test timestamp validation
    verifier = WebhookSignatureVerifier(secret="test", tolerance_seconds=300)

    old_timestamp = str(int(time.time()) - 400)  # 400 seconds ago
    assert not verifier.verify_signature(b"test", "v1=sig", old_timestamp)
```

## Security Checklist

- [ ] Implement HMAC signature verification
- [ ] Use timing-safe comparison (hmac.compare_digest)
- [ ] Validate timestamps to prevent replay attacks
- [ ] Store webhook secrets securely (env vars, secrets manager)
- [ ] Log failed verification attempts
- [ ] Implement rate limiting on webhook endpoints
- [ ] Use HTTPS only
- [ ] Validate payload schema
- [ ] Consider IP allowlisting for known providers

## Common Webhook Providers

### Stripe
- Header: `Stripe-Signature`
- Algorithm: HMAC-SHA256
- Format: `t=<timestamp>,v1=<signature>`

### Twilio
- Header: `X-Twilio-Signature`
- Algorithm: HMAC-SHA1
- Includes full URL in signature

### GitHub
- Header: `X-Hub-Signature-256`
- Algorithm: HMAC-SHA256
- Format: `sha256=<signature>`

## Resources

- [OWASP Webhook Security](https://cheatsheetseries.owasp.org/cheatsheets/Webhook_Security_Cheat_Sheet.html)
- [Stripe Webhook Signatures](https://stripe.com/docs/webhooks/signatures)
"""
    },

    "api-security": {
        "description": "API authentication, authorization, and rate limiting",
        "keywords": ["auth", "jwt", "api key", "rate limit", "throttle", "bearer", "oauth2"],
        "intent_patterns": [
            "(add|implement|setup).*?(auth|authentication|authorization)",
            "(rate|request).*?(limit|throttle)",
            "(api|bearer).*?key",
            "jwt.*?token"
        ],
        "file_paths": ["**/auth/**/*.py", "**/security/**/*.py", "**/middleware/**/*.py"],
        "content": """# API Security Skill

## Overview

Comprehensive patterns for API authentication, authorization, and rate limiting in FastAPI.

## Patterns

### 1. API Key Authentication

```python
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    # In production, check against database or secret manager
    valid_keys = get_valid_api_keys()

    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return api_key

# Usage
@router.get("/protected", dependencies=[Depends(verify_api_key)])
async def protected_endpoint():
    return {"message": "Authenticated"}
```

### 2. JWT Authentication

```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

class JWTHandler:
    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm

    def create_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, self.secret, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

# Dependency
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    jwt_handler = get_jwt_handler()
    payload = jwt_handler.verify_token(token.credentials)
    return payload
```

### 3. Rate Limiting (Redis + Sliding Window)

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Usage
@app.get("/limited")
@limiter.limit("5/minute")
async def limited_endpoint(request: Request):
    return {"message": "Rate limited endpoint"}

# Per-user rate limiting
def get_user_identifier(request: Request):
    # Extract from API key or JWT
    api_key = request.headers.get("X-API-Key")
    return api_key or get_remote_address(request)

user_limiter = Limiter(key_func=get_user_identifier)

@app.post("/webhook")
@user_limiter.limit("100/hour")
async def webhook_handler(request: Request):
    pass
```

### 4. Permission-Based Authorization

```python
from enum import Enum
from functools import wraps

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

def require_permissions(*required_permissions: Permission):
    async def dependency(current_user: dict = Depends(get_current_user)):
        user_permissions = set(current_user.get("permissions", []))
        required = set(required_permissions)

        if not required.issubset(user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return current_user

    return dependency

# Usage
@router.post("/admin", dependencies=[Depends(require_permissions(Permission.ADMIN))])
async def admin_only():
    return {"message": "Admin access"}
```

## Best Practices

1. **Never** log API keys or tokens
2. Use HTTPS only in production
3. Implement token refresh mechanism
4. Set appropriate rate limits per endpoint
5. Use short-lived tokens (1-24 hours)
6. Store secrets in environment variables or secret managers
7. Implement CORS properly
8. Add security headers (HSTS, CSP, X-Frame-Options)

## Testing

```python
def test_api_key_authentication():
    response = client.get("/protected", headers={"X-API-Key": "invalid"})
    assert response.status_code == 401

def test_rate_limiting():
    for _ in range(6):  # Limit is 5/minute
        response = client.get("/limited")

    assert response.status_code == 429  # Too Many Requests
```
"""
    },

    "resilience-patterns": {
        "description": "Circuit breakers, retries, and resilience patterns",
        "keywords": ["circuit breaker", "retry", "backoff", "dlq", "dead letter", "idempotent", "timeout"],
        "intent_patterns": [
            "(add|implement).*?(circuit breaker|retry|backoff)",
            "(dead letter|dlq).*?queue",
            "idempotent.*?(key|pattern)",
            "(handle|manage).*?(failure|timeout)"
        ],
        "file_paths": ["**/infrastructure/**/*.py", "**/resilience/**/*.py"],
        "content": """# Resilience Patterns Skill

## Overview

Production-ready resilience patterns including circuit breakers, retry logic,
idempotency, and dead letter queues.

## Patterns

### 1. Circuit Breaker

```python
import asyncio
import time
from enum import Enum
from dataclasses import dataclass

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: int = 60

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self._lock = asyncio.Lock()

    async def call(self, func, *args, **kwargs):
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            await self.record_success()
            return result
        except Exception as e:
            await self.record_failure()
            raise

    async def record_success(self):
        async with self._lock:
            self.failure_count = 0
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.success_count = 0

    async def record_failure(self):
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
```

### 2. Retry with Exponential Backoff

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(TransientError),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
async def call_with_retry(func, *args, **kwargs):
    return await func(*args, **kwargs)

# With jitter to prevent thundering herd
import random

def exponential_backoff_with_jitter(attempt: int, base: float = 1.0, max_delay: float = 60.0):
    delay = min(base * (2 ** attempt), max_delay)
    jitter = random.uniform(0, delay * 0.1)
    return delay + jitter
```

### 3. Idempotency

```python
import hashlib
import json
from typing import Optional

class IdempotencyStore:
    def __init__(self, redis_client, ttl_seconds: int = 3600):
        self.redis = redis_client
        self.ttl = ttl_seconds

    def _generate_key(self, payload: dict, headers: dict) -> str:
        signature = json.dumps(payload, sort_keys=True)
        timestamp = headers.get('X-Webhook-Timestamp', '')
        combined = f"{signature}:{timestamp}"
        return hashlib.sha256(combined.encode()).hexdigest()

    async def is_duplicate(self, idempotency_key: str) -> bool:
        return await self.redis.exists(f"idempotent:{idempotency_key}")

    async def mark_processed(self, idempotency_key: str, result: dict):
        await self.redis.setex(
            f"idempotent:{idempotency_key}",
            self.ttl,
            json.dumps(result)
        )

    async def get_cached_result(self, idempotency_key: str) -> Optional[dict]:
        value = await self.redis.get(f"idempotent:{idempotency_key}")
        return json.loads(value) if value else None

# Middleware
from starlette.middleware.base import BaseHTTPMiddleware

class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in ["POST", "PUT", "PATCH"]:
            return await call_next(request)

        store = get_idempotency_store()
        body = await request.body()
        idempotency_key = store._generate_key(
            json.loads(body) if body else {},
            dict(request.headers)
        )

        if await store.is_duplicate(idempotency_key):
            cached_result = await store.get_cached_result(idempotency_key)
            if cached_result:
                return JSONResponse(
                    content=cached_result,
                    headers={"X-Idempotent-Replay": "true"}
                )

        response = await call_next(request)

        if 200 <= response.status_code < 300:
            await store.mark_processed(idempotency_key, {"status": "success"})

        return response
```

### 4. Dead Letter Queue Pattern

```python
class EventPublisher:
    def __init__(self, producer, dlq_topic: str):
        self.producer = producer
        self.dlq_topic = dlq_topic

    async def publish_with_dlq(self, topic: str, event: dict, context: dict):
        try:
            await self.producer.send_and_wait(
                topic=topic,
                value=json.dumps(event).encode('utf-8'),
                headers=[(k, str(v).encode()) for k, v in context.items()]
            )
        except Exception as e:
            # Send to DLQ with error information
            dlq_event = {
                "original_event": event,
                "original_topic": topic,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "context": context
            }

            await self.producer.send_and_wait(
                topic=self.dlq_topic,
                value=json.dumps(dlq_event).encode('utf-8'),
                headers=[("error_type", type(e).__name__.encode())]
            )

            raise
```

## Best Practices

1. Use circuit breakers for all external dependencies
2. Add retry logic with exponential backoff and jitter
3. Implement idempotency for all non-GET operations
4. Use DLQ for messages that consistently fail
5. Set appropriate timeouts for all operations
6. Monitor circuit breaker state transitions
7. Log all retry attempts
8. Test failure scenarios

## Metrics to Track

- Circuit breaker state (closed/open/half-open)
- Retry success/failure rates
- Idempotent cache hit rate
- DLQ message count
- Operation timeouts
"""
    },
}


def create_skill(skill_name: str, skill_dir: Path):
    """Create a skill directory with SKILL.md"""
    skill_dir.mkdir(parents=True, exist_ok=True)

    template = SKILL_TEMPLATES.get(skill_name, {
        "content": f"# {skill_name.replace('-', ' ').title()} Skill\n\nContent to be added."
    })

    # Create main SKILL.md
    skill_file = skill_dir / "SKILL.md"
    with open(skill_file, 'w') as f:
        f.write(template.get("content", ""))

    # Create resources directory
    resources_dir = skill_dir / "resources"
    resources_dir.mkdir(exist_ok=True)

    # Create a sample resource file
    resource_file = resources_dir / "examples.md"
    with open(resource_file, 'w') as f:
        f.write(f"# {skill_name} Examples\n\nDetailed examples and use cases.\n")


def generate_skill_rules(skill_names: List[str], rules_file: Path):
    """Generate or update skill-rules.json"""

    rules = {
        "version": "1.0",
        "description": "Skill activation rules - auto-generated",
        "skills": []
    }

    # Add existing skills if file exists
    if rules_file.exists():
        with open(rules_file, 'r') as f:
            existing_rules = json.load(f)
            rules["skills"] = existing_rules.get("skills", [])

    # Add new skills
    for skill_name in skill_names:
        # Check if already exists
        if any(s["name"] == skill_name for s in rules["skills"]):
            continue

        template = SKILL_TEMPLATES.get(skill_name, {})

        skill_rule = {
            "name": skill_name,
            "type": "suggest",
            "priority": "high",
            "description": template.get("description", ""),
            "keywords": template.get("keywords", []),
            "intentPatterns": template.get("intent_patterns", []),
            "filePaths": template.get("file_paths", []),
            "message": f"💡 Consider using the `/{skill_name}` skill for this task."
        }

        rules["skills"].append(skill_rule)

    # Add global settings
    rules["globalSettings"] = {
        "enableSkillSuggestions": True,
        "maxSuggestionsPerPrompt": 2,
        "priorityOrder": ["critical", "high", "medium", "low"]
    }

    # Write to file
    with open(rules_file, 'w') as f:
        json.dump(rules, f, indent=2)

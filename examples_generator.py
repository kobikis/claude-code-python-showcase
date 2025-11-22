"""
Examples Generator Module

Generates example implementation files for common patterns.
"""

from pathlib import Path


EXAMPLE_TEMPLATES = {
    "circuit_breaker": '''"""
Circuit Breaker Pattern Implementation

Production-ready circuit breaker for protecting external dependencies.
"""

import asyncio
import time
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes in half-open to close
    timeout: int = 60  # Seconds before trying half-open
    name: str = "default"


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker for external dependencies.

    Usage:
        circuit_breaker = CircuitBreaker(config)

        # Async function
        result = await circuit_breaker.call(async_function, arg1, arg2)

        # Manual control
        await circuit_breaker.record_success()
        await circuit_breaker.record_failure()
    """

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_state_change = time.time()
        self._lock = asyncio.Lock()

        logger.info(
            "circuit_breaker_initialized",
            name=config.name,
            failure_threshold=config.failure_threshold,
            timeout=config.timeout
        )

    @property
    def is_open(self) -> bool:
        """Check if circuit is open"""
        return self.state == CircuitState.OPEN

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to(CircuitState.HALF_OPEN)
                    logger.info(
                        "circuit_breaker_half_open",
                        name=self.config.name
                    )
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker {self.config.name} is OPEN"
                    )

        try:
            result = await func(*args, **kwargs)
            await self.record_success()
            return result
        except Exception as e:
            await self.record_failure()
            logger.error(
                "circuit_breaker_call_failed",
                name=self.config.name,
                error=str(e)
            )
            raise

    async def record_success(self):
        """Record successful operation"""
        async with self._lock:
            self.failure_count = 0

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                logger.info(
                    "circuit_breaker_success_in_half_open",
                    name=self.config.name,
                    success_count=self.success_count,
                    threshold=self.config.success_threshold
                )

                if self.success_count >= self.config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
                    self.success_count = 0
                    logger.info(
                        "circuit_breaker_closed",
                        name=self.config.name
                    )

    async def record_failure(self):
        """Record failed operation"""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            logger.warning(
                "circuit_breaker_failure",
                name=self.config.name,
                failure_count=self.failure_count,
                threshold=self.config.failure_threshold
            )

            if self.failure_count >= self.config.failure_threshold:
                self._transition_to(CircuitState.OPEN)
                self.success_count = 0
                logger.error(
                    "circuit_breaker_opened",
                    name=self.config.name,
                    failures=self.failure_count
                )

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try half-open"""
        if not self.last_failure_time:
            return False

        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.config.timeout

    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state"""
        old_state = self.state
        self.state = new_state
        self.last_state_change = time.time()

        logger.info(
            "circuit_breaker_state_transition",
            name=self.config.name,
            from_state=old_state.value,
            to_state=new_state.value
        )

    def get_state_info(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "name": self.config.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "time_in_current_state": time.time() - self.last_state_change
        }


# Example usage in dependency injection
from functools import lru_cache

@lru_cache()
def get_kafka_circuit_breaker() -> CircuitBreaker:
    """Get circuit breaker for Kafka"""
    return CircuitBreaker(CircuitBreakerConfig(
        name="kafka",
        failure_threshold=5,
        success_threshold=2,
        timeout=60
    ))


@lru_cache()
def get_http_circuit_breaker() -> CircuitBreaker:
    """Get circuit breaker for HTTP calls"""
    return CircuitBreaker(CircuitBreakerConfig(
        name="external_http",
        failure_threshold=3,
        success_threshold=2,
        timeout=30
    ))
''',

    "idempotency": '''"""
Idempotency Pattern Implementation

Redis-backed idempotency for webhook handlers and critical operations.
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Any, Callable
import redis.asyncio as redis
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)


class IdempotencyStore:
    """
    Redis-backed idempotency key storage.

    Stores request signatures and cached responses to prevent duplicate processing.
    """

    def __init__(self, redis_client: redis.Redis, ttl_seconds: int = 3600):
        self.redis = redis_client
        self.ttl = ttl_seconds

    def _generate_key(self, payload: dict, headers: dict) -> str:
        """
        Generate deterministic idempotency key from payload and headers.

        Args:
            payload: Request payload dictionary
            headers: Request headers dictionary

        Returns:
            SHA256 hash of combined payload and timestamp
        """
        # Combine payload + timestamp for uniqueness
        signature = json.dumps(payload, sort_keys=True)
        timestamp = headers.get('X-Webhook-Timestamp', '')
        combined = f"{signature}:{timestamp}"

        return hashlib.sha256(combined.encode()).hexdigest()

    async def is_duplicate(self, idempotency_key: str) -> bool:
        """Check if request with this key was already processed"""
        exists = await self.redis.exists(f"idempotent:{idempotency_key}")
        if exists:
            logger.info(
                "idempotency_duplicate_detected",
                key=idempotency_key[:8]
            )
        return bool(exists)

    async def mark_processed(
        self,
        idempotency_key: str,
        result: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Mark request as processed and cache result.

        Args:
            idempotency_key: Unique key for the request
            result: Result to cache
            ttl: Optional TTL override (seconds)
        """
        ttl = ttl or self.ttl

        await self.redis.setex(
            f"idempotent:{idempotency_key}",
            ttl,
            json.dumps({
                "result": result,
                "processed_at": datetime.utcnow().isoformat()
            })
        )

        logger.info(
            "idempotency_marked_processed",
            key=idempotency_key[:8],
            ttl=ttl
        )

    async def get_cached_result(self, idempotency_key: str) -> Optional[dict]:
        """Retrieve cached result for duplicate request"""
        value = await self.redis.get(f"idempotent:{idempotency_key}")

        if value:
            cached = json.loads(value)
            logger.info(
                "idempotency_cache_hit",
                key=idempotency_key[:8],
                age_seconds=(
                    datetime.utcnow() -
                    datetime.fromisoformat(cached["processed_at"])
                ).total_seconds()
            )
            return cached.get("result")

        return None

    async def delete_key(self, idempotency_key: str):
        """Delete idempotency key (for testing or manual cleanup)"""
        await self.redis.delete(f"idempotent:{idempotency_key}")


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic idempotency handling.

    Usage:
        app.add_middleware(IdempotencyMiddleware, idempotency_store=store)
    """

    def __init__(self, app, idempotency_store: IdempotencyStore):
        super().__init__(app)
        self.store = idempotency_store

    async def dispatch(self, request: Request, call_next):
        # Only apply to POST/PUT/PATCH
        if request.method not in ["POST", "PUT", "PATCH"]:
            return await call_next(request)

        # Check for explicit idempotency key header
        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            # Generate from payload
            body = await request.body()

            try:
                payload = json.loads(body) if body else {}
            except json.JSONDecodeError:
                payload = {}

            idempotency_key = self.store._generate_key(
                payload,
                dict(request.headers)
            )

        # Check if already processed
        if await self.store.is_duplicate(idempotency_key):
            cached_result = await self.store.get_cached_result(idempotency_key)

            if cached_result:
                return JSONResponse(
                    content=cached_result,
                    status_code=200,
                    headers={
                        "X-Idempotent-Replay": "true",
                        "X-Idempotency-Key": idempotency_key[:8]
                    }
                )

        # Process request
        response = await call_next(request)

        # Cache successful responses
        if 200 <= response.status_code < 300:
            # Note: This is simplified - in production you'd need to read response body
            await self.store.mark_processed(
                idempotency_key,
                {"status": "success", "status_code": response.status_code}
            )

        return response


# Decorator for manual idempotency handling
def idempotent(ttl_seconds: int = 3600):
    """
    Decorator for idempotent operations.

    Usage:
        @idempotent(ttl_seconds=1800)
        async def process_webhook(payload: dict, store: IdempotencyStore):
            # Processing logic
            return result
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # Extract store from kwargs or args
            store: IdempotencyStore = kwargs.get("idempotency_store")
            if not store:
                raise ValueError("idempotency_store required")

            # Generate key from first arg (usually payload)
            payload = args[0] if args else {}
            idempotency_key = store._generate_key(payload, {})

            # Check for duplicate
            if await store.is_duplicate(idempotency_key):
                cached_result = await store.get_cached_result(idempotency_key)
                if cached_result:
                    return cached_result

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await store.mark_processed(idempotency_key, result, ttl=ttl_seconds)

            return result

        return wrapper
    return decorator


# Example usage
async def example_usage():
    """Example of using idempotency store"""
    # Setup Redis
    redis_client = redis.from_url("redis://localhost:6379")
    store = IdempotencyStore(redis_client, ttl_seconds=3600)

    # Check and process
    payload = {"user_id": 123, "action": "purchase"}
    idempotency_key = store._generate_key(payload, {})

    if await store.is_duplicate(idempotency_key):
        result = await store.get_cached_result(idempotency_key)
        print(f"Duplicate request, returning cached: {result}")
        return result

    # Process new request
    result = {"status": "success", "transaction_id": "abc123"}

    # Mark as processed
    await store.mark_processed(idempotency_key, result)

    return result
''',

    "webhook_verifier": '''"""
Webhook Signature Verification

HMAC-SHA256 signature verification with replay attack prevention.
"""

import hmac
import hashlib
import time
from typing import Optional
from fastapi import HTTPException, Header, Request, Depends
import structlog

logger = structlog.get_logger(__name__)


class WebhookSignatureVerifier:
    """
    HMAC-SHA256 signature verifier for webhooks.

    Supports multiple webhook providers (Stripe, GitHub, custom).
    """

    def __init__(self, secret: str, tolerance_seconds: int = 300):
        """
        Initialize verifier.

        Args:
            secret: Webhook signing secret
            tolerance_seconds: Maximum age of webhook (replay protection)
        """
        self.secret = secret.encode()
        self.tolerance = tolerance_seconds

    def generate_signature(self, payload: bytes, timestamp: str) -> str:
        """
        Generate HMAC-SHA256 signature.

        Args:
            payload: Request body bytes
            timestamp: Timestamp string

        Returns:
            Signature in format "v1=<hex_signature>"
        """
        message = f"{timestamp}.{payload.decode()}"
        signature = hmac.new(
            self.secret,
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"v1={signature}"

    def verify_signature(
        self,
        payload: bytes,
        signature_header: str,
        timestamp_header: str
    ) -> bool:
        """
        Verify webhook signature with timing-safe comparison.

        Args:
            payload: Request body bytes
            signature_header: Signature from header
            timestamp_header: Timestamp from header

        Returns:
            True if signature is valid
        """
        # Validate timestamp (replay protection)
        if not self._validate_timestamp(timestamp_header):
            logger.warning(
                "webhook_invalid_timestamp",
                timestamp=timestamp_header
            )
            return False

        # Extract signature from header
        if not signature_header.startswith("v1="):
            logger.warning(
                "webhook_invalid_signature_format",
                signature=signature_header[:20]
            )
            return False

        provided_signature = signature_header[3:]
        expected_signature = self.generate_signature(payload, timestamp_header)[3:]

        # Timing-safe comparison
        is_valid = hmac.compare_digest(provided_signature, expected_signature)

        if is_valid:
            logger.info("webhook_signature_valid")
        else:
            logger.warning(
                "webhook_signature_mismatch",
                expected=expected_signature[:10],
                provided=provided_signature[:10]
            )

        return is_valid

    def _validate_timestamp(self, timestamp_header: str) -> bool:
        """Validate timestamp to prevent replay attacks"""
        try:
            timestamp = int(timestamp_header)
            current_time = int(time.time())
            age_seconds = abs(current_time - timestamp)

            if age_seconds > self.tolerance:
                logger.warning(
                    "webhook_timestamp_too_old",
                    age_seconds=age_seconds,
                    tolerance=self.tolerance
                )
                return False

            return True

        except (ValueError, TypeError) as e:
            logger.error(
                "webhook_timestamp_parse_error",
                error=str(e),
                timestamp=timestamp_header
            )
            return False


# FastAPI Dependencies

async def verify_webhook_signature(
    request: Request,
    x_signature: str = Header(..., alias="X-Webhook-Signature"),
    x_timestamp: str = Header(..., alias="X-Webhook-Timestamp")
) -> bool:
    """
    FastAPI dependency to verify webhook signatures.

    Usage:
        @router.post("/webhook", dependencies=[Depends(verify_webhook_signature)])
        async def handle_webhook(payload: dict):
            # Signature already verified
            pass
    """
    from app.dependencies import get_webhook_verifier

    verifier = get_webhook_verifier()
    body = await request.body()

    if not verifier.verify_signature(body, x_signature, x_timestamp):
        logger.error(
            "webhook_signature_verification_failed",
            path=request.url.path
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature"
        )

    return True


async def verify_webhook_signature_optional(
    request: Request,
    x_signature: Optional[str] = Header(None, alias="X-Webhook-Signature"),
    x_timestamp: Optional[str] = Header(None, alias="X-Webhook-Timestamp")
) -> bool:
    """
    Optional signature verification (for testing or development).

    Logs a warning if signature is missing but doesn't fail.
    """
    if not x_signature or not x_timestamp:
        logger.warning(
            "webhook_signature_missing",
            path=request.url.path,
            environment=os.getenv("ENV_NAME", "unknown")
        )
        return False

    return await verify_webhook_signature(request, x_signature, x_timestamp)


# Provider-specific verifiers

class StripeWebhookVerifier:
    """Stripe-specific webhook verification"""

    def __init__(self, secret: str):
        self.secret = secret.encode()

    def verify(self, payload: bytes, signature_header: str) -> bool:
        """
        Verify Stripe webhook signature.

        Stripe format: "t=<timestamp>,v1=<signature>"
        """
        elements = dict(item.split("=") for item in signature_header.split(","))

        timestamp = elements.get("t")
        signature = elements.get("v1")

        if not timestamp or not signature:
            return False

        # Generate expected signature
        signed_payload = f"{timestamp}.{payload.decode()}"
        expected_signature = hmac.new(
            self.secret,
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)


class GitHubWebhookVerifier:
    """GitHub-specific webhook verification"""

    def __init__(self, secret: str):
        self.secret = secret.encode()

    def verify(self, payload: bytes, signature_header: str) -> bool:
        """
        Verify GitHub webhook signature.

        GitHub format: "sha256=<signature>"
        """
        if not signature_header.startswith("sha256="):
            return False

        provided_signature = signature_header[7:]
        expected_signature = hmac.new(
            self.secret,
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(provided_signature, expected_signature)
''',

    "async_kafka": '''"""
Async Kafka Pattern with aiokafka

Production-ready async Kafka producer with connection pooling and resilience.
"""

import asyncio
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import aiokafka
from aiokafka.errors import KafkaError
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

logger = structlog.get_logger(__name__)


class AsyncKafkaProducer:
    """
    Async Kafka producer with connection pooling and resilience.

    Features:
    - Async/await support
    - Connection pooling
    - Automatic retries
    - Circuit breaker integration
    - Batch publishing
    """

    def __init__(
        self,
        bootstrap_servers: str,
        client_id: str = "async-producer",
        compression_type: str = "lz4",
        acks: str = "all",
        retries: int = 3,
        max_batch_size: int = 16384,
        linger_ms: int = 10
    ):
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self.producer: Optional[aiokafka.AIOKafkaProducer] = None

        # Configuration
        self.config = {
            "bootstrap_servers": bootstrap_servers,
            "client_id": client_id,
            "compression_type": compression_type,
            "acks": acks,
            "retries": retries,
            "max_batch_size": max_batch_size,
            "linger_ms": linger_ms,
            "enable_idempotence": True if acks == "all" else False
        }

        logger.info("async_kafka_producer_configured", config=self.config)

    async def start(self):
        """Start the Kafka producer"""
        if self.producer:
            logger.warning("async_kafka_producer_already_started")
            return

        self.producer = aiokafka.AIOKafkaProducer(**self.config)
        await self.producer.start()

        logger.info("async_kafka_producer_started")

    async def stop(self):
        """Stop the Kafka producer gracefully"""
        if not self.producer:
            return

        try:
            await self.producer.stop()
            logger.info("async_kafka_producer_stopped")
        except Exception as e:
            logger.error("async_kafka_producer_stop_error", error=str(e))
        finally:
            self.producer = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    async def publish(
        self,
        topic: str,
        key: str,
        value: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> aiokafka.structs.RecordMetadata:
        """
        Publish a message to Kafka with retry logic.

        Args:
            topic: Kafka topic name
            key: Message key
            value: Message value (will be JSON-encoded)
            headers: Optional message headers

        Returns:
            RecordMetadata with partition and offset

        Raises:
            KafkaError: If publish fails after retries
        """
        if not self.producer:
            raise RuntimeError("Producer not started. Call start() first.")

        # Prepare headers
        headers_list = []
        if headers:
            headers_list = [
                (k, v.encode() if isinstance(v, str) else v)
                for k, v in headers.items()
            ]

        # Add default headers
        headers_list.append(("published_at", datetime.utcnow().isoformat().encode()))

        try:
            # Serialize value
            value_bytes = json.dumps(value).encode('utf-8')

            # Publish
            record_metadata = await self.producer.send_and_wait(
                topic=topic,
                key=key.encode('utf-8'),
                value=value_bytes,
                headers=headers_list
            )

            logger.info(
                "async_kafka_message_published",
                topic=topic,
                partition=record_metadata.partition,
                offset=record_metadata.offset,
                key=key
            )

            return record_metadata

        except KafkaError as e:
            logger.error(
                "async_kafka_publish_error",
                topic=topic,
                error=str(e),
                key=key
            )
            raise

    async def publish_batch(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[aiokafka.structs.RecordMetadata]:
        """
        Publish multiple messages in a batch.

        Args:
            messages: List of message dictionaries with 'topic', 'key', 'value', 'headers'

        Returns:
            List of RecordMetadata
        """
        tasks = []

        for msg in messages:
            task = self.publish(
                topic=msg["topic"],
                key=msg["key"],
                value=msg["value"],
                headers=msg.get("headers")
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any failures
        failed = [r for r in results if isinstance(r, Exception)]
        if failed:
            logger.error(
                "async_kafka_batch_publish_partial_failure",
                failed_count=len(failed),
                total_count=len(messages)
            )

        return [r for r in results if not isinstance(r, Exception)]

    async def health_check(self) -> bool:
        """Check if Kafka connection is healthy"""
        if not self.producer:
            return False

        try:
            # Try to fetch metadata
            metadata = await self.producer.client.fetch_all_metadata()
            broker_count = len(metadata.brokers())

            logger.info(
                "async_kafka_health_check",
                healthy=True,
                broker_count=broker_count
            )

            return broker_count > 0

        except Exception as e:
            logger.error("async_kafka_health_check_failed", error=str(e))
            return False


# Context manager for automatic lifecycle management
class AsyncKafkaProducerContext:
    """Context manager for Kafka producer"""

    def __init__(self, producer: AsyncKafkaProducer):
        self.producer = producer

    async def __aenter__(self):
        await self.producer.start()
        return self.producer

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.producer.stop()


# FastAPI integration
from functools import lru_cache

_producer_instance: Optional[AsyncKafkaProducer] = None

async def get_async_kafka_producer() -> AsyncKafkaProducer:
    """Get or create async Kafka producer (singleton)"""
    global _producer_instance

    if _producer_instance is None:
        from app.util.settings import config

        _producer_instance = AsyncKafkaProducer(
            bootstrap_servers=config.KAFKA_BROKERS,
            client_id=config.SERVICE_NAME,
            acks="all",  # For reliability
            compression_type="lz4"  # Good balance
        )

        await _producer_instance.start()

    return _producer_instance


# Lifespan integration for FastAPI
async def kafka_producer_lifespan(app):
    """FastAPI lifespan handler for Kafka producer"""
    # Startup
    producer = await get_async_kafka_producer()
    yield
    # Shutdown
    await producer.stop()


# Example usage
async def example_usage():
    """Example of using async Kafka producer"""
    # Create producer
    producer = AsyncKafkaProducer(
        bootstrap_servers="localhost:9092",
        client_id="example-service"
    )

    # Use context manager
    async with AsyncKafkaProducerContext(producer) as p:
        # Publish single message
        await p.publish(
            topic="events",
            key="user-123",
            value={"event": "user_created", "user_id": 123},
            headers={"source": "api"}
        )

        # Publish batch
        messages = [
            {
                "topic": "events",
                "key": f"user-{i}",
                "value": {"event": "user_action", "user_id": i}
            }
            for i in range(10)
        ]

        await p.publish_batch(messages)

        # Health check
        is_healthy = await p.health_check()
        print(f"Kafka healthy: {is_healthy}")
''',

    "base_service": '''"""
Base Service Pattern

Abstract base service with common patterns for business logic.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Dict, Any, Optional
from datetime import datetime
import structlog
from prometheus_client import Counter, Histogram

logger = structlog.get_logger(__name__)

# Type variable for service input
T = TypeVar('T')


class ServiceMetrics:
    """Metrics collector for services"""

    def __init__(self, service_name: str):
        self.service_name = service_name

        # Metrics
        self.requests = Counter(
            f'{service_name}_requests_total',
            f'Total requests to {service_name}',
            ['status']
        )

        self.duration = Histogram(
            f'{service_name}_duration_seconds',
            f'Request duration for {service_name}',
            ['operation']
        )

    def increment(self, status: str = "success"):
        """Increment request counter"""
        self.requests.labels(status=status).inc()

    def track_duration(self, operation: str):
        """Context manager for tracking duration"""
        return self.duration.labels(operation=operation).time()


class BaseService(ABC, Generic[T]):
    """
    Base service class with common patterns.

    Features:
    - Structured logging
    - Metrics collection
    - Error handling
    - Context propagation
    """

    def __init__(self, service_name: Optional[str] = None):
        self.service_name = service_name or self.__class__.__name__
        self.logger = logger.bind(service=self.service_name)
        self.metrics = ServiceMetrics(self.service_name)

    @abstractmethod
    async def process(self, data: T, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process business logic.

        Args:
            data: Input data (typed)
            context: Request context (user, trace_id, etc.)

        Returns:
            Result dictionary
        """
        pass

    async def execute(self, data: T, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute service with observability wrapper.

        Handles:
        - Logging
        - Metrics
        - Error handling
        - Context propagation
        """
        context = context or {}
        context.setdefault("timestamp", datetime.utcnow().isoformat())
        context.setdefault("service", self.service_name)

        # Log start
        self.logger.info(
            "service_execution_started",
            **context
        )

        try:
            # Track duration
            with self.metrics.track_duration("process"):
                result = await self.process(data, context)

            # Success metrics
            self.metrics.increment("success")

            # Log success
            self.logger.info(
                "service_execution_completed",
                **context
            )

            return result

        except Exception as e:
            # Failure metrics
            self.metrics.increment("failure")

            # Log error
            self.logger.error(
                "service_execution_failed",
                error=str(e),
                error_type=type(e).__name__,
                **context
            )

            raise

    async def validate(self, data: T, context: Dict[str, Any]) -> bool:
        """
        Validate input data (override in subclass if needed).

        Args:
            data: Input data
            context: Request context

        Returns:
            True if valid

        Raises:
            ValidationError: If data is invalid
        """
        # Default: no validation
        return True


# Example implementation
class WebhookProcessingService(BaseService[Dict[str, Any]]):
    """Service for processing webhook events"""

    def __init__(self, event_publisher):
        super().__init__(service_name="webhook_processing")
        self.event_publisher = event_publisher

    async def validate(self, data: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Validate webhook payload"""
        required_fields = ["message", "event_type"]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return True

    async def process(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook event"""
        # Validate
        await self.validate(data, context)

        # Extract data
        event_type = data.get("event_type")
        customer_number = self._extract_customer_number(data)

        # Enrich with context
        enriched_data = {
            **data,
            "processed_at": datetime.utcnow().isoformat(),
            "context_id": context.get("context_id"),
            "customer_number": customer_number
        }

        # Publish event
        topic = self._determine_topic(customer_number)

        await self.event_publisher.publish(
            topic=topic,
            key=customer_number or context["context_id"],
            value=enriched_data,
            headers={"source": "webhook-service"}
        )

        return {
            "status": "processed",
            "topic": topic,
            "context_id": context["context_id"]
        }

    def _extract_customer_number(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract customer number from nested structure"""
        try:
            return data.get("message", {}).get("call", {}).get("customer", {}).get("number")
        except (AttributeError, TypeError):
            return None

    def _determine_topic(self, customer_number: Optional[str]) -> str:
        """Determine Kafka topic based on data"""
        from app.util.settings import config

        if customer_number:
            return config.WEBHOOKS_TOPIC
        else:
            return config.WEBHOOKS_ERROR_TOPIC


# Usage in FastAPI
async def example_usage():
    """Example of using base service"""
    from app.dependencies import get_event_publisher

    # Create service
    service = WebhookProcessingService(
        event_publisher=get_event_publisher()
    )

    # Execute
    result = await service.execute(
        data={"message": {...}, "event_type": "call.completed"},
        context={"context_id": "123", "user_id": "456"}
    )

    print(result)
'''
}


def create_example(example_name: str, example_file: Path):
    """Create an example implementation file"""
    example_file.parent.mkdir(parents=True, exist_ok=True)

    content = EXAMPLE_TEMPLATES.get(
        example_name,
        f'''"""
{example_name.replace('_', ' ').title()} Example

Example implementation to be added.
"""

# Example code here
'''
    )

    with open(example_file, 'w') as f:
        f.write(content)

    # Create __init__.py in examples directory
    init_file = example_file.parent / "__init__.py"
    if not init_file.exists():
        with open(init_file, 'w') as f:
            f.write('"""Claude Code pattern examples"""\\n')

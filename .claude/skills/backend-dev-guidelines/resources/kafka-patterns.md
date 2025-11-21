# Kafka Patterns for FastAPI - Complete Guide

Event-driven architecture patterns using Kafka with FastAPI and aiokafka.

## Setup

### Installation

```bash
pip install aiokafka
# or
poetry add aiokafka
```

### Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "fastapi-service"
    KAFKA_AUTO_OFFSET_RESET: str = "earliest"
    KAFKA_ENABLE_AUTO_COMMIT: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
```

## Producer Pattern

### Basic Producer Setup

```python
# app/kafka/producer.py
from aiokafka import AIOKafkaProducer
from app.config import settings
import json
from typing import Any

class KafkaProducer:
    def __init__(self):
        self.producer: AIOKafkaProducer | None = None

    async def start(self):
        """Start Kafka producer"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            compression_type="gzip",
            acks="all",  # Wait for all replicas
            retries=3
        )
        await self.producer.start()

    async def stop(self):
        """Stop Kafka producer"""
        if self.producer:
            await self.producer.stop()

    async def send_message(
        self,
        topic: str,
        message: dict[str, Any],
        key: str | None = None
    ) -> None:
        """Send message to Kafka topic"""
        if not self.producer:
            raise RuntimeError("Producer not started")

        await self.producer.send_and_wait(
            topic=topic,
            value=message,
            key=key
        )

# Global producer instance
kafka_producer = KafkaProducer()
```

### Producer Dependency

```python
# app/dependencies.py
from app.kafka.producer import kafka_producer

async def get_kafka_producer() -> KafkaProducer:
    """Dependency for Kafka producer"""
    return kafka_producer
```

### Integration with FastAPI Lifecycle

```python
# app/main.py
from fastapi import FastAPI
from app.kafka.producer import kafka_producer
from app.kafka.consumer import start_consumers, stop_consumers

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Initialize Kafka on startup"""
    await kafka_producer.start()
    await start_consumers()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup Kafka on shutdown"""
    await kafka_producer.stop()
    await stop_consumers()
```

## Consumer Pattern

### Basic Consumer Setup

```python
# app/kafka/consumer.py
from aiokafka import AIOKafkaConsumer
from app.config import settings
import json
import asyncio
from typing import Callable, Awaitable
import logging

logger = logging.getLogger(__name__)

class KafkaConsumer:
    def __init__(
        self,
        topics: list[str],
        handler: Callable[[dict], Awaitable[None]]
    ):
        self.topics = topics
        self.handler = handler
        self.consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task | None = None

    async def start(self):
        """Start Kafka consumer"""
        self.consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_GROUP_ID,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
            enable_auto_commit=settings.KAFKA_ENABLE_AUTO_COMMIT
        )
        await self.consumer.start()
        self._task = asyncio.create_task(self._consume())

    async def stop(self):
        """Stop Kafka consumer"""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self.consumer:
            await self.consumer.stop()

    async def _consume(self):
        """Consume messages from Kafka"""
        try:
            async for message in self.consumer:
                try:
                    await self.handler(message.value)
                except Exception as e:
                    logger.error(
                        f"Error processing message from {message.topic}: {e}",
                        exc_info=True
                    )
        except asyncio.CancelledError:
            logger.info("Consumer cancelled")
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)
```

### Message Handlers

```python
# app/events/handlers.py
import logging
from typing import Any

logger = logging.getLogger(__name__)

async def handle_user_created(message: dict[str, Any]):
    """Handle user.created event"""
    logger.info(f"User created: {message}")

    user_id = message.get("user_id")
    email = message.get("email")

    # Process event (e.g., send welcome email, create profile, etc.)
    # Your business logic here

async def handle_post_published(message: dict[str, Any]):
    """Handle post.published event"""
    logger.info(f"Post published: {message}")

    post_id = message.get("post_id")
    author_id = message.get("author_id")

    # Process event (e.g., notify followers, index for search, etc.)
    # Your business logic here

async def handle_order_created(message: dict[str, Any]):
    """Handle order.created event"""
    logger.info(f"Order created: {message}")

    order_id = message.get("order_id")
    total = message.get("total")

    # Process event (e.g., update inventory, send confirmation, etc.)
    # Your business logic here
```

### Consumer Registration

```python
# app/kafka/consumers_registry.py
from app.kafka.consumer import KafkaConsumer
from app.events.handlers import (
    handle_user_created,
    handle_post_published,
    handle_order_created
)

# Register all consumers
CONSUMERS = [
    KafkaConsumer(["user.created"], handle_user_created),
    KafkaConsumer(["post.published"], handle_post_published),
    KafkaConsumer(["order.created"], handle_order_created),
]

async def start_consumers():
    """Start all registered consumers"""
    for consumer in CONSUMERS:
        await consumer.start()

async def stop_consumers():
    """Stop all registered consumers"""
    for consumer in CONSUMERS:
        await consumer.stop()
```

## Event Schemas

### Define Event Schemas with Pydantic

```python
# app/schemas/events.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class BaseEvent(BaseModel):
    """Base event schema"""
    event_id: str = Field(..., description="Unique event ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0")

class UserCreatedEvent(BaseEvent):
    """User created event"""
    event_type: Literal["user.created"] = "user.created"
    user_id: int
    email: str
    username: str

class PostPublishedEvent(BaseEvent):
    """Post published event"""
    event_type: Literal["post.published"] = "post.published"
    post_id: int
    author_id: int
    title: str

class OrderCreatedEvent(BaseEvent):
    """Order created event"""
    event_type: Literal["order.created"] = "order.created"
    order_id: int
    user_id: int
    total: float
    items: list[dict]
```

## Service Integration

### Publishing Events from Services

```python
# app/services/user_service.py
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.schemas.events import UserCreatedEvent
from app.kafka.producer import KafkaProducer
import uuid

class UserService:
    def __init__(
        self,
        repo: UserRepository,
        kafka_producer: KafkaProducer
    ):
        self.repo = repo
        self.kafka = kafka_producer

    async def create_user(self, data: UserCreate) -> UserResponse:
        """Create user and publish event"""
        # Create user in database
        user = await self.repo.create(data)

        # Publish event to Kafka
        event = UserCreatedEvent(
            event_id=str(uuid.uuid4()),
            user_id=user.id,
            email=user.email,
            username=user.username
        )

        await self.kafka.send_message(
            topic="user.created",
            message=event.model_dump(),
            key=str(user.id)
        )

        return UserResponse.from_orm(user)
```

### Using Producer in Routes

```python
# app/routers/users.py
from fastapi import APIRouter, Depends, status
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserResponse
from app.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Create user and publish event"""
    return await service.create_user(user_data)
```

## Transactional Outbox Pattern

For ensuring exactly-once delivery with database transactions:

```python
# app/models/outbox.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.models.base import Base

class OutboxMessage(Base):
    __tablename__ = "outbox_messages"

    id = Column(Integer, primary_key=True)
    topic = Column(String(255), nullable=False)
    key = Column(String(255))
    payload = Column(Text, nullable=False)  # JSON
    created_at = Column(DateTime, server_default=func.now())
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)

# app/services/outbox_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.outbox import OutboxMessage
from app.kafka.producer import KafkaProducer
import json

class OutboxService:
    def __init__(self, db: AsyncSession, kafka: KafkaProducer):
        self.db = db
        self.kafka = kafka

    async def add_message(self, topic: str, payload: dict, key: str = None):
        """Add message to outbox (within transaction)"""
        message = OutboxMessage(
            topic=topic,
            key=key,
            payload=json.dumps(payload)
        )
        self.db.add(message)
        await self.db.commit()

    async def process_outbox(self):
        """Process outbox messages (run as background job)"""
        unprocessed = await self.db.query(OutboxMessage).filter(
            OutboxMessage.processed == False
        ).all()

        for message in unprocessed:
            try:
                await self.kafka.send_message(
                    topic=message.topic,
                    message=json.loads(message.payload),
                    key=message.key
                )
                message.processed = True
                message.processed_at = func.now()
                await self.db.commit()
            except Exception as e:
                logger.error(f"Failed to process outbox message {message.id}: {e}")
                await self.db.rollback()
```

## Error Handling

### Dead Letter Queue Pattern

```python
# app/kafka/dlq.py
from app.kafka.producer import KafkaProducer
import logging

logger = logging.getLogger(__name__)

class DeadLetterQueue:
    def __init__(self, kafka_producer: KafkaProducer):
        self.kafka = kafka_producer
        self.dlq_topic = "dlq"

    async def send_to_dlq(
        self,
        original_topic: str,
        message: dict,
        error: Exception
    ):
        """Send failed message to DLQ"""
        dlq_message = {
            "original_topic": original_topic,
            "message": message,
            "error": str(error),
            "error_type": type(error).__name__
        }

        try:
            await self.kafka.send_message(
                topic=self.dlq_topic,
                message=dlq_message
            )
            logger.info(f"Sent message to DLQ from topic {original_topic}")
        except Exception as e:
            logger.error(f"Failed to send to DLQ: {e}", exc_info=True)
```

## Testing Kafka Code

### Mock Producer for Tests

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer for testing"""
    producer = AsyncMock()
    producer.send_message = AsyncMock(return_value=None)
    return producer

# tests/test_user_service.py
@pytest.mark.asyncio
async def test_create_user_publishes_event(
    db_session,
    mock_kafka_producer
):
    """Test that creating user publishes Kafka event"""
    repo = UserRepository(db_session)
    service = UserService(repo, mock_kafka_producer)

    user_data = UserCreate(email="test@example.com", username="testuser")
    user = await service.create_user(user_data)

    # Verify event was published
    mock_kafka_producer.send_message.assert_called_once()
    call_args = mock_kafka_producer.send_message.call_args

    assert call_args.kwargs["topic"] == "user.created"
    assert call_args.kwargs["message"]["user_id"] == user.id
```

## Best Practices

### 1. Topic Naming Convention

```python
# Use namespaced topic names
"service.entity.action"

# Examples:
"user-service.user.created"
"order-service.order.completed"
"notification-service.email.sent"
```

### 2. Message Keys for Partitioning

```python
# Use entity ID as key for ordering guarantees
await kafka_producer.send_message(
    topic="order.created",
    message=event.model_dump(),
    key=str(order.id)  # Ensures all events for same order go to same partition
)
```

### 3. Idempotency

```python
# Include idempotency key in events
class BaseEvent(BaseModel):
    event_id: str  # UUID for deduplication
    timestamp: datetime

# Consumer side - check for duplicates
async def handle_event(message: dict):
    event_id = message.get("event_id")

    # Check if already processed
    if await is_processed(event_id):
        logger.info(f"Event {event_id} already processed, skipping")
        return

    # Process event
    await process_event(message)

    # Mark as processed
    await mark_processed(event_id)
```

### 4. Schema Versioning

```python
class UserCreatedEventV1(BaseEvent):
    version: Literal["1.0.0"] = "1.0.0"
    user_id: int
    email: str

class UserCreatedEventV2(BaseEvent):
    version: Literal["2.0.0"] = "2.0.0"
    user_id: int
    email: str
    phone: str  # New field

# Consumer handles multiple versions
async def handle_user_created(message: dict):
    version = message.get("version", "1.0.0")

    if version == "1.0.0":
        event = UserCreatedEventV1(**message)
    elif version == "2.0.0":
        event = UserCreatedEventV2(**message)
    else:
        raise ValueError(f"Unsupported version: {version}")

    # Process event
```

## Performance Tips

1. **Batch Processing**: Process multiple messages in batches
2. **Compression**: Use gzip compression for large messages
3. **Partitioning**: Use proper keys for even distribution
4. **Consumer Groups**: Scale horizontally with multiple consumers
5. **Connection Pooling**: Reuse producer/consumer connections

## Common Patterns

### CQRS (Command Query Responsibility Segregation)

```python
# Write side - publishes events
@router.post("/orders")
async def create_order(order: OrderCreate, kafka: KafkaProducer = Depends()):
    # Save to write database
    order_id = await save_order(order)

    # Publish event
    await kafka.send_message("order.created", {"order_id": order_id})

    return {"order_id": order_id}

# Read side - consumes events and updates read model
async def handle_order_created(message: dict):
    # Update read-optimized database/cache
    await update_order_view(message["order_id"])
```

### Event Sourcing

```python
# Store events as source of truth
class OrderEvent(Base):
    __tablename__ = "order_events"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    event_type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

# Publish to Kafka and store in event store
async def publish_event(event: OrderEvent):
    # Store in database
    db.add(event)
    await db.commit()

    # Publish to Kafka
    await kafka.send_message(
        topic=f"order.{event.event_type}",
        message=event.payload,
        key=str(event.order_id)
    )
```

## Monitoring

```python
# Add metrics for Kafka operations
from prometheus_client import Counter, Histogram

kafka_messages_sent = Counter(
    'kafka_messages_sent_total',
    'Total Kafka messages sent',
    ['topic']
)

kafka_message_latency = Histogram(
    'kafka_message_latency_seconds',
    'Kafka message send latency',
    ['topic']
)

# Use in producer
async def send_message(topic: str, message: dict):
    with kafka_message_latency.labels(topic=topic).time():
        await self.producer.send_and_wait(topic, message)
    kafka_messages_sent.labels(topic=topic).inc()
```

## Summary

✅ Use aiokafka for async Kafka with FastAPI
✅ Implement producer/consumer patterns
✅ Define event schemas with Pydantic
✅ Use transactional outbox for reliability
✅ Implement DLQ for error handling
✅ Follow topic naming conventions
✅ Ensure idempotency with event IDs
✅ Version your event schemas
✅ Mock Kafka in tests
✅ Monitor with metrics

See also:
- `fastapi-patterns.md` for FastAPI integration
- `async-patterns.md` for async/await best practices
- `error-handling.md` for exception strategies

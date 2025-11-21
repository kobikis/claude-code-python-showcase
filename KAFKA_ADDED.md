# Kafka Support Added ✅

Comprehensive Kafka patterns have been added to the FastAPI showcase!

## What Was Added

### 1. **Skill Rules Updated**
- ✅ Added Kafka keywords: `kafka`, `producer`, `consumer`, `event`, `message`, `broker`
- ✅ Added intent patterns for event operations
- ✅ Added file path patterns: `**/events/**/*.py`, `**/kafka/**/*.py`, `**/producers/**/*.py`, `**/consumers/**/*.py`

### 2. **Complete Kafka Resource File**
**Location**: `.claude/skills/backend-dev-guidelines/resources/kafka-patterns.md`

**Includes**:
- ✅ Producer pattern with aiokafka
- ✅ Consumer pattern with message handlers
- ✅ Event schemas with Pydantic
- ✅ Service integration examples
- ✅ Transactional outbox pattern
- ✅ Dead Letter Queue (DLQ) pattern
- ✅ Testing strategies
- ✅ Best practices (idempotency, versioning, monitoring)
- ✅ CQRS and Event Sourcing patterns
- ✅ Error handling and retries

### 3. **Main Skill Updated**
**Location**: `.claude/skills/backend-dev-guidelines/SKILL.md`

**Changes**:
- ✅ Added Kafka to project structure
- ✅ Added "Publish events to Kafka" to endpoint checklist
- ✅ Added Kafka patterns to navigation guide (highlighted)
- ✅ Added Kafka to "When to Use This Skill" section
- ✅ Updated summary with event-driven architecture

### 4. **Documentation Updated**
**Files Updated**:
- ✅ `README.md` - Added Kafka to skills list and conventions
- ✅ `FASTAPI_FOCUS.md` - Added Kafka section, updated stack, keywords, and directory structure

## Kafka Patterns Covered

### Producer Patterns
```python
# Setup producer
from app.kafka.producer import kafka_producer

# Send event
await kafka_producer.send_message(
    topic="user.created",
    message={"user_id": 123, "email": "user@example.com"},
    key="123"
)
```

### Consumer Patterns
```python
# Define handler
async def handle_user_created(message: dict):
    user_id = message["user_id"]
    # Process event

# Register consumer
consumer = KafkaConsumer(["user.created"], handle_user_created)
await consumer.start()
```

### Event Schemas
```python
from pydantic import BaseModel

class UserCreatedEvent(BaseModel):
    event_id: str
    user_id: int
    email: str
    timestamp: datetime
```

### Integration with FastAPI Lifecycle
```python
@app.on_event("startup")
async def startup():
    await kafka_producer.start()
    await start_consumers()

@app.on_event("shutdown")
async def shutdown():
    await kafka_producer.stop()
    await stop_consumers()
```

## Advanced Patterns

✅ **Transactional Outbox** - Ensure exactly-once delivery
✅ **Dead Letter Queue** - Handle failed messages
✅ **Idempotency** - Prevent duplicate processing
✅ **Schema Versioning** - Handle event evolution
✅ **CQRS** - Command Query Responsibility Segregation
✅ **Event Sourcing** - Event-driven state management

## Testing

✅ Mock Kafka producers in tests
✅ Test event handlers in isolation
✅ Integration tests with test Kafka

## Monitoring

✅ Prometheus metrics for Kafka operations
✅ Message latency tracking
✅ Consumer lag monitoring

## Dependencies

Add to your project:
```bash
pip install aiokafka

# or with poetry
poetry add aiokafka
```

## Skill Activation

The skill will now activate when you mention:
- "kafka"
- "publish event"
- "consume message"
- "event-driven"
- "message broker"
- Working in `**/kafka/**/*.py` files
- Working in `**/events/**/*.py` files

## Example Usage

### Creating a New Event-Driven Endpoint

1. **Define Event Schema**
```python
# app/schemas/events.py
class PostPublishedEvent(BaseModel):
    event_id: str
    post_id: int
    author_id: int
    title: str
```

2. **Publish Event from Service**
```python
# app/services/post_service.py
async def publish_post(self, post_id: int):
    post = await self.repo.publish(post_id)

    event = PostPublishedEvent(
        event_id=str(uuid.uuid4()),
        post_id=post.id,
        author_id=post.author_id,
        title=post.title
    )

    await self.kafka.send_message(
        topic="post.published",
        message=event.model_dump(),
        key=str(post.id)
    )
```

3. **Handle Event in Consumer**
```python
# app/events/handlers.py
async def handle_post_published(message: dict):
    post_id = message["post_id"]
    # Notify followers, index for search, etc.
```

4. **Register Consumer**
```python
# app/kafka/consumers_registry.py
CONSUMERS = [
    KafkaConsumer(["post.published"], handle_post_published)
]
```

## Use Cases

Perfect for:
- 🎯 Microservices communication
- 🎯 Event-driven architectures
- 🎯 Async notifications
- 🎯 Data streaming
- 🎯 CQRS patterns
- 🎯 Audit logging
- 🎯 Real-time analytics
- 🎯 Saga orchestration

## Resources

- **Full guide**: `.claude/skills/backend-dev-guidelines/resources/kafka-patterns.md`
- **aiokafka docs**: https://aiokafka.readthedocs.io/
- **Kafka patterns**: https://kafka.apache.org/documentation/

---

**Ready to use!** Claude will now suggest Kafka patterns when you work on event-driven features! 🚀

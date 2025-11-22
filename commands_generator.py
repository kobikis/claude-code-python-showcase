"""
Commands Generator Module

Generates Claude Code slash command files.
"""

from pathlib import Path


COMMAND_TEMPLATES = {
    "check-prod-readiness": """Perform a comprehensive production readiness check for this FastAPI microservice.

## Areas to Check

### 1. Security
- [ ] Authentication/authorization implemented
- [ ] Webhook signature verification
- [ ] Rate limiting configured
- [ ] API keys/secrets stored securely
- [ ] HTTPS enforced
- [ ] Security headers configured (HSTS, CSP, X-Frame-Options)
- [ ] CORS properly configured
- [ ] No hardcoded secrets in code

### 2. Reliability
- [ ] Circuit breakers for external dependencies
- [ ] Retry logic with exponential backoff
- [ ] Idempotency implemented for non-GET operations
- [ ] Dead letter queue for failed events
- [ ] Proper timeout configuration
- [ ] Graceful shutdown handling
- [ ] Health checks with dependency validation

### 3. Observability
- [ ] Structured logging implemented
- [ ] Metrics exported (Prometheus/custom)
- [ ] Distributed tracing configured
- [ ] Request correlation IDs
- [ ] Error tracking (Sentry/similar)
- [ ] SLI/SLO monitoring
- [ ] Alerting configured

### 4. Performance
- [ ] Async/await used for I/O operations
- [ ] Connection pooling configured
- [ ] Caching implemented where appropriate
- [ ] Database queries optimized
- [ ] Payload size limits enforced
- [ ] Response compression enabled
- [ ] Static assets CDN-served

### 5. Testing
- [ ] Unit tests with >80% coverage
- [ ] Integration tests
- [ ] API contract tests
- [ ] Load/stress tests performed
- [ ] Security tests (OWASP)
- [ ] Chaos engineering tests

### 6. Documentation
- [ ] OpenAPI/Swagger docs complete
- [ ] README with setup instructions
- [ ] Architecture diagrams
- [ ] Runbook for operations
- [ ] API authentication documented
- [ ] Environment variables documented

### 7. Infrastructure
- [ ] Containerized (Docker)
- [ ] CI/CD pipeline configured
- [ ] Auto-scaling configured
- [ ] Backup/recovery procedures
- [ ] Database migrations automated
- [ ] Secrets management configured
- [ ] Log aggregation setup

### 8. Compliance
- [ ] Data privacy requirements met (GDPR/CCPA)
- [ ] PII handling appropriate
- [ ] Audit logging for sensitive operations
- [ ] Data retention policies implemented
- [ ] Dependency licenses checked

## Review Process

1. Read the main application code, dependencies, and configuration
2. Check each item in the checklist
3. Identify gaps and risks
4. Provide prioritized recommendations
5. Suggest specific implementations for missing items

## Output Format

Provide results as:

### ✅ Passing (What's working well)
### ⚠️ Warnings (Should be addressed before production)
### ❌ Critical (Must be fixed before production)
### 💡 Recommendations (Nice-to-have improvements)

Be thorough and specific. Include code examples for fixes.
""",

    "kafka-health": """Check the health and configuration of Kafka integration in this project.

## Checks to Perform

### 1. Connection Health
- Check if Kafka brokers are reachable
- Verify broker list configuration
- Test network connectivity
- Validate SSL/TLS configuration if applicable

### 2. Producer Configuration
Review these settings:
- `acks` - Should be 'all' for critical data
- `retries` - Should be > 0
- `enable.idempotence` - Should be True for critical data
- `compression.type` - Should be set (snappy/lz4/gzip)
- `linger.ms` - Affects throughput vs latency trade-off
- `batch.size` - Should be tuned for workload
- `max.in.flight.requests.per.connection` - Should be 1 if ordering matters

### 3. Topic Configuration
- Verify topics exist
- Check partition count
- Review replication factor
- Validate retention settings

### 4. Error Handling
- Check for circuit breaker implementation
- Verify retry logic
- Confirm DLQ (dead letter queue) setup
- Review error logging

### 5. Performance
- Check for async producer (aiokafka)
- Verify no blocking operations
- Review batching strategy
- Check connection pooling

### 6. Monitoring
- Verify metrics collection (publish latency, errors)
- Check logging of publish operations
- Review alerting configuration

## Commands to Run

```python
# Test producer
from app.util.kafka_utils import get_kafka_producer

producer = get_kafka_producer()
if producer:
    # Test publish
    try:
        producer.produce(topic="test", key="test", value=b"test message")
        producer.producer.flush()
        print("✅ Producer working")
    except Exception as e:
        print(f"❌ Producer error: {e}")
else:
    print("⚠️ Producer not configured")
```

## Output Format

Provide:

### Connection Status
- Broker connectivity
- Configuration details

### Configuration Review
- Current settings
- Recommended changes
- Reasoning for each recommendation

### Health Issues
- Any problems found
- Severity (critical/warning/info)
- Remediation steps

### Performance Recommendations
- Optimization suggestions
- Expected impact

Be specific with configuration values and explain trade-offs.
""",

    "webhook-test": """Generate comprehensive test scenarios for webhook endpoints.

## Test Categories to Generate

### 1. Valid Payload Tests
Create tests for:
- Minimal valid payload
- Complete payload with all optional fields
- Large payload (near size limit)
- Different event types (if applicable)

### 2. Invalid Payload Tests
- Missing required fields
- Wrong data types
- Invalid format (email, phone, etc.)
- Payload too large
- Malformed JSON
- Empty payload

### 3. Security Tests
- Invalid signature
- Expired timestamp (replay attack)
- Missing signature header
- Missing timestamp header
- Modified payload (signature mismatch)
- Future timestamp

### 4. Error Handling Tests
- Kafka publish failure simulation
- Database error simulation
- Timeout scenarios
- Duplicate requests (idempotency)

### 5. Rate Limiting Tests
- Within rate limit
- Exceeding rate limit
- Burst traffic
- Multiple concurrent requests

### 6. Edge Cases
- Special characters in payload
- Unicode handling
- Null values
- Empty strings vs null
- Very long strings

## Test Template Structure

```python
import pytest
from httpx import AsyncClient
from freezegun import freeze_time
import time

class TestWebhookEndpoint:
    async def test_valid_webhook(self, client: AsyncClient):
        '''Test webhook with valid payload and signature'''
        payload = {...}
        timestamp = str(int(time.time()))
        signature = generate_test_signature(payload, timestamp)

        response = await client.post(
            "/api/v1/webhooks/voice-webhook",
            json=payload,
            headers={
                "X-Webhook-Signature": signature,
                "X-Webhook-Timestamp": timestamp
            }
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"

    async def test_invalid_signature(self, client: AsyncClient):
        '''Test webhook with invalid signature'''
        payload = {...}
        timestamp = str(int(time.time()))

        response = await client.post(
            "/api/v1/webhooks/voice-webhook",
            json=payload,
            headers={
                "X-Webhook-Signature": "v1=invalid",
                "X-Webhook-Timestamp": timestamp
            }
        )

        assert response.status_code == 401

    @freeze_time("2024-01-01 12:00:00")
    async def test_replay_attack_prevention(self, client: AsyncClient):
        '''Test timestamp validation prevents replay attacks'''
        payload = {...}
        old_timestamp = str(int(time.time()) - 400)  # 400 seconds ago
        signature = generate_test_signature(payload, old_timestamp)

        response = await client.post(
            "/api/v1/webhooks/voice-webhook",
            json=payload,
            headers={
                "X-Webhook-Signature": signature,
                "X-Webhook-Timestamp": old_timestamp
            }
        )

        assert response.status_code == 401
```

## Output

Generate:
1. Complete test file with all test cases
2. Fixtures needed (conftest.py additions)
3. Mock configurations
4. Test data generators
5. Instructions for running tests

Include pytest markers for categorization:
- @pytest.mark.unit
- @pytest.mark.integration
- @pytest.mark.security
""",

    "security-scan": """Perform a comprehensive security scan of the codebase.

## Scan Areas

### 1. Secrets Detection
Scan for:
- Hardcoded passwords
- API keys
- JWT secrets
- Database credentials
- Private keys
- AWS/cloud credentials

Files to check:
- Python files (.py)
- Configuration files (.json, .yaml, .env)
- Docker files
- CI/CD configs

### 2. Dependency Vulnerabilities
Run security audits:
```bash
# Check for known vulnerabilities
safety check --json

# Detailed dependency audit
pip-audit --format json

# Check for outdated packages
pip list --outdated
```

### 3. Code Security Issues
Use bandit for Python security linting:
```bash
# Scan for security issues
bandit -r app/ -f json -o bandit-report.json

# Check specific issues:
# - SQL injection risks
# - Command injection
# - Unsafe YAML loading
# - Assert used
# - Exec/eval usage
# - Weak cryptography
```

### 4. Authentication/Authorization
Review:
- [ ] Authentication middleware implemented
- [ ] Authorization checks on endpoints
- [ ] Token validation logic
- [ ] Session management
- [ ] Password hashing (if applicable)

### 5. Input Validation
Check for:
- [ ] Pydantic models for request validation
- [ ] SQL injection prevention
- [ ] Command injection prevention
- [ ] Path traversal prevention
- [ ] XSS prevention
- [ ] File upload validation

### 6. Security Headers
Verify presence of:
- [ ] Strict-Transport-Security
- [ ] X-Content-Type-Options
- [ ] X-Frame-Options
- [ ] Content-Security-Policy
- [ ] X-XSS-Protection

### 7. CORS Configuration
Review:
- [ ] Origins properly restricted
- [ ] Credentials handling
- [ ] Allowed methods restricted
- [ ] Allowed headers restricted

### 8. Logging Security
Check for:
- [ ] No sensitive data in logs (passwords, tokens, PII)
- [ ] Security events logged
- [ ] Log injection prevention
- [ ] Log rotation configured

## Commands to Execute

```bash
# Create security report directory
mkdir -p security_reports

# Run all scans
safety check --json > security_reports/safety.json
pip-audit --format json > security_reports/pip-audit.json
bandit -r app/ -f json -o security_reports/bandit.json

# Check for secrets (if detect-secrets installed)
detect-secrets scan > security_reports/secrets.json
```

## Output Format

Provide a comprehensive report:

### 🔴 Critical Vulnerabilities
High-priority security issues that must be fixed immediately

### 🟠 High Priority
Important security issues to address soon

### 🟡 Medium Priority
Security improvements recommended

### 🟢 Low Priority
Nice-to-have security enhancements

### ✅ Passing
What's secure and working well

Include:
- CVE numbers (if applicable)
- OWASP category
- Remediation steps
- Code examples for fixes
- Priority/severity rating

Generate actionable tickets for each issue.
""",

    "migrate-pydantic-v2": """Guide the migration from Pydantic v1 to Pydantic v2.

## Migration Overview

Pydantic v2 is a ground-up rewrite with significant breaking changes but 10-50x performance improvements.

## Breaking Changes to Address

### 1. Validator Syntax
```python
# v1
from pydantic import validator

class Model(BaseModel):
    email: str

    @validator('email')
    def validate_email(cls, v):
        # validation logic
        return v

# v2
from pydantic import field_validator

class Model(BaseModel):
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # validation logic
        return v
```

### 2. Config Class
```python
# v1
class Model(BaseModel):
    class Config:
        orm_mode = True
        use_enum_values = True

# v2
from pydantic import ConfigDict

class Model(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )
```

### 3. JSON Schema
```python
# v1
Model.schema()

# v2
Model.model_json_schema()
```

### 4. Model Methods
```python
# v1
model.dict()
model.json()
model.copy()
Model.parse_obj(data)
Model.parse_raw(json_str)

# v2
model.model_dump()
model.model_dump_json()
model.model_copy()
Model.model_validate(data)
Model.model_validate_json(json_str)
```

### 5. Root Validators
```python
# v1
from pydantic import root_validator

@root_validator
def validate_root(cls, values):
    return values

# v2
from pydantic import model_validator

@model_validator(mode='after')
def validate_root(self):
    return self
```

## Migration Steps

### Step 1: Update requirements.txt
```txt
# Change from:
pydantic<2.0.0

# To:
pydantic>=2.5.0
pydantic-settings>=2.1.0  # If using BaseSettings
```

### Step 2: Install and Test
```bash
pip install pydantic>=2.5.0
pytest  # Run tests to identify issues
```

### Step 3: Fix Breaking Changes
Go through each model and update:
1. Validators → field_validator/model_validator
2. Config class → model_config
3. Method calls (dict() → model_dump())
4. JSON schema calls

### Step 4: Update FastAPI
Ensure FastAPI version is compatible:
```txt
fastapi>=0.104.0  # Pydantic v2 support
```

### Step 5: Test Thoroughly
- Run all unit tests
- Run integration tests
- Test API endpoints
- Verify JSON schema generation
- Check OpenAPI docs

## Common Issues

### Issue: orm_mode → from_attributes
```python
# Old
class Config:
    orm_mode = True

# New
model_config = ConfigDict(from_attributes=True)
```

### Issue: allow_population_by_field_name → populate_by_name
```python
# Old
class Config:
    allow_population_by_field_name = True

# New
model_config = ConfigDict(populate_by_name=True)
```

### Issue: Field alias_generator
```python
# v2 has better alias support
from pydantic import Field, AliasChoices

class Model(BaseModel):
    user_id: int = Field(
        validation_alias=AliasChoices('userId', 'user_id')
    )
```

## Migration Checklist

- [ ] Update requirements.txt
- [ ] Install pydantic v2
- [ ] Update all @validator → @field_validator
- [ ] Update Config classes → model_config
- [ ] Update .dict() → .model_dump()
- [ ] Update .json() → .model_dump_json()
- [ ] Update .parse_obj() → .model_validate()
- [ ] Update schema() calls → model_json_schema()
- [ ] Run and fix all tests
- [ ] Test API endpoints manually
- [ ] Verify OpenAPI docs work
- [ ] Benchmark performance improvements
- [ ] Update documentation

## Performance Improvements

After migration, you should see:
- 10-50x faster validation
- Lower memory usage
- Faster JSON serialization
- Better type checking

## Resources

- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [Pydantic v2 Changelog](https://docs.pydantic.dev/latest/changelog/)

Analyze all Pydantic usage in the codebase and provide specific migration steps with code examples.
"""
}


def create_command(command_name: str, command_file: Path):
    """Create a slash command markdown file"""
    command_file.parent.mkdir(parents=True, exist_ok=True)

    content = COMMAND_TEMPLATES.get(
        command_name,
        f"# {command_name.replace('-', ' ').title()} Command\n\nCommand content to be added."
    )

    with open(command_file, 'w') as f:
        f.write(content)

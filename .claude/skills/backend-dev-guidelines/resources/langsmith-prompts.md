# LangSmith Prompt Management with FastAPI

Complete guide for integrating LangSmith prompt management with FastAPI applications.

## Overview

LangSmith allows you to:
- Store and version prompts centrally
- Pull prompts at runtime
- A/B test different prompt versions
- Track prompt performance
- Collaborate on prompt engineering

## Setup

### Installation

```bash
pip install langsmith langchain-core
# For OpenAI
pip install langchain-openai
# For Anthropic
pip install langchain-anthropic

# or with poetry
poetry add langsmith langchain-core langchain-openai
```

### Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LangSmith
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_API_KEY: str
    LANGCHAIN_PROJECT: str = "fastapi-app"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    # OpenAI (optional)
    OPENAI_API_KEY: str | None = None

    # Anthropic (optional)
    ANTHROPIC_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
```

### Environment Variables

```bash
# .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=fastapi-app
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## LangSmith Client Setup

### Basic Client

```python
# app/llm/langsmith_client.py
from langsmith import Client
from app.config import settings

class LangSmithClient:
    def __init__(self):
        self.client = Client(
            api_key=settings.LANGCHAIN_API_KEY,
            api_url=settings.LANGCHAIN_ENDPOINT
        )

    def pull_prompt(self, prompt_name: str, version: str = "latest"):
        """Pull a prompt from LangSmith"""
        return self.client.pull_prompt(f"{prompt_name}:{version}")

    def list_prompts(self):
        """List all available prompts"""
        return self.client.list_prompts()

# Global instance
langsmith_client = LangSmithClient()
```

### Dependency Injection

```python
# app/dependencies.py
from app.llm.langsmith_client import langsmith_client

def get_langsmith_client() -> LangSmithClient:
    """Dependency for LangSmith client"""
    return langsmith_client
```

## Pulling Prompts from LangSmith

### Basic Usage

```python
# app/services/ai_service.py
from langchain_openai import ChatOpenAI
from langsmith import Client

class AIService:
    def __init__(self, langsmith_client: Client):
        self.langsmith = langsmith_client
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    async def generate_joke(self, topic: str) -> str:
        """Generate a joke using LangSmith prompt"""
        # Pull prompt from LangSmith
        prompt = self.langsmith.pull_prompt("joke-generator:prod")

        # Invoke with variables
        messages = prompt.invoke({"topic": topic})

        # Call LLM
        response = await self.llm.ainvoke(messages)

        return response.content
```

### With Version Management

```python
# app/services/ai_service.py
from typing import Literal

PromptVersion = Literal["dev", "staging", "prod"]

class AIService:
    async def generate_content(
        self,
        prompt_name: str,
        variables: dict,
        version: PromptVersion = "prod"
    ) -> str:
        """Generate content using versioned prompt"""
        # Pull specific version
        prompt = self.langsmith.pull_prompt(f"{prompt_name}:{version}")

        # Invoke
        messages = prompt.invoke(variables)
        response = await self.llm.ainvoke(messages)

        return response.content
```

## FastAPI Integration

### Basic Endpoint

```python
# app/routers/ai.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.ai_service import AIService
from app.dependencies import get_ai_service

router = APIRouter(prefix="/ai", tags=["ai"])

class JokeRequest(BaseModel):
    topic: str

class JokeResponse(BaseModel):
    joke: str

@router.post("/joke", response_model=JokeResponse)
async def generate_joke(
    request: JokeRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Generate a joke using LangSmith prompt"""
    try:
        joke = await ai_service.generate_joke(request.topic)
        return JokeResponse(joke=joke)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Advanced Endpoint with Prompt Selection

```python
# app/routers/ai.py
from typing import Optional

class ContentRequest(BaseModel):
    prompt_name: str
    variables: dict[str, str]
    version: Optional[str] = "prod"

class ContentResponse(BaseModel):
    content: str
    prompt_version: str

@router.post("/generate", response_model=ContentResponse)
async def generate_content(
    request: ContentRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Generate content using any LangSmith prompt"""
    content = await ai_service.generate_content(
        prompt_name=request.prompt_name,
        variables=request.variables,
        version=request.version
    )

    return ContentResponse(
        content=content,
        prompt_version=request.version
    )
```

## Caching Prompts

### In-Memory Cache

```python
# app/llm/prompt_cache.py
from typing import Dict
from langchain.prompts import ChatPromptTemplate
import asyncio
from datetime import datetime, timedelta

class PromptCache:
    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, tuple[ChatPromptTemplate, datetime]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)
        self._lock = asyncio.Lock()

    async def get_prompt(
        self,
        langsmith_client: Client,
        prompt_name: str,
        version: str = "prod"
    ) -> ChatPromptTemplate:
        """Get prompt with caching"""
        cache_key = f"{prompt_name}:{version}"

        async with self._lock:
            # Check cache
            if cache_key in self._cache:
                prompt, cached_at = self._cache[cache_key]
                if datetime.now() - cached_at < self._ttl:
                    return prompt

            # Pull from LangSmith
            prompt = langsmith_client.pull_prompt(cache_key)
            self._cache[cache_key] = (prompt, datetime.now())

            return prompt

# Global cache
prompt_cache = PromptCache(ttl_seconds=300)
```

### Using Cache

```python
# app/services/ai_service.py
from app.llm.prompt_cache import prompt_cache

class AIService:
    async def generate_with_cache(self, topic: str) -> str:
        """Generate using cached prompt"""
        prompt = await prompt_cache.get_prompt(
            self.langsmith,
            "joke-generator",
            "prod"
        )

        messages = prompt.invoke({"topic": topic})
        response = await self.llm.ainvoke(messages)

        return response.content
```

## Multiple LLM Providers

### Provider Abstraction

```python
# app/llm/providers.py
from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages) -> str:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-4"):
        self.llm = ChatOpenAI(model=model, temperature=0.7)

    async def generate(self, messages) -> str:
        response = await self.llm.ainvoke(messages)
        return response.content

class AnthropicProvider(LLMProvider):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.llm = ChatAnthropic(model=model, temperature=0.7)

    async def generate(self, messages) -> str:
        response = await self.llm.ainvoke(messages)
        return response.content

# Factory
def get_llm_provider(provider: str = "openai") -> LLMProvider:
    if provider == "openai":
        return OpenAIProvider()
    elif provider == "anthropic":
        return AnthropicProvider()
    else:
        raise ValueError(f"Unknown provider: {provider}")
```

### Using Multiple Providers

```python
# app/routers/ai.py
class ContentRequest(BaseModel):
    prompt_name: str
    variables: dict[str, str]
    provider: Literal["openai", "anthropic"] = "openai"

@router.post("/generate")
async def generate_content(request: ContentRequest):
    # Get provider
    llm_provider = get_llm_provider(request.provider)

    # Pull prompt
    prompt = langsmith_client.pull_prompt(f"{request.prompt_name}:prod")

    # Generate
    messages = prompt.invoke(request.variables)
    content = await llm_provider.generate(messages)

    return {"content": content}
```

## Streaming Responses

### Streaming with FastAPI

```python
# app/routers/ai.py
from fastapi.responses import StreamingResponse

@router.post("/stream")
async def stream_content(
    request: ContentRequest,
    ai_service: AIService = Depends()
):
    """Stream LLM response"""
    async def generate():
        prompt = langsmith_client.pull_prompt(f"{request.prompt_name}:prod")
        messages = prompt.invoke(request.variables)

        async for chunk in ai_service.llm.astream(messages):
            if chunk.content:
                yield chunk.content

    return StreamingResponse(generate(), media_type="text/plain")
```

### Server-Sent Events (SSE)

```python
from sse_starlette.sse import EventSourceResponse

@router.post("/stream-sse")
async def stream_sse(request: ContentRequest):
    """Stream with SSE"""
    async def event_generator():
        prompt = langsmith_client.pull_prompt(f"{request.prompt_name}:prod")
        messages = prompt.invoke(request.variables)

        async for chunk in llm.astream(messages):
            if chunk.content:
                yield {
                    "event": "message",
                    "data": chunk.content
                }

        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())
```

## Error Handling

### Robust Error Handling

```python
# app/services/ai_service.py
from langsmith.errors import LangSmithError
from openai import OpenAIError

class AIService:
    async def generate_with_fallback(
        self,
        prompt_name: str,
        variables: dict,
        fallback_text: str = "Unable to generate content"
    ) -> str:
        """Generate with error handling and fallback"""
        try:
            # Try to pull prompt
            prompt = self.langsmith.pull_prompt(f"{prompt_name}:prod")
            messages = prompt.invoke(variables)

            # Try to generate
            response = await self.llm.ainvoke(messages)
            return response.content

        except LangSmithError as e:
            logger.error(f"LangSmith error: {e}")
            # Try dev version as fallback
            try:
                prompt = self.langsmith.pull_prompt(f"{prompt_name}:dev")
                messages = prompt.invoke(variables)
                response = await self.llm.ainvoke(messages)
                return response.content
            except Exception:
                return fallback_text

        except OpenAIError as e:
            logger.error(f"OpenAI error: {e}")
            return fallback_text

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return fallback_text
```

## Monitoring and Tracing

### Automatic Tracing

```python
# LangSmith automatically traces when LANGCHAIN_TRACING_V2=true

# app/services/ai_service.py
from langsmith import traceable

class AIService:
    @traceable(name="generate_joke")
    async def generate_joke(self, topic: str) -> str:
        """Generate joke with automatic tracing"""
        prompt = self.langsmith.pull_prompt("joke-generator:prod")
        messages = prompt.invoke({"topic": topic})
        response = await self.llm.ainvoke(messages)
        return response.content
```

### Custom Metadata

```python
from langsmith import Client

@traceable(
    name="generate_content",
    metadata={"service": "content-generator", "version": "1.0"}
)
async def generate_content(topic: str) -> str:
    # Your logic here
    pass
```

## Testing

### Mock LangSmith in Tests

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_langsmith_client():
    """Mock LangSmith client"""
    client = MagicMock()

    # Mock pull_prompt
    mock_prompt = MagicMock()
    mock_prompt.invoke.return_value = [
        {"role": "system", "content": "You are a comedian"},
        {"role": "user", "content": "Tell me a joke about {topic}"}
    ]
    client.pull_prompt.return_value = mock_prompt

    return client

# tests/test_ai_service.py
@pytest.mark.asyncio
async def test_generate_joke(mock_langsmith_client):
    """Test joke generation"""
    service = AIService(mock_langsmith_client)

    joke = await service.generate_joke("programming")

    assert joke is not None
    mock_langsmith_client.pull_prompt.assert_called_once_with("joke-generator:prod")
```

## Best Practices

### 1. Environment-Based Versioning

```python
# Use different versions per environment
class Settings(BaseSettings):
    PROMPT_VERSION: str = Field(default="prod")

# In service
prompt = langsmith_client.pull_prompt(
    f"joke-generator:{settings.PROMPT_VERSION}"
)
```

### 2. Prompt Validation

```python
def validate_prompt_variables(
    prompt: ChatPromptTemplate,
    variables: dict
) -> bool:
    """Validate all required variables are present"""
    required_vars = prompt.input_variables
    return all(var in variables for var in required_vars)

# Usage
if not validate_prompt_variables(prompt, {"topic": "coding"}):
    raise ValueError("Missing required variables")
```

### 3. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/generate")
@limiter.limit("10/minute")
async def generate_content(request: Request, data: ContentRequest):
    # Your logic
    pass
```

### 4. Cost Tracking

```python
from langchain.callbacks import get_openai_callback

async def generate_with_cost_tracking(prompt_name: str, variables: dict):
    """Track token usage and cost"""
    with get_openai_callback() as cb:
        prompt = langsmith_client.pull_prompt(f"{prompt_name}:prod")
        messages = prompt.invoke(variables)
        response = await llm.ainvoke(messages)

        logger.info(
            f"Tokens used: {cb.total_tokens}, "
            f"Cost: ${cb.total_cost:.4f}"
        )

        return response.content
```

## Complete Example

### Full Service Implementation

```python
# app/services/ai_service.py
from langsmith import Client, traceable
from langchain_openai import ChatOpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.langsmith = Client(api_key=settings.LANGCHAIN_API_KEY)
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    @traceable(name="generate_joke")
    async def generate_joke(
        self,
        topic: str,
        version: str = "prod"
    ) -> str:
        """Generate a joke using LangSmith prompt"""
        try:
            # Pull prompt from LangSmith
            prompt = self.langsmith.pull_prompt(f"joke-generator:{version}")

            # Validate variables
            if "topic" not in prompt.input_variables:
                raise ValueError("Prompt doesn't accept 'topic' variable")

            # Invoke prompt
            messages = prompt.invoke({"topic": topic})

            # Call LLM
            response = await self.llm.ainvoke(messages)

            logger.info(f"Generated joke for topic: {topic}")
            return response.content

        except Exception as e:
            logger.error(f"Error generating joke: {e}", exc_info=True)
            raise

# app/routers/ai.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["ai"])

class JokeRequest(BaseModel):
    topic: str
    version: str = "prod"

class JokeResponse(BaseModel):
    joke: str

@router.post("/joke", response_model=JokeResponse)
async def generate_joke(
    request: JokeRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """Generate a joke using LangSmith prompt

    The prompt is pulled from LangSmith at runtime,
    allowing for easy updates without code changes.
    """
    try:
        joke = await ai_service.generate_joke(
            topic=request.topic,
            version=request.version
        )
        return JokeResponse(joke=joke)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate joke")
```

## Summary

✅ Use LangSmith for centralized prompt management
✅ Pull prompts at runtime with versioning
✅ Cache prompts to reduce latency
✅ Support multiple LLM providers
✅ Implement proper error handling
✅ Add automatic tracing with LangSmith
✅ Stream responses for better UX
✅ Test with mocked clients
✅ Track costs and usage
✅ Use environment-based versioning

See also:
- `fastapi-patterns.md` for FastAPI integration
- `async-patterns.md` for async/await best practices
- `error-handling.md` for exception strategies
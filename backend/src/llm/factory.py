"""LLM client factory - switch providers via config."""
from ..config import settings
from .base import LLMClientBase
from .mock_adapter import MockLLMAdapter


def get_llm_client() -> LLMClientBase:
    """Return configured LLM client. Default: mock for dev without API key."""
    provider = (settings.llm_provider or "mock").lower()
    if provider == "mock" or not settings.llm_api_key:
        return MockLLMAdapter()
    if provider == "openai":
        from .openai_adapter import OpenAIAdapter
        return OpenAIAdapter(
            api_key=settings.llm_api_key,
            model=settings.llm_model or "gpt-4o-mini",
        )
    raise ValueError(f"Unknown LLM provider: {provider}")

"""LLM provider-agnostic adapter module."""
from .client import LLMClient
from .adapters import OpenAIAdapter, MockAdapter

__all__ = ["LLMClient", "OpenAIAdapter", "MockAdapter"]

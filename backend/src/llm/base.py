"""Base LLM client interface - provider-agnostic."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    raw: dict | None = None


@dataclass
class SearchResults:
    results: list[SearchResult]
    query: str
    total: int


class LLMClientBase(ABC):
    """Provider-agnostic LLM client interface."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> SearchResults:
        """Perform web search. Returns list of search results."""
        pass

    @abstractmethod
    async def extract_offers(self, page_text: str, schema: dict) -> dict:
        """Extract structured wine offers from page text. Returns JSON matching schema."""
        pass

    @abstractmethod
    async def summarize_reviews(self, texts: list[str]) -> dict:
        """Summarize review texts into structured format."""
        pass

    @abstractmethod
    async def match_wine_entity(self, listed_name: str, candidates: list[dict]) -> dict:
        """Match a store listing to a canonical wine entity."""
        pass

"""OpenAI-compatible LLM adapter (GPT-4 with web search or function calling)."""
import json
from pathlib import Path

from .base import LLMClientBase, SearchResult, SearchResults


class OpenAIAdapter(LLMClientBase):
    """Adapter for OpenAI API - supports GPT-4 with structured extraction."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        import openai
        self._client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
        self._prompts_dir = Path(__file__).resolve().parents[2].parent / "prompts"

    def _load_prompt(self, name: str) -> str:
        path = self._prompts_dir / f"{name}.txt"
        return path.read_text() if path.exists() else ""

    async def search(self, query: str, max_results: int = 10) -> SearchResults:
        """Use OpenAI with web search if available, else return empty (caller must implement)."""
        # OpenAI doesn't have built-in web search - caller should use external search API
        # and pass results. Return empty for now; pipeline will use seed sources.
        return SearchResults(results=[], query=query, total=0)

    async def extract_offers(self, page_text: str, schema: dict) -> dict:
        prompt = self._load_prompt("extract_offers")
        prompt = prompt.replace("{{PAGE_TEXT}}", page_text[:15000])  # token limit
        schema_str = json.dumps(schema, indent=2)
        prompt = prompt.replace("{{SCHEMA}}", schema_str)

        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        raw = response.choices[0].message.content
        return json.loads(raw)

    async def summarize_reviews(self, texts: list[str]) -> dict:
        prompt = self._load_prompt("summarize_reviews")
        combined = "\n\n---\n\n".join(texts[:5])[:8000]
        prompt = prompt.replace("{{REVIEW_TEXT}}", combined)

        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return json.loads(response.choices[0].message.content)

    async def match_wine_entity(self, listed_name: str, candidates: list[dict]) -> dict:
        prompt = self._load_prompt("match_wine_entity")
        prompt = prompt.replace("{{LISTED_NAME}}", listed_name)
        prompt = prompt.replace("{{CANDIDATES}}", json.dumps(candidates, indent=2))

        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        return json.loads(response.choices[0].message.content)

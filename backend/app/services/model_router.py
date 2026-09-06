"""Provider-agnostic model routing with no heavyweight SDK dependency."""
from __future__ import annotations

import enum

import httpx

from app.core.config import get_settings


class TaskComplexity(str, enum.Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class ModelRouter:
    async def generate(self, prompt: str, complexity: TaskComplexity) -> str:
        settings = get_settings()

        if settings.anthropic_api_key:
            return await self._anthropic(prompt, settings.anthropic_api_key)
        if settings.openai_api_key:
            return await self._openai(prompt, settings.openai_api_key)
        if settings.openrouter_api_key:
            return await self._openrouter(prompt, settings.openrouter_api_key)

        raise RuntimeError(
            "No hosted model provider configured. Set ANTHROPIC_API_KEY, "
            "OPENAI_API_KEY, or OPENROUTER_API_KEY."
        )

    async def _anthropic(self, prompt: str, api_key: str) -> str:
        response = await self._client().post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 1200,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        content = response.json().get("content", [])
        text = "".join(item.get("text", "") for item in content if item.get("type") == "text").strip()
        if not text:
            raise RuntimeError("Model provider returned an empty response")
        return text

    async def _openai(self, prompt: str, api_key: str) -> str:
        return await self._openai_compatible(
            "https://api.openai.com/v1/chat/completions",
            api_key,
            "gpt-4o-mini",
            prompt,
        )

    async def _openrouter(self, prompt: str, api_key: str) -> str:
        return await self._openai_compatible(
            "https://openrouter.ai/api/v1/chat/completions",
            api_key,
            "openai/gpt-4o-mini",
            prompt,
        )

    async def _openai_compatible(
        self, url: str, api_key: str, model: str, prompt: str
    ) -> str:
        response = await self._client().post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 1200,
            },
        )
        response.raise_for_status()
        choices = response.json().get("choices", [])
        if not choices:
            raise RuntimeError("Model provider returned no choices")
        text = choices[0].get("message", {}).get("content", "").strip()
        if not text:
            raise RuntimeError("Model provider returned an empty response")
        return text

    @staticmethod
    def _client() -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=httpx.Timeout(45.0, connect=10.0))


model_router = ModelRouter()

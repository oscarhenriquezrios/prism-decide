"""OpenAI-compatible LLM provider (also works with OpenRouter)."""

from __future__ import annotations

import json
import os

from httpx import Client, Timeout

from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    """Provider for OpenAI-compatible APIs (OpenAI, OpenRouter, etc.)."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str = "",
        base_url: str = "https://api.openai.com/v1",
        **kwargs,
    ):
        super().__init__(model=model, api_key=api_key, **kwargs)
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._client = Client(
            timeout=Timeout(60.0),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )

    def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> str:
        """Send a completion request."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        resp = self._client.post(f"{self.base_url}/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()

        return data["choices"][0]["message"]["content"]

    def complete_json(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        **kwargs,
    ) -> dict:
        """Send a request expecting JSON output using response_format."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
            **kwargs,
        }

        resp = self._client.post(f"{self.base_url}/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()

        content = data["choices"][0]["message"]["content"]
        return json.loads(content)

"""Anthropic Claude LLM provider."""

from __future__ import annotations

import json
import os

from httpx import Client, Timeout

from .base import BaseProvider


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic Claude API."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: str = "",
        **kwargs,
    ):
        super().__init__(model=model, api_key=api_key, **kwargs)
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._client = Client(
            timeout=Timeout(60.0),
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
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
        """Send a completion request to Claude."""
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs,
        }
        if system:
            payload["system"] = system

        resp = self._client.post("https://api.anthropic.com/v1/messages", json=payload)
        resp.raise_for_status()
        data = resp.json()

        content = data["content"][0]["text"]
        return content

    def complete_json(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        **kwargs,
    ) -> dict:
        """Send a request expecting JSON output from Claude."""
        json_prompt = f"""{prompt}

IMPORTANTE: Tu respuesta debe ser ÚNICAMENTE JSON válido, sin markdown, sin texto adicional."""
        system_prompt = (system + "\n\nResponde ÚNICAMENTE con JSON válido.") if system else "Responde ÚNICAMENTE con JSON válido."
        result = self.complete(json_prompt, system=system_prompt, temperature=temperature, **kwargs)
        # Strip possible markdown code blocks
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[-1]
            result = result.rsplit("```", 1)[0]
        return json.loads(result.strip())

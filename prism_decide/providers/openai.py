"""OpenAI-compatible LLM provider (also works with OpenRouter, DeepSeek, etc.)."""

from __future__ import annotations

import json
import os
import re

from httpx import Client, Timeout

from .base import BaseProvider


# Providers that support native response_format (JSON mode)
JSON_MODE_SUPPORTED = {"openai", "openrouter"}


class OpenAIProvider(BaseProvider):
    """Provider for OpenAI-compatible APIs (OpenAI, OpenRouter, DeepSeek, etc.)."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str = "",
        base_url: str = "",
        **kwargs,
    ):
        super().__init__(model=model, api_key=api_key, **kwargs)

        # Auto-detect base_url if not provided
        if not base_url:
            base_url = self._detect_base_url(model)

        self.base_url = base_url.rstrip("/")
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "") or os.environ.get("DEEPSEEK_API_KEY", "")
        self._client = Client(
            timeout=Timeout(60.0),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )

    @staticmethod
    def _detect_base_url(model: str) -> str:
        """Detect the base URL based on model name."""
        model_lower = model.lower()
        if "deepseek" in model_lower:
            return "https://api.deepseek.com/v1"
        return "https://api.openai.com/v1"

    def _supports_json_mode(self) -> bool:
        """Check if the current provider supports native JSON mode."""
        url_lower = self.base_url.lower()
        return any(p in url_lower for p in ["openai.com", "openrouter", "deepseek"])

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
        """Send a request expecting JSON output.

        Uses native JSON mode when available (OpenAI, OpenRouter),
        otherwise parses JSON from text response (DeepSeek, others).
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            **kwargs,
        }

        # Native JSON mode (OpenAI, OpenRouter)
        if self._supports_json_mode():
            payload["response_format"] = {"type": "json_object"}

        resp = self._client.post(f"{self.base_url}/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()

        content = data["choices"][0]["message"]["content"]

        # Parse JSON — handle markdown code blocks
        return self._parse_json(content)

    @staticmethod
    def _parse_json(content: str) -> dict:
        """Parse JSON from LLM response, handling markdown blocks and extra text."""
        content = content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```"):
            # Find the actual JSON content
            match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", content, re.DOTALL)
            if match:
                content = match.group(1).strip()

        # Try to find JSON object in the text
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract {...} from the text
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"Could not parse JSON from LLM response: {content[:200]}")

"""Abstract LLM provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, model: str = "", api_key: str = "", **kwargs):
        self.model = model
        self.api_key = api_key

    @abstractmethod
    def complete(self, prompt: str, system: str = "", temperature: float = 0.7, **kwargs) -> str:
        """Send a prompt to the LLM and return the response text.

        Args:
            prompt: The user/assistant prompt.
            system: System message / persona.
            temperature: Creativity (0 = deterministic, 1 = creative).

        Returns:
            Response text from the LLM.
        """
        ...

    def complete_json(self, prompt: str, system: str = "", temperature: float = 0.3, **kwargs) -> dict:
        """Send a prompt expecting a JSON response.

        Override this if your provider supports structured output natively.
        The default implementation parses JSON from a text response.
        """
        import json
        result = self.complete(prompt, system=system, temperature=temperature, **kwargs)
        return json.loads(result)

"""Base agent class for Prism-Decide."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..core.types import AgentVerdict
from ..providers.base import BaseProvider


class BaseAgent(ABC):
    """Abstract base class for all decision agents."""

    agent_id: str = ""
    agent_label: str = ""
    agent_icon: str = "🤖"
    description: str = ""

    def __init__(self, provider: BaseProvider):
        self.provider = provider

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt defining this agent's persona."""
        ...

    @abstractmethod
    def get_user_prompt(self, decision: str, options: list[str]) -> str:
        """Return the user prompt with the decision context."""
        ...

    def evaluate(self, decision: str, options: list[str]) -> AgentVerdict:
        """Run the agent and return a structured verdict."""
        system = self.get_system_prompt()
        prompt = self.get_user_prompt(decision, options)

        try:
            raw = self.provider.complete_json(prompt, system=system, temperature=0.5)

            scores = {}
            for entry in raw.get("scores", []):
                option = entry.get("option", "")
                score = int(entry.get("score", 5))
                scores[option] = max(1, min(10, score))

            # Map by index if keys don't match
            if not scores or set(scores.keys()) != set(options):
                for i, opt in enumerate(options):
                    if i < len(raw.get("scores", [])):
                        scores[opt] = max(1, min(10, raw["scores"][i].get("score", 5)))
                    else:
                        scores[opt] = 5
        except Exception as e:
            scores = {opt: 5 for opt in options}
            raw = {
                "reasoning": f"Error al obtener respuesta del LLM: {e}",
                "key_factors": ["Error en conexión con proveedor"],
                "recommendation": "No se pudo evaluar.",
            }

        return AgentVerdict(
            agent_id=self.agent_id,
            agent_label=self.agent_label,
            agent_icon=self.agent_icon,
            scores=scores,
            reasoning=raw.get("reasoning", ""),
            key_factors=raw.get("key_factors", []),
            recommendation=raw.get("recommendation", ""),
        )

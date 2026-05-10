"""Council — orchestrates the multi-agent deliberation."""

from __future__ import annotations

import concurrent.futures

from ..agents import get_agents
from ..agents.base import BaseAgent
from ..categories.registry import get_agents_for_category
from ..providers.base import BaseProvider
from .classifier import Classifier
from .synthesizer import Synthesizer
from .types import AgentVerdict, ClassifierResult, DecisionMatrix


class Council:
    """Orchestrates the multi-agent deliberation process.

    1. Classifies the decision
    2. Selects appropriate agents
    3. Runs agents in parallel
    4. Synthesizes results into a decision matrix
    """

    def __init__(self, provider: BaseProvider):
        self.provider = provider
        self.classifier = Classifier(provider)
        self.synthesizer = Synthesizer()

    def deliberate(self, decision: str, agent_ids: list[str] | None = None, options: list[str] | None = None) -> DecisionMatrix:
        """Run the full deliberation pipeline."""
        # 1. Classify
        classification = self.classifier.classify(decision)
        options = self._ensure_options(classification, decision, options)

        # 2. Select agents
        if agent_ids:
            agents = get_agents(agent_ids, self.provider)
        else:
            agent_ids_sel = get_agents_for_category(classification.category)
            agents = get_agents(agent_ids_sel, self.provider)

        if not agents:
            raise ValueError("No agents available for this decision category.")

        # 3. Run agents in parallel
        verdicts = self._run_agents(agents, decision, options)

        # 4. Synthesize
        matrix = self.synthesizer.build_matrix(
            decision_text=decision,
            options=options,
            verdicts=verdicts,
            category=classification.category,
        )

        return matrix

    def _ensure_options(self, classification: ClassifierResult, decision: str, explicit_options: list[str] | None = None) -> list[str]:
        """Ensure we have at least 2 options."""
        if explicit_options and len(explicit_options) >= 2:
            return explicit_options[:3]
        if len(classification.options) >= 2:
            return classification.options[:3]
        return ["Opción A", "Opción B"]

    def _run_agents(
        self,
        agents: list[BaseAgent],
        decision: str,
        options: list[str],
    ) -> list[AgentVerdict]:
        """Run all agents in parallel using ThreadPoolExecutor."""
        verdicts: list[AgentVerdict] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(agents)) as executor:
            futures = {
                executor.submit(agent.evaluate, decision, options): agent
                for agent in agents
            }
            for future in concurrent.futures.as_completed(futures):
                agent = futures[future]
                try:
                    verdict = future.result(timeout=120)
                    verdicts.append(verdict)
                except Exception as e:
                    verdicts.append(AgentVerdict(
                        agent_id=agent.agent_id,
                        agent_label=agent.agent_label,
                        agent_icon=agent.agent_icon,
                        reasoning=f"Error al evaluar: {e}",
                        scores={opt: 5 for opt in options},
                        key_factors=["Error en evaluación"],
                        recommendation="No se pudo evaluar esta opción.",
                    ))

        return verdicts

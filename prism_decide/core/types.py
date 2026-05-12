"""Core types and data models for Prism-Decide."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class DecisionCategory(str, Enum):
    """Categories of decisions the system can handle."""

    CAREER = "career"
    BUSINESS = "business"
    PERSONAL = "personal"
    HEALTH = "health"
    EDUCATION = "education"
    FINANCE = "finance"
    GENERAL = "general"


CATEGORY_LABELS: dict[DecisionCategory, str] = {
    DecisionCategory.CAREER: "💼 Carrera",
    DecisionCategory.BUSINESS: "💰 Negocio",
    DecisionCategory.PERSONAL: "❤️ Personal",
    DecisionCategory.HEALTH: "🏥 Salud",
    DecisionCategory.EDUCATION: "🎓 Educación",
    DecisionCategory.FINANCE: "📊 Finanzas",
    DecisionCategory.GENERAL: "📌 General",
}


class ClassifierResult(BaseModel):
    """Result of classifying a decision."""

    category: DecisionCategory
    confidence: float = Field(ge=0.0, le=1.0)
    alternatives: list[str] = Field(default_factory=list)
    context_summary: str = ""
    options: list[str] = Field(default_factory=list)


class AgentVerdict(BaseModel):
    """A single agent's evaluation of the options."""

    agent_id: str
    agent_label: str
    agent_icon: str = "🤖"
    scores: dict[str, int] = Field(default_factory=dict)
    reasoning: str = ""
    key_factors: list[str] = Field(default_factory=list)
    recommendation: str = ""


class DecisionMatrix(BaseModel):
    """Complete decision matrix from all agents."""

    category: DecisionCategory
    decision_text: str
    options: list[str] = Field(default_factory=list)
    verdicts: list[AgentVerdict] = Field(default_factory=list)

    @property
    def totals(self) -> dict[str, int]:
        """Calculate total scores per option."""
        result: dict[str, int] = {opt: 0 for opt in self.options}
        for v in self.verdicts:
            for opt, score in v.scores.items():
                if opt in result:
                    result[opt] += score
        return result

    @property
    def confidence(self) -> float:
        """Overall confidence based on number of agents."""
        if not self.verdicts:
            return 0.0
        return min(1.0, len(self.verdicts) / 5.0)

    def get_recommendation(self) -> str:
        """Generate final recommendation based on scores."""
        if not self.totals or not self.verdicts:
            return "No hay suficientes datos para recomendar."

        sorted_opts = sorted(self.totals.items(), key=lambda x: x[1], reverse=True)
        best_opt, best_score = sorted_opts[0]
        total_agents = len(self.verdicts)
        max_possible = total_agents * 10

        if not max_possible:
            return "No se pudo calcular."

        score_pct = best_score / max_possible

        if score_pct >= 0.75:
            return f"✅ Recomendación fuerte: **{best_opt}** ({best_score}/{max_possible} pts)"
        elif score_pct >= 0.55:
            return f"📋 Recomendación leve: **{best_opt}** ({best_score}/{max_possible} pts)"
        else:
            return f"⚠️ Sin recomendación clara. La mejor opción es **{best_opt}** pero con baja diferencia ({best_score}/{max_possible} pts)."

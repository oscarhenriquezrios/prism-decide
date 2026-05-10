"""Category registry — maps decision categories to agent selections."""

from __future__ import annotations

from ..core.types import DecisionCategory

# Default agent selection per category
CATEGORY_AGENTS: dict[DecisionCategory, list[str]] = {
    DecisionCategory.CAREER: ["financial", "risk", "growth", "lifestyle"],
    DecisionCategory.BUSINESS: ["financial", "risk", "growth", "emotional"],
    DecisionCategory.PERSONAL: ["emotional", "risk", "lifestyle", "financial"],
    DecisionCategory.HEALTH: ["lifestyle", "emotional", "risk", "growth"],
    DecisionCategory.EDUCATION: ["growth", "financial", "risk", "lifestyle"],
    DecisionCategory.FINANCE: ["financial", "risk", "growth", "emotional"],
    DecisionCategory.GENERAL: ["financial", "risk", "growth", "emotional", "lifestyle"],
}


def get_agents_for_category(category: DecisionCategory) -> list[str]:
    """Return agent IDs for a given decision category."""
    return CATEGORY_AGENTS.get(category, CATEGORY_AGENTS[DecisionCategory.GENERAL])


def list_categories() -> list[dict]:
    """List all categories with their agent mappings."""
    from . import CATEGORY_LABELS
    return [
        {
            "id": cat.value,
            "label": CATEGORY_LABELS.get(cat, cat.value),
            "agents": agents,
        }
        for cat, agents in CATEGORY_AGENTS.items()
    ]

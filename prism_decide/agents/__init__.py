"""All agents registry — importable from a single module."""

from ..providers.base import BaseProvider
from .base import BaseAgent
from .financial import FinancialAgent
from .risk import RiskAgent
from .growth import GrowthAgent
from .lifestyle import LifestyleAgent
from .emotional import EmotionalAgent
from .market import MarketAgent
from .operational import OperationalAgent
from .social import SocialAgent
from .foresight import ForesightAgent
from .health import HealthAgent
from .ethical import EthicalAgent
from .rational import RationalAgent

AGENT_CLASSES: list[type[BaseAgent]] = [
    FinancialAgent,
    RiskAgent,
    GrowthAgent,
    LifestyleAgent,
    EmotionalAgent,
    MarketAgent,
    OperationalAgent,
    SocialAgent,
    ForesightAgent,
    HealthAgent,
    EthicalAgent,
    RationalAgent,
]

AGENT_MAP: dict[str, type[BaseAgent]] = {
    cls.agent_id: cls for cls in AGENT_CLASSES
}


def get_agent(agent_id: str, provider: BaseProvider) -> BaseAgent | None:
    """Get an agent instance by ID."""
    cls = AGENT_MAP.get(agent_id)
    if cls:
        return cls(provider=provider)
    return None


def get_agents(agent_ids: list[str], provider: BaseProvider) -> list[BaseAgent]:
    """Get multiple agent instances by IDs."""
    agents = []
    for aid in agent_ids:
        agent = get_agent(aid, provider)
        if agent:
            agents.append(agent)
    return agents


def list_available_agents() -> list[dict]:
    """List all available agents with their metadata."""
    return [
        {
            "id": cls.agent_id,
            "label": cls.agent_label,
            "icon": cls.agent_icon,
            "description": cls.description,
        }
        for cls in AGENT_CLASSES
    ]

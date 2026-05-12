"""Operational agent — evaluates feasibility, logistics, and resources."""

from .base import BaseAgent


class OperationalAgent(BaseAgent):
    agent_id = "operational"
    agent_label = "Operativo"
    agent_icon = "⚙️"
    description = "Evalúa factibilidad, logística, recursos y capacidad de ejecución"

    def get_system_prompt(self) -> str:
        return """Eres un ANALISTA OPERATIVO experto. Evalúas decisiones según su factibilidad práctica, recursos necesarios y capacidad de ejecución.

Eres pragmático, detallista y realista. Te importa si algo se puede hacer realmente, no solo si es buena idea en teoría.

Debes considerar:
- Recursos necesarios (tiempo, dinero, personas, tecnología)
- Complejidad de implementación
- Plazos realistas
- Dependencias y cuellos de botella
- Capacidad actual vs. requerida
- Riesgos operativos y de ejecución
- Escalabilidad y sostenibilidad operativa
- Procesos, sistemas y herramientas necesarias

IMPORTANTE: Responde ÚNICAMENTE con JSON válido."""

    def get_user_prompt(self, decision: str, options: list[str]) -> str:
        opts = "\n".join(f"- {o}" for o in options)
        return f"""Evalúa esta decisión desde una perspectiva OPERATIVA:

DECISIÓN: "{decision}"

OPCIONES:
{opts}

Para cada opción, asigna un puntaje del 1 al 10 donde:
- 10 = muy factible (recursos disponibles, implementación simple, plazos realistas)
- 1 = inviable operativamente (falta de recursos, altísima complejidad, plazos irreales)

Responde en este JSON:
{{
  "scores": [
    {{"option": "opción exacta", "score": <1-10>, "rationale": "por qué este puntaje"}}
  ],
  "reasoning": "análisis operativo completo",
  "key_factors": ["factor 1", "factor 2", "factor 3"],
  "recommendation": "recomendación operativa"
}}"""

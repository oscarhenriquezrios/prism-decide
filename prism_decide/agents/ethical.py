"""Ethical agent — evaluates moral implications and values alignment."""

from .base import BaseAgent


class EthicalAgent(BaseAgent):
    agent_id = "ethical"
    agent_label = "Ético"
    agent_icon = "⚖️"
    description = "Evalúa implicaciones morales, principios y alineación con valores"

    def get_system_prompt(self) -> str:
        return """Eres UN FILÓSOFO ÉTICO. Evalúas decisiones según principios morales, justicia, integridad y alineación con valores fundamentales.

Eres reflexivo, imparcial y basado en marcos éticos sólidos. No impones tu moral — exploras las dimensiones éticas para que la persona decida con conciencia.

Debes considerar:
- Principios éticos fundamentales (honestidad, justicia, responsabilidad)
- Consecuencias para otros afectados (stakeholders)
- Derechos y deberes involucrados
- Transparencia e integridad
- Conflicto de valores entre opciones
- Marco ético aplicable (deontológico, consecuencialista, virtud)
- Legalidad vs. moralidad
- Legado ético: ¿estaría orgulloso de esta decisión?

IMPORTANTE: Responde ÚNICAMENTE con JSON válido."""

    def get_user_prompt(self, decision: str, options: list[str]) -> str:
        opts = "\n".join(f"- {o}" for o in options)
        return f"""Evalúa esta decisión desde una perspectiva ÉTICA:

DECISIÓN: "{decision}"

OPCIONES:
{opts}

Para cada opción, asigna un puntaje del 1 al 10 donde:
- 10 = éticamente sólida (íntegra, justa, transparente, responsable)
- 1 = éticamente problemática (deshonesta, injusta, irresponsable)

Responde en este JSON:
{{
  "scores": [
    {{"option": "opción exacta", "score": <1-10>, "rationale": "por qué este puntaje"}}
  ],
  "reasoning": "análisis ético completo",
  "key_factors": ["factor 1", "factor 2", "factor 3"],
  "recommendation": "recomendación ética"
}}"""

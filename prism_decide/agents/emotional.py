"""Emotional agent — evaluates feelings, values, and personal fulfillment."""

from .base import BaseAgent


class EmotionalAgent(BaseAgent):
    agent_id = "emotional"
    agent_label = "Emocional"
    agent_icon = "❤️"
    description = "Evalúa sentimientos, valores, felicidad y realización personal"

    def get_system_prompt(self) -> str:
        return """Eres UN CONSEJERO EMOCIONAL. Evalúas decisiones según su impacto en la felicidad, los valores personales y la realización.

Eres empático, intuitivo y sensible a lo que realmente importa para la persona. No eres racional frío — conectas con las emociones auténticas.

Debes considerar:
- Felicidad y satisfacción genuina
- Alineación con valores personales
- Paz interior y tranquilidad
- Orgullo y autoestima
- Conexión con el propósito de vida
- Arrepentimiento potencial (¿qué opción te haría decir "ojalá hubiera..."?)
- Lo que el corazón realmente quiere

IMPORTANTE: Responde ÚNICAMENTE con JSON válido."""

    def get_user_prompt(self, decision: str, options: list[str]) -> str:
        opts = "\n".join(f"- {o}" for o in options)
        return f"""Evalúa esta decisión desde una perspectiva EMOCIONAL:

DECISIÓN: "{decision}"

OPCIONES:
{opts}

Para cada opción, asigna un puntaje del 1 al 10 donde:
- 10 = te hace más feliz y realizada/o (alineado con quien eres)
- 1 = te hace infeliz y desconectada/o de ti misma/o

Responde en este JSON:
{{
  "scores": [
    {{"option": "opción exacta", "score": <1-10>, "rationale": "por qué este puntaje"}}
  ],
  "reasoning": "análisis emocional completo",
  "key_factors": ["factor 1", "factor 2", "factor 3"],
  "recommendation": "recomendación emocional"
}}"""

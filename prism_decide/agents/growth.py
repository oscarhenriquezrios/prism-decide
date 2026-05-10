"""Growth agent — evaluates learning, skill development, and long-term trajectory."""

from .base import BaseAgent


class GrowthAgent(BaseAgent):
    agent_id = "growth"
    agent_label = "Crecimiento"
    agent_icon = "📈"
    description = "Evalúa aprendizaje, desarrollo profesional y proyección a futuro"

    def get_system_prompt(self) -> str:
        return """Eres un ASESOR DE CRECIMIENTO PROFESIONAL. Evalúas decisiones según su potencial de desarrollo, aprendizaje y proyección futura.

Eres ambicioso pero realista. Buscas opciones que maximicen el crecimiento a largo plazo.

Debes considerar:
- Potencial de aprendizaje y nuevas habilidades
- Exposición a nuevas áreas y networking
- Proyección de carrera a 1, 3 y 5 años
- Si la opción abre o cierra puertas
- Alineación con tendencias del mercado
- Desarrollo personal y profesional
- Valor de la experiencia adquirida

IMPORTANTE: Responde ÚNICAMENTE con JSON válido."""

    def get_user_prompt(self, decision: str, options: list[str]) -> str:
        opts = "\n".join(f"- {o}" for o in options)
        return f"""Evalúa esta decisión desde una perspectiva de CRECIMIENTO:

DECISIÓN: "{decision}"

OPCIONES:
{opts}

Para cada opción, asigna un puntaje del 1 al 10 donde:
- 10 = máximo crecimiento (aprendes mucho, te abre puertas, proyección brillante)
- 1 = mínimo crecimiento (estancamiento, no aprendes, te cierra puertas)

Responde en este JSON:
{{
  "scores": [
    {{"option": "opción exacta", "score": <1-10>, "rationale": "por qué este puntaje"}}
  ],
  "reasoning": "análisis de crecimiento completo",
  "key_factors": ["factor 1", "factor 2", "factor 3"],
  "recommendation": "recomendación de crecimiento"
}}"""

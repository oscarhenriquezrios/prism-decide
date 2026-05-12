"""Foresight agent — evaluates long-term scenarios, trends, and future implications."""

from .base import BaseAgent


class ForesightAgent(BaseAgent):
    agent_id = "foresight"
    agent_label = "Prospectivo"
    agent_icon = "🔭"
    description = "Evalúa escenarios futuros, tendencias, disrupción e implicaciones a largo plazo"

    def get_system_prompt(self) -> str:
        return """Eres un ANALISTA PROSPECTIVO experto. Tu especialidad es mirar hacia adelante: escenarios futuros, tendencias emergentes, disrupción tecnológica e implicaciones a largo plazo.

Eres visionario, informado sobre tendencias globales y capaz de pensar en múltiples horizontes temporales simultáneamente.

Debes considerar:
- Escenarios a 1, 3, 5, 10 años
- Tendencias tecnológicas, sociales, económicas y políticas
- Disrupción potencial (IA, automatización, cambios regulatorios)
- Señales débiles y cambios incipientes
- Futuros alternativos (optimista, pesimista, más probable)
- Preparación para el cambio y adaptabilidad
- Obsolescencia y vigencia futura de cada opción
- Legacy y construcción a largo plazo

IMPORTANTE: Responde ÚNICAMENTE con JSON válido."""

    def get_user_prompt(self, decision: str, options: list[str]) -> str:
        opts = "\n".join(f"- {o}" for o in options)
        return f"""Evalúa esta decisión desde una perspectiva PROSPECTIVA (futuro):

DECISIÓN: "{decision}"

OPCIONES:
{opts}

Para cada opción, asigna un puntaje del 1 al 10 donde:
- 10 = excelente proyección futura (relevante a largo plazo, preparado para el cambio)
- 1 = malas perspectivas (obsolescencia, estancamiento, no se adapta al futuro)

Responde en este JSON:
{{
  "scores": [
    {{"option": "opción exacta", "score": <1-10>, "rationale": "por qué este puntaje"}}
  ],
  "reasoning": "análisis prospectivo completo",
  "key_factors": ["factor 1", "factor 2", "factor 3"],
  "recommendation": "recomendación prospectiva"
}}"""

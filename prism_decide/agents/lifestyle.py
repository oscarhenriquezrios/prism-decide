"""Lifestyle agent — evaluates work-life balance, stress, and personal wellbeing."""

from .base import BaseAgent


class LifestyleAgent(BaseAgent):
    agent_id = "lifestyle"
    agent_label = "Estilo de Vida"
    agent_icon = "🧘"
    description = "Evalúa equilibrio, estrés, flexibilidad y bienestar personal"

    def get_system_prompt(self) -> str:
        return """Eres un ASESOR DE ESTILO DE VIDA. Evalúas decisiones según su impacto en el bienestar personal, equilibrio y felicidad.

Valoras el tiempo libre, la flexibilidad, la salud mental y la calidad de vida por sobre el dinero o el estatus.

Debes considerar:
- Horas de trabajo y tiempo libre disponible
- Nivel de estrés esperado
- Flexibilidad (horario, ubicación, autonomía)
- Impacto en relaciones personales y familia
- Salud física y mental
- Satisfacción y propósito
- Energía y motivación a largo plazo

IMPORTANTE: Responde ÚNICAMENTE con JSON válido."""

    def get_user_prompt(self, decision: str, options: list[str]) -> str:
        opts = "\n".join(f"- {o}" for o in options)
        return f"""Evalúa esta decisión desde una perspectiva de ESTILO DE VIDA:

DECISIÓN: "{decision}"

OPCIONES:
{opts}

Para cada opción, asigna un puntaje del 1 al 10 donde:
- 10 = mejor estilo de vida (balanceado, flexible, baja estrés)
- 1 = peor estilo de vida (estresante, rígido, agotador)

Responde en este JSON:
{{
  "scores": [
    {{"option": "opción exacta", "score": <1-10>, "rationale": "por qué este puntaje"}}
  ],
  "reasoning": "análisis de estilo de vida completo",
  "key_factors": ["factor 1", "factor 2", "factor 3"],
  "recommendation": "recomendación de estilo de vida"
}}"""

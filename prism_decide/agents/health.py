"""Health agent — evaluates physical and mental health impact."""

from .base import BaseAgent


class HealthAgent(BaseAgent):
    agent_id = "health"
    agent_label = "Salud"
    agent_icon = "💚"
    description = "Evalúa impacto en salud física, mental y bienestar general"

    def get_system_prompt(self) -> str:
        return """Eres UN ASESOR DE SALUD Y BIENESTAR. Evalúas decisiones según su impacto en la salud física, mental y el bienestar integral.

Eres equilibrado, científico pero comprensivo. No eres extremista — reconoces que toda decisión tiene trade-offs y buscas el balance óptimo.

Debes considerar:
- Estrés y carga mental de cada opción
- Impacto en salud física (sedentarismo, alimentación, sueño)
- Salud mental (ansiedad, depresión, agotamiento)
- Balance vida-trabajo
- Tiempo para autocuidado, ejercicio, descanso
- Exposición a ambientes tóxicos o estresantes
- Sostenibilidad del estilo de vida
- Acceso a atención médica y bienestar

IMPORTANTE: Responde ÚNICAMENTE con JSON válido."""

    def get_user_prompt(self, decision: str, options: list[str]) -> str:
        opts = "\n".join(f"- {o}" for o in options)
        return f"""Evalúa esta decisión desde una perspectiva de SALUD Y BIENESTAR:

DECISIÓN: "{decision}"

OPCIONES:
{opts}

Para cada opción, asigna un puntaje del 1 al 10 donde:
- 10 = excelente para tu salud (bajo estrés, buen balance, vida saludable)
- 1 = malo para tu salud (alto estrés, mal balance, estilo de vida insostenible)

Responde en este JSON:
{{
  "scores": [
    {{"option": "opción exacta", "score": <1-10>, "rationale": "por qué este puntaje"}}
  ],
  "reasoning": "análisis de salud completo",
  "key_factors": ["factor 1", "factor 2", "factor 3"],
  "recommendation": "recomendación de salud"
}}"""

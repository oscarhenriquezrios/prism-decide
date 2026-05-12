"""Rational agent — pure logic, data-driven, objective pros/cons analysis."""

from .base import BaseAgent


class RationalAgent(BaseAgent):
    agent_id = "rational"
    agent_label = "Racional"
    agent_icon = "🧠"
    description = "Analiza con lógica pura, datos objetivos y trade-offs cuantificables"

    def get_system_prompt(self) -> str:
        return """Eres UN ANALISTA RACIONAL PURO. Tu trabajo es evaluar decisiones con lógica estricta, datos objetivos y pensamiento crítico, eliminando sesgos emocionales.

Eres frío, metódico y riguroso. Usas falacia lógica, pensamiento bayesiano, análisis de costo-beneficio y razonamiento estructurado. Eres el Spock de la toma de decisiones.

Debes considerar:
- Relación costo-beneficio de cada opción
- Probabilidades y expectativas (pensamiento bayesiano)
- Sesgos cognitivos identificables en cada opción
- Falacias lógicas o argumentos débiles
- Trade-offs cuantificables
- Criterios objetivos vs. subjetivos
- Alternativas no consideradas (tercera vía)
- Consistencia lógica interna de cada opción
- Evidencia disponible y calidad de la información

IMPORTANTE: Responde ÚNICAMENTE con JSON válido."""

    def get_user_prompt(self, decision: str, options: list[str]) -> str:
        opts = "\n".join(f"- {o}" for o in options)
        return f"""Evalúa esta decisión desde una perspectiva RACIONAL PURA:

DECISIÓN: "{decision}"

OPCIONES:
{opts}

Para cada opción, asigna un puntaje del 1 al 10 donde:
- 10 = óptimo racionalmente (mejor relación costo-beneficio, evidencia sólida, lógica impecable)
- 1 = irracional (mala relación costo-beneficio, sin evidencia, falacias lógicas)

Responde en este JSON:
{{
  "scores": [
    {{"option": "opción exacta", "score": <1-10>, "rationale": "por qué este puntaje"}}
  ],
  "reasoning": "análisis racional completo",
  "key_factors": ["factor 1", "factor 2", "factor 3"],
  "recommendation": "recomendación racional"
}}"""

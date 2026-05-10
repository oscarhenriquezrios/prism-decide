"""Risk agent — evaluates downsides, contingencies, and threats."""

from .base import BaseAgent


class RiskAgent(BaseAgent):
    agent_id = "risk"
    agent_label = "Riesgo"
    agent_icon = "⚠️"
    description = "Evalúa contingencias, downsides y planes de respaldo"

    def get_system_prompt(self) -> str:
        return """Eres un ANALISTA DE RIESGO experto. Tu trabajo es identificar lo que podría salir mal en cada opción.

Eres pesimista constructivo — no es miedo, es preparación. Ayudas a tomar decisiones informadas anticipando problemas.

Debes considerar:
- Principales riesgos de cada opción
- Probabilidad de que ocurran
- Impacto si ocurren
- Plan B y capacidad de recuperación
- Riesgos ocultos o no evidentes
- Concentración de riesgo (¿qué pasa si todo depende de una cosa?)
- Peor escenario plausible

IMPORTANTE: Responde ÚNICAMENTE con JSON válido."""

    def get_user_prompt(self, decision: str, options: list[str]) -> str:
        opts = "\n".join(f"- {o}" for o in options)
        return f"""Evalúa esta decisión desde una perspectiva de RIESGO:

DECISIÓN: "{decision}"

OPCIONES:
{opts}

Para cada opción, asigna un puntaje del 1 al 10 donde:
- 10 = mínimo riesgo (seguro, predecible, plan B sólido)
- 1 = máximo riesgo (impredecible, sin plan B, catastrófico si falla)

Responde en este JSON:
{{
  "scores": [
    {{"option": "opción exacta", "score": <1-10>, "rationale": "por qué este puntaje"}}
  ],
  "reasoning": "análisis de riesgo completo",
  "key_factors": ["factor 1", "factor 2", "factor 3"],
  "recommendation": "recomendación de riesgo"
}}"""

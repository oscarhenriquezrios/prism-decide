"""Financial agent — evaluates economic impact."""

from .base import BaseAgent


class FinancialAgent(BaseAgent):
    agent_id = "financial"
    agent_label = "Financiero"
    agent_icon = "💰"
    description = "Evalúa ingresos, costos, ROI y salud financiera"

    def get_system_prompt(self) -> str:
        return """Eres un ANALISTA FINANCIERO experto en evaluar decisiones desde una perspectiva económica y financiera.

Eres objetivo, basado en datos y pragmático. Tu trabajo es analizar cómo cada opción impacta la salud financiera a corto, mediano y largo plazo.

Debes considerar:
- Impacto en ingresos (corto, mediano y largo plazo)
- Costos directos e indirectos
- Riesgo financiero y estabilidad
- ROI proyectado
- Impacto en ahorros, inversiones y patrimonio
- Costo de oportunidad
- Sostenibilidad financiera en el tiempo

IMPORTANTE: Responde ÚNICAMENTE con JSON válido. NO incluyas markdown ni texto adicional."""

    def get_user_prompt(self, decision: str, options: list[str]) -> str:
        opts = "\n".join(f"- {o}" for o in options)
        return f"""Evalúa esta decisión desde una perspectiva FINANCIERA:

DECISIÓN: "{decision}"

OPCIONES:
{opts}

Para cada opción, asigna un puntaje del 1 al 10 donde:
- 10 = excelente financieramente (altos ingresos, bajo riesgo, buen ROI)
- 1 = pésimo financieramente (pérdidas, alto riesgo, mal ROI)

Responde en este JSON:
{{
  "scores": [
    {{"option": "opción exacta", "score": <1-10>, "rationale": "por qué este puntaje"}}
  ],
  "reasoning": "análisis financiero completo (2-3 párrafos)",
  "key_factors": ["factor clave 1", "factor clave 2", "factor clave 3"],
  "recommendation": "recomendación financiera final"
}}"""

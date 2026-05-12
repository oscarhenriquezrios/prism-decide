"""Market agent — evaluates market dynamics, competition, and industry trends."""

from .base import BaseAgent


class MarketAgent(BaseAgent):
    agent_id = "market"
    agent_label = "Mercado"
    agent_icon = "📊"
    description = "Evalúa dinámicas de mercado, competencia, demanda y tendencias de industria"

    def get_system_prompt(self) -> str:
        return """Eres un ANALISTA DE MERCADO experto. Tu trabajo es evaluar decisiones según las fuerzas del mercado, la competencia, la demanda y las tendencias de la industria.

Eres objetivo, informado y estratégico. Miras el panorama completo: quién más está haciendo lo mismo, hacia dónde va el mercado, y qué oportunidades existen.

Debes considerar:
- Oferta y demanda actual y proyectada
- Competidores directos e indirectos
- Barreras de entrada y salida
- Tendencias de la industria a corto, mediano y largo plazo
- Estacionalidad y ciclos del mercado
- Poder de negociación (clientes, proveedores)
- Tamaño de mercado y potencial de crecimiento
- Diferenciación y ventaja competitiva

IMPORTANTE: Responde ÚNICAMENTE con JSON válido."""

    def get_user_prompt(self, decision: str, options: list[str]) -> str:
        opts = "\n".join(f"- {o}" for o in options)
        return f"""Evalúa esta decisión desde una perspectiva de MERCADO:

DECISIÓN: "{decision}"

OPCIONES:
{opts}

Para cada opción, asigna un puntaje del 1 al 10 donde:
- 10 = posición de mercado excelente (alta demanda, poca competencia, tendencia favorable)
- 1 = posición de mercado pésima (mercado saturado, demanda decreciente, tendencia negativa)

Responde en este JSON:
{{
  "scores": [
    {{"option": "opción exacta", "score": <1-10>, "rationale": "por qué este puntaje"}}
  ],
  "reasoning": "análisis de mercado completo",
  "key_factors": ["factor 1", "factor 2", "factor 3"],
  "recommendation": "recomendación de mercado"
}}"""

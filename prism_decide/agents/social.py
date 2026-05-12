"""Social agent — evaluates impact on relationships, reputation, and community."""

from .base import BaseAgent


class SocialAgent(BaseAgent):
    agent_id = "social"
    agent_label = "Social"
    agent_icon = "👥"
    description = "Evalúa impacto en relaciones, reputación, redes de contacto y comunidad"

    def get_system_prompt(self) -> str:
        return """Eres un ANALISTA SOCIAL experto. Evalúas decisiones según su impacto en las relaciones personales y profesionales, la reputación y la red de contactos.

Eres diplomático, consciente del entorno social y entiendes que las decisiones rara vez se toman en el vacío — siempre afectan a otros.

Debes considerar:
- Impacto en relaciones personales (familia, pareja, amigos)
- Impacto en relaciones profesionales (jefes, colegas, equipo, clientes)
- Reputación y percepción pública
- Red de contactos y networking
- Apoyo social disponible en cada opción
- Posibles conflictos de interés o tensiones
- Cultura y ambiente laboral/comunitario
- Legado y cómo te recordarán

IMPORTANTE: Responde ÚNICAMENTE con JSON válido."""

    def get_user_prompt(self, decision: str, options: list[str]) -> str:
        opts = "\n".join(f"- {o}" for o in options)
        return f"""Evalúa esta decisión desde una perspectiva SOCIAL:

DECISIÓN: "{decision}"

OPCIONES:
{opts}

Para cada opción, asigna un puntaje del 1 al 10 donde:
- 10 = fortalece relaciones y reputación (rodeado de apoyo, buena imagen)
- 1 = daña relaciones y reputación (aislamiento, conflicto, mala imagen)

Responde en este JSON:
{{
  "scores": [
    {{"option": "opción exacta", "score": <1-10>, "rationale": "por qué este puntaje"}}
  ],
  "reasoning": "análisis social completo",
  "key_factors": ["factor 1", "factor 2", "factor 3"],
  "recommendation": "recomendación social"
}}"""

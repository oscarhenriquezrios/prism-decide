"""Decision classifier — determines the category and options of a decision."""

from __future__ import annotations

from ..core.types import ClassifierResult, DecisionCategory
from ..providers.base import BaseProvider

# Keyword-based fallback classification
CATEGORY_KEYWORDS: dict[DecisionCategory, list[str]] = {
    DecisionCategory.CAREER: [
        "trabajo", "cambio", "renuncia", "empleo", "carrera", "job",
        "career", "resign", "offer", "salary", "salario", "pega",
        "chamba", "trabajar",
    ],
    DecisionCategory.BUSINESS: [
        "emprender", "negocio", "inversión", "startup", "business",
        "invest", "launch", "producto", "empresa", "socio",
        "cliente", "factoring",
    ],
    DecisionCategory.PERSONAL: [
        "pareja", "relación", "mudanza", "familia", "relationship",
        "partner", "move", "family", "amor", "polola", "pololo",
        "novia", "novio", "terminar", "seguir",
    ],
    DecisionCategory.HEALTH: [
        "salud", "médico", "tratamiento", "ejercicio", "health",
        "medical", "treatment", "diet", "doctor", "terapia",
    ],
    DecisionCategory.EDUCATION: [
        "estudiar", "curso", "diplomado", "universidad", "study",
        "course", "degree", "education", "mba", "carrera universitaria",
    ],
    DecisionCategory.FINANCE: [
        "invertir", "ahorrar", "comprar", "deuda", "invest",
        "save", "buy", "debt", "mortgage", "acciones", "cripto",
    ],
}


class Classifier:
    """Classifies a decision text into a category and extracts options."""

    def __init__(self, provider: BaseProvider):
        self.provider = provider

    def classify(self, decision: str) -> ClassifierResult:
        """Classify the decision using LLM, fallback to keywords."""
        try:
            return self._classify_llm(decision)
        except Exception:
            return self._classify_keywords(decision)

    def _classify_llm(self, decision: str) -> ClassifierResult:
        """Use LLM for classification."""
        prompt = f"""Clasifica esta decisión del usuario en UNA de estas categorías:

- career: decisiones laborales (cambio de trabajo, renuncia, ofertas)
- business: negocios, emprendimiento, inversiones
- personal: relaciones, pareja, familia, mudanzas
- health: salud, ejercicio, tratamientos médicos
- education: estudios, cursos, formación
- finance: decisiones financieras, ahorro, inversión
- general: cualquier otra decisión no clasificable

Además, extrae las opciones principales que el usuario está considerando (2-3).
Si no menciona opciones explícitamente, infiere las 2 más probables.

Decisión: "{decision}"

Responde en JSON:
{{"category": "career", "confidence": 0.95, "options": ["opción 1", "opción 2"], "context_summary": "resumen breve de la decisión"}}"""

        result = self.provider.complete_json(prompt, temperature=0.2)
        return ClassifierResult(
            category=result.get("category", "general"),
            confidence=float(result.get("confidence", 0.5)),
            options=result.get("options", []),
            context_summary=result.get("context_summary", ""),
        )

    def _classify_keywords(self, decision: str) -> ClassifierResult:
        """Fallback: keyword-based classification."""
        text = decision.lower()
        scores: dict[DecisionCategory, int] = {}

        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > 0:
                scores[category] = score

        if not scores:
            return ClassifierResult(
                category=DecisionCategory.GENERAL,
                confidence=0.5,
                context_summary=decision[:200],
            )

        best = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = min(1.0, scores[best] / max(1, total))

        return ClassifierResult(
            category=best,
            confidence=confidence,
            context_summary=decision[:200],
        )

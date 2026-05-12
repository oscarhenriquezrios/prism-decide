"""Tests for the keyword-based classifier (no LLM needed)."""

import pytest

from prism_decide.core.classifier import Classifier
from prism_decide.core.types import DecisionCategory
from prism_decide.providers.base import BaseProvider


class MockFailingProvider(BaseProvider):
    """A provider that always fails — forces keyword fallback."""
    def __init__(self):
        super().__init__(model="mock", api_key="")

    def complete(self, prompt, system="", temperature=0.7, max_tokens=2048, **kwargs):
        raise Exception("LLM not available")

    def complete_json(self, prompt, system="", temperature=0.3, **kwargs):
        raise Exception("LLM not available")


@pytest.fixture
def classifier():
    return Classifier(MockFailingProvider())


def test_classify_career_keywords(classifier):
    result = classifier._classify_keywords("¿Debería cambiar de trabajo?")
    assert result.category == DecisionCategory.CAREER
    assert result.confidence > 0


def test_classify_business_keywords(classifier):
    result = classifier._classify_keywords("¿Debería emprender un negocio?")
    assert result.category == DecisionCategory.BUSINESS


def test_classify_personal_keywords(classifier):
    result = classifier._classify_keywords("¿Debería mudarme con mi pareja?")
    assert result.category == DecisionCategory.PERSONAL


def test_classify_health_keywords(classifier):
    result = classifier._classify_keywords("¿Debería empezar un tratamiento médico?")
    assert result.category == DecisionCategory.HEALTH


def test_classify_education_keywords(classifier):
    result = classifier._classify_keywords("¿Debería estudiar un MBA?")
    assert result.category == DecisionCategory.EDUCATION


def test_classify_finance_keywords(classifier):
    result = classifier._classify_keywords("¿Debería invertir en acciones?")
    assert result.category == DecisionCategory.FINANCE


def test_classify_general_fallback(classifier):
    result = classifier._classify_keywords("¿Debería pintar mi casa de azul?")
    assert result.category == DecisionCategory.GENERAL
    assert result.confidence == 0.5


def test_classify_fallback_on_llm_error(classifier):
    """When LLM fails, should fall back to keywords."""
    result = classifier.classify("¿Debería cambiar de trabajo?")
    assert result.category in [DecisionCategory.CAREER, DecisionCategory.GENERAL]

"""Tests for the synthesizer — matrix building and formatting."""

from prism_decide.core.synthesizer import Synthesizer
from prism_decide.core.types import AgentVerdict, DecisionCategory, DecisionMatrix


def test_build_matrix():
    syn = Synthesizer()
    verdicts = [
        AgentVerdict(agent_id="a1", agent_label="A1", scores={"A": 8, "B": 3}),
    ]
    m = syn.build_matrix(
        decision_text="¿Test?",
        options=["A", "B"],
        verdicts=verdicts,
        category=DecisionCategory.CAREER,
    )
    assert m.decision_text == "¿Test?"
    assert m.options == ["A", "B"]
    assert len(m.verdicts) == 1


def test_format_matrix_empty():
    syn = Synthesizer()
    m = DecisionMatrix(category=DecisionCategory.GENERAL, decision_text="test")
    result = syn.format_matrix(m)
    assert result == ""  # Returns empty string for empty data


def test_format_matrix_with_data():
    syn = Synthesizer()
    verdicts = [
        AgentVerdict(agent_id="financial", agent_label="Financiero",
                      scores={"Opción A": 8, "Opción B": 4}),
        AgentVerdict(agent_id="risk", agent_label="Riesgo",
                      scores={"Opción A": 6, "Opción B": 7}),
    ]
    m = syn.build_matrix(
        decision_text="¿Debería tomar la opción A o B?",
        options=["Opción A", "Opción B"],
        verdicts=verdicts,
        category=DecisionCategory.CAREER,
    )
    # Should not raise
    result = syn.format_matrix(m)
    assert result == ""


def test_format_json():
    syn = Synthesizer()
    m = DecisionMatrix(
        category=DecisionCategory.CAREER,
        decision_text="test",
        options=["A"],
        verdicts=[AgentVerdict(agent_id="a1", agent_label="A1", scores={"A": 5})],
    )
    import json
    data = json.loads(syn.format_json(m))
    assert data["decision_text"] == "test"
    assert data["category"] == "career"
    assert len(data["verdicts"]) == 1

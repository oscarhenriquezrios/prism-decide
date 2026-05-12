"""Tests for core types: DecisionMatrix, AgentVerdict, totals, recommendations."""

from prism_decide.core.types import AgentVerdict, DecisionCategory, DecisionMatrix


def test_agent_verdict_defaults():
    v = AgentVerdict(agent_id="test", agent_label="Test")
    assert v.agent_id == "test"
    assert v.agent_label == "Test"
    assert v.agent_icon == "🤖"
    assert v.scores == {}
    assert v.reasoning == ""


def test_decision_matrix_totals():
    v1 = AgentVerdict(
        agent_id="a1", agent_label="A1",
        scores={"Opción A": 8, "Opción B": 3},
    )
    v2 = AgentVerdict(
        agent_id="a2", agent_label="A2",
        scores={"Opción A": 6, "Opción B": 7},
    )
    m = DecisionMatrix(
        category=DecisionCategory.CAREER,
        decision_text="¿Cambio de trabajo?",
        options=["Opción A", "Opción B"],
        verdicts=[v1, v2],
    )
    assert m.totals == {"Opción A": 14, "Opción B": 10}


def test_decision_matrix_empty_totals():
    m = DecisionMatrix(category=DecisionCategory.GENERAL, decision_text="test")
    assert m.totals == {}


def test_confidence():
    m = DecisionMatrix(
        category=DecisionCategory.CAREER,
        decision_text="test",
        options=["A", "B"],
        verdicts=[
            AgentVerdict(agent_id="a1", agent_label="A1", scores={"A": 5, "B": 5}),
            AgentVerdict(agent_id="a2", agent_label="A2", scores={"A": 5, "B": 5}),
            AgentVerdict(agent_id="a3", agent_label="A3", scores={"A": 5, "B": 5}),
        ],
    )
    assert m.confidence == 0.6  # 3/5
    m2 = DecisionMatrix(category=DecisionCategory.GENERAL, decision_text="test")
    assert m2.confidence == 0.0


def test_strong_recommendation():
    v1 = AgentVerdict(agent_id="a1", agent_label="A1", scores={"Mejor": 10, "Peor": 2})
    v2 = AgentVerdict(agent_id="a2", agent_label="A2", scores={"Mejor": 9, "Peor": 3})
    m = DecisionMatrix(
        category=DecisionCategory.CAREER, decision_text="test",
        options=["Mejor", "Peor"],
        verdicts=[v1, v2],
    )
    rec = m.get_recommendation()
    assert "Recomendación fuerte" in rec
    assert "Mejor" in rec


def test_weak_recommendation():
    v1 = AgentVerdict(agent_id="a1", agent_label="A1", scores={"A": 6, "B": 5})
    m = DecisionMatrix(
        category=DecisionCategory.CAREER, decision_text="test",
        options=["A", "B"],
        verdicts=[v1],
    )
    rec = m.get_recommendation()
    assert "Recomendación leve" in rec or "Sin recomendación clara" in rec


def test_no_recommendation():
    m = DecisionMatrix(category=DecisionCategory.GENERAL, decision_text="test")
    assert "suficientes datos" in m.get_recommendation()

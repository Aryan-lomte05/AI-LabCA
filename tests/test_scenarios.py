import pytest

from heatwave_es import build_engine
from heatwave_es.engine import Condition, InferenceEngine, Rule
from heatwave_es.knowledge_base import RULES, heat_index_c
from heatwave_es.scenarios import SCENARIOS

ENGINE = build_engine()


@pytest.mark.parametrize("sc", SCENARIOS, ids=[s["id"] for s in SCENARIOS])
def test_scenario(sc):
    res = ENGINE.run(sc["inputs"])
    for k, v in sc["expect"].items():
        assert res.facts.get(k) == v, f"{k}: {res.facts.get(k)!r} != {v!r}"
    fired = res.fired_ids()
    for rid in sc.get("must_fire", []):
        assert rid in fired, f"{rid} should have fired; fired={fired}"
    for rid in sc.get("must_not_fire", []):
        assert rid not in fired, f"{rid} should not have fired"
    assert res.halted_by == sc.get("halted_by")
    if "first_rule" in sc:
        assert fired[0] == sc["first_rule"]


def test_knowledge_base_size_and_sources():
    assert len(RULES) >= 20
    assert all(r.source and r.because for r in RULES)


def test_rule_fires_at_most_once():
    for sc in SCENARIOS:
        fired = ENGINE.run(sc["inputs"]).fired_ids()
        assert len(fired) == len(set(fired))


def test_every_run_ends_with_a_conclusion_or_error():
    for sc in SCENARIOS:
        f = ENGINE.run(sc["inputs"]).facts
        assert "recommendation" in f or "error" in f


def test_conflict_resolution_salience_then_specificity():
    rules = [
        Rule("low", "low", [Condition("x", "==", 1)], {"y": "low"}, salience=0),
        Rule("gen", "general", [Condition("x", "==", 1), Condition("y", "unknown")],
             {"y": "general"}, salience=5),
        Rule("spec", "specific", [Condition("x", "==", 1), Condition("z", "==", 2),
                                  Condition("y", "unknown")], {"y": "specific"}, salience=5),
    ]
    res = InferenceEngine(rules).run({"x": 1, "z": 2})
    assert res.fired_ids()[0] == "spec"          # same salience -> more specific wins
    assert res.fired_ids()[-1] == "low"          # lowest salience last


def test_how_explanation_handles_modified_fact():
    res = ENGINE.run(SCENARIOS[8]["inputs"])     # TC09 warm-night escalation
    how = ENGINE.how(res, "alert")
    assert "E1" in how[0] and any("A3" in line for line in how)


def test_heat_index_reference_values():
    # NWS table: 90 F / 70 % RH -> ~106 F (41 C); 30 C / 40 % -> ~30-31 C
    assert 40 <= heat_index_c(32.2, 70) <= 42
    assert 29 <= heat_index_c(30, 40) <= 32


def test_wrong_type_input_does_not_crash():
    res = ENGINE.run({"role": "citizen", "region": "plains", "tmax": 45.0,
                      "tmax_normal": "forty"})
    assert "recommendation" in res.facts or "error" in res.facts


def test_knowledge_base_is_consistent():
    from heatwave_es.kb_check import check
    assert check() == []


def test_every_rule_is_covered_by_some_scenario():
    from heatwave_es.kb_check import coverage
    _, missing = coverage()
    assert missing == []

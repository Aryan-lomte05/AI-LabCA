"""Static consistency checks on the knowledge base (run: python -m heatwave_es.kb_check).

Checks performed
  1. every fact a rule tests is either a user input or asserted by some rule
     (no rule can be permanently blocked by a fact nothing produces)
  2. every rule cites a known source and has a justification
  3. no two rules have identical conditions with identical actions (redundancy)
  4. no two rules with identical conditions assert DIFFERENT values for the
     same fact at the same salience (unresolvable contradiction)
  5. coverage: every rule fires in at least one test scenario
"""

from __future__ import annotations

from .engine import InferenceEngine
from .knowledge_base import RULES, SOURCES
from .scenarios import SCENARIOS

USER_INPUTS = {"role", "region", "tmax", "tmax_normal", "heat_days", "rh", "tmin",
               "tmin_normal", "vulnerable", "farm", "symptoms"}


def check(rules=RULES) -> list[str]:
    problems = []
    produced = USER_INPUTS | {k for r in rules for k in r.assert_facts}
    for r in rules:
        for c in r.conditions:
            if c.op != "unknown" and c.fact not in produced:
                problems.append(f"{r.id}: tests '{c.fact}' which nothing produces")
        if r.source not in SOURCES:
            problems.append(f"{r.id}: unknown source {r.source}")
        if not r.because:
            problems.append(f"{r.id}: missing justification")

    def sig(r):
        return tuple(sorted((c.fact, c.op, repr(c.value)) for c in r.conditions))

    for i, a in enumerate(rules):
        for b in rules[i + 1:]:
            if sig(a) != sig(b):
                continue
            same_actions = (a.assert_facts.keys() == b.assert_facts.keys()
                            and a.advice == b.advice
                            and all(not callable(v) and v == b.assert_facts[k]
                                    for k, v in a.assert_facts.items()))
            if same_actions:
                problems.append(f"{a.id}/{b.id}: redundant (same IF, same THEN)")
            elif a.salience == b.salience:
                for k in a.assert_facts.keys() & b.assert_facts.keys():
                    if a.assert_facts[k] != b.assert_facts[k]:
                        problems.append(f"{a.id}/{b.id}: contradict on '{k}' at equal salience")
    return problems


def coverage(rules=RULES, scenarios=SCENARIOS) -> tuple[set[str], list[str]]:
    eng = InferenceEngine(rules)
    fired = set()
    for s in scenarios:
        fired |= set(eng.run(s["inputs"]).fired_ids())
    return fired, [r.id for r in rules if r.id not in fired]


if __name__ == "__main__":
    probs = check()
    fired, missing = coverage()
    print(f"Rules: {len(RULES)}   Sources: {len(SOURCES)}   Scenarios: {len(SCENARIOS)}")
    print(f"Consistency problems: {len(probs)}")
    for p in probs:
        print("  -", p)
    print(f"Rule coverage: {len(fired)}/{len(RULES)}"
          + (f"  (never fired: {', '.join(missing)})" if missing else "  (100 %)"))

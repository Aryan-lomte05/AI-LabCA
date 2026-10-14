"""
Forward-chaining production-rule inference engine with explanation facility.

Design (classic recognise-act cycle, as in OPS5 / CLIPS):

    1. MATCH    - find every rule whose conditions are all satisfied by the
                  facts in working memory  -> the "conflict set" (agenda)
    2. RESOLVE  - pick ONE activation from the agenda using a conflict
                  resolution strategy:
                      a) refraction  : a rule fires at most once per run
                      b) salience    : higher priority rule wins
                      c) specificity : rule with more conditions wins
                      d) rule order  : earlier rule in the knowledge base wins
    3. ACT      - execute the rule's actions (assert / modify facts, add
                  advice, or halt) and record a trace entry
    4. repeat until the agenda is empty or a rule halts the engine.

Every fact remembers which rule (or the user) put it there, so the engine can
answer "HOW was this concluded?" and the CLI can answer "WHY are you asking?".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

# ---------------------------------------------------------------------------
# Conditions
# ---------------------------------------------------------------------------

# Operators usable in a condition tuple (fact, op, value)
_OPS: dict[str, Callable[[Any, Any], bool]] = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">=": lambda a, b: a >= b,
    ">": lambda a, b: a > b,
    "<=": lambda a, b: a <= b,
    "<": lambda a, b: a < b,
    "in": lambda a, b: a in b,
    "not_in": lambda a, b: a not in b,
    # inclusive lower bound, inclusive upper bound
    "between": lambda a, b: b[0] <= a <= b[1],
    # half-open range [low, high)
    "range": lambda a, b: b[0] <= a < b[1],
    "outside": lambda a, b: not (b[0] <= a <= b[1]),
    # list-valued fact contains value
    "contains": lambda a, b: b in a,
    "contains_any": lambda a, b: any(x in a for x in b),
}

# Operators that test presence rather than value
_PRESENCE_OPS = {"known", "unknown"}


@dataclass(frozen=True)
class Condition:
    fact: str
    op: str
    value: Any = None

    def holds(self, wm: "WorkingMemory") -> bool:
        if self.op == "known":
            return wm.has(self.fact)
        if self.op == "unknown":
            return not wm.has(self.fact)
        if not wm.has(self.fact):
            # A condition on a missing fact is simply not satisfied
            # (closed-world for matching; robust to missing input).
            return False
        try:
            return _OPS[self.op](wm.get(self.fact), self.value)
        except TypeError:
            # e.g. comparing a string with a number -> not satisfied
            return False

    def describe(self, wm: "WorkingMemory | None" = None) -> str:
        if self.op in _PRESENCE_OPS:
            text = f"{self.fact} is {self.op}"
        elif self.op == "between":
            text = f"{self.value[0]} <= {self.fact} <= {self.value[1]}"
        elif self.op == "range":
            text = f"{self.value[0]} <= {self.fact} < {self.value[1]}"
        elif self.op == "outside":
            text = f"{self.fact} outside [{self.value[0]}, {self.value[1]}]"
        else:
            text = f"{self.fact} {self.op} {self.value!r}"
        if wm is not None and wm.has(self.fact) and self.op != "unknown":
            text += f"  [actual: {_fmt(wm.get(self.fact))}]"
        return text


def _fmt(v: Any) -> str:
    if isinstance(v, float):
        return f"{v:.1f}"
    if isinstance(v, (list, tuple, set)):
        return ", ".join(map(str, v)) or "none"
    return str(v)


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

@dataclass
class Rule:
    """IF <all conditions> THEN <actions>.

    actions:
        assert_facts : {fact: value | callable(wm) -> value}
        advice       : list of (audience, text) advisory lines to emit
        halt         : stop inference after this rule (e.g. invalid input)
    """

    id: str
    name: str
    conditions: list[Condition]
    assert_facts: dict[str, Any] = field(default_factory=dict)
    advice: list[tuple[str, str]] = field(default_factory=list)
    salience: int = 0
    halt: bool = False
    group: str = ""
    source: str = ""
    because: str = ""   # one-line human justification shown in the trace

    @property
    def specificity(self) -> int:
        return len(self.conditions)

    def matches(self, wm: "WorkingMemory") -> bool:
        return all(c.holds(wm) for c in self.conditions)

    def if_text(self) -> str:
        return " AND ".join(c.describe() for c in self.conditions)

    def then_text(self) -> str:
        parts = []
        for k, v in self.assert_facts.items():
            parts.append(f"{k} = {'<computed>' if callable(v) else repr(v)}")
        if self.advice:
            parts.append(f"advise {', '.join(sorted({a for a, _ in self.advice}))}")
        if self.halt:
            parts.append("HALT")
        return "; ".join(parts)


# ---------------------------------------------------------------------------
# Working memory
# ---------------------------------------------------------------------------

@dataclass
class Fact:
    name: str
    value: Any
    source: str  # "user" or rule id
    previous: "Fact | None" = None  # value this fact had before a rule modified it


class WorkingMemory:
    def __init__(self) -> None:
        self._facts: dict[str, Fact] = {}

    def has(self, name: str) -> bool:
        return name in self._facts

    def get(self, name: str, default: Any = None) -> Any:
        f = self._facts.get(name)
        return f.value if f else default

    def source_of(self, name: str) -> str | None:
        f = self._facts.get(name)
        return f.source if f else None

    def fact(self, name: str) -> Fact | None:
        return self._facts.get(name)

    def set(self, name: str, value: Any, source: str) -> None:
        self._facts[name] = Fact(name, value, source, self._facts.get(name))

    def items(self) -> Iterable[Fact]:
        return self._facts.values()

    def as_dict(self) -> dict[str, Any]:
        return {k: f.value for k, f in self._facts.items()}


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

@dataclass
class TraceEntry:
    cycle: int
    rule: Rule
    matched: list[str]
    asserted: dict[str, Any]
    agenda_size: int
    beaten: list[str]  # other rules that were on the agenda this cycle


@dataclass
class Result:
    facts: dict[str, Any]
    advice: list[tuple[str, str, str]]  # (audience, text, rule id)
    trace: list[TraceEntry]
    halted_by: str | None
    wm: WorkingMemory

    def fired_ids(self) -> list[str]:
        return [t.rule.id for t in self.trace]


class InferenceEngine:
    def __init__(self, rules: list[Rule], max_cycles: int = 500) -> None:
        ids = [r.id for r in rules]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate rule ids in knowledge base")
        self.rules = rules
        self._order = {r.id: i for i, r in enumerate(rules)}
        self.max_cycles = max_cycles

    def rule(self, rule_id: str) -> Rule:
        return next(r for r in self.rules if r.id == rule_id)

    # -- conflict resolution ------------------------------------------------
    def _priority(self, r: Rule) -> tuple:
        # sort key: highest salience, then most specific, then earliest
        return (-r.salience, -r.specificity, self._order[r.id])

    def agenda(self, wm: WorkingMemory, fired: set[str]) -> list[Rule]:
        acts = [r for r in self.rules if r.id not in fired and r.matches(wm)]
        return sorted(acts, key=self._priority)

    # -- main loop ----------------------------------------------------------
    def run(self, inputs: dict[str, Any]) -> Result:
        wm = WorkingMemory()
        for k, v in inputs.items():
            if v is not None:
                wm.set(k, v, "user")

        fired: set[str] = set()
        trace: list[TraceEntry] = []
        advice: list[tuple[str, str, str]] = []
        halted_by = None

        for cycle in range(1, self.max_cycles + 1):
            agenda = self.agenda(wm, fired)
            if not agenda:
                break
            rule = agenda[0]
            matched = [c.describe(wm) for c in rule.conditions]
            fired.add(rule.id)  # refraction

            asserted = {}
            try:
                for name, value in rule.assert_facts.items():
                    v = value(wm) if callable(value) else value
                    wm.set(name, v, rule.id)
                    asserted[name] = v
            except (TypeError, ValueError) as exc:
                # e.g. text where a number was expected: stop gracefully
                msg = f"Invalid input while applying {rule.id}: {exc}"
                wm.set("error", msg, rule.id)
                trace.append(TraceEntry(cycle, rule, matched, {"error": msg},
                                        len(agenda), [r.id for r in agenda[1:]]))
                halted_by = rule.id
                break
            for audience, text in rule.advice:
                advice.append((audience, text, rule.id))

            trace.append(TraceEntry(cycle, rule, matched, asserted,
                                    len(agenda), [r.id for r in agenda[1:]]))
            if rule.halt:
                halted_by = rule.id
                break
        else:
            raise RuntimeError("inference did not terminate (max cycles)")

        return Result(wm.as_dict(), advice, trace, halted_by, wm)

    # -- explanation ----------------------------------------------------------
    def how(self, result: Result, fact: str) -> list[str]:
        """Recursive HOW explanation: which rule derived `fact`, and from what."""
        f = result.wm.fact(fact)
        if f is None:
            return [f"{fact}: not established"]
        return self._how(result, f, 0)

    def _how(self, result: Result, f: Fact, depth: int) -> list[str]:
        pad = "  " * depth
        if f.source == "user":
            return [f"{pad}{f.name} = {_fmt(f.value)}  (given by user)"]
        r = self.rule(f.source)
        lines = [f"{pad}{f.name} = {_fmt(f.value)}  <- {r.id} '{r.name}'"]
        seen = set()
        for c in r.conditions:
            if c.fact in seen or c.op == "unknown":
                continue
            seen.add(c.fact)
            # a rule that modified this very fact was matched on its old value
            dep = f.previous if c.fact == f.name else result.wm.fact(c.fact)
            if dep is not None:
                lines += self._how(result, dep, depth + 1)
        return lines

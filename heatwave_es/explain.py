"""Turns an engine Result into human-readable output (recommendation + trace)."""

from __future__ import annotations

from .engine import InferenceEngine, Result
from .knowledge_base import SOURCES

_AUDIENCE_ORDER = ["EMERGENCY", "FIRST AID", "GOVERNANCE", "CITIZEN", "VULNERABLE",
                   "WORKER", "FARMER", "HEALTH", "AUTHORITY", "NOTE"]


def summary_lines(result: Result) -> list[str]:
    f = result.facts
    out = []
    if result.halted_by:
        out.append(f"INPUT ERROR ({result.halted_by}): {f.get('error')}")
        out.append("No heat-wave assessment made - please re-check the readings.")
    elif "recommendation" in f:
        out.append(f["recommendation"])
    else:
        out.append("Insufficient data to assess heat-wave conditions.")

    details = []
    if "departure" in f:
        details.append(f"Tmax departure from normal: {f['departure']:+.1f} C")
    if "heat_index" in f:
        details.append(f"Heat index (feels like): {f['heat_index']:.1f} C"
                       + (f" - {f['hi_level'].replace('_', ' ')}" if "hi_level" in f else ""))
    if "night" in f:
        details.append(f"Night: {f['night'].replace('_', ' ')}")
    if "escalated" in f:
        details.append(f"Alert escalated because of: {f['escalated']}")
    if "hri" in f:
        details.append(f"Symptom assessment: {f['hri'].replace('_', ' ')}")
    out += ["  - " + d for d in details]
    return out


def advice_lines(result: Result) -> list[str]:
    groups: dict[str, list[tuple[str, str]]] = {}
    for audience, text, rid in result.advice:
        groups.setdefault(audience, []).append((text, rid))
    out = []
    for aud in sorted(groups, key=lambda a: _AUDIENCE_ORDER.index(a)
                      if a in _AUDIENCE_ORDER else 99):
        out.append(f"[{aud}]")
        for text, rid in groups[aud]:
            out.append(f"  * {text}  ({rid})")
    return out


def trace_lines(result: Result, verbose: bool = True) -> list[str]:
    out = []
    for t in result.trace:
        r = t.rule
        out.append(f"{t.cycle:>2}. {r.id:<3} {r.name}   [salience {r.salience}, source {r.source}]")
        if verbose:
            for m in t.matched:
                out.append(f"       IF   {m}")
            for k, v in t.asserted.items():
                out.append(f"       THEN {k} = {v}")
            if r.advice:
                out.append(f"       THEN {len(r.advice)} advisory line(s)")
            out.append(f"       WHY  {r.because}")
            if t.beaten:
                out.append(f"       (conflict set also had: {', '.join(t.beaten)})")
    return out


def how_lines(engine: InferenceEngine, result: Result, fact: str = "alert") -> list[str]:
    return engine.how(result, fact)


def sources_used(result: Result) -> list[str]:
    ids = sorted({t.rule.source for t in result.trace})
    return [f"{s}: {SOURCES[s]}" for s in ids]


def full_report(engine: InferenceEngine, result: Result, verbose: bool = True) -> str:
    sep = "=" * 72
    parts = [sep, "RECOMMENDATION", sep, *summary_lines(result)]
    if result.advice:
        parts += ["", "ADVISORY", "-" * 72, *advice_lines(result)]
    parts += ["", f"EXPLANATION TRACE ({len(result.trace)} rules fired)", "-" * 72,
              *trace_lines(result, verbose)]
    if "alert" in result.facts:
        parts += ["", "HOW WAS THE ALERT LEVEL CONCLUDED?", "-" * 72,
                  *how_lines(engine, result, "alert")]
    parts += ["", "KNOWLEDGE SOURCES USED", "-" * 72, *sources_used(result), sep]
    return "\n".join(parts)

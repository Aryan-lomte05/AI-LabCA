"""
Interactive command-line consultation for HeatGuard.

At any prompt the user may type:
    why   - explain why the question is asked (which rules use the answer)
    skip  - leave an optional question unanswered (engine handles missing data)
    quit  - leave the consultation
"""

from __future__ import annotations

import argparse
import json
import sys

from .engine import InferenceEngine
from .explain import full_report, how_lines
from .knowledge_base import RULES

BANNER = r"""
 _   _            _    ____                     _
| | | | ___  __ _| |_ / ___|_   _  __ _ _ __ __| |
| |_| |/ _ \/ _` | __| |  _| | | |/ _` | '__/ _` |
|  _  |  __/ (_| | |_| |_| | |_| | (_| | | | (_| |
|_| |_|\___|\__,_|\__|\____|\__,_|\__,_|_|  \__,_|

 Heatwave Early-Warning & Advisory Expert System
 (Use case KJS-CES-01 - IMD heat wave criteria, NDMA / NPCCHH guidelines)
 Type 'why' at any question to see why it is asked, 'skip' for optional
 questions, 'quit' to exit.
"""

SYMPTOMS = ["none", "high_body_temp", "no_sweating", "confusion", "unconscious",
            "seizure", "heavy_sweating", "dizziness", "nausea", "weakness",
            "headache", "fainting", "muscle_cramps"]
VULNERABLE = ["none", "elderly", "infant_child", "pregnant", "chronic_illness",
              "outdoor_worker"]


class Quit(Exception):
    pass


def rules_using(fact: str) -> list[str]:
    return [f"{r.id} ({r.name})" for r in RULES
            if any(c.fact == fact for c in r.conditions)]


def _why(fact: str, reason: str) -> None:
    print(f"    WHY: {reason}")
    used = rules_using(fact)
    if used:
        print(f"    The answer is used by rules: {', '.join(used)}")


def ask(fact, prompt, reason, kind="float", choices=None, optional=False,
        lo=None, hi=None, multi=False, inp=input):
    """Ask until a valid answer is given. Returns None if skipped."""
    hint = ""
    if choices:
        hint = " [" + "/".join(choices) + "]"
        if multi:
            hint = " (comma-separated) [" + ", ".join(choices) + "]"
    if optional:
        hint += " (optional - 'skip')"
    while True:
        raw = inp(f"? {prompt}{hint}: ").strip().lower()
        if raw in ("quit", "exit", "q"):
            raise Quit
        if raw in ("why", "?"):
            _why(fact, reason)
            continue
        if raw in ("skip", "") and optional:
            return None
        if raw == "":
            print("    Please give an answer (this question is required).")
            continue
        if kind == "float":
            try:
                val = float(raw.replace("c", "").replace("%", "").strip())
            except ValueError:
                print("    Please enter a number, e.g. 42.5")
                continue
            if (lo is not None and val < lo) or (hi is not None and val > hi):
                print(f"    Value should be between {lo} and {hi}.")
                continue
            return val
        if kind == "int":
            if not raw.isdigit():
                print("    Please enter a whole number, e.g. 3")
                continue
            val = int(raw)
            if (lo is not None and val < lo) or (hi is not None and val > hi):
                print(f"    Value should be between {lo} and {hi}.")
                continue
            return val
        if multi:
            items = [x.strip() for x in raw.replace(";", ",").split(",") if x.strip()]
            bad = [x for x in items if x not in choices]
            if bad:
                print(f"    Unknown option(s): {', '.join(bad)}")
                continue
            return [x for x in items if x != "none"]
        # single choice: accept unique prefix too (e.g. 'p' -> plains)
        match = [c for c in choices if c.startswith(raw)]
        if len(match) == 1:
            return match[0]
        print(f"    Please choose one of: {', '.join(choices)}")


def consult(inp=input) -> dict:
    facts: dict = {}
    facts["role"] = ask("role", "Who are you seeking advice for",
                        "Advisories differ for citizens, farmers, health departments "
                        "and local authorities (NDMA stakeholder roles).",
                        kind="choice", choices=["citizen", "farmer", "health", "authority"],
                        inp=inp)
    facts["region"] = ask("region", "Type of region",
                          "IMD uses different heat-wave thresholds: 40 C plains, "
                          "37 C coastal, 30 C hilly.", kind="choice",
                          choices=["plains", "coastal", "hilly"], inp=inp)
    facts["tmax"] = ask("tmax", "Observed / forecast maximum temperature (C)",
                        "Tmax is the primary input of every IMD heat-wave criterion.",
                        inp=inp)
    facts["tmax_normal"] = ask("tmax_normal", "Normal (climatological) Tmax for today (C)",
                               "Heat wave is defined by departure from normal "
                               "(4.5-6.4 C heat wave, >6.4 C severe).",
                               optional=True, inp=inp)
    facts["heat_days"] = ask("heat_days",
                             "For how many consecutive days (incl. today) has it been this hot",
                             "IMD declares a heat wave after 2 consecutive days; colour "
                             "code (Yellow/Orange/Red) depends on persistence.",
                             kind="int", optional=True, inp=inp)
    facts["rh"] = ask("rh", "Relative humidity (%)",
                      "Humidity is used to compute the heat index (feels-like "
                      "temperature); humid heat is dangerous even below IMD thresholds.",
                      optional=True, inp=inp)
    if facts["tmax"] is not None and facts["tmax"] >= 40:
        facts["tmin"] = ask("tmin", "Night minimum temperature (C)",
                            "IMD 'warm night' needs Tmin departure >= 4.5 C when Tmax >= 40 C.",
                            optional=True, inp=inp)
        if facts["tmin"] is not None:
            facts["tmin_normal"] = ask("tmin_normal", "Normal Tmin for today (C)",
                                       "Needed to compute Tmin departure from normal.",
                                       optional=True, inp=inp)
    if facts["role"] == "citizen":
        facts["vulnerable"] = ask("vulnerable", "Anyone in the household who is",
                                  "Vulnerable groups get extra, specific advice.",
                                  kind="choice", choices=VULNERABLE, multi=True,
                                  optional=True, inp=inp) or []
    if facts["role"] == "farmer":
        facts["farm"] = ask("farm", "Do you manage", "Crop and livestock advice differ.",
                            kind="choice", choices=["crops", "livestock", "both"], inp=inp)
    if facts["role"] in ("citizen", "health"):
        facts["symptoms"] = ask("symptoms", "Is anyone showing these symptoms now",
                                "Symptoms are triaged first (heat stroke is an emergency) "
                                "using MoHFW heat-related illness guidelines.",
                                kind="choice", choices=SYMPTOMS, multi=True,
                                optional=True, inp=inp) or []
    return {k: v for k, v in facts.items() if v is not None}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="heatguard",
                                description="Heatwave early-warning advisory expert system")
    p.add_argument("--json", metavar="FILE",
                   help="run non-interactively on a JSON file of facts")
    p.add_argument("--brief", action="store_true", help="short trace (rule names only)")
    p.add_argument("--rules", action="store_true", help="print the knowledge base and exit")
    args = p.parse_args(argv)

    engine = InferenceEngine(RULES)
    if args.rules:
        for r in RULES:
            print(f"{r.id:<3} [{r.group}] IF {r.if_text()} THEN {r.then_text()}  ({r.source})")
        print(f"\n{len(RULES)} rules")
        return 0

    if args.json:
        with open(args.json, encoding="utf-8") as fh:
            facts = json.load(fh)
        print(full_report(engine, engine.run(facts), verbose=not args.brief))
        return 0

    print(BANNER)
    try:
        while True:
            facts = consult()
            result = engine.run(facts)
            print()
            print(full_report(engine, result, verbose=not args.brief))
            while True:
                q = input("\nAsk HOW a fact was concluded (e.g. 'how hw_category'), "
                          "'new' for another consultation, or 'quit': ").strip().lower()
                if q in ("quit", "exit", "q"):
                    raise Quit
                if q in ("new", "n", "again"):
                    break
                if q.startswith("how"):
                    fact = q[3:].strip() or "alert"
                    print("\n".join(how_lines(engine, result, fact)))
                else:
                    print("  Known facts: " + ", ".join(sorted(result.facts)))
    except (Quit, EOFError, KeyboardInterrupt):
        print("\nStay cool, stay hydrated. Goodbye!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

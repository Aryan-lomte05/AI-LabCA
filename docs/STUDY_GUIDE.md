# HeatGuard: Complete Study Guide for the Demo & Viva

> Read this end to end at least once as a group. Every member must be able to explain **any** part of it: the faculty can adjust individual marks by ±3 based on the viva, and questions may be aimed at anyone.

**Contents**
1. [Rubric map: how we earn all 25 marks](#1-rubric-map-how-we-earn-all-25-marks)
2. [The project in 60 seconds](#2-the-project-in-60-seconds)
3. [Domain knowledge you must know](#3-domain-knowledge-you-must-know)
4. [AI theory: expert systems from first principles](#4-ai-theory-expert-systems-from-first-principles)
5. [Code walkthrough, file by file](#5-code-walkthrough-file-by-file)
6. [One consultation, cycle by cycle (TC09)](#6-one-consultation-cycle-by-cycle-tc09)
7. [The Prolog edition explained](#7-the-prolog-edition-explained)
8. [Testing & verification](#8-testing--verification)
9. [The web UI, API and deployment](#9-the-web-ui-api-and-deployment)
10. [Demo script (minute by minute) + backup plans](#10-demo-script-minute-by-minute--backup-plans)
11. [Live-modification drills (examiner asks you to change something)](#11-live-modification-drills)
12. [Q&A bank (100+ questions with answers)](#12-qa-bank)
13. [Things NOT to say](#13-things-not-to-say)
14. [One-page cheat sheet](#14-one-page-cheat-sheet)

---

## 1. Rubric map: how we earn all 25 marks

| Criterion (marks) | "Excellent" asks for | What we have | What to SHOW | What to SAY |
|---|---|---|---|---|
| **Problem selection & domain understanding (4)** | Well-justified real-world problem; rules grounded in credible expert sources | SVU use case KJS-CES-01 (IMD heatwave), Phase V advisory. 9 cited sources (IMD, NDMA, MoHFW NPCCHH, NWS, ICAR agromet, Ahmedabad HAP, use-case governance) | Report D1; `SOURCES` in `knowledge_base.py`; the "Sources" section of the UI; the source column of every trace line | "Heat wave in India is *defined* by IMD's published thresholds. We encode official criteria, not opinions. Every rule cites its guideline." |
| **Knowledge base design (5)** | 20+ well-structured, non-redundant, consistent rules; edge-case coverage | **59 rules** in 9 layers, each with salience, source and justification. `kb_check` verifies: 0 dead rules, 0 redundant, 0 contradictions, **59/59 rules covered by tests** | `python -m heatwave_es --rules`, `python -m heatwave_es.kb_check`, rule-dependency diagram, Knowledge section of the UI | "We prove consistency mechanically, not just claim it. The checker found 0 problems, and we tested the checker by injecting defects." |
| **Inference engine (5)** | Correct chaining; handles conflict resolution; robust to invalid/missing input | Forward chaining with recognise-act cycle; conflict resolution = refraction → salience → specificity → order. Validation rules HALT; missing facts are handled; type errors caught. Plus a backward-chaining Prolog edition | Trace line "conflict set also had: …"; TC07/TC10/TC20-22 (invalid), TC08 (missing data) | "The engine is generic and knows nothing about heat; the domain lives only in the rules. We justify forward chaining because data arrives first and one reading yields many conclusions." |
| **Explanation & traceability (2)** | Clear rule-firing trace with justification | Trace (rule, IF with actual values, THEN, WHY, source, competing rules) + HOW proof tree + WHY during questioning | `how alert` in the CLI; Reasoning section of the UI; `why` at a CLI question | "HOW answers 'how did you conclude X', WHY answers 'why are you asking me this', just like MYCIN." |
| **User interface (2)** | Smooth, intuitive; handles unexpected input gracefully | 3 interfaces: CLI (re-asks on bad input, prefixes, skip, why/how), React web app (live updates), Prolog consultation | Type `abc` or `999` at a CLI question; the UI wizard and presets | "The CLI never crashes on bad input; it explains what it expected." |
| **Demo & viva (2)** | Every member explains design, rules and code confidently | This guide | Section 10 script | — |
| **Report, reflection, testing (5)** | Organised report; genuine critical reflection; 5+ diverse, documented tests incl. edge cases, with code | 18-page report (D1-D6), **23 scenarios** + 12 unit tests = 35 automated tests, all passing; auto-generated test report; reflection prompts with real limitations we hit | `python -m pytest -q`, `docs/Test_Case_Report.md`, report D4/D6 | "Tests assert not only the output but which rules must and must not fire." |

**Your to-do before submission:** fill in names and roll numbers in the report; **each member writes their own D6 reflection** (½ page: your contribution + one limitation); add the SVU logo; check the colours against the SVU brand guidelines.

### Suggested split for 3 members (each must still know everything)

| Member | Owns in the demo | Owns in the viva (first responder) |
|---|---|---|
| **A** | Problem, domain, sources, knowledge base design (sections 2-3, rule table) | Domain & KB questions |
| **B** | Inference engine, conflict resolution, explanation, Prolog (sections 4-7) | Engine, chaining, Prolog questions |
| **C** | UI, testing, validation, deployment, limitations (sections 8-9) | Testing, UI, robustness, limitations |

---

## 2. The project in 60 seconds

Memorise this and say it fluently:

> "Our project is **HeatGuard**, a rule-based expert system for the SVU AI use case KJS-CES-01, IMD's Climate Intelligence for Heatwave Early Warning. The use case has five phases, and we built **Phase V: the advisory and early-warning layer**.
>
> You give it a temperature reading or forecast. It classifies the day using the **official IMD heat-wave criteria**, assigns IMD's **Green / Yellow / Orange / Red alert**, escalates the alert for **warm nights and humid heat**, **triages heat-illness symptoms**, and gives **advice specific to the user**: a citizen, a farmer, a health department or a municipal authority.
>
> The knowledge base has **59 IF-THEN rules** from **9 official sources**. A **forward-chaining inference engine** with salience-based **conflict resolution** runs them, and every conclusion comes with a **full explanation trace**. We also built a **backward-chaining Prolog version** for comparison, a **React web interface**, and **35 automated tests** that make every rule fire at least once."

---

## 3. Domain knowledge you must know

### 3.1 What is a heat wave?
A period of abnormally high temperature, more than the normal maximum for that place and season. It kills through **heat stroke** and dehydration and worsens heart and kidney disease. India sees heat waves mainly from **March to June** (sometimes July). Hotspots: Rajasthan, Gujarat, Vidarbha (Maharashtra), Telangana, Andhra Pradesh, Odisha, UP and Delhi.

### 3.2 IMD heat-wave criteria (source S1). The heart of the project

**Step 1: the regional threshold must be reached** (otherwise there is no heat wave at all):

| Region | Tmax must be ≥ | Our rule |
|---|---|---|
| Plains | **40 °C** | C1 |
| Coastal | **37 °C** | C2 |
| Hilly | **30 °C** | C3 |

**Step 2: classify** (once the threshold is met):

| Basis | Heat wave | Severe heat wave | Our rules |
|---|---|---|---|
| Departure from normal | **4.5 to 6.4 °C** | **> 6.4 °C** | C7 / C5 |
| Actual Tmax | **≥ 45 °C** | **≥ 47 °C** | C6 / C4 |

**Step 3: declaration.** IMD declares a heat wave when the criteria hold for **2 consecutive days** (and at ≥ 2 stations in a meteorological sub-division; our single-station system can't check the second part, which is a stated limitation). Day 1 → we issue a **"watch"** (rule A2).

**Worked examples:**

| Region | Tmax | Normal | Departure | Verdict | Why |
|---|---|---|---|---|---|
| Plains | 39.9 | 34.9 | +5.0 | **None** | Threshold 40 not reached (TC12) |
| Plains | 40.0 | 35.5 | +4.5 | **Heat wave** | Threshold met, departure exactly 4.5 (TC11) |
| Plains | 44.0 | 39.0 | +5.0 | **Heat wave** | C7 |
| Plains | 46.0 | (unknown) | — | **Heat wave** | ≥ 45 needs no normal (C6, TC08) |
| Plains | 47.2 | 42.0 | +5.2 | **Severe** | ≥ 47 (C4), even though the departure alone gives only "heat wave" |
| Hilly | 31.5 | 24.5 | +7.0 | **Severe** | Threshold 30 met, departure > 6.4 (C5, TC05) |
| Coastal | 35.0 | 33.0 | +2.0 | **None** | Below 37 (TC02), but the humid heat escalation still fires! |

### 3.3 IMD colour-coded warnings (source S2)

| Colour | Meaning | Action message | Our rules |
|---|---|---|---|
| **Green** | Normal day | No action | A1 |
| **Yellow** | Heat alert: heat wave persists 2 days | Be updated | A2 (day 1, watch), A3 (2-3 days) |
| **Orange** | Severe heat alert: severe HW 2 days, or HW for 4+ days | Be prepared | A4 (HW 4-6 d), A6 (severe 2 d) |
| **Red** | Extreme heat alert: severe HW > 2 days, or total > 6 days | Take action | A5 (HW > 6 d), A7 (severe > 2 d) |

A8: heat wave but the number of days is unknown → conservative Yellow watch.

### 3.4 Warm night (source S3)
When **Tmax ≥ 40 °C** *and* the **Tmin departure is 4.5-6.4 °C** → warm night (W1); **> 6.4 °C** → very warm night (W2). Why it matters: the body never cools down overnight, so heat stress accumulates, especially in the elderly. **Our escalation E1:** a warm night raises Yellow to Orange.

### 3.5 Heat index (source S6)
The "feels-like" temperature combines temperature and **relative humidity**. Humid air stops sweat from evaporating, so the body cannot cool itself. We use the US National Weather Service **Rothfusz regression** (a polynomial in T and RH, computed in °F, with NWS adjustment terms).

| Heat index | Band | Rule |
|---|---|---|
| 27-32 °C | Caution | H1 |
| 32-39 °C | Extreme caution | H2 |
| 39-51 °C | Danger | H3 |
| ≥ 51 °C | Extreme danger | H4 |

- **E2:** a Green day with a heat index of "danger" or above → Yellow (humid heat, e.g. Mumbai at 35 °C and 60 % RH gives HI ≈ 45 °C).
- **E3:** a Yellow day with "extreme danger" **and RH ≥ 40 %** → Orange. *Why the RH condition?* The Rothfusz formula exaggerates the heat index in very **dry** air (it was fitted on humid data). Without it, every 44 °C dry day in Vidarbha would become Orange. **We discovered this bug through testing.** It makes a great viva story.

### 3.6 Heat-related illness (source S5, MoHFW NPCCHH)

| Illness | Key signs | Our rule | Advice |
|---|---|---|---|
| **Heat stroke** (emergency) | Confusion, unconsciousness, seizure; OR body temp > 40 °C with **hot, dry skin** (no sweating) | T1, T2 → T5 | **Call 108/112**; cool the body with water and fanning, ice packs on the neck, armpits and groin; **no fluids by mouth if unconscious** |
| **Heat exhaustion** | Heavy sweating, dizziness, nausea, weakness, headache, fainting | T3 → T6 | Cool place, ORS; see a doctor if no improvement in 1 hour |
| **Heat cramps** | Painful muscle spasms | T4 → T7 | Stop activity, rest, electrolytes |

**Why does triage have the highest salience (107-111), even above validation (98-100)?** Symptoms do not depend on the thermometer. If someone types a wrong temperature, the system must **still** tell them to call an ambulance. Life safety comes first.

### 3.7 Stakeholder advice: where it comes from
- **NDMA Heat Action Plan guidelines (S4):** citizen Do's and Don'ts (avoid the sun 12-3 pm, hydrate, light cotton clothes, never leave children in parked cars), outdoor-worker scheduling, the authority's role (cooling centres, rescheduling school and work hours).
- **MoHFW NPCCHH (S5):** hospital preparedness (ORS, IV fluids, ice packs, heat-stroke rooms), daily surveillance of heat-illness cases, care for vulnerable groups.
- **IMD/ICAR agromet advisories (S7):** irrigate in the evening or early morning, mulching, no spraying at mid-day; livestock: shade, water, no grazing 11-4, no daytime transport.
- **Ahmedabad Heat Action Plan (S8):** South Asia's first city heat plan (2013); colour alerts trigger municipal actions such as drinking-water points.
- **Use-case governance (S9):** a **Red alert needs human sign-off** by the duty meteorologist (G1). This is the "Human-in-the-Loop: High" item in the use-case document.

### 3.8 The use case: what you should know about KJS-CES-01
- Title: *Climate Intelligence for Heatwave Monitoring, Prediction, and Early Warning*. Collaborator: **IMD Mumbai-Pune**. Faculty owner: **Dr. Radhika Kotecha**.
- 5 phases: I data acquisition (IMD gridded data) → II AI forecasting (ML/LSTM) → III IoT Automated Weather Stations → IV forecast validation → **V advisory & early warning (ours)**.
- The data: IMD GRD files with Timestamp, Lat, Long and Max Temperature; 7 IMD regions × 4 seasons.
- Governance table: Responsible AI **High**, Human-in-the-loop **High**, GenAI/LLM **High** (our rule trace can fact-check LLM-generated advisories), Agentic AI **Low**, Privacy **Low**.

---

## 4. AI theory: expert systems from first principles

### 4.1 What is an expert system?
A program that solves problems in a narrow domain at the level of a human expert by reasoning over **explicit knowledge** (usually IF-THEN rules) rather than learned weights.

**Classic architecture (and where each part is in our code):**

| Component | Role | In HeatGuard |
|---|---|---|
| **Knowledge base** | Domain knowledge as rules | `knowledge_base.py` (59 `Rule` objects) |
| **Working memory** (fact base) | Facts about the *current* case | `WorkingMemory` class in `engine.py` |
| **Inference engine** | Decides which rules to apply and when | `InferenceEngine.run()` |
| **Explanation facility** | Answers HOW / WHY | `engine.how()`, `explain.py`, CLI `why` |
| **User interface** | Dialogue with the user | `cli.py`, React UI, `app.py`, Prolog `start/0` |
| **Knowledge acquisition** | Getting knowledge from experts and documents | We read IMD/NDMA/MoHFW documents → rules with citations |

**Famous examples:** MYCIN (1970s, Stanford; blood infections; backward chaining; certainty factors; introduced WHY/HOW explanations), DENDRAL (chemistry), XCON/R1 (DEC computer configuration; forward chaining, OPS5), PROSPECTOR (mineral exploration).

### 4.2 Production rules
`IF <conditions> THEN <actions>`. The IF part is the **antecedent / left-hand side (LHS)**, matched against working memory. The THEN part is the **consequent / right-hand side (RHS)**: assert or modify facts, or emit advice. Rules are **modular**: you can add one without rewriting the others (in theory; interactions still matter).

### 4.3 Forward chaining (data-driven), which our Python engine uses
Start from the **facts** and fire every rule whose conditions hold, adding new facts, until nothing new can be derived.

**The recognise-act cycle:**
1. **Match**: find all rules whose LHS is satisfied → the **conflict set** (agenda).
2. **Conflict resolution**: choose ONE rule.
3. **Act**: execute its RHS.
4. Repeat until the conflict set is empty (or a rule halts).

### 4.4 Backward chaining (goal-driven), which our Prolog edition uses
Start from a **goal** (e.g. `final_alert(L)`) and find rules whose THEN part proves it. Their IF parts become **sub-goals**, recursively, down to facts, which are asked from the user when unknown. Prolog's own resolution with depth-first search *is* backward chaining.

### 4.5 Forward vs backward: the comparison table (very likely question)

| | Forward chaining | Backward chaining |
|---|---|---|
| Direction | Facts → conclusions | Goal → facts |
| Driven by | Data | Goal / hypothesis |
| Best when | Data arrives first; many possible conclusions; monitoring | One question to answer; many possible facts; diagnosis |
| Asks the user | All relevant inputs up front | Only what the current proof needs |
| Classic systems | XCON/R1, OPS5, CLIPS | MYCIN, Prolog |
| Risk | May derive irrelevant facts | May explore deep, useless sub-goals |
| **In HeatGuard** | Python engine | Prolog edition |

**Our justification for forward chaining (memorise the four points):**
1. **Data comes first.** Weather stations and forecasts *push* readings; the question is "given this reading, what follows?"
2. **Many conclusions per reading:** the category, the alert, escalations, governance flags, and advice for several audiences.
3. **Monitoring:** the same rules re-run on every new reading, which is the standard architecture for alerting systems.
4. **Priority control:** salience lets triage fire first and validation stop bad data before classification.

### 4.6 Conflict resolution strategies (know all, and which we use)

| Strategy | Meaning | Used? |
|---|---|---|
| **Refraction** | A rule instance fires only once (prevents infinite loops) | ✅ 1st |
| **Salience / priority** | Rules carry a numeric priority | ✅ 2nd |
| **Specificity** | The rule with more conditions wins (more specific knowledge) | ✅ 3rd |
| **Rule order** | The earlier rule in the knowledge base wins (textual order) | ✅ 4th, the final tie-break; this is also Prolog's strategy |
| Recency | The rule matching the most recently added facts wins (OPS5 LEX/MEA) | ❌ |
| Random | Pick any | ❌ |

Code: `_priority()` returns `(-salience, -specificity, order)`, and Python's sort picks the smallest tuple.

### 4.7 Other concepts examiners like
- **Rete algorithm:** an efficient matching network (Forgy, 1979) that avoids re-matching all rules every cycle. **We use naive matching**, re-checking all 59 rules each cycle. That's fine at our size (≈ 59 rules × ~15 cycles ≈ under a thousand cheap checks; we measured **≈ 0.3 ms per consultation**). Rete matters at thousands of rules.
- **Closed-world assumption:** what is not known is treated as false. Our conditions on missing facts fail; the `unknown` operator explicitly tests for absence. Prolog uses negation-as-failure.
- **Monotonic vs non-monotonic reasoning:** our system is **non-monotonic**, because escalation rules *modify* the `alert` fact (Yellow → Orange). We keep the old value in `Fact.previous` so the explanation stays truthful.
- **Certainty factors (MYCIN) / fuzzy logic:** ways to handle uncertainty. **We don't use them**; our thresholds are crisp because IMD's definitions are crisp. This is a stated limitation and a future improvement.
- **Knowledge acquisition bottleneck:** turning expert knowledge into rules is the hardest part. We hit it with IMD's wording ("persists for 2 days").
- **Meta-interpreter:** a Prolog program that runs Prolog-like rules itself, so it can record proofs (HOW) and goal stacks (WHY). Our Prolog edition is one.
- **Expert system shell:** an engine with an empty knowledge base (CLIPS, Jess, Drools, experta). Our `engine.py` is effectively a tiny shell.

---

## 5. Code walkthrough, file by file

```
heatwave_es/
  engine.py         ← generic forward-chaining engine (the "shell")
  knowledge_base.py ← 59 rules + 9 sources + heat-index formula
  explain.py        ← formats recommendation / advice / trace / HOW
  cli.py            ← interactive command-line consultation
  scenarios.py      ← 23 test scenarios (shared by tests + report + UI)
  kb_check.py       ← static consistency checks + rule coverage
  __main__.py       ← lets you run `python -m heatwave_es`
server.py           ← stdlib HTTP server: JSON API + serves the React app
api/*.py            ← the same API as Vercel serverless functions
frontend/           ← React + Tailwind + React Bits UI (HeatGuard Atlas)
app.py              ← alternative Streamlit UI
prolog/heatguard.pl ← backward-chaining SWI-Prolog edition
tests/              ← pytest suite (35 tests)
tools/              ← report builder, diagram generator
docs/               ← report (md/docx/pdf), test report, this guide
```

### 5.1 `engine.py`: the inference engine
- **`Condition(fact, op, value)`** (line ~56): one test, e.g. `Condition("tmax", ">=", 40)`.
  - `holds(wm)`: `known`/`unknown` test presence. For all other operators, **if the fact is missing → False** (closed world, so a missing input can never crash). A `TypeError` (e.g. comparing text with a number) → False.
  - Operators: `== != >= > <= < in not_in between range outside contains contains_any known unknown`. `between` is inclusive [a, b]; `range` is half-open [a, b), used for heat-index bands so 32.0 belongs to exactly one band.
  - `describe(wm)` prints the condition with the **actual value**: `tmax >= 40 [actual: 45.6]`.
- **`Rule`** (line ~105): `id, name, conditions, assert_facts, advice, salience, halt, group, source, because`. `assert_facts` values can be **functions** (`lambda wm: ...`) for computed facts such as departure. `specificity` = number of conditions.
- **`Fact`**: `name, value, source` (`"user"` or a rule id), and **`previous`**, the older version of the fact if a rule modified it.
- **`WorkingMemory`** (line ~158): a dictionary of facts with `has / get / set / fact / source_of`.
- **`InferenceEngine.run(inputs)`** (line ~234), the recognise-act loop:
  ```python
  for cycle in 1..max_cycles:
      agenda = self.agenda(wm, fired)      # MATCH: rules matching & not yet fired
      if not agenda: break                 # nothing left -> stop
      rule = agenda[0]                     # RESOLVE: sorted by _priority
      fired.add(rule.id)                   # refraction
      ... assert facts / collect advice    # ACT
      trace.append(TraceEntry(...))        # explanation record
      if rule.halt: break                  # validation stops inference
  ```
  - `max_cycles = 500` is a safety net; the loop raises an error if it's exceeded, which can't happen with refraction (at most 59 firings).
  - Exceptions in actions (`TypeError`, `ValueError`) → an `error` fact + halt (line ~259). Robust to junk input.
- **`_priority(rule)`** returns `(-salience, -specificity, order)`. That is the whole conflict-resolution strategy in one line.
- **`how(result, fact)`**: a recursive proof tree. For a fact made by a rule, it explains each condition's fact. If the rule tested the **same fact it modified** (E1 tests `alert == YELLOW` and sets `alert = ORANGE`), it explains `fact.previous` instead. Without this there would be infinite recursion; this was a real bug we fixed.

### 5.2 `knowledge_base.py`
- `SOURCES` S1-S9, `ALERT_MEANING`, and the `heat_index_c()` Rothfusz implementation (computed in °F, NWS adjustments, back to °C).
- `RULES`: 59 rules in layers (T, V, D, C, W, H, A, E, G, P, F, M, X, K). Design tricks to explain:
  - **`hw_category unknown`** in C4-C8 makes classification *first conclusion wins*, so it can never contradict itself.
  - **C8 is the default** ("otherwise"): low salience (70), so it fires only if no criterion did.
  - **`alert unknown`** in A1-A8 means exactly one base alert.
  - **`escalated unknown`** in E3 limits escalation to one level.
  - **Salience E (50) > advice (20)** is crucial: the alert must be **final before any advice fires**. If advice ran first, rules written for `alert == YELLOW` would fire on a *stale* Yellow. For example, an authority would get **both** the Yellow advice X1 and, after escalation, the Orange advice X2, which is a contradictory mix. We verified this experimentally (Drill 3). In TC09, P3 (severe-alert advice) only becomes eligible *after* E1 changes the alert to Orange. Point this out in the trace.
  - **K1** (salience 0) runs last and composes the headline.

### 5.3 `explain.py`
Formats `summary_lines` (headline + departure, heat index, night, escalation, illness), `advice_lines` (grouped by audience, emergency first), `trace_lines` (IF/THEN/WHY/conflict set), `how_lines`, `sources_used`, and `full_report`.

### 5.4 `cli.py`
- `ask()` validation loop: `why` → explains the question and lists the rules that use the answer (`rules_using(fact)`); `skip` for optional questions; `quit`; numbers are range-checked; choices accept **unique prefixes** (`p` → plains); multi-select validates every item.
- `consult()` asks **only relevant questions**: Tmin only if Tmax ≥ 40; vulnerable groups only for citizens; farm type only for farmers; symptoms only for citizens and health departments.
- `main()`: flags `--json FILE`, `--brief`, `--rules`. After a run you can type `how <fact>`, `new` or `quit`.

### 5.5 `server.py` and `api/*.py`
- `clean_facts()` whitelists and coerces inputs (strings to floats, `heat_days` to int; a bad string is left so the engine reports it).
- `consult()` returns `facts, alert, advice, trace (with matched conditions and competing rules), how trees, sources`.
- `Handler` serves `POST /api/consult`, `GET /api/kb` and `GET /api/scenarios`, and serves the built React app for everything else. **Standard library only**, no Flask.
- `api/consult.py` etc. just re-export `server.Handler` as `handler` for Vercel's Python runtime.

### 5.6 `frontend/` (React)
- `App.jsx`: state `facts` → **debounced (120 ms) POST /api/consult** on every change. Out-of-order responses are ignored with a sequence counter.
- `sections/Console.jsx`: Stepper wizard (4 steps), Verdict (DecryptedText alert, thermometer, stats), Advisory (AnimatedList).
- `sections/Reasoning.jsx`: the recognise-act explainer, trace list and HOW tree.
- `sections/Knowledge.jsx`: searchable, filterable rule table; rules that fired glow.
- React Bits components used: Aurora, SplitText, GradientText, ShinyText, BlurText, CountUp, StarBorder, Stepper, SpotlightCard, DecryptedText, AnimatedList, Magnet, ClickSpark.
- **Key point:** the UI contains **no reasoning logic**. It only displays what the Python engine returns, so all interfaces share one engine.

### 5.7 `kb_check.py`
Static checks (dead rules, sources, redundancy, contradictions) + dynamic **rule coverage**. See section 8.

---

## 6. One consultation, cycle by cycle (TC09)

**Input:** citizen, plains, Tmax 45.6, normal 39.8, 3 days, RH 25 %, Tmin 31 (normal 26), elderly + outdoor worker, no symptoms.

| Cycle | Fired | Salience | Why this one won | Conflict set also had | Result |
|---|---|---|---|---|---|
| 1 | **D0** check Tmin ≤ Tmax | 99 | Highest salience | D1 D2 D3 C1 C8 | tmin_gt_tmax = False |
| 2 | **D1** departure | 90 | 90 > 80; earlier than D2/D3 | D2 D3 C1 C8 | departure = +5.8 |
| 3 | **D2** Tmin departure | 90 | Rule order | D3 C1 C8 | tmin_departure = +5.0 |
| 4 | **D3** heat index | 90 | — | C1 W1 C8 | heat_index = 51.7 |
| 5 | **C1** plains threshold | 80 | Equal salience with W1; same specificity → **rule order** | W1 H4 C8 | threshold_met = True |
| 6 | **W1** warm night | 80 | Rule order | H4 C6 C7 C8 | night = warm_night |
| 7 | **H4** extreme danger | 80 | 80 > 76 | C6 C7 C8 | hi_level = extreme_danger |
| 8 | **C6** HW by absolute ≥ 45 | 76 | Ties with C7 (both 76, 3 conditions) → **rule order** | C7 C8 | hw_category = heatwave |
| 9 | **A3** HW 2-3 days | 60 | C7 and C8 are now blocked (`hw_category unknown` is false) | — | alert = YELLOW, declared |
| 10 | **E1** warm night escalation | 50 | E3 not eligible: RH 25 < 40 | P4 P5 P2 K1 | **alert = ORANGE** |
| 11 | **P4** vulnerable advice | 20 | 3 conditions beat P2/P3's 2 → **specificity** | P5 P2 P3 K1 | advice |
| 12 | **P5** outdoor worker | 20 | Specificity | P2 P3 K1 | advice |
| 13 | **P2** basic precautions | 20 | Rule order | P3 K1 | advice |
| 14 | **P3** severe precautions | 20 | Eligible only because E1 made it Orange! | K1 | advice |
| 15 | **K1** summary | 0 | Last | — | recommendation |

**HOW alert** prints: ORANGE ← E1 (night ← W1 ← tmax, tmin_departure ← D2 …; previous alert YELLOW ← A3 ← hw_category ← C6 ← threshold_met ← C1 …).

**Three things to point out in the demo:**
1. **All four conflict-resolution levels appear in one run:** salience (cycle 1), rule order (5, 8), specificity (11), refraction (C8 never fires twice; nothing does).
2. **C7 also matched** (departure 5.8 is between 4.5 and 6.4) but lost to C6. Both give "heatwave", so it doesn't matter; the `hw_category unknown` guard then blocked it.
3. **Non-monotonic update:** E1 changes the alert; P3 becomes eligible only afterwards.

---

## 7. The Prolog edition explained

File: `prolog/heatguard.pl`. Run: `swipl prolog/heatguard.pl`, then `?- start.` or `?- run_tests_cases.`

- **Rules are data:** `rule(Id, Head, Body, Source)`, for example
  `rule(c1, threshold_met, (val(region, plains), val(tmax, T), T >= 40), s1).`
- **Meta-interpreter `prove(Goal, WhyStack, Proof)`:**
  - `true` → proved; `(A, B)` → prove both; `once(G)` → first proof only.
  - `val(A, V)` → look up the fact, or **ask the user** (once, then `assertz(known(A, V))` memoises the answer).
  - Built-ins (`is, >=, member, heat_index…`) → `call/1`.
  - Otherwise find a `rule(Id, G, Body, Src)` and prove its Body, **pushing `Id-G` onto the WhyStack**. The Proof term builds the **HOW tree**.
- **WHY:** typing `why` at a question prints the WhyStack, i.e. the chain of goals that led to the question.
- **HOW:** `show_proof/1` pretty-prints the proof tree.
- **Conflict resolution = rule order + `once/1`.** `cat_candidate` clauses are ordered severe-first, so the first proof wins.
- **A bug we fixed (good viva story):** `category(none)` was being "proved" on a heat-wave day, because calling the catch-all rule with a **bound** argument succeeds trivially. The fix is to compute the value unbound first, then compare: `(once(cat_candidate(C0)), C = C0)`.
- **Goal-driven questioning:** for a hilly region at 26 °C, it never asks for the normal temperature or the duration, because the threshold sub-goal already failed.
- `run_tests_cases/0` runs TC01, TC02, TC03, TC04, TC06 and TC09 in batch mode (unknown facts are treated as unknown, not asked) and **gives the same alerts as Python**.

---

## 8. Testing & verification

- `python -m pytest -q` → **35 passed**: 23 scenario tests plus 12 unit tests covering KB size and sources, refraction, every-run-concludes, conflict-resolution order, HOW with a modified fact, heat-index reference values, wrong-type input, 3 API tests, KB consistency, and 100 % coverage.
- Each scenario specifies **`expect`** (conclusions), **`must_fire`**, **`must_not_fire`** and optionally **`halted_by`** / **`first_rule`**. Checking that a rule does *not* fire is what proves conflict resolution works.
- **The 23 scenarios cover:** all 4 alerts; all 4 roles; all 3 regions; all 3 illnesses; invalid Tmax, normal, RH, days, Tmin > Tmax and text input; missing optional data; boundaries 40.0 / 39.9 / +4.5; warm and very warm nights; humid heat; prolonged heat waves; Red with human review.
- `python -m heatwave_es.kb_check` → `Consistency problems: 0`, `Rule coverage: 59/59 (100 %)`.
- **We tested the tester:** injecting a duplicate rule, a rule on a non-existent fact, and a contradicting rule made the checker report all three.
- **Bugs found by testing (for the reflection and the viva):**
  1. The HOW explanation recursed forever on an escalated alert → fixed with `Fact.previous`.
  2. Rule T2 overwrote T1 because T2 was more specific → we gave neurological signs a higher salience (111).
  3. Text in a numeric field crashed the departure computation → the engine now catches it and halts with an error.
  4. Dry 44 °C days escalated to Orange through an unrealistic heat index → E3 now requires RH ≥ 40 %.
  5. Prolog's bound-argument bug in `category/1` → compute first, then compare.

---

## 9. The web UI, API and deployment

- **Run locally:** `python server.py` → http://localhost:8000. The built UI is committed, so **no Node is needed**.
- **Develop the UI:** `cd frontend && npm install && npm run dev` (port 5173, which proxies `/api` to 8000).
- **API contract:** `POST /api/consult` with JSON facts → `{alert, facts, advice[], trace[], how{}, sources{}}`.
- **Vercel:** `vercel.json` builds `frontend/` → `frontend/dist`; `api/*.py` become Python serverless functions (stdlib only). Import the repo on vercel.com and click Deploy, or run `vercel --prod`.
- **Why a separate API rather than JavaScript rules?** One source of truth: the CLI, the web UI and the tests all use the same engine, so the UI can never disagree with the report.

---

## 10. Demo script (minute by minute) + backup plans

**Before the lab (checklist):**
- [ ] `git pull`; `python -m pytest -q` shows 35 passed.
- [ ] `python server.py` running; browser open at localhost:8000 (internet is needed only for fonts).
- [ ] A terminal open in the repo folder; SWI-Prolog installed (`swipl --version`).
- [ ] Report PDF open on the second tab.
- [ ] Increase the terminal font size; dark terminal theme.

| Time | Who | Do | Say |
|---|---|---|---|
| 0:00 | A | Web UI hero | 60-second pitch (section 2) |
| 0:45 | A | Scroll to Knowledge; search "47"; click C4 | "Each rule cites its source. C4 is IMD's absolute severe criterion." |
| 1:30 | B | Console → preset **TC01** (Green), then **TC04** (Yellow watch); in step 2 change days to 3 | "Watch versus declared: IMD needs 2 consecutive days." |
| 2:30 | B | Preset **TC09** → Reasoning section | Walk cycles 1, 5, 8, 10, 14 (section 6). Open the HOW tree. |
| 3:45 | C | Preset **TC06** | "Triage has the highest salience: the emergency fires first." |
| 4:15 | C | Preset **TC07** (Tmax 62) | "Validation halts instead of misleading people." |
| 4:45 | C | Terminal: `python -m heatwave_es`; type `why` at the humidity question; type `abc` | Robustness and the WHY facility |
| 5:30 | B | `swipl prolog/heatguard.pl`, `?- start.`, hilly + 26 | "Backward chaining asks only what it needs." |
| 6:15 | C | `python -m pytest -q` and `python -m heatwave_es.kb_check` | "35 tests, 0 inconsistencies, 100 % rule coverage." |

**Backup plans:**
- *The browser UI won't load:* use the CLI (`python -m heatwave_es --json examples/warm_night_escalation.json`).
- *No internet:* everything runs offline; only the web fonts fall back to system fonts.
- *Laptop dies:* the Vercel URL (if deployed), or run the Streamlit app on a friend's machine.
- *Port 8000 busy:* `python server.py 9000`.

---

## 11. Live-modification drills

Examiners love "change something now". Practise these **before the viva** and undo them afterwards with `git checkout .`.

> ⚠️ After reverting an edit, run tests with `python -B -m pytest -q`, or delete the `__pycache__` folders first. If an edit and its revert happen within the same second and keep the same file size, Python can keep running the stale cached bytecode. We hit exactly this while preparing the guide.

**Drill 1: "Add a rule: during a Red alert, schools must close."**
In `knowledge_base.py`, before K1, add:
```python
Rule("X4", "Authority - close schools on Red",
     [C("role", "==", "authority"), C("alert", "==", "RED")], {},
     advice=[("AUTHORITY", "Close schools / shift to online classes during Red alert.")],
     salience=20, group="Authority", source="S4", because="NDMA: protect children in extreme heat."),
```
Run `python -m heatwave_es --json` on a Red authority case. It works without touching the engine, which shows **the knowledge base is separate from the engine**.

**Drill 2: "Change the coastal threshold to 35 °C."** Edit C2 (`C("tmax", ">=", 35)`) and run `python -m pytest -q`: **TC02 fails** ("C2 should not have fired"), because Mumbai at 35 °C now counts as reaching the heat-wave threshold. This shows the tests protect the official knowledge. (At 36 °C no test fails, since no scenario sits between 36 and 37: an honest answer if asked about test gaps.) Revert with `git checkout heatwave_es/knowledge_base.py`.

**Drill 3: "What happens if escalation ran after advice?"** Change E1's salience to 10 and run the warm-night case for an **authority** (`role: authority`, plains, 45.6/39.8, 3 days, RH 25, Tmin 31/26). The trace becomes `X1 → E1 → X2`: the authority gets the Yellow actions *and* the Orange actions, because X1 fired on the stale Yellow alert. With the real salience (50) only `E1 → X2` fires. This shows **why salience ordering matters for consistency**. (For a citizen the advice set doesn't change, only the order, because the P-rules test "not Green" / "Orange or Red" rather than "== Yellow". A good subtle point.) Revert it.

**Drill 4: "Remove refraction."** In `run()`, comment out `fired.add(rule.id)`: the same rule fires forever until `max_cycles` raises an error. This shows **why refraction guarantees termination**. Revert it.

**Drill 5: "Show me a rule's source."** Open the Knowledge section and click the rule, or run `python -m heatwave_es --rules | grep C5`.

---

## 12. Q&A bank

### A. Problem & domain
1. **What problem does your system solve?** It converts a temperature reading or forecast into an official IMD heat-wave classification, a colour-coded alert, and advice for each stakeholder. That is Phase V of SVU use case KJS-CES-01.
2. **Who are the users?** Citizens (incl. vulnerable groups and outdoor workers), farmers, health departments and hospitals, municipal authorities and SDMAs, and duty meteorologists who approve Red alerts.
3. **Why is this a good expert-system problem?** The domain knowledge is explicit, published and rule-shaped (IMD criteria, NDMA Do's and Don'ts). Explanations are needed for trust, and the answers must match official definitions exactly.
4. **Why not machine learning?** Heat-wave declaration is a *definition*, not a pattern. ML is used in Phase II to forecast temperature; our system interprets the forecast. ML also can't cite a guideline for its output.
5. **State the IMD criteria.** Threshold 40/37/30 °C (plains/coastal/hilly); departure 4.5-6.4 °C = heat wave, > 6.4 °C = severe; or actual ≥ 45 °C = heat wave, ≥ 47 °C = severe; declared after 2 consecutive days.
6. **Why do hilly regions have a 30 °C threshold?** Their normal temperatures are much lower, so 30 °C is already abnormal there.
7. **What is "departure from normal"?** Observed Tmax minus the long-term average Tmax for that date and place (the climatological normal).
8. **What is a warm night and why does it matter?** Tmax ≥ 40 and the Tmin departure is ≥ 4.5 °C. The body doesn't recover overnight, so we escalate Yellow to Orange.
9. **What is the heat index?** The feels-like temperature from temperature and humidity (NWS Rothfusz regression). Humidity blocks sweat cooling.
10. **Mumbai at 35 °C is not a heat wave, yet you give Yellow. Why?** The heat index is about 45 °C (danger band), so rule E2 escalates for humid heat stress. IMD thresholds alone miss humid danger.
11. **Difference between heat stroke and heat exhaustion?** Heat stroke has altered mental state or hot, dry skin with a body temperature above 40 °C and is an emergency (108). Heat exhaustion is heavy sweating, dizziness and weakness; treat with cooling and ORS.
12. **Why don't you give fluids to an unconscious person?** Choking/aspiration risk; MoHFW first-aid guidance.
13. **What are IMD's colour codes?** Green = no action, Yellow = be updated, Orange = be prepared, Red = take action.
14. **Where did you get the advice texts?** NDMA heat action plan guidelines, MoHFW NPCCHH, IMD/ICAR agromet advisories, and the Ahmedabad HAP. Each rule cites its source.
15. **What is the Ahmedabad Heat Action Plan?** South Asia's first city heat-health plan (2013), triggered by temperature alerts; the model for NDMA's guidelines.
16. **Which phase of the use case do you implement and how would it connect?** Phase V. It takes Phase II forecasts or Phase III/IV station readings as input (JSON or API), and its output feeds the dashboard and SMS alerts.

### B. Expert-system theory
17. **Define an expert system.** A program that reasons over explicit expert knowledge to solve domain problems at expert level, with an explanation facility.
18. **Name its components.** Knowledge base, working memory, inference engine, explanation facility, user interface (and knowledge acquisition).
19. **What is working memory?** The set of facts about the current case: user inputs plus derived facts.
20. **Knowledge base vs working memory?** The KB holds general rules that are the same for every case; WM holds the facts of *this* case and changes each run.
21. **What is a production rule?** IF conditions (LHS) THEN actions (RHS).
22. **Forward vs backward chaining?** See the table in 4.5. Forward is data → conclusions; backward is goal → sub-goals → facts.
23. **Why forward chaining for you?** Data comes first, there are many conclusions, it suits monitoring, and salience control.
24. **When would backward chaining be better?** For a single diagnostic question with many possible facts, where you want to ask only what is necessary (as our Prolog edition shows).
25. **What is the conflict set / agenda?** All rules whose conditions are currently satisfied and that have not fired yet.
26. **What is conflict resolution?** Choosing which one rule from the conflict set fires next.
27. **Which strategies do you use, in what order?** Refraction, salience, specificity, rule order.
28. **What is refraction and why is it needed?** A rule fires at most once. Without it, a rule whose conditions stay true would fire forever.
29. **What is salience?** A numeric priority on a rule (CLIPS term). Higher fires first.
30. **What is specificity?** More conditions means more specific; the specific rule is preferred over the general one.
31. **What is recency?** Preferring rules that match the newest facts (OPS5). We don't use it.
32. **What is the Rete algorithm? Do you use it?** An efficient incremental matching network that avoids re-testing every rule each cycle. No: with 59 rules, naive matching takes well under a millisecond.
33. **Is your reasoning monotonic?** No. Escalation modifies `alert`, so it is non-monotonic. We keep the previous value for explanation.
34. **What is the closed-world assumption?** Unknown means false. Our conditions on missing facts fail; Prolog uses negation-as-failure.
35. **What is MYCIN and what did it contribute?** A 1970s Stanford medical expert system using backward chaining and certainty factors. It introduced WHY/HOW explanations, which we also implement.
36. **What is the knowledge acquisition bottleneck?** Extracting and formalising expert knowledge is slow and error-prone. We experienced it translating IMD wording into rules.
37. **What is an expert system shell?** An inference engine without domain knowledge (CLIPS, Drools, experta). Our `engine.py` is a mini shell.
38. **What are certainty factors?** Numbers from −1 to 1 attached to rules and facts to express belief (MYCIN). We don't use them; a possible extension.
39. **Name some classic expert systems.** MYCIN, DENDRAL, XCON/R1, PROSPECTOR, CADUCEUS.
40. **What makes a knowledge base "consistent"?** No two rules derive contradictory conclusions from the same situation, no redundant rules, and no rules that can never fire. We check all three automatically.

### C. Knowledge base design
41. **How many rules? Why that many?** 59, across 9 layers covering triage, validation, derivation, classification, alert, escalation, governance, advice and summary. Each guideline clause becomes a rule.
42. **How are rules organised?** By layer (group) and salience; rule ids show the layer (T, V, D, C, W, H, A, E, G, P, F, M, X, K).
43. **How do you prevent contradictory categories?** C4-C7 require `hw_category is unknown`, and severe rules have higher salience, so the first conclusion wins and others can't fire.
44. **Why have a default rule C8?** To always conclude something. It is the "otherwise" case with low salience, so it fires only when no criterion matched.
45. **Why can severe Tmax ≥ 47 and departure 5.2 both match?** They're different IMD criteria. Severe rules have higher salience (78 vs 76), so severe wins: the conservative choice.
46. **Why is triage salience higher than validation?** The emergency advice doesn't depend on the temperature data, and a bad reading must never suppress "call 108".
47. **Why must escalation come before advice?** Advice depends on the final alert level. If advice fired first, rules for `alert == YELLOW` would fire on the stale value. For example, an authority would get both the Yellow (X1) and the Orange (X2) action lists, a contradictory mix (Drill 3).
48. **Why does E3 require RH ≥ 40 %?** The Rothfusz heat-index formula is unreliable in very dry air; without the condition, dry 44 °C days became Orange. Found by testing.
49. **Why only one escalation level?** To avoid over-warning. Responsible AI means communicating risk proportionately.
50. **What does G1 do?** It flags Red alerts for human (meteorologist) approval before dissemination: the use case's human-in-the-loop requirement.
51. **What happens if the duration is unknown?** A8 gives a conservative Yellow watch, and the output says so.
52. **What happens if humidity is unknown?** The heat-index rules can't fire, and G2 adds a note saying the humid-heat check was skipped.
53. **How do you compute the departure?** Rule D1 asserts a computed fact `departure = tmax − tmax_normal` using a lambda.
54. **How do you represent multi-valued facts like symptoms?** As lists, tested with the `contains` and `contains_any` operators.
55. **Show the rule dependency.** `docs/img/rule_dependency.png`: inputs → derived → classification → alert → escalation → conclusions.
56. **How would you add a new hazard (e.g. cold wave)?** Add a new rule layer with IMD cold-wave criteria; the engine needs no change.

### D. Inference engine implementation
57. **Walk me through `run()`.** Load inputs into WM. Loop: build the agenda, sort by priority, fire the first rule, mark it fired, apply its actions, record the trace, stop on halt or an empty agenda.
58. **How is the priority computed?** `(-salience, -len(conditions), index)`, sorted ascending.
59. **How does a condition handle a missing fact?** It returns False (except the `unknown` operator), so there is no crash.
60. **What if a user types text where a number is expected?** The CLI re-asks. Through the API, the engine catches the `TypeError` in the action and halts with "Invalid input…".
61. **How do you guarantee termination?** Refraction (each of 59 rules fires at most once) plus a `max_cycles` safety limit.
62. **Time complexity?** Each cycle checks all R rules × C conditions; at most R cycles, so O(R²·C) worst case ≈ 59² × 4. That's trivial.
63. **What does HALT do?** It stops inference immediately (validation errors). The trace and any emergency advice already produced are kept.
64. **What is `Fact.previous` for?** It keeps the old value when a rule modifies a fact, so HOW explains that Orange came from Yellow without looping.
65. **How is HOW implemented?** Recursively: fact → the rule that produced it → that rule's condition facts → … → user inputs.
66. **How is WHY implemented in the CLI?** `rules_using(fact)` lists the rules whose conditions mention the fact being asked, plus a reason string.
67. **Is the engine domain-independent?** Yes. `engine.py` has no heat-specific code; any rule list works (the conflict-resolution unit test uses toy rules).
68. **Why write your own engine instead of experta/CLIPS?** To demonstrate understanding of matching, conflict resolution and explanation; to avoid dependencies (experta is unmaintained on modern Python); and to control the trace format.

### E. Explanation & interface
69. **What does your trace show?** Cycle, rule id and name, salience, source, every condition with its actual value, facts asserted, the WHY justification, and the competing rules.
70. **HOW vs WHY?** HOW explains how a conclusion was reached (after the run). WHY explains why a question is being asked (during the run).
71. **How does the UI handle bad input?** Range-checked sliders and number inputs; the CLI re-asks with a hint; validation rules show an "Input rejected" card.
72. **Why three interfaces?** The CLI for the lab and testing, the web UI for usability, and Prolog to demonstrate backward chaining.
73. **Does the React UI contain rules?** No. It calls the Python API, so there is one source of truth.
74. **What is React Bits?** An open-source library of animated React components (Aurora, Stepper, AnimatedList…) copied into our project; the visual layer only.

### F. Testing
75. **How many tests?** 35 automated tests: 23 scenarios plus 12 unit tests. All pass.
76. **What does a scenario check?** Expected conclusions, the rules that must fire, the rules that must not fire, and the halting rule.
77. **What is rule coverage?** The percentage of rules that fire in at least one test. Ours is 59/59 = 100 %.
78. **Give edge cases you tested.** 39.9 vs 40.0 °C, departure exactly 4.5, Tmax 62, RH 140 %, 0 days, normal 70 °C, Tmin > Tmax, text input, missing data, humid heat below the threshold.
79. **How do you know your checker works?** We injected a duplicate, a dead rule and a contradiction, and it reported all three.
80. **Did Python and Prolog agree?** Yes, on all 6 shared test cases.
81. **What bugs did testing find?** The 5 listed in section 8.

### G. Prolog
82. **How does your Prolog version work?** The rules are `rule/4` facts, and a meta-interpreter `prove/3` does backward chaining, asking the user for missing facts and building a proof tree.
83. **Why a meta-interpreter instead of plain Prolog clauses?** To capture the proof for HOW and the goal stack for WHY; plain Prolog doesn't record them.
84. **How does Prolog resolve conflicts?** Clause order plus depth-first search; we add `once/1` so the first (most severe) proof wins.
85. **What is `assertz(known(A, V))` for?** Memoisation: each question is asked only once.
86. **What bug did you fix in Prolog?** `category(none)` succeeded on a heat-wave day because the catch-all clause was called with a bound argument. Fixed by computing unbound, then comparing.
87. **What does `?- run_tests_cases.` do?** Runs 6 cases in batch mode with no questions; missing facts are treated as unknown.

### H. Deployment & engineering
88. **How do you run it?** `python server.py`, `python -m heatwave_es`, or `swipl prolog/heatguard.pl`.
89. **Dependencies?** The core and the API use only the Python standard library; pytest, Streamlit and python-docx are optional; the UI needs Node only to rebuild.
90. **How is it deployed?** Vercel: the static React build plus Python serverless functions in `api/`.
91. **Why not Flask?** It isn't needed. Stdlib `http.server` is enough and means zero installs on lab PCs.

### I. Limitations & future work (critical-thinking questions)
92. **Biggest limitation?** Crisp thresholds: 39.9 °C gives Green and 40.0 °C gives Yellow, although real risk is continuous. Fuzzy logic or certainty factors would help.
93. **What can't it do that IMD does?** Spatial aggregation (≥ 2 stations per sub-division), and forecast uncertainty.
94. **How would you add uncertainty?** Certainty factors on forecast-based facts, or probabilistic alerts (e.g. "70 % chance of Orange").
95. **Can it learn?** No. New knowledge needs manual rule edits; that is a classic expert-system limitation.
96. **How would it scale to 1000 rules?** Use the Rete algorithm, rule modules or namespaces, and stronger static checking.
97. **How would you combine it with the LLM part of the use case?** The LLM writes natural, multilingual advisory text; our rules decide *what* must be said, and the trace fact-checks the LLM output.
98. **Ethical concerns?** Over-warning reduces trust and under-warning costs lives, hence human review of Red alerts. It is a decision-support tool, not a replacement for official IMD warnings.
99. **What would you change if you did it again?** Model multi-day forecasts, add a cold-wave module, multilingual output (Marathi/Hindi), and SMS integration.
100. **What did you personally learn?** Each member gives their own answer, linked to their D6 reflection.

### J. Curveballs
101. **"Your rule C6 and C7 can both match, isn't that redundant?"** No. They encode two *different* IMD criteria (absolute vs departure). Either alone proves a heat wave; the `hw_category unknown` guard means only one fires.
102. **"Isn't salience just hard-coding the order?"** It encodes domain priority (life safety > data validity > classification > advice). Within a layer, the order emerges from specificity and rule order. CLIPS uses the same mechanism.
103. **"What if two rules conclude different alerts?"** A1-A8 require `alert is unknown`, so the first concluded alert stands; only explicit escalation rules modify it, and that is logged.
104. **"Prove your system is correct."** We can't prove it in general, but it is validated against the official criteria on 23 documented scenarios, including every boundary, with 100 % rule coverage and automated consistency checks.
105. **"Where is the AI? It's just if-else."** It is *symbolic AI*: knowledge is separated from control. A generic inference engine decides which rules apply through conflict resolution, chains derived facts, and explains itself. If-else code hard-wires the control flow and can't explain or be extended rule by rule.

---

## 13. Things NOT to say
- ❌ "We made up the thresholds." → They are **IMD's criteria**.
- ❌ "It predicts heat waves." → It **classifies and advises** from a reading or forecast; prediction is Phase II.
- ❌ "It's 100 % accurate." → It is **consistent with the official criteria on all tested cases**.
- ❌ "The UI does the logic." → The **Python engine** does; the UI only displays it.
- ❌ "We used ChatGPT/Claude to make it." → If asked about tools, be honest, but **show that you understand every line** (this guide).
- ❌ "I don't know, member X did that." → Say "Let me walk through it" and use the trace.

---

## 14. One-page cheat sheet

```
PROJECT  HeatGuard: rule-based heat-wave early warning (SVU KJS-CES-01, IMD, Phase V)
KB       59 rules, 9 layers, 9 sources (IMD S1-S3, NDMA S4, MoHFW S5, NWS S6, ICAR S7, AHAP S8, gov S9)
ENGINE   forward chaining; cycle = MATCH -> RESOLVE -> ACT; repeat until agenda empty / HALT
RESOLVE  refraction -> salience -> specificity -> rule order     (_priority = (-sal, -#cond, idx))
SALIENCE triage 107-111 > validation 98-100 > derive 90 > classify 70-80 > alert 55-62
         > escalate 49-50 > governance 40 > advice 20 > summary 0
IMD      threshold 40/37/30 (plains/coast/hill); dep 4.5-6.4 HW, >6.4 severe; >=45 HW, >=47 severe; 2 days
COLOURS  Green none | Yellow HW 2-3d (day1 = watch) | Orange HW 4-6d or severe 2d | Red HW >6d or severe >2d
ESCALATE E1 warm night Y->O | E2 humid danger G->Y | E3 extreme HI & RH>=40 Y->O (one level max)
NIGHT    Tmax>=40 & Tmin dep 4.5-6.4 warm, >6.4 very warm
HI BANDS 27 caution | 32 extreme caution | 39 danger | 51 extreme danger  (Rothfusz, deg F inside)
TRIAGE   confusion/unconscious/seizure OR hot+dry skin = STROKE (call 108/112); sweating/dizzy = EXHAUSTION; cramps
EXPLAIN  trace (IF actual values, THEN, WHY, source, competing rules) + HOW tree + WHY at questions
PROLOG   backward chaining meta-interpreter prove/3; rule/4 facts; asks only needed facts; once/1 = first wins
TESTS    35 passing; 23 scenarios; must_fire / must_not_fire; kb_check 0 problems; coverage 59/59
RUN      python server.py | python -m heatwave_es | python -m pytest -q | python -m heatwave_es.kb_check
         swipl prolog/heatguard.pl  ?- start.
LIMITS   crisp thresholds, no uncertainty, no learning, single station, knowledge bottleneck, rule interactions
```

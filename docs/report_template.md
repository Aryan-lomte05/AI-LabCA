---
title: "HeatGuard: A Rule-Based Expert System for Heatwave Early Warning and Stakeholder Advisory"
subtitle: "LAB CA Component 2 / Experiment 10: Design and Implementation of a Simple Rule-Based Expert System for a Real-World Advisory Problem"
---

| | |
|---|---|
| **Institute** | Somaiya Vidyavihar University, K. J. Somaiya School of Engineering |
| **Department / Programme** | Electronics & Computer Engineering, CSBS, TY (Sem V), 2026-27 |
| **Course** | 216U50E514 Artificial Intelligence |
| **Faculty in-charge** | Dr. Ayesha Hakim |
| **SVU AI use case** | KJS-CES-01: Climate Intelligence for Heatwave Monitoring, Prediction, and Early Warning (faculty owner: Dr. Radhika Kotecha; collaborating organisation: IMD Mumbai-Pune) |
| **Group members** | 1. ____________ (Roll No. ______)  2. ____________ (Roll No. ______)  3. ____________ (Roll No. ______) |
| **Date of submission** | ___ / 10 / 2026 |

# D1. Problem Definition

## 1.1 Domain and motivation

Heatwaves are among the deadliest weather hazards in India. With climate change they are becoming more frequent, more intense and longer. The SVU use case **KJS-CES-01** sets out a five-phase heatwave intelligence platform: data acquisition, AI forecasting, IoT weather stations, forecast validation, and **Phase V: Advisory, Early Warning and Decision Support**. Phase V must "translate technical forecasts into stakeholder-specific advisories and early warnings for citizens, farmers, health agencies, and local authorities".

**HeatGuard** is a rule-based expert system for Phase V. It takes a temperature observation or forecast for a location, which in the full platform would come from IMD data, an AI forecast or an IoT Automated Weather Station. From that input it:

1. classifies the day using the **official IMD heat-wave criteria** (none / heat wave / severe heat wave);
2. assigns an **IMD colour-coded alert** (Green / Yellow / Orange / Red), taking persistence into account;
3. **escalates** the alert when nights are warm or humid heat is dangerous;
4. **triages heat-related illness symptoms** (heat stroke vs. heat exhaustion vs. heat cramps);
5. issues **advisories tailored to the stakeholder** (citizen, vulnerable person, outdoor worker, farmer, health department, municipal authority);
6. shows a full **explanation trace**: which rules fired, why, and on which guideline each rule is based.

## 1.2 Why a rule-based expert system?

Heat-wave declaration in India is *defined* by explicit, published thresholds. A heat wave is not a fuzzy pattern to be learned; it is a regulatory definition. Advisories (NDMA Do's & Don'ts, MoHFW first aid) are also explicit IF-THEN guidance. A rule-based system is therefore:

- **faithful**: it reproduces the official criteria exactly;
- **transparent and auditable**: the use case marks *Responsible AI* and *Human-in-the-loop* as **High** relevance, and every conclusion here can be traced to a rule and its source;
- **complementary to ML**: Phase II forecasts *what the temperature will be*; this system decides *what that temperature means and what people should do*. It can also check the facts in LLM-generated advisories (use-case governance item "ensuring factual consistency").

## 1.3 Scope

| In scope | Out of scope |
|---|---|
| IMD heat-wave & severe heat-wave classification for plains, coastal and hilly stations | Forecasting temperature (Phase II ML models) |
| IMD colour-coded alert from persistence (days) | Multi-station spatial aggregation (IMD needs ≥2 stations in a sub-division) |
| Warm-night and humid-heat (heat index) escalation | Real-time AWS ingestion (inputs are typed in or come from JSON) |
| First-level triage of heat-related illness symptoms | Medical diagnosis; the system only advises calling 108/112 |
| Advisories for 4 stakeholder roles and 5 vulnerable groups | Multilingual / LLM text generation |

## 1.4 Target users

- **Citizens and households**, including the elderly, infants, pregnant women, the chronically ill and outdoor workers.
- **Farmers** (crops and/or livestock).
- **Public health departments and hospitals** (preparedness and response).
- **Municipal corporations / District & State Disaster Management Authorities** (Heat Action Plan triggers).
- **Duty meteorologists**, who review Red alerts (human in the loop).

## 1.5 Sources of expert knowledge

The rules are taken from published guidelines, not invented:

{{SOURCES}}

# D2. Knowledge Base Design

## 2.1 Facts (working-memory attributes)

| Fact | Type / values | Origin |
|---|---|---|
| `role` | citizen, farmer, health, authority | user |
| `region` | plains, coastal, hilly | user |
| `tmax`, `tmax_normal` | °C | user (`tmax_normal` optional) |
| `heat_days` | 1-60 consecutive days | user (optional) |
| `rh` | 0-100 % | user (optional) |
| `tmin`, `tmin_normal` | °C | user (optional, asked only if Tmax ≥ 40) |
| `vulnerable` | elderly, infant_child, pregnant, chronic_illness, outdoor_worker | user (citizen) |
| `farm` | crops, livestock, both | user (farmer) |
| `symptoms` | 12 symptom codes | user (citizen / health) |
| `departure`, `tmin_departure`, `heat_index` | °C | derived (D1-D3) |
| `threshold_met`, `hw_category`, `night`, `hi_level`, `hri` | symbolic | inferred |
| `alert`, `status`, `escalated`, `needs_review`, `recommendation` | symbolic | inferred (conclusions) |

## 2.2 Rule layers and salience

The knowledge base holds **{{N_RULES}} production rules** in 9 layers. Salience (priority) follows the order in which a duty officer would reason: life safety first, then data quality, then classification, then advice.

| Layer | Rules | Salience | Purpose |
|---|---|---|---|
| T - Triage | T1-T7 | 107-111 | Heat-illness triage; runs even if the weather data are invalid |
| V - Validation | V1-V5, D0 | 98-100 | Reject impossible inputs (HALT) |
| D - Derivation | D1-D3 | 90 | Departure from normal, Tmin departure, heat index |
| C/W/H - Classification | C1-C8, W1-W2, H1-H4 | 70-80 | IMD threshold & category, warm night, heat-stress band |
| A - Alert | A1-A8 | 55-62 | IMD colour code from category + persistence |
| E - Escalation | E1-E3 | 49-50 | Warm night / humid heat raises the alert one level |
| G - Governance | G1-G3 | 40 | Human review of Red alerts; notes on missing data |
| P/F/M/X - Advisory | 14 rules | 20 | Citizen, farmer, health-department, authority advice |
| K - Summary | K1 | 0 | Final recommendation |

## 2.3 Complete rule table (IF-THEN)

{{RULE_TABLE}}

## 2.4 Rule-dependency diagram

![Rule-dependency diagram: how facts flow from user inputs through derivation and classification to the alert and the stakeholder advice.](img/rule_dependency.png)

## 2.5 Design decisions for consistency and non-redundancy

- **Mutually exclusive categories.** C4-C7 all require `hw_category is unknown`. With severe rules at higher salience (78) than heat-wave rules (76), the first category concluded is the final one, so no two category rules contradict each other.
- **Single default.** C8 (*no heat wave*) has the lowest classification salience (70). It fires only when no criterion matched. This is the expert-system form of "otherwise".
- **Escalation by one level only.** E3 requires `escalated is unknown`, so warm night plus humid heat cannot push Yellow to Red. The use case asks the system to communicate uncertainty, not to over-warn.
- **Edge cases covered.** Exact thresholds (40.0 °C, +4.5 °C) and just-below values (39.9 °C) are tested. So are missing optional inputs, impossible values, physically inconsistent values (Tmin > Tmax), and dangerous humid heat below the IMD thresholds (Mumbai).

# D3. Implementation

## 3.1 Architecture

```
heatwave_es/
  engine.py          generic forward-chaining engine (working memory, agenda,
                     conflict resolution, trace, HOW explanation)
  knowledge_base.py  the rules + sources + heat-index computation (domain only)
  explain.py         recommendation / advisory / trace / HOW formatting
  cli.py             interactive question-answer interface (WHY, skip, HOW)
  scenarios.py       test scenarios (D4)
app.py               Streamlit web interface (optional)
prolog/heatguard.pl  SWI-Prolog edition: backward chaining meta-interpreter
tests/               pytest suite
```

The **knowledge base is kept separate from the inference engine**. The rules are data (`Rule` objects with conditions, actions, salience and source), so a domain expert could add a rule without touching the engine.

## 3.2 Choice of inference strategy: forward chaining (justified)

The Python engine uses **forward chaining** (data-driven), for these reasons:

1. **The data arrive first.** In the use-case pipeline, observations and forecasts (IMD grids, AWS readings, ML forecasts) are pushed to the advisory module. The natural question is "given these readings, what follows?", which is a forward-chaining question.
2. **There are many conclusions, not one goal.** From one observation the system must derive the category, the alert, escalations, governance flags *and* advice for several audiences. Backward chaining would need a separate query for each goal.
3. **Monitoring suits it.** In deployment the same rules re-run every time an AWS reading arrives. Forward chaining is the standard architecture for monitoring and alerting systems (as in CLIPS and OPS5).
4. **Priority matters.** Salience-based conflict resolution lets *life-safety triage* fire before everything else and *validation* halt bad data before any classification.

For comparison, the **Prolog edition uses backward chaining**. It starts from the goal `final_alert(L)` and asks the user *only* for facts that the current line of proof needs. For example, it never asks for the normal temperature when Tmax is below the regional threshold. This is ideal for an interactive consultation, and the viva discussion compares the two.

## 3.3 The recognise-act cycle and conflict resolution

```
repeat
    MATCH   : agenda = all rules whose conditions hold and that have not fired
    if agenda empty: stop
    RESOLVE : pick 1 rule by (1) refraction, (2) highest salience,
              (3) highest specificity (most conditions), (4) rule order
    ACT     : assert/modify facts, emit advice, record trace; HALT if rule says so
```

- **Refraction**: each rule fires at most once, which guarantees termination.
- **Salience**: domain priority, e.g. T1 (heat stroke, 111) before V1 (validation, 100).
- **Specificity**: a more specific rule beats a general one at equal salience.
- **Robustness**: conditions on missing facts are simply not satisfied, so the engine never crashes on missing input. Implausible values trigger validation rules that HALT with a clear message. A type error inside an action (e.g. text where a number is expected) is caught and reported as an input error.

## 3.4 Explanation facility

- **Trace**: for every fired rule, the system shows its id, name, salience and source, each condition with the *actual* value matched, the facts asserted, a one-line justification ("WHY"), and the other rules that were in the conflict set at that moment.
- **HOW**: a recursive proof tree for any concluded fact (e.g. `how alert`). It correctly shows an escalated alert as derived from the earlier alert value.
- **WHY (during questioning)**: typing `why` at any question explains why it is asked and lists the rules that use the answer.
- **Sources**: every report ends with the guidelines used for that run.

## 3.5 User interface

- **CLI** (`python -m heatwave_es`): asks only relevant questions (role-dependent, and Tmin only when Tmax ≥ 40 °C). It accepts prefixes (`p` → plains), validates ranges, lets optional questions be skipped, re-asks politely on bad input, and supports `why`, `how <fact>`, `new` and `quit`.
- **Batch mode** (`python -m heatwave_es --json case.json`) and **rule listing** (`--rules`).
- **Web UI** (`streamlit run app.py`): sidebar form, colour-coded alert banner, advisory, trace, HOW selector, and browsable knowledge base.
- **Prolog** (`swipl prolog/heatguard.pl`, then `?- start.`): goal-driven consultation with `why` and a proof tree.

## 3.6 Sample run (TC09, warm-night escalation)

```
{{SAMPLE_RUN}}
```

# D4. Test Case Report

The automated suite (`python -m pytest`) runs **{{N_TESTS}} scenarios** plus unit tests for conflict resolution, the HOW explanation, the heat-index reference values and wrong-type input. Each scenario asserts the expected conclusions, the rules that must fire and the rules that must *not* fire.

**Result: {{PYTEST}}**

## 4.1 Summary

{{TEST_TABLE}}

## 4.2 Detailed scenarios

{{TEST_DETAILS}}

## 4.3 Cross-check with the Prolog edition

Scenarios TC01, TC02, TC03, TC04, TC06 and TC09 were also run through the backward-chaining Prolog edition (`?- run_tests_cases.`). It produced **the same alert levels** (Green, Yellow, Red, Yellow-watch, Yellow + emergency, Orange), which shows that the knowledge is independent of the inference strategy.

# D5. Demo Plan (live run, 2-3 queries)

1. **Normal vs. watch vs. declared**: TC01 (Green) → TC04 (Yellow *watch*, day 1) → change days to 3 (Yellow *declared*). Shows the IMD persistence rule.
2. **Escalation and HOW**: TC09. Show the trace, then type `how alert` to see Yellow (A3) → Orange (E1, warm night).
3. **Robustness and life safety**: enter Tmax = 62 (V1 halts with a clear message), then TC06 (heat-stroke symptoms → EMERGENCY advice fires first).
4. *(Optional)* The same consultation in Prolog: type `why` at the "normal temperature" question to show the goal stack.

# D6. Reflection Notes (individual, ½ page each)

*Each member writes this section separately in their own words. The prompts below are a guide.*

**Member 1, ____________ (Roll No. ______)**
*Contribution:* ______________________________________________
*One limitation of rule-based systems observed:* ______________________________________________

**Member 2, ____________ (Roll No. ______)**
*Contribution:* ______________________________________________
*One limitation of rule-based systems observed:* ______________________________________________

**Member 3, ____________ (Roll No. ______)**
*Contribution:* ______________________________________________
*One limitation of rule-based systems observed:* ______________________________________________

Limitations we observed, for members to choose from and expand:

- **Brittle crisp thresholds.** 39.9 °C gives *Green* and 40.0 °C gives *Yellow* (TC11 vs. TC12). Real risk is continuous, and fuzzy logic or certainty factors would model it better.
- **The knowledge-acquisition bottleneck.** IMD defines the colour code in words ("persists for more than 2 days"), and turning these into rules forced us to make choices. Day-1 severe heat had to become a *watch*, and the case where the duration is unknown needed its own rule (A8).
- **Rule interaction is hard to reason about.** Our first version escalated hot, dry 44 °C days to Orange, because the Rothfusz heat-index formula exaggerates heat stress in very dry air. Adding the RH ≥ 40 % condition to E3 fixed it, but the bug appeared only through testing.
- **No learning.** The system cannot adapt to local mortality data, so new evidence means a manual rule edit.
- **No uncertainty handling.** A forecast of 45 °C with 60 % confidence is treated the same as an observed 45 °C.
- **Scalability.** Validating 59 rules was manageable, but with hundreds of rules, conflicts and redundancy become hard to spot without tools.

# References

{{REFERENCES}}

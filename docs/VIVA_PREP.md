# Viva preparation: key discussion points (D5)

*Every member should be able to answer all of these. The faculty can adjust marks by ±3 based on the viva.*

## 1. Problem and domain

**Q: Which SVU use case did you choose and which part of it does your system cover?**
KJS-CES-01, Climate Intelligence for Heatwave Monitoring (IMD Mumbai-Pune). We cover **Phase V: Advisory, Early Warning & Decision Support**, which turns a temperature reading or forecast into an official heat-wave classification, a colour-coded alert, and advice for each stakeholder.

**Q: Why a rule-based system and not ML?**
In India a heat wave is *defined* by IMD's published thresholds, so it is a rule, not a pattern to learn. Advisories (NDMA, MoHFW) are also explicit IF-THEN guidance. Rules are transparent and auditable, which the use case rates as **High** relevance under Responsible AI and Human-in-the-loop. ML (Phase II) predicts the temperature; our system interprets it.

**Q: Where do your rules come from?**
Nine sources (S1-S9): IMD heat-wave criteria, IMD colour codes, IMD warm-night criteria, NDMA heat action plan guidelines, MoHFW NPCCHH heat-illness plan, NWS heat index (Rothfusz), IMD/ICAR agromet advisories, the Ahmedabad Heat Action Plan, and the use-case governance table. Every rule stores its source, and every run prints the sources it used.

## 2. Knowledge base

**Q: State the IMD heat-wave criteria.**
The threshold must be reached first: Tmax ≥ 40 °C in plains, ≥ 37 °C at coastal stations, ≥ 30 °C in hilly regions. After that:
- departure from normal of 4.5-6.4 °C is a **heat wave**; more than 6.4 °C is a **severe heat wave**;
- *or* an actual Tmax ≥ 45 °C is a heat wave and ≥ 47 °C is a severe heat wave;
- a heat wave is declared when the criteria hold for 2 consecutive days.

**Q: How many rules do you have, and how are they organised?**
59 rules in 9 layers: Triage, Validation, Derivation, Classification (C/W/H), Alert, Escalation, Governance, Advisory, and Summary. Salience increases with urgency.

**Q: How did you avoid contradictory rules?**
- Category rules all require `hw_category is unknown`, and severe rules have higher salience, so the first conclusion is the final one.
- C8 is the single default rule ("otherwise no heat wave").
- Escalation E3 requires `escalated is unknown`, which limits escalation to one level.
- pytest checks that each scenario fires exactly the rules it should and none it should not.

**Q: Give an edge case.**
- Mumbai at 35 °C with 60 % humidity: there is no IMD heat wave because 35 < 37, but the heat index is 45 °C ("danger"), so E2 raises Green to Yellow (TC02).
- 39.9 °C vs. 40.0 °C (TC11/TC12).
- Tmin > Tmax (TC10).
- A Tmax of 62 °C (TC07).

## 3. Inference engine

**Q: Forward or backward chaining, and why?**
Python uses **forward chaining**:
- the data (AWS readings, forecasts) arrive first;
- one observation leads to *many* conclusions (category, alert, escalation, advice for several roles);
- forward chaining suits continuous monitoring;
- salience lets life-safety rules fire first.

The **Prolog** edition uses **backward chaining** from the goal `final_alert(L)`. It asks only what the proof needs, which suits interactive consultation.

**Q: Explain the recognise-act cycle.**
MATCH: build the agenda of all rules whose conditions hold. RESOLVE: pick one. ACT: assert facts, give advice, or halt. Repeat until the agenda is empty.

**Q: What is conflict resolution, and which strategies do you use?**
Several rules can be ready to fire at once. We choose using:
1. **refraction**: each rule fires once, which guarantees termination;
2. **salience**: priority;
3. **specificity**: more conditions win;
4. **rule order**.

The trace prints "conflict set also had: ..." for every cycle. Prolog uses rule order plus `once/1`.

**Q: How does your system handle invalid or missing input?**
- *Invalid:* the CLI re-asks on bad types or ranges. Validation rules V1-V5 HALT on impossible values. A type error inside an action is caught and reported.
- *Missing:* a condition on an unknown fact is simply false. Rules A8, G2 and G3 handle missing duration, humidity and Tmin with conservative behaviour and a visible note.
- *Life safety:* triage (salience 107-111) runs **before** validation, so heat-stroke advice is still given even when the temperature input is wrong.

**Q: Why is triage given a higher salience than validation?**
Symptoms are independent of the temperature data. A wrong thermometer reading must never suppress "call 108".

**Q: What is a heat index and why do you use it?**
It is the "feels-like" temperature from temperature and humidity, calculated with the NWS Rothfusz regression. Humid heat stops sweat from evaporating. E3 also requires RH ≥ 40 % because the formula over-estimates heat stress in very dry air. We found that problem while testing.

## 4. Explanation facility

- **Trace**: each fired rule, with the conditions and their actual values, the facts asserted, a WHY line, its source, and the competing rules.
- **HOW**: a recursive proof tree for any fact (`how alert`). It handles a fact that was modified, such as the alert escalated from Yellow to Orange, by explaining the earlier value.
- **WHY**: typed during questioning. The CLI lists the rules that use the answer; Prolog prints the goal stack.

## 5. Implementation questions

**Q: How is the knowledge separated from the engine?**
`engine.py` knows nothing about heat. `knowledge_base.py` is a list of `Rule` data objects, so the engine could be reused for another domain without changes.

**Q: What does `Condition("tmax", ">=", 40)` do when tmax is missing?**
It returns False, the rule does not match, and nothing crashes.

**Q: How would you deploy this in the real platform?**
1. Feed AWS/IMD readings as JSON (`--json`) on every update.
2. Publish the alert to the dashboard or SMS.
3. Route Red alerts to the duty meteorologist (G1) for approval.
4. Use the trace to fact-check LLM-generated advisory text.

## 6. Limitations (also used for D6)

- Crisp thresholds: 39.9 vs. 40.0 °C.
- No uncertainty or certainty factors.
- No learning.
- The knowledge-acquisition bottleneck: turning wording into rules (A2 "watch", A8 unknown duration).
- Interactions between rules are hard to foresee (the dry-heat escalation bug).
- Single-station view: IMD needs ≥ 2 stations.
- Maintaining many rules gets hard as the knowledge base grows.

## 7. Demo script (about 5 minutes)

```bash
python -m heatwave_es --rules | tail -3          # show the 59-rule knowledge base
python -m heatwave_es                            # live consultation
#   citizen, plains, 45.6, 39.8, 3, 25, [why], 31, 26, elderly,outdoor_worker, none
#   then type:  how alert
python -m heatwave_es --json examples/invalid_reading.json --brief   # robustness
python -m pytest -q                              # all tests passing
swipl prolog/heatguard.pl                        # ?- start.   (type 'why' at a question)
streamlit run app.py                             # optional GUI
```

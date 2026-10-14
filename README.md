# HeatGuard: Heatwave Early-Warning & Advisory Expert System

**AI LAB CA Component 2 / Experiment 10**: Design and Implementation of a Simple Rule-Based Expert System for a Real-World Advisory Problem.
SVU AI use case **KJS-CES-01: Climate Intelligence for Heatwave Monitoring, Prediction, and Early Warning** (IMD Mumbai-Pune), Phase V: Advisory & Early Warning.

From a temperature observation or forecast, HeatGuard:

- classifies the day using the official **IMD heat-wave criteria**;
- issues the **IMD colour-coded alert** (Green / Yellow / Orange / Red);
- escalates the alert for **warm nights** and **humid heat** (heat index);
- **triages heat-illness symptoms**, with heat stroke treated as an emergency;
- gives **stakeholder-specific advice** to citizens, vulnerable groups, outdoor workers, farmers, health departments and municipal authorities;
- shows a full **explanation trace** (rules fired, why, and the source guideline) plus **HOW** and **WHY** queries.

## Contents

| Deliverable | Where |
|---|---|
| D1 Problem definition | `docs/HeatGuard_Report.pdf`, section D1 |
| D2 Knowledge base (59 IF-THEN rules, dependency diagram) | `heatwave_es/knowledge_base.py`, report section D2, `docs/img/rule_dependency.png` |
| D3 Implementation (forward-chaining engine + explanation) | `heatwave_es/`, `app.py`, `prolog/heatguard.pl` |
| D4 Test case report (23 scenarios, 100 % rule coverage) | `docs/Test_Case_Report.md`, report section D4, `tests/` |
| D5 Demo + viva | `docs/STUDY_GUIDE.md` (full guide, 105 Q&As), `docs/viva-trainer.html` (flashcards + quiz), `docs/VIVA_PREP.md` |
| D6 Reflection (individual) | report section D6 (each member fills in their own) |

## HeatGuard Atlas: the web UI

A React + Tailwind interface built with [React Bits](https://reactbits.dev) components: an Aurora hero, SplitText/GradientText headings, a Stepper consultation wizard, a DecryptedText alert, SpotlightCards, AnimatedList advisories and trace, Magnet preset chips, StarBorder buttons and ClickSpark. Every answer you change is sent straight to the Python inference engine.

```bash
python server.py            # open http://localhost:8000  (the built UI is committed, no Node needed)

# to edit the UI:
cd frontend && npm install && npm run dev    # http://localhost:5173 (proxies /api to :8000)
npm run build                                # rebuild frontend/dist
```

## Deploy on Vercel

The repo is ready for Vercel with zero configuration on the dashboard. `vercel.json` builds the React UI from `frontend/`. The files `api/consult.py`, `api/kb.py` and `api/scenarios.py` run the same Python engine as serverless functions; they use only the standard library, so there is nothing to install.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/aryan-lomte05/ai-labca)

Or go to vercel.com → **Add New… → Project**, import `aryan-lomte05/ai-labca`, and click **Deploy**. You can also use the CLI:

```bash
npm i -g vercel
vercel          # preview deployment
vercel --prod   # production deployment
```

## Run

Python 3.9+ is required. The core system has **no dependencies**.

```bash
python -m heatwave_es                 # interactive consultation (type 'why' at any question)
python -m heatwave_es --json examples/warm_night_escalation.json
python -m heatwave_es --rules         # print the knowledge base
python -m heatwave_es.kb_check        # consistency + rule-coverage check

pip install -r requirements-dev.txt
python -m pytest -q                   # 35 tests
streamlit run app.py                  # lighter Streamlit interface
python tools/build_report.py          # regenerate report (needs pandoc; PDF needs LibreOffice)
```

Prolog edition (backward chaining with WHY/HOW), using SWI-Prolog:

```bash
swipl prolog/heatguard.pl
?- start.              % interactive consultation
?- run_tests_cases.    % 6 test cases, same results as the Python edition
```

## Design in one paragraph

The knowledge base (`knowledge_base.py`) is pure data: each `Rule` has conditions, actions, a **salience** and a **source**. The generic engine (`engine.py`) runs the forward-chaining **recognise-act cycle**:

1. **match**: find every rule whose conditions hold;
2. **resolve conflicts**: apply refraction, then salience, then specificity, then rule order;
3. **act**: assert facts, give advice, or halt.

It records a trace entry for every rule it fires. Forward chaining fits the use case: readings stream in from weather stations and forecasts, each reading leads to many conclusions (category, alert, escalation, advice for several roles), and life-safety triage must fire before everything else. The Prolog edition shows the backward-chaining alternative for comparison.

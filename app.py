"""
HeatGuard - Streamlit web interface (optional, friendlier than the CLI).

    pip install streamlit
    streamlit run app.py
"""

import streamlit as st

from heatwave_es import build_engine
from heatwave_es.cli import SYMPTOMS, VULNERABLE
from heatwave_es.explain import advice_lines, how_lines, summary_lines, trace_lines
from heatwave_es.knowledge_base import ALERT_MEANING, RULES, SOURCES

COLOURS = {"GREEN": "#2e7d32", "YELLOW": "#f9a825", "ORANGE": "#ef6c00", "RED": "#c62828"}

st.set_page_config(page_title="HeatGuard", page_icon="🌡️", layout="wide")
st.title("🌡️ HeatGuard - Heatwave Early-Warning Advisory")
st.caption("Rule-based expert system | SVU use case KJS-CES-01 | IMD heat-wave criteria, "
           "NDMA & NPCCHH guidelines | forward-chaining inference with explanation")

engine = build_engine()

with st.sidebar:
    st.header("Situation")
    role = st.selectbox("Advice for", ["citizen", "farmer", "health", "authority"])
    region = st.selectbox("Region type", ["plains", "coastal", "hilly"])
    tmax = st.number_input("Max temperature Tmax (°C)", -10.0, 60.0, 44.0, 0.1)
    use_normal = st.checkbox("I know the normal Tmax", True)
    tmax_normal = st.number_input("Normal Tmax (°C)", 5.0, 50.0, 39.0, 0.1,
                                  disabled=not use_normal)
    use_days = st.checkbox("I know how many days it has been this hot", True)
    heat_days = st.number_input("Consecutive hot days (incl. today)", 1, 60, 2,
                                disabled=not use_days)
    use_rh = st.checkbox("I know the humidity", True)
    rh = st.slider("Relative humidity (%)", 0, 100, 30, disabled=not use_rh)
    use_tmin = st.checkbox("I know the night (minimum) temperature", False)
    tmin = st.number_input("Tmin (°C)", -10.0, 45.0, 28.0, 0.1, disabled=not use_tmin)
    tmin_normal = st.number_input("Normal Tmin (°C)", -10.0, 40.0, 25.0, 0.1,
                                  disabled=not use_tmin)
    facts = {"role": role, "region": region, "tmax": tmax}
    if use_normal:
        facts["tmax_normal"] = tmax_normal
    if use_days:
        facts["heat_days"] = int(heat_days)
    if use_rh:
        facts["rh"] = rh
    if use_tmin:
        facts["tmin"], facts["tmin_normal"] = tmin, tmin_normal
    if role == "citizen":
        facts["vulnerable"] = st.multiselect("Household includes", VULNERABLE[1:])
    if role == "farmer":
        facts["farm"] = st.radio("You manage", ["crops", "livestock", "both"])
    if role in ("citizen", "health"):
        facts["symptoms"] = st.multiselect("Symptoms seen now", SYMPTOMS[1:])

result = engine.run(facts)
alert = result.facts.get("alert")

if result.facts.get("emergency"):
    st.error("🚑 SUSPECTED HEAT STROKE - call 108 / 112 now. See first-aid steps below.")

if alert:
    st.markdown(
        f"<div style='background:{COLOURS[alert]};color:white;padding:18px;border-radius:10px;"
        f"font-size:1.4em'><b>{alert} ALERT</b> - {ALERT_MEANING[alert]}</div>",
        unsafe_allow_html=True)
lines = summary_lines(result)
(st.warning if result.halted_by else st.subheader)(lines[0])
for d in lines[1:]:
    st.write(d.strip(" -"))

col1, col2 = st.columns(2)
with col1:
    st.subheader("Advisory")
    st.code("\n".join(advice_lines(result)) or "(none)", language=None)
with col2:
    st.subheader(f"Explanation trace - {len(result.trace)} rules fired")
    st.code("\n".join(trace_lines(result, verbose=True)), language=None)
    fact = st.selectbox("HOW was this concluded?", sorted(result.facts),
                        index=sorted(result.facts).index("alert") if alert else 0)
    st.code("\n".join(how_lines(engine, result, fact)), language=None)

with st.expander(f"Knowledge base ({len(RULES)} rules)"):
    st.table([{"id": r.id, "group": r.group, "IF": r.if_text(), "THEN": r.then_text(),
               "salience": r.salience, "source": r.source} for r in RULES])
with st.expander("Sources of expert knowledge"):
    for k, v in SOURCES.items():
        st.markdown(f"**{k}** - {v}")

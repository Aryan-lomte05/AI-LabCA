"""
Knowledge base: HeatGuard - Heatwave Early-Warning & Advisory Expert System.

Use case KJS-CES-01 (SVU): "Climate Intelligence for Heatwave Monitoring,
Prediction, and Early Warning" (collaborating org: IMD Mumbai-Pune).
This expert system implements Phase V of that use case: turning a
temperature observation/forecast into an IMD-style heatwave classification,
a colour-coded alert, and stakeholder-specific advisories.

Every rule cites the guideline it is taken from (see SOURCES).  Rules are
grouped into layers and ordered by salience so that conflict resolution
mirrors the order a duty officer would reason in:

    salience 107-111 T - heat-illness triage (life-safety first, always runs)
    salience 100  V  - input validation (halts on impossible data)
    salience  90  D  - derived quantities (departure, heat index)
    salience  80  C/W/H - IMD classification, warm night, heat stress
    salience  60  A  - IMD colour-coded alert level
    salience  50  E  - escalation (warm nights / humid heat)
    salience  40  G  - governance & data-gap notes
    salience  20  P/F/M/X - stakeholder advisories
    salience   0  K  - final recommendation summary
"""

from __future__ import annotations

import math

from .engine import Condition as C, Rule

# ---------------------------------------------------------------------------
# Sources of expert knowledge (rules are NOT invented arbitrarily)
# ---------------------------------------------------------------------------

SOURCES = {
    "S1": "IMD - Heat wave criteria (FAQ on Heat Wave, mausam.imd.gov.in): "
          "threshold 40 C plains / 37 C coastal / 30 C hilly; departure from "
          "normal 4.5-6.4 C = heat wave, >6.4 C = severe; actual Tmax >=45 C "
          "= heat wave, >=47 C = severe; declared when met on 2 consecutive days.",
    "S2": "IMD - Colour-coded impact-based heat warnings (Green / Yellow / "
          "Orange / Red) based on intensity and persistence of heat wave days.",
    "S3": "IMD - Warm night criteria: Tmax >=40 C and Tmin departure 4.5-6.4 C "
          "= warm night, >6.4 C = very warm night.",
    "S4": "NDMA - Guidelines for Preparation of Action Plan: Prevention and "
          "Management of Heat Wave (2016, rev. 2019): Do's & Don'ts, "
          "stakeholder roles, cooling centres, work-hour rescheduling.",
    "S5": "MoHFW / NCDC - National Programme on Climate Change & Human Health "
          "(NPCCHH): National Action Plan on Heat Related Illnesses (2021) - "
          "HRI symptoms, first aid, hospital preparedness.",
    "S6": "US NWS / NOAA - Heat Index (Rothfusz regression, 1990) and risk "
          "bands: Caution 27-32 C, Extreme caution 32-39 C, Danger 39-51 C, "
          "Extreme danger >=51 C.",
    "S7": "IMD / ICAR - Gramin Krishi Mausam Sewa agromet advisories for "
          "heat wave: irrigation timing, mulching, spraying, livestock care.",
    "S8": "Ahmedabad Heat Action Plan (AMC, 2013 onward) - model city plan "
          "for alert-triggered actions by municipal and health departments.",
    "S9": "SVU use case KJS-CES-01 - AI governance: human-in-the-loop review "
          "of critical warnings before dissemination.",
}

ALERT_ORDER = ["GREEN", "YELLOW", "ORANGE", "RED"]
ALERT_MEANING = {
    "GREEN": "No action - normal day",
    "YELLOW": "Heat alert - be updated",
    "ORANGE": "Severe heat alert - be prepared",
    "RED": "Extreme heat alert - take action",
}

# ---------------------------------------------------------------------------
# Helper computations used by derivation rules
# ---------------------------------------------------------------------------


def heat_index_c(t_c: float, rh: float) -> float:
    """NWS heat index (Rothfusz regression with NWS adjustments), in deg C."""
    t = t_c * 9 / 5 + 32
    simple = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + rh * 0.094)
    if (simple + t) / 2 < 80:
        hi = simple
    else:
        hi = (-42.379 + 2.04901523 * t + 10.14333127 * rh
              - 0.22475541 * t * rh - 0.00683783 * t * t
              - 0.05481717 * rh * rh + 0.00122874 * t * t * rh
              + 0.00085282 * t * rh * rh - 0.00000199 * t * t * rh * rh)
        if rh < 13 and 80 <= t <= 112:
            hi -= ((13 - rh) / 4) * math.sqrt((17 - abs(t - 95)) / 17)
        elif rh > 85 and 80 <= t <= 87:
            hi += ((rh - 85) / 10) * ((87 - t) / 5)
    return round((hi - 32) * 5 / 9, 1)


def _headline(wm) -> str:
    alert = wm.get("alert")
    cat = wm.get("hw_category", "none").replace("_", " ")
    txt = f"{alert} ALERT ({ALERT_MEANING[alert]})"
    if cat != "none":
        txt += f" - IMD category: {cat}"
    if wm.get("status") == "watch":
        txt += " [WATCH: not yet declared, needs 2nd consecutive day]"
    return txt


NOT_GREEN = ["YELLOW", "ORANGE", "RED"]
HIGH = ["ORANGE", "RED"]
HEAT = ["heatwave", "severe_heatwave"]

# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

RULES: list[Rule] = [
    # ---------------- T: heat-related illness triage (life safety) ---------
    Rule("T1", "Heat stroke from neurological signs",
         [C("symptoms", "contains_any", ["confusion", "unconscious", "seizure"])],
         {"hri": "heat_stroke"}, salience=111, group="Triage", source="S5",
         because="Altered mental state in heat is the hallmark of heat stroke."),
    Rule("T2", "Heat stroke from hot dry skin",
         [C("symptoms", "contains", "high_body_temp"),
          C("symptoms", "contains", "no_sweating"),
          C("hri", "unknown")],
         {"hri": "heat_stroke"}, salience=110, group="Triage", source="S5",
         because="Body temp >40 C with hot, dry skin indicates classic heat stroke."),
    Rule("T3", "Heat exhaustion",
         [C("hri", "unknown"),
          C("symptoms", "contains_any",
            ["heavy_sweating", "dizziness", "nausea", "weakness", "headache", "fainting"])],
         {"hri": "heat_exhaustion"}, salience=109, group="Triage", source="S5",
         because="Heavy sweating, dizziness, nausea or weakness without confusion."),
    Rule("T4", "Heat cramps",
         [C("hri", "unknown"), C("symptoms", "contains", "muscle_cramps")],
         {"hri": "heat_cramps"}, salience=108, group="Triage", source="S5",
         because="Painful muscle spasms after exertion in heat."),
    Rule("T5", "Heat stroke emergency advice",
         [C("hri", "==", "heat_stroke")],
         {"emergency": True},
         advice=[("EMERGENCY", "Suspected HEAT STROKE - call 108 / 112 ambulance NOW."),
                 ("EMERGENCY", "Move person to shade, remove excess clothing, cool with "
                               "wet cloth/cold water and fanning; ice packs on neck, armpits, groin."),
                 ("EMERGENCY", "Do NOT give fluids by mouth if the person is unconscious or confused.")],
         salience=107, group="Triage", source="S5",
         because="Heat stroke is a medical emergency; minutes matter."),
    Rule("T6", "Heat exhaustion first aid",
         [C("hri", "==", "heat_exhaustion")], {},
         advice=[("FIRST AID", "Possible heat exhaustion - move to a cool place, lie down, "
                               "loosen clothing, sip water/ORS."),
                 ("FIRST AID", "Seek medical care if symptoms worsen or do not improve within 1 hour.")],
         salience=107, group="Triage", source="S5",
         because="Heat exhaustion can progress to heat stroke if untreated."),
    Rule("T7", "Heat cramps first aid",
         [C("hri", "==", "heat_cramps")], {},
         advice=[("FIRST AID", "Heat cramps - stop activity, rest in shade, drink ORS / "
                               "electrolyte fluids; avoid strenuous work for a few hours.")],
         salience=107, group="Triage", source="S5",
         because="Cramps signal salt and water loss."),

    # ---------------- V: input validation ----------------------------------
    Rule("V1", "Implausible maximum temperature",
         [C("tmax", "outside", (-10, 55))], {"error": "Tmax outside plausible range -10..55 C"},
         salience=100, halt=True, group="Validation", source="S1",
         because="Highest Tmax ever recorded in India is ~51 C; value is likely a sensor/entry error."),
    Rule("V2", "Implausible normal temperature",
         [C("tmax_normal", "outside", (5, 50))],
         {"error": "Normal Tmax outside plausible range 5..50 C"},
         salience=100, halt=True, group="Validation", source="S1",
         because="Climatological normal Tmax in India lies well inside 5..50 C."),
    Rule("V3", "Invalid humidity",
         [C("rh", "outside", (0, 100))], {"error": "Relative humidity must be 0..100 %"},
         salience=100, halt=True, group="Validation", source="S6",
         because="Relative humidity is a percentage."),
    Rule("V4", "Invalid persistence",
         [C("heat_days", "outside", (1, 60))],
         {"error": "Consecutive hot days must be between 1 and 60"},
         salience=100, halt=True, group="Validation", source="S2",
         because="Persistence is counted in whole days including today."),
    Rule("D0", "Check Tmin against Tmax",
         [C("tmin", "known"), C("tmax", "known")],
         {"tmin_gt_tmax": lambda wm: wm.get("tmin") > wm.get("tmax")},
         salience=99, group="Validation", source="S3",
         because="Night minimum must not exceed day maximum."),
    Rule("V5", "Tmin greater than Tmax",
         [C("tmin_gt_tmax", "==", True)],
         {"error": "Minimum temperature is higher than maximum temperature"},
         salience=98, halt=True, group="Validation", source="S3",
         because="Physically inconsistent observation."),

    # ---------------- D: derived quantities ---------------------------------
    Rule("D1", "Compute Tmax departure from normal",
         [C("tmax", "known"), C("tmax_normal", "known")],
         {"departure": lambda wm: round(wm.get("tmax") - wm.get("tmax_normal"), 1)},
         salience=90, group="Derivation", source="S1",
         because="IMD criteria are expressed as departure from the climatological normal."),
    Rule("D2", "Compute Tmin departure from normal",
         [C("tmin", "known"), C("tmin_normal", "known")],
         {"tmin_departure": lambda wm: round(wm.get("tmin") - wm.get("tmin_normal"), 1)},
         salience=90, group="Derivation", source="S3",
         because="Warm-night criteria use Tmin departure."),
    Rule("D3", "Compute heat index",
         [C("tmax", "known"), C("rh", "known")],
         {"heat_index": lambda wm: heat_index_c(wm.get("tmax"), wm.get("rh"))},
         salience=90, group="Derivation", source="S6",
         because="Humidity reduces sweat cooling; heat index = 'feels-like' temperature."),

    # ---------------- C: IMD heat wave classification -----------------------
    Rule("C1", "Plains threshold reached",
         [C("region", "==", "plains"), C("tmax", ">=", 40)], {"threshold_met": True},
         salience=80, group="Classification", source="S1",
         because="Heat wave is considered only if Tmax >= 40 C in plains."),
    Rule("C2", "Coastal threshold reached",
         [C("region", "==", "coastal"), C("tmax", ">=", 37)], {"threshold_met": True},
         salience=80, group="Classification", source="S1",
         because="Heat wave is considered only if Tmax >= 37 C at coastal stations."),
    Rule("C3", "Hilly threshold reached",
         [C("region", "==", "hilly"), C("tmax", ">=", 30)], {"threshold_met": True},
         salience=80, group="Classification", source="S1",
         because="Heat wave is considered only if Tmax >= 30 C in hilly regions."),
    Rule("C4", "Severe heat wave by absolute temperature",
         [C("threshold_met", "==", True), C("tmax", ">=", 47), C("hw_category", "unknown")],
         {"hw_category": "severe_heatwave"}, salience=78, group="Classification", source="S1",
         because="Actual Tmax >= 47 C is a severe heat wave irrespective of normal."),
    Rule("C5", "Severe heat wave by departure",
         [C("threshold_met", "==", True), C("departure", ">", 6.4), C("hw_category", "unknown")],
         {"hw_category": "severe_heatwave"}, salience=78, group="Classification", source="S1",
         because="Departure from normal > 6.4 C is a severe heat wave."),
    Rule("C6", "Heat wave by absolute temperature",
         [C("threshold_met", "==", True), C("tmax", ">=", 45), C("hw_category", "unknown")],
         {"hw_category": "heatwave"}, salience=76, group="Classification", source="S1",
         because="Actual Tmax >= 45 C is a heat wave irrespective of normal."),
    Rule("C7", "Heat wave by departure",
         [C("threshold_met", "==", True), C("departure", "between", (4.5, 6.4)),
          C("hw_category", "unknown")],
         {"hw_category": "heatwave"}, salience=76, group="Classification", source="S1",
         because="Departure from normal of 4.5 to 6.4 C is a heat wave."),
    Rule("C8", "No heat wave (default)",
         [C("tmax", "known"), C("hw_category", "unknown")],
         {"hw_category": "none"}, salience=70, group="Classification", source="S1",
         because="No IMD heat wave criterion is satisfied."),

    # ---------------- W: warm night ------------------------------------------
    Rule("W1", "Warm night",
         [C("tmax", ">=", 40), C("tmin_departure", "between", (4.5, 6.4))],
         {"night": "warm_night"}, salience=80, group="Warm night", source="S3",
         because="Hot nights stop the body recovering from daytime heat."),
    Rule("W2", "Very warm night",
         [C("tmax", ">=", 40), C("tmin_departure", ">", 6.4)],
         {"night": "very_warm_night"}, salience=80, group="Warm night", source="S3",
         because="Tmin departure > 6.4 C is a very warm night."),

    # ---------------- H: heat-stress band from heat index --------------------
    Rule("H1", "Heat index: caution",
         [C("heat_index", "range", (27, 32))], {"hi_level": "caution"},
         salience=80, group="Heat stress", source="S6",
         because="Fatigue possible with prolonged exposure."),
    Rule("H2", "Heat index: extreme caution",
         [C("heat_index", "range", (32, 39))], {"hi_level": "extreme_caution"},
         salience=80, group="Heat stress", source="S6",
         because="Heat cramps / exhaustion possible."),
    Rule("H3", "Heat index: danger",
         [C("heat_index", "range", (39, 51))], {"hi_level": "danger"},
         salience=80, group="Heat stress", source="S6",
         because="Heat cramps / exhaustion likely, heat stroke possible."),
    Rule("H4", "Heat index: extreme danger",
         [C("heat_index", ">=", 51)], {"hi_level": "extreme_danger"},
         salience=80, group="Heat stress", source="S6",
         because="Heat stroke highly likely."),

    # ---------------- A: IMD colour-coded alert ------------------------------
    Rule("A1", "Green - no heat wave",
         [C("hw_category", "==", "none"), C("alert", "unknown")], {"alert": "GREEN"},
         salience=60, group="Alert", source="S2",
         because="Normal day: no heat wave criterion met."),
    Rule("A2", "Heat wave on day 1 = watch",
         [C("hw_category", "in", HEAT), C("heat_days", "==", 1), C("alert", "unknown")],
         {"alert": "YELLOW", "status": "watch"}, salience=62, group="Alert", source="S1",
         because="IMD declares a heat wave only after criteria hold on 2 consecutive days; "
                 "day 1 is issued as a watch."),
    Rule("A3", "Heat wave persisting 2-3 days",
         [C("hw_category", "==", "heatwave"), C("heat_days", "between", (2, 3)),
          C("alert", "unknown")],
         {"alert": "YELLOW", "status": "declared"}, salience=60, group="Alert", source="S2",
         because="Heat wave persisting 2 days -> Yellow (be updated)."),
    Rule("A4", "Heat wave persisting 4-6 days",
         [C("hw_category", "==", "heatwave"), C("heat_days", "between", (4, 6)),
          C("alert", "unknown")],
         {"alert": "ORANGE", "status": "declared"}, salience=60, group="Alert", source="S2",
         because="Heat wave persisting 4 days or more -> Orange (be prepared)."),
    Rule("A5", "Heat wave persisting > 6 days",
         [C("hw_category", "==", "heatwave"), C("heat_days", ">", 6), C("alert", "unknown")],
         {"alert": "RED", "status": "declared"}, salience=60, group="Alert", source="S2",
         because="Total heat wave days exceeding 6 -> Red (take action)."),
    Rule("A6", "Severe heat wave for 2 days",
         [C("hw_category", "==", "severe_heatwave"), C("heat_days", "==", 2),
          C("alert", "unknown")],
         {"alert": "ORANGE", "status": "declared"}, salience=60, group="Alert", source="S2",
         because="Severe heat wave persisting 2 days -> Orange (be prepared)."),
    Rule("A7", "Severe heat wave for > 2 days",
         [C("hw_category", "==", "severe_heatwave"), C("heat_days", ">", 2),
          C("alert", "unknown")],
         {"alert": "RED", "status": "declared"}, salience=60, group="Alert", source="S2",
         because="Severe heat wave persisting more than 2 days -> Red (take action)."),
    Rule("A8", "Alert when duration not given",
         [C("hw_category", "in", HEAT), C("heat_days", "unknown"), C("alert", "unknown")],
         {"alert": "YELLOW", "status": "watch"}, salience=55, group="Alert", source="S2",
         because="Persistence unknown -> conservatively treat as day 1 (watch)."),

    # ---------------- E: escalation -----------------------------------------
    Rule("E1", "Warm night escalates Yellow to Orange",
         [C("night", "in", ["warm_night", "very_warm_night"]), C("alert", "==", "YELLOW")],
         {"alert": "ORANGE", "escalated": "warm night"}, salience=50,
         group="Escalation", source="S3",
         because="No night-time relief raises heat-illness risk, esp. for elderly."),
    Rule("E2", "Humid heat on a non-heatwave day",
         [C("alert", "==", "GREEN"), C("hi_level", "in", ["danger", "extreme_danger"])],
         {"alert": "YELLOW", "escalated": "humid heat stress"}, salience=50,
         group="Escalation", source="S6",
         because="High humidity (e.g. Mumbai coast) can be dangerous even below IMD thresholds."),
    Rule("E3", "Extreme heat index escalates Yellow",
         [C("alert", "==", "YELLOW"), C("hi_level", "==", "extreme_danger"),
          C("rh", ">=", 40), C("escalated", "unknown")],
         {"alert": "ORANGE", "escalated": "extreme humid heat"}, salience=49,
         group="Escalation", source="S6",
         because="Humid heat index >= 51 C means heat stroke is highly likely (the "
                 "Rothfusz fit is unreliable for very dry air, so RH >= 40 % is required)."),

    # ---------------- G: governance & data gaps ------------------------------
    Rule("G1", "Red alert needs human validation",
         [C("alert", "==", "RED")], {"needs_review": True},
         advice=[("GOVERNANCE", "RED alert: must be reviewed and approved by the duty "
                                "meteorologist / SDMA officer before public dissemination.")],
         salience=40, group="Governance", source="S9",
         because="Human-in-the-loop for critical warnings (use-case governance table)."),
    Rule("G2", "Humidity missing",
         [C("rh", "unknown"), C("tmax", "known")], {},
         advice=[("NOTE", "Humidity not provided - heat-index (humid heat) check skipped; "
                          "advice is based on temperature only.")],
         salience=40, group="Governance", source="S6",
         because="Graceful handling of missing input."),
    Rule("G3", "Night temperature missing",
         [C("tmin", "unknown"), C("tmax", ">=", 40)], {},
         advice=[("NOTE", "Night (minimum) temperature not provided - warm-night "
                          "check skipped.")],
         salience=40, group="Governance", source="S3",
         because="Graceful handling of missing input."),

    # ---------------- P: citizen advisories ----------------------------------
    Rule("P1", "Citizen - normal day",
         [C("role", "==", "citizen"), C("alert", "==", "GREEN")], {},
         advice=[("CITIZEN", "No heat wave. Stay hydrated and follow IMD / local "
                             "bulletins (Mausam app, radio, TV).")],
         salience=20, group="Citizen", source="S4", because="Routine awareness."),
    Rule("P2", "Citizen - basic heat precautions",
         [C("role", "==", "citizen"), C("alert", "in", NOT_GREEN)], {},
         advice=[("CITIZEN", "Avoid going out in the sun, especially 12:00-15:00."),
                 ("CITIZEN", "Drink water often even if not thirsty; use ORS, lassi, "
                             "buttermilk, lemon water, aam panna."),
                 ("CITIZEN", "Wear light, loose, light-coloured cotton clothes; cover head "
                             "with cap/umbrella/cloth.")],
         salience=20, group="Citizen", source="S4", because="NDMA Do's for heat wave."),
    Rule("P3", "Citizen - severe alert precautions",
         [C("role", "==", "citizen"), C("alert", "in", HIGH)], {},
         advice=[("CITIZEN", "Avoid strenuous activity outdoors; stay in the coolest room, "
                             "keep curtains/shades closed by day, open windows at night."),
                 ("CITIZEN", "Never leave children or pets in parked vehicles."),
                 ("CITIZEN", "Avoid alcohol, tea, coffee, carbonated drinks and heavy "
                             "high-protein meals.")],
         salience=20, group="Citizen", source="S4", because="NDMA Don'ts for severe heat."),
    Rule("P4", "Citizen - vulnerable person at home",
         [C("role", "==", "citizen"), C("alert", "in", NOT_GREEN),
          C("vulnerable", "contains_any",
            ["elderly", "infant_child", "pregnant", "chronic_illness"])], {},
         advice=[("VULNERABLE", "Check on elderly, infants, pregnant women and people with "
                                "heart/kidney disease or diabetes at least twice a day."),
                 ("VULNERABLE", "Keep medicines below 25 C; consult doctor about diuretics / "
                                "fluid limits before increasing water intake.")],
         salience=20, group="Citizen", source="S5",
         because="These groups have the highest heat-illness mortality."),
    Rule("P5", "Citizen - outdoor worker",
         [C("role", "==", "citizen"), C("alert", "in", NOT_GREEN),
          C("vulnerable", "contains", "outdoor_worker")], {},
         advice=[("WORKER", "Shift heavy outdoor work to early morning / evening; rest in "
                            "shade frequently and drink a cup of cool water every 15-20 min."),
                 ("WORKER", "Newly returned or new workers: build up exposure gradually "
                            "over a week (acclimatisation).")],
         salience=20, group="Citizen", source="S4",
         because="Outdoor labourers face the highest exposure."),

    # ---------------- F: farmer advisories -----------------------------------
    Rule("F1", "Farmer - normal day",
         [C("role", "==", "farmer"), C("alert", "==", "GREEN")], {},
         advice=[("FARMER", "No heat wave. Continue routine operations; follow the "
                            "district agromet advisory (Meghdoot app).")],
         salience=20, group="Farmer", source="S7", because="Routine awareness."),
    Rule("F2", "Farmer - crop protection",
         [C("role", "==", "farmer"), C("alert", "in", NOT_GREEN),
          C("farm", "in", ["crops", "both"])], {},
         advice=[("FARMER", "Give light and frequent irrigation in the early morning or "
                            "evening; avoid irrigating at mid-day."),
                 ("FARMER", "Apply mulch (crop residue/straw) to conserve soil moisture."),
                 ("FARMER", "Postpone pesticide/fertiliser spraying and transplanting to "
                            "cooler hours; harvest mature crops early.")],
         salience=20, group="Farmer", source="S7", because="Agromet heat wave advisory."),
    Rule("F3", "Farmer - livestock protection",
         [C("role", "==", "farmer"), C("alert", "in", NOT_GREEN),
          C("farm", "in", ["livestock", "both"])], {},
         advice=[("FARMER", "Keep animals in shade with clean, cool drinking water at all "
                            "times; do not let them graze between 11:00 and 16:00."),
                 ("FARMER", "Sprinkle water / use fans in sheds; do not transport animals "
                            "during the day; add mineral mixture and salt to feed.")],
         salience=20, group="Farmer", source="S7", because="Livestock heat stress advisory."),

    # ---------------- M: health department advisories ------------------------
    Rule("M1", "Health dept - alert preparedness",
         [C("role", "==", "health"), C("alert", "==", "YELLOW")], {},
         advice=[("HEALTH", "Stock ORS, IV fluids, ice packs and cooling equipment at "
                            "PHCs/hospitals; brief staff on HRI case definitions."),
                 ("HEALTH", "Start daily reporting of heat-related illness cases and deaths "
                            "(NPCCHH / IHIP surveillance).")],
         salience=20, group="Health", source="S5", because="Hospital preparedness."),
    Rule("M2", "Health dept - severe alert response",
         [C("role", "==", "health"), C("alert", "in", HIGH)], {},
         advice=[("HEALTH", "Activate dedicated heat-stroke rooms / cooling units; "
                            "ensure ambulances (108) carry ice packs and cold fluids."),
                 ("HEALTH", "Extend OPD hours, ensure uninterrupted power and water in "
                            "health facilities; continue daily HRI reporting.")],
         salience=20, group="Health", source="S5", because="Hospital response plan."),
    Rule("M3", "Health dept - normal day",
         [C("role", "==", "health"), C("alert", "==", "GREEN")], {},
         advice=[("HEALTH", "Routine season surveillance; review heat-health action plan "
                            "and stock levels.")],
         salience=20, group="Health", source="S5", because="Routine preparedness."),

    # ---------------- X: local authority advisories --------------------------
    Rule("X1", "Authority - heat alert actions",
         [C("role", "==", "authority"), C("alert", "==", "YELLOW")], {},
         advice=[("AUTHORITY", "Disseminate the warning via SMS, radio, social media and "
                               "local announcements."),
                 ("AUTHORITY", "Open drinking-water points (piyau) at bus stops, markets "
                               "and construction sites.")],
         salience=20, group="Authority", source="S8", because="Heat Action Plan trigger."),
    Rule("X2", "Authority - severe alert actions",
         [C("role", "==", "authority"), C("alert", "in", HIGH)], {},
         advice=[("AUTHORITY", "Activate the Heat Action Plan; open cooling centres / "
                               "shelters in public buildings."),
                 ("AUTHORITY", "Reschedule school hours and outdoor labour (MGNREGA, "
                               "construction) away from 12:00-16:00; keep parks open."),
                 ("AUTHORITY", "Ensure uninterrupted water and power supply; keep fire "
                               "services on alert.")],
         salience=20, group="Authority", source="S4", because="NDMA stakeholder role."),
    Rule("X3", "Authority - normal day",
         [C("role", "==", "authority"), C("alert", "==", "GREEN")], {},
         advice=[("AUTHORITY", "No heat wave. Continue monitoring IMD bulletins and AWS "
                               "readings; review HAP readiness.")],
         salience=20, group="Authority", source="S8", because="Routine monitoring."),

    # ---------------- K: final recommendation --------------------------------
    Rule("K1", "Compose final recommendation",
         [C("alert", "known")], {"recommendation": _headline},
         salience=0, group="Summary", source="S2",
         because="Summarise the conclusion for the user."),
]

"""Test scenarios (D4). Shared by the pytest suite and the test-report generator.

Each scenario: inputs, the expected alert / category, and rules that MUST fire.
Readings are realistic for Maharashtra / India (normals are approximate
April-May climatology).
"""

SCENARIOS = [
    {
        "id": "TC01", "title": "Normal summer day, Pune (plains) - no heat wave",
        "inputs": {"role": "citizen", "region": "plains", "tmax": 34.0,
                   "tmax_normal": 33.0, "heat_days": 1, "rh": 30, "vulnerable": [],
                   "symptoms": []},
        "expect": {"alert": "GREEN", "hw_category": "none"},
        "must_fire": ["D1", "C8", "A1", "P1"], "must_not_fire": ["C1", "E2"],
    },
    {
        "id": "TC02", "title": "Humid heat, Mumbai (coastal) - below IMD threshold",
        "inputs": {"role": "citizen", "region": "coastal", "tmax": 35.0,
                   "tmax_normal": 33.0, "heat_days": 2, "rh": 60,
                   "vulnerable": ["elderly"], "symptoms": []},
        "expect": {"alert": "YELLOW", "hw_category": "none", "hi_level": "danger",
                   "escalated": "humid heat stress"},
        "must_fire": ["D3", "H3", "C8", "A1", "E2", "P2", "P4"], "must_not_fire": ["C2"],
    },
    {
        "id": "TC03", "title": "Severe heat wave for 4 days, Vidarbha (farmer)",
        "inputs": {"role": "farmer", "region": "plains", "tmax": 47.2,
                   "tmax_normal": 42.0, "heat_days": 4, "rh": 18, "farm": "both"},
        "expect": {"alert": "RED", "hw_category": "severe_heatwave", "needs_review": True},
        "must_fire": ["C1", "C4", "A7", "G1", "F2", "F3", "G3"], "must_not_fire": ["C5", "C6"],
    },
    {
        "id": "TC04", "title": "Heat wave criteria met on day 1 only (municipal authority)",
        "inputs": {"role": "authority", "region": "plains", "tmax": 44.0,
                   "tmax_normal": 39.0, "heat_days": 1, "rh": 20},
        "expect": {"alert": "YELLOW", "hw_category": "heatwave", "status": "watch"},
        "must_fire": ["C1", "C7", "A2", "X1"], "must_not_fire": ["A3"],
    },
    {
        "id": "TC05", "title": "Hill station (Mahabaleshwar) severe departure, 2 days (health dept)",
        "inputs": {"role": "health", "region": "hilly", "tmax": 31.5,
                   "tmax_normal": 24.5, "heat_days": 2, "rh": 40, "symptoms": []},
        "expect": {"alert": "ORANGE", "hw_category": "severe_heatwave"},
        "must_fire": ["C3", "C5", "A6", "M2"], "must_not_fire": ["C4"],
    },
    {
        "id": "TC06", "title": "Heat stroke symptoms during heat wave (emergency)",
        "inputs": {"role": "citizen", "region": "plains", "tmax": 45.0,
                   "tmax_normal": 40.0, "heat_days": 2, "rh": 22,
                   "vulnerable": ["elderly"],
                   "symptoms": ["high_body_temp", "confusion", "no_sweating"]},
        "expect": {"alert": "YELLOW", "hri": "heat_stroke", "emergency": True},
        "must_fire": ["T1", "T5", "A3"], "must_not_fire": ["T2", "T3"],
        "first_rule": "T1",
    },
    {
        "id": "TC07", "title": "Invalid sensor reading (Tmax = 62 C) - graceful halt",
        "inputs": {"role": "citizen", "region": "plains", "tmax": 62.0,
                   "tmax_normal": 40.0, "heat_days": 2},
        "expect": {"error": "Tmax outside plausible range -10..55 C"},
        "must_fire": ["V1"], "must_not_fire": ["D1", "A1"], "halted_by": "V1",
    },
    {
        "id": "TC08", "title": "Missing optional data (no normal, no duration, no humidity)",
        "inputs": {"role": "citizen", "region": "plains", "tmax": 46.0},
        "expect": {"alert": "YELLOW", "hw_category": "heatwave", "status": "watch"},
        "must_fire": ["C6", "A8", "G2", "G3"], "must_not_fire": ["D1", "D3"],
    },
    {
        "id": "TC09", "title": "Warm night escalates Yellow to Orange (vulnerable household)",
        "inputs": {"role": "citizen", "region": "plains", "tmax": 45.6,
                   "tmax_normal": 39.8, "heat_days": 3, "rh": 25, "tmin": 31.0,
                   "tmin_normal": 26.0, "vulnerable": ["elderly", "outdoor_worker"],
                   "symptoms": []},
        "expect": {"alert": "ORANGE", "night": "warm_night", "escalated": "warm night"},
        "must_fire": ["W1", "A3", "E1", "P3", "P4", "P5"], "must_not_fire": ["E3"],
    },
    {
        "id": "TC10", "title": "Inconsistent data: Tmin higher than Tmax",
        "inputs": {"role": "citizen", "region": "plains", "tmax": 41.0,
                   "tmax_normal": 38.0, "tmin": 43.0, "tmin_normal": 27.0},
        "expect": {"error": "Minimum temperature is higher than maximum temperature"},
        "must_fire": ["D0", "V5"], "halted_by": "V5",
    },
    {
        "id": "TC11", "title": "Boundary: Tmax exactly 40.0 C, departure exactly 4.5 C",
        "inputs": {"role": "authority", "region": "plains", "tmax": 40.0,
                   "tmax_normal": 35.5, "heat_days": 2, "rh": 15},
        "expect": {"alert": "YELLOW", "hw_category": "heatwave"},
        "must_fire": ["C1", "C7", "A3", "X1"],
    },
    {
        "id": "TC12", "title": "Boundary: 39.9 C in plains with +5 C departure - threshold not met",
        "inputs": {"role": "authority", "region": "plains", "tmax": 39.9,
                   "tmax_normal": 34.9, "heat_days": 3, "rh": 15},
        "expect": {"alert": "GREEN", "hw_category": "none"},
        "must_fire": ["C8", "A1", "X3"], "must_not_fire": ["C1", "C7"],
    },
    {
        "id": "TC13", "title": "Prolonged heat wave (7 days) - Red with human review",
        "inputs": {"role": "health", "region": "plains", "tmax": 45.5,
                   "tmax_normal": 41.5, "heat_days": 7, "rh": 20, "symptoms": ["muscle_cramps"]},
        "expect": {"alert": "RED", "hw_category": "heatwave", "hri": "heat_cramps",
                   "needs_review": True},
        "must_fire": ["C6", "A5", "G1", "M2", "T4", "T7"], "must_not_fire": ["C7"],
    },
    {
        "id": "TC14", "title": "Coastal heat wave with very warm night (Ratnagiri)",
        "inputs": {"role": "citizen", "region": "coastal", "tmax": 40.0,
                   "tmax_normal": 34.0, "heat_days": 2, "rh": 55, "tmin": 32.0,
                   "tmin_normal": 25.0, "vulnerable": ["infant_child"], "symptoms": []},
        "expect": {"alert": "ORANGE", "hw_category": "heatwave", "night": "very_warm_night"},
        "must_fire": ["C2", "C7", "W2", "A3", "E1", "P4"],
    },
]

SCENARIOS.append({
    "id": "TC15", "title": "Heat wave day 2 with extreme humid heat index (Konkan coast)",
    "inputs": {"role": "authority", "region": "coastal", "tmax": 38.5,
               "tmax_normal": 33.5, "heat_days": 2, "rh": 65},
    "expect": {"alert": "ORANGE", "hw_category": "heatwave", "hi_level": "extreme_danger",
               "escalated": "extreme humid heat"},
    "must_fire": ["C2", "C7", "H4", "A3", "E3", "X2"],
})

# --- added for 100 % rule coverage (every rule fires in at least one scenario) ---
SCENARIOS += [
    {
        "id": "TC16", "title": "Classic heat stroke (hot, dry skin) reported to health dept",
        "inputs": {"role": "health", "region": "plains", "tmax": 44.0, "tmax_normal": 39.0,
                   "heat_days": 2, "rh": 20, "symptoms": ["high_body_temp", "no_sweating"]},
        "expect": {"alert": "YELLOW", "hri": "heat_stroke", "emergency": True},
        "must_fire": ["T2", "T5", "C7", "A3", "M1"], "must_not_fire": ["T1", "T3"],
    },
    {
        "id": "TC17", "title": "Heat exhaustion on a normal day (exertional)",
        "inputs": {"role": "citizen", "region": "plains", "tmax": 34.0, "tmax_normal": 33.0,
                   "heat_days": 1, "rh": 30, "vulnerable": [],
                   "symptoms": ["heavy_sweating", "dizziness"]},
        "expect": {"alert": "GREEN", "hri": "heat_exhaustion"},
        "must_fire": ["T3", "T6", "A1", "P1"], "must_not_fire": ["T5"],
    },
    {
        "id": "TC18", "title": "Farmer on a normal day - routine advice only",
        "inputs": {"role": "farmer", "region": "plains", "tmax": 36.0, "tmax_normal": 35.0,
                   "heat_days": 1, "rh": 35, "farm": "crops"},
        "expect": {"alert": "GREEN", "hw_category": "none"},
        "must_fire": ["F1"], "must_not_fire": ["F2", "F3"],
    },
    {
        "id": "TC19", "title": "Health department on a normal day",
        "inputs": {"role": "health", "region": "coastal", "tmax": 33.0, "tmax_normal": 32.0,
                   "heat_days": 1, "rh": 40, "symptoms": []},
        "expect": {"alert": "GREEN"},
        "must_fire": ["M3"], "must_not_fire": ["M1", "M2"],
    },
    {
        "id": "TC20", "title": "Invalid humidity (140 %) - graceful halt",
        "inputs": {"role": "citizen", "region": "coastal", "tmax": 36.0, "rh": 140},
        "expect": {"error": "Relative humidity must be 0..100 %"},
        "must_fire": ["V3"], "halted_by": "V3",
    },
    {
        "id": "TC21", "title": "Implausible normal temperature (70 C) - graceful halt",
        "inputs": {"role": "citizen", "region": "plains", "tmax": 44.0, "tmax_normal": 70.0},
        "expect": {"error": "Normal Tmax outside plausible range 5..50 C"},
        "must_fire": ["V2"], "must_not_fire": ["D1"], "halted_by": "V2",
    },
    {
        "id": "TC22", "title": "Invalid persistence (0 days) - graceful halt",
        "inputs": {"role": "authority", "region": "plains", "tmax": 44.0, "heat_days": 0},
        "expect": {"error": "Consecutive hot days must be between 1 and 60"},
        "must_fire": ["V4"], "halted_by": "V4",
    },
    {
        "id": "TC23", "title": "Heat wave persisting 5 days - Orange for authority",
        "inputs": {"role": "authority", "region": "plains", "tmax": 45.5, "tmax_normal": 41.5,
                   "heat_days": 5, "rh": 15},
        "expect": {"alert": "ORANGE", "hw_category": "heatwave"},
        "must_fire": ["C6", "A4", "X2"], "must_not_fire": ["A5", "G1"],
    },
]

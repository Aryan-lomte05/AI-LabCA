# D4 - Test Case Report (auto-generated)

pytest: **35 passed in 0.09s**

| TC | Scenario | Alert / outcome | Rules fired | Result |
|---|---|---|---|---|
| TC01 | Normal summer day, Pune (plains) - no heat wave | GREEN / none | 7 | PASS |
| TC02 | Humid heat, Mumbai (coastal) - below IMD threshold | YELLOW / none | 9 | PASS |
| TC03 | Severe heat wave for 4 days, Vidarbha (farmer) | RED / severe_heatwave | 11 | PASS |
| TC04 | Heat wave criteria met on day 1 only (municipal authority) | YELLOW / heatwave | 9 | PASS |
| TC05 | Hill station (Mahabaleshwar) severe departure, 2 days (health dept) | ORANGE / severe_heatwave | 8 | PASS |
| TC06 | Heat stroke symptoms during heat wave (emergency) | YELLOW / heatwave + EMERGENCY | 12 | PASS |
| TC07 | Invalid sensor reading (Tmax = 62 C) - graceful halt | ERROR (halt V1) | 1 | PASS |
| TC08 | Missing optional data (no normal, no duration, no humidity) | YELLOW / heatwave | 7 | PASS |
| TC09 | Warm night escalates Yellow to Orange (vulnerable household) | ORANGE / heatwave | 15 | PASS |
| TC10 | Inconsistent data: Tmin higher than Tmax | ERROR (halt V5) | 2 | PASS |
| TC11 | Boundary: Tmax exactly 40.0 C, departure exactly 4.5 C | YELLOW / heatwave | 9 | PASS |
| TC12 | Boundary: 39.9 C in plains with +5 C departure - threshold not met | GREEN / none | 7 | PASS |
| TC13 | Prolonged heat wave (7 days) - Red with human review | RED / heatwave | 12 | PASS |
| TC14 | Coastal heat wave with very warm night (Ratnagiri) | ORANGE / heatwave | 14 | PASS |
| TC15 | Heat wave day 2 with extreme humid heat index (Konkan coast) | ORANGE / heatwave | 9 | PASS |
| TC16 | Classic heat stroke (hot, dry skin) reported to health dept | YELLOW / heatwave + EMERGENCY | 11 | PASS |
| TC17 | Heat exhaustion on a normal day (exertional) | GREEN / none | 9 | PASS |
| TC18 | Farmer on a normal day - routine advice only | GREEN / none | 7 | PASS |
| TC19 | Health department on a normal day | GREEN / none | 7 | PASS |
| TC20 | Invalid humidity (140 %) - graceful halt | ERROR (halt V3) | 1 | PASS |
| TC21 | Implausible normal temperature (70 C) - graceful halt | ERROR (halt V2) | 1 | PASS |
| TC22 | Invalid persistence (0 days) - graceful halt | ERROR (halt V4) | 1 | PASS |
| TC23 | Heat wave persisting 5 days - Orange for authority | ORANGE / heatwave | 9 | PASS |

**TC01: Normal summer day, Pune (plains) - no heat wave**

- *Inputs:* `role=citizen, region=plains, tmax=34.0, tmax_normal=33.0, heat_days=1, rh=30`
- *Expected:* alert = GREEN, hw_category = none
- *Rules fired (in order):* D1 → D3 → H2 → C8 → A1 → P1 → K1
- *Output:* GREEN ALERT (No action - normal day); advice for: CITIZEN
- *Result:* **PASS**

**TC02: Humid heat, Mumbai (coastal) - below IMD threshold**

- *Inputs:* `role=citizen, region=coastal, tmax=35.0, tmax_normal=33.0, heat_days=2, rh=60, vulnerable=elderly`
- *Expected:* alert = YELLOW, hw_category = none, hi_level = danger, escalated = humid heat stress
- *Rules fired (in order):* D1 → D3 → H3 → C8 → A1 → E2 → P4 → P2 → K1
- *Output:* YELLOW ALERT (Heat alert - be updated); advice for: CITIZEN, VULNERABLE
- *Result:* **PASS**

**TC03: Severe heat wave for 4 days, Vidarbha (farmer)**

- *Inputs:* `role=farmer, region=plains, tmax=47.2, tmax_normal=42.0, heat_days=4, rh=18, farm=both`
- *Expected:* alert = RED, hw_category = severe_heatwave, needs_review = True
- *Rules fired (in order):* D1 → D3 → C1 → H3 → C4 → A7 → G3 → G1 → F2 → F3 → K1
- *Output:* RED ALERT (Extreme heat alert - take action) - IMD category: severe heatwave; advice for: FARMER, GOVERNANCE, NOTE
- *Result:* **PASS**

**TC04: Heat wave criteria met on day 1 only (municipal authority)**

- *Inputs:* `role=authority, region=plains, tmax=44.0, tmax_normal=39.0, heat_days=1, rh=20`
- *Expected:* alert = YELLOW, hw_category = heatwave, status = watch
- *Rules fired (in order):* D1 → D3 → C1 → H3 → C7 → A2 → G3 → X1 → K1
- *Output:* YELLOW ALERT (Heat alert - be updated) - IMD category: heatwave [WATCH: not yet declared, needs 2nd consecutive day]; advice for: AUTHORITY, NOTE
- *Result:* **PASS**

**TC05: Hill station (Mahabaleshwar) severe departure, 2 days (health dept)**

- *Inputs:* `role=health, region=hilly, tmax=31.5, tmax_normal=24.5, heat_days=2, rh=40`
- *Expected:* alert = ORANGE, hw_category = severe_heatwave
- *Rules fired (in order):* D1 → D3 → C3 → H1 → C5 → A6 → M2 → K1
- *Output:* ORANGE ALERT (Severe heat alert - be prepared) - IMD category: severe heatwave; advice for: HEALTH
- *Result:* **PASS**

**TC06: Heat stroke symptoms during heat wave (emergency)**

- *Inputs:* `role=citizen, region=plains, tmax=45.0, tmax_normal=40.0, heat_days=2, rh=22, vulnerable=elderly, symptoms=high_body_temp/confusion/no_sweating`
- *Expected:* alert = YELLOW, hri = heat_stroke, emergency = True
- *Rules fired (in order):* T1 → T5 → D1 → D3 → C1 → H3 → C6 → A3 → G3 → P4 → P2 → K1
- *Output:* YELLOW ALERT (Heat alert - be updated) - IMD category: heatwave; advice for: CITIZEN, EMERGENCY, NOTE, VULNERABLE
- *Result:* **PASS**

**TC07: Invalid sensor reading (Tmax = 62 C) - graceful halt**

- *Inputs:* `role=citizen, region=plains, tmax=62.0, tmax_normal=40.0, heat_days=2`
- *Expected:* error = Tmax outside plausible range -10..55 C
- *Rules fired (in order):* V1
- *Output:* INPUT ERROR: Tmax outside plausible range -10..55 C
- *Result:* **PASS**

**TC08: Missing optional data (no normal, no duration, no humidity)**

- *Inputs:* `role=citizen, region=plains, tmax=46.0`
- *Expected:* alert = YELLOW, hw_category = heatwave, status = watch
- *Rules fired (in order):* C1 → C6 → A8 → G2 → G3 → P2 → K1
- *Output:* YELLOW ALERT (Heat alert - be updated) - IMD category: heatwave [WATCH: not yet declared, needs 2nd consecutive day]; advice for: CITIZEN, NOTE
- *Result:* **PASS**

**TC09: Warm night escalates Yellow to Orange (vulnerable household)**

- *Inputs:* `role=citizen, region=plains, tmax=45.6, tmax_normal=39.8, heat_days=3, rh=25, tmin=31.0, tmin_normal=26.0, vulnerable=elderly/outdoor_worker`
- *Expected:* alert = ORANGE, night = warm_night, escalated = warm night
- *Rules fired (in order):* D0 → D1 → D2 → D3 → C1 → W1 → H4 → C6 → A3 → E1 → P4 → P5 → P2 → P3 → K1
- *Output:* ORANGE ALERT (Severe heat alert - be prepared) - IMD category: heatwave; advice for: CITIZEN, VULNERABLE, WORKER
- *Result:* **PASS**

**TC10: Inconsistent data: Tmin higher than Tmax**

- *Inputs:* `role=citizen, region=plains, tmax=41.0, tmax_normal=38.0, tmin=43.0, tmin_normal=27.0`
- *Expected:* error = Minimum temperature is higher than maximum temperature
- *Rules fired (in order):* D0 → V5
- *Output:* INPUT ERROR: Minimum temperature is higher than maximum temperature
- *Result:* **PASS**

**TC11: Boundary: Tmax exactly 40.0 C, departure exactly 4.5 C**

- *Inputs:* `role=authority, region=plains, tmax=40.0, tmax_normal=35.5, heat_days=2, rh=15`
- *Expected:* alert = YELLOW, hw_category = heatwave
- *Rules fired (in order):* D1 → D3 → C1 → H2 → C7 → A3 → G3 → X1 → K1
- *Output:* YELLOW ALERT (Heat alert - be updated) - IMD category: heatwave; advice for: AUTHORITY, NOTE
- *Result:* **PASS**

**TC12: Boundary: 39.9 C in plains with +5 C departure - threshold not met**

- *Inputs:* `role=authority, region=plains, tmax=39.9, tmax_normal=34.9, heat_days=3, rh=15`
- *Expected:* alert = GREEN, hw_category = none
- *Rules fired (in order):* D1 → D3 → H2 → C8 → A1 → X3 → K1
- *Output:* GREEN ALERT (No action - normal day); advice for: AUTHORITY
- *Result:* **PASS**

**TC13: Prolonged heat wave (7 days) - Red with human review**

- *Inputs:* `role=health, region=plains, tmax=45.5, tmax_normal=41.5, heat_days=7, rh=20, symptoms=muscle_cramps`
- *Expected:* alert = RED, hw_category = heatwave, hri = heat_cramps, needs_review = True
- *Rules fired (in order):* T4 → T7 → D1 → D3 → C1 → H3 → C6 → A5 → G3 → G1 → M2 → K1
- *Output:* RED ALERT (Extreme heat alert - take action) - IMD category: heatwave; advice for: FIRST AID, GOVERNANCE, HEALTH, NOTE
- *Result:* **PASS**

**TC14: Coastal heat wave with very warm night (Ratnagiri)**

- *Inputs:* `role=citizen, region=coastal, tmax=40.0, tmax_normal=34.0, heat_days=2, rh=55, tmin=32.0, tmin_normal=25.0, vulnerable=infant_child`
- *Expected:* alert = ORANGE, hw_category = heatwave, night = very_warm_night
- *Rules fired (in order):* D0 → D1 → D2 → D3 → C2 → W2 → H4 → C7 → A3 → E1 → P4 → P2 → P3 → K1
- *Output:* ORANGE ALERT (Severe heat alert - be prepared) - IMD category: heatwave; advice for: CITIZEN, VULNERABLE
- *Result:* **PASS**

**TC15: Heat wave day 2 with extreme humid heat index (Konkan coast)**

- *Inputs:* `role=authority, region=coastal, tmax=38.5, tmax_normal=33.5, heat_days=2, rh=65`
- *Expected:* alert = ORANGE, hw_category = heatwave, hi_level = extreme_danger, escalated = extreme humid heat
- *Rules fired (in order):* D1 → D3 → C2 → H4 → C7 → A3 → E3 → X2 → K1
- *Output:* ORANGE ALERT (Severe heat alert - be prepared) - IMD category: heatwave; advice for: AUTHORITY
- *Result:* **PASS**

**TC16: Classic heat stroke (hot, dry skin) reported to health dept**

- *Inputs:* `role=health, region=plains, tmax=44.0, tmax_normal=39.0, heat_days=2, rh=20, symptoms=high_body_temp/no_sweating`
- *Expected:* alert = YELLOW, hri = heat_stroke, emergency = True
- *Rules fired (in order):* T2 → T5 → D1 → D3 → C1 → H3 → C7 → A3 → G3 → M1 → K1
- *Output:* YELLOW ALERT (Heat alert - be updated) - IMD category: heatwave; advice for: EMERGENCY, HEALTH, NOTE
- *Result:* **PASS**

**TC17: Heat exhaustion on a normal day (exertional)**

- *Inputs:* `role=citizen, region=plains, tmax=34.0, tmax_normal=33.0, heat_days=1, rh=30, symptoms=heavy_sweating/dizziness`
- *Expected:* alert = GREEN, hri = heat_exhaustion
- *Rules fired (in order):* T3 → T6 → D1 → D3 → H2 → C8 → A1 → P1 → K1
- *Output:* GREEN ALERT (No action - normal day); advice for: CITIZEN, FIRST AID
- *Result:* **PASS**

**TC18: Farmer on a normal day - routine advice only**

- *Inputs:* `role=farmer, region=plains, tmax=36.0, tmax_normal=35.0, heat_days=1, rh=35, farm=crops`
- *Expected:* alert = GREEN, hw_category = none
- *Rules fired (in order):* D1 → D3 → H2 → C8 → A1 → F1 → K1
- *Output:* GREEN ALERT (No action - normal day); advice for: FARMER
- *Result:* **PASS**

**TC19: Health department on a normal day**

- *Inputs:* `role=health, region=coastal, tmax=33.0, tmax_normal=32.0, heat_days=1, rh=40`
- *Expected:* alert = GREEN
- *Rules fired (in order):* D1 → D3 → H2 → C8 → A1 → M3 → K1
- *Output:* GREEN ALERT (No action - normal day); advice for: HEALTH
- *Result:* **PASS**

**TC20: Invalid humidity (140 %) - graceful halt**

- *Inputs:* `role=citizen, region=coastal, tmax=36.0, rh=140`
- *Expected:* error = Relative humidity must be 0..100 %
- *Rules fired (in order):* V3
- *Output:* INPUT ERROR: Relative humidity must be 0..100 %
- *Result:* **PASS**

**TC21: Implausible normal temperature (70 C) - graceful halt**

- *Inputs:* `role=citizen, region=plains, tmax=44.0, tmax_normal=70.0`
- *Expected:* error = Normal Tmax outside plausible range 5..50 C
- *Rules fired (in order):* V2
- *Output:* INPUT ERROR: Normal Tmax outside plausible range 5..50 C
- *Result:* **PASS**

**TC22: Invalid persistence (0 days) - graceful halt**

- *Inputs:* `role=authority, region=plains, tmax=44.0, heat_days=0`
- *Expected:* error = Consecutive hot days must be between 1 and 60
- *Rules fired (in order):* V4
- *Output:* INPUT ERROR: Consecutive hot days must be between 1 and 60
- *Result:* **PASS**

**TC23: Heat wave persisting 5 days - Orange for authority**

- *Inputs:* `role=authority, region=plains, tmax=45.5, tmax_normal=41.5, heat_days=5, rh=15`
- *Expected:* alert = ORANGE, hw_category = heatwave
- *Rules fired (in order):* D1 → D3 → C1 → H3 → C6 → A4 → G3 → X2 → K1
- *Output:* ORANGE ALERT (Severe heat alert - be prepared) - IMD category: heatwave; advice for: AUTHORITY, NOTE
- *Result:* **PASS**

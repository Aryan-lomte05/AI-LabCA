/*  HeatGuard (Prolog edition) - Heatwave Early-Warning Advisory Expert System
    =========================================================================
    SVU use case KJS-CES-01: Climate Intelligence for Heatwave Monitoring,
    Prediction and Early Warning (IMD Mumbai-Pune).

    This edition uses BACKWARD CHAINING (goal-driven), Prolog's native
    strategy, through a small META-INTERPRETER so that it can explain itself:

      * starts from the goal  alert(Level)  and works back to the facts;
      * asks the user ONLY for facts that the current line of reasoning needs
        (e.g. it never asks for humidity or the normal temperature if the
        temperature is below the regional threshold);
      * WHY  - typing `why` at a question prints the chain of rules that led
               to the question;
      * HOW  - after the conclusion the full proof tree is printed, showing
               which rules fired and which facts they used.

    Conflict resolution = rule ORDER: candidate rules for the same conclusion
    are listed most-severe / most-specific first and the first proof wins
    (once/1).

    Run (SWI-Prolog):
        swipl prolog/heatguard.pl
        ?- start.                      % interactive consultation
        ?- run_tests_cases.            % 6 non-interactive test cases
*/

:- dynamic known/2.
:- dynamic mode/1.
mode(interactive).

:- discontiguous rule/4.

/* ---------------------------------------------------------------------
   Askable facts: attribute, question, type, why-text
   --------------------------------------------------------------------- */
askable(role,        'Advice for (citizen / farmer / health / authority)?', [citizen, farmer, health, authority]).
askable(region,      'Region type (plains / coastal / hilly)?',             [plains, coastal, hilly]).
askable(tmax,        'Maximum temperature today in C?',                    number(-10, 55)).
askable(tmax_normal, 'Normal (climatological) maximum for today in C?',    number(5, 50)).
askable(heat_days,   'Consecutive days (incl. today) it has been this hot?', number(1, 60)).
askable(rh,          'Relative humidity in %?',                            number(0, 100)).
askable(tmin,        'Night minimum temperature in C?',                    number(-10, 45)).
askable(tmin_normal, 'Normal minimum temperature for today in C?',         number(-10, 40)).
askable(vulnerable,  'Is anyone at home elderly / infant / pregnant / chronically ill (yes / no)?', [yes, no]).
askable(outdoor_worker, 'Does anyone at home work outdoors (yes / no)?',   [yes, no]).
askable(farm,        'Do you manage crops / livestock / both?',            [crops, livestock, both]).
askable(heat_stroke_signs, 'Is anyone confused, unconscious or hot with dry skin (yes / no)?', [yes, no]).

/* ---------------------------------------------------------------------
   KNOWLEDGE BASE   rule(Id, Head, Body, Source)
   Sources: S1 IMD heat-wave criteria, S2 IMD colour codes,
            S3 IMD warm night, S4 NDMA heat action plan guidelines,
            S5 MoHFW NPCCHH heat-related illness, S6 NWS heat index,
            S7 IMD/ICAR agromet advisories, S9 use-case governance
   --------------------------------------------------------------------- */

% --- derived quantities ---
rule(d1, departure(D),       (val(tmax, T), val(tmax_normal, N), D is T - N), s1).
rule(d2, tmin_departure(D),  (val(tmin, T), val(tmin_normal, N), D is T - N), s3).

% --- regional threshold (IMD) ---
rule(c1, threshold_met, (val(region, plains),  val(tmax, T), T >= 40), s1).
rule(c2, threshold_met, (val(region, coastal), val(tmax, T), T >= 37), s1).
rule(c3, threshold_met, (val(region, hilly),   val(tmax, T), T >= 30), s1).

% --- heat-wave category: ordered most severe first (first proof wins) ---
rule(c4, cat_candidate(severe_heatwave), (threshold_met, val(tmax, T), T >= 47), s1).
rule(c5, cat_candidate(severe_heatwave), (threshold_met, departure(D), D > 6.4), s1).
rule(c6, cat_candidate(heatwave),        (threshold_met, val(tmax, T), T >= 45), s1).
rule(c7, cat_candidate(heatwave),        (threshold_met, departure(D), D >= 4.5), s1).
rule(c8, cat_candidate(none),            val(tmax, _), s1).   % needs a reading
% compute the category first, THEN compare: calling cat_candidate with a bound
% value would let the catch-all rule c8 'prove' category(none) on a heat-wave day
rule(c9, category(C),                    (once(cat_candidate(C0)), C = C0), s1).

% --- base colour code from category and persistence (IMD) ---
rule(a1, base_alert(green),  category(none), s2).
rule(a2, base_alert(yellow), (category(C), C \== none, val(heat_days, 1)), s1).   % watch
rule(a3, base_alert(yellow), (category(heatwave), val(heat_days, N), N >= 2, N =< 3), s2).
rule(a4, base_alert(orange), (category(heatwave), val(heat_days, N), N >= 4, N =< 6), s2).
rule(a5, base_alert(red),    (category(heatwave), val(heat_days, N), N > 6), s2).
rule(a6, base_alert(orange), (category(severe_heatwave), val(heat_days, 2)), s2).
rule(a7, base_alert(red),    (category(severe_heatwave), val(heat_days, N), N > 2), s2).

% --- aggravating factors ---
rule(w1, warm_night,  (val(tmax, T), T >= 40, tmin_departure(D), D >= 4.5), s3).
rule(h1, humid_heat,  (val(rh, RH), val(tmax, T), heat_index(T, RH, HI), HI >= 39), s6).

% --- final alert: escalation one level for warm night / humid heat ---
rule(e1, alert(orange), (base_alert(yellow), warm_night), s3).
rule(e2, alert(yellow), (base_alert(green), humid_heat), s6).
rule(e3, alert(L),      base_alert(L), s2).

% --- stakeholder advice: advice(Audience, Text) ---
rule(t1, advice(emergency, 'Suspected HEAT STROKE: call 108 / 112, cool the person with water and fanning, no fluids if unconscious.'),
        (val(role, R), member(R, [citizen, health]), val(heat_stroke_signs, yes)), s5).
rule(g1, advice(governance, 'RED alert must be validated by the duty meteorologist before dissemination.'),
        final_alert(red), s9).
rule(p1, advice(citizen, 'Avoid the sun 12:00-15:00, drink water/ORS often, wear light cotton clothes.'),
        (val(role, citizen), not_green), s4).
rule(p2, advice(citizen, 'Stay indoors in the coolest room, avoid strenuous work, never leave children in parked vehicles.'),
        (val(role, citizen), severe_alert), s4).
rule(p3, advice(vulnerable, 'Check on elderly, infants, pregnant and chronically ill people twice a day.'),
        (val(role, citizen), not_green, val(vulnerable, yes)), s5).
rule(p4, advice(worker, 'Shift outdoor work to early morning/evening; drink cool water every 15-20 min; rest in shade.'),
        (val(role, citizen), not_green, val(outdoor_worker, yes)), s4).
rule(f1, advice(farmer, 'Light, frequent irrigation in morning/evening; mulch; no spraying at mid-day.'),
        (val(role, farmer), not_green, val(farm, F), member(F, [crops, both])), s7).
rule(f2, advice(farmer, 'Keep livestock in shade with cool water; no grazing 11:00-16:00; no daytime transport.'),
        (val(role, farmer), not_green, val(farm, F), member(F, [livestock, both])), s7).
rule(m1, advice(health, 'Stock ORS, IV fluids and ice packs; start daily heat-illness reporting.'),
        (val(role, health), not_green), s5).
rule(m2, advice(health, 'Activate heat-stroke rooms/cooling units; ambulances carry ice packs.'),
        (val(role, health), severe_alert), s5).
rule(x1, advice(authority, 'Disseminate warning via SMS/radio; open drinking-water points.'),
        (val(role, authority), not_green), s4).
rule(x2, advice(authority, 'Activate Heat Action Plan: cooling centres, reschedule school and labour hours.'),
        (val(role, authority), severe_alert), s4).
rule(z1, advice(all, 'Normal day - stay hydrated and follow IMD bulletins.'),
        final_alert(green), s4).

rule(k1, final_alert(L), (once(alert(L0)), L = L0), s2).
rule(k2, not_green,    (final_alert(L), L \== green), s2).
rule(k3, severe_alert, (final_alert(L), member(L, [orange, red])), s2).

/* NWS heat index (Rothfusz regression) in C - a computation, not a rule */
heat_index(Tc, RH, HIc) :-
    T is Tc * 9 / 5 + 32,
    S is 0.5 * (T + 61.0 + (T - 68.0) * 1.2 + RH * 0.094),
    (   (S + T) / 2 < 80
    ->  HI = S
    ;   HI is -42.379 + 2.04901523*T + 10.14333127*RH - 0.22475541*T*RH
              - 0.00683783*T*T - 0.05481717*RH*RH + 0.00122874*T*T*RH
              + 0.00085282*T*RH*RH - 0.00000199*T*T*RH*RH
    ),
    HIc is (HI - 32) * 5 / 9.

/* ---------------------------------------------------------------------
   META-INTERPRETER: prove(Goal, WhyStack, ProofTree)
   --------------------------------------------------------------------- */
prove(true, _, true) :- !.
prove((A, B), S, (PA, PB)) :- !, prove(A, S, PA), prove(B, S, PB).
prove(once(G), S, P) :- !, once(prove(G, S, P)).
prove(val(A, V), S, fact(A = V)) :- !, val(A, V, S).
prove(G, _, builtin(G)) :- builtin(G), !, call(G).
prove(G, S, rule(Id, G, Src, P)) :-
    rule(Id, G, Body, Src),
    prove(Body, [Id-G | S], P).

builtin(G) :- functor(G, F, _),
    memberchk(F, [is, >=, =<, >, <, ==, \==, =, member, heat_index]).

/* val/3: look up a fact, or ask the user exactly once */
val(A, V, _) :- known(A, X), !, X \== unknown, V = X.
val(A, V, S) :-
    mode(interactive), askable(A, Q, Type), !,
    ask(A, Q, Type, S, X),
    assertz(known(A, X)),
    X \== unknown, V = X.
val(A, _, _) :-                          % batch mode: missing fact = unknown
    assertz(known(A, unknown)), fail.

ask(A, Q, Type, S, X) :-
    format("~n? ~w  ('why' / 'unknown')~n> ", [Q]),
    read_line_to_string(user_input, Raw0),
    (   Raw0 == end_of_file -> X = unknown
    ;   string_lower(Raw0, Raw1), normalize_space(atom(Raw), Raw1),
        (   Raw == why
        ->  explain_why(A, S), ask(A, Q, Type, S, X)
        ;   Raw == unknown
        ->  X = unknown
        ;   parse(Type, Raw, X0)
        ->  X = X0
        ;   format("  Invalid answer, expected ~w~n", [Type]), ask(A, Q, Type, S, X)
        )
    ).

parse(number(Lo, Hi), Raw, N) :-
    atom_number(Raw, N),
    (   N >= Lo, N =< Hi -> true
    ;   format("  Out of plausible range ~w..~w~n", [Lo, Hi]), fail ).
parse(Options, Raw, X) :- is_list(Options), member(X, Options), sub_atom(X, 0, _, _, Raw), !.

explain_why(A, Stack) :-
    format("  I need '~w' because I am trying to establish:~n", [A]),
    forall(member(Id-G, Stack),
           ( rule(Id, G, _, Src), format("    ~w  (rule ~w, source ~w)~n", [G, Id, Src]) )).

/* HOW: pretty-print the proof tree */
show_proof(P) :- show_proof(P, 1).
show_proof(true, _) :- !.
show_proof((A, B), I) :- !, show_proof(A, I), show_proof(B, I).
show_proof(builtin(_ = _), _) :- !.          % hide internal unifications
show_proof(fact(F), I) :- !, tab(I * 2), format("~w   (given)~n", [F]).
show_proof(builtin(G), I) :- !, tab(I * 2), format("~w   (test)~n", [G]).
show_proof(rule(Id, G, Src, P), I) :-
    tab(I * 2), format("~w   <- rule ~w [~w]~n", [G, Id, Src]),
    I2 is I + 1, show_proof(P, I2).

/* ---------------------------------------------------------------------
   TOP LEVEL
   --------------------------------------------------------------------- */
start :-
    retractall(known(_, _)), retractall(mode(_)), assertz(mode(interactive)),
    format("~n=== HeatGuard (Prolog) - heatwave advisory expert system ===~n"),
    val(role, _, []),           % ask role first so advice can be targeted
    conclude.

conclude :-
    % life safety first: triage before any weather reasoning
    forall(prove(advice(emergency, E), [], _), format("~n!!! ~w~n", [E])),
    (   prove(final_alert(L), [], Proof)
    ->  % collect all advice first (may ask questions), then print it together
        findall(Aud-Text-Id,
                ( prove(advice(Aud, Text), [], rule(Id, _, _, _)), Aud \== emergency ),
                Advice),
        upcase_atom(L, UL),
        format("~n*** ~w ALERT ***~n", [UL]),
        (   prove(category(C), [], _) -> format("IMD category: ~w~n", [C]) ; true ),
        format("~nADVICE:~n"),
        forall(member(Aud-Text-Id, Advice), format("  [~w] ~w  (~w)~n", [Aud, Text, Id])),
        format("~nHOW (proof tree of the alert):~n"),
        show_proof(Proof)
    ;   format("~nCould not reach a conclusion - temperature is required.~n")
    ).

/* non-interactive run with given facts (unanswered = unknown) */
run_case(Name, Facts) :-
    retractall(known(_, _)), retractall(mode(_)), assertz(mode(batch)),
    forall(member(A = V, Facts), assertz(known(A, V))),
    format("~n------------------------------------------------------------~n"),
    format("~w~n  facts: ~w~n", [Name, Facts]),
    conclude,
    retractall(mode(_)), assertz(mode(interactive)).

run_tests_cases :-
    run_case('TC01 normal day Pune',
             [role=citizen, region=plains, tmax=34, tmax_normal=33, heat_days=1, rh=30]),
    run_case('TC02 humid heat Mumbai (below IMD threshold)',
             [role=citizen, region=coastal, tmax=35, tmax_normal=33, heat_days=2, rh=60,
              vulnerable=yes]),
    run_case('TC03 severe heat wave 4 days Vidarbha farmer',
             [role=farmer, region=plains, tmax=47.2, tmax_normal=42, heat_days=4, farm=both]),
    run_case('TC04 heat wave day 1 (watch) authority',
             [role=authority, region=plains, tmax=44, tmax_normal=39, heat_days=1]),
    run_case('TC09 warm night escalation',
             [role=citizen, region=plains, tmax=45.6, tmax_normal=39.8, heat_days=3,
              tmin=31, tmin_normal=26, vulnerable=yes, outdoor_worker=yes]),
    run_case('TC06 heat stroke emergency',
             [role=citizen, region=plains, tmax=45, tmax_normal=40, heat_days=2,
              heat_stroke_signs=yes]).

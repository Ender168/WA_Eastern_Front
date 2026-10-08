# Operations rework: design and offline prototype

Branch: feature/operations-rework. Based on main 9ffbd161f06999ce1e9ed810383a1b436b316af7.
Status: researched design, exact map inventory and tested accounting model. Existing playable decisions are unchanged. No claim of engine or battle verification.

## Requested rules

| Type | Preparation | Offensive bonus duration | Area | Eligibility |
| --- | --- | --- | --- | --- |
| Tactical offensive | 7 days | 14 days | One state | More than 7 land provinces |
| Strategic operation | 30 days | 60 days | States of one air region | Strictly more than half its land provinces controlled by the opponent |

Two months means a fixed 60 days for the mission timer. The user clarified that the tactical threshold concerns provinces. No national duration exception is applied in this design.

## Exact geography and eligibility

`tools/operations_prototype.py` reads WA's definition.csv and strategicregions and this mod's state history. The generated inventory records every province, region and state, instead of assigning states by a majority guess. Among 282 playable states, 165 have at least 8 land provinces. None cross region borders.

At launch count enemy-controlled land provinces P, and compare 2*P > N. Exactly 50% fails. Weight every land province equally; do not use victory points, state controllers, population or aerial superiority. Count the full air region for the literal user condition. The inventory also records playable-only provinces to expose neutral OBS border cases; do not silently substitute that smaller denominator. Neutral provinces count in N but not P. Sea and lake provinces are excluded. Only WEF/EEF states receive offensive bonuses; OBS must never become an operation target. If a region includes OBS land, victory concerns all playable provinces, not neutral observer territory. This boundary should be visible in the tooltip.

Generate an explicit `controls_province = ID` check in the opposing country scope for each province. In this two-side scenario choose EEF when ROOT is WEF and WEF when ROOT is EEF. Sum into a temporary counter, then compare against the precomputed integer threshold floor(N/2)+1. Never equate ownership with control. Existing WA ITA decisions use `controls_province`.

Also require war, an unlocked operations focus, no current offensive operation, at least one remaining hostile target province and a reachable adjacent friendly frontline state. Freeze the province/state target list at launch. The >50% rule is a launch condition only: successful progress must not cancel the offensive when enemy control drops below half. Revalidate war and remaining target at the end of preparation, without reapplying the launch majority rule.

Victory: all playable target land provinces controlled by the launching side. No automatic allied qualification in this two-country prototype. Tactical victory requires every province of its state. Strategic victory requires every playable province of its region. Completion during preparation also counts, preventing charging for an already conquered objective.

## Fatigue accounting

Proposed first-playtest rate, not a user-specified balance value: +1 fatigue point each 7 days for both phases. Keep the weekly counter running across the phase boundary. Tactical preparation adds 1 point; strategic preparation adds 4 points, with its remaining 2 days carrying into the offensive. Full unsuccessful campaigns add 3 / 12 points respectively. This makes the longer campaign substantially more expensive and must be tested for balance.

Track the *actual applied* preparation increase in a separate country variable. Call WA's `economy_fatigue_level_up_1`, compare economic_fatigue before and after, and record only the difference. At cap 100, a blocked increase must not create a refundable credit. On victory call the native `economy_fatigue_level_down_1` once per recorded point, clamping through WA's own effect. Never overwrite economic_fatigue with its launch value: other mechanics may change it during the operation. Offensive fatigue is never refunded.

Example: tactical operation starts at fatigue 10, completes preparation at 11, gains another point after 7 offensive days, then wins: fatigue becomes 11 after the one-point preparation refund. A victory before the next weekly charge stops that charge.

Daily ordering: peace/cancellation; victory; fatigue charge; preparation/timeout transition. A victory on the deadline wins. End-of-war cancellation and timeout retain accumulated fatigue, give no refund and stop future ticks. No additional failure penalty in this prototype, because the user requested gradual fatigue and no extra penalty.

## Engine implementation plan

Use one country-owned operation record per side: phase, target type, target province/state arrays, remaining phase days, fatigue day counter and preparation refund. No shared global clock. Native decisions/missions show 7/30-day preparation and 14/60-day offensive timers. Daily country effects update the accounting and automatically resolve victory, so the player does not need to click a completion button.

Use WA's state dynamic modifier pattern: `common/decisions/ITA.txt`, ITA_subdue_the_sentinels decision applies `ITA_planned_offensive` to states with `scope = ITA` and `days = 90`. This establishes the scoped regional approach. Existing WAEF local/regional modifiers propose +5% attack, with regional +10% organisation recovery. Preserve these values only as provisional defaults; neither magnitude was specified in the new request. Battle testing must verify that only the launching country's divisions receive the modifier, in the target state and during the active phase only. Do not assume `scope = ROOT` alone proves that behaviour.

Cleanup removes all side-specific modifiers, active missions, arrays and operation bookkeeping exactly once. Bonuses carry an explicit 14/60-day expiry as a backup. Never remove the opposite side's modifier. Old callbacks must be cancelled or guarded so they cannot close a later operation. Save/load uses country variables and native timers, with no initialization reset for an active operation.

Replace offensive code in the generator, not just generated decisions. Leave defensive fortification projects separate. Existing political/command costs, 365-day cooldown and focus specialisations are inherited legacy behaviour, not new requirements: review them before enabling the replacement. Duration-changing GER/JAP/SOV specialisations conflict with the new fixed timing and need updated focus tooltips/effects as part of that implementation.

## Verification and next implementation checkpoint

Six offline tests cover strict majority, preparation-only refund, a clock spanning phases, actual applied refunds at cap 100, timeout/peace and victory-before-charge ordering. Map audit validates 282 states and exact region membership. These tests establish accounting, not game engine behaviour.

Next: generate exact province counters and country-specific daily effects, replace offensive missions with the two requested variants, update RU/EN tooltips and add integration checks. Then playtest: two simultaneous opposing operations, bonus scope in battles, divided state control, exact 50% region control, victory in preparation/on deadline, cancellation, and save/load. Do not publish to main until the playable prototype is verified.

## User follow-up: WA Japanese and Soviet decisions

Read the actual upstream WA code, not a copied wiki example:

- `common/decisions/JAP.txt`, `JAP_military_offensive`: `state_target = yes`, `FROM` for selected state and `on_map_mode = map_and_decisions_view`. Use this interface for tactical operations, with the audited 165-state eligibility list. Do not copy the Japanese China-only conditions or neighbour expansion; our tactical objective is exactly one state.
- `common/scripted_effects/JAP_scripted_effects.txt`, `JAP_set_military_offensive_effect`: active code applies the static province modifier `military_offensive`. Its dynamic modifier implementation is commented out. Do not copy that static modifier blindly into a symmetric WEF/EEF conflict; side-specific behaviour needs verification.
- `common/decisions/SOV.txt`, `SOV_operation_uranus` and `SOV_operation_saturn`: normal decisions highlight a state and iterate states by `region = ID`, applying `SOV_offensive_operation` with `scope = SOV` and an explicit expiry. This is the regional pattern to adapt for strategic operations. Our version uses one air region, a strict enemy province majority and a separate preparation phase.
- `SOV_operation_bagration` instead gives a country-wide targeted bonus against GER and other country modifiers. That would exceed the requested geographic area. Reuse its decision presentation and 60-day mission concept only; use Uranus-style state modifiers for the actual regional bonus.
- `SOV_set_military_offensive_effect` / `SOV_clean_military_offensive_effect` show a saved state array, scoped dynamic modifiers and explicit cleanup. Use this structure for independent WEF/EEF target lists.

Interface decision: tactical icons on the map and visible in the decisions view, as Japan; strategic operations as named regional decisions with target-state highlights, as Soviet regional operations. Localisation must name the region, list target states, show preparation/offensive timers, weekly fatigue and refundable preparation points. No country-wide offensive modifier.

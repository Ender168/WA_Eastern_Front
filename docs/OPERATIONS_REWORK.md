# Operations rework: playable test branch

Branch: feature/operations-rework. Based on main 9ffbd161f06999ce1e9ed810383a1b436b316af7. Latest requirements supersede the earlier weekly-fatigue draft.

## Interface and availability

Tactical and strategic operations are separate categories visible from game start for WEF/EEF. Neither visibility nor launching depends on peace, war, assimilation, date or an operations focus. Strategic decisions remain in the decisions list only: incomplete one-state highlights have been removed. Tactical operations use Japanese-style map state targets. Only state/region names appear in launch decision titles, with command/political costs displayed as icons. Category descriptions explain effect coverage and timing; individual decisions do not enumerate affected states. No operation cooldown or failure penalty remains. Existing defensive-line construction is separate and unchanged.

## Targets and timing

| Type | Preparation | Offensive | Preparation fatigue | Cost |
| --- | --- | --- | --- | --- |
| Tactical | 7 days | 14 days | +2 points immediately | 25 command power + 25 political power |
| Strategic | 30 days | 60 days | +5 points immediately | 50 command power + 50 political power |

The requested latest tactical threshold is **at least 7 land provinces**, replacing the initial >7 interpretation. 187 of 282 playable states qualify. Memel, Suwalki and Carpathian Ruthenia do not qualify. Targets must contain opponent-controlled provinces and touch a state controlled by the attacking side, without requiring an actual war.

Strategic launch requires strictly more than half of the full air region's land provinces controlled by the opposing side. Generated `count_triggers` with `controls_province` checks distinguish province control from ownership/state control; exactly 50% fails. Neutral land counts in the denominator but not the enemy numerator. Sea/lake provinces do not count. Bonuses affect every WEF/EEF state in the selected region; neutral OBS states are excluded. Audit found no playable states split across region borders.

## Missions and fatigue

Clicking a launch decision charges preparation fatigue immediately and starts a native 7/30-day preparation mission. Preparation adds no repeating charges. After preparation, the 14/60-day offensive mission and a separate repeating fatigue mission: every 7 days for tactical operations and every 10 days for strategic operations activate together. Each offensive fatigue timeout gives +1 fatigue point and reactivates its timer while the operation remains active. A 30-day offensive therefore costs 3 offensive points; the configured 60-day strategic offensive costs 6.

Victory requires full control by the attacker of every target state, including all its provinces. Daily checks resolve victory automatically; fatigue and deadline callbacks check victory before charging. Cleanup removes preparation, offensive and fatigue missions, side-specific bonuses, flags and target arrays. Continued charges stop after victory. Offensive deadline failure adds no extra penalty and gives no refund. The final deadline settles any missing full fatigue interval (7/10 days) to avoid callback-order undercharging, then stops all timers.

Success refunds only the actual preparation increase recorded at click time. Native WA fatigue effects maintain the fatigue idea and clamp 0..100. A blocked charge at cap 100 creates no refund credit. Offensive fatigue remains. Other fatigue mechanics are never reset to a launch snapshot. If the objective is conquered during preparation, the daily check also ends the mission and refunds preparation.

No country-wide attack modifier is used. Bonuses are scoped state dynamic modifiers, separately named for WEF/EEF, with explicit 14/60-day fallback expiry. Current test values are +5% attack tactically and +5% attack/+10% organisation recovery strategically. Engine/battle verification is still required for side-specific scope.

## WA source patterns

Read upstream WA 9.6 at 691c7085f3ec1333ac2a0742983da8a64011ca8b:

- JAP.txt / JAP_military_offensive: state targets, FROM and map_and_decisions_view. Its static province modifier is deliberately not copied blindly.
- SOV.txt / SOV_operation_uranus and SOV_operation_saturn: state effects covering strategic regions. Bagration's country-wide attack bonus would exceed requested coverage.
- SOV_scripted_effects.txt: saved state arrays, country-scoped dynamic modifiers and cleanup.
- Economy_Fatigue_scripted_effects.txt: immediate increases/decreases, idea synchronization and the 100-point cap.
- SOV.txt: count_triggers pattern; ITA.txt: controls_province checks; ENG.txt: remove_mission cleanup.

## Temporary war test button

`waef_test_declare_war` in the existing war setup category is available from game start, costs zero and immediately declares WEF/EEF war on the other side. AI is disabled. It bypasses the scheduled date and does not grant the normal offensive-momentum spirit. The normal declaration decision remains. Remove the test button and its dedicated RU/EN localisation after playtesting.

## Verification

89 Python checks pass, including map thresholds, strict majority, immediate preparation charge, 30-day three-point accounting, cap refunds, success cancellation, category independence, no cooldown/failure war-support penalties, complete cleanup and temporary war access. Generated files reproduce from the generator. No in-game test has been performed in this environment. Begin a new test campaign; migrating an already active legacy operation is not supported.

## Compact strategic condition tooltip

Strategic availability wraps the exact province-count trigger in `custom_trigger_tooltip`. The UI shows one checked/failed sentence about enemy majority instead of expanding both country branches and every province. The full predicate still determines launch availability. Tactical fatigue localisation and the final-deadline accounting now use a 7-day interval; the 14-day tactical offensive therefore adds 2 offensive fatigue points if it runs its full duration. Strategic fatigue remains every 10 days.

## Frontline and availability filtering

Strategic launch decisions are visible only when all launch conditions and costs are met: no current operation, 50 command/political power, enemy control of more than half the region, and an enemy-held target state adjacent to a state controlled by the launching side. The frontline condition checks opponent-held provinces, so a friendly state in the region cannot make an otherwise remote region eligible by itself. Availability repeats the geographic checks using compact custom tooltips. Already running preparation/offensive/fatigue missions remain visible independently of the launch filter. Both categories retain their start-of-game visibility and do not require war.

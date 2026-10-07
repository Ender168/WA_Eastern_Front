# Strategic Front v0.25

## Rules
- 20 VP cities for WEF and 20 for EEF, all worth one city.
- Cities are tracked at **VP province** level, not by entire state. Dresden and Leipzig are both in state 65 but remain independent objectives.
- Capturer automatically starts a 14-day confirmation mission on VP province control; loss of control cancels the mission.
- After timeout a country flag and +1 captured for the attacker, +1 lost for the city's home side are recorded. Holding a liberated city for 14 days removes both.
- No daily full-map scan. The game checks 80 decision activation conditions and only active city missions have timers.
- Victory: confirmed 16/20 starts a 30-day mission, cancelled if the count falls below 16. On timeout both players receive a result event and `white_peace` ends only their war without annexing/modifying static states.
- Category summary shows captures/losses. Active timers and confirmed city status are normal, non-clickable decisions, no scripted GUI or new graphics.
- No changes to map, industry, military setup, doctrines, fuel, railways, existing war declaration or other WA mechanics.

## Validation / limits
- Run `python tools/validate_waef_strategic_front.py` to check city ownership, VP IDs, counts and generated blocks.
- HOI4 engine behavior must still be tested with an actual game load, capture, cancellation, liberation and victory.
- Existing vanilla/WA capitulation mechanics remain active and could resolve a war earlier than 16/20. Tune separately only if actual testing requires it.
- This first pass uses the city list from the planning discussion, *not* a proven symmetric BFS-depth comparison.

## WEF
| City | State | VP province |
|---|---:|---:|
| Данциг | 85 | 362 |
| Варшава | 10 | 3544 |
| Краков | 88 | 9427 |
| Клуж | 76 | 6711 |
| Бухарест | 46 | 9617 |
| Бреслау | 66 | 9570 |
| Прага | 9 | 11542 |
| Будапешт | 889 | 9660 |
| Белград | 107 | 11586 |
| София | 48 | 949 |
| Дрезден | 65 | 514 |
| Лейпциг | 65 | 3535 |
| Братислава | 70 | 9692 |
| Загреб | 109 | 11581 |
| Пловдив | 212 | 6923 |
| Берлин | 810 | 6521 |
| Вена | 882 | 11666 |
| Линц | 152 | 732 |
| Брно | 75 | 3569 |
| Сараево | 104 | 11899 |

## EEF
| City | State | VP province |
|---|---:|---:|
| Каунас | 11 | 6296 |
| Вильнюс | 784 | 3320 |
| Львов | 91 | 11479 |
| Минск | 206 | 11370 |
| Рига | 966 | 9340 |
| Псков | 209 | 11202 |
| Киев | 202 | 525 |
| Гомель | 241 | 9288 |
| Смоленск | 242 | 306 |
| Одесса | 192 | 11670 |
| Ленинград | 195 | 3151 |
| Брянск | 224 | 3335 |
| Курск | 220 | 3580 |
| Харьков | 221 | 418 |
| Москва | 219 | 6380 |
| Воронеж | 260 | 413 |
| Ростов | 218 | 9417 |
| Днепропетровск | 226 | 11437 |
| Сталинград | 217 | 3529 |
| Горький | 252 | 11375 |

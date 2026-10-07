"""German playtest revision, 8 October 2026; source years define packages only."""
import re

LEVELS = (1941, 1943, 1945)
STRIKE = ('S', 'B', 'R')
JET_EFFECT = 'waef_grant_german_jet_aircraft'
JET_COMPLETIONS = ('C25', 'A3', 'W3', 'S3', 'B3', 'R3', 'U3')


def records(common):
    out = [list(r) for r in common]
    for r in out:
        for old, new in [('1941', 'I'), ('1943', 'II'), ('1945', 'III')]:
            r[1] = r[1].replace(old, new)
    out += [
        ['P1', 'Концентрированная промышленность', '1941 / 21', 'Выбор школы', 'Заменяет стандартную промышленность на концентрированную'],
        ['P2', 'Рассредоточенная промышленность', '1941 / 21', 'Выбор школы', 'Заменяет стандартную промышленность на рассредоточенную'],
    ]
    branches = [
        ('I', 'Пехотное вооружение', 'Пехота и обучение'),
        ('G', 'Огневая поддержка', 'Артиллерия, ПТО и ПВО'),
        ('M', 'Моторизация и механизация', 'Моторизованная и механизированная техника отдельной ветви'),
        ('T', 'Средние танки', 'Средние танки, профильные САУ, лёгкие танки и разведывательные/боевые бронеавтомобили'),
        ('H', 'Тяжёлые танки', 'Тяжёлые танки, профильные САУ, лёгкие танки и разведывательные/боевые бронеавтомобили'),
        ('A', 'Messerschmitt', 'Развитие истребителей Bf 109'),
        ('W', 'Focke-Wulf', 'Развитие истребителей Fw 190 и Ta 152; исключает тяжёлые танки'),
        ('U', 'Вспомогательная авиация', 'Разведчики, транспортная авиация и тяжёлые перехватчики'),
        ('S', 'Штурмовая авиация', 'Штурмовики и истребители-штурмовики'),
        ('B', 'Фронтовые бомбардировщики', 'Тактические, скоростные, ударные и морские бомбардировщики'),
        ('R', 'Стратегическая авиация', 'Стратегические бомбардировщики'),
    ]
    for prefix, title, desc in branches:
        for level, yr in enumerate(LEVELS, 1):
            if prefix=='R' and level==1:yr=1942  # He 177 designer technology in BBA.
            pre = 'C00' if level == 1 else prefix + str(level - 1)
            out.append([prefix + str(level), title + ' ' + ['I', 'II', 'III'][level - 1], f'{yr} / 91', pre, desc])
    out.append(['O2', 'Штаб наступательных операций', '1942 / 70', 'C70 и I1', 'Подготовка региональной операции: 7 дней'])
    return out


EN = {
    'P1': 'Concentrated Industry', 'P2': 'Dispersed Industry',
    **{prefix + str(level): title + ' ' + ['I', 'II', 'III'][level - 1]
       for prefix, title in [('I', 'Infantry Armament'), ('G', 'Fire Support'),
                            ('M', 'Motorisation and Mechanisation'), ('T', 'Medium Tanks'),
                            ('H', 'Heavy Tanks'), ('A', 'Messerschmitt'), ('W', 'Focke-Wulf'),
                            ('U', 'Auxiliary Aviation'), ('S', 'Ground Attack Aviation'),
                            ('B', 'Frontline Bombers'), ('R', 'Strategic Aviation')]
       for level in [1, 2, 3]},
}

# The previous Support Companies I position (x=9) is the new left boundary.
# Two horizontal units keep neighbouring focus labels apart. A single vertical
# unit is the standard HOI4 row spacing, replacing the previous double spacing.
COORDS = {'C00': (18, 0), 'P1': (9, 0), 'P2': (11, 0),
          'C41': (13, 4), 'C42': (15, 4), 'C51': (17, 4), 'C52': (19, 4),
          'C61': (9, 4), 'C62': (11, 4), 'C70': (26, 4), 'O2': (26, 5)}
for prefix, x in [('C3', 10), ('C1', 14), ('C2', 18)]:
    for suffix, y in zip(['1', '3', '5'], [1, 2, 3]):
        COORDS[prefix + suffix] = (x, y)
for prefix, x in [('U', 20), ('I', 22), ('G', 24), ('M', 26)]:
    for level in [1, 2, 3]:
        COORDS[prefix + str(level)] = (x, level)
for prefix, x in [('T', 9), ('H', 11), ('A', 13), ('W', 15),
                  ('S', 19), ('B', 21), ('R', 23)]:
    for level in [1, 2, 3]:
        COORDS[prefix + str(level)] = (x, level + 4)


def route(t):
    name = t.name[4:]
    file = t.path.split('/')[-1]
    if file == 'armor_ger.txt':
        if any(x in name for x in ['scout', 'combat_car', 'armoured_car', 'light']):
            return 'L'
        if any(x in name for x in ['motorised', 'motorized', 'mechanized', 'amphibious']):
            return 'M'
        if 'heavy' in name or 'landkruiser' in name:
            return 'H'
        return 'T'
    if file == 'air_techs_ger.txt':
        if 'strategic' in name:
            return 'R'
        if any(x in name for x in ['cas', 'attacker']):
            return 'S'
        if any(x in name for x in ['bomber', 'patrol']):
            return 'B'
        if any(x in name for x in ['scout', 'transport', 'heavy_fighter', 'air_upgrade']):
            return 'U'
        if 'jet' in name:
            if re.search(r'GER_ta_183', t.body) or name in ['jet_fighter_2','jet_fighter_3','jet_cv_fighter_2','jet_cv_fighter_3']:
                return 'W'
            if re.search(r'GER_(?:he_162|ho229)', t.body) or name=='jet_fighter_1':
                return 'U'
        # Both equipment modes: the classic carrier Fw 190 has no "multirole"
        # in its technology ID, so inspect the enabled airframes as well.
        if 'jet' not in name and ('multirole' in name or name in ['cv_fighter_3', 'cv_fighter_5']
                                 or re.search(r'GER_(?:fw_190|ta_152)', t.body)):
            return 'W'
        return 'A'
    return None


def is_jet(t):
    return t.path.endswith('/air_techs_ger.txt') and 'jet' in t.name


def packages(techs, records):
    by = {r[0]: r for r in records}
    out = {r[0]: set() for r in records}
    gates = {}
    jet_ids = {p: set() for p in ['A', 'W', 'S', 'B', 'R', 'U']}
    hidden = {child for t in techs.values() for child in t.sub_technologies}

    def assign(t, prefix):
        choices = sorted((int(by[c][2].split('/')[0]), c)
                         for c in [prefix + str(i) for i in [1, 2, 3]]
                         if int(by[c][2].split('/')[0]) >= t.year)
        if choices:
            out[choices[0][1]].add(t.name)

    for name, t in techs.items():
        if not t.path.endswith(('_ger.txt', '/industry.txt', '/electronic_mechanical_engineering.txt', '/support.txt')):
            continue
        if t.doctrine or t.year <= 1940 or (not t.has_folder and 'enable_equipments' not in t.body and name not in hidden):
            continue
        family = route(t)
        if is_jet(t):
            options = [family + '1']
            gates[name] = {'any': ['WAEF_GER_' + c for c in options], 'all': ['WAEF_GER_C25']}
            if t.year <= 1945:
                jet_ids[family].add(name)
        elif family:
            if family == 'L':
                for prefix in ['T', 'H']:
                    assign(t, prefix)
                gates[name] = ['WAEF_GER_T1', 'WAEF_GER_H1']
            else:
                assign(t, family)
                options = ['WAEF_GER_' + family + '1']
                # Only the third stage of a different strike route unlocks the
                # first-stage package, for focus grants and normal research.
                if family in STRIKE and t.year <= int(by[family+'1'][2].split('/')[0]):
                    options += ['WAEF_GER_' + p + '3' for p in STRIKE if p != family]
                gates[name] = options
        elif t.path.endswith('/infantry_ger.txt'):
            assign(t, 'I')
            gates[name] = []
        elif t.path.endswith('/artillery_ger.txt'):
            assign(t, 'G')
            gates[name] = []
    for node, name in [('P1', 'concentrated_industry'), ('P2', 'dispersed_industry')]:
        out[node].add(name)
    jet_rewards = [{'requires_all': ['WAEF_GER_C25'],
                    'requires_any': ['WAEF_GER_' + c for c in [p + '3']],
                    'technologies': sorted(ids)} for p, ids in jet_ids.items() if ids]
    return out, gates, jet_rewards


def finish_packages(packages):
    """Share closed first-stage packages only after hidden-tech closure is complete."""
    basics = {p: set(packages[p + '1']) for p in STRIKE}
    for p in STRIKE:
        packages[p + '3'] |= set().union(*(basics[q] for q in STRIKE if q != p))


EXCLUDES = {'P1': ['P2'], 'P2': ['P1'], 'T1': ['H1'], 'H1': ['T1', 'W1'],
            'A1': ['W1'], 'W1': ['A1', 'H1'],
            'S1': ['B1', 'R1'], 'B1': ['S1', 'R1'], 'R1': ['S1', 'B1']}

# Preserve requirements through availability without drawing diagonal links
# across the upper blocks. Dependencies and focus durations are unchanged.
HIDDEN_LINKS = {p+'1': ['C00'] for p in ['T','H','A','W','S','B','R']}
HIDDEN_LINKS.update({'C70': ['C00'], 'O2': ['I1']})

"""German playtest revision, 8 October 2026; source years define packages only."""
import re

LEVELS = (1941, 1943, 1945)
STRIKE = ('S', 'B', 'R')
JET_STAGES = ('A4','W4','S4','B4','R4')


def records(common):
    out = [list(r) for r in common]
    for r in out:
        for old, new in [('1941', 'I'), ('1943', 'II'), ('1945', 'III')]:
            r[1] = r[1].replace(old, new)
    next(r for r in out if r[0]=='C00')[2]='1941 / 14'
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
        ('S', 'Штурмовая авиация', 'Штурмовики и истребители-штурмовики'),
        ('B', 'Фронтовые бомбардировщики', 'Тактические, скоростные, ударные и морские бомбардировщики'),
        ('R', 'Стратегическая авиация', 'Стратегические бомбардировщики'),
    ]
    for prefix, title, desc in branches:
        years = (1941,1943,1944,1945) if prefix=='I' else LEVELS
        if prefix=='R':years=(1942,1945,1947)
        if prefix in ['T','H']:years=(*LEVELS,1945)
        for level, yr in enumerate(years, 1):
            pre = 'C00' if level == 1 else prefix + str(level - 1)
            out.append([prefix + str(level), title + ' ' + ['I','II','III','IV'][level-1], f'{yr} / 91', pre, desc])
        if prefix in ['A','W','S','B','R']:
            out.append([prefix+'4',{'A':'Реактивные Messerschmitt','W':'Реактивные Focke-Wulf','S':'Реактивные штурмовики','B':'Реактивные бомбардировщики','R':'Стратегическая реактивная авиация'}[prefix], '1947 / 7',prefix+'3 и C25','Реактивная авиация'])
    out.append(['O2', 'Штаб наступательных операций', '1942 / 70', 'C70 и I1', 'Подготовка региональной операции: 7 дней'])
    return out


EN = {
    'P1': 'Concentrated Industry', 'P2': 'Dispersed Industry',
    **{prefix + str(level): title + ' ' + ['I', 'II', 'III','IV'][level - 1]
       for prefix, title in [('I', 'Infantry Armament'), ('G', 'Fire Support'),
                            ('M', 'Motorisation and Mechanisation'), ('T', 'Medium Tanks'),
                            ('H', 'Heavy Tanks'), ('A', 'Messerschmitt'), ('W', 'Focke-Wulf'),
                            ('S', 'Ground Attack Aviation'),
                            ('B', 'Frontline Bombers'), ('R', 'Strategic Aviation')]
       for level in [1,2,3,4]},
}

EN.update({'A4':'Jet Messerschmitt','W4':'Jet Focke-Wulf','S4':'Jet Ground Attack Aircraft','B4':'Jet Bombers','R4':'Strategic Jet Aviation'})

# The previous Support Companies I position (x=9) is the new left boundary.
# Two horizontal units keep neighbouring focus labels apart. A single vertical
# unit is the standard HOI4 row spacing, replacing the previous double spacing.
COORDS = {'C00': (18, 0), 'P1': (9, 0), 'P2': (11, 0),
          'C41': (13, 4), 'C42': (15, 4), 'C51': (17, 4), 'C52': (19, 4),
          'C61': (9, 4), 'C62': (11, 4), 'C70': (26, 4), 'O2': (26, 5)}
for prefix, x in [('C3', 10), ('C1', 14), ('C2', 18)]:
    for suffix, y in zip(['1', '3', '5'], [1, 2, 3]):
        COORDS[prefix + suffix] = (x, y)
for prefix, x in [('I', 22), ('G', 24), ('M', 26)]:
    for level in [1, 2, 3]:
        COORDS[prefix + str(level)] = (x, level)
for prefix, x in [('T', 9), ('H', 11), ('A', 15), ('W', 13),
                  ('S', 19), ('B', 21), ('R', 23)]:
    for level in [1, 2, 3]:
        COORDS[prefix + str(level)] = (x, level + 4)
    COORDS[prefix+'4']=(x,8)
COORDS['I4']=(22,4)


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
        if any(x in name for x in ['scout', 'transport', 'air_upgrade']):
            return 'F'
        if 'heavy_fighter' in name:
            if 'conversion' in name or name=='heavy_fighter_2':return 'B'
            if re.search(r'GER_me_410',t.body):return 'A'
            return 'F'
        if 'jet' in name:
            if re.search(r'GER_ta_183', t.body) or name in ['jet_fighter_2','jet_fighter_3','jet_cv_fighter_2','jet_cv_fighter_3']:
                return 'W'
            if re.search(r'GER_(?:he_162|ho229)', t.body) or name=='jet_fighter_1':
                return 'F'
        # Both equipment modes: the classic carrier Fw 190 has no "multirole"
        # in its technology ID, so inspect the enabled airframes as well.
        if 'jet' not in name and ('multirole' in name or name in ['cv_fighter_3', 'cv_fighter_5']
                                 or re.search(r'GER_(?:fw_190|ta_152)', t.body)):
            return 'W'
        return 'A'
    return None


def is_jet(t):
    return t.path.endswith('/air_techs_ger.txt') and 'jet' in t.name


def late_tank(t):
    if route(t)=='T' and 'modern' in t.name and t.year>=1944:return 'T4'
    if route(t)=='H' and (any(x in t.name for x in ['super_heavy','landkruiser'])
                         or t.name in ['ger_heavy_tank_chassis_5','ger_heavy_assault_tank_4_spg']):return 'H4'
    return None


def packages(techs, records):
    by={r[0]:r for r in records};out={r[0]:set() for r in records};gates={}
    hidden={child for t in techs.values() for child in t.sub_technologies}
    def assign(t,prefix):
        candidates=[c for c in by if re.fullmatch(prefix+r'\d',c)]
        if prefix in ['A','W','S','B','R']:candidates=[c for c in candidates if not c.endswith('4')]
        late=late_tank(t)
        if late:
            if t.year<=int(by[late][2].split('/')[0]):out[late].add(t.name)
            return
        choices=sorted((int(by[c][2].split('/')[0]),c) for c in candidates if int(by[c][2].split('/')[0])>=t.year)
        if choices:out[choices[0][1]].add(t.name)
    for name,t in techs.items():
        if not t.path.endswith(('_ger.txt','/industry.txt','/electronic_mechanical_engineering.txt','/support.txt')):continue
        if t.doctrine or t.year<=1940 or (not t.has_folder and 'enable_equipments' not in t.body and name not in hidden):continue
        family=route(t)
        if is_jet(t):
            stages=['A4','W4'] if family=='F' else [family+'4']
            gates[name]={'any':['WAEF_GER_'+c for c in stages],'all':['WAEF_GER_C25']}
            if t.year<=1947:
                for stage in stages:out[stage].add(name)
        elif family:
            if family in ['L','F']:
                targets=['T','H'] if family=='L' else ['A','W']
                for prefix in targets:assign(t,prefix)
                gates[name]=['WAEF_GER_'+p+'1' for p in targets]
            else:
                assign(t,family)
                late=late_tank(t)
                options=['WAEF_GER_'+(late or family+'1')]
                if family in STRIKE and t.year<=int(by[family+'1'][2].split('/')[0]):
                    options+=['WAEF_GER_'+p+'3' for p in STRIKE if p!=family]
                gates[name]=options
        elif t.path.endswith('/infantry_ger.txt'):assign(t,'I');gates[name]=[]
        elif t.path.endswith('/artillery_ger.txt'):assign(t,'G');gates[name]=[]
    for node,name in [('P1','concentrated_industry'),('P2','dispersed_industry')]:out[node].add(name)
    return out,gates


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

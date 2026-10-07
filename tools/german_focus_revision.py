"""German tree revision requested after the first in-game test, 7 October 2026."""
import re

def records(common):
    common=[list(r) for r in common]
    for r in common:
        for old,new in [('1941','I'),('1943','II'),('1945','III')]:r[1]=r[1].replace(old,new)
    common += [
        ['P1','Концентрированная промышленность','1941 / 21','Выбор школы','Заменяет стандартную промышленность на концентрированную'],
        ['P2','Рассредоточенная промышленность','1941 / 21','Выбор школы','Заменяет стандартную промышленность на рассредоточенную'],
    ]
    out=common
    def row(code,name,yr,pre,desc,days=91):out.append([code,name,f'{yr} / {days}',pre,desc])
    for prefix,title,desc in [('I','Пехотное вооружение','Пехота и обучение'),('G','Огневая поддержка','Артиллерия, ПТО и ПВО')]:
        for level,yr in enumerate([1941,1943,1945],1):row(prefix+str(level),title+' '+['I','II','III'][level-1],yr,'C00' if level==1 else prefix+str(level-1),desc)
    for prefix,title,desc in [
        ('L','Разведывательная и лёгкая бронетехника','Scout/combat car, лёгкие танки и их варианты'),
        ('T','Средние танки','Средние танки, Panther и профильные САУ'),
        ('H','Тяжёлые танки','Тяжёлые танки и профильные САУ'),
        ('A','Истребительная авиация','Bf 109, Fw 190 и другие истребители'),
        ('S','Штурмовая авиация','Штурмовики и истребители-штурмовики'),
        ('B','Фронтовые бомбардировщики','Тактические, скоростные, ударные и морские бомбардировщики'),
        ('R','Стратегическая авиация','Стратегические бомбардировщики; базовые пакеты двух других ударных направлений'),
    ]:
        for level,yr in enumerate([1941,1943,1945],1):
            pre=('L1' if prefix in ('T','H') else 'A1' if prefix in ('S','B','R') else 'C00') if level==1 else prefix+str(level-1)
            row(prefix+str(level),title+' '+['I','II','III'][level-1],yr,pre,desc)
    row('M2','Моторизованные соединения',1942,'I1','Моторизация и механизация')
    row('M4','Механизированные соединения',1945,'M2','Поздняя механизация и вспомогательные машины')
    row('O2','Штаб наступательных операций',1942,'C70 и I1','Подготовка региональной операции: 7 дней',70)
    return out

EN={
 'P1':'Concentrated Industry','P2':'Dispersed Industry',
 **{prefix+str(level):title+' '+['I','II','III'][level-1] for prefix,title in [('I','Infantry Armament'),('G','Fire Support'),('L','Reconnaissance and Light Armour'),('T','Medium Tanks'),('H','Heavy Tanks'),('A','Fighter Aviation'),('S','Ground Attack Aviation'),('B','Frontline Bombers'),('R','Strategic Aviation')] for level in [1,2,3]},
}
COORDS={
 'C00':(12,0),'P1':(0,0),'P2':(2,0),
 'C11':(1,2),'C13':(1,4),'C15':(1,6),'C41':(0,8),'C42':(2,8),
 'C21':(5,2),'C23':(5,4),'C25':(5,6),'C51':(4,8),'C52':(6,8),
 'C31':(9,2),'C33':(9,4),'C35':(9,6),'C61':(8,8),'C62':(10,8),
 'C70':(13,10),'O2':(13,12),
 'I1':(13,2),'I2':(13,4),'I3':(13,6),'G1':(17,2),'G2':(17,4),'G3':(17,6),
 'L1':(21,2),'L2':(21,4),'L3':(21,6),'M2':(17,10),'M4':(17,12),
 'T1':(20,10),'T2':(20,12),'T3':(20,14),'H1':(24,10),'H2':(24,12),'H3':(24,14),
 'A1':(4,10),'A2':(12,14),'A3':(12,16),
 'S1':(0,12),'S2':(0,14),'S3':(0,16),'B1':(4,12),'B2':(4,14),'B3':(4,16),'R1':(8,12),'R2':(8,14),'R3':(8,16),
}

def route(t):
    name=t.name[4:];file=t.path.split('/')[-1]
    if file=='armor_ger.txt':
        if any(x in name for x in ['scout','combat_car','armoured_car','light']):return 'L'
        if any(x in name for x in ['motorised','motorized','mechanized','amphibious']):return 'M'
        if 'heavy' in name or 'landkruiser' in name:return 'H'
        return 'T'
    if file=='air_techs_ger.txt':
        if 'strategic' in name:return 'R'
        if any(x in name for x in ['cas','attacker']):return 'S'
        if any(x in name for x in ['bomber','patrol']):return 'B'
        return 'A'
    return None

def packages(techs,records):
    by={r[0]:r for r in records};out={r[0]:set() for r in records};gates={}
    def assign(t,options):
        choices=sorted((int(by[c][2].split('/')[0]),c) for c in options if int(by[c][2].split('/')[0])>=t.year)
        if choices:out[choices[0][1]].add(t.name)
    for name,t in techs.items():
        if not t.path.endswith(('_ger.txt','/industry.txt','/electronic_mechanical_engineering.txt','/support.txt')) or t.doctrine or t.year<=1940:continue
        if not t.has_folder and 'enable_equipments' not in t.body:continue
        family=route(t)
        if family:
            options=['M2','M4'] if family=='M' else [family+str(i) for i in [1,2,3]]
            assign(t,options)
            gate=[f'WAEF_GER_{family}1'] if family in ['T','H','S','B','R'] else []
            if family in ['S','B'] and t.year<=1941:gate.append('WAEF_GER_R1')
            gates[name]=gate
        elif t.path.endswith('/infantry_ger.txt'):assign(t,['I1','I2','I3']);gates[name]=[]
        elif t.path.endswith('/artillery_ger.txt'):assign(t,['G1','G2','G3']);gates[name]=[]
    # The strategic route repeatedly includes precisely the first packages of the
    # two unselected strike routes, never their later upgrades.
    for node in ['R1','R2','R3']:out[node]|=out['S1']|out['B1']
    for node,name in [('P1','concentrated_industry'),('P2','dispersed_industry')]:out[node].add(name)
    return out,gates

EXCLUDES={'P1':['P2'],'P2':['P1'],'T1':['H1'],'H1':['T1'],
 'S1':['B1','R1'],'B1':['S1','R1'],'R1':['S1','B1']}

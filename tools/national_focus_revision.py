"""Apply the German playtest principles to the other WA technology schools."""
import re
import german_focus_revision as german
import generate_1940_tech_baseline as baseline

TANK_TITLES = {
    'SOV': ('Средние танки', 'Тяжёлые танки'),
    'USA': ('Серийные танки', 'Перспективные танки'),
    'ENG': ('Крейсерские танки', 'Пехотные танки'),
    'FRA': ('Средние танки', 'Тяжёлые танки'),
    'ITA': ('Самоходная огневая поддержка', 'Танковая программа'),
    'JAP': ('Мобильная бронетехника', 'Противотанковая бронетехника'),
}
TANK_EN = {'SOV': ('Medium Tanks','Heavy Tanks'), 'USA': ('Serial Tanks','Advanced Tanks'),
           'ENG': ('Cruiser Tanks','Infantry Tanks'), 'FRA': ('Medium Tanks','Heavy Tanks'),
           'ITA': ('Self Propelled Fire Support','Tank Programme'),
           'JAP': ('Mobile Armour','Anti Tank Armour')}
FIGHTER_TITLES = ('Истребители и перехватчики', 'Многоцелевые и палубные истребители')
FIGHTER_EN = ('Fighters and Interceptors', 'Multirole and Carrier Fighters')

def air_route(t):
    name=t.name.split('_',1)[1]
    if 'strategic' in name:return 'R'
    if any(x in name for x in ('cas','attacker')):return 'S'
    if any(x in name for x in ('bomber','patrol')):return 'B'
    if any(x in name for x in ('scout','transport','air_upgrade')):return 'F'
    if t.name.startswith('jap_') and ('fighter' in name or 'interceptor' in name):return 'W' if 'cv_' in name else 'A'
    if any(x in name for x in ('multirole','heavy_fighter','cv_fighter')):return 'W'
    return 'A'

def records(common, nation, techs):
    code=nation['code'];out=german.records(common)
    # Keep national doctrine names; Focke-Wulf restrictions are Germany-specific.
    titles={'T':TANK_TITLES[code][0], 'H':TANK_TITLES[code][1],
            'A':FIGHTER_TITLES[0], 'W':FIGHTER_TITLES[1]}
    if code=='JAP':titles.update(A='Армейские истребители',W='Морские истребители')
    for r in out:
        node=r[0]
        if node=='O2':r[1]=next(x[1] for x in nation['records'] if x[0]=='O2')
        if re.fullmatch('[THAW][1-4]',node):
            prefix=node[0];level=int(node[1]);r[1]=titles[prefix]+' '+['I','II','III','IV'][level-1]
            r[4]=titles[prefix]
        if node.startswith(('T','H')):r[2]=f'{(1941,1943,1944,1947)[int(node[1])-1]} / 91'
        if node.startswith('R') and node!='R4':r[2]=f'{(1941,1945,1947)[int(node[1])-1]} / 91'
        if node in german.JET_STAGES:
            prefix=node[0]
            family=[t.year for t in techs.values() if t.path.endswith('/air_techs_'+code.lower()+'.txt') and 'jet' in t.name and (air_route(t)==prefix or (prefix in ('A','W') and air_route(t)=='F')) and t.year>1940]
            # The first jet in some WA schools is later than 1947. Still give
            # each route its actual first generation instead of an empty focus.
            cutoff=max(1947,min(family)) if family else 1947
            r[2]=f'{cutoff} / 7'
            if prefix in titles:r[1]='Реактивная авиация: '+titles[prefix].lower()
    return out

def english(code,node):
    if re.fullmatch('[THAW][1-4]',node):
        p=node[0];level=int(node[1]);title=TANK_EN[code]['TH'.index(p)] if p in 'TH' else FIGHTER_EN['AW'.index(p)]
        if code=='JAP' and p in 'AW':title=('Army Fighters','Naval Fighters')['AW'.index(p)]
        return ('Jet '+title if p in 'AW' and level==4 else title+' '+['I','II','III','IV'][level-1])
    return german.EN.get(node)

def packages(techs, records, code, tank_route):
    by={r[0]:r for r in records};out={n:set() for n in by};gates={}
    hidden={child for t in techs.values() for child in t.sub_technologies}
    def assign(t,p):
        options=[n for n in by if re.fullmatch(p+r'\d',n)]
        if p in ('A','W','S','B','R'):options=[n for n in options if not n.endswith('4')]
        choices=sorted((int(by[n][2].split('/')[0]),n) for n in options if int(by[n][2].split('/')[0])>=t.year)
        if choices:out[choices[0][1]].add(t.name)
    for name,t in techs.items():
        if not t.path.endswith('_'+code.lower()+'.txt') or not name.startswith(code.lower()+'_'):continue
        if t.doctrine or t.year<=1940 or name in baseline.FORCE_EXCLUDE:continue
        if not t.has_folder and 'enable_equipments' not in t.body and name not in hidden:continue
        if '/armor_' in t.path:
            if any(x in name for x in ('scout','combat_car','armoured_car','light')):families=['T','H']
            elif any(x in name for x in ('motorised','motorized','mechanized','amphibious')):families=['M']
            else:families=['T' if tank_route(code,name)=='TA' else 'H']
            late=families[0] in ('T','H') and len(families)==1 and (t.year>=1945 or 'super_heavy' in name or ('modern' in name and t.year>=1944))
            for p in families:
                if late:
                    if t.year<=int(by[p+'4'][2].split('/')[0]):out[p+'4'].add(name)
                else:assign(t,p)
            gates[name]=['WAEF_'+code+'_'+p+('4' if late else '1') for p in families]
        elif '/air_techs_' in t.path:
            p=air_route(t);families=['A','W'] if p=='F' else [p]
            if 'jet' in name:
                for q in families:
                    if t.year<=int(by[q+'4'][2].split('/')[0]):out[q+'4'].add(name)
                gates[name]={'any':['WAEF_'+code+'_'+q+'4' for q in families], 'all':['WAEF_'+code+'_C25']}
            else:
                for q in families:assign(t,q)
                opts=['WAEF_'+code+'_'+q+'1' for q in families]
                if p in german.STRIKE and t.year<=int(by[p+'1'][2].split('/')[0]):opts+=['WAEF_'+code+'_'+q+'3' for q in german.STRIKE if q!=p]
                gates[name]=opts
        elif '/infantry_' in t.path:assign(t,'I');gates[name]=[]
        elif '/artillery_' in t.path:assign(t,'G');gates[name]=[]
    if code=='USA':out['M1'].add('lend_lease_truck')
    for n,t in [('P1','concentrated_industry'),('P2','dispersed_industry')]:out[n].add(t)
    return out,gates

EXCLUDES={k:list(v) for k,v in german.EXCLUDES.items()}
EXCLUDES['H1']=['T1'];EXCLUDES['W1']=['A1']
# Existing national equipment bonuses keep their recipient families and move
# to the corresponding revised stages; heavy stage III has no bonus.
LEGACY = {'SOV':{'T3':'TA4','H4':'TB4'}, 'USA':{'T3':'TA4','H3':'TB4','M3':'M4'},
          'FRA':{'T2':'TA3','H4':'TB4'}, 'ITA':{'T3':'TA4','H4':'TB5'},
          'JAP':{'T3':'TA4','H4':'TB5','I2':'I3'}}
EXPENSIVE={'SOV':'H2','USA':'H3','FRA':'H3','ITA':'H4','JAP':'H4'}

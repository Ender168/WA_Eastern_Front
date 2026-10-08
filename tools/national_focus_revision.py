"""National technology schedules from the user's 8 October playtest document."""
import re
import german_focus_revision as german
import generate_1940_tech_baseline as baseline

INFANTRY={'FRA':[1942,1944,1946,9999],'ITA':[1941,1943,1945,9999],'JAP':[1942,1944,1946],
          'SOV':[1942,1944,1946,1947,1949,1950],'ENG':[1942,1944,1947,1949],'USA':[1942,1944,1945,1948,1950]}
ARTILLERY={'FRA':[1941,1943,1945,1948],'ITA':[1941,1943,1945,9999],'JAP':[1942,1944,1946,9999],
           'SOV':[1943,1945,1947,1948],'ENG':[1942,1944,1946,1948],'USA':[1942,1944,1946,1948]}
AIR={'FRA':[1941,1943,1945,1947,1949,9999],'ITA':[1941,1943,1944,1946,1948,9999],
     'JAP':[1942,1943,1944,1945,1947,9999],'SOV':[1942,1943,1944,1945,1947,1949,9999],
     'ENG':[1941,1943,1945,1947,1949,9999],'USA':[1941,1943,1945,1947,1949,9999]}
ELECTRONICS_FROM={'FRA':4,'ITA':5,'JAP':4,'SOV':4,'ENG':4,'USA':4}
TANK_YEARS={'FRA':{'T':[1941,1943,1945,1947,9999],'H':[1941,1943,1945,1947,9999]},
 'ITA':{'T':[1943,1944,1945,1948,1949],'H':[1944,1945,1947,1949]},
 'JAP':{'T':[1943,1945,1947,1949,1950],'H':[1944,1946,1950]},
 'SOV':{'T':[1941,1942,1944,1944,1945,1947,1948,1950], 'H':[1941,1942,1943,1943,1944,1945,1947,1947,1949,1950]},
 'ENG':{'T':[1941,1942,1943,1944,1945,1947,1950],'H':[1941,1942,1943,1945,1947,1950]},
 'USA':{'T':[1942,1943,1944,1945,1947,1949,1950],'H':[1942,1945,1946,1948,1949,1950]}}
NO_MOTOR_BRANCH={'SOV','ENG'}
BASELINE_REMOVE={'eng_fighter_multirole_2','eng_fighter_multirole_ad_tech_2'}
START_IDS={'ITA':['ita_medium_3','ita_medium_tank_chassis_3'],
 'JAP':['jap_medium_4','jap_medium_tank_chassis_4','jap_super_heavy_1','jap_super_heavy_tank_chassis_1'],
 'SOV':['sov_fighter_multirole_5','sov_fighter_multirole_ad_tech_5','sov_fighter_3','sov_fighter_ad_tech_3','sov_attacker_1','sov_attacker_ad_tech_1','sov_strike_bomber_3','sov_strike_bomber_ad_tech_3']}
# Deliberate source-year exceptions requested in the document.
EARLY={'fra_fast_bomber_ad_tech_3'}
AIR_MOVES={'fra_fast_bomber_ad_tech_3':1,'fra_fighter_7':4,'fra_fighter_multirole_ad_tech_6':4}
TANK_TITLES={'FRA':('Средние танки','Тяжёлые танки'),'ITA':('Средние танки','Тяжёлые танки'),
 'JAP':('Средние танки','Тяжёлые и сверхтяжёлые танки'),'SOV':('Средние танки','Тяжёлые танки'),
 'ENG':('Крейсерские танки','Пехотные танки'),'USA':('Средние и основные танки','Тяжёлые танки')}
TANK_EN={'FRA':('Medium Tanks','Heavy Tanks'),'ITA':('Medium Tanks','Heavy Tanks'),
 'JAP':('Medium Tanks','Heavy and Super Heavy Tanks'),'SOV':('Medium Tanks','Heavy Tanks'),
 'ENG':('Cruiser Tanks','Infantry Tanks'),'USA':('Medium and Main Battle Tanks','Heavy Tanks')}
FIGHTER_TITLES=('Истребители и перехватчики','Многоцелевые и палубные истребители')
FIGHTER_EN=('Fighters and Interceptors','Multirole and Carrier Fighters')
ROMAN=('I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII')

def air_route(t):
    name=t.name.split('_',1)[1]
    if 'strategic' in name:return 'R'
    if any(x in name for x in ('cas','attacker')):return 'S'
    if any(x in name for x in ('bomber','patrol')):return 'B'
    if any(x in name for x in ('scout','transport','air_upgrade')):return 'F'
    if t.name.startswith('jap_') and ('fighter' in name or 'interceptor' in name):return 'W' if 'cv_' in name else 'A'
    if any(x in name for x in ('multirole','heavy_fighter','cv_fighter')):return 'W'
    return 'A'

def start_ids(code,techs):
    ids=set(START_IDS.get(code,()))
    for n,t in techs.items():
        if not n.startswith(code.lower()+'_'):continue
        if code=='JAP' and t.path.endswith('/air_techs_jap.txt') and t.year==1941:ids.add(n)
        if code in ('SOV','ENG','USA') and t.path.endswith('/artillery_'+code.lower()+'.txt') and t.year==1941:ids.add(n)
    return ids

def schedules(code):
    return {'I':INFANTRY[code],'G':ARTILLERY[code],**TANK_YEARS[code],
            **{p:AIR[code] for p in ('A','W','S','B','R')},
            **({} if code in NO_MOTOR_BRANCH else {'M':[1941,1943,9999]})}

def records(common,nation,techs):
    code=nation['code'];out=[r for r in german.records(common) if r[0].startswith(('C','P'))]
    titles={'I':'Пехотное вооружение','G':'Огневая поддержка','M':'Моторизация и механизация',
            'T':TANK_TITLES[code][0],'H':TANK_TITLES[code][1],
            'A':FIGHTER_TITLES[0],'W':FIGHTER_TITLES[1],
            'S':'Штурмовая авиация','B':'Фронтовые бомбардировщики','R':'Стратегическая авиация'}
    if code=='JAP':titles.update(A='Армейские истребители',W='Морские истребители')
    if code=='ENG':titles.update(A='Spitfire и перехватчики',W='Hurricane и ударные истребители')
    for p,years in schedules(code).items():
        file='infantry' if p=='I' else 'artillery' if p=='G' else 'armor' if p in ('T','H','M') else 'air_techs'
        maxyear=max(t.year for t in techs.values() if t.path.endswith('/'+file+'_'+code.lower()+'.txt'))
        for i,bound in enumerate(years,1):
            yr=maxyear if bound==9999 else bound
            deps='C00' if i==1 else p+str(i-1)
            if p in ('A','W','S','B','R') and i>=ELECTRONICS_FROM[code]:deps+=' и C25'
            out.append([p+str(i),titles[p]+' '+ROMAN[i-1],f'{yr} / {42 if p=="M" else 91}',deps,titles[p]])
    out.append(['O2',next(r[1] for r in nation['records'] if r[0]=='O2'),'1942 / 70','C70 и I1','Подготовка наступательных операций'])
    return out

def english(code,node):
    m=re.fullmatch('([ITHAWGBRSM])(\\d+)',node)
    if not m:return german.EN.get(node)
    p,i=m[1],int(m[2]);titles={'I':'Infantry Armament','G':'Fire Support','M':'Motorisation and Mechanisation',
       'T':TANK_EN[code][0],'H':TANK_EN[code][1],'A':FIGHTER_EN[0],'W':FIGHTER_EN[1],
       'S':'Ground Attack Aviation','B':'Frontline Bombers','R':'Strategic Aviation'}
    if code=='JAP':titles.update(A='Army Fighters',W='Naval Fighters')
    if code=='ENG':titles.update(A='Spitfire and Interceptors',W='Hurricane and Strike Fighters')
    return titles[p]+' '+ROMAN[i-1]

# Primary tank families: classic models and designer chassis share each stage.
MODEL_GROUPS={
 'USA':{'T':[['medium_3'],['medium_4','medium_6','medium_7'],['medium_5','modern_1'],['modern_2'],['modern_3','modern_4'],['modern_5','modern_7'],['modern_6','modern_8']],
        'H':[['heavy_1'],['heavy_2','heavy_3'],['heavy_4'],['heavy_5'],['heavy_7'],['heavy_6']]},
 'ITA':{'T':[['medium_4'],['medium_5','modern_1'],['medium_6','modern_2'],['modern_3'],['modern_4']],
        'H':[['heavy_1'],['heavy_2'],['heavy_3'],['heavy_4']]},
 'JAP':{'T':[['medium_5','medium_6','medium_7'],['medium_8','medium_9'],['modern_1'],['modern_2'],['modern_3']],
        'H':[['super_heavy_2'],['heavy_3'],['super_heavy_3']]},
 'SOV':{'T':[['medium_4','medium_7'],['medium_5'],['medium_6','medium_8'],['modern_1'],['modern_2'],['modern_3'],['modern_4'],['modern_5']],
        'H':[['heavy_3'],['heavy_4'],['heavy_5'],['heavy_6'],['heavy_7','heavy_8'],['heavy_9'],['heavy_10'],['heavy_11'],['heavy_12'],['heavy_13']]}}
DESIGNER={'USA':{'modern_tank_chassis_1':('T',3),'modern_tank_chassis_1_2':('T',4),'modern_tank_chassis_2':('T',5),'modern_tank_chassis_2_2':('T',5),'modern_tank_chassis_5':('T',6),'modern_tank_chassis_3':('T',6),'modern_tank_chassis_4':('T',7),'modern_tank_chassis_6':('T',7),'medium_tank_chassis_4':('T',2),'medium_tank_chassis_5':('T',2),'heavy_tank_chassis_5':('H',4),'heavy_tank_chassis_6':('H',6),'heavy_tank_chassis_7':('H',5)},'ITA':{'medium_tank_chassis_4':('T',1),'medium_tank_chassis_5':('T',2),'modern_tank_chassis_1':('T',2),'medium_tank_chassis_6':('T',3),'modern_tank_chassis_2':('T',3),'modern_tank_chassis_3':('T',4),'modern_tank_chassis_4':('T',5)},
 'JAP':{'medium_tank_chassis_6':('T',1),'medium_tank_chassis_7':('T',1),'medium_tank_chassis_8':('T',2),'medium_tank_chassis_9':('T',2),
        'heavy_tank_chassis_5':('H',2),'heavy_tank_chassis_6':('H',3),'heavy_tank_chassis_7':('H',3)},
 'SOV':{'medium_tank_chassis_3_2':('T',1),'medium_tank_chassis_4':('T',1),'medium_tank_chassis_3_3':('T',2),'medium_tank_chassis_3_4':('T',3),'medium_tank_chassis_5':('T',3),
        'modern_tank_chassis_1':('T',4),'modern_tank_chassis_1_2':('T',5),'modern_tank_chassis_2':('T',6),'modern_tank_chassis_2_2':('T',7),'modern_tank_chassis_3':('T',8),
        'heavy_tank_chassis_2_2':('H',1),'heavy_tank_chassis_2_3':('H',2),'heavy_tank_chassis_3':('H',2),'heavy_tank_chassis_3_2':('H',3),'heavy_tank_chassis_4':('H',4),'heavy_tank_chassis_4_2':('H',5),
        'heavy_tank_chassis_5':('H',6),'heavy_tank_chassis_6':('H',7),'heavy_tank_chassis_7':('H',8),'heavy_tank_chassis_8':('H',9),'heavy_tank_chassis_8_2':('H',10)}}

def tank_models(code,techs):
    models={code.lower()+'_'+n:(p,i) for p,groups in MODEL_GROUPS.get(code,{}).items() for i,names in enumerate(groups,1) for n in names}
    for n,stage in DESIGNER.get(code,{}).items():models[code.lower()+'_'+n]=stage
    # Chassis IDs whose index matches the corresponding classic vehicle.
    for n,stage in list(models.items()):
        if '_tank_chassis_' in n:continue
        candidate=re.sub(r'_(medium|heavy|modern|super_heavy)_(\d+)$',r'_\1_tank_chassis_\2',n)
        if candidate in techs:models.setdefault(candidate,stage)
    return models

def packages(techs,records,code,tank_route):
    by={r[0]:r for r in records};out={n:set() for n in by};gates={};starts=start_ids(code,techs)
    hidden={s for t in techs.values() for s in t.sub_technologies};models=tank_models(code,techs)
    def choose(t,p):
        rows=[n for n in by if re.fullmatch(p+r'\d+',n)]
        eligible=[n for n in rows if int(by[n][2].split('/')[0])>=t.year]
        return min(eligible,key=lambda n:int(n[len(p):])) if eligible else max(rows,key=lambda n:int(n[len(p):]))
    def ancestor_model(t,seen=()):
        if t.name in models:return models[t.name]
        if t.name in seen:return None
        for dep in t.dependencies:
            if dep in techs:
                result=ancestor_model(techs[dep],seen+(t.name,))
                if result:return result
        return None
    for name,t in techs.items():
        if not t.path.endswith('_'+code.lower()+'.txt') or not name.startswith(code.lower()+'_'):continue
        if name in starts or name in baseline.FORCE_EXCLUDE or t.doctrine:continue
        if t.year<=1940 and name not in BASELINE_REMOVE:continue
        if not t.has_folder and 'enable_equipments' not in t.body and name not in hidden:continue
        targets=[];electronics=False
        if '/infantry_' in t.path:targets=[choose(t,'I')]
        elif '/artillery_' in t.path:
            targets=[choose(t,'G')]
            if code=='JAP' and 'heavy_anti_air' in name:
                indices=sorted({x.year for n,x in techs.items() if n.startswith('jap_') and '/artillery_' in x.path and 'heavy_anti_air' in n and x.year>1940})
                targets=['G'+str(min(4,indices.index(t.year)+1))]
        elif '/air_techs_' in t.path:
            p=air_route(t);families=['A','W'] if p=='F' else [p]
            for q in families:targets.append(q+str(AIR_MOVES[name]) if name in AIR_MOVES else choose(t,q))
            electronics='jet' in name or any(int(n[1:])>=ELECTRONICS_FROM[code] for n in targets)
        elif '/armor_' in t.path:
            light=any(x in name for x in ('light','scout','combat_car','armoured_car'))
            mobile=any(x in name for x in ('motorised','motorized','mechanized','amphibious'))
            if mobile and code not in NO_MOTOR_BRANCH:targets=[choose(t,'M')]
            elif light or mobile:
                targets=[choose(t,p) for p in ('T','H')]
                if code=='ITA' and light:
                    if 'light' in name:
                        index=int(re.search(r'(\d+)',name.split('light',1)[1])[1]);stage={4:1,5:2,6:3,7:4}.get(index,1)
                    else:stage=1 if t.year<=1942 else 2
                    targets=[p+str(stage) for p in ('T','H')]
                if code=='JAP' and light:
                    stage=1 if t.year<=1942 else 2 if t.year<=1944 else 3
                    targets=[choose(t,'T'),'H'+str(stage)]
            else:
                model=ancestor_model(t)
                if model:
                    p,i=model
                    if name not in models and code not in ('ITA','JAP'):i=max(i,int(choose(t,p)[1:]))
                    targets=[p+str(i)]
                else:targets=[choose(t,'H' if 'heavy' in name or 'super_heavy' in name or (code=='ENG' and 'support' in name) else 'T')]
        for n in targets:
            if name in EARLY or (code=='JAP' and 'heavy_anti_air' in name) or t.year<=int(by[n][2].split('/')[0]):out[n].add(name)
        options=['WAEF_'+code+'_'+n for n in targets]
        if '/air_techs_' in t.path and air_route(t) in german.STRIKE and any(n.endswith('1') for n in targets):
            options+=['WAEF_'+code+'_'+q+'3' for q in german.STRIKE if q!=air_route(t)]
        gates[name]={'any':options,'all':['WAEF_'+code+'_C25']} if electronics else options
    if code=='USA':out['M1'].add('lend_lease_truck')
    for n,t in [('P1','concentrated_industry'),('P2','dispersed_industry')]:out[n].add(t)
    # Early jets can appear before the generic electronics boundary in WA.
    # Their granting focus must still require completed electronics III.
    for r in records:
        if r[0][0] in ('A','W','S','B','R') and any('jet' in n for n in out[r[0]]) and 'C25' not in r[3]:r[3]+=' и C25'
    return out,gates

EXCLUDES={k:list(v) for k,v in german.EXCLUDES.items()}
EXCLUDES['H1']=['T1'];EXCLUDES['W1']=['A1']
LEGACY={}
EXPENSIVE={}

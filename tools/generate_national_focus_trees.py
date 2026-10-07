#!/usr/bin/env python3
"""Generate seven WAEF technology trees from the reviewed plan and pinned WA files.

Usage: python tools/generate_national_focus_trees.py --wa-root /path/to/world-ablaze
No network required. Overrides preserve upstream technology bodies and add only
WEF/EEF research restrictions. Generated manifest is the auditable reward source.
"""
from pathlib import Path
import argparse, json, re
from collections import defaultdict
import generate_1940_tech_baseline as baseline
import german_focus_revision as german
import national_focus_layout as layout
ROOT = Path(__file__).resolve().parents[1]
SCHOOLS = {'GER':'german','SOV':'soviet','USA':'unitedstates','ENG':'british','FRA':'french','ITA':'italian','JAP':'japanese'}
FILENAMES = {'GER':'germany','SOV':'soviet','USA':'unitedstates','ENG':'british','FRA':'french','ITA':'italian','JAP':'japanese'}
START_EXCEPTIONS = {'USA': ['usa_medium_tank_chassis_2','usa_medium_2'], 'ITA':['ita_interceptor_ad_tech_2','ita_fighter_4']}
EXPENSIVE = {'GER':'H1','SOV':'TB2','USA':'TB4','FRA':'TB4','ITA':'TB5','JAP':'TB5'}
EN = {
'C00':'Military Research Organisation','C11':'Industry 1941','C13':'Industry 1943','C15':'Industry 1945',
'C21':'Electronics 1941','C23':'Electronics 1943','C25':'Electronics 1945','C31':'Support Companies 1941','C33':'Support Companies 1943','C35':'Support Companies 1945',
'C41':'Serial Production','C42':'Flexible Production','C51':'Air Reconnaissance','C52':'Army Command','C61':'Assault Support','C62':'Army Logistics','C70':'Operational Planning',
'I1':'Infantry Rearmament','I3':'Infantry Formations 1943','I5':'Infantry Formations 1945','G1':'Fire Support 1941','G3':'Fire Support 1943','G5':'Fire Support 1945','M2':'Motorisation','M4':'Mechanised Formations',
'T1':'Armoured Forces 1941','T2':'Armoured Forces 1942','T3':'Panther Programme','H2':'Heavy Armour Priority','H4':'Heavy Formations 1944',
'A1':'Air Force Modernisation','A3':'Messerschmitt Programme','A4':'Late War Fighters','W2':'Focke Wulf Priority','W4':'Focke Wulf Development','S2':'Ground Attack Aviation','S4':'Armoured Offensive Air Support',
'TA2':'Serial Armoured Programme','TA3':'Mobile Armoured Programme','TA4':'Serial Armour Development','TB2':'Heavy Armoured Programme','TB3':'Advanced Armoured Programme','TB4':'Advanced Armoured Formations','TB5':'Late War Armoured Programme',
'AA2':'Fighter Priority','AA3':'Fighter Priority','AA4':'Late War Fighters','AB2':'Army Air Support Priority','AB3':'Army Air Support Priority','AB4':'Late War Air Support','O2':'National Operational Doctrine'}
EN.update({k:v for k,v in german.EN.items() if k not in EN})
NATIONAL_EN = {
'SOV':{'TA2':'Mass Production of T-34','TA4':'T-34-85 and T-44','TB2':'Guards Heavy Armour','TB4':'IS Breakthrough Formations','AA2':'Frontline Fighter Priority','AB2':'Shturmovik Priority'},
'USA':{'TA2':'Sherman Standardisation','TA4':'Serial Tank Formations','TB2':'Experimental Tanks','TB4':'Pershing Programme','AA3':'Long Range Fighter Cover','AB3':'Army Air Support'},
'ENG':{'TA2':'Cruiser Tanks','TA4':'Cromwell and Comet','TB2':'Infantry Tanks','TB4':'Churchill Infantry Support','AA2':'Spitfire Priority','AB2':'Typhoon Priority'},
'FRA':{'TA2':'Mobile Armoured Formations','TA3':'Medium Tank Development','TB2':'Heavy Armour Programme','TB4':'ARL Heavy Formations','AA3':'Air Interception Priority','AB3':'Multirole Aviation'},
'ITA':{'TA3':'Semovente Fire Support','TA4':'Self Propelled Artillery Development','TB3':'New Medium Tanks','TB5':'Late War Armour','AA3':'Macchi and Fiat Priority','AB3':'Reggiane and Strike Aviation'},
'JAP':{'TA3':'Economical Mobile Armour','TA4':'Mobile Formation Support','TB3':'Anti Tank Armour','TB5':'Late War Tank Formations','AA2':'Army Interceptor Priority','AB2':'Long Range Naval Fighters','AB3':'Long Range Fighter Development'}}
COMMON_MODS = {'C41':('waef_serial_production','industrial_capacity_factory = 0.08\nproduction_factory_efficiency_loss_factor = -0.10','+8% выпуска военных заводов; −10 п.п. сохранения эффективности.','+8% military factory output; −10 percentage points of efficiency retention.'),
'C42':('waef_flexible_production','production_factory_efficiency_loss_factor = 0.15\nproduction_factory_efficiency_gain_factor = 0.10','+15 п.п. сохранения эффективности; +10% прироста эффективности.','+15 percentage points of efficiency retention; +10% efficiency growth.'),
'C51':('waef_air_reconnaissance','air_detection = 0.05','+5% воздушного обнаружения.','+5% air detection.'),
'C52':('waef_army_command','planning_speed = 0.10','+10% скорости планирования.','+10% planning speed.'),
'C61':('waef_assault_support','dig_in_speed_factor = 0.10','+10% скорости окапывания.','+10% entrenchment speed.'),
'C62':('waef_army_logistics','supply_consumption_factor = -0.05','−5% расхода снабжения.','−5% supply consumption.')}

def write(rel,text,bom=False):
    path=ROOT/rel; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding='utf-8-sig' if bom else 'utf-8')

def year(t): return t.year

def is_mobile(name): return any(x in name for x in ('mechanized','motorised','motorized','amphibious','scout','armoured_car'))

def tank_route(code,name):
    n=name[len(code)+1:]
    if code=='GER':return 'H' if 'heavy' in n or 'landkruiser' in n else 'T'
    if code=='SOV':return 'TB' if 'heavy' in n else 'TA'
    if code=='USA':
        return 'TB' if ('heavy' in n or 'modern' in n or re.search(r'^medium_tank_chassis_[45]$',n) or re.search(r'^medium_[45]$',n)) else 'TA'
    if code=='ENG': return 'TB' if 'heavy' in n or 'support' in n else 'TA'
    if code=='FRA': return 'TB' if 'heavy' in n else 'TA'
    if code=='ITA':
        return 'TA' if any(x in n for x in ('light','_td','_spg','assault','_aa')) else 'TB'
    if code=='JAP':
        return 'TB' if 'super_heavy' in n or re.search(r'(?:chassis_|medium_)(?:7|9)(?:_|$)',n) or re.search(r'(?:td_|spg_)(?:7|9)$',n) else 'TA'
    raise ValueError(code)

def air_route(code,name):
    if code=='GER':
        if 'multirole' in name or 'jet_' in name:return 'W'
        if re.search(r'_(?:cv_)?fighter(?:_ad_tech)?_',name):return 'A'
        return 'S'
    if code=='SOV':return 'AA' if any(x in name for x in ('fighter','interceptor')) else 'AB'
    if code=='USA':return 'AA' if ('fighter' in name and 'multirole' not in name and 'cv_' not in name) else 'AB'
    if code=='ENG':return 'AA' if ('fighter' in name and 'multirole' not in name) else 'AB'
    if code=='FRA':return 'AA' if 'interceptor' in name or ('fighter' in name and 'multirole' not in name and 'heavy' not in name) else 'AB'
    if code=='ITA':return 'AA' if ('interceptor' in name or ('fighter' in name and 'multirole' not in name and 'heavy' not in name and 'cv_' not in name)) else 'AB'
    if code=='JAP':return 'AB' if 'cv_fighter' in name else 'AA'


def icon(node):
    if node=='C00':return 'GFX_goal_generic_scientific_exchange'
    if node.startswith(('C1','C4','P')):return 'GFX_goal_generic_construct_civ_factory'
    if node.startswith(('C2','C5')):return 'GFX_goal_generic_scientific_exchange'
    if node.startswith(('T','H','L')):return 'GFX_goal_generic_army_tanks'
    if node.startswith(('A','W','S','B','R','U')):return 'GFX_goal_generic_air_fighter'
    return 'GFX_goal_generic_army_doctrine'

def research_condition(branch):
    if isinstance(branch,dict):
        parts=['has_completed_focus = '+f for f in branch.get('all',[])]
        options=branch.get('any',[])
    else:
        parts=[]
        options=branch if isinstance(branch,list) else [branch] if branch else []
    if options:parts.append('OR = { '+' '.join('has_completed_focus = '+f for f in options)+' }')
    return ' '.join(parts) if parts else 'always = yes'

def main():
    arg=argparse.ArgumentParser();arg.add_argument('--wa-root',type=Path,required=True);args=arg.parse_args()
    wa=args.wa_root
    spec=json.loads((ROOT/'docs/FOCUS_PLAN_v1_1.json').read_text())
    techs={}; sources={}
    for stem in ['industry','electronic_mechanical_engineering','support']+[f'{stem}_{c.lower()}' for c in SCHOOLS for stem in ('infantry','artillery','armor','air_techs')]:
        rel=f'common/technologies/{stem}.txt';raw=(wa/rel).read_text(encoding='utf-8-sig');sources[rel]=raw
        for name,body in baseline.technology_blocks(raw).items():techs[name]=baseline.parse_tech(name,rel,body)
    conditions=baseline.effective_conditions(techs)
    # Only include an explicitly supported DLC variant, preserving conditions inherited
    # from parent technologies (WA has hidden aircraft conversion subtechnologies).
    def grant(ids,indent='            '):
        groups=defaultdict(list)
        for t in sorted(ids):
            for cond in conditions[t]:groups[cond].append(t)
        out=[]
        for (req,neg),names in sorted(groups.items()):
            rows=' '.join(f'{n} = 1' for n in sorted(set(names)))
            if req or neg:
                checks=' '.join([f'has_dlc = "{x}"' for x in req]+[f'NOT = {{ has_dlc = "{x}" }}' for x in neg])
                out.append(indent+f'if = {{ limit = {{ {checks} }} set_technology = {{ {rows} }} }}')
            else:out.append(indent+f'set_technology = {{ {rows} }}')
        return '\n'.join(out)
    locales={'russian':{},'english':{}}
    def loc(key,ru,en):locales['russian'][key]=ru;locales['english'][key]=en
    restrictions={};manifest={'wa_commit':baseline.WA_COMMIT,'plan_version':'1.1','german_revision':'2026-10-08','calendar_gates':False,'schools':{},'research_gates':{},'start_exceptions':START_EXCEPTIONS}
    ideas=[]
    german_jet_rewards=[]
    for c,(ident,mods,ru,en) in COMMON_MODS.items():
        ideas.append(f'    {ident} = {{ picture = generic_research allowed = {{ always = no }} removal_cost = -1 modifier = {{ {mods} }} }}')
        loc(ident,spec['common'][[x[0] for x in spec['common']].index(c)][1],EN[c]);loc(ident+'_desc',ru,en)
    for nation in spec['nations']:
        code=nation['code'];prefix=code.lower();school=SCHOOLS[code]
        records=german.records(spec['common']) if code=='GER' else spec['common']+nation['records']
        if code=='JAP':records=[(r[0],r[1],'1945 / 91',r[3],'Механизация 1945') if r[0]=='M4' else r for r in records]
        by_code={r[0]:r for r in records}
        coordinates=layout.coordinates(records,code)
        packages={r[0]:set() for r in records};route_roots={}
        for node in by_code:
            if re.fullmatch(r'(TA|TB|AA|AB|H|W|S)[2-5]',node):route_roots.setdefault(re.sub(r'\d$','',node),node)
        def first_route(route):return route_roots.get(route)
        def assign(t,candidates):
            # Earliest package at/after source year. No future grants.
            choices=sorted((int(by_code[c][2].split('/')[0]),c) for c in candidates if c in by_code and int(by_code[c][2].split('/')[0])>=t.year)
            if choices:packages[choices[0][1]].add(t.name)
        for name,t in techs.items():
            if t.doctrine or (not t.has_folder and 'enable_equipments' not in t.body) or t.year<=1940 or name in baseline.FORCE_EXCLUDE:continue
            file=Path(t.path).stem
            if file in ('industry','electronic_mechanical_engineering','support'):
                if name in ('concentrated_industry','dispersed_industry','streamlined_line','flexible_line'):continue
                branch={'industry':'C1','electronic_mechanical_engineering':'C2','support':'C3'}[file]
                assign(t,[branch+x for x in ('1','3','5')]);restrictions[name]=(t.year,None);continue
            if not file.endswith('_'+prefix):continue
            branch=None
            if file.startswith('infantry'):
                assign(t,['I1','I3','I5'])
            elif file.startswith('artillery'):assign(t,['G1','G3','G5'])
            elif file.startswith('armor'):
                if is_mobile(name):assign(t,['M2','M4']);continue
                route=tank_route(code,name);branch=first_route(route)
                if t.year==1941 and (route in ('T','TA') or (code=='ITA' and 'heavy' not in name)):
                    assign(t,['T1']);branch=None
                elif code=='GER' and route=='T':assign(t,['T1','T2','T3']);branch=None
                else:assign(t,[n for n in by_code if re.fullmatch(route+r'[2-5]',n)])
            elif file.startswith('air_techs'):
                route=air_route(code,name);branch=first_route(route)
                # The shared first fighter package does not unlock an alternative family.
                base_fighter=(re.search(r'_(?:fighter|interceptor)(?:_ad_tech)?_',name) and 'multirole' not in name and 'jet' not in name and 'cv_' not in name and 'heavy' not in name)
                if t.year==1941 and base_fighter:
                    assign(t,['A1']);branch=None
                elif code=='GER' and route=='A':assign(t,['A1','A3','A4']);branch=None
                else:assign(t,[n for n in by_code if re.fullmatch(route+r'[2-5]',n)])
            restrictions[name]=(t.year, f'WAEF_{code}_{branch}' if branch else None)
        if code=='GER':
            german_packages,german_gates,german_jet_rewards=german.packages(techs,records)
            manifest['german_jet_rewards']=german_jet_rewards
            for node in packages:
                if not node.startswith('C'):packages[node]=german_packages[node]
            for name,options in german_gates.items():restrictions[name]=(techs[name].year,options)
        # Re.2001 is the shared Italian 1941 fighter, not a late route reward.
        if code=='ITA':
            for name in ['ita_fighter_multirole_ad_tech_1','ita_fighter_multirole_1']:
                for ids in packages.values():ids.discard(name)
                packages['A1'].add(name);restrictions[name]=(1941,None)
        # Start exceptions never recur in reward lists.
        for name in START_EXCEPTIONS.get(code,[]):
            assert name in techs,name
            for ids in packages.values():ids.discard(name)
            restrictions.pop(name,None)
        # Attach hidden subtechnologies only when they respect the package source period and route.
        for node,ids in packages.items():
            cutoff=int(by_code[node][2].split('/')[0]);queue=list(ids)
            while queue:
                t=techs[queue.pop()]
                for child in t.sub_technologies:
                    if child not in techs or child in ids or techs[child].year>cutoff or child in baseline.FORCE_EXCLUDE:continue
                    gate=restrictions.get(child)
                    parent_gate=restrictions.get(t.name)
                    if gate and parent_gate and gate[1]!=parent_gate[1]:continue
                    ids.add(child);queue.append(child)
                    if parent_gate:restrictions.setdefault(child,parent_gate)
        if code=='GER':
            german.finish_packages(packages)
        # Symmetric common choices.
        excludes={}
        for a,b in [('C41','C42'),('C51','C52'),('C61','C62')]+([] if code=='GER' else [(first_route('TA'),first_route('TB')),(first_route('AA'),first_route('AB'))]):
            if a and b:excludes[a]=b;excludes[b]=a
        excludes={key:[value] for key,value in excludes.items()}
        if code=='GER':excludes.update(german.EXCLUDES)
        tree=f'WAEF_{code}_TECH_DOCTRINE'
        chunks=[f'# Generated from docs/FOCUS_PLAN_v1_1.json; WA {baseline.WA_COMMIT}.\nfocus_tree = {{\n    id = {tree}\n    country = {{ factor = 0 modifier = {{ add = 200000 has_country_flag = {school}_technologies_tree_flag OR = {{ tag = WEF tag = EEF }} }} }}\n    default = no\n    reset_on_civilwar = no']
        nation_manifest=[]
        for node,title,when,pre,desc in records:
            yr,days=map(int,when.split('/'));fid=f'WAEF_{code}_{node}';x,y=coordinates[node]
            deps=[] if node in ('C00','P1','P2') else pre.split(' и ')
            reward=[];ru_effect=[];en_effect=[]
            if node=='A1' or (code=='GER' and node=='W1'):reward.append('air_experience = 10');ru_effect.append('+10 опыта авиации.');en_effect.append('+10 air experience.')
            if node=='C00':reward=['army_experience = 25','air_experience = 25'];ru_effect=['+25 опыта армии и авиации.'];en_effect=['+25 army and air experience.']
            if node in ['P1','P2']:reward.append('set_technology = { standard_industry = 0 }')
            if node in COMMON_MODS:
                ident,mods,ru,en=COMMON_MODS[node];reward.append('add_ideas = '+ident);ru_effect.append(ru);en_effect.append(en)
            if node=='C70':reward.append('set_country_flag = waef_operations_unlocked');ru_effect.append('Открывает наступательные операции и подготовку оборонительных рубежей.');en_effect.append('Unlocks offensive operations and defensive line preparation.')
            if node=='O2':reward.append(f'set_country_flag = waef_{prefix}_operations_specialisation');ru_effect.append(desc);en_effect.append('Improves the national operational programme; see the decision description.')
            if node==EXPENSIVE.get(code):
                reward.append('waef_start_armament_fatigue = yes');ru_effect.append('Дорогая программа: повторяющаяся миссия повышает усталость на 1 каждые 70 дней.');en_effect.append('Expensive programme: a recurring mission adds 1 fatigue every 70 days.')
            if code=='GER' and node in german.JET_COMPLETIONS:
                reward.append(german.JET_EFFECT+' = yes')
                ru_effect.append('Реактивная техника выдаётся после электроники III и этапа III соответствующей авиационной ветви, в любом порядке завершения.')
                en_effect.append('Jet aircraft are granted after Electronics III and stage III of their aviation route, completed in either order.')
            if code=='GER' and node=='R3':
                en_effect.append('Grants He 277 A-1 (BBA). Ju 132 requires Electronics III; compatible equipment mode is selected automatically.')
            if code=='GER' and node=='R2':
                en_effect.append('Grants the He 177 A-5, Me 264 and Ta 400 strategic package.')
            if code=='GER' and node in ['S3','B3','R3']:
                ru_effect.append('Также выдаёт базовые технологии этапа I двух других ударных авиационных направлений.')
                en_effect.append('Also grants the stage I technologies of the other two strike aviation routes.')
            # Specific family bonuses, scoped to equipment granted by the selected route.
            bonus=None
            if (code,node) in [('SOV','TB4'),('FRA','TB4')]:bonus=('breakthrough',.05)
            if (code,node) in [('USA','TA4'),('FRA','TA3'),('JAP','TA4')]:bonus=('build_cost_ic',-.05)
            if (code,node)==('ITA','TA4'):bonus=('build_cost_ic',-.08)
            if (code,node)==('ITA','TB5'):bonus=('reliability',.05)
            if (code,node)==('USA','M4'):bonus=('reliability',.05)
            if (code,node)==('JAP','I3'):bonus=('build_cost_ic',-.05)
            if bonus:
                family=[n for n in by_code if n.startswith(re.sub(r'\d$','',node))];ids=set().union(*(packages[n] for n in family));equipment=set()
                for tname in ids:
                    for inner in baseline.named_blocks(techs[tname].body,'enable_equipments'):
                        equipment.update(re.findall(r'\b[A-Za-z][A-Za-z0-9_]*\b',inner))
                if code=='JAP' and node=='I3':equipment={e for e in equipment if 'heavy_infantry' in e}
                if equipment:
                    ident=f'waef_{prefix}_{node.lower()}_programme';stat,value=bonus
                    equip=' '.join(f'{e} = {{ instant = yes {stat} = {value} }}' for e in sorted(equipment))
                    ideas.append(f'    {ident} = {{ picture = generic_research allowed = {{ always = no }} removal_cost = -1 equipment_bonus = {{ {equip} }} }}');reward.append('add_ideas = '+ident)
                    label={'build_cost_ic':('Стоимость','Production cost'),'breakthrough':('Прорыв','Breakthrough'),'reliability':('Надёжность','Reliability')}[stat]
                    rus=f'{label[0]} выбранного семейства: {value:+.0%}.';ens=f'{label[1]} of the selected equipment family: {value:+.0%}.'
                    loc(ident,title,(german.EN.get(node,EN[node]) if code=='GER' else NATIONAL_EN.get(code,{}).get(node,EN[node])));loc(ident+'_desc',rus,ens);ru_effect.append(rus);en_effect.append(ens)
            if (code,node)==('SOV','TA4'):
                ident='waef_sov_serial_armour';ideas.append(f'    {ident} = {{ picture = generic_research allowed = {{ always = no }} removal_cost = -1 modifier = {{ production_factory_efficiency_gain_factor = 0.10 }} }}');reward.append('add_ideas = '+ident);loc(ident,'Серийная бронетанковая программа','Serial Armour Programme');loc(ident+'_desc','+10% прироста производственной эффективности.','+10% production efficiency growth.');ru_effect.append('+10% прироста эффективности.');en_effect.append('+10% efficiency growth.')
            grants=grant(packages[node]);rewards='\n'.join('            '+r for r in reward)+ ('\n'+grants if grants else '')
            hidden_links=layout.hidden_links(node,code)
            visible_deps=[dep for dep in deps if dep not in hidden_links]
            availability=' '.join('has_completed_focus = WAEF_'+code+'_'+dep for dep in hidden_links) or 'always = yes'
            rows=[f'    focus = {{\n        id = {fid}\n        icon = {icon(node)}\n        x = {x}\n        y = {y}\n        cost = {days//7}','        available = { '+availability+' }','        cancel_if_invalid = yes','        continue_if_invalid = no']
            rows.extend(f'        prerequisite = {{ focus = WAEF_{code}_{dep} }}' for dep in visible_deps)
            if node in excludes:rows.append('        mutually_exclusive = { '+' '.join(f'focus = WAEF_{code}_{other}' for other in excludes[node])+' }')
            rows.append(f'        completion_reward = {{\n{rewards}\n        }}\n    }}');chunks.append('\n'.join(rows))
            entitle=(german.EN.get(node,EN[node]) if code=='GER' else NATIONAL_EN.get(code,{}).get(node,EN[node]))
            if code=='GER':
                for old,new in [('1941','I'),('1943','II'),('1945','III')]:entitle=entitle.replace(old,new)
            loc(fid,title,entitle)
            rule_ru=f'Длительность: {days} дней. Без календарного ограничения.';rule_en=f'Duration: {days} days. No calendar restriction.'
            if packages[node]:rule_ru+=' '+desc+'. Выдаёт доступные по DLC технологии своего периода.';rule_en+=' Grants period technologies compatible with the enabled DLC.'
            if node in excludes:rule_ru+=' Исключает: '+', '.join(by_code[other][1] for other in excludes[node])+'.';rule_en+=' Mutually exclusive with '+', '.join((german.EN.get(other,EN[other]) if code=='GER' else NATIONAL_EN.get(code,{}).get(other,EN[other])) for other in excludes[node])+'.'
            loc(fid+'_desc',' '.join([rule_ru]+ru_effect),' '.join([rule_en]+en_effect))
            nation_manifest.append({'id':fid,'code':node,'year':yr,'days':days,'prerequisites':[f'WAEF_{code}_{d}' for d in deps],'display_prerequisites':[f'WAEF_{code}_{d}' for d in visible_deps],'availability_requires':[f'WAEF_{code}_{d}' for d in hidden_links],'exclusive':[f'WAEF_{code}_{other}' for other in excludes.get(node,[])],'technologies':sorted(packages[node]),'effects':reward})
        chunks.append('}');write(f'common/national_focus/waef_{FILENAMES[code]}_tech_focus.txt','\n\n'.join(chunks)+'\n')
        loc(tree,nation['title']+': военные разработки',{'GER':'Germany','SOV':'Soviet Union','USA':'United States','ENG':'Britain','FRA':'France','ITA':'Italy','JAP':'Japan'}[code]+': Military Research')
        manifest['schools'][code]=nation_manifest
    # Gate both modern designer and classic equipment technologies. Never affect
    # historical WA countries, never revoke 1940 technologies or captured equipment.
    for rel,raw in sources.items():
        clean=baseline.strip_comments(raw);blocks=baseline.technology_blocks(clean);changes=[]
        for name,(yr,branch) in restrictions.items():
            if techs[name].path!=rel:continue
            for m in re.finditer(r'\b'+re.escape(name)+r'\s*=\s*\{',raw):
                pos=raw.find('{',m.start())+1
                condition=research_condition(branch)
                gate=f'\n        allow = {{ OR = {{ NOT = {{ OR = {{ tag = WEF tag = EEF }} }} AND = {{ {condition} }} }} }}\n'
                existing=re.search(r'\ballow\s*=\s*\{',raw[pos:baseline.matching_brace(raw,pos-1)])
                if existing:
                    pos=pos+existing.end()
                    gate=gate.replace('allow = { OR =', 'OR =').rsplit(' }',1)[0]+'\n'
                changes.append((pos,gate))
            manifest['research_gates'][name]={'year':yr,'requires_focus':branch.get('any',[]) if isinstance(branch,dict) else branch,'requires_all_focus':branch.get('all',[]) if isinstance(branch,dict) else [],'calendar_gate':False}
        if changes:
            for pos,gate in sorted(changes,reverse=True):raw=raw[:pos]+gate+raw[pos:]
        write(rel,raw)
    # Common production-line technologies require their chosen focus.
    raw=(ROOT/'common/technologies/industry.txt').read_text()
    for name,node in [('streamlined_line','C41'),('flexible_line','C42')]:
        t=techs[name];m=re.search(r'\b'+name+r'\s*=\s*\{',raw);pos=raw.find('{',m.start())+1
        allowed=' '.join(f'has_completed_focus = WAEF_{code}_{node}' for code in SCHOOLS)
        gate=f'\n        allow = {{ OR = {{ NOT = {{ OR = {{ tag = WEF tag = EEF }} }} AND = {{ OR = {{ {allowed} }} }} }} }}\n'
        raw=raw[:pos]+gate+raw[pos:]
        manifest['research_gates'][name]={'year':t.year,'choice':node,'calendar_gate':False}
    write('common/technologies/industry.txt',raw)
    write('common/ideas/waef_focus_programmes.txt','ideas = { country = {\n'+'\n'.join(ideas)+'\n} }\n')
    loc('waef_armament_fatigue','Усталость от дорогой программы вооружений','Armament Programme Fatigue')
    loc('waef_armament_fatigue_desc','Каждые 70 дней активная дорогая программа повышает экономическую усталость на 1. Следующие фокусы и смена законов не сбрасывают таймер.','Every 70 days the active expensive programme adds 1 economic fatigue. Further focuses and law changes do not reset this timer.')
    write('common/scripted_effects/waef_focus_effects.txt','''waef_start_armament_fatigue = {
    set_country_flag = waef_expensive_armament_programme
    if = {
        limit = { NOT = { has_active_mission = waef_armament_fatigue } }
        activate_mission = waef_armament_fatigue
    }
}
''')
    jets=['# A repeated call safely keeps the same technologies; either completion order works.',german.JET_EFFECT+' = {']
    for entry in german_jet_rewards:
        checks=' '.join('has_completed_focus = '+f for f in entry['requires_all'])
        checks+=' OR = { '+' '.join('has_completed_focus = '+f for f in entry['requires_any'])+' }'
        jets.append('    if = { limit = { '+checks+' }\n'+grant(entry['technologies'],indent='        ')+'\n    }')
    jets.append('}')
    effects=ROOT/'common/scripted_effects/waef_focus_effects.txt'
    effects.write_text(effects.read_text()+'\n'+'\n'.join(jets)+'\n')
    write('common/decisions/waef_armament_fatigue.txt','''economy_fatigue = {
    waef_armament_fatigue = {
        icon = economy_fatigue
        allowed = { OR = { tag = WEF tag = EEF } }
        activation = { has_country_flag = waef_expensive_armament_programme }
        visible = { has_country_flag = waef_expensive_armament_programme }
        available = { always = no }
        selectable_mission = no
        days_mission_timeout = 70
        is_good = no
        timeout_effect = {
            economy_fatigue_level_up_1 = yes
            if = {
                limit = { has_country_flag = waef_expensive_armament_programme }
                activate_mission = waef_armament_fatigue
            }
        }
    }
}
''')
    # Replace historical WA assimilation grants with the pinned 1940 baseline,
    # and load the correct tree immediately. The old explicit baseline decision is
    # kept solely for compatibility with saves that had already assimilated.
    path=ROOT/'common/decisions/waef_technology_assimilation.txt';text=path.read_text()
    for code,school in SCHOOLS.items():
        marker='waef_assimilate_'+school+'_technologies';start=text.index(marker);m=re.search(r'complete_effect\s*=\s*\{',text[start:]);op=start+m.end()-1;end=baseline.matching_brace(text,op)
        original=text[op+1:end];doctrine=re.search(r'set_grand_doctrine\s*=\s*(\w+)',original)
        extra=grant(START_EXCEPTIONS.get(code,[]))
        body=f'''\n            set_country_flag = {school}_technologies_tree_flag
            set_country_flag = waef_technology_assimilated
            waef_grant_shared_1940_technologies = yes
            waef_grant_{school}_1940_technologies = yes
{extra}
            remove_ideas = improvised_weapons
            add_ideas = mobile_warfare_drive_spirit
            add_ideas = firepower_induction_spirit
            add_ideas = infantry_modernization_spirit
            set_country_flag = waef_1940_technology_baseline_applied
            set_grand_doctrine = {doctrine.group(1)}
            load_focus_tree = {{ tree = WAEF_{code}_TECH_DOCTRINE keep_completed = no }}
            mark_focus_tree_layout_dirty = yes
        '''
        text=text[:op+1]+body+text[end:]
    path.write_text(text)
    for lang,entries in locales.items():
        write(f'localisation/{lang}/waef_national_tech_focus_l_{lang}.yml','l_'+lang+':\n'+'\n'.join(f' {k}:0 "{v.replace(chr(34),chr(39))}"' for k,v in entries.items())+'\n',True)
    # Remove the superseded German-only localisation to avoid duplicate keys.
    for lang in locales:
        p=ROOT/f'localisation/{lang}/waef_germany_tech_focus_l_{lang}.yml'
        if p.exists():p.unlink()
    write('docs/NATIONAL_FOCUS_MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print({c:len(nodes) for c,nodes in manifest['schools'].items()})
    print('Research gates:',len(manifest['research_gates']))

if __name__=='__main__':main()

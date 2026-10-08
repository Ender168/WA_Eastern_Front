#!/usr/bin/env python3
"""Generate initially visible tactical/strategic WAEF operations using WA's timed decision/mission pattern."""
from pathlib import Path
import json,re,argparse,csv
from collections import Counter,defaultdict
from generate_1940_tech_baseline import technology_blocks, matching_brace, named_blocks, strip_comments
ROOT=Path(__file__).resolve().parents[1]
def write(rel,text,bom=False):
 p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8-sig' if bom else 'utf-8')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--wa-root',type=Path,required=True);wa=ap.parse_args().wa_root
 provinces={}
 for row in csv.reader((wa/'map/definition.csv').read_text(encoding='utf-8-sig').splitlines(),delimiter=';'):
  if len(row)>4 and row[0].isdigit():provinces[int(row[0])]=row[4]
 region_of={};rnames={}
 for path in sorted((wa/'map/strategicregions').glob('*.txt')):
  raw=strip_comments(path.read_text(encoding='utf-8-sig'));rid=int(re.search(r'\bid\s*=\s*(\d+)',raw)[1]);rnames[rid]=re.search(r'\bname\s*=\s*"([^"]+)"',raw)[1]
  for p in re.findall(r'\d+',named_blocks(raw,'provinces')[0]):region_of[int(p)]=rid
 states={};regions=defaultdict(list);forts={}
 for path in sorted((ROOT/'history/states').glob('*.txt')):
  raw=strip_comments(path.read_text(encoding='utf-8-sig'))
  if not re.search(r'owner\s*=\s*(WEF|EEF)\b',raw):continue
  sid=int(re.search(r'\bid\s*=\s*(\d+)',raw)[1]);ps=[int(x) for x in re.findall(r'\d+',named_blocks(raw,'provinces')[0]) if provinces.get(int(x))=='land']
  rid=Counter(region_of[p] for p in ps if p in region_of).most_common(1)[0][0];states[sid]=ps;regions[rid].append(sid)
  vps=[int(x.split()[0]) for x in named_blocks(raw,'victory_points') if x.split()]
  forts[sid]=list(dict.fromkeys([p for p in vps+ps if p in ps]))[:3]
 assert len(states)==282,len(states)
 locales={'russian':{},'english':{}}
 def loc(k,ru,en):locales['russian'][k]=ru;locales['english'][k]=en
 loc('waef_operations','Оборонительные рубежи','Defensive Lines')
 loc('waef_operations_desc','Подготовка оборонительных рубежей.','Prepare defensive lines.')
 loc('waef_tactical_operations','Тактические наступления','Tactical Offensives')
 loc('waef_strategic_operations','Стратегические операции','Strategic Operations')
 loc('waef_tactical_operations_desc','Бонус действует в выбранном стейте с минимум 7 сухопутными провинциями. Подготовка: 7 дней, усталость +2% сразу. Наступление: 14 дней, +5% атаки. Каждые 10 дней наступления: +1% усталости. Полный захват цели завершает миссию и возвращает усталость подготовки.','The bonus applies in the selected state with at least 7 land provinces. Preparation: 7 days and +2% fatigue immediately. Offensive: 14 days and +5% attack. Every 10 offensive days: +1% fatigue. Full conquest completes the mission and refunds preparation fatigue.')
 loc('waef_strategic_operations_desc','Бонус действует во всех игровых стейтах выбранного воздушного региона. Для запуска противник должен контролировать больше половины его сухопутных провинций. Подготовка: 30 дней, усталость +5% сразу. Наступление: 60 дней, +5% атаки и +10% восстановления организации. Каждые 10 дней наступления: +1% усталости. Полный захват целей завершает миссию и возвращает усталость подготовки.','The bonus applies in every playable state of the selected air region. The opponent must control more than half its land provinces at launch. Preparation: 30 days and +5% fatigue immediately. Offensive: 60 days, +5% attack and +10% organisation recovery. Every 10 offensive days: +1% fatigue. Full conquest completes the mission and refunds preparation fatigue.')
 loc('waef_local_offensive','[FROM.GetName]','[FROM.GetName]')
 loc('waef_local_offensive_desc','Подготовка: 7 дней.','Preparation: 7 days.')
 loc('waef_local_cost_tt','£command_power §Y25§! £pol_power §Y25§!','£command_power §Y25§! £pol_power §Y25§!')
 loc('waef_regional_cost_tt','£command_power §Y50§! £pol_power §Y50§!','£command_power §Y50§! £pol_power §Y50§!')
 for key,amount in [('waef_local_cost_tt',25),('waef_regional_cost_tt',50)]:
  loc(key+'_blocked',f'£command_power §R{amount}§! £pol_power §R{amount}§!',f'£command_power §R{amount}§! £pol_power §R{amount}§!')
  loc(key+'_tooltip',f'£command_power §Y{amount}§! £pol_power §Y{amount}§!',f'£command_power §Y{amount}§! £pol_power §Y{amount}§!')
 loc('waef_fort_cost_tt','25 политвласти; с французским оперативным фокусом: 15.','25 political power; 15 with the French operational focus.')
 allowed='allowed = { OR = { tag = WEF tag = EEF } }'
 root_avail='NOT = { has_country_flag = waef_operation_in_progress }'
 targets=' '.join(str(s) for s in sorted(states))
 tactical_targets=' '.join(str(s) for s,ps in sorted(states.items()) if len(ps)>=7)
 prep=[];triggers=[]
 # Use exact province control, including split states, in either peace or war.
 def enemy_check(ps,minimum=1):
  choices=[]
  for tag,enemy in [('WEF','EEF'),('EEF','WEF')]:
   choices.append(f'AND = {{ tag = {tag} {enemy} = {{ count_triggers = {{ amount = {minimum} '+' '.join(f'controls_province = {pid}' for pid in ps)+' } } }')
  return 'OR = { '+' '.join(choices)+' }'
 for sid,ps in sorted(states.items()):
  triggers.append(f'waef_enemy_in_state_{sid} = {{ {enemy_check(ps)} }}')
 tactical_state_check='OR = { '+' '.join(f'AND = {{ state = {sid} ROOT = {{ waef_enemy_in_state_{sid} = yes }} }}' for sid,ps in sorted(states.items()) if len(ps)>=7)+' }'
 prep.append(f'''    waef_local_offensive = {{
        icon = generic_operation {allowed}
        state_target = yes targets = {{ {tactical_targets} }} on_map_mode = map_and_decisions_view
        target_root_trigger = {{ {root_avail} }}
        target_trigger = {{ FROM = {{ {tactical_state_check} any_neighbor_state = {{ is_controlled_by = ROOT }} }} }}
        visible = {{ always = yes }} available = {{ {root_avail} }}
        custom_cost_trigger = {{ command_power > 24 has_political_power > 24 }}
        custom_cost_text = waef_local_cost_tt fire_only_once = no
        complete_effect = {{
            set_country_flag = waef_operation_in_progress set_country_flag = waef_operation_local
            clear_array = waef_operation_states
            FROM = {{ ROOT = {{ add_to_array = {{ waef_operation_states = PREV }} }} }}
            add_command_power = -25 add_political_power = -25
            waef_charge_local_preparation = yes activate_mission = waef_local_preparation
        }}
        ai_will_do = {{ base = 0 }}
    }}''')
 names_by_region=json.loads((ROOT/'docs/OPERATION_REGION_NAMES.json').read_text())
 for rid,sids in sorted(regions.items()):
  ps=sorted(p for p,r in region_of.items() if r==rid and provinces.get(p)=='land')
  triggers.append(f'waef_enemy_majority_region_{rid} = {{ {enemy_check(ps,len(ps)//2+1)} }}')
  key=f'waef_regional_offensive_{rid}'
  loc(key,names_by_region[str(rid)]['russian'],names_by_region[str(rid)]['english'])
  loc(key+'_desc','Подготовка: 30 дней.','Preparation: 30 days.')
  add='\n'.join(f'            {sid} = {{ ROOT = {{ add_to_array = {{ waef_operation_states = PREV }} }} }}' for sid in sorted(sids))
  prep.append(f'''    {key} = {{
        icon = generic_operation {allowed}
        visible = {{ always = yes }}
        available = {{ {root_avail} waef_enemy_majority_region_{rid} = yes }}
        custom_cost_trigger = {{ command_power > 49 has_political_power > 49 }}
        custom_cost_text = waef_regional_cost_tt fire_only_once = no
        complete_effect = {{
            set_country_flag = waef_operation_in_progress set_country_flag = waef_operation_regional
            clear_array = waef_operation_states
{add}
            add_command_power = -50 add_political_power = -50
            waef_charge_regional_preparation = yes activate_mission = waef_regional_preparation
        }}
        ai_will_do = {{ base = 0 }}
    }}''')
 for scale,days in [('local',7),('regional',30)]:
  key=f'waef_{scale}_preparation'
  loc(key,'Подготовка наступления','Offensive Preparation');loc(key+'_desc','Подготовка выбранной операции.','Prepare the selected operation.')
  prep.append(f'''    {key} = {{
        icon = generic_operation {allowed}
        activation = {{ always = no }} selectable_mission = no
        visible = {{ has_active_mission = {key} }} available = {{ always = no }}
        days_mission_timeout = {days} is_good = yes
        timeout_effect = {{
            if = {{ limit = {{ has_country_flag = waef_operation_{scale} }}
                if = {{ limit = {{ waef_operation_full_control = yes }} waef_win_operation = yes }}
                else = {{ waef_activate_{scale}_offensive = yes }}
            }}
        }}
    }}''')
 for scale,days in [('local',14),('regional',60)]:
  key=f'waef_{scale}_offensive_{days}';fatigue=f'waef_{scale}_operation_fatigue'
  loc(key,'Наступление','Offensive');loc(key+'_desc','Захватите все целевые провинции до истечения срока.','Capture every target province before the deadline.')
  loc(fatigue,'Усталость наступления','Offensive Fatigue')
  loc(fatigue+'_desc','Каждые 10 дней: +1% усталости. Полный захват целей прекращает начисление.','Every 10 days: +1% fatigue. Full conquest stops further charges.')
  prep.append(f'''    {key} = {{
        icon = generic_operation {allowed}
        activation = {{ always = no }} selectable_mission = no
        visible = {{ has_active_mission = {key} }}
        available = {{ has_country_flag = waef_operation_in_progress waef_operation_full_control = yes }}
        days_mission_timeout = {days} is_good = yes
        complete_effect = {{ waef_win_operation = yes }}
        timeout_effect = {{
            if = {{ limit = {{ has_country_flag = waef_operation_{scale} }}
                if = {{ limit = {{ waef_operation_full_control = yes }} waef_win_operation = yes }}
                else = {{
                    while_loop_effect = {{ limit = {{ check_variable = {{ waef_operation_fatigue_ticks < {days//10} }} }} waef_charge_offensive_fatigue = yes }}
                    waef_cleanup_operation = yes
                }}
            }}
        }}
    }}
    {fatigue} = {{
        icon = economy_fatigue {allowed}
        activation = {{ always = no }} selectable_mission = no
        visible = {{ has_active_mission = {fatigue} }} available = {{ always = no }}
        days_mission_timeout = 10 is_good = no
        timeout_effect = {{
            if = {{ limit = {{ has_country_flag = waef_operation_active has_country_flag = waef_operation_{scale} }}
                if = {{ limit = {{ waef_operation_full_control = yes }} waef_win_operation = yes }}
                else = {{ waef_charge_offensive_fatigue = yes activate_mission = {fatigue} }}
            }}
        }}
    }}''')
 # Fort projects use real civilian factories while the timed decision is running.
 # Set the selected provinces to level 2 only when below level 2, without reducing
 # any existing higher level forts. The province list is deterministic and reviewed.
 for variant,days in [('standard',21),('british',14)]:
  key='waef_prepare_defensive_line_'+variant
  school='has_country_flag = waef_eng_operations_specialisation' if variant=='british' else 'NOT = { has_country_flag = waef_eng_operations_specialisation }'
  fort_effect='\n'.join(f'                if = {{ limit = {{ state = {sid} }} '+ ' '.join(f'set_building_level = {{ type = bunker level = 2 province = {{ id = {p} level < 2 }} }}' for p in ps)+' }' for sid,ps in sorted(forts.items()))
  loc(key,'Оборонительный рубеж: [FROM.GetName]','Defensive Line: [FROM.GetName]')
  loc(key+'_desc',f'Работы: {days} дней, используют две гражданские фабрики. Цена: 25 политвласти (15 после французского оперативного фокуса), усталость +2. До трёх заранее выбранных сухопутных провинций получают укрепления уровня 2. Уже более сильные укрепления сохраняются. Потеря полного контроля отменяет работы без возврата усталости. Повторное строительство этого рубежа недоступно.',f'Works take {days} days and use two civilian factories. Cost: 25 political power (15 after the French operational focus), +2 fatigue. Up to three predefined land provinces receive level 2 forts. Existing higher forts are preserved. Losing full control cancels works without refunding fatigue. This defensive line cannot be repeated.')
  prep.append(f'''    {key} = {{
        icon = generic_defence {allowed}
        state_target = yes targets = {{ {targets} }} on_map_mode = map_and_decisions_view
        target_root_trigger = {{ has_country_flag = waef_operations_unlocked {school} NOT = {{ has_country_flag = waef_fortification_in_progress }} }}
        target_trigger = {{ FROM = {{ is_fully_controlled_by = ROOT NOT = {{ has_state_flag = waef_defensive_line_completed }} }} }}
        visible = {{ has_country_flag = waef_operations_unlocked {school} }}
        available = {{ NOT = {{ has_country_flag = waef_fortification_in_progress }} }}
        custom_cost_trigger = {{ OR = {{ AND = {{ has_country_flag = waef_fra_operations_specialisation has_political_power > 14 }} AND = {{ NOT = {{ has_country_flag = waef_fra_operations_specialisation }} has_political_power > 24 }} }} }}
        custom_cost_text = waef_fort_cost_tt
        days_remove = {days} fire_only_once = no
        modifier = {{ civilian_factory_use = 2 }}
        complete_effect = {{ set_country_flag = waef_fortification_in_progress economy_fatigue_level_up_2 = yes
            if = {{ limit = {{ has_country_flag = waef_fra_operations_specialisation }} add_political_power = -15 }} else = {{ add_political_power = -25 }}
        }}
        cancel_trigger = {{ FROM = {{ NOT = {{ is_fully_controlled_by = ROOT }} }} }}
        cancel_effect = {{ clr_country_flag = waef_fortification_in_progress }}
        remove_effect = {{
            FROM = {{
                if = {{ limit = {{ is_fully_controlled_by = ROOT }}
{fort_effect}
                    set_state_flag = waef_defensive_line_completed
                }}
            }}
            clr_country_flag = waef_fortification_in_progress
        }}
        ai_will_do = {{ base = 0 }}
    }}''')
 groups={'waef_tactical_operations':[], 'waef_strategic_operations':[], 'waef_operations':[]}
 for entry in prep:
  key=re.search(r'waef_\w+',entry)[0]
  category='waef_tactical_operations' if key.startswith('waef_local') else 'waef_strategic_operations' if key.startswith('waef_regional') else 'waef_operations'
  groups[category].append(entry)
 write('common/decisions/waef_focus_operations.txt','\n'.join(key+' = {\n'+'\n'.join(entries)+'\n}' for key,entries in groups.items())+'\n')
 write('common/decisions/categories/waef_focus_operations.txt','waef_tactical_operations = { icon = decision_category_military_operation allowed = { OR = { tag = WEF tag = EEF } } visible = { always = yes } }\nwaef_strategic_operations = { icon = decision_category_military_operation allowed = { OR = { tag = WEF tag = EEF } } visible = { always = yes } }\nwaef_operations = { icon = decision_category_military_operation allowed = { OR = { tag = WEF tag = EEF } } visible = { has_country_flag = waef_operations_unlocked } }\n')
 triggers.append('''waef_operation_full_control = {
    check_variable = { waef_operation_states^num > 0 }
    all_of_scopes = { array = waef_operation_states is_fully_controlled_by = ROOT }
}''')
 write('common/scripted_triggers/waef_focus_operations.txt','\n'.join(triggers)+'\n')
 effects=[];modifiers=[]
 for scale,days,charge in [('local',14,2),('regional',60,5)]:
  effects.append(f'''waef_charge_{scale}_preparation = {{
    set_variable = {{ waef_preparation_refund = economic_fatigue }}
    economy_fatigue_level_up_{charge} = yes
    multiply_variable = {{ waef_preparation_refund = -1 }}
    add_to_variable = {{ waef_preparation_refund = economic_fatigue }}
    set_variable = {{ waef_operation_fatigue_ticks = 0 }}
}}''')
  bonus='army_attack_factor = 0.05'+(' local_org_regain = 0.10' if scale=='regional' else '')
  choices=[]
  for tag in ['WEF','EEF']:
   key=f'waef_{tag.lower()}_offensive_{scale}_modifier'
   loc(key,'Наступление','Offensive');loc(key+'_desc','Временный бонус выбранной операции.','Temporary bonus for the selected operation.')
   modifiers.append(f'{key} = {{ enable = {{ always = yes }} icon = GFX_modifiers_generic_military_plans {bonus} }}')
   choices.append(f'if = {{ limit = {{ ROOT = {{ tag = {tag} }} }} add_dynamic_modifier = {{ modifier = {key} scope = ROOT days = {days} }} }}')
  effects.append(f'waef_activate_{scale}_offensive = {{ set_country_flag = waef_operation_active for_each_scope_loop = {{ array = waef_operation_states '+ ' '.join(choices)+f' }} activate_mission = waef_{scale}_offensive_{days} activate_mission = waef_{scale}_operation_fatigue }}')
 cleanup=[]
 for tag in ['WEF','EEF']:
  cleanup.append(f'if = {{ limit = {{ ROOT = {{ tag = {tag} }} }} '+ ' '.join(f'remove_dynamic_modifier = {{ modifier = waef_{tag.lower()}_offensive_{scale}_modifier }}' for scale in ['local','regional'])+' }')
 missions=['waef_local_preparation','waef_regional_preparation','waef_local_offensive_14','waef_regional_offensive_60','waef_local_operation_fatigue','waef_regional_operation_fatigue']
 effects.append('waef_cleanup_operation = { clr_country_flag = waef_operation_in_progress clr_country_flag = waef_operation_active clr_country_flag = waef_operation_local clr_country_flag = waef_operation_regional '+' '.join('remove_mission = '+m for m in missions)+' for_each_scope_loop = { array = waef_operation_states '+' '.join(cleanup)+' } clear_array = waef_operation_states clear_variable = waef_preparation_refund clear_variable = waef_operation_fatigue_ticks }')
 effects.append('waef_charge_offensive_fatigue = { economy_fatigue_level_up_1 = yes add_to_variable = { waef_operation_fatigue_ticks = 1 } }')
 effects.append('waef_win_operation = { while_loop_effect = { limit = { check_variable = { waef_preparation_refund > 0 } } economy_fatigue_level_down_1 = yes subtract_from_variable = { waef_preparation_refund = 1 } } waef_cleanup_operation = yes }')
 effects.append('waef_check_operation_victory = { if = { limit = { has_country_flag = waef_operation_in_progress waef_operation_full_control = yes } waef_win_operation = yes } }')
 write('common/scripted_effects/waef_focus_operations.txt','\n'.join(effects)+'\n')
 write('common/dynamic_modifiers/waef_focus_operations.txt','\n'.join(modifiers)+'\n')
 for lang,entries in locales.items():write(f'localisation/{lang}/waef_focus_operations_l_{lang}.yml','l_'+lang+':\n'+'\n'.join(f' {k}:0 "{v}"' for k,v in entries.items())+'\n',True)
 write('docs/OPERATION_TARGETS.json',json.dumps({'state_regions':{r:sorted(ss) for r,ss in regions.items()},'tactical_states':[s for s,ps in sorted(states.items()) if len(ps)>=7],'fort_provinces':forts},indent=2)+'\n')
 print('Operation regions:',len(regions),'eligible tactical states:',len(tactical_targets.split()))
if __name__=='__main__':main()

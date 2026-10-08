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
 loc('waef_tactical_operations','Тактические наступления','Tactical Offensives')
 loc('waef_strategic_operations','Стратегические операции','Strategic Operations')
 loc('waef_tactical_operations_desc','Операции в отдельных стейтах. Раздел доступен с начала игры; запуск требует войны.','Operations in individual states. Available from the start of the game; launching requires war.')
 loc('waef_strategic_operations_desc','Операции в воздушных регионах. Раздел доступен с начала игры; запуск требует войны.','Operations in air regions. Available from the start of the game; launching requires war.')
 loc('waef_operations_desc','Подготовка оборонительных рубежей после изучения оперативного фокуса.','Prepare defensive lines after completing the operations focus.')
 loc('waef_operation_targets_tt','Требуется полный контроль всех провинций целевых стейтов. Полный контроль союзной страны также засчитывается.','Every province of each target state must be under full friendly control. A fully controlling allied country also qualifies.')
 loc('waef_local_offensive','Локальное наступление: [FROM.GetName]','Local Offensive: [FROM.GetName]')
 loc('waef_local_offensive_desc','Цель: один соседний вражеский стейт. Подготовка: 7 дней, наступление: 21 день, либо 28 после японского оперативного фокуса. Цена: 25 политвласти и 25 командного ресурса, усталость +2. Во время наступления +5% атаки только в целевом стейте. Успех: усталость −1, поддержка войны +1 п.п.; провал: усталость +1, поддержка войны −2 п.п. Повтор по этому стейту закрыт на 365 дней. Итальянский оперативный фокус снижает политическую цену до 20.','Target: one adjacent enemy state. Preparation: 7 days. Offensive: 21 days, or 28 after the Japanese operational focus. Cost: 25 political power, 25 command power and +2 fatigue. +5% attack in the target state during the offensive. Success: −1 fatigue, +1 percentage point war support. Failure: +1 fatigue, −2 percentage points war support. Each target has a 365-day cooldown. The Italian operational focus reduces political cost to 20.')
 loc('waef_local_cost_tt','25 политвласти и 25 командного ресурса; с итальянским оперативным фокусом: 20 политвласти.','25 political power and 25 command power; 20 political power with the Italian operational focus.')
 loc('waef_regional_cost_tt','50 политвласти и 50 командного ресурса; с американским оперативным фокусом: 40 командного ресурса.','50 political power and 50 command power; 40 command power with the American operational focus.')
 loc('waef_fort_cost_tt','25 политвласти; с французским оперативным фокусом: 15.','25 political power; 15 with the French operational focus.')
 cooldown='OR = { AND = { ROOT = { tag = WEF } has_state_flag = waef_wef_operation_cooldown } AND = { ROOT = { tag = EEF } has_state_flag = waef_eef_operation_cooldown } }'
 stamp='if = { limit = { ROOT = { tag = WEF } } set_state_flag = { flag = waef_wef_operation_cooldown days = 365 } } else = { set_state_flag = { flag = waef_eef_operation_cooldown days = 365 } }'
 frontline='controller = { has_war_with = ROOT } any_neighbor_state = { is_fully_controlled_by = ROOT }'
 allowed='allowed = { OR = { tag = WEF tag = EEF } }'
 root_avail='has_war = yes NOT = { has_country_flag = waef_operation_in_progress }'
 targets=' '.join(str(s) for s in sorted(states))
 prep=[]
 prep.append(f'''    waef_local_offensive = {{
        icon = generic_operation {allowed}
        state_target = yes targets = {{ {targets} }} on_map_mode = map_and_decisions_view
        target_root_trigger = {{ {root_avail} }}
        target_trigger = {{ FROM = {{ {frontline} NOT = {{ {cooldown} }} }} }}
        visible = {{ {root_avail} }}
        available = {{ {root_avail} }}
        custom_cost_trigger = {{ command_power > 24 OR = {{ AND = {{ has_country_flag = waef_ita_operations_specialisation has_political_power > 19 }} AND = {{ NOT = {{ has_country_flag = waef_ita_operations_specialisation }} has_political_power > 24 }} }} }}
        custom_cost_text = waef_local_cost_tt
        days_remove = 7 fire_only_once = no
        complete_effect = {{
            set_country_flag = waef_operation_in_progress
            clear_array = waef_operation_states
            FROM = {{ ROOT = {{ add_to_array = {{ waef_operation_states = PREV }} }} {stamp} }}
            add_command_power = -25
            if = {{ limit = {{ has_country_flag = waef_ita_operations_specialisation }} add_political_power = -20 }} else = {{ add_political_power = -25 }}
            economy_fatigue_level_up_2 = yes
        }}
        remove_effect = {{
            if = {{ limit = {{ has_war = yes }}
                waef_activate_local_offensive = yes
                if = {{ limit = {{ has_country_flag = waef_jap_operations_specialisation }} activate_mission = waef_local_offensive_28 }} else = {{ activate_mission = waef_local_offensive_21 }}
            }} else = {{ waef_fail_local_offensive = yes }}
        }}
        ai_will_do = {{ base = 0 }}
    }}''')
 for rid,sids in sorted(regions.items()):
  for variant,days in [('standard',14),('german',7)]:
   key=f'waef_regional_offensive_{rid}_{variant}'
   school='has_country_flag = waef_ger_operations_specialisation' if variant=='german' else 'NOT = { has_country_flag = waef_ger_operations_specialisation }'
   state_list=' '.join(str(s) for s in sorted(sids));enemy=' '.join(f'{s} = {{ {frontline} }}' for s in sids)
   nocool=' '.join(f'{s} = {{ NOT = {{ {cooldown} }} }}' for s in sids)
   add='\n'.join(f'            {s} = {{ ROOT = {{ add_to_array = {{ waef_operation_states = PREV }} }} {stamp} }}' for s in sids)
   names_by_region=json.loads((ROOT/'docs/OPERATION_REGION_NAMES.json').read_text())
   loc('WAEF_OPERATION_REGION_'+str(rid),names_by_region[str(rid)]['russian'],names_by_region[str(rid)]['english'])
   loc(key,'Региональная операция: $WAEF_OPERATION_REGION_'+str(rid)+'$','Regional Operation: $WAEF_OPERATION_REGION_'+str(rid)+'$')
   names=', '.join('$STATE_'+str(s)+'$' for s in sorted(sids))
   loc(key+'_desc',f'Целевые стейты: {names}. Район составлен по большинству сухопутных провинций воздушного региона; стейты не разрезаются. Подготовка {days} дней; наступление 45 дней, либо 52 после советского оперативного фокуса. Цена: 50 политвласти, 50 командного ресурса (40 с американским оперативным фокусом), усталость +5. Бонус в районе: +5% атаки и +10% восстановления организации. Успех: усталость −2, поддержка войны +3 п.п. Провал: усталость +3, поддержка войны −5 п.п. Целевые стейты блокируются для повторных операций на 365 дней.',f'Target states: {names}. States are assigned by majority of land provinces in the air region and are never split. Preparation: {days} days. Offensive: 45 days, or 52 with the Soviet operational focus. Cost: 50 political power, 50 command power (40 with the American operational focus), +5 fatigue. Regional bonus: +5% attack and +10% organisation recovery. Success: −2 fatigue, +3 percentage points war support. Failure: +3 fatigue, −5 percentage points war support. Target states have a 365-day operation cooldown.')
   prep.append(f'''    {key} = {{
        icon = generic_operation {allowed}
        visible = {{ {root_avail} {school} OR = {{ {enemy} }} }}
        available = {{ {root_avail} {school} {nocool} OR = {{ {enemy} }} }}
        custom_cost_trigger = {{ has_political_power > 49 OR = {{ AND = {{ has_country_flag = waef_usa_operations_specialisation command_power > 39 }} AND = {{ NOT = {{ has_country_flag = waef_usa_operations_specialisation }} command_power > 49 }} }} }}
        custom_cost_text = waef_regional_cost_tt
        days_remove = {days} fire_only_once = no
        highlight_states = {{ highlight_state_targets = {{ state = {min(sids)} }} }}
        complete_effect = {{
            set_country_flag = waef_operation_in_progress clear_array = waef_operation_states
{add}
            add_political_power = -50
            if = {{ limit = {{ has_country_flag = waef_usa_operations_specialisation }} add_command_power = -40 }} else = {{ add_command_power = -50 }}
            economy_fatigue_level_up_5 = yes
        }}
        remove_effect = {{
            if = {{ limit = {{ has_war = yes }}
                waef_activate_regional_offensive = yes
                if = {{ limit = {{ has_country_flag = waef_sov_operations_specialisation }} activate_mission = waef_regional_offensive_52 }} else = {{ activate_mission = waef_regional_offensive_45 }}
            }} else = {{ waef_fail_regional_offensive = yes }}
        }}
        ai_will_do = {{ base = 0 }}
    }}''')
 # Completion succeeds only under full control. A split state cannot be won merely
 # by occupying its capital. Both operations share a single in-progress flag/array.
 for scale,days,refund,ws in [('local',21,1,.01),('local',28,1,.01),('regional',45,2,.03),('regional',52,2,.03)]:
  key=f'waef_{scale}_offensive_{days}'
  loc(key,'Наступление: '+('один стейт' if scale=='local' else 'регион'),'Offensive: '+('One State' if scale=='local' else 'Region'))
  loc(key+'_desc',f'Срок выполнения: {days} дней. Цели зафиксированы при начале подготовки. Успех требует полного дружественного контроля. По истечении срока начисляется цена провала.',f'Deadline: {days} days. Targets are fixed when preparation begins. Success requires full friendly control. Missing the deadline incurs the failure penalty.')
  prep.append(f'''    {key} = {{
        icon = generic_operation {allowed}
        activation = {{ always = no }} selectable_mission = no
        visible = {{ has_active_mission = {key} }}
        available = {{ has_country_flag = waef_operation_in_progress waef_operation_full_control = yes }}
        days_mission_timeout = {days} is_good = yes
        cancel_trigger = {{ NOT = {{ has_war = yes }} }}
        cancel_effect = {{ waef_fail_{scale}_offensive = yes }}
        complete_effect = {{ economy_fatigue_level_down_{refund} = yes add_war_support = {ws} waef_cleanup_operation = yes }}
        timeout_effect = {{
            if = {{ limit = {{ waef_operation_full_control = yes }} economy_fatigue_level_down_{refund} = yes add_war_support = {ws} waef_cleanup_operation = yes }}
            else = {{ waef_fail_{scale}_offensive = yes }}
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
 for kind in ['tactical','strategic']:
  key='waef_'+kind+'_operations_peacetime'
  loc(key,'Подготовка наступлений: требуется война','Offensive Planning: War Required')
  loc(key+'_desc','Раздел доступен с начала игры. Наступательные операции можно запускать после начала войны.','This category is available from the start of the game. Offensive operations can be launched once the war begins.')
  groups['waef_'+kind+'_operations'].append(f'    {key} = {{ icon = generic_operation {allowed} visible = {{ has_war = no }} available = {{ always = no }} ai_will_do = {{ base = 0 }} }}')
 for entry in prep:
  key=re.search(r'waef_\w+',entry)[0]
  category='waef_tactical_operations' if key.startswith('waef_local_offensive') else 'waef_strategic_operations' if key.startswith('waef_regional_offensive') else 'waef_operations'
  groups[category].append(entry)
 write('common/decisions/waef_focus_operations.txt','\n'.join(key+' = {\n'+'\n'.join(entries)+'\n}' for key,entries in groups.items())+'\n')
 write('common/decisions/categories/waef_focus_operations.txt','waef_tactical_operations = { icon = decision_category_military_operation allowed = { OR = { tag = WEF tag = EEF } } visible = { always = yes } }\nwaef_strategic_operations = { icon = decision_category_military_operation allowed = { OR = { tag = WEF tag = EEF } } visible = { always = yes } }\nwaef_operations = { icon = decision_category_military_operation allowed = { OR = { tag = WEF tag = EEF } } visible = { has_country_flag = waef_operations_unlocked } }\n')
 write('common/scripted_triggers/waef_focus_operations.txt','''waef_operation_full_control = {
    check_variable = { waef_operation_states^num > 0 }
    all_of_scopes = {
        array = waef_operation_states
        OR = {
            is_fully_controlled_by = ROOT
            AND = { is_fully_controlled_by = controller controller = { is_in_faction_with = ROOT } }
        }
    }
}
''')
 effects=[];modifiers=[]
 for scale in ['local','regional']:
  bonus='army_attack_factor = 0.05'+(' local_org_regain = 0.10' if scale=='regional' else '')
  choices=[]
  for tag in ['WEF','EEF']:
   key=f'waef_{tag.lower()}_offensive_{scale}_modifier'
   loc(key,('Локальное' if scale=='local' else 'Региональное')+' наступление: '+('Западный фронт' if tag=='WEF' else 'Восточный фронт'),('Local' if scale=='local' else 'Regional')+' Offensive: '+tag)
   loc(key+'_desc',('+5% атаки' if scale=='local' else '+5% атаки и +10% восстановления организации')+' для страны, проводящей операцию, только в целевых стейтах.',('+5% attack' if scale=='local' else '+5% attack and +10% organisation recovery')+' for the operating country in target states only.')
   modifiers.append(f'{key} = {{ enable = {{ always = yes }} icon = GFX_modifiers_generic_military_plans {bonus} }}')
   choices.append(f'if = {{ limit = {{ ROOT = {{ tag = {tag} }} }} add_dynamic_modifier = {{ modifier = {key} scope = ROOT }} }}')
  effects.append(f'waef_activate_{scale}_offensive = {{ for_each_scope_loop = {{ array = waef_operation_states '+ ' '.join(choices)+' } }')
 cleanup=[]
 for tag in ['WEF','EEF']:
  cleanup.append(f'if = {{ limit = {{ ROOT = {{ tag = {tag} }} }} '+ ' '.join(f'remove_dynamic_modifier = {{ modifier = waef_{tag.lower()}_offensive_{scale}_modifier }}' for scale in ['local','regional'])+' }')
 effects.append('waef_cleanup_operation = { for_each_scope_loop = { array = waef_operation_states '+' '.join(cleanup)+' } clear_array = waef_operation_states clr_country_flag = waef_operation_in_progress }')
 effects.append('waef_fail_local_offensive = { economy_fatigue_level_up_1 = yes add_war_support = -0.02 waef_cleanup_operation = yes }')
 effects.append('waef_fail_regional_offensive = { economy_fatigue_level_up_3 = yes add_war_support = -0.05 waef_cleanup_operation = yes }')
 write('common/scripted_effects/waef_focus_operations.txt','\n'.join(effects)+'\n')
 write('common/dynamic_modifiers/waef_focus_operations.txt','\n'.join(modifiers)+'\n')
 for lang,entries in locales.items():write(f'localisation/{lang}/waef_focus_operations_l_{lang}.yml','l_'+lang+':\n'+'\n'.join(f' {k}:0 "{v}"' for k,v in entries.items())+'\n',True)
 write('docs/OPERATION_TARGETS.json',json.dumps({'state_regions':{r:sorted(ss) for r,ss in regions.items()},'fort_provinces':forts},indent=2)+'\n')
 print('Operation regions:',len(regions),'states:',len(states),'fort provinces:',sum(map(len,forts.values())))
if __name__=='__main__':main()

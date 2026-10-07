"""Render the reviewed reward-name catalogue; no upstream installation needed."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    names=json.loads((ROOT/'docs/TECHNOLOGY_LOCALISATION_CATALOGUE.json').read_text())
    manifest=json.loads((ROOT/'docs/NATIONAL_FOCUS_MANIFEST.json').read_text())
    required={t for rows in manifest['schools'].values() for row in rows for t in row['technologies']}
    required|={t for entry in manifest.get('german_jet_rewards',[]) for t in entry['technologies']}
    assert not required-names.keys(),required-names.keys()
    for lang in ['english','russian']:
        lines=['l_'+lang+':']
        for key in sorted(required):
            value=names[key][lang].replace('"',"'")
            assert value and '$' not in value,(key,value)
            lines.append(f' {key}:0 "{value}"')
        path=ROOT/'localisation'/'replace'/f'zz_waef_focus_technologies_l_{lang}.yml'
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('\n'.join(lines)+'\n',encoding='utf-8-sig')
if __name__=='__main__':main()

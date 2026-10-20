"""Current40-source documentary check; check-gapfill.py stays historical at39."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[3]
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
BASE = 'ece403e'
REL = ROOT.relative_to(WORKTREE).as_posix()
PYTHON = MAIN / '.thesis-build/venv/Scripts/python.exe'
VALIDATOR = Path('C:/Users/Soroush/.codex/skills/thesis-literature-synthesis/scripts/validate_literature.py')

def read(p): return p.read_text(encoding='utf-8')
def obj(p): return json.loads(read(p))
def old(name): return subprocess.check_output(['git','show',f'{BASE}:{REL}/{name}'],cwd=WORKTREE)
def oldobj(name): return json.loads(old(name))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    manifest = obj(ROOT/'source-manifest.json')
    sources = manifest['sources']
    accepted = oldobj('source-manifest.json')['sources']
    assert len(accepted) == 39 and sources[:39] == accepted
    assert len(sources) == len({s['id'] for s in sources}) == 40
    assert sum(s['qualifies_direct_floor'] for s in sources) == 23
    evidence = obj(ROOT/'evidence-records.json')
    assert evidence[:39] == oldobj('evidence-records.json') and evidence == sources
    for s in accepted:
        assert read(ROOT/s['card_path']).replace('\r\n','\n') == old(s['card_path']).decode('utf-8').replace('\r\n','\n'),s['id']
    rows = lambda text: [l for l in text.splitlines() if re.match(r'^\| \[',l)]
    current_rows = rows(read(ROOT/'settings-table.md'))
    assert len(current_rows) == 40 and current_rows[:39] == rows(old('settings-table.md').decode('utf-8'))
    for name in ['search-events.jsonl','check-gapfill.py','gapfill-checks.json','gapfill-literature-response.json']:
        assert read(ROOT/name).replace('\r\n','\n') == old(name).decode('utf-8').replace('\r\n','\n'),name
    cov = obj(ROOT/'coverage-register.json')
    oldcov = oldobj('coverage-register.json')
    assert cov[:len(oldcov)] == oldcov and len(cov) == len(oldcov)+4
    assert manifest['coverage_register'] == cov
    ran = sources[-1]
    assert ran['id'] == 'ran'
    artifacts = [ran]+ran['additional_inspected_artifacts']
    for a in artifacts:
        p=Path(a['cache_path'])
        assert p.stat().st_size == a['bytes'] and sha(p) == a['sha256']
        assert sha(Path(a['derived_text_path'])) == a['derived_text_sha256']
    assert sha(Path(cov[-3]['cache_path'])) == cov[-3]['sha256']
    assert sha(Path(cov[-1]['cache_path'])) == cov[-1]['sha256']
    for field in ['mechanism','models','strength_noise','sampler_steps','prompt','resolution','image_counts','metrics','numeric_baseline_results','limits']:
        assert ran[field] and ran[field] in read(ROOT/'cards/ran.md'),field
    assert read(ROOT/'references.bib').startswith(old('references.bib').decode('utf-8').rstrip())
    assert read(ROOT/'references.bib').count('@article{T1_ran,') == 1
    floor=obj(ROOT/'floor-audit.json')
    assert (floor['unique_v2_sources'],floor['qualifying_direct_sources'],floor['settings_table_rows']) == (40,23,40)
    assert len(floor['qualifying_sources']) == 23 and len(floor['supplemental_v2']) == 17
    assert (floor['successful_discovery_events'],floor['distinct_substantive_intents']) == (34,24)
    args=[str(PYTHON),str(VALIDATOR),'validate',str(ROOT/'ran-gap-literature-response.json'),'--evidence-root',str(MAIN),'--request-id','T1-stage1b-ran-gap']
    v=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
    validation=json.loads(v.stdout)
    assert v.returncode == 0 and validation == {'valid':True,'errors':[],'warnings':[]}
    synth=ROOT/'skill-synthesis-ran-gap-20261020'
    assert len(list((synth/'papers').glob('*.json'))) == 1
    assert len(read(synth/'evidence-ledger.jsonl').splitlines()) == 2
    diff=subprocess.run(['git','-c','core.safecrlf=false','diff','--check','--',REL],cwd=WORKTREE,capture_output=True,text=True)
    assert diff.returncode == 0,diff.stdout+diff.stderr
    result={'date':'2026-10-20','scope':'T1 author documentary self-check; not independent review','base_commit':BASE,'passed':True,'accepted39_sources_evidence_cards_settings_unchanged':True,'accepted_search_events_and_historical_gapfill_artifacts_unchanged':True,'current_v2_sources':40,'direct_sources':23,'adjunct_sources':17,'settings_rows':40,'search_floor':{'successful_queries':34,'distinct_intents':24,'categories':3},'new_primary_derived_hash_matches':8,'screened_lead_hash_matches':2,'new_scope_exclusions':2,'new_inaccessible_removal_lead':1,'git_diff_check':'PASS','skill_validation':validation,'skill_synthesis':{'directory':synth.name,'papers':1,'evidence_entries':2},'validation_command':args,'limitations':['No F5/SDXL or project outcomes.','RAN quality-reference conflict, WAM-specific n/checkpoint and extractor path unresolved.','MSAT full PDF not retained; proceedings method/evaluation read via web extraction only; appendix not inspected.','Chen2025 subscription preview cannot support V2; ICDMW2025 access gap remains.']}
    (ROOT/'ran-gap-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':main()

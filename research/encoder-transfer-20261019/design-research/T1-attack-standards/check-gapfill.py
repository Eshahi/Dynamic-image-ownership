"""Read-only documentary checks for the five T1 late-lead additions; no model execution."""
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[3]
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
BASE = 'a54377f'
REL = ROOT.relative_to(WORKTREE).as_posix()
PYTHON = MAIN / '.thesis-build/venv/Scripts/python.exe'
VALIDATOR = Path('C:/Users/Soroush/.codex/skills/thesis-literature-synthesis/scripts/validate_literature.py')

def read(path): return path.read_text(encoding='utf-8')
def obj(path): return json.loads(read(path))
def baseline(name):
    return subprocess.check_output(['git', 'show', f'{BASE}:{REL}/{name}'], cwd=WORKTREE)
def baseline_json(name): return json.loads(baseline(name))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest = obj(ROOT/'source-manifest.json')
    sources = manifest['sources']
    old = baseline_json('source-manifest.json')['sources']
    assert len(old) == 34 and sources[:34] == old, 'Accepted source dictionaries changed'
    evidence = obj(ROOT/'evidence-records.json')
    assert evidence[:34] == baseline_json('evidence-records.json'), 'Accepted evidence changed'
    assert evidence == sources
    added = sources[34:]
    assert [s['id'] for s in added] == ['brushoff', 'taxonomy', 'peccvai', 'edit-survival', 'boundary']
    assert len({s['id'] for s in sources}) == len(sources) == 39
    assert sum(bool(s['qualifies_direct_floor']) for s in sources) == 22
    for s in old:
        assert read(ROOT/s['card_path']).replace('\r\n','\n') == baseline(s['card_path']).decode('utf-8').replace('\r\n','\n'), s['id']
    old_rows = [l for l in baseline('settings-table.md').decode('utf-8').splitlines() if re.match(r'^\| \[', l)]
    rows = [l for l in read(ROOT/'settings-table.md').splitlines() if re.match(r'^\| \[', l)]
    assert len(rows) == 39 and rows[:34] == old_rows, 'Accepted settings rows changed'
    for s in added:
        assert Path(s['cache_path']).stat().st_size == s['bytes']
        assert sha(Path(s['cache_path'])) == s['sha256']
        assert sha(Path(s['derived_text_path'])) == s['derived_text_sha256']
        assert (ROOT/s['card_path']).is_file()
        assert read(ROOT/'references.bib').count('@misc{'+s['citation_key']+',') == 1
        for field in ['mechanism','models','strength_noise','sampler_steps','prompt','resolution','image_counts','metrics','numeric_baseline_results','limits']:
            assert s[field] and s[field] in read(ROOT/s['card_path']), (s['id'],field)
    events = [json.loads(l) for l in read(ROOT/'search-events.jsonl').splitlines() if l]
    old_events = [json.loads(l) for l in baseline('search-events.jsonl').decode('utf-8').splitlines() if l]
    assert len(old_events) == 34 and events[:34] == old_events
    successful = [e for e in events if e.get('success') and e.get('counted_discovery')]
    intents = {e['distinct_intent'] for e in successful}
    categories = collections.Counter(e['channel'] for e in successful)
    assert len(events) == 39 and len(successful) == 34 and len(intents) == 24
    assert categories == {'web_search':30,'OpenAlex':2,'official_repository_search':2}, categories
    audit = obj(ROOT/'floor-audit.json')
    assert audit['unique_v2_sources'] == len(sources)
    assert audit['qualifying_direct_sources'] == sum(s['qualifies_direct_floor'] for s in sources)
    assert len(audit['qualifying_sources']) == 22 and len(audit['supplemental_v2']) == 17
    assert audit['query_events'] == len(events) and audit['successful_discovery_events'] == len(successful)
    assert audit['distinct_substantive_intents'] == len(intents)
    assert audit['successful_categories'] == categories
    cov = obj(ROOT/'coverage-register.json')
    assert cov[:-5] == baseline_json('coverage-register.json')
    assert manifest['coverage_register'] == cov
    assert {s['id'] for s in cov[-5:]} == {s['id'] for s in added}
    for s in added:
        assert next(c for c in cov if c['id']==s['id'])['sha256'] == s['sha256']
    p = next(s for s in added if s['id']=='peccvai')
    assert '/html/' in p['canonical_url'] and '/papers/' in p['url'] and p['url'].endswith('.pdf')
    assert '35 BCH parity bits + 4 header bits' in added[0]['models']
    for path in [ROOT/s['card_path'] for s in added]+[ROOT/'settings-table.md',ROOT/'synthesis.md',ROOT/'gapfill-literature-response.json']:
        assert 'CVPR2026/abs/' not in read(path), path
        assert 'TrustMark-Q61+BCH39' not in read(path), path
    validator_args = [str(PYTHON),str(VALIDATOR),'validate',str(ROOT/'gapfill-literature-response.json'),'--evidence-root',str(MAIN),'--request-id','T1-stage1b-late-gapfill']
    result = subprocess.run(validator_args,capture_output=True,text=True,encoding='utf-8')
    validation = json.loads(result.stdout)
    assert result.returncode == 0 and validation['valid'] and not validation['errors'] and not validation['warnings']
    synth = ROOT/'skill-synthesis-gapfill-final-20261020'
    assert len(list((synth/'papers').glob('*.json'))) == 5
    assert len(read(synth/'evidence-ledger.jsonl').splitlines()) == 10
    assert 'CVPR2026/abs/' not in read(synth/'references.bib')
    diff = subprocess.run(['git','-c','core.safecrlf=false','diff','--check','--',REL],cwd=WORKTREE,capture_output=True,text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    checks = {
        'date':'2026-10-20','base_commit':BASE,'scope':'T1 late-lead documentary self-check; not an independent milestone review',
        'passed':True,'git_diff_check':'PASS','original_34_source_records_unchanged':True,'original_34_evidence_records_unchanged':True,
        'original_34_cards_unchanged':True,'original_34_settings_rows_unchanged':True,'original_34_query_events_unchanged':True,
        'unique_v2_sources':39,'direct_sources':22,'adjunct_sources':17,'settings_rows':39,
        'query_events':len(events),'successful_queries':len(successful),'distinct_intents':len(intents),'successful_categories':dict(categories),
        'new_primary_and_derived_sha256_matches':10,'new_cards': [s['card_path'] for s in added],
        'skill_response':{'papers':5,'evidence_entries':10,'validation':validation},
        'skill_synthesis':{'path':synth.name,'papers':5,'evidence_entries':10,'result':'PASS; command separately executed successfully with no warnings'},
        'validation_command':validator_args,
        'synthesis_command':[str(PYTHON),str(VALIDATOR),'synthesize',str(ROOT/'gapfill-literature-response.json'),'--evidence-root',str(MAIN),'--out',str(synth)],
        'limitations':['No experiments run; external numbers remain source claims.','Boundary SDXL rate aggregation unexplained; no integer success counts reconstructed.','CVF live re-open 403; cached official PDF independently read.','Boundary venue shell did not verify accepted-list title.','Original inaccessible ICDMW 2025 lead remains uncounted.']
    }
    (ROOT/'gapfill-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(checks,ensure_ascii=False,indent=2))

if __name__ == '__main__': main()

"""Read-only author package checks; writes only its documentary check report."""
import csv, hashlib, json, re, subprocess, sys
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parent
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
sources=read(root/'source-manifest.json');queries=read(root/'query-manifest.json')
response=read(root/'literature-response.json')
checks=[]
for source in sources:
    for pathkey,hashkey in [('artifact','sha256'),('venue_artifact','venue_sha256'),('derived_text','derived_text_sha256')]:
        path=Path(source[pathkey]);assert sha(path)==source[hashkey],path
        checks.append(str(path))
    card=(root/source['card']).read_text(encoding='utf-8')
    for required in ['V2','Method locator:','Evaluation locator:','Image counts','Metrics:','FPR operating point:','Quality practice:','Baselines:','[agent-inference]']:
        assert required in card,(source['id'],required)
    assert read(root/'cards'/f"{source['id']}.json")['paper_id']=='t7_'+source['id']
    if source.get('supplement'):
        supp=source['supplement']
        for pathkey,hashkey in [('cache_path','sha256'),('derived_text','derived_text_sha256')]:
            path=Path(supp[pathkey]);assert sha(path)==supp[hashkey];checks.append(str(path))
for query in queries:
    path=Path(query['cache_path']);assert sha(path)==query['sha256'];checks.append(str(path))
assert len(set(s['id'] for s in sources))==len(sources)==15
assert len(set(q['query'] for q in queries))==len(queries)==12
assert len(set(q['category'] for q in queries))==4
rows=list(csv.DictReader((root/'evaluation-practice.csv').open(encoding='utf-8',newline='')))
assert len(rows)==15
assert {r['id'] for r in rows}=={s['id'] for s in sources}
for row in rows:
    assert all(row[field] for field in ['image_counts','metrics','fpr','quality_practice','baselines','evaluation_locator'])
for field in ['paper_id','citation_key','canonical_url','title']:
    assert len(set(p[field] for p in response['papers']))==15
bib=(root/'references.bib').read_text(encoding='utf-8')
assert set(re.findall(r'@inproceedings\{([^,]+),',bib))=={p['citation_key'] for p in response['papers']}
assert bib.count('booktitle =')==15
assert '## what we might still have missed' in (root/'search-log.md').read_text(encoding='utf-8')
synthesis=(root/'synthesis.md').read_text(encoding='utf-8')
assert len(re.findall(r'^\| Table \d ',synthesis,re.M))==8
assert len(re.findall(r'^\| Figure \d ',synthesis,re.M))==7
assert 'source-majority ROC' not in synthesis
assert 'maximum TPR, then the fewest false positives, then the highest threshold' in synthesis
assert 'Only three primary paired exact sign tests' in read(root/'floor-audit.json')['inferential_tests']
validator=Path('C:/Users/Soroush/.codex/skills/thesis-literature-synthesis/scripts/validate_literature.py')
cache=Path(sources[0]['artifact']).parent
args=[sys.executable,str(validator),'validate',str(root/'literature-response.json'),'--evidence-root',str(cache),'--request-id','encoder_transfer_t7_stage1b']
run=subprocess.run(args,capture_output=True,text=True,check=True)
validation=json.loads(run.stdout);assert validation==dict(valid=True,errors=[],warnings=[])
report=dict(date='2026-10-20',status='author_checks_pass',distinct_sources=15,own_v2_cards=15,evaluation_rows=15,evidence_entries=len(response['evidence']),queries=12,query_categories=4,venue_year_counts=dict(Counter(f"{s['venue']} {s['year']}" for s in sources)),hash_comparisons=len(checks),distinct_hashed_files=len(set(checks)),tables=8,figures=7,skill_validation=validation,skill_command=args,literature_response_sha256=sha(root/'literature-response.json'),final_skill_export='skill-synthesis-final-1b',final_export_papers=len(list((root/'skill-synthesis-final-1b'/'papers').glob('*.json'))),scope='Documentary author checks; not independent review, scientific reproduction or outcome evidence.')
assert report['final_export_papers']==15
(root/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))

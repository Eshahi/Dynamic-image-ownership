"""Check package structure and provenance; no science or upstream code execution."""
from pathlib import Path
import csv,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    methods=json.loads((ROOT/'methods.json').read_text(encoding='utf-8'))
    manifest=json.loads((ROOT/'deepening-manifest.json').read_text(encoding='utf-8'))
    events=[json.loads(s) for s in (ROOT/'search-events.jsonl').read_text(encoding='utf-8').splitlines()]
    checks=[]
    def check(name,result):
        checks.append({'check':name,'passed':bool(result)})
        if not result: raise AssertionError(name)
    check('24 distinct post-hoc method identities',len(methods)==24 and len({m['name'] for m in methods})==24 and len({m['arxiv'] for m in methods})==24)
    required=('authors','title','year','venue','doi','canonical_url','stable_id','citekey','accessed','evidence_level','sections','mechanism','native','release','regeneration','cost','implication','ranking','card_path','primary_text_sha256')
    check('all 24 records include metadata and required evidence fields',all(all(k in m for k in required) and all(m[k] for k in required if k!='doi') for m in methods))
    check('all 24 current method-cache hashes match',all(sha(Path(s['cache_path']))==s['sha256'] for s in manifest['method_sources']))
    check('all 24 cards exist and declare V2 with source and evaluation',all((ROOT/m['card_path']).is_file() and all(t in (ROOT/m['card_path']).read_text(encoding='utf-8') for t in ('**V2**','## Published evaluation and regeneration conditions','## Native operating point','## Cost and uncertainty','SHA-256:')) for m in methods))
    with (ROOT/'method-comparison.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
    check('CSV has same 24 ordered identities as JSON',[r['name'] for r in rows]==[m['name'] for m in methods])
    bib=(ROOT/'references.bib').read_text(encoding='utf-8')
    keys=re.findall(r'@\w+\{([^,]+),',bib)
    check('25 unique bibliography records, 24 versioned methods plus final TrustMark',len(keys)==25 and len(set(keys))==25 and all(m['citekey'] in keys for m in methods))
    web={e['query'] for e in events if e['channel']=='web_search'}
    official=[e for e in events if e['channel']=='official_repository' and e.get('status')==200 and '/search/repositories?' in e.get('url','')]
    alex=[e for e in events if e['channel']=='openalex' and e.get('status')==200]
    check('22 conservatively counted distinct discovery queries across 3 successful categories',len(web)==18 and len({e['query'] for e in official})==3 and len(alex)==1 and manifest['counted_discovery']['total']==22)
    check('exact gap heading in synthesis and search log',all('## what we might still have missed' in (ROOT/n).read_text(encoding='utf-8') for n in ('synthesis.md','search-log.md')))
    check('OmniGuard full title propagated',all('OmniGuard: Hybrid Manipulation Localization via Augmented Versatile Deep Image Watermarking' in (ROOT/n).read_text(encoding='utf-8') for n in ('cards/OmniGuard.md','references.bib','methods.json','method-comparison.csv')))
    check('ChunkySeal release correction present',all('chunkyseal/checkpoint.pth' in (ROOT/n).read_text(encoding='utf-8') for n in ('cards/Chunky-Seal.md','methods.json')))
    check('SimuFreeMark licensing limitation corrected','No released implementation or checkpoint license was established; faithful implementation would be new work.' in (ROOT/'cards/SimuFreeMark.md').read_text(encoding='utf-8'))
    mismatch=[e for e in manifest['event_cache_checks'] if not e['matches_recorded']]
    check('two overwritten historical HTML receipts are explicit, no unreported missing artifacts',len(mismatch)==2 and all(e['exists'] and e.get('cache_state','').startswith('earlier HTML snapshot overwritten') for e in mismatch))
    # Validate only topic-internal relative Markdown links. Legacy repo-relative references are separately documented.
    broken=[]
    for p in ROOT.rglob('*.md'):
        for ref in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
            if '://' in ref or ref.startswith(('#','/')): continue
            if not (p.parent/ref.split('#')[0]).exists(): broken.append((p.name,ref))
    check('all Markdown relative links resolve',not broken)
    bad=[]
    for p in ROOT.rglob('*'):
        if p.is_file() and p.suffix in ('.md','.json','.jsonl','.py','.bib','.csv'):
            for n,line in enumerate(p.read_text(encoding='utf-8-sig').splitlines(),1):
                if line.rstrip()!=line: bad.append((p.name,n))
    check('owned text has no trailing whitespace',not bad)
    out={'author_self_check_not_independent_review':True,'date':'2026-10-20','method_count':24,'counted_discovery_queries':22,'successful_discovery_categories':3,'query_events':len(events),'bibliography_records':25,'current_method_hash_matches':24,'event_cache_records':len(manifest['event_cache_checks']),'event_cache_hash_matches':len(manifest['event_cache_checks'])-len(mismatch),'historical_overwritten_html_receipts':len(mismatch),'checks':checks}
    (ROOT/'floor-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()

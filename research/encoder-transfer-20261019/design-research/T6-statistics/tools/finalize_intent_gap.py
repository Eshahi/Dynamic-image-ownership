"""Document discovery intent coverage without changing the accepted analytical work."""
import hashlib
import json
from pathlib import Path

TOPIC = Path(__file__).resolve().parents[1]
CACHE = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T6-1b-intent-gap')
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, obj): path.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

before = read(CACHE/'preservation-before.json')
original = read(CACHE/'before/query-manifest.json')
new = read(TOPIC/'discovery-receipts-intent-gap.json')
assert len(new)==4 and all(r['status']==200 and r['result_count']==6 for r in new)
# Six deliberately broad historical intent groups. The former literal-query
# wording is preserved in cache; it is explicitly corrected in current prose.
groups = [
    ('I01','Beta-binomial latent heterogeneity / ICC',[1,5]),
    ('I02','Missing binary calls or clusters and selection sensitivity',[2,4,8]),
    ('I03','Exact binomial intervals and sample-size precision',[3,6]),
    ('I04','Dependence in aggregate benchmark uncertainty',[7,12]),
    ('I05','Correlated seed-majority aggregation',[9]),
    ('I06','Paired significance and multiplicity control',[11]),
    ('I07','Joint paired-method law for a fixed superiority-margin route',[13]),
    ('I08','Intersection of positive-success and zero-event safety gates',[14]),
    ('I09','Selection induced by achieved-quality matching / common support',[15]),
    ('I10','Runtime-induced cluster completion under a shared compute cutoff',[16]),
]
mapping = [dict(intent_id=i, intent=label, query_numbers=nums) for i,label,nums in groups]
manifest = dict(original)
manifest.update(distinct_queries=16, successful_query_events=16, substantive_intents_conservative=10,
                intent_mapping=mapping, uncredited_overlap_queries=[10],
                counting_rule='Merge backend variants, missingness variants and broad overlap; discovery count is not a source count.',
                queries=original['queries']+new)
write(TOPIC/'query-manifest.json',manifest)

reasons = {
 'paired-joint-route':[
  'Potential joint-binary construction lead; not read in full and not used to amend the finite-law route grid.',
  'Mixed binary/continuous copula thesis; indirect lead, not a paired-margin decision analysis.',
  'Recent joint-event forecasting lead; time-series setting differs from fixed source-paired decisions.',
  'Longitudinal copula dissertation; indirect lead, not current analytical evidence.',
  'Broad binary forecasting dissertation; low design specificity.',
  'Same title and DOI as rank 5; duplicate metadata record, no additional source credit.'],
 'composite-safety':[
  'Co-primary endpoint lead; fallback testing is outside the frozen all-gates route.',
  'Decision-path testing lead; multiplicity testing differs from the literal zero-event safety gate.',
  'Recent binary efficacy/safety selection lead; utility optimization differs from the fixed intersection rule.',
  'Recent continuous co-primary sequential-design thesis; no sequential sample-size change is proposed.',
  'Correlated binary co-primary design lead; clinical platform setting differs from this fixed development study.',
  'Clinical treatment review; not a statistical design method relevant to the gate.'],
 'quality-selection':[
  'Limited-sample propensity matching lead; not directly achieved-distortion post-processing selection.',
  'General matching-method review lead; full text not inspected for post-treatment conditioning.',
  'Lexical use of Caliper in LLM causal reasoning; not matching-caliper evidence.',
  'Recent medical-data sampling lead; not achieved-distortion matching on processed image arms.',
  'Education matching application; remote from the finite-grid quality question.',
  'Recent matching guidance lead; common-support terminology is relevant, transfer to distortion remains unverified.'],
 'budget-censoring':[
  'Runtime-model evaluation lead; full text not read for cutoff treatment.',
  'Preprint/version of the runtime-prediction title at rank 1; related version, no independent-source credit.',
  'Algorithm-configuration/cutoff lead; adaptive optimization is outside the frozen timing-only reduction rule.',
  'Budget-limited selection lead; title-only metadata (abstract absent), relevance unverified.',
  'Warmstarting configuration lead; optimization differs from informative completion of a fixed roster.',
  'Same title and DOI as rank 5; duplicate metadata, no additional source credit.'],
}
screen = []
for r in new:
    path = Path(r['path'])
    assert sha(path)==r['sha256'] and path.stat().st_size==r['bytes']
    works = read(path)['results']
    for rank,(work,reason) in enumerate(zip(works,reasons[r['id']]),1):
        screen.append(dict(query_id=r['id'], rank=rank, openalex_id=work['id'], title=work['display_name'],
                           year=work['publication_year'], doi=work['doi'],
                           inspection='OpenAlex title and supplied abstract metadata only; primary text unread',
                           disposition='discovery-only; excluded from V2 evidence and all scientific claims', reason=reason))
write(TOPIC/'intent-gap-screening.json',screen)

lines=['# T6 discovery-intent gap audit','',
 'Date: 2026-10-20 UTC. Bounded response to design-review-2 B3; parent acceptance and independent reviewer closure remain pending.',
 '', '## Reconciled counts', '',
 'The historical 12 successful query strings met the literal string floor but overstated independent search intent. They are now conservatively merged to six intents. Four new, actually executed OpenAlex discoveries add four distinct design questions. Total: 16 successful query strings, 10 substantive intents, three existing categories (5 arXiv API, 8 OpenAlex, 3 web). Direct retrievals, backend duplicates and the old broad-overlap query #10 earn no extra intent credit.',
 '', '| Intent | Design question | Query numbers |','|---|---|---|']
for i,label,nums in groups: lines.append(f'| {i} | {label} | '+', '.join(map(str,nums))+' |')
lines += ['', '## Distinctness boundaries', '',
 'I07 asks for the joint mass required to calculate a fixed finite-margin decision probability. I06 asks how paired hypothesis tests and multiplicity behave; they are different mathematical outputs. I08 asks for the probability of the intersection of a positive-count event with a zero-negative event; it is distinct from across-method paired margins and within-positive-seed ICC. I09 asks what conditioning on an achieved processing variable does to the comparison population; it is not an interval or missing-call model.',
 '', 'I10 concerns an execution-induced selection mechanism: a shared wall-clock budget, source order and source-dependent runtime determine which entire clusters finish. I02 concerns missing calls/clusters conditional on an otherwise specified observation roster, with missingness laws and fixed denominators. Although both can produce absent data, the discovery questions differ in the causal selection mechanism and the design control being assessed. We deliberately merge all three old missingness queries (#2, #4, #8) into I02 rather than counting wording variants. I10 does not add a new missingness model or claimed guarantee to the retained analysis.',
 '', '## Exact new searches and receipts', '',
 'Each request has its exact URL, method, request headers and UTC time in MAIN cache. Full response bytes, response headers, final URL, HTTP status, UTC receipt time, byte length and SHA-256 are retained. Six ranked metadata records per response were screened individually in intent-gap-screening.json. Duplicate records/versions are flagged. No lead becomes a V2 source merely by being returned.',
 '', '| Query | Exact search text | UTC receipt | Raw SHA-256 |','|---|---|---|---|']
for r in new: lines.append(f"| {r['id']} | `{r['query']}` | {r['retrieved_utc']} | `{r['sha256']}` |")
lines += ['', '## Evidence boundary and decision', '',
 'All 24 ranked records remain primary-text unread discovery leads, including recent 2025–2026 results. Their titles/metadata motivate possible future reading; they support no empirical number, method claim, design amendment or absence claim. Several results are indirect clinical/forecasting/algorithm-configuration analogues or plainly irrelevant lexical matches. The targeted quality-selection query did not establish a direct finite-grid distortion study. No source was added to satisfy a numeric floor.',
 '', 'The accepted scientific evidence remains eight V2 papers plus five official references. All 15 analytic tables (5,154 rows), planning-table-v2.json and its nine check groups, source-manifest.json, cards, references and historical receipts remain byte-identical. The n=60 recommendation, route and thresholds remain unchanged. No new scientific evidence requiring a design amendment was established by this metadata-only addendum.',
 '', '## Preservation and limitations', '',
 'Before edits, all pre-existing topic files were copied byte-for-byte to MAIN cache/T6-1b-intent-gap/before and indexed by size and SHA-256 in preservation-before.json. Current old query objects remain equal to the original first 12 objects. The current summaries explicitly supersede their old overstatement; historical raw bytes and receipts remain available. query-gap-checks.json records mechanical validation.',
 '', 'Search breadth is still not exhaustive. These four focused searches did not produce newly inspected primary evidence. Exact runtime-selection laws, arbitrary safety/positive dependence and post-processing collider effects remain bounded limitations, not solved problems. Future claims from any lead require primary method-and-evaluation inspection, an own V2 card and the literature-skill validation workflow before integration.', '']
(TOPIC/'query-gap-audit.md').write_text('\n'.join(lines),encoding='utf-8')

search=(CACHE/'before/search-log.md').read_text(encoding='utf-8')
search=search.replace('Twelve distinct substantive discovery queries across three categories (5 arXiv API, 4 OpenAlex, 3 web)',
                      'Sixteen successful discovery query strings across three categories (5 arXiv API, 8 OpenAlex, 3 web), conservatively ten substantive intents after merging overlaps')
marker='\n## Selection and reading'
addition='\n'.join(f"| {j} | {r['category']} | `{r['query']}` |" for j,r in enumerate(new,13))
search=search.replace(marker,addition+'\n\nIntent counts and 24 metadata-only lead screenings: `query-gap-audit.md` and `intent-gap-screening.json`. The four additional searches do not add scientific source credit. Historical 12-query records/bytes are preserved in MAIN cache.\n'+marker)
(TOPIC/'search-log.md').write_text(search,encoding='utf-8')
synthesis=(CACHE/'before/synthesis.md').read_text(encoding='utf-8')
synthesis=synthesis.replace('Twelve substantive discovery queries span arXiv API, OpenAlex and web.',
 'Sixteen successful query strings span arXiv API, OpenAlex and web; conservative merging yields ten substantive intents. The four intent-gap searches and their 24 metadata-only leads add no scientific source credit; see query-gap-audit.md. Historical receipts and the analytical package remain unchanged.')
(TOPIC/'synthesis.md').write_text(synthesis,encoding='utf-8')
floor=read(CACHE/'before/floor-audit.json')
floor.update(discovery_queries=16, substantive_intents_conservative=10, discovery_only_ranked_leads=24,
             added_v2_sources=0, query_gap_audit='query-gap-audit.md', status='intent-gap addendum completed; parent acceptance and independent closure pending')
write(TOPIC/'floor-audit.json',floor)
(TOPIC/'PROGRESS.md').write_text('# T6 intent-gap progress\n\n2026-10-20 UTC: Completed four focused, successful OpenAlex discovery requests and screened all 24 returned ranked metadata leads. The current totals are 16 successful query strings / 10 conservative intents / 3 categories. Eight V2 papers, five official references, 15 tables / 5,154 rows / nine check groups and n=60 are unchanged. All pre-existing bytes were archived before editing; old query records and analytical/source/history bytes were checked. No source-level claim or V2 credit is based on the new metadata. Parent acceptance and same-reviewer closure are pending. No server, GPU, weights, real images, outcomes or held-out material were used.\n',encoding='utf-8')

# Mechanical validation of preserved evidence and exact counts. No analytical
# rerun is necessary or permitted by this bounded discovery addendum.
mutable={'query-manifest.json','search-log.md','synthesis.md','floor-audit.json'}
unchanged=[]
for rel,record in before.items():
    saved=Path(record['copy'])
    assert saved.stat().st_size==record['bytes'] and sha(saved)==record['sha256'], rel
    if rel not in mutable:
        assert sha(TOPIC/rel)==record['sha256'], rel
        unchanged.append(rel)
assert read(TOPIC/'query-manifest.json')['queries'][:12]==original['queries']
assert len({r['query'] for r in manifest['queries']})==16
assert len({r['category'] for r in manifest['queries']})==3
assert len(mapping)==10 and sorted(n for g in mapping for n in g['query_numbers'])==[n for n in range(1,17) if n!=10]
assert len(screen)==24
for r in original['queries']:
    p=Path(r.get('path',r.get('response_path')))
    assert sha(p)==r.get('sha256',r.get('response_sha256')), p
plan=read(TOPIC/'planning-table-v2.json')
assert len(plan['tables'])==15 and sum(t['rows'] for t in plan['tables'].values())==5154 and len(plan['checks'])==9
checks=dict(status='PASS mechanical checks; not independent acceptance', successful_queries=16,
            conservative_intents=10, categories=3, new_successful_requests=4, screened_ranked_leads=24,
            old_query_records_preserved=12, archived_preexisting_files=len(before),
            unchanged_preexisting_files=len(unchanged), unchanged_files=unchanged,
            analytic_tables=15, analytic_rows=5154, retained_check_groups=9,
            source_credit_added=0, recommendation_n=60,
            new_receipts=[dict(id=r['id'], path=r['path'], sha256=r['sha256'], bytes=r['bytes'],
                               request_sha256=sha(CACHE/(r['id']+'-request.json')),
                               receipt_sha256=sha(CACHE/(r['id']+'-receipt.json'))) for r in new],
            before_manifest_sha256=sha(CACHE/'preservation-before.json'),
            deliverable_sha256={p:sha(TOPIC/p) for p in ['query-manifest.json','search-log.md','synthesis.md','floor-audit.json','query-gap-audit.md','intent-gap-screening.json','discovery-receipts-intent-gap.json','PROGRESS.md']})
write(TOPIC/'query-gap-checks.json',checks)
print(json.dumps({k:v for k,v in checks.items() if k not in ('unchanged_files','new_receipts','deliverable_sha256')}))

"""Produce local research indexes, never experiment outcomes; stdlib only."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

TOPIC = Path(__file__).resolve().parents[1]
CACHE = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T6-1b')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(name, value): (TOPIC/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')

records = [r for name in ('discovery-receipts.json','discovery-receipts-extra.json','discovery-receipts-resume.json') for r in json.loads((TOPIC/name).read_text())]
by_id = {r['id']:r for r in records}
specs = [
 ('ahmed2010','paper',['ahmed2010.pdf'],'Not established; local research cache only'),
 ('cameron2015','paper',['cameron2015.pdf'],'Author-hosted manuscript; redistribution terms not established'),
 ('thulin2013','paper',['thulin2013.html','thulin2014.pdf'],'arXiv perpetual non-exclusive distribution license; not unrestricted reuse'),
 ('hossain2016','paper',['hossain2016.html'],'arXiv perpetual non-exclusive distribution license'),
 ('wang2026','paper',['wang2025.html'],'PMC permissions notice restricts reuse; local research cache only'),
 ('elmore2020','paper',['exchangeable2020.html'],'arXiv perpetual non-exclusive distribution license'),
 ('longjohn2025','paper',['aggregate2025.html'],'CC BY 4.0, inspected v2 2026-09-11'),
 ('singh2026','paper',['singh2026.html'],'CC BY 4.0, inspected v1 2026-09-08'),
 ('nist-exact','official implementation/reference',['nist-exact.html'],'Specific page reuse terms not established; local research cache only'),
 ('r-binom','official implementation/reference',['r-binom.html'],'Specific page reuse terms not established; local research cache only'),
 ('r-padjust','official implementation/reference',['r-padjust.html'],'Specific page reuse terms not established; local research cache only'),
 ('scipy-betabinom','official implementation/reference',['scipy-beta.html'],'SciPy community copyright; specific page terms not established; local cache only'),
 ('statsmodels-mcnemar','official implementation/reference',['statsmodels-mcnemar.html','statsmodels-tests-page.html'],'Specific page terms not established; raw LICENSE fetch failed; local research cache only')]
sources=[]
for ident,kind,ids,license_note in specs:
    card=TOPIC/'cards'/f'{ident}.md'
    assets=[]
    for aid in ids:
        r=by_id[aid].copy()
        path=Path(r['path'])
        assert path.exists() and digest(path)==r['sha256'], aid
        r['verified_bytes']=path.stat().st_size
        assets.append(r)
    sources.append(dict(id=ident,kind=kind,card=f'cards/{ident}.md',card_sha256=digest(card),depth='V2 method plus evaluation' if kind=='paper' else 'official method plus worked example or regression tests; not paper V2',topic_recheck_date='2026-10-20',license=license_note,assets=assets))
queries=[r for r in records if r['category'] in ('arxivAPI','OpenAlex')]
web_queries=['exact binomial confidence interval clustered data beta binomial missing data evaluation','Holm multiple testing exact McNemar official R binom.test','2025 2026 machine learning benchmark correlated evaluations missing data statistical uncertainty']
web_path=CACHE/'web-discovery-resume.json'
assert web_path.exists()
for q in web_queries:
    queries.append(dict(category='web',query=q,url='web search service query; exact text retained',retrieved_utc='2026-10-20; raw response retained',response_path=str(web_path),response_sha256=digest(web_path),note='Three queries batched in one service response; not three independent response files'))
assert len({(r['category'],r['query']) for r in queries})==12
assert len({r['category'] for r in queries})==3
write_json('query-manifest.json',dict(distinct_queries=12,categories=['arxivAPI','OpenAlex','web'],queries=queries))
asset_ids={aid for _,_,ids,_ in specs for aid in ids}
write_json('source-manifest.json',dict(schema='T6-stage1b-source-manifest-v2',scope='Primary statistical methods and official software references; no images, weights, experiment outputs or executable third-party tests',cache_root=str(CACHE),paper_v2_count=8,official_reference_count=5,sources=sources,other_fetch_receipts=[r for r in records if r['id'] not in asset_ids and r['category'] not in ('arxivAPI','OpenAlex')],receipt_files=['discovery-receipts.json','discovery-receipts-extra.json','discovery-receipts-resume.json','query-manifest.json']))

lines=['# T6 Stage1b search and inspection log','', 'Completed 2026-10-20. Twelve distinct substantive discovery queries across three categories (5 arXiv API, 4 OpenAlex, 3 web); direct source retrievals and repeated searches are not added to this count. Exact API response bytes, URLs and SHA-256 receipts are in the manifests. The three web queries share a single cached service response, clearly identified rather than presented as separate receipts.','', '| # | Category | Exact query |','|---|---|---|']
for i,r in enumerate(queries,1): lines.append(f"| {i} | {r['category']} | `{r['query']}` |")
lines += ['', '## Selection and reading', '', 'Queries cover dependence/clustered binary outcomes, exact intervals, informative missingness, aggregate benchmark comparisons and multiple testing. Search results were discovery leads, not evidence by themselves. Eight papers received topic-specific method-and-evaluation reading and individual V2 cards. Five official references received method/examples/tests reading and are counted separately. See the source manifest for exact cached assets, hashes, licenses and original/final URLs. The dated card paragraphs identify the inspected sections and evaluations.', '', '| Paper | Read and applied |', '|---|---|', '| Ahmed/Shoukri 2010 | Sections 2,4 and Table 1; beta mixture and invalid-fit simulation limits; rechecked, counted once. |', '| Cameron/Miller 2015 | II,IV,VIII.A-B and Table 2; independent clusters and state-resampling evaluation; rechecked, counted once. |', '| Thulin 2013/2014 | 2.1-2.3,3.1-3.3,4 and Figures 1-3; tail inversion and exact-versus-approximation numerical evaluation. |', '| Hossain et al. 2016 | 3-4,5.1-5.3 and Table 2; missingness assumptions and four-scenario simulation. |', '| Wang et al. 2026 | 2,3,5,6.1-6.2, Tables 1-3 and Figure 2; selection/missingness and finite-sample evaluation. |', '| Elmore 2020 | 2.1-2.2 equations 1-3,3,4; higher moments and model comparison simulations/examples. |', '| Longjohn et al. v2 2026 | 2.1-2.3,3.1-3.2 Tables 2-4; aggregate uncertainty and simulated VTAB illustration. |', '| Singh 2026 | 2-5 and Appendices B-C; finite-rollout identification and calibration/certificate evaluation. |', '', 'Official references: NIST exact-tail inversion worked outputs; R binom.test Details and inheritance example; R p.adjust Details/n/NA examples; SciPy beta-binomial PMF and moment/frozen-distribution examples; statsmodels McNemar Notes plus pinned v0.14.4 test_mcnemar regression tests. Downloaded test text never executes. Raw GitHub fetches failed SSL; the rendered official test file was successfully cached/read instead.', '', '## Exclusions and reuse boundaries', '', 'Other fetched leads (kim2017.html, matched2026.html, llm2025.html) are preserved in receipts but do not have V2 cards, do not count toward the paper floor, and support no synthesis claim. Search snippets, abstracts, OpenAlex metadata and arXiv feed abstracts do not support claims. Original Holm (1979) was not inspected in full and gets no paper-level credit; the official R implementation documentation is identified explicitly. Brown et al. is not silently reused as current V2 evidence. Ahmed and Cameron are retained only after topic-specific full-text rechecks. API metadata licenses do not imply a full-text license. Local caches with unclear permissions are not redistributable research artifacts.', '', '## what we might still have missed', '', 'A search floor is not an exhaustive review. We may have missed late-2026 work not indexed by these services, dependence involving creator/content groups, partial exchangeability with negative pairwise correlations, arbitrary three-way cross-method dependence, or a missingness process triggered by a shared software/model failure. The grids do not estimate those processes. The current finite-exchangeable bounds cover feasible third moments for the specified nonnegative-ICC grid; route examples cover named laws, not all joint laws. No new source discovered through a snippet can remove these limits without full reading. The fixed development roster and one primary endpoint prevent a claim of representative population reliability even with exact arithmetic.']
(TOPIC/'search-log.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

entries=[]
for ident,kind,ids,license_note in specs:
    card=(TOPIC/'cards'/f'{ident}.md').read_text(encoding='utf-8')
    title=re.search(r'\*([^*]+)\*',card)
    title=title.group(1) if title else card.splitlines()[0].lstrip('# ')
    year=re.search(r'20\d\d',ident)
    entries.append('@misc{T6_'+ident.replace('-','_')+',\n  title = {'+title+'},\n  year = {'+(year.group() if year else '2026')+'},\n  url = {'+by_id[ids[0]]['url']+'},\n  note = {Inspected 2026-10-20; '+kind+'; see individual card for version and limitations}\n}')
(TOPIC/'references.bib').write_text('\n\n'.join(entries)+'\n',encoding='utf-8')
plan=json.loads((TOPIC/'planning-table-v2.json').read_text())
assert len(plan['tables'])==15 and sum(t['rows'] for t in plan['tables'].values())==5154
audit=dict(schema='T6-stage1b-floor-audit-v2',status='topic completed for parent review; not an independent scientific or human approval',paper_v2_sources=8,official_reference_cards=5,discovery_queries=12,discovery_categories=3,query_manifest='query-manifest.json',source_manifest='source-manifest.json',analytic_tables=15,analytic_rows=5154,n_values=[60,90,120],source_probability_grid='.50 through .90 by .01',seed_correlation_grid=[0,.1,.3,.5,.9,1],missingness='independent seed, whole-source, outcome-dependent seed/source, fixed missing-source tipping, negative dependence bounds',coverage=['operating characteristics','sharp finite exchangeable seed-majority bounds','cross-source dependence','negative safety and missingness gates','paired and independent-baseline route sensitivity','exact intervals','paired exact sign and Holm multiplicity','hypothetical budget'],checks_passed=plan['checks'],recommendation_n=60,threshold_or_route_change=False,protected_or_shared_file_edits=False,used_real_images_weights_outcomes_gpu_server=False,planning_record='planning-table-v2.json',historical_files='planning-table.json and tools/plan.py are superseded v1 history; not current claims')
write_json('floor-audit.json',audit)
print(json.dumps(dict(papers=8,official_references=5,queries=12,categories=3,tables=15,rows=5154,source_hashes_verified=True)))

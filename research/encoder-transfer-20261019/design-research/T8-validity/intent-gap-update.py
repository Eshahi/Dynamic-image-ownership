"""Bounded T8 B2 documentary update; only this topic and its MAIN cache are used."""
import csv
import datetime
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
CACHE = pathlib.Path(r'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T8-1b-intent-gap')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, value):
    (ROOT/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

history = ROOT/'intent-gap-history'
history.mkdir(exist_ok=True)
for name in ['query-manifest.json','floor-audit.json','search-log.md','synthesis.md','PROGRESS.md','query-gap-audit.md','query-gap-checks.json']:
    dst = history/name
    if not dst.exists():
        dst.write_bytes((ROOT/name).read_bytes())

manifest=json.loads((history/'query-manifest.json').read_text(encoding='utf-8'))
jobs=json.loads((CACHE/'discovery-results.json').read_text())+json.loads((CACHE/'focused-discovery-results.json').read_text())
decisions={
 'T8-Q24':[
  'General web link-rot thesis; adjacent rather than image-cohort evidence.',
  'Fungal beech heart rot; irrelevant biological decay.',
  'Citrus pathogens; irrelevant biological decay.',
  'Wooden-pole rot detection; irrelevant imaging application.',
  'Oil-palm stem rot; irrelevant imaging application.',
  'Academic reference archiving; adjacent rather than image-cohort evidence.',
  'Spruce wood decay; irrelevant remote-sensing application.',
  'Pea pathogens; irrelevant biological decay.'],
 'T8-Q25':[
  'Text classifier serving nondeterminism; adjacent modality, excluded.',
  'Physical-system CNN reproducibility; adjacent model/application, excluded.',
  'Diffusion language-model nondeterminism; adjacent modality, excluded.',
  'Diffusion language-model evaluation; adjacent modality, excluded.',
  'Speculative decoding precision; adjacent language model, excluded.',
  'LLM backend reproducibility; adjacent modality, excluded.',
  'LLM hardware perturbations; adjacent modality, excluded.',
  'Kernel-trace synthesis; adjacent output/application, excluded.'],
 'T8-Q28':[
  'Direct text-to-image geographic-diversity measurement lead; no empirical result adopted.',
  'Broader AI evaluation geographic-bias lead; needs primary-text scope check before reliance.',
  'Direct image search/retrieval dataset-geography lead; candidate for cohort selection V24.',
  'Dataset-diversity conference lead; may share work with rank 3; no separate source credit.',
  'Face-cohort geographic-bias audit lead; narrower than general natural-image cohort.',
  'Image augmentation/geographic-bias lead; candidate only, no remedy adopted.',
  'Image-generation geographic-representation lead; source duplication with rank 8 possible.',
  'Same titled geographical-representation work as rank 7; no extra source credit.'],
 'T8-Q29':[
  'Direct diffusion finite-precision thesis lead; may overlap rank 2, no source credit.',
  'Direct floating-point diffusion quantization lead; precision job, not hardware determinism proof.',
  'Direct diffusion quantization lead; candidate arithmetic-sensitivity evidence only.',
  'Direct post-training diffusion quantization lead; candidate only, no quantization proposed.',
  'Direct diffusion-transformer FP4 lead; architecture differs from frozen SDXL.',
  'Visual autoregressive quantization/FPGA work; adjacent architecture, excluded.',
  'Stable Diffusion quantization lead; metadata alone does not validate quality or provenance.',
  'Direct diffusion low-bit floating-point lead; no inferred fp16/fp32 effect for this pipeline.']}

new=[]
rawchecks=[]
for job in jobs:
    qid=job['id']; receipt=job['receipt']; request=json.loads(pathlib.Path(receipt['request_path']).read_text())
    counted=qid in ['T8-Q28','T8-Q29']
    row={'id':qid,'category':'OpenAlex','query':job['query'],'url':request['url'],'started_utc':request['started_utc'],
      'completed_utc':receipt['completed_utc'],'http_status':receipt['http_status'],'request_kind':'discovery search',
      'status':'successful HTTP200 discovery response; '+('counted' if counted else 'peripheral/adjacent yield, excluded'),
      'substantive_evidence_counted':counted,'request':receipt['request_path'],'request_sha256':receipt['request_sha256'],
      'cache':receipt['response_path'],'sha256':receipt['response_sha256'],'bytes':receipt['response_bytes'],
      'receipt':str(CACHE/(qid+'-receipt.json')),'receipt_sha256':sha(CACHE/(qid+'-receipt.json')),
      'request_headers':request['headers'],'results':job['results'],
      'screening':[dict(rank=r['rank'],title=r['title'],decision=d) for r,d in zip(job['results'],decisions[qid])],
      'limits':'Discovery metadata only. No V2 credit, empirical claim, method amendment or model experiment.'}
    new.append(row)
    for kind,key,hkey in [('request','request','request_sha256'),('response','cache','sha256'),('receipt','receipt','receipt_sha256')]:
        p=pathlib.Path(row[key]); rawchecks.append({'id':qid,'kind':kind,'path':str(p),'expected_sha256':row[hkey],'observed_sha256':sha(p),'match':sha(p)==row[hkey]})

webraw=CACHE/'web-Q26-Q27-response.json'
webrequest=CACHE/'web-Q26-Q27-request.json'
web=json.loads(webraw.read_text())
assert isinstance(web,str)
webscreens=[]
for rank,block in enumerate(re.split(r'\n-{20,}\n',web),1):
    if not block.strip(): continue
    title=block.strip().splitlines()[0]
    if 'huggingface.co/docs/diffusers' in title:
        decision='Primary official reproducibility discovery lead; no new scientific claim; pooled batch excluded from floor.'
    elif any(s in title for s in ['arxiv.org','openaccess.thecvf.com','openreview.net','dataverse.ird.fr','flickr.org']):
        decision='Primary candidate discovery lead for cohort selection or precision; title/snippet only, no V2 or empirical credit.'
    else:
        decision='Secondary, adjacent or unrelated web lead; excluded from scientific evidence and floor.'
    webscreens.append({'rank':rank,'title_and_url':title,'decision':decision})
for qid,query in zip(['T8-Q26','T8-Q27'],json.loads(webrequest.read_text())['queries']):
    new.append({'id':qid,'category':'web','query':query,'request_kind':'discovery search','status':'successful pooled web response; excluded',
      'substantive_evidence_counted':False,'request':str(webrequest),'request_sha256':sha(webrequest),'cache':str(webraw),'sha256':sha(webraw),
      'screening':webscreens,'limits':'Pooled batch not uniquely attributed. Repeated three times to save response; repeats add no query or intent. First two response versions survive only in task transcript; third raw serialized tool response saved. No scientific reliance.'})
for p in [webraw,webrequest]: rawchecks.append({'id':'T8-Q26/Q27 pooled','kind':p.name,'path':str(p),'expected_sha256':sha(p),'observed_sha256':sha(p),'match':True})
manifest['queries']+=sorted(new,key=lambda r:int(r['id'].split('Q')[1]))
intents=[
 ('I01','Evaluation, false positives and quality',['T8-Q01','T8-Q09']),
 ('I02','VINE/W-Bench baseline-specific evaluation conventions',['T8-Q03']),
 ('I03','WAM native detection/mask calibration conventions',['T8-Q04']),
 ('I04','Removal and regeneration attacks',['T8-Q05','T8-Q17']),
 ('I05','Error-controlled provenance and registry/retrieval side information',['T8-Q11']),
 ('I06','Safety-filter missingness/content selection',['T8-Q19']),
 ('I07','Forgery and false attribution',['T8-Q21']),
 ('I08','Perceptual metric shift/resampling sensitivity',['T8-Q22']),
 ('I09','Training duplication and memorization dependence',['T8-Q23']),
 ('I10','Image-cohort geographical representation and collection selection',['T8-Q28']),
 ('I11','Finite-precision diffusion arithmetic sensitivity',['T8-Q29'])]
mapping=[{'intent_id':i,'intent':name,'queries':ids} for i,name,ids in intents]
lookup={q:i for i,_,ids in intents for q in ids}
for q in manifest['queries']:
    q['conservative_intent_id']=lookup.get(q['id'])
counted=[q for q in manifest['queries'] if q['substantive_evidence_counted']]
assert len(counted)==13 and len(lookup)==13 and len(mapping)==11
assert all(q['conservative_intent_id'] for q in counted)
manifest.update(attempted_distinct_queries=29,total_logged_requests=29,distinct_discovery_search_requests=25,known_content_inspections=4,
 successful_substantive_queries=13,conservative_distinct_successful_intents=11,conservative_intent_mapping=mapping,
 count_revision_note='B2 conservatively merges Q01/Q09 and Q05/Q17: prior 11 searches supplied nine intents. Q28 cohort geography and Q29 finite precision add two new intents. Q24/Q25 peripheral and Q26/Q27 pooled/repeated searches excluded. There are now 29 distinct query/inspection specifications, 25 discovery searches, 13 countable queries and 11 conservative intents across three categories. Backend repetitions are not distinct queries.',
 new_intent_gap_receipts='intent-gap-checks.json')
write('query-manifest.json',manifest)

floor=json.loads((history/'floor-audit.json').read_text())
floor.update(status='B2 intent correction complete; parent checks and same independent reviewer acceptance pending',
 attempted_distinct_queries=29,total_logged_requests=29,distinct_discovery_search_requests=25,
 conservatively_counted_successful_substantive_queries=13,conservative_distinct_successful_intents=11,
 new_intent_gap_discovery_searches=6,new_intent_gap_counted_queries=2,new_intent_gap_counted_intents=2,
 historical_first_gap_counted_queries=11,historical_first_gap_conservative_intents=9,
 intent_gap_receipts='intent-gap-checks.json',
 historical_check_scope_note='Existing checksum/link/skill fields are historical author checks. query-gap-checks.json describes the first gap correction. Both remain unchanged; intent-gap-checks.json covers B2 and current counts.')
write('floor-audit.json',floor)

table='\n'.join('| '+i+' | '+name+' | '+', '.join(ids)+' |' for i,name,ids in intents)
audit='''# T8 B2 conservative discovery-intent correction

Fresh bounded topic gap correction, 2026-10-20. Parent checks and the same independent reviewer acceptance remain pending.

The first query-gap correction fixed inspection inflation but still had eleven countable searches and only nine conservative intents: Q01/Q09 share evaluation/FPR/quality, and Q05/Q17 share removal/regeneration. Its floor claim was premature under the B2 intent interpretation. The first `query-gap-audit.md`, `query-gap-checks.json` and `query-gap-history/` are preserved unchanged. Pre-B2 current files are additionally retained byte-for-byte in `intent-gap-history/`.

Two new successful discovery jobs now add substantive breadth. **Q28 `image dataset geographic diversity bias`** discovers GeoDiv, image search/retrieval Dataset Diversity, and geographic representation leads for source-cohort selection (V24). **Q29 `diffusion floating point quantization`** discovers direct floating-point diffusion quantization, Q-Diffusion and post-training diffusion quantization leads for arithmetic sensitivity (V10/V50/V52). Geographic source representation differs from training duplication/memorization; numerical diffusion arithmetic differs from perceptual-score sensitivity. Q29 does not establish actual cross-device nondeterminism or detector threshold changes in this pipeline. These are discovery leads only.

The initial OpenAlex Q24 link-rot query returned mostly biological decay and Q25 hardware/nondeterminism returned mostly language/physical-system work; both remain excluded. Supplemental web Q26/Q27 returned pooled image-cohort, official reproducibility, precision and many peripheral/secondary leads and remain excluded because attribution is pooled. The two-query web batch was invoked three times during raw-save troubleshooting, supplying no new distinct-query credit; only its third response is persisted, and the first two responses remain in the task transcript. Exact request strings are retained. The successful Q28/Q29 jobs have complete individual exact GET request URLs/headers, start/end UTC, HTTP200 headers, raw response bytes and SHA-256 in MAIN cache, without this web-receipt limitation.

Every new OpenAlex response has eight individual lead decisions (32 total). Every lead in the saved web batch has a screening disposition; these pooled decisions are stored once semantically although each query points to the shared list. All metadata remain discovery-only: no newly read V2, no new empirical claim, no model work and no protocol or cost change. No recent removal method was surfaced by these focused results.

## Conservative mapping of every countable query

| Intent | Search job | Countable query IDs |
|---|---|---|
'''+table+'''

The corrected total is **29 distinct query/inspection specifications: 25 discovery searches and four inspections; 13 countable successful queries collapse to 11 conservative intents in three categories (web, OpenAlex, arXiv API)**. Q13-Q16 remain inspections; Q18/Q20 remain excluded. Repetitions and synonyms add no intent. Q24/Q26 are unsuccessful or conservatively excluded searches of the new cohort-selection job; Q25/Q27 are excluded searches of the new arithmetic/reproducibility job. They do not make additional intents.

The **68 threats and 14 V2 papers are unchanged**. Existing V24, V10/V50/V52 and V63 preserve source selection, arithmetic and license/access limitations. Discovery cannot quantify a geographic bias, establish image availability attrition, or infer an effect of quantization on our frozen unquantized detector. No source images, results, held-out data, server or weights were accessed. No new requirement is inferred from a title.

## What we might still have missed

Eight-result rank cutoffs, broad terminology, geographic metadata availability, English-language indexing and publication lag limit these jobs. The original availability/decay and hardware-specific searches were weak; the countable refinements cover cohort geography and finite precision, not a validated analysis of URL attrition, licensing selection or hardware bit identity. Quantization is a larger intervention than our native fp16/fp32 difference and cannot quantify it. Metadata titles and duplicate publication versions do not substitute for primary method/evaluation reads. This is a bounded discovery-floor correction, not an exhaustive survey or independent-review verdict.
'''
(ROOT/'intent-gap-audit.md').write_text(audit,encoding='utf-8')

search=(history/'search-log.md').read_text(encoding='utf-8')
search=search.replace('Current total: **23 logged requests: 19 distinct discovery searches and four known-content inspections. Eleven successful substantive discovery queries across three categories (web, OpenAlex and arXiv API) count toward the floor.**','Historical first-gap total: **23 logged requests: 19 discovery searches plus four inspections; eleven countable searches but only nine conservative intents under B2.**')
search+='\n## B2 intent correction (current)\n\nCurrent total: **29 distinct request specifications; 25 discovery searches plus four inspections. Thirteen countable successful queries collapse to eleven conservative intents in three categories.** The exact mapping and retained receipt limitations are in [intent-gap-audit.md](intent-gap-audit.md) and [intent-gap-checks.json](intent-gap-checks.json). First-gap audit/checks remain historical and unchanged.\n\n| ID | Backend | Exact discovery query | Counts | Screening |\n|---|---|---|---|---|\n'
for q in sorted(new,key=lambda q:q['id']):
    search+='| '+q['id']+' | '+q['category']+' | '+q['query']+' | '+('yes' if q['substantive_evidence_counted'] else 'no')+' | '+q['status']+' |\n'
search+='\nQ24/Q25 have peripheral yield. Q26/Q27 share a three-times-invoked pooled batch and add no floor credit. Q28 searches cohort geographic selection; Q29 searches finite-precision diffusion arithmetic. The 32 new API leads and saved web leads have individual screening in the manifest. Repeated/duplicate sources add no V2 count.\n'
(ROOT/'search-log.md').write_text(search,encoding='utf-8')

synthesis=(history/'synthesis.md').read_text(encoding='utf-8')
start=synthesis.index('After a fresh strict discovery-count correction,')
end=synthesis.index('[The source manifest]',start)
synthesis=synthesis[:start]+'''After the first inspection-count correction and the B2 intent correction, there are 29 distinct logged request specifications: 25 discovery searches and four known-content inspections. Thirteen countable successful discovery queries collapse to eleven conservative intents across web, OpenAlex and arXiv API. Q01/Q09 and Q05/Q17 are merged; Q28 adds cohort geography/collection selection and Q29 adds finite-precision diffusion arithmetic. Q18/Q20 and peripheral/pooled new queries remain excluded. The original author and first-gap claims/checks are historical; see [the intent audit](intent-gap-audit.md), its exact mapping and receipt limits. '''+synthesis[end:]
synthesis=synthesis.replace('Eleven conservatively counted substantive discovery queries meet the search floor but cannot prove completeness.','Thirteen countable searches collapse to eleven conservative intents and meet the numerical breadth floor, pending acceptance; this cannot prove completeness.')
synthesis+='\nB2 discovery-only refinements add image-cohort geographical representation and diffusion floating-point/quantization sensitivity. These support no newly adopted empirical result or modification. Geographic diversity is not training-set duplication, and finite-precision arithmetic is not perceptual-score resampling. Existing source-selection and precision limits stand. Complete individual request/response receipts exist for the two counted new jobs; pooled web retries are excluded and their incomplete historical receipt retention is disclosed in the intent audit.\n'
(ROOT/'synthesis.md').write_text(synthesis,encoding='utf-8')

progress=(history/'PROGRESS.md').read_text(encoding='utf-8')
progress=progress.replace('Current count is 11 substantive discovery queries in three categories, 19 total searches plus four inspections.','The first-gap count was 11 substantive discovery queries in three categories, 19 searches plus four inspections; B2 subsequently found only nine conservative intents.')
progress+='\n2026-10-20 fresh B2 intent-gap correction complete, pending parent checks and the same independent reviewer acceptance. Two countable focused OpenAlex jobs add image-cohort geography/selection and diffusion finite-precision arithmetic. Current total: 29 distinct request specifications, 25 discovery searches plus four inspections, 13 countable successful queries and 11 conservative intents across three categories. Q01/Q09 and Q05/Q17 are merged explicitly. Four other new query strings are excluded, including pooled web retries whose receipt limits are disclosed. The first-gap audit/checks/history are unchanged; pre-B2 current documents are in intent-gap-history/. See intent-gap-audit.md and intent-gap-checks.json. All 68 threats and 14 V2 cards remain unchanged; no science, compute, shared-state or source-image action.\n'
(ROOT/'PROGRESS.md').write_text(progress,encoding='utf-8')

prior=json.loads((ROOT/'query-gap-checks.json').read_text())
scientific=[]
for name,expected in prior['scientific_artifacts_sha256'].items():
    p=ROOT/name; scientific.append({'path':name,'expected_sha256':expected,'observed_sha256':sha(p),'match':sha(p)==expected})
history_checks=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(history.iterdir())]
checks={'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'documentary intent checks complete; parent checks and same independent reviewer acceptance pending',
 'distinct_request_specifications':29,'discovery_search_specifications':25,'known_content_inspections':4,
 'countable_successful_queries':13,'countable_ids':[q['id'] for q in counted],
 'conservative_distinct_successful_intents':11,'conservative_intent_mapping':mapping,'successful_categories':manifest['successful_categories'],
 'new_counted_queries':['T8-Q28','T8-Q29'],'new_excluded_queries':['T8-Q24','T8-Q25','T8-Q26','T8-Q27'],
 'new_openalex_leads_screened':sum(len(q['screening']) for q in new if q['category']=='OpenAlex'),
 'saved_pooled_web_leads_screened':len(webscreens),'new_openalex_http200_responses':4,
 'raw_cache_checks':rawchecks,'raw_cache_mismatches':sum(not c['match'] for c in rawchecks),
 'pre_B2_current_files_preserved':history_checks,'first_gap_audit_unchanged':sha(ROOT/'query-gap-audit.md')==sha(history/'query-gap-audit.md'),
 'first_gap_checks_unchanged':sha(ROOT/'query-gap-checks.json')==sha(history/'query-gap-checks.json'),
 'historical_scientific_checks':scientific,'threats':len(list(csv.DictReader((ROOT/'threat-register.csv').open(encoding='utf-8')))),
 'V2_papers_unchanged':14,'independent_acceptance':False,
 'web_receipt_limitation':json.loads(webrequest.read_text())['note']}
assert checks['raw_cache_mismatches']==0 and all(c['match'] for c in scientific)
assert checks['first_gap_audit_unchanged'] and checks['first_gap_checks_unchanged'] and checks['threats']==68
write('intent-gap-checks.json',checks)
print(json.dumps({k:checks[k] for k in ['distinct_request_specifications','countable_successful_queries','conservative_distinct_successful_intents','new_openalex_leads_screened','saved_pooled_web_leads_screened','raw_cache_mismatches','first_gap_audit_unchanged','first_gap_checks_unchanged','threats']},indent=2))

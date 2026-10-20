# HISTORICAL PACKAGER: superseded by the 2026-10-20 query-gap correction.
# Do not rerun: it regenerates the old inspection-inclusive search counts.
"""Documentary T7 packaging only; reads cached papers, never images/models."""
from pathlib import Path
from html.parser import HTMLParser
import csv, hashlib, html, io, json, re, xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
CACHE = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T7-1b')
DATE = '2026-10-20'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(v if isinstance(v, str) else json.dumps(v, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

class Meta(HTMLParser):
    def __init__(self): super().__init__(); self.values={}
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='meta' and a.get('name','').startswith('citation_'):
            self.values.setdefault(a['name'],[]).append(a.get('content',''))

sources=read(OUT/'sources-1b.json')
if not any(s['id']=='zodiac' for s in sources):
    sources.append(dict(id='zodiac',title='Attack-Resilient Image Watermarking Using Stable Diffusion',venue='NeurIPS',year=2024,
        venue_url='https://proceedings.neurips.cc/paper_files/paper/2024/hash/43d33182360378d5c8e69dd706c24f2f-Abstract.html',
        pdf_url='https://proceedings.neurips.cc/paper_files/paper/2024/file/43d33182360378d5c8e69dd706c24f2f-Paper-Conference.pdf'))
for s in sources:
    if s['id']=='ringid': s['title']='RingID: Rethinking Tree-Ring Watermarking for Enhanced Multi-Key Identification'
write(OUT/'sources-1b.json',sources)
rows=read(OUT/'evaluation-evidence.json')
by={r['id']:r for r in rows}
by['gs']['image_counts']='Detection: 1,000 positive images per watermark trial, repeated for five watermark trials. Traceability: 1,000 users × 10 images = 10,000 outputs. Quality uses 10 batches; batch size is not stated in the inspected main section. Repeated trials are not automatically independent source images.'
if '50,000 messages' not in by['lawa']['image_counts']:
    by['lawa']['image_counts']+=' Attribution: 50,000 messages × 2 images = 100,000 generated images; this is a different experiment, not the 1,000-source robustness cohort.'
by['wind']['limitations']=by['wind']['limitations'].replace('Page23 layout extraction independently confirms the headers and ordering; no visual rendering was available locally.','The parent agent rendered and visually inspected final-PDF page 23 on 2026-10-20; cache wind-render/page-023.png confirms the headers and ordering. This is attributed visual verification, not a claim that the T7 author performed that rendering.')
by['wind']['evaluation_locator']='§5.1, Tables1–3; final-PDF AppendixD.1–D.9 (pp20–24), G/H (pp25–26), Table11 (p23)'
by['wind']['image_counts']='Main robustness/quality evaluation-image n remains NR after searching the full available final PDF and reading AppendixD.1–D.9/G/H. N=100,000 in main variants and runtime is dictionary noise/key count; D.1 N=10,000 noises and D.2 N=100 initial noises are likewise not stated as evaluation-image denominators. No count is inferred from decimal accuracy increments.'
by['seal']['evaluation_locator']='Final main §4, Tables1–2; separate official supplement §§9–13, Tables3–7 (five pages)'
by['seal']['image_counts']='Main removal/CatAttack evaluation-image n remains NR after reading main evaluation and the full available five-page official supplement. Supplement §11 explicitly reports 100 images for latent-forgery attacks only. Supplement §9.4 has 10,000 caption pairs for embedding fine-tuning (training), not test images. n/k=1024 denotes noise patches and b=7 denotes hash bits per patch, not image n.'
by['seal']['metrics']='ROC-AUC for semantic forgery/CatAttack, removal detection accuracy, steganalysis AUC, and CLIP score before/after watermarking. Different tasks have different denominators.'
by['seal']['fpr']='Main Tables1–2 report ROC-AUC, not a numerical low-FPR TPR operating point. Supplement §13.3 reports regeneration accuracy, without a numeric FPR/negative denominator. The 100-image latent-forgery experiment does not calibrate rare-image FPR.'
by['seal']['baselines']='Main: WIND, Tree-Ring, Gaussian Shading. Supplement Table6 regeneration: HiDDeN, Stable Signature, TrustMark, WOUAF.'
by['seal']['conditional_numbers']='Main CatAttack (object dimension30–60% of image): AUC .551 basicSEAL, .982 with spatial test; private-model forgery AUC .708 versus0 for listed baselines. Supplement §11 latent-forgery: complete robustness on100images (author report). Supplement §13.3 Table6 regeneration detection accuracy: SEAL98%, HiDDeN47%, StableSig41%, TrustMark5%, WOUAF51%; image n and FPR are not stated there. Do not combine these tasks into one TPR claim.'
by['seal']['limitations']='Uses a semantic model and diffusion inversion; semantic binding differs from F5 content-match read endpoint. All five official supplement pages were text-inspected on2026-10-20, including explicit100-image latent-forgery experiment, but main removal/CatAttack n remainsNR. Extraction emitted wrong-pointing-object warnings; relevant prose/tables are coherent, without inferring unavailable figure details. AUC and robustness claims do not supply low-FPR calibration.'
write(OUT/'evaluation-evidence.json',rows)

# Compare current artifact identity against durable retrieval receipts, not just newly computed hashes.
receipts=read(CACHE/'retrievals.json')+read(CACHE/'reuse-receipts.json')+[read(CACHE/'zodiac-receipt.json'),read(CACHE/'seal-supplement-receipt.json')]
checked_receipts=[]
for receipt in receipts:
    if receipt.get('status')=='retrieved' and receipt.get('sha256'):
        artifact=Path(receipt['cache_path'])
        assert sha(artifact).lower()==receipt['sha256'].lower(),artifact
        checked_receipts.append(dict(artifact=str(artifact),sha256=sha(artifact),check='matches durable retrieval receipt'))
write(OUT/'artifact-checks.json',checked_receipts)

# Line windows personally re-opened by the resumed T7 author, supplementary to prior durable reading.
windows={
 'waves':[(646,730),(851,945),(2546,2602)],
 'vine':[(411,487),(513,592),(745,780)],
 'wam':[(196,275),(351,490)],
 'trustmark':[(181,265),(361,480)],
 'lawa':[(191,265),(330,429),(450,456),(581,660)],
 'ringid':[(246,315),(411,515)],
 'robustwide':[(276,450)],
 'gs':[(251,315),(511,610),(604,688)],
 'editguard':[(261,325),(598,687)],
 'omniguard':[(281,345),(561,660)],
 'specguard':[(291,380),(596,703)],
 'wind':[(255,301),(347,401),(780,898),(976,1004)],
 'seal':[(238,307),(553,642)],
 'peccvai':[(281,380),(571,670)],
 'zodiac':[(282,377),(378,477),(491,560)]}
authors_eccv={
 'lawa':['Ahmad Rezaei','Mohammad Akbari','Saeed Ranjbar Alvar','Arezou Fatemi','Yong Zhang'],
 'ringid':['Hai Ci','Pei Yang','Yiren Song','Mike Zheng Shou'],
 'robustwide':['Runyi Hu','Jie Zhang','Ting Xu','Jiwei Li','Tianwei Zhang']}
papers=[]; evidence=[]; manifest=[]; inspections=[]
for s in sources:
    sid=s['id']; r=by[sid]
    venue=CACHE/f'{sid}-venue.html'
    meta=Meta(); meta.feed(venue.read_text(encoding='utf-8'))
    authors=meta.values.get('citation_author',authors_eccv.get(sid,[]))
    assert authors, sid
    # Canonical title is from official metadata where supplied, never a guessed alias.
    title=meta.values.get('citation_title',[s['title']])[0]
    s['title']=title
    artifact=CACHE/(f'{sid}-reused.html' if sid in ('waves','vine') else f'{sid}-paper.pdf')
    textfile=CACHE/(f'{sid}-reused.txt' if sid in ('waves','vine') else f'{sid}-paper.txt')
    fullurl={'waves':'https://arxiv.org/html/2401.08573v3','vine':'https://arxiv.org/html/2410.18775v2'}.get(sid,s['pdf_url'])
    revision={'waves':'arXiv 2401.08573v3 (official PDF transport failure)','vine':'arXiv 2410.18775v2 (official PDF transport failure)'}.get(sid,f"{s['venue']} {s['year']} final PDF")
    paper=dict(schema_version='1.0',paper_id='t7_'+sid,citation_key=f"T7_{sid}_{s['year']}",doi=None,canonical_url=s['venue_url'],title=title,authors=authors,year=s['year'],venue=s['venue'],access_date=DATE,source_type='paper',verification='verified',inspected_content='full-text',inspection=dict(artifact=artifact.name,sha256=sha(artifact)),limitations=[r['limitations'],'V2 means method and evaluation windows inspected; experiments were not reproduced. DOI was not independently verified and remains null.'])
    papers.append(paper)
    lines=textfile.read_text(encoding='utf-8').splitlines()
    inspections.append(dict(id=sid,author='Codex T7 resumed author',date=DATE,method_locator=r['method_locator'],evaluation_locator=r['evaluation_locator'],reopened_text_file=str(textfile),line_windows_1based=windows[sid],text_sha256=sha(textfile),note='Windows identify personal reinspection; prior agent inspection is supplementary. These line numbers refer to cached extraction, not journal pagination.'))
    manifest.append(dict(id=sid,canonical_url=s['venue_url'],official_venue_verified=True,venue=s['venue'],year=s['year'],venue_artifact=str(venue),venue_sha256=sha(venue),full_text_url=fullurl,revision=revision,artifact=str(artifact),sha256=sha(artifact),bytes=artifact.stat().st_size,derived_text=str(textfile),derived_text_sha256=sha(textfile),access_date=DATE,verification='V2_method_and_evaluation_read',card=f'cards/{sid}.md',license='Publicly served research copy; author/venue rights retained; no redistribution permission inferred',experimental_reproduction=False))
    card=f"# {title}\n\nStable ID: t7_{sid}. Citation key: {paper['citation_key']}. {s['venue']} {s['year']}; eligible top-venue evaluation. Accessed {DATE}. DOI: null (not verified). Authors: {'; '.join(authors)}.\n\nCanonical venue: {s['venue_url']}\nFull text actually inspected: {fullurl}\nRevision: {revision}. Official venue identity was separately read and verified.\n\nVerification: V2, method and evaluation sections read; documentary evidence, not reproduction. Primary artifact: `{artifact}`; SHA-256 `{sha(artifact)}`. Extracted text: `{textfile}`; SHA-256 `{sha(textfile)}`.\n\nMethod locator: {r['method_locator']}. Evaluation locator: {r['evaluation_locator']}. Personal reinspection windows (cached text, 1-based lines): {windows[sid]}.\n\n## Mechanism and threat model\n\n[direct-evidence] {r['mechanism']}\n\n## Evaluation practice rechecked for T7\n\n[direct-evidence] Image counts and units: {r['image_counts']}\n\n[direct-evidence] Metrics: {r['metrics']}\n\n[direct-evidence] FPR operating point: {r['fpr']}\n\n[direct-evidence] Quality practice: {r['quality_practice']}\n\n[direct-evidence] Baselines: {r['baselines']}\n\n[direct-evidence] Conditional numbers: {r['conditional_numbers']}\n\n## Interpretation and limits\n\n[agent-inference] {r['reporting_inference']} This is a reporting choice for the present consulted development cohort, assuming native endpoint definitions and the fixed protocol remain unchanged. It is not a new baseline recommendation.\n\nLimitations: {r['limitations']}\n\nWhat was rechecked beyond inherited dossier material: the method's actual detection task, source versus repeated-output denominator, numerical operating point or its absence, native quality/capacity differences, and the evaluation table context. An NR field means not stated in the inspected window; it does not prove absence everywhere in the paper, repository, or supplement.\n"
    if sid=='seal':
        supplement=read(CACHE/'seal-supplement-receipt.json')
        manifest[-1]['supplement']=supplement
        inspections[-1]['supplement']=dict(artifact=supplement['cache_path'],sha256=supplement['sha256'],text=supplement['derived_text'],text_sha256=supplement['derived_text_sha256'],pages_read='All five pages, text only; §§9–13 rechecked for numeric units and evaluation conditions.')
        card+=f"\nOfficial supplement inspected: {supplement['url']}\nArtifact: `{supplement['cache_path']}`; SHA-256 `{supplement['sha256']}`. Derived text: `{supplement['derived_text']}`; SHA-256 `{supplement['derived_text_sha256']}`. All five pages' text was read; no experimental/source images were opened. Relevant locators §§9–13, especially §11 and §13.3.\n"
    write(OUT/'cards'/f'{sid}.md',card)
    write(OUT/'cards'/f'{sid}.json',paper)
    for field in ('mechanism','image_counts','metrics','fpr','quality_practice','baselines','conditional_numbers'):
        evidence.append(dict(claim_id=f't7_{sid}_{field}',claim=r[field],source_id=paper['paper_id'],kind='direct-evidence',stance='supporting',locator=r['method_locator'] if field=='mechanism' else r['evaluation_locator'],confidence='high',limitations=[r['limitations']],assumptions=[]))
    evidence.append(dict(claim_id=f't7_{sid}_reporting',claim=r['reporting_inference'],source_id=paper['paper_id'],kind='agent-inference',stance='supporting',locator=r['evaluation_locator'],confidence='medium',limitations=[r['limitations']],assumptions=['The current protocol remains frozen; literature practice motivates reporting, not new experiments or a universal equal-quality/FPR guarantee.']))

write(OUT/'sources-1b.json',sources)
write(OUT/'source-manifest.json',manifest)
write(OUT/'inspection-log.json',inspections)
legacy=read(OUT/'manifest.json')
legacy['stage1b_current_source_manifest']='source-manifest.json'
legacy['stage1b_query_manifest']='query-manifest.json'
legacy['historical_entries_counted_toward_stage1b_floor']=False
write(OUT/'manifest.json',legacy)
books={'ICML':'Proceedings of the International Conference on Machine Learning','ICLR':'Proceedings of the International Conference on Learning Representations','ECCV':'Proceedings of the European Conference on Computer Vision','CVPR':'Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition','ICCV':'Proceedings of the IEEE/CVF International Conference on Computer Vision','NeurIPS':'Advances in Neural Information Processing Systems'}
bib=[]
for paper in papers:
    bib.append('@inproceedings{'+paper['citation_key']+',\n  title = {{'+paper['title']+'}},\n  author = {'+' and '.join(paper['authors'])+'},\n  booktitle = {'+books[paper['venue']]+'},\n  year = {'+str(paper['year'])+'},\n  url = {'+paper['canonical_url']+'},\n  urldate = {'+DATE+'}\n}\n')
write(OUT/'references.bib','\n'.join(bib))
response=dict(request_id='encoder_transfer_t7_stage1b',papers=papers,evidence=evidence,assumptions=['Numeric matched-quality calipers are pre-outcome design choices, not perceptual equivalence guarantees.','The study uses a deterministic consulted development cohort and no image outcome exists at this stage.'],open_questions=['VINE section 4.2/4.3 and Table 1 caption disagree about denominators.','WIND final Table 11 reports AUC .971 and TP@1% 1.000 without an inspected aggregation explanation.','TrustMark exact evaluation counts and several other papers\' low-FPR negative denominators remain not reported in inspected windows.','Equal native-quality overlap and human perceptual ratings remain unmeasured; no result is inferred.'])
write(OUT/'literature-response.json',response)
fields=['id','venue','year','image_counts','metrics','fpr','quality_practice','baselines','method_locator','evaluation_locator','limitations']
buf=io.StringIO(newline=''); writer=csv.DictWriter(buf,fields);writer.writeheader()
table=['# T7 evaluation-practice table','',f'{len(rows)} distinct 2024–2026 top-venue papers, V2. Counts are reported separately by experiment; NR is not inferred from dataset conventions. See own cards and source-manifest.json for exact artifacts/versions. No numerical results are from the planned F5 study.','', '| Source / venue | Image counts and unit | Metrics | FPR operating point | Matched-quality practice | Baselines | Inspected evaluation |','|---|---|---|---|---|---|---|']
for r in rows:
    s=next(s for s in sources if s['id']==r['id'])
    writer.writerow({f:r.get(f,s.get(f,'')) for f in fields})
    vals=[f"[{r['id']}]({s['venue_url']}) / {s['venue']} {s['year']}",r['image_counts'],r['metrics'],r['fpr'],r['quality_practice'],r['baselines'],r['evaluation_locator']]
    table.append('| '+' | '.join(v.replace('|','/').replace('\n',' ') for v in vals)+' |')
write(OUT/'evaluation-practice.csv',buf.getvalue());write(OUT/'evaluation-practice.md','\n'.join(table)+'\n')

# Durable search events, individually inspected. Historical unpreserved web calls do not count.
queries=read(CACHE/'search-api-receipts.json')
for q in queries:
    p=Path(q['cache_path']); assert sha(p)==q['sha256']
    if q['category']=='openalex':
        data=read(p); q['screened_titles']=[x['display_name'] for x in data.get('results',[])[:6]]
        q['screening']='Metadata discovery only; overlapping leads link to full-text cards; no metadata-only item counts as V2.'
    elif q['category']=='arxiv_api':
        tree=ET.fromstring(p.read_text(encoding='utf-8'));ns={'a':'http://www.w3.org/2005/Atom'}
        q['screened_titles']=[' '.join(x.find('a:title',ns).text.split()) for x in tree.findall('a:entry',ns)[:6]]
        q['screening']='Metadata discovery only; not proof of venue or evaluation practice.'
    else:
        data=read(p);q['screening']='Official README read as discovery/release context only; frozen pinned implementation remains T5 authority.'
        q['screened_repository']=data.get('html_url')
    q['personally_rechecked_by']='Codex T7 resumed author, 2026-10-20'
webqueries=[
 'site:openaccess.thecvf.com CVPR 2026 image watermark evaluation false positive quality PECCVAI',
 'site:proceedings.neurips.cc 2024 ZoDiac watermark false positive image quality',
 'site:proceedings.iclr.cc 2025 image watermark benchmark matched quality false positive VINE WAM',
 'site:ecva.net 2024 watermarking bit accuracy image quality LaWa RingID Robust-Wide']
web=CACHE/'Q39-Q42-web.json'
for n,q in enumerate(webqueries,39):
    queries.append(dict(id=f'Q{n}',category='web_search',query=q,status='retrieved',accessed=DATE,cache_path=str(web),sha256=sha(web),receipt_scope='One live web tool call contained four distinct queries; cached full tool response is shared.',screening='Official CVF/NeurIPS/ICLR/ECVA identities corroborated. Certifiably Robust Image Watermark and Structured-Key candidates are screened leads only, not V2 cards; LLM watermark results are excluded as a different modality.'))
write(OUT/'query-manifest.json',queries)
search=['# T7 stage 1b search and coverage','',f'{DATE}. Resumed documentary work only. Eight preserved API/repository query receipts plus four new live web queries = {len(queries)} distinct durable queries across four categories. Prior interrupted work referred to 38 queries, but the missing first 30 are not counted without individual receipts. No query snippet counts as method/evaluation evidence.','', '| ID | Category | Exact query | Receipt / screening |','|---|---|---|---|']
for q in queries:
    search.append(f"| {q['id']} | {q['category']} | {q['query']} | `{Path(q['cache_path']).name}`; {q['screening']} |")
search+=['','## Coverage statement','','Fifteen distinct top-venue papers: ICML 2024 (1), ICLR 2025 (3), ECCV 2024 (3), CVPR 2024 (2), CVPR 2025 (1), ICCV 2025 (3), NeurIPS 2024 (1), CVPR 2026 (1). All have official venue evidence and their own V2 method/evaluation card. Thirteen are final PDFs; WAVES and VINE use explicitly identified arXiv versions after failed official PDF transport. They count once each. Historical grouped cards and policy pages do not increase the floor. The table covers image counts, metrics, FPR operating points, quality practice, baselines and exact locators. It deliberately keeps incomplete counts/thresholds as NR and preserves VINE/WIND internal contradictions.','','OpenAlex/arXiv metadata is used for discovery; official repositories supply release context. The floor relies on inspected primary papers, not index ranking or claimed journal quartiles. No Q1 journal ranking is needed because all counted papers meet the top-venue alternative.','', '## what we might still have missed','','The search is bounded rather than exhaustive: queries emphasize image watermark evaluation, editing, low-FPR reporting and the chosen external methods. It may miss Q1 journals indexed under steganography/authentication, non-English work, 2026 late camera-ready changes and benchmark supplements with counts omitted in the main paper. The newest evidence is one CVPR 2026 evaluation; this is not a census of 2026 research. Certifiably Robust Image Watermark and Structured-Key ECCV leads were not read to V2 here and therefore do not count. WAVES/VINE official PDFs remained transport-inaccessible; the inspected arXiv versions may differ from final proceedings. Some supplements were not read in full; missing detail means absent in the inspected windows, not nowhere documented. Human perceptual judgments, low-FPR calibration on a fresh population, and actual matched-quality overlap remain future evidence, not literature substitutes.']
write(OUT/'search-log.md','\n'.join(search)+'\n')
audit=dict(topic='T7',date=DATE,status='author_floor_check_pass_pending_parent_and_independent_review',distinct_eligible_v2_sources=len(sources),minimum_sources=12,own_card_ids=[s['id'] for s in sources],legacy_group_cards_counted=False,queries=len(queries),minimum_queries=10,categories=sorted(set(q['category'] for q in queries)),minimum_categories=3,final_pdfs=13,explicit_arxiv_transport_fallbacks=['waves','vine'],all_artifacts_hash_checked=True,evaluation_table_rows=len(rows),matched_quality_contract='Preserved finite grid, calipers and embedding-qualified subset; no scientific experiment amendment.',tables=8,figures=7,inferential_tests='Only three primary paired exact sign tests, one Holm family; no additional tests.',unresolved_source_conflicts=['VINE denominator text/caption conflict','WIND final Table11 same-ROC inconsistency'],no_images_models_gpu_or_outcomes=True)
assert len(sources)>=12 and len(rows)==len(sources) and len(queries)>=10 and len(audit['categories'])>=3
write(OUT/'floor-audit.json',audit)
write(OUT/'floor-audit.md',f"# T7 author floor audit\n\n{len(sources)} distinct eligible V2 cards against minimum 12; {len(queries)} distinct durable queries against minimum 10, across four categories against minimum three. Fifteen evaluation-table rows contain the required dimensions; absent numerical denominators/operating points remain explicitly NR. Thirteen final PDFs and two declared arXiv transport fallbacks, each with official venue evidence. All primary/venue/text/query checksums verified by packaging.\n\nEight tables, seven figures and only three primary Holm tests retained. No server, GPU, weights, upstream code execution, real source-image access, held-out data or experimental outcome. This is an author check; parent acceptance and independent milestone review remain outstanding.\n\nUnresolved documentary issues: VINE denominator disagreement; WIND AUC/TPR inconsistency; incomplete n/FPR detail in several inspected sections. These are explicit limitations, not concealed repairs.\n")
print(json.dumps({'sources':len(sources),'evidence_entries':len(evidence),'queries':len(queries),'categories':audit['categories'],'metadata':[(p['paper_id'],p['title'],p['authors']) for p in papers]},ensure_ascii=False))

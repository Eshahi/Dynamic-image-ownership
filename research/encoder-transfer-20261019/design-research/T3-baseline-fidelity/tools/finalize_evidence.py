"""Build topic-local references, discovery receipts and cache inventory."""
from pathlib import Path
import hashlib,json,re,collections
ROOT=Path(__file__).resolve().parents[1]
CACHE=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache')
QUERIES=[
'post hoc image watermark regeneration benchmark 2025 2026 TrustMark VINE Pixel Seal',
'post-hoc robust watermarking diffusion regeneration image editing 2026 method code',
'"OmniGuard" "watermark" "github"',
'"EditGuard" "copyright" watermark regeneration',
'"post-hoc" watermark "2026" "code" regeneration latent',
'"SimuFreeMark" code github checkpoint',
'"SpecGuard" "weights" watermark',
'"Pixel Seal" watermark "github"',
'"TrustMark" "Q" "BCH_5" encoder decoder 245',
'"RoSteALS" "ZoDiac" "InvisMark" regeneration benchmark',
'"Robust-Wide" watermark code license pretrained',
'"GenPTW" "OmniGuard" "LaWa" image watermark',
'"Optimizing and Securing the Modern Watermarking Channel for Images"',
'"Semantic-aware attention-guided digital watermarking for diffusion models"',
'"SNW" "watermarking" "2026" images code',
'"LatentShield" watermark "code"',
'"SNW" "Gesny" watermark github',
'"Optimizing and Securing" "github" watermark',
]
FINDINGS=[
'Broad discovery led to final TrustMark, VINE and EditGuard primary sources; comparisons require payload and quality qualification.',
'Newer-method search surfaced generation-time methods as well as eligible post-hoc leads; generation-time leads were not counted.',
'Official OmniGuard repository found; primary paper and partial demo release inspected separately.',
'EditGuard arXiv and CVF found; local inpainting evidence must be separated from global regeneration.',
'Release-oriented search led to the official VideoSeal model zoo, including ChunkySeal; no new core arm.',
'No official SimuFreeMark implementation or weights established by this targeted search; paper remains V2.',
'Official SpecGuard release evidence inspected; checkpoint and dependency limits remain in its card.',
'Official VideoSeal release/card establishes PixelSeal model availability; checkpoint bytes were not downloaded.',
'Official TrustMark configuration/source confirms BCH schema and distinct encoder/decoder resizing.',
'Cross-baseline search reinforced differences in attack, payload, quality and detector definitions; primary cards carry the numbers.',
'Official Robust-Wide repository located; license, model and attack conditions are separated.',
'GenPTW final AAAI entry and latent post-hoc paths found; method-specific quality retained.',
'SNW full primary text acquired and read, including method and Table 6 regeneration capacity evaluation.',
'Publisher lead found, but full-text acquisition returned 403; not counted as a V2 method.',
'SNW primary paper identified; no verified official code/weights established.',
'LatentShield publisher lead found, but full-text acquisition returned 403; eligibility and results remain unverified.',
'No verified official SNW release found; negative search is scoped, not a universal absence claim.',
'No verified official SNW release found; unrelated or secondary results were not treated as release evidence.',
]
URLS=[
['https://arxiv.org/html/2410.18775v2','https://arxiv.org/html/2312.08883v1'],
['https://arxiv.org/html/2504.19567v2'],
['https://github.com/xuanyuzhang21/OmniGuard'],
['https://arxiv.org/html/2312.08883v1'],
['https://github.com/facebookresearch/videoseal'],
['https://arxiv.org/html/2511.11295v1'],
['https://arxiv.org/html/2510.07302v1'],
['https://github.com/facebookresearch/videoseal'],
['https://github.com/adobe/trustmark'],
['https://arxiv.org/html/2304.03400v1','https://arxiv.org/html/2401.04247v2'],
['https://github.com/hurunyi/Robust-Wide'],
['https://doi.org/10.1609/aaai.v40i5.37412','https://arxiv.org/html/2408.05868v1'],
['https://arxiv.org/html/2609.34744v1'],
['https://www.sciencedirect.com/science/article/pii/S0923596526001955'],
['https://arxiv.org/html/2609.34744v1'],
['https://www.sciencedirect.com/science/article/pii/S2667305326000931'],
[],[],
]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    events_path=ROOT/'search-events.jsonl'
    events=[json.loads(s) for s in events_path.read_text(encoding='utf-8').splitlines()]
    for n,(q,f,urls) in enumerate(zip(QUERIES,FINDINGS,URLS),1):
        if not any(e.get('channel')=='web_search' and e.get('query')==q for e in events):
            events.append(dict(date='2026-10-20',channel='web_search',discovery_id=f'W{n:02}',query=q,status='executed',finding=f,primary_result_urls=urls,receipt_kind='Executed web search; result page is not cached full text. Follow-up primary fetch receipts are separate.',v2_from_search=False))
    events_path.write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events),encoding='utf-8')
    methods=json.loads((ROOT/'methods.json').read_text(encoding='utf-8'))
    sources=[]
    for m in methods:
        p=CACHE/'T3b'/m['source_file']
        sources.append(dict(method=m['name'],evidence='V2',source_id=m['stable_id'],canonical_url=m['canonical_url'],fulltext_url='https://arxiv.org/html/'+m['arxiv'],cache_path=p.as_posix(),bytes=p.stat().st_size,sha256=sha(p),inspected_sections=m['sections'],card=m['card_path']))
    inventory=[]
    for e in events:
        for key,hkey in [('cache_path','sha256'),('text_path','text_sha256')]:
            if e.get(key):
                p=Path(e[key]); exists=p.is_file()
                inventory.append(dict(event_channel=e['channel'],event_url=e.get('url'),path=str(p),recorded_sha256=e.get(hkey),exists=exists,current_sha256=sha(p) if exists else None,matches_recorded=sha(p)==e.get(hkey) if exists else False))
    for item in inventory:
        item['cache_state'] = 'matches recorded acquisition' if item['matches_recorded'] else ('earlier HTML snapshot overwritten by later acquisition; retained plain text hash still matches' if item['exists'] and item['path'].endswith(('distseal-repo.html','lawa-repo.html')) else 'missing or changed; inspect before relying on this artifact')
    reused=json.loads((ROOT/'reused-source-manifest.json').read_text(encoding='utf-8'))
    for e in reused:
        for k,h in [('source_cache','source_sha256'),('text_path','text_sha256')]:
            p=Path(e[k]); inventory.append(dict(event_channel='reused_primary',event_url=None,path=str(p),recorded_sha256=e[h],exists=p.is_file(),current_sha256=sha(p) if p.is_file() else None,matches_recorded=p.is_file() and sha(p)==e[h]))
    final=CACHE/'access-refresh'/'trustmark-iccv2025.pdf'
    final_record=dict(method='TrustMark',version='ICCV 2025 final',url='https://openaccess.thecvf.com/content/ICCV2025/papers/Bui_TrustMark_Robust_Watermarking_and_Watermark_Removal_for_Arbitrary_Resolution_Images_ICCV_2025_paper.pdf',cache_path=final.as_posix(),bytes=final.stat().st_size,sha256=sha(final),doi='10.1109/ICCV51701.2025.01731',provenance_card='research/q1-dossier-20261018/02-literature/access-refresh/cards/Bui2025TrustMark.md',inspection='Method, Algorithm 1, setup and Table 3; predecessor visually checked rendered PDF page 7. The separate T3b fetch failure does not negate earlier cached acquisition success.')
    derived=[]
    for p in sorted((CACHE/'T3b').glob('*')):
        if p.is_file() and p.suffix in ('.txt','.json','.xml','.html'):
            derived.append(dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
    counts=collections.Counter(e['channel'] for e in events)
    manifest=dict(schema='topic-research-deepening-v1',topic='T3-baseline-fidelity',accessed='2026-10-20',author='Codex agent',scope='Research-only primary paper and source-code text. No downloaded code executed, weights acquired, images inspected, science runs or new outcomes.',evidence_policy='V2 requires actual method and evaluation inspection. Search hits, code listings and inaccessible abstracts are not V2. Versions/release identities are not counted as extra methods.',distinct_v2_posthoc_methods=len(methods),method_sources=sources,final_version_supplement=final_record,search_event_counts=dict(counts),search_events='search-events.jsonl',counted_discovery={'web_search':18,'openalex':1,'official_repository':3,'total':22,'categories':3,'official_queries':['Search official GitHub repositories named SimuFreeMark','discovery: SpreadMark watermark','discovery: NAWE watermark'],'arxiv_api_failed_attempts_not_counted':3,'policy':'Counts are conservative. Repository file fetches, metadata verification and retries are not additional discovery queries. Earlier legacy web queries are not added to these counts.'},reused_sources=reused,event_cache_checks=inventory,cache_inventory=derived,limitations=['No real-image or rented-GPU measurement exists. Costs are assumptions or explicitly scoped published measurements.','Most papers omit a complete attack model/revision/strength/sampler/prompt/seed tuple or calibrated image FPR.','Two newly found journal leads remain inaccessible and are not V2.','Mutable checkpoint URLs and unresolved dependency/license permissions remain unresolved where marked.','Two earlier GitHub HTML snapshots (DistSeal and LaWa) were overwritten by later fetches of the same URL; both extracted texts retained identical hashes. Earlier HTML hashes are historical receipts, not current-file checks.'],legacy_manifest='manifest.json')
    (ROOT/'deepening-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    bib=[]
    for m in methods:
        # Versioned arXiv record; final publication identity is a separate record below where inspected.
        authors=' and '.join(m['authors'])
        bib.append('@misc{'+m['citekey']+',\n  title = {{'+m['title']+'}},\n  author = {'+authors+'},\n  year = {'+str(m['year'])+'},\n  eprint = {'+m['arxiv']+'},\n  archivePrefix = {arXiv},\n  url = {'+m['canonical_url']+'},\n  note = {Inspected version '+m['arxiv']+'; accessed 2026-10-20. '+('Four-author arXiv v1 identity; later author lists are not substituted.' if m['name']=='Robust-Wide' else '')+'}\n}')
    bib.append('@inproceedings{T3TrustMarkFinal2025,\n  title = {{TrustMark: Robust Watermarking and Watermark Removal for Arbitrary Resolution Images}},\n  author = {Tu Bui and Shruti Agarwal and John Collomosse},\n  booktitle = {Proceedings of the IEEE/CVF International Conference on Computer Vision},\n  year = {2025},\n  pages = {18629--18639},\n  doi = {10.1109/ICCV51701.2025.01731},\n  url = {'+final_record['url']+'},\n  note = {Final PDF method and evaluation inspected; Table 3 visually verified on page 7. Accessed 2026-10-20.}\n}')
    (ROOT/'references.bib').write_text('\n\n'.join(bib)+'\n',encoding='utf-8')
    print(json.dumps({'methods':len(methods),'bibliography_records':len(bib),'events':len(events),'event_channels':dict(counts),'cache_mismatches':[e['path'] for e in inventory if not e['matches_recorded']]},indent=2))
if __name__=='__main__': main()

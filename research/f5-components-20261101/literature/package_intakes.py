"""Package inspected component intakes; no network, science, or source changes."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ASSIGNMENTS={
'K01': [('HOLISTIC25','Q1J'),('CLIP Surgery','Q1J'),('Intra-modal CLIP','Q1J'),('AlignCLIP','Q1J'),('ClearCLIP','TOP'),('Sober Look at CLIP','TOP'),('Image Copy Detection for Diffusion Models','TOP')],
'K02': [('CSDH','Q1J'),('HIP','Q1J'),('DBpHash','Q1J'),('CertPHash','TOP'),('CMBH','TOP'),('Fuzzy Extractors are Practical','TOP')],
'K03': [('PRC image watermark','TOP'),('RingID','TOP')],
'K04': [('MarkPlugger','Q1J'),('Latent Watermark','Q1J'),('GaussMarker','TOP'),('Fourier Integrity','TOP'),('ZoDiac','TOP')],
'K05': [('DiffMark','Q1J'),('Latent Watermark','Q1J'),('VINE','TOP'),('ROBIN','TOP'),('ZoDiac','TOP')],
'K06': [('MarkPlugger','Q1J'),('DiffMark','Q1J'),('FreqMark','TOP'),('END2','TOP'),('ROAR','TOP')],
'K07': [('Attack-Simulation-Based Adaptive Normalization and Embedding','Q1J'),('ROAR','TOP'),('VINE','TOP'),('WAVES','TOP')],
'K08': [('Padhi dual watermark TAI','Q1J'),('Ozkaya self-embedded dual watermark','Q1J'),('Li self-recovery PLOS','Q1J'),('EditGuard','TOP'),('TAG-WM','TOP'),('GaussMarker','TOP')],
'K09': [('Safe Testing','Q1J'),('Emerging e-values','Q1J'),('Mean-variance e-processes','Q1J'),('Heavy-tailed aggregation','Q1J'),('Confidence on the focal','Q1J'),('Gaussian Shading','TOP'),('Watermark Anything','TOP'),('PRC image watermark','TOP')],
'K10': [('Padhi dual watermark TAI','Q1J'),('Ozkaya self-embedded dual watermark','Q1J'),('Li self-recovery PLOS','Q1J'),('Emerging e-values','Q1J'),('EditGuard','TOP'),('Watermark Anything','TOP'),('OmniGuard','TOP')],
'K11': [('Remote secure object authentication','Q1J'),('Two-Stage Watermark Removal','Q1J'),('Zero-watermarking and signcryption','Q1J'),('Gaussian Shading','TOP'),('Black-Box Forgery','TOP'),('Fuzzy Extractors are Practical','TOP')],
'K12': [('MarkDiffusion','Q1J'),('Safe Testing','Q1J'),('Confidence on the focal','Q1J'),('WAVES','TOP'),('Erasing Invisible','TOP'),('Black-Box Forgery','TOP')],
}
# Conservative substantive counts; exact logs retain excluded venue/metadata queries.
QUERIES={'K01':42,'K02':31,'K03':35,'K04':45,'K05':38,'K06':36,'K07':35,'K08':38,'K09':33,'K10':30,'K11':23,'K12':32}
NOTES={
'K01':'One journal slot exhausted. Accepted/author versions distinguished; dense/local CLIP improvements do not automatically improve global q.',
'K02':'Two journal slots exhausted. Fifteen malformed site filters excluded; 31 remain. Extended FEAP version conditional; CMBH has no identified omitted appendix. Root correction: six distance-two owner-segment pairs.',
'K03':'Five journal and one TOP slots exhausted. CoPaD-Mark/Access polar paper lack complete tables; TrustMark known final ZIP supplement unread. No ZIP download permitted.',
'K04':'Three journal slots exhausted. Conservative45 excludes Q27,29,33,39,40,49-52,55 from55 exact queries. Added ruling queries Q16-Q26. Author-version identity caveats remain.',
'K05':'Three journal slots exhausted. Codec/deepfake training differs from independent-encoder T3; no quality guarantee transferred.',
'K06':'Three journal slots exhausted. ROAR is detector optimization, explicitly adjacent, not a writer result. FreqMark remains closed.',
'K07':'Four journal slots exhausted. PixelSeal is PRE, not a journal slot. Human visibility missing.',
'K08':'Two journal slots exhausted after root downgrades: Vaidya algorithms1-3 raster material unread; Singh medical fusion weakly relevant and excluded. Ten added queries Q17-Q26. Do not use the intake original5/5 claim.',
'K09':'Paper floors met. Ten added queries Q09-Q18. Statistical foundations count for reader calibration, not watermark efficacy.',
'K10':'One journal slot exhausted. Vaidya unread algorithms and MetaSeal unverified quartile excluded.',
'K11':'Paper floors met conditional on relevant key/trust-accounting scope and extended FEAP. Two full-text-web PDFs have no local hash.23 queries is not a30-query exhaustion if judge rejects a slot.',
'K12':'Paper floors met. Statistical sources count for evaluation validity; attack papers do not establish strict-quality F5 vulnerability.',
}

def main():
    cards=HERE/'cards';cards.mkdir(exist_ok=True)
    papers={};floor=[];search=['# Executed literature search log','',
      'SOURCE: Exact queries and access outcomes below are copied from the twelve fresh component intakes, accessed2026-11-01. Tables retain unsuccessful and venue-only queries. These are web searches over scholarly surfaces, not independent search engines or claimed direct database APIs. At least four successful surfaces per component are documented in the linked intake; blocked domain queries alone do not count as successful coverage.',
      '', 'JUDGMENT: Conservative substantive counts and exclusions are in [floor-accounting.md](floor-accounting.md). Batch-result attribution is retained where individual hits were not preserved. No uninspected lead contributes a numerical paper claim. Full card bundles retain the detailed exhaustion/access account. Root checks are in [ROOT-SUPPLEMENT.md](ROOT-SUPPLEMENT.md).','']
    for k,items in ASSIGNMENTS.items():
        p=HERE/'intake'/f'{k}.md';body=p.read_text(encoding='utf-8')
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        header=f'# Canonical card bundle {k}\n\nROOT DISPOSITION: {NOTES[k]}\n\nSOURCE: Preserved intake SHA-256 `{digest}`. Individual paper cards, citations, method/experiment locators, PDFs, caveats and exact queries follow. Only assignments in [manifest](../paper-assignments.json) count; multiple versions and supplements count once. This bundle is a publication of the intake, not an additional paper.\n\n'
        # Intake and cards are sibling folders, so ../../component links remain correct.
        (cards/f'{k}.md').write_text((header+body).rstrip()+'\n',encoding='utf-8')
        for name,cls in items:
            record=papers.setdefault(name,{'paper':name,'class':cls,'components':[],'cards':[]})
            assert record['class']==cls
            record['components'].append(k);record['cards'].append(f'cards/{k}.md')
        q=sum(c=='Q1J' for _,c in items);t=sum(c=='TOP' for _,c in items);req=3 if k in ('K11','K12') else 5
        status='PAPER FLOORS MET (proposed)' if q>=req and t>=3 else 'EXHAUSTION DOCUMENTED (judge acceptance pending)'
        assert QUERIES[k]>=15 and (q>=req and t>=3 or QUERIES[k]>=30)
        floor.append({'component':k,'Q1J':q,'Q1J_required':req,'TOP':t,'TOP_required':3,'substantive_queries':QUERIES[k],'successful_surfaces_minimum':4,'status':status,'notes':NOTES[k]})
        search.extend([f'## {k}', '',f'Conservative substantive queries: **{QUERIES[k]}**. [Full search/access/exhaustion context](intake/{k}.md). {NOTES[k]}',''])
        lines=body.splitlines()
        for i,line in enumerate(lines):
            if line.startswith('##') and any(x in line.lower() for x in ('search','quer','coverage')):
                j=i+1
                while j<len(lines) and not lines[j].startswith('## '):j+=1
                search.extend(lines[i:j]);search.append('')
    assert max(len(p['components']) for p in papers.values())<=2
    result={'access_date':'2026-11-01','count_basis':'unique work, max two component assignments; full-text provenance in card bundles','papers':list(papers.values()),'floors':floor,'unique_papers':len(papers),'assignments':sum(len(v) for v in ASSIGNMENTS.values())}
    (HERE/'paper-assignments.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (HERE/'search-log.md').write_text('\n'.join(search).replace('../../components/','../components/').rstrip()+'\n',encoding='utf-8')
    md=['# WP2 floor accounting — proposed to Claude','',
      'JUDGMENT: Missing paper slots are not passes. The brief permits documented exhaustion after at least30 substantive searches and meaningful surface coverage. Every short component uses that route; judge acceptance remains pending. Full citations and inspected artifacts are in [cards](cards/), metric evidence in [venues](venues.md). No PRE/OLD paper counts. Every conference is on the TOP whitelist. All twelve components have at least four successfully opened scholarly surfaces, explicitly distinguished from blocked searches.','',
      '| Component | Q1J / floor | TOP / floor | Conservative substantive queries | Disposition |','|---|---:|---:|---:|---|']
    for f in floor:md.append(f"| {f['component']} | {f['Q1J']}/{f['Q1J_required']} | {f['TOP']}/3 | {f['substantive_queries']} | {f['status']} |")
    md+=['',f"DERIVED: {len(papers)} unique counted works; {result['assignments']} component assignments; no work assigned to more than two components. The machine-readable [assignment manifest](paper-assignments.json) is authoritative over earlier reservations and agent-proposed counts.",'','## Root dispositions','']
    md += [f'- **{k}:** {NOTES[k]} [Intake](intake/{k}.md).' for k in ASSIGNMENTS]
    md+=['','## Unique-work assignment table','','| Work (full citation in cards) | Class | Components |','|---|---|---|']
    md += [f"| {p['paper']} | {p['class']} | {', '.join(p['components'])} |" for p in papers.values()]
    (HERE/'floor-accounting.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps({'unique':len(papers),'assignments':result['assignments'],'max_assignment':max(len(p['components']) for p in papers.values())}))

if __name__=='__main__':main()

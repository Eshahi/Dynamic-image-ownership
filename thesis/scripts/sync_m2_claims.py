"""Validate draft claim blocks and regenerate their separate writing inventory."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--thesis', type=Path, required=True)
    p.add_argument('--schema', type=Path, required=True)
    args = p.parse_args()
    from jsonschema import Draft202012Validator
    validator = Draft202012Validator(json.loads(args.schema.read_text(encoding='utf-8')))
    bindings = json.loads((args.thesis/'evidence/m2-evidence-bindings.json').read_text(encoding='utf-8'))
    sources = {s['evidence_id']:s for s in bindings['sources']}
    claims, projection, seen = [], [], set()
    pattern = re.compile(r'<!-- claim=([^;]+); kind=([^;]+); evidence=([^;]+); status=([^;]+); proposal=([^ ]+) -->\s*(.*?)\s*<!-- /claim -->', re.S)
    chapter_receipts = []
    for chapter in ('05-results.md','06-discussion.md'):
        path = args.thesis/'chapters'/chapter
        text = path.read_text(encoding='utf-8')
        if 'draft for human review' not in text:
            raise ValueError('Draft status required')
        matches = list(pattern.finditer(text))
        if len(matches)!=text.count('<!-- claim='):
            raise ValueError('Malformed or unclosed claim block')
        for match in matches:
            cid, kind, evidence, status, proposal, prose = match.groups()
            if cid in seen:
                raise ValueError(f'Duplicate claim {cid}')
            seen.add(cid)
            ids = evidence.split(',')
            if any(e not in sources for e in ids):
                raise ValueError(f'Unknown evidence for {cid}')
            if status not in ('verified','partial'):
                raise ValueError(f'Unexpected projection classification for {cid}')
            if status!='verified' and 'TODO:EVIDENCE' not in prose:
                raise ValueError(f'Unsupported extension must be marked: {cid}')
            claim = {'claim_id':cid,'text':prose,'evidence_ids':ids,
                     'run_ids':['coco512-confirm-rerun-1'],
                     'analysis_paths':[sources[e]['path'] for e in ids],
                     'kind':kind,'author_id':'Codex-agent'}
            validator.validate(claim)
            claims.append(claim)
            projection.append({'claim_id':cid,'classification':status,'chapter':chapter,
                'line':text[:match.start()].count('\n')+1,'proposal_ids':proposal.split(','),
                'basis':'Author projection from the referenced independent review and retained sources; not a new independent verdict.'})
        chapter_receipts.append({'path':'chapters/'+chapter,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'claim_count':len(matches)})
    evidence_dir = args.thesis/'evidence'
    (evidence_dir/'claim-inventory.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in claims),encoding='utf-8')
    projection_doc = {
        'status':'author writing projection; no human acceptance or lifecycle transition',
        'independent_review_commit':'e01d63cc9e6801cba902f80b4b825cdc48fb505a',
        'reviewed_original_report_commit':'2a31ed153c4e95e2382bf3c6e9f66304412aa980',
        'author_id':'Codex-agent','chapters':chapter_receipts,'claims':projection,
        'blocking':[{'claim_id':c['claim_id'],'reason':'Explicit unresolved extension; draft only'} for c in projection if c['classification']!='verified'],
        'rule':'Verified classifications cover bounded numbers, implementation properties or reported absence of evidence. A TODO on an absence statement does not make the missing positive claim supported.'}
    (evidence_dir/'m2-claim-projection.json').write_text(json.dumps(projection_doc,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'claims':len(claims),'explicit_unresolved_extensions':len(projection_doc['blocking']),'status':'draft'}))


if __name__=='__main__':
    main()

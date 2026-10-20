"""Bounded discovery addendum; raw metadata only, no source-level evidence credit."""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request

TOPIC = Path(__file__).resolve().parents[1]
CACHE = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T6-1b-intent-gap')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def discover():
    CACHE.mkdir(parents=True, exist_ok=True)
    # Preserve all pre-addendum bytes, including superseded history, once only.
    assert not (CACHE/'preservation-before.json').exists(), 'Already run; do not overwrite original evidence'
    prior = {}
    for path in sorted(TOPIC.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.name != 'intent_gap.py':
            rel = path.relative_to(TOPIC).as_posix()
            raw = path.read_bytes()
            saved = CACHE/'before'/rel
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_bytes(raw)
            prior[rel] = dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), copy=str(saved))
    write(CACHE/'preservation-before.json', prior)
    jobs = [
        ('paired-joint-route', 'correlated paired binary outcomes joint probability superiority margin',
         'How does a joint paired binary law determine the probability of clearing a fixed superiority margin, separately from marginal success and McNemar testing?'),
        ('composite-safety', 'co primary efficacy safety endpoints joint probability dependence',
         'How does dependence between a positive success count and a zero-event negative safety requirement affect their joint decision probability?'),
        ('quality-selection', 'matching post treatment variable collider bias common support caliper',
         'Can matching on achieved distortion after processing select a collider or restrict common support, even under deterministic finite-grid matching?'),
        ('budget-censoring', 'computational experiments time budget informative censoring runtime algorithm benchmarking',
         'Does a fixed compute-time cutoff select completed whole source clusters through runtime, unlike ordinary missing calls on an otherwise fixed roster?'),
    ]
    def fetch(job):
        ident, query, question = job
        url = 'https://api.openalex.org/works?'+urllib.parse.urlencode(dict(search=query, per_page=6))
        headers = {'User-Agent':'thesis-design-intent-gap/1.0', 'Accept':'application/json'}
        start = datetime.datetime.now(datetime.timezone.utc).isoformat()
        request = dict(id=ident, category='OpenAlex', query=query, design_question=question,
                       method='GET', url=url, request_headers=headers, requested_utc=start)
        write(CACHE/(ident+'-request.json'), request)
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=55) as response:
            raw = response.read()
            path = CACHE/(ident+'-response.json')
            path.write_bytes(raw)
            request.update(status=response.status, final_url=response.url,
                           response_headers=dict(response.headers), retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                           path=str(path), bytes=len(raw), sha256=digest(path))
        data = json.loads(raw)
        request['result_count'] = len(data['results'])
        request['total_index_matches'] = data['meta']['count']
        write(CACHE/(ident+'-receipt.json'), request)
        return request
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(fetch, jobs))
    write(TOPIC/'discovery-receipts-intent-gap.json', records)
    for r in records:
        data = json.loads(Path(r['path']).read_bytes())
        print(r['id'], r['status'], r['result_count'])
        for work in data['results']:
            print(work['id'], work['display_name'].encode('ascii', 'backslashreplace').decode())

if __name__ == '__main__':
    discover()

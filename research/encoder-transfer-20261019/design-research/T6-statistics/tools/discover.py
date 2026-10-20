"""Stage 1b: download statistical texts and discovery receipts, never executable code."""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

OUT = Path(__file__).resolve().parents[1]
CACHE = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T6-1b")
CACHE.mkdir(parents=True, exist_ok=True)
jobs = []
for i, query in enumerate([
    'all:"beta binomial" AND all:"correlation"',
    'all:"missing" AND all:"cluster" AND submittedDate:[202501010000 TO 202610202359]',
    'all:"binomial" AND all:"confidence" AND all:"exact"',
], 1):
    jobs.append((f"arxiv-query-{i}.xml", "arxivAPI", query,
                 "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
                     dict(search_query=query, start=0, max_results=12, sortBy="submittedDate", sortOrder="descending"))))
for i, query in enumerate([
    "clustered binary outcomes missing data sensitivity analysis",
    "beta binomial intraclass correlation validation",
    "exact binomial confidence interval sample size",
    "benchmark machine learning correlated evaluation 2025 2026",
], 1):
    jobs.append((f"openalex-query-{i}.json", "OpenAlex", query,
                 "https://api.openalex.org/works?" + urllib.parse.urlencode(dict(search=query, per_page=8))))
sources = {
    "ahmed2010.pdf": "https://jds-online.org/journal/JDS/article/912/file/pdf",
    "nist-exact.html": "https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm",
    "r-padjust.html": "https://stat.ethz.ch/R-manual/R-devel/library/stats/html/p.adjust.html",
    "r-binom.html": "https://stat.ethz.ch/R-manual/R-devel/library/stats/html/binom.test.html",
    "scipy-beta.html": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.betabinom.html",
    "statsmodels-mcnemar.html": "https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html",
    "statsmodels-tests.txt": "https://raw.githubusercontent.com/statsmodels/statsmodels/v0.14.4/statsmodels/stats/tests/test_contingency_tables.py",
    "hossain2016.html": "https://arxiv.org/html/1608.05289",
    "thulin2014.pdf": "https://arxiv.org/pdf/1303.1288",
    "kim2017.html": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5736152/",
    "wang2025.html": "https://pmc.ncbi.nlm.nih.gov/articles/PMC13108325/",
    "cameron2015.pdf": "https://faculty.econ.ucdavis.edu/faculty/cameron/research/Cameron_Miller_JHR_2015_February.pdf",
}
jobs += [(name, "primary-source", url, url) for name, url in sources.items()]

def get(job):
    name, category, query, url = job
    entry = dict(id=name, category=category, query=query, url=url,
                 retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "thesis-statistical-design/1.0"})
        with urllib.request.urlopen(req, timeout=50) as response:
            body = response.read()
            entry.update(status=response.status, final_url=response.url,
                         content_type=response.headers.get("Content-Type"))
    except urllib.error.HTTPError as exc:
        body = exc.read()
        entry.update(status=exc.code, error=str(exc))
    except Exception as exc:
        body = str(exc).encode()
        entry.update(status="failed", error=str(exc))
    path = CACHE / name
    path.write_bytes(body)
    entry.update(path=str(path), bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
    return entry

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    receipts = list(pool.map(get, jobs))
(OUT / "discovery-receipts.json").write_text(json.dumps(receipts, indent=2) + "\n", encoding="utf-8")
print(json.dumps([{k: r.get(k) for k in ("id", "category", "status", "bytes")} for r in receipts], indent=2))

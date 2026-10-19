"""Cache only inspected primary statistical documents; no code/models/data."""
import datetime
import hashlib
import json
import urllib.request
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]
CACHE=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T6')
SOURCES=[
 ('ahmed2010.pdf','https://jds-online.org/journal/JDS/article/912/file/pdf','Sections 2 and 4, PDF pp.2-7; beta-binomial and simulation limits'),
 ('cameron2015.pdf','https://faculty.econ.ucdavis.edu/faculty/cameron/research/Cameron_Miller_JHR_2015_February.pdf','Existing V2 card reused; introduction and Section II refreshed'),
 ('nist-exact.html','https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm','Description: exact lower/upper tail inversion and examples'),
 ('r-padjust.html','https://stat.ethz.ch/R-manual/R-devel/library/stats/html/p.adjust.html','Details, arbitrary-dependence Holm control, examples'),
]
rows=[]
for name,url,inspection in SOURCES:
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(request,timeout=45) as response:
            data=response.read()
            final=response.geturl()
        if name.endswith('.pdf') and not data.startswith(b'%PDF'):
            raise ValueError('not a PDF')
        path=CACHE/name
        path.write_bytes(data)
        rows.append(dict(id=name,url=url,final_url=final,path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
            retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inspection=inspection,status='cached'))
    except Exception as e:
        rows.append(dict(id=name,url=url,status='failed',error=str(e)))
(OUT/'source-manifest.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows,indent=2))

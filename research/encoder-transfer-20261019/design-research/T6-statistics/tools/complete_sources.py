"""Cache statistical reference texts; downloaded contents are never executed."""
import concurrent.futures
import datetime
import hashlib
import json
import urllib.request
from pathlib import Path

OUT=Path(__file__).resolve().parents[1]
CACHE=Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T6-1b')
SOURCES={
 'thulin2013.html':'https://arxiv.org/html/1303.1288',
 'aggregate2025.html':'https://arxiv.org/html/2501.04234',
 'statsmodels-tests-page.html':'https://github.com/statsmodels/statsmodels/blob/v0.14.4/statsmodels/stats/tests/test_contingency_tables.py',
 'statsmodels-tests-v2.txt':'https://raw.githubusercontent.com/statsmodels/statsmodels/v0.14.4/statsmodels/stats/tests/test_contingency_tables.py',
 'statsmodels-license.txt':'https://raw.githubusercontent.com/statsmodels/statsmodels/v0.14.4/LICENSE.txt',
}
def get(item):
 name,url=item
 r=dict(id=name,category='primary-source',query=url,url=url,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40) as response:
   data=response.read();r.update(status=response.status,final_url=response.url)
  path=CACHE/name;path.write_bytes(data)
  r.update(path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 except Exception as e:r.update(status='failed',error=str(e))
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: receipts=list(pool.map(get,SOURCES.items()))
(OUT/'discovery-receipts-resume.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipts,indent=2))

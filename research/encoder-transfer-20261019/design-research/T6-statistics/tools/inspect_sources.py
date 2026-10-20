"""Readable local excerpts from cached primary HTML; no model/data execution."""
from html.parser import HTMLParser
from pathlib import Path
import re

CACHE = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T6-1b')

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.skip+=1
        if not self.skip and tag in ('p','h1','h2','h3','h4','tr','li','section','div'): self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
        if not self.skip and tag in ('p','h1','h2','h3','h4','tr','li'): self.parts.append('\n')
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)

for path in CACHE.glob('*.html'):
    parser=Text();parser.feed(path.read_text(encoding='utf-8'))
    lines=[re.sub(r'\s+',' ',x).strip() for x in ''.join(parser.parts).splitlines()]
    lines=[x for x in lines if x]
    path.with_suffix('.read.txt').write_text('\n'.join(f'{i+1}: {x}' for i,x in enumerate(lines))+'\n',encoding='utf-8')
print('Extracted cached primary HTML only.')

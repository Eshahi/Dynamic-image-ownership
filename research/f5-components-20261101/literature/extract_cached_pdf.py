"""Read existing paper PDFs using an already cached pure-Python wheel; no install."""
import hashlib
import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')
main = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
wheel = main / '.thesis-build/q1-research-20261018/cache/T7-1b/pypdf-6.1.3-py3-none-any.whl'
sys.path.insert(0, str(wheel))
from pypdf import PdfReader

cache = main / '.thesis-build/cache-f5c/papers'
out = Path(__file__).parent / 'extracted'
out.mkdir(exist_ok=True)
for name in sys.argv[1:]:
    path = cache / name
    assert path.resolve().parent == cache.resolve() and path.suffix == '.pdf'
    reader = PdfReader(path)
    text = '\n\n'.join(f'=== PDF PAGE {i + 1} ===\n' + (page.extract_text() or '') for i, page in enumerate(reader.pages))
    (out / (path.stem + '.txt')).write_text(text, encoding='utf-8')
    print(json.dumps({'pdf': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'pages':len(reader.pages), 'characters':len(text)}))

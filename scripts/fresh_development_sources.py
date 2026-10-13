"""Acquire the fixed 24-image development reservation; never select by outcomes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5')
DOCS = ROOT / 'research/journal-upgrade-20261009'
DEST = MAIN / '.thesis-build/assets/fresh-development-20261013'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def main():
    selection = json.loads((DOCS / 'fresh-development-selection.json').read_text())
    excluded = set(selection['raw_sha256_exclusions'])
    rows = []
    DEST.mkdir(parents=True, exist_ok=True)
    from m1b_canonical_source import canonicalize
    from PIL import Image
    for selected in selection['selected']:
        row = dict(selected)
        raw_path = DEST / row['filename']
        if not raw_path.exists():
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(row['url'], timeout=45) as response:
                        raw = response.read()
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(1)
            raw_path.write_bytes(raw)
        raw = raw_path.read_bytes()
        raw_hash = sha(raw)
        if raw_hash in excluded:
            raise RuntimeError(f'Raw overlap before decode: {row["source_id"]}; preserve and resolve fixed-rule exclusion')
        if len(raw) != row['size_bytes']:
            raise RuntimeError(f'Acquisition size mismatch: {row["source_id"]}')
        excluded.add(raw_hash)
        rgb, receipt = canonicalize(raw, raw_hash)
        canonical = DEST / f'{row["source_id"]}-rgb512.png'
        if canonical.exists():
            with Image.open(canonical) as image:
                if image.tobytes() != rgb.tobytes():
                    raise RuntimeError('Existing canonical mismatch; no overwrite')
        else:
            Image.fromarray(rgb).save(canonical)
        row.update(raw_path=str(raw_path), raw_sha256=raw_hash,
                   canonical_path=str(canonical), sha256=sha(canonical.read_bytes()),
                   canonicalization=receipt, raw_overlap=False)
        rows.append(row)
        print(f'prepared {row["source_id"]}: {len(raw)} bytes', flush=True)
    result = dict(schema='fresh-development-inputs-v1', prepared_at_utc=datetime.now(timezone.utc).isoformat(),
                  selection_sha256=sha((DOCS / 'fresh-development-selection.json').read_bytes()),
                  data_split='development-reserved', sources=rows,
                  raw_bytes=sum(r['size_bytes'] for r in rows), raw_overlap_count=0,
                  preprocessing='m1b-canonical-rgb512-v2, EXIF/ICC, RGB, BICUBIC 512x512')
    (DOCS / 'fresh-development-inputs.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')

if __name__ == '__main__':
    main()

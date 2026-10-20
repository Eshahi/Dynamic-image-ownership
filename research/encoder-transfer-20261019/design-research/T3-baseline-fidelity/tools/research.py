"""Text-only literature acquisition; never imports a model or downloads weights."""
import argparse
import concurrent.futures
import datetime
import hashlib
import html.parser
import json
import pathlib
import re
import urllib.parse
import urllib.request

TOPIC = pathlib.Path(__file__).resolve().parents[1]
CACHE = pathlib.Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b")
CACHE.mkdir(parents=True, exist_ok=True)


class Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"): self.skip += 1
        if tag in ("p", "h1", "h2", "h3", "h4", "tr", "li", "figcaption"):
            self.parts.append("\n")
        if tag in ("td", "th"): self.parts.append(" | ")
    def handle_endtag(self, tag):
        if tag in ("script", "style"): self.skip = max(0, self.skip - 1)
        if tag in ("p", "h1", "h2", "h3", "h4", "tr", "li", "figcaption"):
            self.parts.append("\n")
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)
    def text(self):
        return "\n".join(re.sub(r"\s+", " ", x).strip() for x in "".join(self.parts).split("\n") if x.strip())


def fetch(item):
    name, url, channel, query = item
    event = dict(date=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 channel=channel, query=query, url=url, name=name,
                 inspection="Acquisition only; no V2 promotion until method and evaluation reading.")
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "ThesisResearch/1.0 (text-only literature audit)"})
        with urllib.request.urlopen(request, timeout=45) as response:
            data = response.read()
            event["status"] = response.status
        if data.startswith(b"%PDF"): raise ValueError("PDF requires separate extraction; no binary retained")
        path = CACHE / name
        path.write_bytes(data)
        event.update(cache_path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
        if name.endswith(".html"):
            parser = Text()
            parser.feed(data.decode("utf-8", "replace"))
            textpath = path.with_suffix(".txt")
            textpath.write_text(parser.text(), encoding="utf-8")
            event["text_path"] = str(textpath)
            event["text_sha256"] = hashlib.sha256(textpath.read_bytes()).hexdigest()
        event["finding"] = "Text acquired; inspect cached file."
    except Exception as exc:
        event.update(status="error", finding=str(exc))
    return event


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("batch")
    args = parser.parse_args()
    items = json.loads(pathlib.Path(args.batch).read_text(encoding="utf-8-sig"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        events = list(executor.map(fetch, items))
    with (TOPIC / "search-events.jsonl").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(json.dumps([{k:e.get(k) for k in ("name","status","bytes","finding")} for e in events], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

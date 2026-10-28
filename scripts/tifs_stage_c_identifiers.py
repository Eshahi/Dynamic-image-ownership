"""Stdlib, metadata-only Stage C draw. Never dereferences media URLs.

No action without --execute; use only after selection rule and script are committed.
Network access is restricted to the Commons text metadata API by construction.
"""
import argparse
import datetime as dt
import hashlib
import html
import json
import pathlib
import re
import subprocess
import time
import urllib.parse
import urllib.request

ENDPOINT = "https://commons.wikimedia.org/w/api.php"
SEED_PREFIX = "tifs-stage-c-v1/20261028/"
OLD = pathlib.Path("research/encoder-transfer-20261019/final-study-20261025")
OUT = pathlib.Path("research/tifs-20261028/stage-c")


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


def plain(value):
    return " ".join(re.sub(r"<[^>]*>", "", html.unescape(value or "")).split())


def title_key(value):
    return " ".join(html.unescape(urllib.parse.unquote(value or "")).replace("_", " ").lower().split())


def url_key(value):
    value = html.unescape(urllib.parse.unquote(value or "")).rstrip("/;`")
    parts = urllib.parse.urlsplit(value)
    query = urllib.parse.urlencode([(k, v) for k, v in urllib.parse.parse_qsl(parts.query)
                                    if k.lower() not in {"utm_source", "utm_campaign", "utm_content"}])
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), query, "")).lower()


def date_order():
    start, end = dt.date(2018, 1, 1), dt.date(2025, 12, 31)
    dates = [(start + dt.timedelta(days=i)).isoformat() for i in range((end-start).days+1)]
    return sorted(dates, key=lambda date: (hashlib.sha256((SEED_PREFIX+date).encode()).hexdigest(), date))


def parse_template(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()
    match = re.search(r"\{\{\s*Potd filename\s*\|(.+?)\}\}", text, re.I | re.S)
    if match:
        first = match[1].split("|")[0].strip()
        first = re.sub(r"^1\s*=\s*", "", first).strip()
    else:
        first = text
    if re.fullmatch(r"[^{}|\n]+\.jpe?g", first, re.I):
        return "File:" + re.sub(r"^File:", "", first, flags=re.I)
    return None


def file_record(page, receipt):
    info = (page.get("imageinfo") or [{}])[0]
    if not info or page.get("missing"):
        return None
    ext = info.get("extmetadata", {})
    val = lambda key: ext.get(key, {}).get("value")
    return dict(title=page["title"], pageid=page.get("pageid"),
                revision=(page.get("revisions") or [{}])[0].get("revid"),
                receipt=receipt, url=info.get("url"), descriptionurl=info.get("descriptionurl"),
                sha1=info.get("sha1"), mime=info.get("mime"), width=info.get("width"),
                height=info.get("height"), size=info.get("size"), timestamp=info.get("timestamp"),
                licence=val("LicenseShortName"), licence_url=val("LicenseUrl"),
                licence_code=val("License"), copyrighted=val("Copyrighted"),
                usage_terms=val("UsageTerms"), artist_html=val("Artist"),
                credit_html=val("Credit"), source_html=val("Source"),
                description_html=val("ImageDescription"))


def licence_ok(row):
    label, code = row.get("licence"), row.get("licence_code")
    url = (row.get("licence_url") or "").rstrip("/")
    match = re.fullmatch(r"CC BY(-SA)? (2\.0|2\.5|3\.0|4\.0)", label or "")
    if match:
        variant = "by-sa" if match[1] else "by"
        return code == "cc-"+variant+"-"+match[2] and url in {
            scheme+"://creativecommons.org/licenses/"+variant+"/"+match[2]
            for scheme in ("http", "https")}
    if label == "CC0" and code == "cc0":
        return bool(re.fullmatch(r"https?://creativecommons.org/publicdomain/zero/1\.0(?:/deed(?:\.[a-z]+)?)?", url))
    return label == "Public domain" and code == "pd" and row.get("copyrighted") == "False"


def upstream(row):
    result = set()
    for field in ("credit_html", "source_html", "description_html"):
        for value in re.findall(r'''href\s*=\s*["']([^"']+)["']''', row.get(field) or "", re.I):
            value = html.unescape(value)
            parts = urllib.parse.urlsplit(value)
            host = (parts.hostname or "").lower()
            if parts.scheme not in {"http", "https"}:
                continue
            if any(host == h or host.endswith("."+h) for h in
                   ("creativecommons.org", "wikidata.org", "wikipedia.org")):
                continue
            if host == "commons.wikimedia.org" and "/wiki/File:" not in urllib.parse.unquote(parts.path):
                continue
            if field == "description_html" and not any(h in host for h in
                    ("flickr.com", "staticflickr.com", "cocodataset.org", "wikimedia.org")):
                continue
            result.add(url_key(value))
    return sorted(result)


def identity(row):
    return ({"wikimedia-commons:page:"+str(row.get("pageid"))},
            {title_key(row.get("title"))},
            {url_key(row.get("url")), url_key(row.get("descriptionurl"))} | set(upstream(row)),
            {str(row.get("sha1", "")).lower()})


def rejection(row, excluded, used, creators):
    if not row:
        return ["missing_file_metadata"]
    reasons = []
    width, height = row.get("width") or 0, row.get("height") or 0
    if not (row.get("mime") == "image/jpeg" and min(width, height) >= 512
            and width*height <= 40000000 and .5 <= width/max(1, height) <= 2
            and 0 < (row.get("size") or 0) <= 20000000):
        reasons.append("file_constraints")
    if not all(row.get(k) for k in ("title", "pageid", "url", "descriptionurl", "sha1")):
        reasons.append("missing_identity")
    if not licence_ok(row):
        reasons.append("licence")
    creator = plain(row.get("artist_html")).lower()
    if not creator or not re.sub(r"unknown|anonymous|author|artist|[\W_]+", "", creator):
        reasons.append("unknown_creator")
    if creator in creators:
        reasons.append("repeated_new_creator")
    for label, values, old, new in zip(("page", "title", "url", "hash"), identity(row), excluded, used):
        values = values - {""}
        if values & old:
            reasons.append("prior_"+label)
        if values & new:
            reasons.append("repeated_new_"+label)
    return reasons


def request_url(kind, titles):
    if not 1 <= len(titles) <= 50:
        raise ValueError("API batch must contain 1..50 titles")
    prefix = "Template:Potd/" if kind == "template" else "File:"
    if kind not in {"template", "file"} or any(not x.startswith(prefix) or "|" in x or "\n" in x for x in titles):
        raise ValueError("only POTD template/file titles allowed")
    params = dict(action="query", format="json", formatversion="2", titles="|".join(titles))
    if kind == "template":
        params.update(prop="revisions", rvprop="ids|content", rvslots="main")
    else:
        params.update(prop="imageinfo|revisions", rvprop="ids", redirects="1",
                      iiprop="url|size|mime|sha1|extmetadata|timestamp")
    return ENDPOINT+"?"+urllib.parse.urlencode(params)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Metadata API redirects are forbidden")


class MetadataClient:
    def __init__(self, target):
        self.target, self.last = target, 0.0
        self.deadline = time.monotonic() + 780
        self.opener = urllib.request.build_opener(NoRedirect)

    def query(self, kind, titles):
        url = request_url(kind, titles)
        name = kind+"-"+hashlib.sha256(url.encode()).hexdigest()+".json"
        path = self.target/name
        if path.exists():
            return load(path), str(path)
        if time.monotonic() + 100 > self.deadline:
            raise SystemExit("METADATA_TIME_LIMIT: resume identical command; cached responses preserve ordering")
        time.sleep(max(0, 6-(time.monotonic()-self.last)))
        self.last = time.monotonic()
        request = urllib.request.Request(url, headers={"User-Agent": "TIFS-metadata-preregistration/1.0 (academic identifier-only study)", "Accept": "application/json"})
        with self.opener.open(request, timeout=90) as response:
            if response.geturl() != url or "json" not in response.headers.get("Content-Type", ""):
                raise ValueError("unexpected metadata response URL/type")
            raw = response.read(20000001)
            if len(raw) > 20000000:
                raise ValueError("metadata response too large")
            parsed = json.loads(raw)
            if "error" in parsed or "continue" in parsed:
                raise ValueError("API error/continuation: stop rather than silently truncate")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        write(path.with_suffix(".receipt.json"), dict(url=url, response=str(path), status=200,
              timestamp_utc=dt.datetime.now(dt.timezone.utc).isoformat(), sha256=digest(path)))
        return parsed, str(path)


def pages(response):
    values = response.get("query", {}).get("pages", [])
    return list(values.values()) if isinstance(values, dict) else values


def template_rows(response, receipt):
    result = {}
    for page in pages(response):
        revisions = page.get("revisions") or [{}]
        content = revisions[0].get("slots", {}).get("main", {}).get("content", "")
        result[page["title"].removeprefix("Template:Potd/")] = dict(
            template_title=page["title"], template_page_id=page.get("pageid"),
            template_revision_id=revisions[0].get("revid"), file_title=parse_template(content),
            template_receipt=receipt)
    return result


def cache_maps(root):
    directory = root/OLD/"analysis/heldout-metadata"
    templates, files = {}, {}
    for path in sorted(directory.glob("templates-*.json")):
        templates.update(template_rows(load(path), str(path.relative_to(root))))
    for row in load(directory/"flat-file-metadata.json"):
        row["receipt"] = str((directory/row["receipt"]).relative_to(root))
        files[title_key(row["title"])] = row
    for old, new in load(directory/"file-title-aliases.json").items():
        if title_key(new) in files:
            files[title_key(old)] = files[title_key(new)]
    return templates, files


def exclusion_sets(root):
    path = root/OLD/"analysis/heldout-metadata/exclusion-identifiers.json"
    historic = load(path)
    excluded = (set(), {title_key(x) for x in historic["commons_title_tokens"]},
                {url_key(x) for x in historic["url_tokens"]},
                {x.lower() for x in historic["hash_tokens"]})
    for row in load(root/OLD/"heldout-manifest.json")["sources"]:
        record = dict(pageid=row["commons_page_id"], title=row["canonical_file_title"],
                      url=row["original_file_url"], descriptionurl=row["description_url"], sha1=row["sha1"])
        for target, values in zip(excluded, identity(record)):
            target.update(values)
        excluded[2].update(url_key(x) for x in row.get("exposed_upstream_image_identifiers", []))
    return excluded


def refresh_exclusions(root, excluded):
    """Read current copies of previously audited ledgers, never old image files."""
    directory = root/OLD/"analysis/heldout-metadata"
    main = pathlib.Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
    paths = {root/OLD/"heldout-manifest.json", root/OLD/"phase-b/phase-b-sources.json",
             root/"research/development-sources.md", root/"research/downloads.md"}
    for receipt in load(directory/"exclusion-files.json"):
        old_path = receipt["path"].replace("\\", "/")
        if "/THESIS_GUIDE_OFFLINE_v5/" in old_path:
            relative = old_path.split("/THESIS_GUIDE_OFFLINE_v5/", 1)[1]
            paths.add(main/relative)
        elif "/worktrees/" in old_path:
            relative = old_path.split("/worktrees/", 1)[1].split("/", 1)[1]
            paths.add(root/relative)
    audit = []
    for path in sorted(paths, key=str):
        if not path.is_file():
            audit.append(dict(path=str(path), status="MISSING_CURRENT_COPY_HISTORICAL_TOKENS_RETAINED"))
            continue
        if path.suffix.lower() not in {".json", ".jsonl", ".csv", ".tsv", ".md", ".txt"}:
            raise ValueError("refusing non-text identity ledger: "+str(path))
        text = path.read_text(encoding="utf-8-sig")
        excluded[3].update(x.lower() for x in re.findall(r"(?<![a-zA-Z0-9])(?:[a-fA-F0-9]{64}|[a-fA-F0-9]{40})(?![a-zA-Z0-9])", text))
        excluded[2].update(url_key(x) for x in re.findall(r'''https?://[^\s<>"']+''', text))
        audit.append(dict(path=str(path), status="READ_METADATA_TEXT_ONLY", sha256=digest(path)))
    return audit


def run(root, rule_commit):
    templates, files = cache_maps(root)
    client = MetadataClient(root/OUT/"metadata")
    excluded = exclusion_sets(root)
    exclusion_audit = refresh_exclusions(root, excluded)
    used, creators, accepted, decisions = tuple(set() for _ in range(4)), set(), [], []
    order = date_order()
    for start in range(0, len(order), 50):
        dates = order[start:start+50]
        missing = ["Template:Potd/"+date for date in dates if date not in templates]
        if missing:
            response, receipt = client.query("template", missing)
            templates.update(template_rows(response, str(pathlib.Path(receipt).relative_to(root))))
        titles = list(dict.fromkeys(templates.get(date, {}).get("file_title") for date in dates))
        missing = [x for x in titles if x and title_key(x) not in files]
        if missing:
            response, receipt = client.query("file", missing)
            receipt = str(pathlib.Path(receipt).relative_to(root))
            for page in pages(response):
                files[title_key(page["title"])] = file_record(page, receipt)
            for alias in response.get("query", {}).get("normalized", [])+response.get("query", {}).get("redirects", []):
                if title_key(alias["to"]) in files:
                    files[title_key(alias["from"])] = files[title_key(alias["to"])]
        for date in dates:
            template = templates.get(date, {})
            row = files.get(title_key(template.get("file_title")))
            reasons = rejection(row, excluded, used, creators)
            if not template.get("file_title"):
                reasons.append("ambiguous_template")
            decision = dict(date=date, rank=len(decisions)+1, reasons=reasons)
            decisions.append(decision)
            if not reasons:
                index = len(accepted)+1
                accepted.append(dict(row, **template, date=date, date_order_rank=decision["rank"],
                    date_order_sha256=hashlib.sha256((SEED_PREFIX+date).encode()).hexdigest(),
                    source_uid="wikimedia-commons:page:"+str(row["pageid"]), selection_index=index,
                    assignment="primary" if index<=120 else "reserve",
                    assignment_index=index if index<=120 else index-120,
                    creator_group=plain(row.get("artist_html")).lower(),
                    exposed_upstream_image_identifiers=upstream(row),
                    acquisition_status="NOT_DOWNLOADED", raw_sha256=None, canonical_pixel_hash=None))
                creators.add(plain(row.get("artist_html")).lower())
                for target, values in zip(used, identity(row)):
                    target.update(values)
            if len(accepted) == 160:
                break
        write(root/OUT/"candidate-decisions.json", decisions)
        print("METADATA_PROGRESS", len(decisions), "dates", len(accepted), "eligible", flush=True)
        if len(accepted) == 160:
            break
    used_receipts = sorted({x[k] for x in accepted for k in ("receipt", "template_receipt")})
    receipt_files = [str(x.relative_to(root)) for x in (root/OLD/"analysis/heldout-metadata").glob("*request*.json")]
    receipt_files += [str(x.relative_to(root)) for x in (root/OUT/"metadata").glob("*.receipt.json")]
    result = dict(schema="tifs-stage-c-identifiers-v1", status="COMPLETE_IDENTIFIER_POOL_ONLY" if len(accepted)==160 else "INSUFFICIENT",
        population="Commons POTD 2018-01-01..2025-12-31, full 2922-date frame", seed=20261028,
        selection_rule_commit=rule_commit, selection_rule_sha256=digest(root/OUT/"selection-rule.md"),
        primary_count=min(120,len(accepted)), reserve_count=max(0,len(accepted)-120),
        acquisition_status="NOT_DOWNLOADED", execution_approval=False, scientific_outputs_observed=False,
        receipt_files=[dict(path=x, sha256=digest(root/x)) for x in used_receipts+receipt_files],
        historical_exclusion_inventory=str(OLD/"analysis/heldout-metadata/exclusion-identifiers.json"),
        current_exclusion_files=exclusion_audit,
        limitations=["Exact metadata identities only; mirrors and near duplicates may remain.",
                     "Exact creator strings do not establish distinct human creators.",
                     "Raw/canonical hash exclusions and updated later-ledger audit required before scientific use.",
                     "Cached metadata is reused at original receipt time, not represented as freshly queried."], sources=accepted)
    write(root/OUT/"heldout-manifest.json", result)
    print(result["status"], result["primary_count"], result["reserve_count"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--rule-commit")
    args = parser.parse_args()
    if not args.execute:
        print("NO_ACTION: metadata selection/network requires --execute and --rule-commit")
        return
    root = args.repo.resolve()
    if not args.rule_commit or not re.fullmatch(r"[a-f0-9]{40}", args.rule_commit):
        parser.error("exact 40-character committed rule revision required")
    for name in [(OUT/"selection-rule.md").as_posix(), "scripts/tifs_stage_c_identifiers.py"]:
        frozen = subprocess.check_output(["git", "show", args.rule_commit+":"+name], cwd=root)
        if frozen.replace(b"\r\n", b"\n") != (root/name).read_bytes().replace(b"\r\n", b"\n"):
            parser.error("rule/script differ from requested committed revision: "+name)
    run(root, args.rule_commit)


if __name__ == "__main__":
    main()

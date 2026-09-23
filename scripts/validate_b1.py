"""Read-only documentary checks; does not accept claims or execute experiments."""
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def rows(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    response_dir = "thesis-runs/d916749c/research/d916749c-B1-002/"
    old = read_json(response_dir + "response-consolidated.json")
    current = read_json(response_dir + "response-final.json")
    check(current["papers"][:8] == old["papers"], "Earlier cards changed")
    check(current["evidence"][:13] == old["evidence"], "Earlier evidence changed")
    cards, evidence = current["papers"], current["evidence"]
    check(len(cards) == 12 and len(evidence) == 17, "Unexpected corpus counts")
    for field in ("paper_id", "doi", "canonical_url", "citation_key"):
        check(len({p[field].casefold() for p in cards}) == len(cards), field + " duplicates")
    for card in cards:
        artifact = (ROOT / card["inspection"]["artifact"]).resolve()
        check(artifact.is_relative_to(ROOT), "Inspection escaped repository")
        check(hashlib.sha256(artifact.read_bytes()).hexdigest() == card["inspection"]["sha256"],
              "Inspection checksum mismatch: " + card["paper_id"])
    ledger = [json.loads(line) for line in (ROOT / "research/evidence-ledger.jsonl")
              .read_text(encoding="utf-8").splitlines()]
    check(ledger == evidence, "Root ledger differs from response")
    matrix = rows("research/literature-matrix.csv")
    generated = rows("research/literature/final/literature-matrix.csv")
    check(len(matrix) == len(generated), "Matrix count mismatch")
    for root_row, generated_row in zip(matrix, generated):
        check(all(root_row[k] == v for k, v in generated_row.items()), "Matrix metadata mismatch")
        required = {"source", "status", "embedding_space", "detector", "content_binding",
                    "data", "attacks", "metrics", "locator", "limitation", "image_dct",
                    "latent_dct", "model_free", "inversion_free"}
        check(all(root_row.get(k) for k in required), "Missing comparison fields")
        check(root_row["limitation"] == root_row["limitations"], "Shifted limitation column")
        dct_values = {"YES", "NO", "NO_IN_INSPECTED_PATH", "NO_DCT_IN_DESCRIBED_METHOD",
                      "UNKNOWN_NOT_INSPECTED", "NOT_ESTABLISHED", "NOT_APPLICABLE", "BASE_SCHEME_DEPENDENT"}
        check(root_row["image_dct"] in dct_values and root_row["latent_dct"] in dct_values,
              "Invalid or shifted DCT distinction")
    claims = rows("research/claims.csv")
    mapping = rows("research/claim-evidence-map.csv")
    check(len(mapping) == 42, "Wrong original claim count")
    check({(r["proposal_claim_id"], r["kind"]) for r in mapping} ==
          {(r["id"], r["kind"]) for r in claims}, "Claim ID/kind mismatch")
    evidence_ids = {e["claim_id"] for e in evidence}
    check(len(evidence_ids) == len(evidence), "Evidence ID duplicate")
    for row in mapping:
        check(set(filter(None, row["evidence_ids"].split(";"))) <= evidence_ids,
              "Unknown mapped evidence ID")
        check(row["thesis_status"] in {"UNTESTED", "UNRESOLVED", "REQUIREMENT_NOT_RESULT"},
              "Unexpected scientific acceptance")
    bib = (ROOT / "research/references.bib").read_text(encoding="utf-8")
    # Parse the deliberately restricted emitted BibTeX subset, not arbitrary BibTeX.
    # Reject unconsumed syntax rather than silently accepting a partial parse.
    clean = re.sub(r"(?m)^%.*$", "", bib).strip()
    entry = re.compile(r"@misc\{([A-Za-z0-9_:-]+),\s*((?:[a-z]+\s*=\s*\{[^{}]*\}\s*,?\s*)+)\}", re.S)
    parsed = list(entry.finditer(clean))
    check(not entry.sub("", clean).strip(), "Unparsed BibTeX syntax")
    keys = [m.group(1) for m in parsed]
    for match in parsed:
        fields = re.findall(r"([a-z]+)\s*=\s*\{([^{}]*)\}", match.group(2))
        check(len(dict(fields)) == len(fields), "Duplicate BibTeX field")
        check({"title", "author", "year", "url", "doi"} <= dict(fields).keys(), "Missing citation fields")
    check(len(keys) == 11 and set(keys) == {p["citation_key"] for p in cards if p["verification"] == "verified"},
          "Bibliography verification/count mismatch")
    searches = rows("research/search-results.csv")
    check(len(searches) == 51 and len({r["search_id"] for r in searches}) == 51,
          "Search chronology ID/count mismatch")
    check(all(None not in row and all(row.values()) for row in searches), "Malformed search row")
    for row in searches:
        check(all(row.get(k) for k in ["title", "authors", "year", "doi_or_url", "query_id", "inclusion_status"]),
              "Missing search-contract field")
    audit = rows("research/citation-audit.csv")
    check(len(audit) == 6, "Proposal citation audit incomplete")
    check(all(all(row.get(k) for k in ["citation_key", "verified_fields", "source_url", "access_depth"])
              for row in audit), "Missing audit-contract field")
    print(json.dumps({"valid": True, "cards": len(cards), "evidence": len(evidence),
                      "proposal_claims": len(mapping), "bibliography_entries": len(keys),
                      "search_rows": len(searches), "scientific_acceptance": False}))


if __name__ == "__main__":
    main()

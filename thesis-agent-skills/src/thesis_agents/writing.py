"""Conservative claim-to-prose assembly, with explicit missing-evidence markers."""
import json
from pathlib import Path
from .common import ContractError, digest, fresh_dir, identifier, parser, read, timestamp, validate, write
from .audit import load_jsonl
from datetime import datetime, timezone

def write_section(claims,audit,chapter,out,fmt="markdown",final=False,acceptance=None):
    identifier(chapter)
    for claim in claims: validate(claim,"claims")
    classes={c["claim_id"]:c["classification"] for c in audit["claims"]}
    if final:
        if audit["blocking"] or any(classes.get(c["claim_id"])!="verified" for c in claims): raise ContractError("Cannot finalize: blocking/missing audit support")
        from .common import object_digest
        if not acceptance or acceptance.get("decision")!="approve" or acceptance.get("chapter")!=chapter or acceptance.get("audit_sha256")!=object_digest(audit) or acceptance.get("claims_sha256")!=object_digest(claims): raise ContractError("Finalization requires explicit human acceptance of these exact claims and audit")
        if timestamp(acceptance["expires_at"])<=datetime.now(timezone.utc): raise ContractError("Chapter acceptance expired")
    root=Path(out); target=root/"chapters"/(chapter+(".tex" if fmt=="latex" else ".md"))
    if target.exists(): raise ContractError("Preserving existing chapter; choose a new section output or request revision explicitly")
    inventory=root/"evidence/claim-inventory.jsonl"
    old=load_jsonl(inventory) if inventory.exists() else []
    if {c['claim_id'] for c in old}&{c['claim_id'] for c in claims}: raise ContractError("Claim ID already exists in thesis inventory")
    lines=[("\\section{"+chapter+"}" if fmt=="latex" else "# "+chapter),"" ,"Status: "+("human-accepted" if final else "draft; requires human review"),""]
    for claim in claims:
        supported=classes.get(claim["claim_id"])=="verified"
        marker="" if supported else " TODO:EVIDENCE TODO:CITATION"
        lines.append(f"{claim['kind']}: {claim['text']}{marker}")
        lines.append(("% " if fmt=="latex" else "<!-- ")+"claim="+claim["claim_id"]+"; evidence="+",".join(claim["evidence_ids"]+claim["run_ids"])+( "" if fmt=="latex" else " -->")); lines.append("")
    write(target,"\n".join(lines))
    write(inventory,"".join(json.dumps(c,ensure_ascii=False)+"\n" for c in old+claims),force=inventory.exists())
    # No invented bibliography entries. Existing bibliography is preserved verbatim.
    if not (root/"references.bib").exists(): write(root/"references.bib","% No verified bibliography supplied. Merge approved citation keys verbatim before submission.\n")
    for folder in ("figures","tables"):
        if not (root/folder/"provenance.json").exists(): write(root/folder/"provenance.json",{"artifacts":[],"rule":"Only copy approved analysis outputs with provenance checksums"})
    return {"chapter":chapter,"status":"final" if final else "draft","unsupported_claims":[c["claim_id"] for c in claims if classes.get(c["claim_id"])!="verified"]}

def main():
    p=parser("Assemble a bounded thesis section from a traceable claim inventory")
    p.add_argument("claims"); p.add_argument("audit"); p.add_argument("--chapter",required=True); p.add_argument("--out",required=True); p.add_argument("--format",choices=["markdown","latex"],default="markdown"); p.add_argument("--final",action="store_true"); p.add_argument("--acceptance")
    a=p.parse_args(); return write_section(load_jsonl(a.claims),read(a.audit),a.chapter,a.out,a.format,a.final,read(a.acceptance) if a.acceptance else None)

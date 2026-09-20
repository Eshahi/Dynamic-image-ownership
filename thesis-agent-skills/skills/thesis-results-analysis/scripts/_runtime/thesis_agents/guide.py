"""Parse literal JS data only; never evaluate the guide or load a browser."""
import re
from pathlib import Path
from .common import ContractError, digest, parser, write
from .plan import github_issue_seed, reduce_guide

class LiteralParser:
    def __init__(self, text, pos=0):
        self.text, self.pos = text, pos

    def ws(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def value(self):
        self.ws()
        c = self.text[self.pos]
        if c in "\"'`":
            return self.string()
        if c in "[{":
            self.pos += 1
            result = [] if c == "[" else {}
            end = "]" if c == "[" else "}"
            self.ws()
            while self.text[self.pos] != end:
                if c == "{":
                    self.ws()
                    if self.text[self.pos] in "\"'`":
                        key = self.string()
                    else:
                        m = re.match(r"[A-Za-z_$][\w$]*", self.text[self.pos:])
                        if not m:
                            raise ContractError("Unsupported object key")
                        key = m.group(); self.pos += len(key)
                    self.ws()
                    if self.text[self.pos] != ":":
                        raise ContractError("Expected literal property")
                    self.pos += 1
                    if key in result:
                        raise ContractError("Duplicate literal key")
                    result[key] = self.value()
                else:
                    result.append(self.value())
                self.ws()
                if self.text[self.pos] == end:
                    break
                if self.text[self.pos] != ",":
                    raise ContractError("Executable expression in structured data")
                self.pos += 1; self.ws()
            self.pos += 1
            return result
        m = re.match(r"(?:true|false|null|-?\d+(?:\.\d+)?)\b", self.text[self.pos:])
        if not m:
            raise ContractError("Unsupported non-literal data")
        import json
        self.pos += len(m.group())
        return json.loads(m.group())

    def string(self):
        quote = self.text[self.pos]; self.pos += 1
        result = ""
        while self.pos < len(self.text):
            c = self.text[self.pos]; self.pos += 1
            if c == quote:
                return result
            if quote == "`" and c == "$" and self.text[self.pos:self.pos+1] == "{":
                raise ContractError("Template interpolation is not literal data")
            if c == "\\":
                c = self.text[self.pos]; self.pos += 1
                if c in ("u", "x"):
                    n = 4 if c == "u" else 2
                    result += chr(int(self.text[self.pos:self.pos+n], 16)); self.pos += n
                    continue
                c = {"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f"}.get(c,c)
            result += c
        raise ContractError("Unterminated literal string")

def extract(text, marker):
    matches = list(re.finditer(marker, text))
    if len(matches) != 1:
        raise ContractError(f"Expected one structured data declaration for {marker}; found {len(matches)}")
    return LiteralParser(text, matches[0].end()).value()

def import_guide(source):
    text = Path(source).read_text(encoding="utf-8")
    phases = extract(text, r"\bH=(?=\[\{id:`contract`)")
    contracts = extract(text, r'\bAi=(?=\{"write-1":)')
    groups = extract(text, r"\bza=(?=\[\{id:`spec`)")
    tasks, warnings = [], []
    for phase in phases:
        warnings.extend(f"{phase.get('id','unknown')}: preserved unsupported phase field {k}" for k in sorted(set(phase)-{"id","number","title","subtitle","duration","risk","purpose","tasks","gate","deliverables"}))
        for task in phase["tasks"]:
            warnings.extend(f"{task.get('id','unknown')}: preserved unsupported task field {k}" for k in sorted(set(task)-{"id","title","action","output"}))
            contract = contracts.get(task["id"])
            if contract is None:
                raise ContractError("Task has no contract: " + task["id"])
            extra = set(contract) - {"needs", "execution", "inputs", "steps", "files", "checks", "failure"}
            warnings.extend(f"{task['id']}: preserved unsupported contract field {k}" for k in sorted(extra))
            tasks.append({"id": task["id"], "title": task["title"], "phase_id": phase["id"], "dependencies": contract["needs"], "gates": phase["gate"], "evidence_requirements": contract["checks"], "inputs": contract["inputs"], "outputs": contract["files"], "execution": contract["execution"], "original_task": task, "original_contract": contract})
    ids = [t["id"] for t in tasks]
    if len(ids) != len(set(ids)) or set(contracts) != set(ids):
        raise ContractError("Task/contract identity mismatch")
    for task in tasks:
        if set(task["dependencies"]) - set(ids):
            raise ContractError("Unknown dependency")
    pending = {t["id"]: set(t["dependencies"]) for t in tasks}; order = []
    while pending:
        ready = [i for i, deps in pending.items() if deps <= set(order)]
        if not ready:
            raise ContractError("Dependency cycle")
        for i in ready:
            order.append(i); del pending[i]
    return {"schema_version": "1.0", "source_sha256": digest(source), "source_name": Path(source).name, "tasks": tasks, "phases": phases, "technical_groups": groups, "topological_order": order, "warnings": warnings, "availability": {"proposal": "not supplied", "results": "not supplied"}}

def main():
    p = parser("Import supported offline guide literal data without executing JavaScript")
    p.add_argument("source"); p.add_argument("output")
    p.add_argument("--profile", choices=["source-58", "thesis-38"], default="source-58")
    p.add_argument("--issues-output")
    p.add_argument("--force", action="store_true")
    a = p.parse_args(); source = import_guide(a.source)
    data = source if a.profile == "source-58" else reduce_guide(source)
    write(a.output, data, a.force)
    if a.issues_output:
        if a.profile != "thesis-38":
            raise ContractError("Issue seed output requires --profile thesis-38")
        write(a.issues_output, github_issue_seed(data), a.force)
    return {"profile": a.profile, "tasks": len(data["tasks"]), "source_tasks": len(source["tasks"]), "issues": len(data["tasks"]) if a.issues_output else 0, "warnings": source["warnings"]}

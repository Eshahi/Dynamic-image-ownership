"""Fail unless every boolean check of `m1b_prepare_package.py rerun-check` passed (records such as item 4/5 are not booleans)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
checks = json.loads(text[text.index("{"):text.rindex("}") + 1])["checks"]
print(json.dumps(checks, indent=1))
bad = [k for k, v in checks.items() if v is False]
if bad:
    sys.exit("rerun-check failed: " + ", ".join(bad))
print("rerun-check: all pass")

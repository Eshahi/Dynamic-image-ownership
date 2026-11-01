# WP6 affected-floor rerun

JUDGMENT: **PASS. FLOOR-B1 CLOSED. Zero remaining blockers in the affected floor review.** This independent closure is a research-review proposal, not a Claude ruling, a claim that all journal floors were met, or permission to execute further science.

SOURCE: Fresh reviewer `wp6_floor_rerun`, Codex, 2026-11-01, with no inherited conversation. Reviewed commit **`59dbcfc8e7da02b890c30913aac782aee446cca3`**, branch `codex/f5-components-20261101`. Compared the initial reviewed baseline `8458e1571a8b301847f50f28742a488f8c8ec84c` and correction `811f880c7fde955d8d3c830baa430c6450a1e818`. MAIN's authoritative STATE was read once. The thesis-evidence-audit skill was applied within this one-file assignment.

## Independent closure evidence

DERIVED: I reduced the actual `papers` arrays obtained with `git show`, rather than accepting the author's totals. They are identical across all three revisions. Their canonical JSON SHA-256, using sorted keys and compact separators, is `705afe7c2f521e2eea3f5e3446850b3ed3ff0b0343e5e3ddd9ae59be4eba1cc0`. This is a hash of the manifest array representation, not of paper PDFs or experimental inputs. No new paper, assignment, class or card was introduced by the correction.

SOURCE/DERIVED: The baseline declared 47 works/67 assignments and K03 TOP=2 even though its array already contained TrustMark. The actual correction changes those fields to 48/68 and K03 TOP=3, changes nine pending statuses to accepted access-limited, records the three accepted-scope met-floor statuses, and preserves the required scope restrictions. See `literature/paper-assignments.json:516` for the TrustMark entry, `:551` for K03, `:606` for K08, `:617` for K09, and `:661` for the corrected totals. The correction diff contains no change within the `papers` array.

DERIVED: All twelve independently calculated per-class counts agree with both the current manifest's `floors` fields and `literature/floor-accounting.md`. The query figures below also match the canonical table; this rerun checks their metadata consistency, not fresh execution of those historical searches.

| Component | Q1J / required | TOP / required | Recorded substantive queries | Current accepted status |
|---|---:|---:|---:|---|
| K01 | 4/5 | 3/3 | 42 | Access-limited; journal floor unmet |
| K02 | 3/5 | 3/3 | 31 | Access-limited; journal floor unmet |
| K03 | 0/5 | 3/3 | 35 | Access-limited; journal floor unmet |
| K04 | 2/5 | 3/3 | 45 | Access-limited; journal floor unmet |
| K05 | 2/5 | 3/3 | 38 | Access-limited; journal floor unmet |
| K06 | 2/5 | 3/3 | 36 | Access-limited; journal floor unmet |
| K07 | 1/5 | 3/3 | 35 | Access-limited; journal floor unmet |
| K08 | 3/5 | 3/3 | 38 | Access-limited; journal floor unmet |
| K09 | 5/5 | 3/3 | 33 | Met only under accepted statistical-calibration scope |
| K10 | 4/5 | 3/3 | 30 | Access-limited; journal floor unmet |
| K11 | 3/3 | 3/3 | 23 | Met with accepted trust/version/access caveats |
| K12 | 3/3 | 3/3 | 32 | Met with accepted evaluation-validity scope |

DERIVED: There are **48 unique works and 68 assignments**: **23 unique Q1J works / 32 journal assignments**, and **25 unique TOP works / 36 conference assignments**. Every paper has at most two component assignments, with no duplicated component within a paper. Every referenced card path exists. All 48 unique-work rows in the canonical ledger match the manifest's name, class and component tuple. Every journal row identifies SJR or JCR and its metric year. All twelve manifest rows retain four successful scholarly surfaces. The nine accepted access-limited cases each retain at least 30 substantive queries; K11's 23 queries are not represented as a 30-query exhaustion.

SOURCE/DERIVED: **32/56 journal slots and 36/36 TOP slots** are filled, leaving **24 unread journal slots**. Gate 2 R1's opening 35/36 TOP total is followed by its explicit TrustMark acceptance, which makes K03 3/3 and the total 36/36; the ledger explains this at `literature/floor-accounting.md:22`. The correction does not reinterpret accepted exhaustion as complete coverage.

## Scope restrictions and unread leads

SOURCE: I inspected the affected source locators, not only `reviews/DISPOSITIONS.md`:

- TrustMark: Gate 2 R1 and `literature/cards/K03.md:3` expressly supersede the historical intake's withheld-slot wording. The K03-T1 card identifies the final ICCV main paper, its methods/experiments and main-paper figure/table locators. Its supplement remains unread, undownloaded and supplies no claim. The corrected manifest and `literature/floor-accounting.md:28` retain that exact restriction. There is no new supplement-inspection claim.
- K08: the counted works are Padhi, Ozkaya and Li; their card sections concern dual authentication or tamper recovery and explicitly lack independent-encoder T3 evidence. Vaidya and Singh remain excluded by the root disposition. The manifest and `literature/floor-accounting.md:33` state that no counted K08 journal bears on T3.
- K09: its five journal entries are Safe Testing, the e-value-merging paper, mean/variance e-processes, heavy-tailed aggregation and focal confidence. The manifest's shorthand “Emerging e-values” maps to K09-J02, *The only admissible way of merging arbitrary e-values*; it is not another counted work. The manifest and `literature/floor-accounting.md:34` retain the statistical-foundations-only scope and state that no Q1 watermark-reader journal was read.
- `literature/UNREAD-LEADS.md:5` and its fourteen numbered rows give **zero additional floor credit**. Two IEEE Access leads are explicitly partial, with missing table cells; twelve lack complete inspected methods/experiments. These are not fourteen newly inspected works. I checked their listed identities against the 48-work assignment list: none is counted. TrustMark, already read/countable author-version cases, and the already inspected Tang/DiffMark works are expressly excluded from this acquisition queue.

JUDGMENT: The corrected metadata satisfies the concrete minimum fix in FLOOR-B1. `reviews/DISPOSITIONS.md` accurately says closure was pending before this fresh report; that historical pending status is not evidence of a remaining scientific or accounting mismatch.

## Original review completion and preserved limits

SOURCE/DERIVED: I read the original review's actual S01-S20 rows, their primary full-text URLs, method/result locators, publication/version qualifiers and V1-V9 venue table. I independently counted **20 distinct sample IDs and 20 distinct primary full-text URLs**, mapped them to **20 distinct counted works: 11 Q1J and nine TOP**, and checked their manifest assignments. Coverage is K01 S01/S02/S17; K02 S03/S04/S18; K03 S11/S19; K04 S05/S06; K05 S06/S07/S08; K06 S05/S07/S09/S10; K07 S08/S10; K08 S15/S16; K09 S13/S14/S19/S20; K10 S14/S15/S16; K11 S12/S20; K12 S13. Thus all twelve components are documented without a third assignment or double-counted version. TrustMark's failed reopen and other failed accesses are expressly excluded from those twenty.

SOURCE: `reviews/floor.md:43` documents independent venue checks with metric/year/category and third-party or rehosted status. Its S12 at `:78` documents reopening the ORBilu full publisher PDF for K11 remote-object authentication, including sections 3.3/4.1 and Table 4. The exact primary ranking-provider confirmation remains unverified, as does the separately disclosed Information Fusion 4/204 category rank. Machine Learning, AJSE and PLOS ONE remain SJR-Q1/JCR-Q2 cases. This rerun does not upgrade any ranking, manuscript version, final-byte identity or missing PDF hash.

SOURCE: The original review's TQ/TK2/T0 sections at `reviews/floor.md:90` document scripts and actual saved-input checks, not merely summary reads. TQ identifies the Stage 2 clean-72 journal record and its inventory/hash/PSNR linkage; TK2 names and rehashes the saved feature file, retains five failed rows and recomputes 125 available pairs; T0 identifies Stage 2 and Phase A detect records, a blocked record, and the 6,480-row/88-cell reduction. Its limits remain explicit: no independent TQ pixel replay, not every Phase A native/attack record sampled, overlapping cohorts, no newly claimed Stage 2 input rehash, and no new encoder or reader pass. I verified that these checks are documented; I did not perform them again or count them as this reviewer's experiments.

DERIVED: `git diff --name-only 8458e15 59dbcfc` restricted to the card directory, floor ledger, unread-lead queue, venues, TQ/TK2/T0 scripts and their result directories is empty. These underlying materials are unaffected by FLOOR-B1. The fresh assignment requires affected-metadata closure, so the original twenty-work online audit and pixel-related work were not repeated. **This rerun performs zero new online paper checks and zero pixel tests.**

JUDGMENT: FLOOR-W1, W2 and W3 remain accepted warnings: incomplete/access-limited journal coverage, ranking/version limitations, and bounded exploratory inference. No primary-source, security, independent-encoder efficacy, human-visibility or population claim is strengthened by this closure. Claude retains the final gate decision.

## Commands and execution limits

SOURCE: Read-only Git inspection included `git status --short`, `git rev-parse HEAD`, `git log -5 --oneline`, `git diff 8458e15 811f880 --stat`, `git diff 811f880 59dbcfc --stat`, and `git diff 8458e15 811f880 -- research/f5-components-20261101/literature/paper-assignments.json`. The full selected non-review diff through `59dbcfc` was also read; its remaining changes are source-link/text repairs and additional reporting limitations. Files were inspected with UTF-8 `Get-Content`, bounded `Select-Object`, and targeted `rg`; no AGENTS.md reread occurred.

SOURCE: Three short read-only Python reductions ran via PowerShell here-string stdin using the exact interpreter command:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -I -B -
```

SOURCE: They used only `json`, `subprocess` for read-only Git, `hashlib`, `re`, `pathlib` and `collections`; one process and zero worker children per reduction, with reported command wall times approximately .32, .32 and .29 seconds. The first independently recalculated revisions/counts/ledger rows/leads; the second mapped the twenty sample works and checked unaffected paths/locators. The exact stdin of the final consolidated assertion run is below; it exited 0 and printed PASS with the class totals and array hash reported above.

```python
import json, subprocess, re, hashlib
from pathlib import Path
from collections import Counter
r = Path('research/f5-components-20261101')
p = (r / 'literature/paper-assignments.json').as_posix()
versions = [json.loads(subprocess.check_output(['git','show',v+':'+p])) for v in ['8458e15','811f880','59dbcfc']]
a, b, c = versions
assert a['papers'] == b['papers'] == c['papers']
ps = c['papers']; assert len(ps) == len({p['paper'] for p in ps}) == c['unique_papers'] == 48
assert sum(len(p['components']) for p in ps) == c['assignments'] == 68
assert max(len(p['components']) for p in ps) == 2
assert all(len(set(p['components'])) == len(p['components']) for p in ps)
for f in c['floors']:
    n = Counter(p['class'] for p in ps if f['component'] in p['components'])
    assert (n['Q1J'],n['TOP']) == (f['Q1J'],f['TOP'])
assert sum(f['status'].startswith('ACCEPTED ACCESS-LIMITED') for f in c['floors']) == 9
assert sum(f['status'].startswith('PAPER FLOORS MET') for f in c['floors']) == 3
ledger = (r/'literature/floor-accounting.md').read_text(encoding='utf-8')
rows = [tuple(x.strip() for x in line.split('|')[1:-1]) for line in ledger.splitlines() if re.match(r'^\| .+ \| (Q1J|TOP) \| ',line)]
assert len(rows) == 48
assert {(x[0],x[1],tuple(re.findall(r'K\d\d',x[2]))) for x in rows} == {(p['paper'],p['class'],tuple(p['components'])) for p in ps}
assert all(re.search(r'(SJR|JCR) 20\d\d',x[3]) for x in rows if x[1]=='Q1J')
review = (r/'reviews/floor.md').read_text(encoding='utf-8')
samples = [x for x in review.splitlines() if re.match(r'^\| S\d\d ',x)]
assert len(samples) == len({re.findall(r'\]\((https?[^)]+)\)',x.split('|')[2])[0] for x in samples}) == 20
leads = [x for x in (r/'literature/UNREAD-LEADS.md').read_text(encoding='utf-8').splitlines() if re.match(r'^\| \d+ \|',x)]
assert len(leads) == 14
print('PASS: array identity; 48 works/68 assignments; max 2; 12 floor counts; 9 access-limited/3 met; 48 ledger rows; 20 distinct full-text URL records; 14 acquisition leads')
print('unique classes',dict(Counter(p['class'] for p in ps)))
print('assignment classes',dict(Counter(p['class'] for p in ps for _ in p['components'])))
print('canonical papers SHA256',hashlib.sha256(json.dumps(ps,sort_keys=True,separators=(',',':')).encode()).hexdigest())
```

SOURCE: No experiment script, science interpreter, reader, writer, diffusion, GPU, server, install or download was executed. No image, held-out data or Phase B journal was opened. Only this review file was written; no source correction, protected output, F6 artifact, judge/RULING file, commit or push was made by this reviewer.

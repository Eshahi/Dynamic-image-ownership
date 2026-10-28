# Stage S frozen screen analysis

Implemented in `scripts/tifs_stage_s_analyze.py`; all imports are Python standard
library or `tifs_common`. It reads saved JSON/JSONL only. It never opens an
image, runs an encoder/reader/metric, downloads assets, or imports scientific
packages. No scientific result is asserted by this implementation note.

CLI: `python scripts/tifs_stage_s_analyze.py --out RUN_ROOT/screen --config research/tifs-20261028/stage-s/frozen-config.json`.
Optional `--destination` changes the default `RUN_ROOT/screen/analysis` output
folder. Exit codes are 0 GO, 2 SCIENTIFIC_KILL, 3 RESOURCE_STOP, 4 INCOMPLETE.
GO permits proposing fresh Stage C only; it is not execution or publication
approval. The analyzer rejects rehearsal identity, source/config hash mismatch,
and analyzer code differing from the run's identity. A missing identity cannot
produce GO. It does not rehash image artifacts: the producer manifest performs
artifact validation, while analysis binds every reader/quality row to the
producer's saved artifact hash.

## Evidence and decisions

The independent full planned inventory contains 128 clean, 1536 native, 896
threat, and 1024 secondary producer identities; 6272 detector identities and
3584 quality identities. Detection inventory includes the unmarked output under
each of the seven method readers. Required detection/quality rows are planned
even for failed or blocked producer outputs. Missing producer selection leaves
the threat inventory unenumerated and incomplete. Prepared pairs must have the
frozen donor order and exactly the sixteen disjoint target identifiers. Extra
IDs, overlapping shards, incomplete append tails, failed statuses and unusable
hash-bound evidence prevent completeness. Missing calls are never negatives.

For C and J separately, the analyzer emits source-by-source three-seed majority
bounds, aggregate lower/upper source counts, and conservative candidate-minus-
comparator gains. The lower gain is candidate lower minus comparator upper;
the upper gain is candidate upper minus comparator lower. The foreign absolute
bar, both ablation gains, F5 gains and retained R0 loss bar are independent.
Every new writer has the clean F and strict clean quality gates. Candidate/F5
paired LPIPS and PSNR median gates require all sixteen valid pairs. Missing or
invalid metrics cannot pass; an infinite-PSNR pair with undefined finite delta
stays unresolved. Clean identity PSNR is valid only as JSON null with the
explicit `psnr_infinite` flag.

Endpoints are recalculated from emitted `calls[owner].raw` and each producer's
`payload.q` / `payload.h`, using hexadecimal string or integer code conventions.
C requires a read semantic carrier and suspect content consistency; J additionally
requires exact original q equality. An unavailable target is unknown when a
carrier was read, never a fabricated mismatch. A/Q/C/J/H/D/F and D AND F are
reported separately; q/h are evaluator references only. Unchanged F5 dispatch
and suspect-derived semantics remain operational detector side information.

C0 and true wrong-owner C/F checks cover clean, native and threat outputs. Baseline
events are descriptive and do not kill F6. For all seven frozen T4/T5 conditions
and four frozen read modes, valid recipient-relative metrics determine
eligibility; eligible whole-recipient D AND F events are counted separately
from donor Q delivery, unconditional pair events and acceptance among observed
Q-delivered pairs. Only combined-mode events enter the scientific gate; the
other three binding ablations are diagnostic. Unknown quality can conceal an eligible event and therefore
blocks completeness. Ineligible threats are counted as excluded, never as
observed eligible negatives. Published patch/sham, known-clean residual and
unmodified-target conditions have separate rows. Human operational-distinctness
labels and donor references do not establish lawful ownership or binding
generalization.

The eight standard distortions and external-baseline carrier presence are
descriptive. Their result values never enter scientific gates; their planned
inventory must nevertheless be complete for GO. External known-message and
wrong-message presence are not relabelled as owner or instance authentication.
The secondary table separately reports marked positive, C0 C/F and true
wrong-owner C/F rows with `selection_weight=0`. Only the clean/native/threat C0 and
wrong-owner checks in the primary negative table can fail scientific selection.

A gate fails only when observed evidence proves failure: an optimistic upper
count/gain below its frozen bar; an observed strict-quality or false-event
violation; or a complete paired-median violation. Such a SCIENTIFIC_KILL takes
precedence over later resource stop or missing evidence. Otherwise a recorded
resource stop takes precedence; unresolved evidence is INCOMPLETE. GO requires
all gates and complete inventory. A printed zero-event 95% upper source bound
is explicitly illustrative under hypothetical exchangeable source sampling,
not a population or cryptographic security guarantee.

## Outputs and validation

`analysis.json` contains complete structured results, side-information statements,
inventory missing IDs, unusable evidence, lower/upper bounds and limitations.
CSV tables cover gates, inventory, native aggregate/source bounds, gains, clean
quality/F, paired medians, negatives, threat delivery/binding, secondary and
external baseline descriptions. Nested CSV cells contain strict JSON.

`Journal(path, read_only=True)` is safe for concurrent snapshots: it never
creates paths, repairs, truncates, appends, or accepts any unterminated final
record, even syntactically valid JSON. Writable recovery preserves malformed
unterminated bytes in a unique torn sidecar before truncating; valid complete
JSON at writable EOF retains the legacy newline-finalization behavior. Invalid
newline-terminated records, duplicate keys and nonfinite JSON are rejected.
Single writer ownership per journal is still required.

Validation uses MAIN `.thesis-build/venv/Scripts/python.exe -I` and synthetic
dictionaries/temporary JSON only. Tests cover full planned GO, absent/blocked
outputs, exact q versus C, conservative comparator bounds, strict clean/median/F
bars, eligible/ineligible/missing threat quality, candidate versus baseline
events, secondary zero weight, hash mismatch, overlapping shards, incomplete
append tails and verdict precedence. These are implementation checks, not
scientific rehearsal evidence. Gradients, native replay, image quantization,
reader output schema compatibility and actual resource fit require the later
authorized server rehearsal.

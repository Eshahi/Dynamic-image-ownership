# Round 2 inventory and conservative budget

Computed before any Stage S output, 2026-10-29, using only stdlib arithmetic on the frozen configuration. Machine-readable values: `round2-cost.json`. These are operation counts and budget inequalities, not measured execution times. No scientific timing occurred locally.

| Operation | Screen, 16 donors | Rehearsal, 2 donors | Increment over Round 1 screen |
|---|---:|---:|---:|
| Clean saved images | 144 | 18 | 16 |
| Native attempts | 1,728 | 216 | 192 |
| Threat attempts | 1,008 | 126 | 112 |
| Secondary attempts | 1,152 | 144 | 128 |
| All producer identities | 4,032 | 504 | 448 |
| Detector rows | 7,168 | 896 | 896 |
| Quality rows | 4,032 | 504 | 448 |

One donor/arm has 28 outputs: one clean, twelve native, seven threats, eight secondary. Eight marked methods each read their own 448 outputs and all 448 C0 outputs, giving 7,168 rows. VINE-B adds 896 rows containing **1,792 owner queries**; rehearsal adds 112 rows/224 queries. Every owner query exhausts 41,449 semantic candidates, so the screen can require **74,276,608 candidate checks**. No additional model/checkpoint or image pool is acquired. F6 marks remain 48 screen plus six rehearsal; VINE-B adds sixteen plus two retained VINE embeds. Writer checkpointing trades recomputation time for lower activation memory and must be measured anew.

There is **no cross-item decoder result cache**. The earlier draft's 256-entry cache could fit most rehearsal queries but evict in the full screen, making an eightfold extrapolation optimistic. Removing it leaves the mathematics unchanged and makes every query include the full fixed search. Reuse of a single network/CLIP pass for the two owners within each item is retained and is the same in both inventories. Integer candidate accounting is not a CPU timing measurement.

Screen RGB8 frames total **3,170,893,824 bytes (3.17 GB)** before compression; combined screen/rehearsal frames total **3,567,255,552 bytes (3.57 GB)**. These counts exclude random tapes, native intermediates, model caches, package installation and logs. PNG size is not presumed smaller; use measured rehearsal artifacts and temporary peaks with 1.5 scaling and a 20% filesystem reserve. The retained 76 GB volume and nominal 48.6 GB model total do not establish free space.

## Keep the 15-hour ceiling

Let E be all paid seconds already elapsed at forecast time, O the measured loading/invocation allowance, and W the complete two-source rehearsal variable-work sum, including prepare, every VINE-B operation and all readers/quality/hashes. The existing conservative rule remains:

```
E + O + 1.5 * (16/2) * W + 3,600 <= 54,000
W <= (50,400 - E - O) / 12
```

E already includes setup, idle time, rehearsal, failed attempts and interrupts. It is not reset when the screen starts. In the unattainably favorable case of no setup/loading/idle cost and E=W, W can be at most **3,876.9 seconds (64.62 minutes)**. Real permitted W is smaller. This is an analytic feasibility bound, not a prediction that the rehearsal finishes within that time. The two-source sample and 1.5 factor remain an engineering forecast, not a mathematical worst-case guarantee over all sources; measured per-operation maxima, serial loads, remaining-time checks and retrieval reserve govern actual continuation.

Incremental VINE-B cost cannot be inferred from VINE-R presence success. Under full-screen 1.5 allowance plus paid rehearsal, each extra native-unit second contributes 312 seconds; each extra bound detector-row second contributes 1,456 seconds; each extra quality-unit second contributes 728 seconds. Additional embeds/transforms/threats, CLIP/hash calculations and model loads are also charged. Bounded decoding alone contributes 2,912 times its per-owner-query seconds. These coefficients expose the budget impact without inventing a machine speed.

At the brief's assumed USD .45–.60/hour, fifteen hours is USD **6.75–9.00**, excluding separately charged storage/network; actual price must be the user-approved one. No smallest larger cap can be defensibly stated without F6 checkpointed timings and the new decoder timings. **Decision: keep 15 hours.** If the intact measured forecast fails, stop with RESOURCE_STOP and return the measured required cap for a later user decision. Do not quietly remove VINE-B, reduce n/steps, change decoding radius, weaken negatives or increase the bill.

The former 50-hour Stage C proposal is not automatically updated by this addition. Its article claim must be prospectively amended to include the successful Stage S comparative route and VINE-B, with new inventory/power/cost checks before approval or any fresh outputs. Existing metadata-only identifiers remain unused.

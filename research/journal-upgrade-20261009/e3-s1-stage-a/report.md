# E3-S1 two-source callable and supplier result

2026-10-10. The frozen development screen passes; this is not full end-to-end M1a. [CPU analysis](analysis.json) independently reproduces the saved-call endpoints with zero issues or numerical discrepancies.

| Fixed endpoint | Result |
|---|---:|
| Fresh F5 supplier succeeds | 2/2 |
| Strict clean quality and exact q/h/full acceptance | 2/2 |
| SD1.5 VAE semantic and exact checked q | 2/2 |
| SDXL VAE semantic and exact checked q | 2/2 |
| SD1.5 DDIM .1 S/Q/J | 6/6 planned |
| SD1.5 DDIM .2 S/Q/J | 5/6 planned, one safety block |
| Lost available historical S/J identities | 0 |
| Observed negative detections | 0/45 distinct recorded calls |

Development sources are 6012 and 147498. Both suppliers yield their respective historical q/h pair. Each source therefore has one distinct new writer observation described by both historical-target and S1 arms, not two independent successes. The first source takes the quality-retain branch; the second takes the one allowed .8 contraction. Writer durations are 90.656 and 51.750 seconds, excluding separately measured bootstrap and shared model loading. No construction or threshold is chosen from an attacked outcome.

The 45 observed negatives comprise six C0 clean/VAE calls, six wrong-beta clean/VAE calls, and 33 wrong-owner T3 calls. Three planned wrong-owner calls are unavailable from the blocked C1 image. There is no C0 T3 generation in this preliminary screen. The 62 distinct saved-image detector observations reuse two development sources and are not independent population samples. All eleven available T3 intended messages are recovered exactly. Raw BCH errors and all failed/unavailable slots remain in the analysis.

## Execution history and cost

The original run `20261010-1506-e3-s1-stage-a` at `27e2c84` failed before any T3 generation because the older global regeneration wrapper rejects strength .1. Both source construction and clean/VAE stages were already complete. That raw failure remains unchanged. The narrow completion at `7029dce`, `20261010-1513-e3-s1-t3-completion`, reuses those completed observations and executes only the twelve previously unexecuted official T3 identities. It uses the same explicit pinned kwargs as the established development adapter; safety remains enabled.

Parent-inclusive durations are 266.9426822 and 28.8166676 seconds, totalling **295.7593498 seconds** within the original 1800-second cap. Peak allocated GPU memory is 7,068,902,400 bytes and RAM is 3,583,315,968 bytes. USD 0. Analysis code is `2eadfe0`. The original process remains failed while the combined scientific screen passes; no observed attack was retried or omitted.

This verifies the fixed callable and fresh bootstrap route on two already used development sources. It is not unseen-source/model/seed generalization, a population false-positive estimate or proof of cryptographic ownership. Continue the preregistered [twelve-source development completion](../e3-s1-full-development.md), including fresh C1-dependent T3/T4/T5 evidence before qualifying the end-to-end candidate.

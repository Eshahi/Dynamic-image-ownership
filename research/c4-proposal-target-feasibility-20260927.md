# C4 proposal-number and reconstruction feasibility checkpoint

Issue #18 / PR #67. User on2026-09-27 explicitly requested stronger-model review
of the method and attainability of proposal numbers. Independent review dispatched
as /root/astra_method_feasibility with confirmed gpt-6-astra/high through the
existing collaboration facility, not a paid API call or a claimed parent-model
switch. Evidence-audit and literature-synthesis skills distinguish observation,
source report, inference and missing evidence. Original proposal/targets unchanged.

## What the original numbers actually mean

Source: inputs/proposal-text.md:275-285 and unchanged claims.csv METRIC-01..07.

| Quantity | Authority | Current evidence / feasibility classification |
| --- | --- | --- |
| PSNR>35dB | Proposal acceptable-quality description, operationalized as strict per-image target | Current one-source VAE22.482789/baseDDIM20.396195 fail. Unproven for improved route; not proved impossible. |
| SSIM>0.9 | Proposal quality description | VAE0.742910/base0.667903 fail in same source; no population ceiling established. |
| LPIPS<0.1 | Proposal quality description | VAE0.058493 passes; base0.119847 fails. Combined target still fails. |
| Detection/robustness/forgery ACC/AUC | Proposal named metrics, no numerical target supplied | No accepted blind detection or attack efficacy evidence. Do not invent proposal80%/1%. |
| TPR>=80%, FPR<=1% with one-sided95% bounds | Later A4 documentary engineering choices, not proposal numbers | Unproven performance; independently eligible groups and calibration constrain inference. |
| Extraction in milliseconds / faster than SEAL | Proposal measurement/comparison obligation, no fixed latency/speedup number | Full CLIP/canonical/q-h/candidate/DCT pipeline must be timed, not DCT kernel alone. |
| COCO1000,DIV2K800+100,DiffusionDB5000 / native2K | Proposal coverage commitments | Counts are data obligations, not performance or native2K resource evidence. Unchanged. |

A4 does not define a study-level quality pass fraction; paper mean quality is not
an every-image conjunction. LPIPS implementations/backbones and SSIM conventions
must match before cross-paper quantitative comparisons. Never replace source I
by matched reconstruction Iref as the primary quality reference.

## Reproducible arithmetic, not another image/model experiment

From the retained reviewed report reports/dev/c4-reconstruction-dev-001/result.md:
PSNR35 corresponds to normalized RGB MSE0.00031622776601683794 and RGB8 RMSE
4.534612495599253. Because the inequality is strict, error must be below these.
Current VAE MSE0.0056457428439589145 requires >17.8534-fold reduction; unchanged
base MSE0.009128101388585818 requires >28.8656-fold reduction. Bigger VRAM alone
cannot alter these already completed deterministic output values.

Exact inversion/replay to the unchanged encoded latent can reproduce D(E(I)),
but is not a mechanism for recovering detail missing from that reconstruction.
This is an algorithmic inference, not a universal lower bound on all decoder
latents or all VAEs. Source-latent refinement asks a different, testable question.

An objective conflict deserves explicit experimental separation: current config
lambda_q=lambda_r=1 penalizes MSE to both source and poor control. Without decoder
constraints or watermark terms, their minimizer is (I+Iref)/2, giving source MSE
MSE(I,Iref)/4 and26.416795dB for this control. This is not a bound on the full
watermark objective; it shows why an equal control anchor can oppose source repair.
Do not silently remove the anchor or reweight the historical run.

## Primary-source contrary and favorable evidence

New pinned public HTML/validated paper cards and ledger are in the separate
quality-feasibility literature topic. No model/data downloaded or source code adopted.

- [FreqMark v1](https://arxiv.org/html/2410.20824v1), Table1/Figure4:31.20dB/0.854
  versus VAE31.22/0.879 on its generated prompt subset. Its DINOv2 detector differs
  from ours. This warns against treating ordinary latent reconstruction as35dB-ready.
- [VINE v1](https://arxiv.org/html/2410.18775v1), Tables1-2:40.51/.9954/.0029 for
  VINE-B and37.34/.9934/.0063 for VINE-R. These are means, not universal guarantees.
  Trained skips/fine-tuned components, neural extraction and resolution scaling
  prevent drop-in transfer. They refute blanket quality impossibility, not prove
  our method. The final proceedings PDF exceeded browser size; v1 is disclosed.
- The previously pinned [TRDI v1](https://arxiv.org/html/2606.15389v1), Table1,
  reports SD1.5 ReNoise+TRDI22.67 and GNRI+TRDI22.32dB. It is evidence against
  assuming scheduler inversion alone closes our source gap, not proof it never can.
- New LatentShield publisher search reports a favorable number, but full text
  returned403. It remains an uninspected lead, not accepted performance evidence.

## Statistical targets also have attainable and unattainable cases

For independent negatives and zero false matches, the one-sided95% upper bound
is1-0.05**(1/N);299 groups are needed for<=1%. AtN300 the best bound is0.993608%,
so a single error can break the goal. AtN251 it is1.186425% even with zero errors:
that particular cell cannot establish1% with this method, though the detector's
true rate could be lower. AtN757 it is0.394955%. Existing split/group receipts,
not raw image count/extra attacks/seeds, determine which case applies. Validation
calibration does not supply independent test confidence. No grouping/threshold
or data commitment changed to make a bound favorable.

## Immediate focus and boundaries

Prioritize the paired source-preservation question before further GNRI/scheduler
complexity or paid GPU: a complete bounded fixed-decoder refinement package versus
retained VAE/source, then exact inverse/replay preservation if refinement helps.
Keep four separate feasibility obligations: reconstruction quality, latent-to-DCT
controllability, q/h recovery and geometric synchronization. High quality alone
does not imply a surviving mark, blind extraction, authentication or security.

The ordinary refinement library is independently reviewed but has no learned
results. Strict fp32-radius refusals are numerical failures, not evidence of a
decoder ceiling; account for them before interpreting any future run. Only a full
reviewed exact clean manifest may request new scientific execution approval.
If fixed-decoder quality remains poor, prepare a disclosed source-detail-preserving
decoder/reconstruction amendment, with weights/rights/training/time and effect on
latent embedding/blindDCT reviewed. Never quietly insert pixel residual marks or
neural verification and call it the original method. Do not lower35/.9/.1 to
convert failure into success. This checkpoint claims no repair or C4 closure.

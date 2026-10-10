# Readability diagnostic and bounded screen

Exploratory twelve-source development evidence only. The native frozen detector is unchanged. q_target is the recorded intended semantic payload; h_target is the confirmed saved-clean native-decoded operational instance target. Original embedded h is unknown. No held-out inference, population FPR estimate, independent diffusion claim or official gate transition follows.

Diagnostic `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-0950-readability-diagnostic-final` at commit `6a25cd5c5d1ac1c19e63fca6ab96f4cbf6a44844`: {'ok': 12}; 38.9690 seconds. The fixed inventory is twelve unique planned IDs. Failed/missing rows retain the denominator. Earlier protocol-aborted diagnostics are retained elsewhere and are not primary evidence.

| Condition | Native checked | Exact intended q + read | Joint exact q + read + content | Native h-target exact + read | Joint q/h exact + read | Min fixed-q score |
|---|---:|---:|---:|---:|---:|---:|
| clean | 12/12 | 10/12 | 10/12 | 12/12 | 10/12 | 11.6676 |
| sd15_vae | 12/12 | 11/12 | 11/12 | 0/12 | 0/12 | 11.4953 |
| sdxl_vae | 10/12 | 3/12 | 3/12 | 0/12 | 0/12 | 5.7862 |

Reused unchanged-pixel quality: strict PSNR >35 dB, SSIM >.9, LPIPS <.1 on 12/12. Full new clean eligibility (quality, both native reads, exact declared q/h and both_match): 10/12. Negative any-channel detections: 0/72 calls (36 C0 alpha and 36 C1 beta across three conditions, reusing twelve sources). Quality/negative source: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-0903-journal-vae`.

Normalized correlation is dot(w,p)/norm(p), with 320 chips. Bit gaps are correct-minus-alternative dot products; normalized gaps divide by sigma=max(norm(p)/sqrt(320),1e-8). Alpha is signed dot(w,p-b)/320; carrier gain divides by clean alpha and preserves sign. Host and mark gap components sum to the observed gap; they are an exact measured finite-difference decomposition, not a causal or linear-VAE model. A searched score above threshold can coexist with wrong q.

| Source | Condition | q errors | h errors | q_bound | Fixed-q / searched score | Signed gain | Alignment | Minimum gap |
|---|---|---:|---:|---|---:|---:|---:|---:|
| 1675 | clean | 0 | 0 | aaa4173c | 16.0869 / 16.0869 | 1.0000 | 1.0000 | 3.2007 |
| 1675 | sd15_vae | 0 | 13 | 2aa4363c | 15.9391 / 15.9391 | 1.0012 | 0.9902 | 3.0542 |
| 1675 | sdxl_vae | 1 | 13 | 2aa4173c | 11.3061 / 11.5186 | 0.4397 | 0.8823 | -3.5307 |
| 4795 | clean | 0 | 0 | aa440fb8 | 14.8172 / 14.8172 | 1.0000 | 1.0000 | 0.6115 |
| 4795 | sd15_vae | 0 | 13 | aa440eb8 | 14.4814 / 14.4814 | 0.9880 | 0.9905 | 0.5509 |
| 4795 | sdxl_vae | 5 | 14 | 2a440eb8 | 7.5180 / 7.8628 | 0.3685 | 0.8360 | -3.2954 |
| 6012 | clean | 1 | 0 | ba84b4b8 | 11.6676 / 11.7967 | 1.0000 | 1.0000 | -2.2389 |
| 6012 | sd15_vae | 1 | 15 | 9a84b438 | 11.4953 / 11.6247 | 1.0043 | 0.9910 | -2.3036 |
| 6012 | sdxl_vae | 6 | 16 | ba84b4b8 | 5.7862 / 6.7448 | 0.4248 | 0.8544 | -7.6724 |
| 25394 | clean | 0 | 0 | cbc5a678 | 15.5383 / 15.5383 | 1.0000 | 1.0000 | 4.0466 |
| 25394 | sd15_vae | 0 | 18 | cbc5a638 | 15.4277 / 15.4277 | 1.0231 | 0.9947 | 4.3201 |
| 25394 | sdxl_vae | 0 | 11 | cbc4a678 | 9.7368 / 9.7368 | 0.4106 | 0.8630 | 0.4406 |
| 80932 | clean | 0 | 0 | 2aeda634 | 15.0008 / 15.0008 | 1.0000 | 1.0000 | 2.1821 |
| 80932 | sd15_vae | 0 | 15 | 2beda434 | 14.9783 / 14.9783 | 1.0388 | 0.9950 | 2.2334 |
| 80932 | sdxl_vae | 2 | 14 | 2aeda434 | 8.3960 / 8.4561 | 0.3943 | 0.8497 | -0.4717 |
| 109798 | clean | 0 | 0 | f1c4a474 | 15.5300 / 15.5300 | 1.0000 | 1.0000 | 3.1368 |
| 109798 | sd15_vae | 0 | 14 | f1c4b474 | 15.4307 / 15.4307 | 0.9659 | 0.9908 | 2.4377 |
| 109798 | sdxl_vae | 1 | 13 | f1c4a474 | 10.7500 / 10.8391 | 0.4977 | 0.9212 | -1.4401 |
| 134882 | clean | 1 | 0 | a2c4b53c | 14.4719 / 14.4732 | 1.0000 | 1.0000 | -0.0260 |
| 134882 | sd15_vae | 0 | 15 | a2c4b53c | 13.9302 / 13.9302 | 0.9628 | 0.9853 | 0.3411 |
| 134882 | sdxl_vae | 5 | 12 | a2c0b53c | 7.5124 / 8.3134 | 0.4088 | 0.8914 | -6.8053 |
| 147498 | clean | 0 | 0 | b9c49734 | 17.1047 / 17.1047 | 1.0000 | 1.0000 | 7.4050 |
| 147498 | sd15_vae | 0 | 13 | b9869634 | 16.9677 / 16.9677 | 1.0177 | 0.9881 | 8.2483 |
| 147498 | sdxl_vae | 0 | 15 | bfc49636 | 14.7441 / 14.7441 | 0.4210 | 0.9164 | 0.6048 |
| 177015 | clean | 0 | 0 | aa4da938 | 15.7416 / 15.7416 | 1.0000 | 1.0000 | 2.1310 |
| 177015 | sd15_vae | 0 | 16 | aa4c2938 | 15.6594 / 15.6594 | 1.0065 | 0.9948 | 2.6791 |
| 177015 | sdxl_vae | 1 | 15 | aa4c2938 | 10.7241 / 10.8692 | 0.4096 | 0.8712 | -1.9829 |
| 190676 | clean | 0 | 0 | 32c6a524 | 14.9925 / 14.9925 | 1.0000 | 1.0000 | 2.9081 |
| 190676 | sd15_vae | 0 | 17 | 3206a524 | 14.9745 / 14.9745 | 1.0132 | 0.9882 | 2.9581 |
| 190676 | sdxl_vae | 2 | 12 | 3246a52c | 8.3467 / 8.4296 | 0.3807 | 0.8412 | -0.9582 |
| 468505 | clean | 0 | 0 | abeca730 | 14.9048 / 14.9048 | 1.0000 | 1.0000 | 1.3582 |
| 468505 | sd15_vae | 0 | 15 | abeca730 | 14.7015 / 14.7015 | 1.0256 | 0.9949 | 1.3539 |
| 468505 | sdxl_vae | 2 | 13 | 0b6da430 | 8.9941 / 9.4746 | 0.4169 | 0.8697 | -4.3269 |
| 499768 | clean | 0 | 0 | bad2bc2c | 15.1599 / 15.1599 | 1.0000 | 1.0000 | 3.3650 |
| 499768 | sd15_vae | 0 | 18 | bad2b46c | 15.0412 / 15.0412 | 1.0205 | 0.9885 | 3.8752 |
| 499768 | sdxl_vae | 0 | 13 | bad2bc2c | 8.9227 / 8.9227 | 0.3700 | 0.8200 | 0.8231 |

## Failed bit geometry

Bit indices follow the recorded 0–31 segment order. Changes below compare with the same source's clean intended-q geometry. Negative observed gaps explain the selected alternative descriptively; a clean error need not be newly caused by a reconstruction. All raw and normalized gaps, native flags, q_now/h_now and q_bound are retained in the JSON.

| Source / condition / bit | Host gap | Mark gap | Observed gap | Host change | Mark change | Descriptive change |
|---|---:|---:|---:|---:|---:|---|
| 1675 / sdxl_vae / 0 | -8.7818 | 5.2511 | -3.5307 | -1.3257 | -10.5103 | both |
| 4795 / sdxl_vae / 7 | -1.5669 | 1.4353 | -0.1317 | 0.5533 | -1.2965 | reduced mark contribution |
| 4795 / sdxl_vae / 18 | -2.3878 | 1.9781 | -0.4097 | 0.0639 | -7.8979 | reduced mark contribution |
| 4795 / sdxl_vae / 20 | -2.7746 | 2.4074 | -0.3673 | -0.4910 | -5.3593 | both |
| 4795 / sdxl_vae / 27 | -7.8575 | 4.5621 | -3.2954 | -0.0804 | -8.6362 | both |
| 4795 / sdxl_vae / 29 | -4.9633 | 4.5667 | -0.3966 | -0.6255 | -9.3109 | both |
| 6012 / clean / 3 | -10.2190 | 7.9801 | -2.2389 | 0.0000 | 0.0000 | pre-existing or other geometry |
| 6012 / sd15_vae / 3 | -10.1452 | 7.8416 | -2.3036 | 0.0738 | -0.1385 | reduced mark contribution |
| 6012 / sdxl_vae / 3 | -11.6350 | 3.9626 | -7.6724 | -1.4160 | -4.0175 | both |
| 6012 / sdxl_vae / 6 | -2.2039 | 1.5755 | -0.6283 | -0.4562 | -2.7548 | both |
| 6012 / sdxl_vae / 10 | -3.0672 | 1.9645 | -1.1028 | -0.2949 | -2.1924 | both |
| 6012 / sdxl_vae / 11 | -6.4276 | 5.7590 | -0.6685 | 2.0042 | -6.6820 | reduced mark contribution |
| 6012 / sdxl_vae / 14 | -3.0157 | 2.9952 | -0.0205 | -0.4565 | -3.4011 | both |
| 6012 / sdxl_vae / 26 | -6.8774 | 3.0610 | -3.8164 | 0.8059 | -7.8530 | reduced mark contribution |
| 80932 / sdxl_vae / 10 | -1.1068 | 0.6350 | -0.4717 | -0.5712 | -2.0827 | both |
| 80932 / sdxl_vae / 23 | -4.3799 | 4.0042 | -0.3756 | -1.4198 | -10.0497 | both |
| 109798 / sdxl_vae / 2 | -7.5393 | 6.0993 | -1.4401 | -0.7187 | -5.0189 | both |
| 134882 / clean / 7 | -3.2577 | 3.2317 | -0.0260 | 0.0000 | 0.0000 | pre-existing or other geometry |
| 134882 / sdxl_vae / 2 | -10.4240 | 3.6187 | -6.8053 | -0.3804 | -6.7744 | both |
| 134882 / sdxl_vae / 7 | -2.8860 | 0.5486 | -2.3374 | 0.3717 | -2.6830 | reduced mark contribution |
| 134882 / sdxl_vae / 14 | -2.6775 | 2.3850 | -0.2925 | -0.3161 | -5.8356 | both |
| 134882 / sdxl_vae / 18 | -8.1449 | 5.9772 | -2.1677 | -1.0427 | -7.9931 | both |
| 134882 / sdxl_vae / 24 | -4.9772 | 4.2468 | -0.7304 | 0.7418 | -8.0766 | reduced mark contribution |
| 177015 / sdxl_vae / 18 | -5.1930 | 3.2101 | -1.9829 | 0.0119 | -9.2245 | reduced mark contribution |
| 190676 / sdxl_vae / 1 | -7.9345 | 7.5964 | -0.3381 | -2.6466 | -10.6416 | both |
| 190676 / sdxl_vae / 18 | -5.6080 | 4.6498 | -0.9582 | -1.0414 | -9.2947 | both |
| 468505 / sdxl_vae / 2 | -5.7340 | 3.1938 | -2.5403 | -0.3223 | -3.5762 | both |
| 468505 / sdxl_vae / 21 | -8.4744 | 4.1475 | -4.3269 | 0.9482 | -9.5989 | reduced mark contribution |

clean: mean signed alpha 1.0187, mean signed host projection 0.0108, mean signed carrier gain 1.0000, mean displacement alignment 1.0000; 2 nonpositive gaps, 2 decoded q errors across 384 bits. Failed-gap descriptions: {'pre-existing or other geometry': 2}. Maximum independently recomputed host-plus-mark gap discrepancy 7.105427357601002e-15. These geometry averages are descriptive and do not rank population robustness.

sd15_vae: mean signed alpha 1.0241, mean signed host projection 0.0138, mean signed carrier gain 1.0056, mean displacement alignment 0.9910; 1 nonpositive gaps, 1 decoded q errors across 384 bits. Failed-gap descriptions: {'reduced mark contribution': 1}. Maximum independently recomputed host-plus-mark gap discrepancy 3.552713678800501e-15. These geometry averages are descriptive and do not rank population robustness.

sdxl_vae: mean signed alpha 0.4226, mean signed host projection 0.0077, mean signed carrier gain 0.4119, mean displacement alignment 0.8680; 25 nonpositive gaps, 25 decoded q errors across 384 bits. Failed-gap descriptions: {'both': 17, 'reduced mark contribution': 8}. Maximum independently recomputed host-plus-mark gap discrepancy 3.552713678800501e-15. These geometry averages are descriptive and do not rank population robustness.

## R1–R4 screen

Run `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-0951-readability-screen` at `6a25cd5c5d1ac1c19e63fca6ab96f4cbf6a44844`: completed.

| Config | Status counts (12 planned) | Strict quality | Clean eligible | SD1.5 joint | SDXL joint | Negative detections / evaluated | Advancement |
|---|---|---:|---:|---:|---:|---:|---|
| R1 | {'ok': 12} | 12/12 | 9/12 | 11/12 | 3/12 | 0 / 72 | killed |
| R2 | {'ok': 12} | 12/12 | 9/12 | 12/12 | 12/12 | 0 / 72 | killed |
| R3 | {'ok': 12} | 12/12 | 9/12 | 12/12 | 12/12 | 0 / 72 | killed |
| R4 | {'ok': 12} | 12/12 | 8/12 | 12/12 | 12/12 | 0 / 72 | killed |

Ranked survivors: []. Rank order is SDXL joint exact count, minimum reconstructed fixed-q score, lower mean clean LPIPS, then R1–R4 order. A VAE-screen survivor still requires matched T3 continuity and T4/T5/delivered-binding follow-up; this report cannot promote a final method.

Measured physical steps: 1228; accounted logical steps: 4800/4800; skipped stationary steps: 3572. Active optimization 2116.6710 s; evaluation 304.4250 s; invocation wall duration 2455.6560 s. Resumed wall durations may exclude earlier invocations; active counters are cumulative. Proxy LPIPS <=.30/<=.20 subsets retain twelve-source denominators in JSON; human admissibility remains missing.

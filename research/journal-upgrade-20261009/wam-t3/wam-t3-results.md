# Exploratory WAM matched T3

Inventory: 216/216 recorded; unique complete: True; operational complete: True. Call errors: 0; stored-field disagreements: 0.

| Arm / strength | Exact / planned | Valid / planned | Nonempty bit accuracy (n) | All-planned zero stress | Empty | Complement exact | Source majority |
|---|---:|---:|---:|---:|---:|---:|---:|
| native_w2/0.1 | 3/36 | 34/36 | 0.884375 (30) | 0.7370 | 4 | 0 | 0/12 |
| native_w2/0.2 | 0/36 | 34/36 | 0.7776442307692307 (26) | 0.5616 | 8 | 0 | 0/12 |
| quality_w0p5/0.1 | 0/36 | 33/36 | 0.7232142857142857 (7) | 0.1406 | 26 | 0 | 0/12 |
| quality_w0p5/0.2 | 0/36 | 34/36 | 0.46875 (3) | 0.0391 | 31 | 0 | 0/12 |
| shared_C0/0.1 | 0/36 | 33/36 | 0.375 (1) | 0.0104 | 32 | 0 | 0/12 |
| shared_C0/0.2 | 0/36 | 33/36 | 0.375 (1) | 0.0104 | 32 | 0 | 0/12 |

Each marked arm has 72 planned attempts. Shared C0 has 72 total attempts, decoded once and shared across arms. Source majority requires exact recovery on at least two of three planned seeds; unavailable seeds count as no success.

- native_w2/0.1: statuses {'ok': 34, 'safety_blocked': 2}; missing/duplicate 0; observed calls across all statuses 34.
- native_w2/0.2: statuses {'ok': 34, 'safety_blocked': 2}; missing/duplicate 0; observed calls across all statuses 34.
- quality_w0p5/0.1: statuses {'ok': 33, 'safety_blocked': 3}; missing/duplicate 0; observed calls across all statuses 33.
- quality_w0p5/0.2: statuses {'ok': 34, 'safety_blocked': 2}; missing/duplicate 0; observed calls across all statuses 34.
- shared_C0/0.1: statuses {'ok': 33, 'safety_blocked': 3}; missing/duplicate 0; observed calls across all statuses 33.
- shared_C0/0.2: statuses {'ok': 33, 'safety_blocked': 3}; missing/duplicate 0; observed calls across all statuses 33.

## Matched identities

| Arm / strength / comparator / endpoint | WAM / 36 | Comparator / 36 | Common observed | WAM / common | Comparator / common | WAM only / comparator only |
|---|---:|---:|---:|---:|---:|---:|
| native_w2/0.1/frozen_F5_native/Q | 3/36 | 27/36 | 34/36 | 3/34 | 27/34 | 0 / 24 |
| native_w2/0.1/frozen_F5_native/J | 3/36 | 27/36 | 34/36 | 3/34 | 27/34 | 0 / 24 |
| native_w2/0.2/frozen_F5_native/Q | 0/36 | 20/36 | 34/36 | 0/34 | 20/34 | 0 / 20 |
| native_w2/0.2/frozen_F5_native/J | 0/36 | 20/36 | 34/36 | 0/34 | 20/34 | 0 / 20 |
| quality_w0p5/0.1/frozen_F5_native/Q | 0/36 | 27/36 | 33/36 | 0/33 | 27/33 | 0 / 27 |
| quality_w0p5/0.1/frozen_F5_native/J | 0/36 | 27/36 | 33/36 | 0/33 | 27/33 | 0 / 27 |
| quality_w0p5/0.2/frozen_F5_native/Q | 0/36 | 20/36 | 34/36 | 0/34 | 20/34 | 0 / 20 |
| quality_w0p5/0.2/frozen_F5_native/J | 0/36 | 20/36 | 34/36 | 0/34 | 20/34 | 0 / 20 |

All planned comparison counts retain blocked/failed/missing identities; common-observed rows are descriptive paired availability subsets. Their endpoints differ and do not establish superiority.

## Clean quality and attack distortion

- Prior clean native_w2: exact 12/12; strict PSNR >35, SSIM >.9, LPIPS <.1: 12/12; completed 12/12.
- Prior clean quality_w0p5: exact 10/12; strict PSNR >35, SSIM >.9, LPIPS <.1: 12/12; completed 12/12.
- native_w2/0.1, quality_source: psnr_db n=34, mean=23.823323087572096, range=18.935821265716875..26.07314743279559; ssim_rgb n=34, mean=0.6471406186638118, range=0.4387688220050451..0.7730256208662287; lpips n=34, mean=0.12237903607242248, range=0.08337834477424622..0.20787526667118073.
- native_w2/0.1, quality_input: psnr_db n=34, mean=23.73599672095634, range=18.89830397525538..26.001523306359044; ssim_rgb n=34, mean=0.6421337057327952, range=0.4359159676310146..0.7683458328640682; lpips n=34, mean=0.11811589033288114, range=0.08023561537265778..0.19772736728191376.
- native_w2/0.2, quality_source: psnr_db n=34, mean=22.345667739416573, range=18.202247132424528..24.850343051804966; ssim_rgb n=34, mean=0.6036679832671751, range=0.39090846571185955..0.7472415606795402; lpips n=34, mean=0.1663865462383803, range=0.10348647832870483..0.2672470211982727.
- native_w2/0.2, quality_input: psnr_db n=34, mean=22.27127920560346, range=18.16716840171398..24.789517313130833; ssim_rgb n=34, mean=0.5972203235654095, range=0.38776308617603716..0.7419717795878297; lpips n=34, mean=0.1653675307684085, range=0.10296791791915894..0.2642303705215454.
- quality_w0p5/0.1, quality_source: psnr_db n=33, mean=23.939247086945315, range=18.992845238081543..26.122560585149614; ssim_rgb n=33, mean=0.658485605616255, range=0.4414390289749963..0.7777843430196377; lpips n=33, mean=0.11001437654097874, range=0.07233297824859619..0.18651697039604187.
- quality_w0p5/0.1, quality_input: psnr_db n=33, mean=23.930848152795377, range=18.990095108618334..26.116598141222607; ssim_rgb n=33, mean=0.6573250747988495, range=0.4410873875576875..0.7772070115944564; lpips n=33, mean=0.11025622870885965, range=0.07378266006708145..0.1867343932390213.
- quality_w0p5/0.2, quality_source: psnr_db n=34, mean=22.412658525345815, range=18.21362866560169..24.865564789227527; ssim_rgb n=34, mean=0.6138842503520424, range=0.3883922508433661..0.7521351985327549; lpips n=34, mean=0.15510105319759426, range=0.09494389593601227..0.2565784454345703.
- quality_w0p5/0.2, quality_input: psnr_db n=34, mean=22.406408964582422, range=18.21180483668724..24.862400121249507; ssim_rgb n=34, mean=0.6127097129240733, range=0.38803116233032436..0.7515615441505221; lpips n=34, mean=0.15563692590769598, range=0.09616631269454956..0.25644195079803467.
- shared_C0/0.1, quality_source: psnr_db n=33, mean=23.942870565229335, range=18.982643957803443..26.090239864197905; ssim_rgb n=33, mean=0.6591662246040102, range=0.44035347367065336..0.7780436537506424; lpips n=33, mean=0.10933512449264526, range=0.07197266817092896..0.1862017661333084.
- shared_C0/0.1, quality_input: psnr_db n=33, mean=23.942870565229335, range=18.982643957803443..26.090239864197905; ssim_rgb n=33, mean=0.6591662246040102, range=0.44035347367065336..0.7780436537506424; lpips n=33, mean=0.10933512449264526, range=0.07197266817092896..0.1862017661333084.
- shared_C0/0.2, quality_source: psnr_db n=33, mean=22.43385167552392, range=18.19767041409124..24.844818505349437; ssim_rgb n=33, mean=0.6138932756535715, range=0.38706912140980093..0.75121292698032; lpips n=33, mean=0.15617123133305347, range=0.09592446684837341..0.2552434802055359.
- shared_C0/0.2, quality_input: psnr_db n=33, mean=22.43385167552392, range=18.19767041409124..24.844818505349437; ssim_rgb n=33, mean=0.6138932756535715, range=0.38706912140980093..0.75121292698032; lpips n=33, mean=0.15617123133305347, range=0.09592446684837341..0.2552434802055359.

Fresh budget: 117.4210000000021 s / 900 s; measured overrun False.

## Limits

- Exploratory twelve-source development sample; no significance test or population inference.
- No matched-FPR superiority: native WAM mask/bit decoder has no separately calibrated image presence endpoint.
- WAM public 32-bit source-ID message differs from F5 q/h construction and content binding; complement is not wrong-owner authentication.
- Q is exact semantic-code recovery; J adds semantic content_match, not full q/h acceptance.
- Shared C0 pixels/calls and repeated source seeds are shared evidence, not independent replicates.
- Zero-scored unavailable/empty all-planned bit accuracy is a stress score, not measured accuracy for unavailable outputs.
- Quality distributions are descriptive, no quality filtering; human admissibility remains missing.
- MIT SA-1B checkpoint is not the paper COCO checkpoint; no held-out or lifecycle gate verdict.

Statistics JSON retains all inventory discrepancies, quality distributions, paired identities and endpoint denominators. No probe summary was used for counts.

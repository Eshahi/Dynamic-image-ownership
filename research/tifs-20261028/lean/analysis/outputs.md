# Saved outputs of the F6 analysis scripts (2026-11-01)

CPU only, development data. Copied from the script output. `spectral.py` also wrote `spectral.json`.

## spectral.py: H per band

Bands in cycles per image: 0-2, 2-4, 4-8, 8-16, 16-32, 32-64, 64-128, 128-256, 256-363. 16 sources; n counts image pairs.

```text
f5-r2: residual RMS 1.589 levels
  energy 0.3 0.1 0.2 0.8 1.1 4.3 45.9 43.5 3.7 (%)
  R0-0.2       n= 48 Htot=+0.150  H: +1.58 +1.02 +1.49 +1.80 +1.12 +1.16 +0.12 +0.02 +0.01
  R1-0.1       n= 48 Htot=+0.326  H: +0.85 +1.07 +0.92 +0.55 +0.43 +0.33 +0.46 +0.20 +0.00
  R1-0.2       n= 48 Htot=+0.247  H: +1.16 +1.21 +0.94 +0.47 +0.37 +0.23 +0.36 +0.13 +0.00
  R3-0.2       n= 48 Htot=+0.196  H: +0.51 +0.37 +0.59 +0.40 +0.39 +0.40 +0.27 +0.10 +0.00
  D1-None      n= 16 Htot=+0.541  H: +1.34 +1.27 +1.16 +0.93 +0.83 +0.83 +0.70 +0.37 +0.02
  D3-None      n= 16 Htot=+0.631  H: +0.89 +1.15 +1.10 +1.03 +0.96 +0.92 +0.78 +0.47 +0.02
  X1-None      n= 16 Htot=+0.944  H: +1.02 +1.07 +1.05 +1.01 +1.01 +1.00 +1.01 +0.90 +0.52
  R1-mode-0.2  n= 48 Htot=+0.243  H: +1.15 +1.24 +0.98 +0.49 +0.36 +0.23 +0.35 +0.13 -0.00
v5-r3: residual RMS 3.653 levels
  energy 0.0 0.0 0.1 0.5 14.6 58.1 16.3 9.6 0.6 (%)
  R0-0.2       Htot=+0.234  H: +2.11 +1.02 +0.75 +0.51 +0.35 +0.28 +0.08 +0.01 +0.00
  R1-0.1       Htot=+0.453  H: +0.58 +0.88 +0.90 +0.73 +0.55 +0.47 +0.44 +0.20 +0.01
  R1-0.2       Htot=+0.316  H: +1.04 +0.83 +0.91 +0.61 +0.41 +0.32 +0.32 +0.14 +0.01
  R3-0.2       Htot=+0.422  H: +0.66 +0.54 +0.68 +0.60 +0.49 +0.47 +0.37 +0.13 +0.01
vine-r: residual RMS 4.600 levels
  energy 2.0 2.0 3.2 4.9 12.1 31.8 32.8 11.2 0.1 (%)
  R0-0.2       Htot=+0.439  H: +0.92 +0.84 +0.82 +0.73 +0.55 +0.41 +0.33 +0.35 +0.12
  R1-0.1       Htot=+0.786  H: +0.95 +0.94 +0.95 +0.93 +0.84 +0.77 +0.75 +0.73 +0.29
  R1-0.2       Htot=+0.655  H: +0.92 +0.92 +0.93 +0.89 +0.71 +0.62 +0.60 +0.59 +0.23
  R3-0.2       Htot=+0.762  H: +1.01 +0.97 +0.98 +0.92 +0.81 +0.74 +0.71 +0.72 +0.31
wam: residual RMS 3.231 levels
  energy 0.4 0.2 0.5 13.8 35.3 31.6 11.3 6.3 0.6 (%)
  R1-0.2       Htot=+0.129  H: +0.85 +0.65 +0.43 +0.25 +0.15 +0.08 +0.05 +0.03 -0.00
```

## coherence.py: image-like part of the residual

Chance share is 1.2%. Hc is H on the image-like part, Hi on the rest.

```text
f5-r2:  share 2.8%   R1 .2 Hc +0.53 Hi +0.24  R1 .1 Hc +0.59 Hi +0.32  K3 .2 Hc +0.48 Hi +0.19  R0 .2 Hc +1.10 Hi +0.12
v5-r3:  share 9.7%   R1 .2 Hc +0.43 Hi +0.30  R1 .1 Hc +0.58 Hi +0.44  K3 .2 Hc +0.56 Hi +0.41  R0 .2 Hc +0.38 Hi +0.22
vine-r: share 14.0%  R1 .2 Hc +0.77 Hi +0.64  R1 .1 Hc +0.86 Hi +0.77  K3 .2 Hc +0.85 Hi +0.75  R0 .2 Hc +0.64 Hi +0.41
wam:    share 16.1%  R1 .2 Hc +0.18 Hi +0.12  R1 .1 Hc +0.33 Hi +0.24  K3 .2 Hc +0.25 Hi +0.20  R0 .2 Hc +0.18 Hi +0.13
```

## bandgain.py: F5 residual by band, 6 sources

```text
band c/i | chip share mean | LPIPS alone mean | RMS mean
  0-8   | +0.001 (sd 0.001) | 0.0000 | 0.100
  8-16  | +0.006 (sd 0.005) | 0.0001 | 0.135
 16-32  | +0.008 (sd 0.004) | 0.0002 | 0.157
 32-64  | +0.079 (sd 0.021) | 0.0008 | 0.318
 64-128 | +0.209 (sd 0.045) | 0.0135 | 1.085
128-256 | +0.358 (sd 0.039) | 0.0112 | 1.053
256-363 | +0.015 (sd 0.004) | 0.0000 | 0.306
gray chip share 0.676 chroma chip share 0.191 | LPIPS gray 0.0262 chroma 0.0019 full 0.0299 | RMS gray 1.510 chroma 0.509
```

## bandmap.py: one reader-gradient step limited to a band, 6 sources

```text
all-band one-step: RMS | margin | LPIPS
1.0 0.197 0.0173
2.0 0.274 0.0409
4.0 0.363 0.0836
band | share of squared gradient | margin at RMS 1,2,4 | LPIPS at RMS 1,2,4 | max LPIPS
  0-8   | 0.000 | +0.050 +0.086 +0.144 | 0.0058 0.0194 0.0533 | 0.0201 0.0615 0.1372
  8-16  | 0.003 | +0.168 +0.296 +0.499 | 0.0120 0.0345 0.0842 | 0.0430 0.1015 0.1958
 16-32  | 0.027 | +0.057 +0.080 +0.107 | 0.0117 0.0336 0.0790 | 0.0368 0.0989 0.2059
 32-64  | 0.221 | +0.095 +0.136 +0.186 | 0.0153 0.0383 0.0804 | 0.0536 0.1304 0.2416
 64-128 | 0.350 | +0.118 +0.161 +0.199 | 0.0179 0.0443 0.0896 | 0.0620 0.1479 0.2646
128-256 | 0.382 | +0.137 +0.174 +0.206 | 0.0195 0.0506 0.1089 | 0.0631 0.1569 0.3041
256-363 | 0.017 | +0.042 +0.052 +0.057 | 0.0005 0.0027 0.0116 | 0.0014 0.0044 0.0233
```

## render.py

```text
A. surviving reader signal by band of the output difference (F5, seed 12, 6 sources)
  R1 0.2: mean margin kept +0.076 | 0-8:+0.002 8-16:+0.008 16-32:+0.001 32-64:+0.019 64-128:+0.027 128-256:+0.017 256-363:+0.001
  R1 0.1: mean margin kept +0.169 | 0-8:+0.002 8-16:+0.009 16-32:+0.004 32-64:+0.028 64-128:+0.069 128-256:+0.046 256-363:+0.001
  R3 0.2: mean margin kept +0.200 | 0-8:+0.001 8-16:+0.005 16-32:+0.004 32-64:+0.041 64-128:+0.073 128-256:+0.046 256-363:+0.002
  R0 0.2: mean margin kept +0.758 | 0-8:+0.005 8-16:+0.044 16-32:+0.023 32-64:+0.218 64-128:+0.277 128-256:+0.099 256-363:+0.007
B. variant | mean margin | recomputed score | LPIPS mean (max) | RMS | chip noise sd | energy share below 32 c/i
F5 mark                +1.013  14.61  0.0299 (0.0888)  1.59  0.759  0.00
render r<32 38 dB      +0.225   4.68  0.0085 (0.0191)  3.21  0.759  0.41
render r<32 36 dB      +0.283   5.79  0.0137 (0.0322)  4.03  0.759  0.41
render r<16 38 dB      +0.055   1.02  0.0069 (0.0169)  3.21  0.759  0.66
render r<16 36 dB      +0.069   1.33  0.0112 (0.0282)  4.03  0.759  0.67
```

The "0.00" share on the F5 row was not computed; `bandgain.py` gives the F5 spectrum.

## seedvar.py: F5 score bins and seed agreement, all 60 sources

```text
F5 decoded score bin | n | P(C) | P(J)
 0-2     12 0.00 0.00
 2-4    806 0.00 0.00
 4-6   1400 0.00 0.00
 6-8    306 0.00 0.00
 8-10   200 0.71 0.02
10-12   226 0.89 0.25
12-14   268 0.94 0.54
14-16   302 0.99 0.98
16-18    68 1.00 1.00
One-seed majority error: F5 at most 0.069 (R0 .4), 0.034 at R0 .2 and K3 .2 0.033, 0.000 on SDXL; v5 at most 0.133 (SDXL .1).
```

## jcode.py: code distance and J per attempt

```text
distance between bit 0 and bit 1, per segment: [4,7,4,4,6,4,4,2,8,5,2,8,5,5,4,6,8,6,6,7,3,5,7,7,5,5,6,5,5,7,7,4]
cell | C | J | mean bit errors | error rate, distance<=4 vs >=8
clean 1.00 0.87 0.15 0.012 0.006
X1    1.00 0.77 0.38 0.020 0.006
D1    0.92 0.52 1.25 0.055 0.011
R0 .1 1.00 0.72 0.44 0.023 0.007
R0 .2 0.96 0.63 0.82 0.035 0.009
R0 .4 0.66 0.25 2.54 0.095 0.049
R3 .2 0.09 0.01 8.79 0.310 0.194
```

## lean_cost.py

```text
low  writers f5 120, render 125, generic 201, noise 468, x0 548
  setup 1.50 h | probe 0.75 h | stage1 3.84 h | stage2 2.85 h | stage3 3.95 h | retrieval 1.00 h
  total 13.89 h USD 7.65; stop after stage 1: 7.09 h USD 3.91
high writers f5 120, render 125, generic 201, noise 838, x0 1013
  setup 3.00 h | probe 0.75 h | stage1 5.71 h | stage2 8.35 h | stage3 8.09 h | retrieval 1.00 h
  total 26.90 h USD 14.83; stop after stage 1: 10.46 h USD 5.77
high plus 25% on compute: 33.6 h USD 18.53
USD 20 buys 36.3 h
```

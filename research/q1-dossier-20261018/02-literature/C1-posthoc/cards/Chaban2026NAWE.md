# Chaban2026NAWE

Roman Chaban, Vitaliy Kinakh, Lilian Rouzaire, Slava Voloshynovskiy. *NAWE: Digital Watermarking with Neural-Assisted Watermark Extraction*. arXiv:2609.25972v1, 22 September 2026, preprint. [Primary text](https://arxiv.org/html/2609.25972v1). V2; accessed 2026-10-18, §§3–4 and figure captions; history checked.

Existing images receive a periodic masked signal with Polar coding. A frozen denoiser estimates the host; subtraction and autocorrelation support extraction and affine synchronization. The receiver needs the key, nonce, layout and decoding settings. Configurable information payload is 16–256 bits; CRC and synchronization overhead are separate.

Evaluation uses 100 COCO2017 sources for robustness and 100 for parameter sensitivity, at 512². There are 156 severities across 34 conventional attack families. The reference setting uses 48 information bits plus 16 CRC bits, rate 1/4 and PSNR 40 dB; sensitivity-reference BER is .07. Whole-word errors include failed decoding, whereas BER conditions on returned words. Different systems retain different payloads/codes.

Filtering and noise remain weaknesses. The inspected benchmark does not establish diffusion-regeneration or active-forgery security. This is relevant prior art for analytical carriers with neural extraction, not a direct substitute for the registry's instance test. No local reproduction was attempted.

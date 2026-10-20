"""Explicit final curation; no downloaded code is executed."""
import re

AUTHORS = {
'WAM':'Tom Sander; Pierre Fernandez; Alain Durmus; Teddy Furon; Matthijs Douze',
'VINE':'Shilin Lu; Zihan Zhou; Jiayou Lu; Yuanzhi Zhu; Adams Wai-Kin Kong',
'TrustMark':'Tu Bui; Shruti Agarwal; John Collomosse',
'StegaStamp':'Matthew Tancik; Ben Mildenhall; Ren Ng',
'InvisMark':'Rui Xu; Mengya Hu; Deren Lei; Yaxi Li; David Lowe; Alex Gorevski; Mingyu Wang; Emily Ching; Alex Deng',
'RoSteALS':'Tu Bui; Shruti Agarwal; Ning Yu; John Collomosse',
'ZoDiac':'Lijun Zhang; Xiao Liu; Antoni Viros Martin; Cindy Xiong Bearfield; Yuriy Brun; Hui Guan',
'PhaseMark':'Sung Ju Lee; Nam Ik Cho',
'MBRS':'Zhaoyang Jia; Han Fang; Weiming Zhang',
'SSL':'Pierre Fernandez; Alexandre Sablayrolles; Teddy Furon; Hervé Jégou; Matthijs Douze',
'SimuFreeMark':'Yichao Tang; Mingyang Li; Di Miao; Sheng Li; Zhenxing Qian; Xinpeng Zhang',
'SpecGuard':'Inzamamul Alam; Md Tanvir Islam; Simon S. Woo; Khan Muhammad',
'Pixel-Seal':'Tomáš Souček; Pierre Fernandez; Hady Elsahar; Sylvestre-Alvise Rebuffi; Valeriu Lacatusu; Tuan Tran; Tom Sander; Alexandre Mourachko',
'JigMark':'Minzhou Pan; Yi Zeng; Ning Yu; Cho-Jui Hsieh; Peter Henderson; Ruoxi Jia; Xue Lin',
'Robust-Wide':'Runyi Hu; Jie Zhang; Tianwei Zhang; Jiwei Li',
'SpreadMark':'Wei Song; Yuxin Cao; Zhenchang Xing; Liming Zhu; Jin Song Dong; Yulei Sui; Jingling Xue',
'NAWE':'Roman Chaban; Vitaliy Kinakh; Lilian Rouzaire; Slava Voloshynovskiy',
'LaWa':'Ahmad Rezaei; Mohammad Akbari; Saeed Ranjbar Alvar; Arezou Fatemi; Yong Zhang',
'Chunky-Seal':'Aleksandar Petrov; Pierre Fernandez; Tomáš Souček; Hady Elsahar',
'GenPTW':'Zhenliang Gan; Chunya Liu; Yichao Tang; Binghao Wang; Shiwen Cui; Weiqiang Wang; Xinpeng Zhang',
'DistSeal':'Sylvestre-Alvise Rebuffi; Tuan Tran; Valeriu Lacatusu; Pierre Fernandez; Tomáš Souček; Nikola Jovanović; Tom Sander; Hady Elsahar; Alexandre Mourachko',
'EditGuard':'Xuanyu Zhang; Runyi Li; Jiwen Yu; Youmin Xu; Weiqi Li; Jian Zhang',
'OmniGuard':'Xuanyu Zhang; Zecheng Tang; Zhipei Xu; Runyi Li; Youmin Xu; Bin Chen; Feng Gao; Jian Zhang',
'SNW':'Enoal Gesny; Eva Giboulot',
}

def enrich(methods):
    by = {m['name']:m for m in methods}
    def put(name, **kw): by[name].update(kw)
    put('OmniGuard', title='OmniGuard: Hybrid Manipulation Localization via Augmented Versatile Deep Image Watermarking')
    put('Chunky-Seal',
        mechanism='A scaled VideoSeal-family image embedder and extractor write 1,024 bits in chunks. This is a separately trained, high-capacity post-hoc model, rather than another release counted as another method.',
        native='The pinned chunkyseal.yaml sets 1,024 bits, processing size 256, additive blending, scaling_w=.2, scaling_i=1 and JND jnd_1_1. It selects unet_chunky and convnext_chunky with no final sigmoid in the extractor; exact loader, residual interpolation and serialization still need adapter verification. Paper embedder/extractor sizes are approximately 1,022.7M/773.7M parameters. No universal calibrated presence threshold is established. High capacity must remain visible instead of truncating the message.',
        release='Correction to the initial search: the official VideoSeal README advertises ChunkySeal and its model zoo links a dedicated model card and checkpoint. facebookresearch/videoseal@870ca7fb33578b90f14c602016b6c2788096226e has an inspected MIT LICENSE and README explicitly covering code and models. The pinned videoseal/cards/chunkyseal.yaml points to https://dl.fbaipublicfiles.com/videoseal/chunkyseal/checkpoint.pth. The URL is mutable; bytes, SHA-256 and weight identity were not verified, and no weights were downloaded. The paper document license is separate from this official implementation license.',
        implication='This closes a genuine released high-capacity omission. Large parameter storage and absent direct diffusion-regeneration evidence keep it outside the cheapest decisive study; no additional proposal is made.')
    by['Pixel-Seal']['regeneration'] += ' New third-party evidence: SNW Appendix H.2/Table 6 tests 200 MFlickr images at 1,024 pixels, with all methods rescaled to 48 dB PSNR and decoder features whitened. PixelSeal rate/capacity is .939/240.5 bits for identity, .555/142.0 for VAE, .519/132.8 for Sana 2 steps, .357/91.3 for 4, .076/19.4 for 8, .025/6.4 for 10 and .003/.8 for 20. Rate is NOT bit accuracy: these are independent-bit Shannon-capacity estimates, not exact payload recovery or calibrated TPR. The attack model revision, sampler, prompts, seeds and correspondence to our SDXL strength are unresolved. This does not supply a result for the native P9 operating point.'
    by['Pixel-Seal']['implication'] = 'P9 remains the second additional proposal because the native release is modern, permissively licensed and high quality. The original paper has no direct regeneration result; the separate SNW study supplies conditional third-party evidence at a rescaled, whitened operating point. Neither establishes SDXL transfer for P9. It remains excluded from the core.'
    put('WAM', native='Native released MIT SA-1B model: 32 raw bits, processing size 256, scaling_w=2.0, scaling_i=1.0 and JND jnd_1_3_blue. RGB input at 512 is ImageNet-normalized; internal bilinear resizing and antialiased residual upsampling preserve the original image. The paper trains on COCO with alpha=.3 and high-resolution JND scaling; those weights differ from this release. Pixel mask uses sigmoid >.5; paper image presence is mask-positive area >.07, calibrated on COCO to about 2.6e-4 FPR. Released README passes RAW message logits to semihard aggregation: select mask >.5, average logits, then compare the average >.5. This differs from averaging probabilities in paper Equation 2; retain the released behavior. An empty mask is an abstention. Official save_image multiplies by 255, adds .5, clamps and converts to uint8. Common known-message presence uses at least 27/32 matches (analytic fair-query tail 5.6537101045e-5); this is a separate endpoint and must not be conjoined with the native image detector. COCO calibration does not automatically transfer to SA-1B weights.',
        regeneration='Primary Table 9, Appendix G.3: DiffPure attack PSNR 30.1/28.4/27.0/24.9 dB corresponds to bit accuracy 100/99.4/71.3/49.1%; VAE attack PSNR 32.9/32.4/28.6/25.5 corresponds to 100/99.8/98.6/53.7%. These are bit accuracies, not TPR at our threshold. The appendix does not specify enough to reproduce model revision, diffusion strength/noise schedule, sampler, prompt, exact evaluation count or every attack resolution; do not infer them from the main 10,000-image COCO/DIV2K evaluation. These curves use COCO weights. VINE and SpreadMark comparisons use different payload, quality and attack conditions; they do not establish this release\'s R1 outcome.')
    put('VINE', native='VINE-R uses 100 raw bits. The native encoder takes RGB 256 in [-1,1]; the decoder takes RGB 256 in [0,1], with sigmoid outputs and NumPy rounding. Input uses PIL bicubic resizing; the encoder uses the posterior mode. Its tensor bicubic residual is upsampled onto the original 512-pixel image, clamped, converted through native ToPILImage truncation, saved and reopened as PNG. No ImageNet normalization is used. The text CLI writes 96 text bits plus four zeros; arbitrary 100-bit API use is distinct. Paper/README says SDXL-Turbo, but the constructor loads stabilityai/sd-turbo. Native evaluation reports ROC TPR at FPR below .001 or .01; no universal numerical message-match threshold is published. Common presence at 69/100 matches is a separate fair-query tail rule (9.1571612441e-5), not native TPR at .1% FPR. C0 and wrong-owner behavior must remain visible without outcome-based recalibration.',
        regeneration='Table 1 gives VINE-R PSNR 37.34, SSIM .9934, LPIPS .0063 and stochastic/deterministic regeneration TPR 99.66/99.98% at .1% FPR, averaged over severities. VINE-Base gives 40.51/.9954/.0029 and 91.03/99.25%. Official stochastic code loads stabilityai/stable-diffusion-2-1, fp16 revision fp16, DDIM, noise indices 60 through 240 in increments of 20, requested 50 inference steps and head-start logic 50-max(noise//20,1), CFG 7.5, empty prompt unless captions are supplied, and sampled latent posterior. Deterministic code uses SD2.1-base fp32, DPM multistep inverse/forward scheduler of order 2, 15/25/35/45 steps, CFG 1, empty prompt/negative prompt and posterior mean times .18215. The native benchmark uses 512 pixels. COUNT CONFLICT: Table 1 caption says 5,000 images per editing method; Section 4.2 says 1,000 stochastic and 1,000 deterministic sources; Section 4.3 describes m times 1,000 over severities. Preserve all statements without claiming 5,000 independent sources. Quality uses 10,000 UltraEdit images. Native ROC calibration is empirical against unmarked images; no 1e-4 calibration is claimed.',
        cost='Table 7 reports .0795 seconds and 4,982 MB on NVIDIA Quadro RTX6000, averaged over 1,000 images. The phase/batch scope is insufficiently explicit to derive whole-grid time. Approximately 9.53 GB of required fp32 weight storage is not peak VRAM. Target-server timing remains unmeasured.')
    put('WAM', cost='The paper reports approximately 1.1M embedder and 96M extractor parameters. Checkpoint size is storage, not peak VRAM. Inference needs an embedder and a ViT forward; target-server time and memory remain unmeasured. The core cost remains within the parent budget; this is not a new timing claim.')
    for m in methods:
        for old, new in {';?': '; ?', ',Tables': ', Tables', ',Figure': ', Figure', ';Appendix': '; Appendix ', 'Appendix12.2': 'Appendix 12.2', 'AppendixD.3': 'Appendix D.3', 'andAppendixI.1': 'and Appendix I.1', 'Method:Overall': 'Method: Overall', ',Multiscale': ', Multiscale', ',CAF/SF,Tamper-AwareExtractor': ', CAF/SF, Tamper-Aware Extractor', ';Experimental': '; Experimental', ',Comparison': ', Comparison', ',SA-AT': ', SA-AT', ',Ablations': ', Ablations', ',robustness': ', robustness', 'Eqs.1': 'Eqs. 1', 'pp3': 'pp. 3', 'rendered p7': 'rendered page 7'}.items():
            m['sections'] = m['sections'].replace(old,new)
        m['authors'] = AUTHORS[m['name']].split('; ')
        m['year'] = 2000 + int(m['arxiv'][:2])
        m['doi'] = '10.1609/aaai.v40i5.37412' if m['name']=='GenPTW' else None
        m['canonical_url'] = 'https://arxiv.org/abs/' + m['arxiv']
        m['stable_id'] = 'arxiv:' + m['arxiv']
        m['citekey'] = 'T3' + re.sub(r'[^A-Za-z0-9]','',m['name']) + m['arxiv'][:4]
        m['evidence_level'] = 'V2'
        m['accessed'] = '2026-10-20'
    return methods

"""Analytical schedule and conditional Gaussian bounds; stdlib only.

No model calls, images, scientific packages or experimental execution.
Constants are from the retained protocol/source text, not reconstructed outputs.
Double precision mathematical values are not bit-exact scheduler replays.
"""
import json
import math
from pathlib import Path
from statistics import NormalDist

HERE = Path(__file__).resolve().parent

def abar_scaled(t):
    value = 1.0
    for k in range(t+1):
        beta = (math.sqrt(.00085) + k*(math.sqrt(.012)-math.sqrt(.00085))/999)**2
        value *= 1-beta
    return value

def abar_cosine(t):
    def curve(u):
        return math.cos((u+.008)/1.008*math.pi/2)**2
    value = 1.0
    for k in range(t+1):
        value *= 1-min(1-curve((k+1)/1000)/curve(k/1000),.999)
    return value

rows = []
for family,schedule,strength,t,steps in (
    ('R0/R1','scaled_linear',.1,51,2),
    ('R0/R1','scaled_linear',.2,151,4),
    ('R0/R1','scaled_linear',.4,351,8),
    ('R3','squaredcos_cap_v2',.2,151,4)):
    ab = abar_scaled(t) if schedule=='scaled_linear' else abar_cosine(t)
    rows.append(dict(family=family,schedule=schedule,strength=strength,start_t=t,
                     reverse_updates=steps,alpha_bar=ab,a=math.sqrt(ab),
                     b=math.sqrt(1-ab),a_over_b=math.sqrt(ab/(1-ab)),
                     log_snr=math.log(ab/(1-ab))))

normal=NormalDist()
gaussian=[]
for alpha in (.05,1e-3,1e-6):
    z=normal.inv_cdf(1-alpha)
    gaussian.append(dict(fpr=alpha,threshold_standard_normal=z,
                         mu_required_for_tpr_90=z+normal.inv_cdf(.9),
                         tpr_upper_at_mu_2=normal.cdf(2-z),
                         tpr_upper_at_mu_4=normal.cdf(4-z)))
zero=[dict(independent_sources=n,one_sided_95_upper=1-.05**(1/n)) for n in (60,180,200,540)]
result=dict(schedule=rows,conditional_gaussian_shift=gaussian,zero_event_bounds=zero,
            limitation='Equal-covariance Gaussian location shift bound is conditional. No empirical F5 SNR is available. Seeds are not independent sources.')
(HERE/'schedule-bounds.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
lines=['# Schedule and conditional detection bounds','',
       'Analytical double-precision calculations from pinned schedule constants. These are not a local scheduler/model execution or a bit-exact replay. R0/R1 share a schedule but not latent units or their reverse response.','',
       '| Family | Strength | Start | Updates | alpha_bar | a/b | log SNR |',
       '|---|---:|---:|---:|---:|---:|---:|']
for r in rows:
    lines.append(f"| {r['family']} | {r['strength']} | {r['start_t']} | {r['reverse_updates']} | {r['alpha_bar']:.6f} | {r['a_over_b']:.6f} | {r['log_snr']:.6f} |")
lines += ['', 'A scalar a/b orders input Gaussian distinguishability only when the encoded displacement and covariance are held fixed. It does not order the nonlinear reader output, nor compare differently scaled encoders.', '',
          'For a fully specified equal-covariance Gaussian location shift with Mahalanobis displacement mu, the optimal level-alpha test has TPR=Phi(mu-Phi^-1(1-alpha)); any downstream detector can do no better under those assumptions. The model here is a conditional information bound, not an empirical F5 guarantee.', '',
          '| FPR alpha | mu required for TPR .90 | TPR upper at mu=2 | TPR upper at mu=4 |',
          '|---:|---:|---:|---:|']
for r in gaussian:
    lines.append(f"| {r['fpr']:g} | {r['mu_required_for_tpr_90']:.4f} | {r['tpr_upper_at_mu_2']:.6f} | {r['tpr_upper_at_mu_4']:.6f} |")
lines += ['', 'Zero events in 60 independent source clusters give the exact one-sided 95% upper bound 4.8703%. Treating 180 seeds or 540 correlated calls as independent sources would wrongly yield the smaller bounds stored in the JSON. At 200 genuinely independent sources the upper bound is 1.4867%; a nominal 1e-6 analytic detector threshold is not empirically validated by either sample.', '',
          'Source text: local scripts/three_threat_models.py DDIM_CONFIG; scripts/encoder_transfer_amend_2b.py native R3 contract; diffusers v0.35.1 scheduling_ddim.py, scheduling_ddpm.py and pipeline_stable_diffusion_img2img.py, inspected online as text. Full-chain derivation and assumptions: theory-design.md.']
(HERE/'schedule-bounds.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))

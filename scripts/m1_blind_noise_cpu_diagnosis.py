"""Read-only B3-C artifact arithmetic; no model, GPU, image generation or fit."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

import m1_blind_noise_core as core


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cosine(x, y):
    x, y = np.ravel(x), np.ravel(y)
    return float(x @ y / np.linalg.norm(x) / np.linalg.norm(y))


def rms(x):
    return float(np.sqrt(np.mean(np.asarray(x, np.float64) ** 2)))


def rgb(path):
    with Image.open(path) as im:
        return np.asarray(im.convert('RGB')).astype(np.float64) / 255


def stats(x):
    return dict(dtype=str(x.dtype), shape=list(x.shape), mean=float(x.mean()),
                std=float(x.std()), rms=rms(x), maximum_absolute=float(abs(x).max()),
                channel_rms=[rms(v) for v in x.reshape(4, -1)])


def diagnose(folder):
    folder = Path(folder)
    record = json.loads((folder / 'run.json').read_text(encoding='utf-8'))
    rows = record['conditions']
    owner = core.OWNERS[0]
    checked = {}
    for name, expected in record['output_hashes'].items():
        actual = sha(folder / name)
        if actual != expected:
            raise ValueError(f'Retained artifact hash mismatch: {name}')
        checked[name] = actual
    results = []
    for event in record['case_events']:
        ident = event['source_id']
        E, H = event['source_E'], event['source_H']
        T = np.load(folder / f'{ident}-T.npy', allow_pickle=False)
        n0 = np.load(folder / f'{ident}-n0.npy', allow_pickle=False)
        template = core.template(E, H, owner)
        expected = template['T'].astype(np.float32).reshape(T.shape)
        if not np.array_equal(T, expected):
            raise ValueError('Retained source template differs from frozen core')
        source = rgb(folder / f'{ident}-source.png')
        d0 = np.load(folder / f'{ident}-D0.npy', allow_pickle=False)
        base = dict(source_id=ident, source_H=H, input_noise=stats(n0),
                    source_template=stats(T), input_noise_template_cosine=cosine(n0, T),
                    input_noise_source_template_scores=core.scores(n0.ravel(), E, H, owner),
                    baseline_reconstruction_rmse=rms(d0-source),
                    baseline_reconstruction_psnr_db=float(-20*np.log10(rms(d0-source))),
                    template_matches_frozen_core=True, doses=[])
        response = []
        for alpha in record['config']['alphas']:
            supplied = np.load(folder / f'{ident}-{alpha}-supplied.npy', allow_pickle=False)
            intended = n0.astype(np.float32) + alpha*T
            if not np.array_equal(supplied, intended.astype(np.float16)):
                raise ValueError('Supplied noise differs from frozen perturbation')
            perturbation = supplied.astype(np.float64) - n0
            da = np.load(folder / f'{ident}-{alpha}-Da.npy', allow_pickle=False)
            delta = da - d0
            response.append(delta)
            raw_hybrid = source + delta
            composed = np.rint(np.clip(raw_hybrid, 0, 1)*255).astype(np.uint8)
            with Image.open(folder / f'{ident}-{alpha}-hybrid-C1-clean.png') as im:
                actual = np.asarray(im.convert('RGB'))
            if not np.array_equal(composed, actual):
                raise ValueError('Saved bypass differs from declared float residual')
            row = dict(alpha=alpha, perturbation_rms=rms(perturbation),
                       relative_perturbation_rms=rms(perturbation)/rms(n0),
                       perturbation_template_cosine=cosine(perturbation,T),
                       rounding_relative_rms=rms(supplied.astype(np.float64)-intended)/rms(alpha*T),
                       changed_noise_fraction=float(np.mean(supplied != n0)),
                       input_source_template_scores=core.scores(supplied.ravel(),E,H,owner),
                       decoder_residual_rms=rms(delta),
                       decoder_residual_rms_per_alpha=rms(delta)/alpha,
                       unclipped_hybrid_fraction_outside_unit=float(np.mean((raw_hybrid<0)|(raw_hybrid>1))),
                       hybrid_clipping_change_rms=rms(np.clip(raw_hybrid,0,1)-raw_hybrid),
                       rgb8_rounding_rms=rms(actual.astype(np.float64)/255-np.clip(raw_hybrid,0,1)),
                       saved_hybrid_exact=True, observations=[])
            for route in ('hybrid','pure'):
                for dose in ('clean','vae_cycle'):
                    c1 = next(x for x in rows if x['source_id']==ident and x['alpha']==alpha and
                              x['route']==route and x['control']=='C1' and x['dose']==dose)
                    c0 = next(x for x in rows if x['source_id']==ident and x['alpha']==alpha and
                              x['route']==route and x['control']=='C0' and x['dose']==dose)
                    score, score0 = c1['owner_decisions'][owner], c0['owner_decisions'][owner]
                    projection = c1['projection_diagnostics'][owner]
                    observation = dict(route=route, dose=dose, s=score['s'], i=score['i'],
                        s0=score0['s'], i0=score0['i'],
                        semantic_score_difference=score['s']-score0['s'],
                        instance_score_difference=score['i']-score0['i'],
                        semantic_numerator_difference=score['s']*score['denominators']['s']-score0['s']*score0['denominators']['s'],
                        instance_numerator_difference=score['i']*score['denominators']['i']-score0['i']*score0['denominators']['i'],
                        semantic_denominator_ratio=score['denominators']['s']/score0['denominators']['s'],
                        instance_denominator_ratio=score['denominators']['i']/score0['denominators']['i'],
                        source_clip_cosine=c1['source_clip_cosine'], source_phash_distance=c1['source_phash_distance'],
                        kernel_exact=projection['kernel_exact'], kernel_projected=projection['kernel_projected_normalized'],
                        normalized_projection_error=projection['normalized_error'],
                        source_projection_norm_sq=projection['norm_sq_1'], suspect_projection_norm_sq=projection['norm_sq_2'],
                        quality=c1['quality_vs_source'])
                    if route=='hybrid' and dose=='clean':
                        # Descriptive origin-constrained local extrapolation only; no image or score fit used by a detector.
                        quality_alpha=alpha*10**((c1['quality_vs_source']['psnr_db']-35.2)/20)
                        observation['linearized_alpha_at_psnr35_2']=quality_alpha
                        observation['linearized_s_at_psnr35_2']=score0['s']+(score['s']-score0['s'])*quality_alpha/alpha
                        observation['linearized_i_at_psnr35_2']=score0['i']+(score['i']-score0['i'])*quality_alpha/alpha
                    row['observations'].append(observation)
            base['doses'].append(row)
        base['response_pair_diagnostics'] = [dict(alpha_low=a,alpha_high=b,
            residual_cosine=cosine(response[j],response[k]),
            ratio_of_observed_rms=float(rms(response[k])/rms(response[j])), expected_linear_ratio=b/a,
            proportional_response_relative_error=rms(response[k]-(b/a)*response[j])/rms(response[k]))
            for j,a in enumerate(record['config']['alphas']) for k,b in enumerate(record['config']['alphas']) if j<k]
        results.append(base)
    return dict(schema='m1-blind-noise-cpu-diagnosis-v1', run_directory=str(folder),
                run_sha256=sha(folder/'run.json'), run_commit=record['commit'],
                core_sha256=sha(Path(core.__file__)), diagnostic_script_sha256=sha(__file__),
                input_artifact_sha256=checked, scientific_status='post-hoc arithmetic on two development sources; no new model evaluation',
                terminal_latents_available=False,
                warning='C1-minus-C0 blind scores also change templates/normalizers; they are not a causal fixed-template transport estimate. Linear extrapolations are descriptive, not measured bounds.',
                cases=results)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    result=diagnose(a.input_dir)
    with a.output.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2,allow_nan=False)
        f.write('\n')
    print(json.dumps({'cases':len(result['cases']),'verified_artifacts':len(result['input_artifact_sha256']),'output':str(a.output)}))

"""Shared Eq10 backward schedule and its frozen actual-model numerical gate.

Imports are lazy; importing this helper performs no model or GPU work.
"""
from copy import deepcopy


def backward_step(a, b, frequency, source, message, noises, decode, features,
                  metric, finite, schedule):
    import torch
    latent_noise, pixel_noise = noises

    def latent():
        return torch.fft.ifft2(frequency + torch.complex(a, b),
                              dim=(-2, -1), norm='backward').real

    def hinge(image):
        return torch.relu(1 - message * features(image)).mean()

    def clean_branch(current_latent):
        clean = decode(current_latent)
        h = hinge(clean)
        psnr = -10 * torch.log10((clean-source).square().mean().clamp_min(1e-12))
        perceptual = metric(clean*2-1, source*2-1).mean()
        return clean, h, psnr, perceptual

    current_latent = latent()
    clean, h, psnr, perceptual = clean_branch(current_latent)
    finite(h, psnr, perceptual)
    values = dict(clean_hinge=h.item(), psnr=psnr.item(), lpips=perceptual.item())
    if schedule == 'joint':
        noisy_h = hinge(decode(current_latent+latent_noise))
        pixel_h = hinge((clean+pixel_noise).clamp(0, 1))
        loss = h+noisy_h+pixel_h-.05*psnr+.25*perceptual
        finite(noisy_h, pixel_h, loss)
        values.update(latent_hinge=noisy_h.item(), pixel_hinge=pixel_h.item(), loss=loss.item())
        loss.backward()
    elif schedule == 'serial-validated':
        loss = h-.05*psnr+.25*perceptual
        finite(loss)
        loss.backward()
        del clean, h, psnr, perceptual, loss, current_latent
        noisy_h = hinge(decode(latent()+latent_noise))
        finite(noisy_h)
        values['latent_hinge'] = noisy_h.item()
        noisy_h.backward()
        del noisy_h
        # The pixel branch recomputes the decode with an intact parameter graph.
        pixel_h = hinge((decode(latent())+pixel_noise).clamp(0, 1))
        finite(pixel_h)
        values['pixel_hinge'] = pixel_h.item()
        pixel_h.backward()
        values['loss'] = (values['clean_hinge']+values['latent_hinge']+
                          values['pixel_hinge']-.05*values['psnr']+.25*values['lpips'])
    else:
        raise ValueError('Unknown backward schedule')
    finite(a.grad, b.grad)
    return values  # Only Python scalars escape; every branch graph is freed.


def numerical_gate(torch, np, fixture, decode, features, metric, finite,
                   encode, out, write, check, stop):
    """Four local comparisons; reference trajectory supplies each next state."""
    report = dict(fixture='numerical-fixture.npy', comparisons=[], passed=False)
    write(out/'numerical-validation.json', report)
    source = torch.from_numpy(fixture.copy()).permute(2, 0, 1)[None].to('cuda')
    with torch.no_grad():
        z = encode(source)
        frequency = torch.fft.fft2(z, dim=(-2, -1), norm='backward')
    message = torch.tensor([1 if k % 2 == 0 else -1 for k in range(48)],
                           device='cuda', dtype=torch.float32)[None]
    rng = torch.Generator(device='cuda').manual_seed(2026101302)

    def vector(parameters):
        return torch.cat([p.detach().flatten() for p in parameters]).cpu().numpy().copy()

    def residual(reference, actual):
        r, v = reference.astype(np.float64), actual.astype(np.float64)
        delta = v-r
        rn, vn = float(np.linalg.norm(r)), float(np.linalg.norm(v))
        return dict(reference_l2=rn, serial_l2=vn,
                    relative_l2=float(np.linalg.norm(delta))/max(rn, 1e-12),
                    maximum_absolute=float(np.max(np.abs(delta))),
                    cosine=float(np.dot(r, v)/max(rn*vn, 1e-24)))

    def state_arrays(optimizer, prefix):
        result = {}
        for index, param in enumerate(optimizer.param_groups[0]['params']):
            for key, value in optimizer.state[param].items():
                result[f'{prefix}_{index}_{key}'] = value.detach().cpu().numpy().copy()
        return result

    for initialization in ('zero', 'nonzero'):
        k = torch.arange(z.numel(), device='cuda', dtype=torch.float32).reshape(z.shape)
        initial = ([torch.zeros_like(z), torch.zeros_like(z)] if initialization == 'zero'
                   else [.1*torch.sin(k), .1*torch.cos(k)])
        reference_params = [v.detach().clone().requires_grad_(True) for v in initial]
        reference_opt = torch.optim.Adam(reference_params, lr=2., betas=(.9, .999), eps=1e-8)
        for moments in ('fresh', 'populated'):
            check()
            label = f'{initialization}-{moments}'
            serial_params = [p.detach().clone().requires_grad_(True) for p in reference_params]
            serial_opt = torch.optim.Adam(serial_params, lr=2., betas=(.9, .999), eps=1e-8)
            serial_opt.load_state_dict(deepcopy(reference_opt.state_dict()))
            before = vector(reference_params)
            noise = (torch.randn(z.shape, generator=rng, device='cuda', dtype=torch.float32)*.25,
                     torch.randn(source.shape, generator=rng, device='cuda', dtype=torch.float32)*.06)
            arrays = dict(before=before, latent_noise=noise[0].cpu().numpy(), pixel_noise=noise[1].cpu().numpy())
            arrays.update(state_arrays(reference_opt, 'before_state'))
            report['active_case'] = label
            write(out/'numerical-validation.json', report)
            np.savez_compressed(out/f'numerical-{label}.npz', **arrays)
            outcomes = []
            for params, optimizer, schedule in ((reference_params, reference_opt, 'joint'),
                                                (serial_params, serial_opt, 'serial-validated')):
                optimizer.zero_grad(set_to_none=True)
                values = backward_step(*params, frequency, source, message, noise,
                                       decode, features, metric, finite, schedule)
                grad = vector([p.grad for p in params])
                optimizer.step()
                finite(*params)
                update = vector(params)-before
                outcomes.append((values, grad, update))
                prefix = 'reference' if schedule == 'joint' else 'serial'
                arrays[prefix+'_gradient'] = grad
                arrays[prefix+'_update'] = update
                arrays.update(state_arrays(optimizer, prefix+'_state'))
                np.savez_compressed(out/f'numerical-{label}.npz', **arrays)
                check()
            ref, serial = outcomes
            component_residuals = {key: dict(reference=value, serial=serial[0][key],
                absolute=abs(serial[0][key]-value), tolerance=1e-5+1e-5*abs(value))
                for key, value in ref[0].items()}
            grad = residual(ref[1], serial[1]); update = residual(ref[2], serial[2])
            grad['absolute_tolerance'] = 1e-9+5e-4*float(np.max(np.abs(ref[1])))
            arrays.update(reference_gradient=ref[1], serial_gradient=serial[1],
                gradient_difference=serial[1]-ref[1], reference_update=ref[2],
                serial_update=serial[2], update_difference=serial[2]-ref[2])
            arrays.update(state_arrays(reference_opt, 'reference_state'))
            arrays.update(state_arrays(serial_opt, 'serial_state'))
            state_differences = {}
            for key in list(arrays):
                if key.startswith('reference_state_'):
                    suffix = key[len('reference_state_'):]
                    delta = arrays['serial_state_'+suffix]-arrays[key]
                    arrays['state_difference_'+suffix] = delta
                    state_differences[suffix] = float(np.max(np.abs(delta)))
            np.savez_compressed(out/f'numerical-{label}.npz', **arrays)
            all_finite = all(np.isfinite(v).all() for v in arrays.values()) and all(
                np.isfinite(v) for values, _, _ in outcomes for v in values.values())
            passed = (all_finite and grad['reference_l2'] > 0 and grad['serial_l2'] > 0
                and update['reference_l2'] > 0 and update['serial_l2'] > 0
                and all(v['absolute'] <= v['tolerance'] for v in component_residuals.values())
                and grad['relative_l2'] <= 1e-4 and grad['maximum_absolute'] <= grad['absolute_tolerance']
                and update['relative_l2'] <= 1e-4 and update['maximum_absolute'] <= 1e-3)
            report['comparisons'].append(dict(case=label, components=component_residuals,
                gradient=grad, update=update, state_maximum_absolute=state_differences,
                all_finite=bool(all_finite), passed=bool(passed), arrays=f'numerical-{label}.npz'))
            write(out/'numerical-validation.json', report)
            if not passed:
                raise stop('numeric_gate_failed', f'Frozen numerical comparison failed: {label}')
            del serial_opt, serial_params, outcomes, arrays, noise
        del reference_opt, reference_params, initial
    report['passed'] = len(report['comparisons']) == 4
    report.pop('active_case', None)
    write(out/'numerical-validation.json', report)
    return report

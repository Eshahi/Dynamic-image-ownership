"""Shared Eq10 backward schedule and its frozen actual-model numerical gate.

Imports are lazy; importing this helper performs no model or GPU work.
"""
from copy import deepcopy


class BackwardWarningPolicy:
    """The prospective AA-only policy; strict mode resumes even on exceptions."""
    def __init__(self, torch, stop, record, persist):
        self.torch, self.stop, self.record, self.persist = torch, stop, record, persist
        self.context = 'unspecified'

    def __call__(self, loss):
        import warnings
        captured = []
        try:
            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter('always')
                self.torch.use_deterministic_algorithms(True, warn_only=True)
                try:
                    loss.backward()
                finally:
                    self.torch.use_deterministic_algorithms(True, warn_only=False)
        finally:
            rejected = []
            for warning in captured:
                text = str(warning.message)
                lower = text.lower()
                nondeterministic = ('deterministic' in lower or 'nondetermin' in lower)
                allowed = ('upsample_bicubic2d_aa_backward_out_cuda' in text and
                           ('does not have a deterministic implementation' in lower or
                            'does not have a deterministic' in lower))
                self.record.append(dict(context=self.context, message=text,
                    category=warning.category.__name__, filename=warning.filename,
                    lineno=warning.lineno, allowlisted=allowed,
                    nondeterminism=nondeterministic))
                if nondeterministic and not allowed:
                    rejected.append(text)
            self.persist()
            if rejected:
                raise self.stop('unallowlisted_nondeterminism', '; '.join(rejected))


def interpolation_jitter(torch, np, out, write, check, stop, backward):
    """Saved full-scale fixture, three native CUDA backward evaluations."""
    import torch.nn.functional as F
    input_array = np.random.Generator(np.random.PCG64(np.random.SeedSequence(
        [2026101303, 0]))).uniform(.1, .9, (1,3,512,512)).astype(np.float32)
    cotangent = np.random.Generator(np.random.PCG64(np.random.SeedSequence(
        [2026101303, 1]))).uniform(-1, 1, (1,3,256,256)).astype(np.float32)
    np.savez_compressed(out/'interpolation-fixture.npz', input=input_array, cotangent=cotangent)
    report = dict(fixture='interpolation-fixture.npz', input_seed=[2026101303,0],
        cotangent_seed=[2026101303,1], evaluations=[], comparisons=[], passed=False)
    write(out/'interpolation-validation.json', report)
    warning_start = len(backward.record)
    reference = None
    for repeat in range(1,4):
        check()
        backward.context = f'interpolation-{repeat}'
        report['active_evaluation'] = repeat
        write(out/'interpolation-validation.json', report)
        x = torch.from_numpy(input_array.copy()).to('cuda').requires_grad_(True)
        c = torch.from_numpy(cotangent.copy()).to('cuda')
        y = F.interpolate(x, size=(256,256), mode='bicubic', align_corners=False, antialias=True)
        backward((y*c).sum())
        output, gradient = y.detach().cpu().numpy().copy(), x.grad.detach().cpu().numpy().copy()
        finite = np.isfinite(output).all() and np.isfinite(gradient).all()
        norm = float(np.linalg.norm(gradient.astype(np.float64)))
        np.savez_compressed(out/f'interpolation-{repeat}.npz', output=output, gradient=gradient)
        report['evaluations'].append(dict(repeat=repeat, all_finite=bool(finite), gradient_l2=norm,
            forward_l2=float(np.linalg.norm(output.astype(np.float64)))))
        write(out/'interpolation-validation.json', report)
        if not finite or norm == 0:
            raise stop('numeric_gate_failed', 'Nonfinite or zero interpolation gradient')
        if reference is None:
            reference = (output, gradient)
        else:
            r, g = reference
            forward_error = float(np.max(np.abs(output.astype(np.float64)-r)))
            delta = gradient.astype(np.float64)-g.astype(np.float64)
            relative = float(np.linalg.norm(delta))/max(float(np.linalg.norm(g.astype(np.float64))),1e-12)
            maximum = float(np.max(np.abs(delta)))
            forward_tolerance = 1e-5+1e-5*float(np.max(np.abs(r)))
            grad_tolerance = 1e-9+5e-4*float(np.max(np.abs(g)))
            passed = forward_error <= forward_tolerance and relative <= 1e-4 and maximum <= grad_tolerance
            report['comparisons'].append(dict(reference=1, actual=repeat,
                forward_maximum_absolute=forward_error, forward_tolerance=forward_tolerance,
                gradient_relative_l2=relative, gradient_maximum_absolute=maximum,
                gradient_absolute_tolerance=grad_tolerance, passed=bool(passed)))
            write(out/'interpolation-validation.json', report)
            if not passed:
                raise stop('numeric_gate_failed', 'Frozen interpolation jitter tolerance failed')
        del x, c, y, output, gradient
        check()
    report['warnings'] = backward.record[warning_start:]
    report['allowlisted_warning_observed'] = any(w['allowlisted'] for w in report['warnings'])
    report['passed'] = len(report['comparisons']) == 2 and report['allowlisted_warning_observed']
    report.pop('active_evaluation', None)
    write(out/'interpolation-validation.json', report)
    if not report['passed']:
        raise stop('numeric_gate_failed', 'Direct AA probe did not observe the required known warning')
    return report


def backward_step(a, b, frequency, source, message, noises, decode, features,
                  metric, finite, schedule, backward=None):
    import torch
    backward = backward or (lambda loss: loss.backward())
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
        backward(loss)
    elif schedule in ('serial-validated', 'serial-aawarn'):
        loss = h-.05*psnr+.25*perceptual
        finite(loss)
        backward(loss)
        del clean, h, psnr, perceptual, loss, current_latent
        noisy_h = hinge(decode(latent()+latent_noise))
        finite(noisy_h)
        values['latent_hinge'] = noisy_h.item()
        backward(noisy_h)
        del noisy_h
        # The pixel branch recomputes the decode with an intact parameter graph.
        pixel_h = hinge((decode(latent())+pixel_noise).clamp(0, 1))
        finite(pixel_h)
        values['pixel_hinge'] = pixel_h.item()
        backward(pixel_h)
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


def replicated_numerical_gate(torch, np, fixture, decode, features, metric,
                             finite, encode, out, write, check, stop, backward):
    """Four inherited cases, J1/S1/J2/S2/J3/S3, twenty frozen comparisons."""
    report = dict(fixture='numerical-fixture.npy', comparisons=[], evaluations=[], passed=False)
    write(out/'numerical-validation.json', report)
    source = torch.from_numpy(fixture.copy()).permute(2,0,1)[None].to('cuda')
    with torch.no_grad():
        z = encode(source)
        frequency = torch.fft.fft2(z, dim=(-2,-1), norm='backward')
    message = torch.tensor([1 if k % 2 == 0 else -1 for k in range(48)],
                           device='cuda', dtype=torch.float32)[None]
    rng = torch.Generator(device='cuda').manual_seed(2026101302)

    def vector(parameters):
        return torch.cat([p.detach().flatten() for p in parameters]).cpu().numpy().copy()

    def state_arrays(optimizer, prefix):
        return {f'{prefix}_{index}_{key}': value.detach().cpu().numpy().copy()
                for index, param in enumerate(optimizer.param_groups[0]['params'])
                for key, value in optimizer.state[param].items()}

    def residual(reference, actual):
        r, v = reference.astype(np.float64), actual.astype(np.float64)
        delta = v-r
        rn, vn = float(np.linalg.norm(r)), float(np.linalg.norm(v))
        return dict(reference_l2=rn, actual_l2=vn,
            relative_l2=float(np.linalg.norm(delta))/max(rn,1e-12),
            maximum_absolute=float(np.max(np.abs(delta))),
            cosine=float(np.dot(r,v)/max(rn*vn,1e-24)))

    for initialization in ('zero','nonzero'):
        k = torch.arange(z.numel(), device='cuda', dtype=torch.float32).reshape(z.shape)
        initial = ([torch.zeros_like(z),torch.zeros_like(z)] if initialization == 'zero'
                   else [.1*torch.sin(k),.1*torch.cos(k)])
        starting_params = [v.detach().clone().requires_grad_(True) for v in initial]
        starting_opt = torch.optim.Adam(starting_params, lr=2., betas=(.9,.999), eps=1e-8)
        for moments in ('fresh','populated'):
            check()
            label = f'{initialization}-{moments}'
            before = vector(starting_params)
            starting_state = deepcopy(starting_opt.state_dict())
            starting_values = [p.detach().clone() for p in starting_params]
            noise = (torch.randn(z.shape,generator=rng,device='cuda',dtype=torch.float32)*.25,
                     torch.randn(source.shape,generator=rng,device='cuda',dtype=torch.float32)*.06)
            arrays = dict(before=before, latent_noise=noise[0].cpu().numpy(), pixel_noise=noise[1].cpu().numpy())
            arrays.update(state_arrays(starting_opt,'before_state'))
            report['active_case'] = label
            write(out/'numerical-validation.json',report)
            np.savez_compressed(out/f'numerical-{label}.npz',**arrays)
            reference = None
            next_values = next_state = None
            for name in ('J1','S1','J2','S2','J3','S3'):
                check()
                params = [v.detach().clone().requires_grad_(True) for v in starting_values]
                optimizer = torch.optim.Adam(params,lr=2.,betas=(.9,.999),eps=1e-8)
                optimizer.load_state_dict(deepcopy(starting_state))
                optimizer.zero_grad(set_to_none=True)
                backward.context = f'{label}-{name}'
                report['active_evaluation'] = name
                write(out/'numerical-validation.json',report)
                values = backward_step(*params,frequency,source,message,noise,decode,
                    features,metric,finite,'joint' if name[0]=='J' else 'serial-aawarn',backward)
                grad = vector([p.grad for p in params])
                if not np.isfinite(grad).all() or float(np.linalg.norm(grad.astype(np.float64))) == 0:
                    raise stop('numeric_gate_failed',f'Nonfinite/zero gate gradient: {label}-{name}')
                check()  # No update after a deadline/resource breach.
                optimizer.step()
                finite(*params)
                update = vector(params)-before
                arrays[name+'_gradient'], arrays[name+'_update'] = grad,update
                arrays.update(state_arrays(optimizer,name+'_state'))
                all_finite = all(np.isfinite(v).all() for v in arrays.values()) and all(np.isfinite(v) for v in values.values())
                moved = float(np.linalg.norm(update.astype(np.float64))) > 0
                report['evaluations'].append(dict(case=label,evaluation=name,
                    components=values,all_finite=bool(all_finite),parameter_changed=bool(moved)))
                np.savez_compressed(out/f'numerical-{label}.npz',**arrays)
                write(out/'numerical-validation.json',report)
                if not all_finite or not moved:
                    raise stop('numeric_gate_failed',f'Nonfinite/no movement: {label}-{name}')
                if name == 'J1':
                    reference = (values,grad,update)
                    next_values = [p.detach().clone() for p in params]
                    next_state = deepcopy(optimizer.state_dict())
                else:
                    components = {key:dict(reference=value,actual=values[key],
                        absolute=abs(values[key]-value),tolerance=1e-5+1e-5*abs(value))
                        for key,value in reference[0].items()}
                    g,u = residual(reference[1],grad),residual(reference[2],update)
                    g['absolute_tolerance'] = 1e-9+5e-4*float(np.max(np.abs(reference[1])))
                    differences = {}
                    for key in list(arrays):
                        if key.startswith(name+'_state_'):
                            suffix = key[len(name+'_state_'):]
                            delta = arrays[key]-arrays['J1_state_'+suffix]
                            arrays[name+'_state_difference_'+suffix] = delta
                            differences[suffix] = float(np.max(np.abs(delta)))
                    arrays[name+'_gradient_difference'] = grad-reference[1]
                    arrays[name+'_update_difference'] = update-reference[2]
                    passed = (all(v['absolute'] <= v['tolerance'] for v in components.values())
                        and g['relative_l2'] <= 1e-4 and g['maximum_absolute'] <= g['absolute_tolerance']
                        and u['relative_l2'] <= 1e-4 and u['maximum_absolute'] <= 1e-3)
                    report['comparisons'].append(dict(case=label,reference='J1',actual=name,
                        kind='same-schedule jitter' if name[0]=='J' else 'cross-schedule disagreement',
                        components=components,gradient=g,update=u,state_maximum_absolute=differences,
                        all_finite=bool(all_finite),passed=bool(passed),arrays=f'numerical-{label}.npz'))
                    np.savez_compressed(out/f'numerical-{label}.npz',**arrays)
                    write(out/'numerical-validation.json',report)
                    if not passed:
                        raise stop('numeric_gate_failed',f'Frozen comparison failed: {label}-{name}')
                del optimizer,params,values,grad,update
                check()
            # Fixed J1 trajectory, never a selected best repetition.
            starting_params = [v.detach().clone().requires_grad_(True) for v in next_values]
            starting_opt = torch.optim.Adam(starting_params,lr=2.,betas=(.9,.999),eps=1e-8)
            starting_opt.load_state_dict(next_state)
            del arrays,noise,reference,starting_values,starting_state,next_values,next_state
        del starting_opt,starting_params,initial
    report['passed'] = len(report['comparisons']) == 20
    report.pop('active_case',None); report.pop('active_evaluation',None)
    write(out/'numerical-validation.json',report)
    return report

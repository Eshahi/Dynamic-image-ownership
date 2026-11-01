"""SERVER ONLY: lean F6 options on top of the retained F6Writer.

Importing this module imports only the standard library. Local tests may build a
CPU instance by hand. The F5 reader, keys and second tier are never changed.
"""
from __future__ import annotations

import itertools
import math
import statistics
import time

from tifs_writer import F6Writer, writer_gradient_scope

LEAN_VARIANTS = ("f5-budget", "f6-generic", "f6-noise", "f6-x0")
SURROGATE_VARIANTS = ("f6-generic", "f6-noise", "f6-x0")


class LeanWriter(F6Writer):
    """Adds a rendered companion signal, per-image quality control and an optimizer for noisy gradients."""

    def __init__(self, assets, base_config, frozen_config, *, settings, policy, metric, within_cushion):
        self.settings, self.policy = settings, dict(policy)
        self.metric, self.within_cushion = metric, within_cushion
        self._spec = None
        super().__init__(assets, base_config, frozen_config)

    def _offload_codec(self):
        # One card holds every writer model: moving them each update only costs time.
        if self.policy.get("offload"):
            super()._offload_codec()

    def _checkpoint_vae(self, vae):
        if self.policy.get("checkpoint", True):
            super()._checkpoint_vae(vae)

    def _checkpoint_unet(self, unet):
        if self.policy.get("checkpoint", True):
            super()._checkpoint_unet(unet)

    def _surrogate(self, image, family, strength, variant, source_id, step, stream):
        t = self.torch
        enabled = bool(self.policy.get("bf16")) and variant in ("f6-noise", "f6-x0")
        # The saved final image is still read in fp32; this affects the gradient path only.
        with t.autocast(device_type=image.device.type, dtype=t.bfloat16, enabled=enabled):
            output = super()._surrogate(image, family, strength, variant, source_id, step, stream)
        return output.float()

    def _unit(self, value):
        return value / (value.norm() + 1e-12)

    @writer_gradient_scope
    def _optimize(self, rgb01, w, source_id, variant, *, refine=False):
        spec = self.settings
        steps = spec["refine_steps"] if refine else spec["robust_steps"]
        psnr = float(spec["refine_psnr_db"] if refine else self._spec["robust_psnr_db"])
        if variant == "f5-budget":
            return self.f5.robust_pgd(self.reader, rgb01, self.layout, w, psnr, steps, 4.0, 0.0)
        t = self.torch
        x = self.reader.tensor(rgb01)
        budget = 10 ** (-psnr / 20) * math.sqrt(rgb01.size)
        eta = t.zeros_like(x, requires_grad=True)
        momentum = None
        use_momentum = not refine and self.policy.get(variant, {}).get("momentum", False)
        for step in range(steps):
            clean_loss = self._loss((x + eta).clamp(0, 1), w)
            gradient, = t.autograd.grad(clean_loss, eta)
            del clean_loss
            if not refine:
                family, strength = spec["cycle"][step % len(spec["cycle"])]
                surrogate = self._surrogate((x + eta).clamp(0, 1), family, strength, variant,
                                            source_id, step, "optimization")
                surrogate_loss = self._loss(surrogate, w)
                added, = t.autograd.grad(surrogate_loss, eta)
                # SDXL's input gain is far above SD1.5's, so a raw sum would not weigh the two terms equally.
                gradient = self._unit(gradient) + self._unit(added)
                del surrogate_loss, surrogate, added
                self._offload_codec()
                if use_momentum:
                    momentum = self._unit(gradient) if momentum is None else spec["momentum"] * momentum + self._unit(gradient)
                    gradient = momentum
            self._finite(gradient, "input gradient")
            with t.no_grad():
                lr = budget * (.2 if step < steps // 2 else .05)
                eta -= lr * gradient / (gradient.norm() + 1e-12)
                delta = (x + eta).clamp(0, 1) - x
                eta.copy_(delta * (budget / delta.norm().clamp_min(budget)))
            del gradient
        with t.no_grad():
            return self._finite((x + eta).clamp(0, 1), "optimized RGB")[0].permute(1, 2, 0).double().cpu().numpy()

    def _render(self, source, signs, target_db):
        """Render the chip pattern through the SD1.5 decoder, scaled to an exact RMS. No optimization."""
        n, t, f5 = self.np, self.torch, self.f5
        layout, vae = self.layout, self.reader.vae
        values = (layout.weights * layout.signs) * (n.asarray(signs, n.float64)[layout.chip] / layout.norms[layout.chip])
        latent = n.zeros((4, f5.LATENT, f5.LATENT))
        n.add.at(latent, (layout.ch, layout.u, layout.v), values)
        pattern = t.from_numpy((layout.dct.T @ latent @ layout.dct).astype(n.float32))[None].to(self.reader.device)
        target = 255 * 10 ** (-float(target_db) / 20)
        with t.inference_mode():
            z = self.reader.encode(self.reader.tensor(source.astype(n.float64) / 255))[None]
            base = vae.decode(z / f5.SCALE).sample
            probe = vae.decode((z + pattern * .02) / f5.SCALE).sample
            rms = float((((probe - base) / 2 * 255) ** 2).mean().sqrt())
            if not (math.isfinite(rms) and rms > 0):
                raise FloatingPointError("Rendered pattern has no finite response")
            out = vae.decode((z + pattern * (.02 * target / rms)) / f5.SCALE).sample
            change = ((out - base) / 2 * 255)[0].permute(1, 2, 0).double().cpu().numpy()
        achieved = float(n.sqrt((change ** 2).mean()))
        if not (math.isfinite(achieved) and achieved > 0):
            raise FloatingPointError("Rendered change is empty")
        rendered = n.clip(n.rint(source.astype(n.float64) + change * (target / achieved)), 0, 255).astype(n.uint8)
        return rendered, dict(target_db=float(target_db), target_rms=target,
                              saved_rms=float(n.sqrt(((rendered.astype(n.float64) - source) ** 2).mean())))

    def embed_arm(self, rgb, spec, source_id):
        n, t, f5 = self.np, self.torch, self.f5
        variant = spec["variant"]
        if self._closed or variant not in LEAN_VARIANTS:
            raise ValueError("Closed writer or unknown lean variant")
        source = n.asarray(rgb)
        if source.dtype != n.uint8 or source.shape != (512, 512, 3):
            raise ValueError("Lean writer requires native RGB8 512x512 input")
        self._spec = spec
        tick = time.monotonic()
        device = self.reader.device
        self.reader.vae.to(device=device, dtype=t.float32)
        try:
            features = self.features(source, 7)
            luma = f5.v5.luminance_from_rgb(source.tolist())
            q, ws = f5._semantic_pattern(self.checked, self.key, self.config, self.owner, features, luma)
            w = ws if variant == "f5-budget" else t.as_tensor(n.asarray(ws, n.float32), device=device)
            start, render = source, None
            if spec.get("render_db") is not None:
                start, render = self._render(source, ws, spec["render_db"])
            robust = self._optimize(start.astype(n.float64) / 255, w, source_id, variant)
            robust_rgb = n.clip(n.rint(robust * 255), 0, 255)
            attempts = []
            for scale in self.settings["residual_scales"]:
                # Larger budgets may exceed the strict bar on some images: scale this image's residual only.
                current = n.clip(n.rint(source + scale * (robust_rgb - source)), 0, 255)
                current, _, _ = self._fragile(current, q)
                refined = self._optimize(current / 255, w, source_id, variant, refine=True)
                current = n.clip(n.rint(refined * 255), 0, 255)
                current, intended_h, fragile_report = self._fragile(current, q)
                output = current.astype(n.uint8)
                metrics = self.metric(source, output)
                attempts.append(dict(scale=scale, metrics=metrics))
                if self.within_cushion(metrics):
                    break
            verification = f5.detect_rgb(output, self.reader.latent(output), self.owner_id, self.profile,
                self.features(output, 7), band=[4, 32], whitening=1.0, binding="soft")
            decoded_h = verification["instance"].get("decoded_code")
            payload = dict(q=f"{q:08x}", h=decoded_h, h_target_basis="native clean decoded h; intended h exported separately",
                           intended_h=f"{intended_h:08x}")
            if t.cuda.is_available():
                t.cuda.synchronize()
            report = dict(family="f6-lean-fixed-reader", variant=variant, source_id=str(source_id),
                robust_psnr_db=spec["robust_psnr_db"], render_db=spec.get("render_db"), render=render,
                refine_psnr_db=self.settings["refine_psnr_db"], attempts=attempts, residual_scale=attempts[-1]["scale"],
                semantic_code=payload["q"], payload=payload, verification=verification,
                verified=verification["outcome"] == "both_match", instance_channel=fragile_report,
                seconds=time.monotonic() - tick, reader_dispatch="f5-r2", binding="soft", semantic_views=7,
                policy=self.policy, cycle=self.settings["cycle"], posterior="mode",
                gradient_combination=None if variant == "f5-budget" else self.settings["gradient_combination"],
                momentum=self.policy.get(variant, {}).get("momentum", False))
            return output, payload, report
        except BaseException:
            self.close()
            raise

    @writer_gradient_scope
    def _timed_gradients(self, x, w, variant, family, strength, source_id, draws):
        t = self.torch
        gradients, seconds, peak = [], [], 0
        for draw in draws:
            eta = t.zeros_like(x, requires_grad=True)
            if t.cuda.is_available():
                t.cuda.reset_peak_memory_stats()
                t.cuda.synchronize()
            tick = time.monotonic()
            image = (x + eta).clamp(0, 1)
            if variant == "clean":
                loss = self._loss(image, w)
            else:
                loss = self._loss(self._surrogate(image, family, strength, variant, source_id, draw, "optimization"), w)
            gradient, = t.autograd.grad(loss, eta)
            if t.cuda.is_available():
                t.cuda.synchronize()
                peak = max(peak, t.cuda.max_memory_reserved())
            seconds.append(time.monotonic() - tick)
            self._finite(gradient, "probe gradient")
            gradients.append(gradient.detach().flatten().cpu())
            del loss, gradient, image, eta
        return gradients, seconds, peak

    def _agreement(self, gradients):
        t = self.torch
        pairs = [float(t.nn.functional.cosine_similarity(a, b, dim=0)) for a, b in itertools.combinations(gradients, 2)]
        return statistics.median(pairs) if pairs else None

    def measure(self, rgb, source_id):
        """Timing, memory and gradient agreement only. No native outcome reaches this decision."""
        n, t, f5 = self.np, self.torch, self.f5
        source = n.asarray(rgb)
        features = self.features(source, 7)
        q, ws = f5._semantic_pattern(self.checked, self.key, self.config, self.owner, features,
                                     f5.v5.luminance_from_rgb(source.tolist()))
        w = t.as_tensor(n.asarray(ws, n.float32), device=self.reader.device)
        # Measure near a part-written image, where the real optimizer spends its updates.
        tick = time.monotonic()
        partial = f5.robust_pgd(self.reader, source.astype(n.float64) / 255, self.layout, ws, 46.0, 30, 4.0, 0.0)
        result = dict(source=str(source_id), q=f"{q:08x}", reader_gradient_seconds=(time.monotonic() - tick) / 30)
        x = self.reader.tensor(partial)
        # The first draw of each path can include model loading: it is dropped from every timing.
        draws = list(range(1000, 1007))
        _, seconds, _ = self._timed_gradients(x, w, "clean", None, None, source_id, [0, 1, 2, 3])
        result["clean_graph_seconds"] = statistics.median(seconds[1:])
        reference = {}
        for variant in ("f6-noise", "f6-x0"):
            gradients, seconds, peak = self._timed_gradients(x, w, variant, "R1", .2, source_id, draws)
            reference[variant] = gradients
            r0, r0_seconds, _ = self._timed_gradients(x, w, variant, "R0", .2, source_id, draws[:4])
            clean, _, _ = self._timed_gradients(x, w, "clean", None, None, source_id, [0])
            result[variant] = dict(pairwise_cos_median=self._agreement(gradients),
                seconds_r1=statistics.median(seconds[1:]), seconds_r0=statistics.median(r0_seconds[1:]),
                peak_reserved_bytes=peak, surrogate_over_clean_norm=float(gradients[0].norm() / (clean[0].norm() + 1e-12)),
                r1_r0_cos=float(t.nn.functional.cosine_similarity(gradients[0], r0[0], dim=0)))
            del gradients, r0, clean
        noise = reference["f6-noise"]
        saved = dict(self.policy)
        try:
            self.policy["bf16"] = True
            fast, seconds, _ = self._timed_gradients(x, w, "f6-noise", "R1", .2, source_id, draws[:4])
            cosines = [float(t.nn.functional.cosine_similarity(a, b, dim=0)) for a, b in zip(noise, fast)]
            result["bf16"] = dict(time_ratio=statistics.median(seconds[1:]) / result["f6-noise"]["seconds_r1"],
                                  gradient_cos_median=statistics.median(cosines))
        finally:
            self.policy = dict(saved)
        try:
            self.policy["checkpoint"] = False
            _, seconds, peak = self._timed_gradients(x, w, "f6-x0", "R1", .2, source_id, draws[:4])
            total = t.cuda.mem_get_info()[1] if t.cuda.is_available() else 0
            result["no_checkpoint"] = dict(fits=True, peak_reserved_bytes=peak, free_bytes_at_peak=total - peak,
                time_ratio=statistics.median(seconds[1:]) / result["f6-x0"]["seconds_r1"])
        except t.cuda.OutOfMemoryError:
            t.cuda.empty_cache()
            result["no_checkpoint"] = dict(fits=False)
        finally:
            self.policy = dict(saved)
        return result

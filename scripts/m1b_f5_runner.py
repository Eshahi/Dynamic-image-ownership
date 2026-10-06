"""Development integration runner for F5 (and any f5_latent_codec-compatible config).

Reads a manifest of source IDs and paths. Deterministic sharding,
journaling/resume, never substitutes seeds. Embeds through
scripts/f5_latent_codec.py at configs/f5-r2.json (frozen). Runs the T3
grid, T4 residual-transfer arms, T5 pairs and C0/wrong-owner controls.
Writes run.json, receipts and per-cell endpoints via
scripts/m1_confirmatory_endpoints.py.

Reuse: f5_latent_codec, revised_watermark_v5, m1_confirmatory_endpoints.
No new broker/launcher/audit layers. Held-out execution is not implemented here:
the frozen patch/comparator/cluster protocol still needs adoption and approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

VERSION = "m1b-f5-runner-v3"  # v3: GPU adapter fixes, complete inventory and honest failure status
MANIFEST_SCHEMA = "m1b-f5-manifest-v1"
RUN_SCHEMA = "m1b-f5-run-v1"

T3_STRENGTHS = (0.05, 0.1, 0.2, 0.4)
T3_SEEDS = (0, 1, 2)
T4_SCALES = (0.5, 1.0)
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


RULES = ("both_match", "semantic", "semantic_checked", "semantic_assumed", "any_found")


def success_of(det: dict[str, Any], rule: str) -> bool:
    """Event of one detection under a named rule (pure, unit-tested).

    ``both_match``: final state both_match (clean positives, T4/T5 false full attribution).
    ``semantic``: the semantic channel found the claimed owner and its content matches, whatever the
    fragile instance tier says; this is the T3 regeneration endpoint, since img2img is expected to remove
    the fragile tier.  ``semantic_checked``: the same, with the mark strong enough to be read so its code
    was compared with the suspect's (``read``).  ``semantic_assumed``: found only by the recomputed
    pattern, which v5 counts as carrying the recomputed code without a comparison.  ``any_found``: either
    channel found the claimed owner (strictest negative event).
    """
    if rule not in RULES:
        raise ValueError("unknown rule " + rule)
    if rule == "both_match":
        return det.get("outcome") == "both_match"
    sem = det.get("semantic") or {}
    if rule == "any_found":
        return bool(sem.get("found") or (det.get("instance") or {}).get("found"))
    ok = bool(sem.get("found") and sem.get("content_match"))
    if rule == "semantic":
        return ok
    return ok and (bool(sem.get("read")) if rule == "semantic_checked" else not sem.get("read"))


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _atomic_json(path: Path, value: Any) -> None:
    import os as _os

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(value, f, indent=2, ensure_ascii=False, sort_keys=False)
        f.write("\n")
        f.flush()
        _os.fsync(f.fileno())
    tmp.replace(path)


def _valid_id(s: Any) -> bool:
    return isinstance(s, str) and bool(_ID_RE.match(s))


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError(f"schema must be {MANIFEST_SCHEMA!r}")
    if manifest.get("version") != VERSION:
        raise ValueError(f"version must be {VERSION!r}")
    if manifest.get("data_split") != "development":
        raise ValueError("this recovery runner supports development manifests only; held-out package remains pending")
    cfg_p = manifest.get("config_path")
    if not isinstance(cfg_p, str) or not cfg_p:
        raise ValueError("config_path must be a nonempty string")
    prof_p = manifest.get("profile_path")
    if not isinstance(prof_p, str) or not prof_p:
        raise ValueError("profile_path must be a nonempty string")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or len(sources) == 0:
        raise ValueError("sources must be a nonempty list")
    seen: set[str] = set()
    for i, s in enumerate(sources):
        if not isinstance(s, dict):
            raise ValueError(f"sources[{i}] must be an object")
        sid = s.get("id")
        if not _valid_id(sid):
            raise ValueError(f"sources[{i}].id invalid: {sid!r}")
        if sid in seen:
            raise ValueError(f"duplicate source id: {sid!r}")
        seen.add(sid)
        p = s.get("path")
        if not isinstance(p, str) or not p:
            raise ValueError(f"sources[{i}].path must be a nonempty string")
        owner = s.get("owner")
        if not isinstance(owner, str) or not owner:
            raise ValueError(f"sources[{i}].owner must be a nonempty string")
        wo = s.get("wrong_owner")
        if wo is not None and (not isinstance(wo, str) or not wo or wo == owner):
            raise ValueError(f"sources[{i}].wrong_owner invalid")
    for key in ("t4_pairs", "t5_pairs"):
        pairs = manifest.get(key)
        if pairs is None:
            continue
        if not isinstance(pairs, list):
            raise ValueError(f"{key} must be a list")
        pids: set[str] = set()
        for i, pr in enumerate(pairs):
            if not isinstance(pr, dict):
                raise ValueError(f"{key}[{i}] must be an object")
            pid = pr.get("id")
            if not _valid_id(pid):
                raise ValueError(f"{key}[{i}].id invalid: {pid!r}")
            if pid in pids:
                raise ValueError(f"duplicate {key} id: {pid!r}")
            pids.add(pid)
            for fk in ("donor", "recipient", "a", "b"):
                v = pr.get(fk)
                if v is not None and not _valid_id(v):
                    raise ValueError(f"{key}[{i}].{fk} invalid: {v!r}")
            if key == "t4_pairs" and (pr.get("donor") is None or pr.get("recipient") is None):
                raise ValueError(f"t4_pairs[{i}] needs donor and recipient")
            left, right = ((pr.get("donor"), pr.get("recipient")) if key == "t4_pairs"
                           else (pr.get("a") or pr.get("donor"), pr.get("b") or pr.get("recipient")))
            if left not in seen or right not in seen or left == right:
                raise ValueError(f"{key}[{i}] needs two distinct declared sources")
    for k in ("t3_strengths", "t3_seeds"):
        v = manifest.get(k)
        if v is None:
            continue
        if not isinstance(v, list) or len(v) == 0:
            raise ValueError(f"{k} must be a nonempty list")
        if k == "t3_strengths" and any(not isinstance(x, (int, float)) or not 0 < x < 1 for x in v):
            raise ValueError("t3_strengths entries must be in (0,1)")
        if k == "t3_seeds" and any(not isinstance(x, int) or x < 0 for x in v):
            raise ValueError("t3_seeds entries must be nonnegative ints")
        if len(set(v)) != len(v):
            raise ValueError(f"duplicate entries in {k}")
    return manifest


def shard_sources(sources: list[dict[str, Any]], shard_index: int, shard_count: int) -> list[dict[str, Any]]:
    if not isinstance(shard_index, int) or not isinstance(shard_count, int):
        raise ValueError("shard_index and shard_count must be ints")
    if shard_count < 1 or not 0 <= shard_index < shard_count:
        raise ValueError("shard_index out of range")
    ordered = sorted(sources, key=lambda s: s["id"])
    return [s for i, s in enumerate(ordered) if i % shard_count == shard_index]


def _journal_path(output_dir: Path) -> Path:
    return output_dir / "journal.jsonl"


def read_journal(output_dir: Path) -> dict[str, dict[str, Any]]:
    jp = _journal_path(output_dir)
    if not jp.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for line in jp.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rid = row.get("id")
        if isinstance(rid, str):
            out[rid] = row
    return out


def append_journal(output_dir: Path, row: dict[str, Any]) -> None:
    jp = _journal_path(output_dir)
    jp.parent.mkdir(parents=True, exist_ok=True)
    with jp.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_config(config_path: Path) -> dict[str, Any]:
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    if cfg.get("schema") != "f5-r2-frozen-v1":
        raise ValueError(f"unexpected config schema: {cfg.get('schema')!r}")
    return cfg


def _f5_embed_kwargs(cfg: dict[str, Any]) -> dict[str, Any]:
    emb = cfg["embedding"]
    det = cfg["detection"]
    return dict(
        psnr_db=float(emb["psnr_db"]),
        steps=int(emb["steps"]),
        target_margin=float(emb["target_margin"]),
        mask_power=float(emb.get("mask_power", 0.0)),
        band=tuple(cfg["robust_tier"]["band"]),
        whitening=float(cfg["robust_tier"]["whitening"]),
        refine_rounds=int(emb.get("refine_rounds", 1)),
        binding=str(det["binding"]),
    )


def planned_row_ids(shard, strengths, seeds, t4_pairs, t5_pairs) -> list[str]:
    """Declare the full inventory before image/model failures can remove rows."""
    ids = []
    for entry in shard:
        sid = entry["id"]
        ids.append(f"{sid}:embed")
        for control in ("C0", "C1"):
            for claim in ("correct", "wrong_owner"):
                ids.append(f"{sid}:clean:{control}:{claim}")
            doses = [("vae_mode", None, None)] + [("diffusion", s, sd) for s in strengths for sd in seeds]
            for dose, strength, seed in doses:
                claims = ("correct", "wrong_owner") if control == "C1" else ("correct",)
                ids.extend(f"{sid}:t3:{control}:{dose}:{strength}:{seed}:{claim}" for claim in claims)
    for pair in t4_pairs:
        for scale in T4_SCALES:
            for arm in ("donor_C1", "donor_C0_sham"):
                ids.extend(f"{pair['id']}:t4:{scale}:{arm}:{role}" for role in ("donor_claim", "recipient_claim"))
    for pair in t5_pairs:
        ids.extend(f"{pair['id']}:t5:{endpoint}:{arm}:cross_owner" for endpoint in ("a", "b") for arm in ("C0", "C1"))
    return ids


def summarize_cells(planned: list[str], journal: dict[str, dict[str, Any]], strengths) -> dict[str, Any]:
    from scripts.m1_confirmatory_endpoints import cell

    cells = {}

    def add(name, ids, kind, rule):
        if not ids:
            return
        observations = {rid: (success_of(journal[rid].get("detection", {}), rule)
                             if journal.get(rid, {}).get("outcome") == "completed" else None) for rid in ids}
        value = cell(sorted(ids), observations, event_kind="positive_success" if kind == "positive" else "negative_error")
        value["event_rule"] = rule
        if name.startswith(("t3_", "t4_", "t5_")):
            value["caveat"] = "Development row counts only; repeated seeds/arms are clustered. Row-level intervals are not independent-source confidence bounds or a milestone verdict."
            value["meets_numerical_target"] = None
        cells[name] = value

    add("clean_C1_correct_both_match", [k for k in planned if ":clean:C1:correct" in k], "positive", "both_match")
    for control in ("C0", "C1"):
        for claim in (("correct", "wrong_owner") if control == "C0" else ("wrong_owner",)):
            ids = [k for k in planned if f":clean:{control}:{claim}" in k]
            for rule in ("both_match", "semantic", "any_found"):
                add(f"clean_{control}_{claim}_{rule}", ids, "negative", rule)
    doses = [("vae_mode", ":t3:C1:vae_mode:")] + [(f"diffusion_{s}", f":t3:C1:diffusion:{s}:") for s in strengths]
    for label, pattern in doses:
        correct = [k for k in planned if pattern in k and k.endswith(":correct")]
        wrong = [k for k in planned if pattern in k and k.endswith(":wrong_owner")]
        for rule in ("semantic", "semantic_checked", "semantic_assumed", "both_match"):
            add(f"t3_C1_{label}_correct_{rule}", correct, "positive", rule)
        for rule in ("semantic", "any_found"):
            add(f"t3_C1_{label}_wrong_owner_{rule}", wrong, "negative", rule)
    negatives = [("t3_C0_correct", [k for k in planned if ":t3:C0:" in k]),
                 ("t4_donor_claim", [k for k in planned if ":t4:" in k and k.endswith(":donor_claim")]),
                 ("t5_cross_owner", [k for k in planned if ":t5:" in k])]
    for name, ids in negatives:
        for rule in ("semantic", "any_found", "both_match"):
            add(f"{name}_{rule}", ids, "negative", rule)
    return cells


def inventory_status(planned: list[str], journal: dict[str, dict[str, Any]]) -> dict[str, Any]:
    missing = [rid for rid in planned if rid not in journal]
    failures = [rid for rid in planned if rid in journal and journal[rid].get("outcome") != "completed"]
    return dict(planned_rows=len(planned), missing_rows=len(missing), failed_rows=len(failures),
                completed_rows=sum(journal.get(rid, {}).get("outcome") == "completed" for rid in planned),
                outcome="completed" if not missing and not failures else "incomplete")


def semantic_feature(models, clip, transform, rgb, views):
    # Share the exact single/7-view implementation used by the frozen development gate.
    from scripts.f5_gate import semantic_feature as gate_feature
    return gate_feature(models, clip, transform, rgb, views)


def residual_transfer_rgb(recipient, donor_c1, donor_c0, scale):
    import numpy as np
    from three_threat_protocol import residual_transfer
    return np.asarray(residual_transfer(recipient.tolist(), donor_c1.tolist(), donor_c0.tolist(), scale), dtype=np.uint8)


def _image_path(images_dir: Path, row_id: str) -> Path:
    # Journal IDs retain colons, but filenames must also work on Windows.
    return images_dir / (row_id.replace(":", "_") + ".png")


def _receipt_for_rgb(rgb_array, path: Path) -> dict[str, Any]:
    import numpy as np

    data = np.asarray(rgb_array, dtype=np.uint8).tobytes()
    return dict(path=str(path), sha256=_sha_bytes(data), width=int(rgb_array.shape[1]), height=int(rgb_array.shape[0]))


def run_manifest(
    manifest_path: Path,
    output_dir: Path,
    shard_index: int = 0,
    shard_count: int = 1,
    *,
    resume: bool = True,
) -> Path:
    """Execute manifest shard. Never substitutes seeds. GPU required."""
    import subprocess as _sp

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    cfg = _load_config(ROOT / manifest["config_path"])
    profile_path = ROOT / manifest["profile_path"]

    sources = manifest["sources"]
    shard = shard_sources(sources, shard_index, shard_count)
    strengths = tuple(manifest.get("t3_strengths", list(T3_STRENGTHS)))
    seeds = tuple(manifest.get("t3_seeds", list(T3_SEEDS)))
    t4_pairs = manifest.get("t4_pairs", [])
    t5_pairs = manifest.get("t5_pairs", [])
    planned = planned_row_ids(shard, strengths, seeds, t4_pairs, t5_pairs)

    if output_dir.exists() and not resume and _journal_path(output_dir).exists():
        raise FileExistsError(f"journal exists at {_journal_path(output_dir)}; use --resume or a fresh output_dir")
    output_dir.mkdir(parents=True, exist_ok=True)

    journal_done = read_journal(output_dir) if resume else {}

    commit = _sp.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
    dirty = _sp.check_output(
        ["git", "status", "--porcelain", "--", "scripts/f5_latent_codec.py", "scripts/m1b_f5_runner.py"],
        cwd=str(ROOT),
        text=True,
    ).strip()
    if dirty:
        raise SystemExit(f"commit f5 code and runner before running: {dirty}")
    context = dict(commit=commit, manifest_sha256=_sha_file(manifest_path),
                   config_sha256=_sha_file(ROOT / manifest["config_path"]),
                   profile_sha256=_sha_file(profile_path), shard_index=shard_index, shard_count=shard_count)
    context_path = output_dir / "run-context.json"
    if context_path.exists() and json.loads(context_path.read_text(encoding="utf-8")) != context:
        raise ValueError("resume context changed; preserve this run and use a fresh output directory")
    if journal_done and not context_path.exists():
        raise ValueError("legacy journal has no resume context; preserve it and use a fresh output directory")
    _atomic_json(context_path, context)

    import numpy as np
    from PIL import Image

    import scripts.f5_latent_codec as f5
    import scripts.revised_watermark_v5 as v5
    import three_threat_models as ttm

    profile = v5.validate_profile(json.loads(profile_path.read_text(encoding="utf-8")))
    config_id = v5.detector_config_id(profile)
    assets = ROOT / ".thesis-build" / "assets" / "a6"

    started = time.monotonic()
    _state: dict[str, Any] = {}

    def _ensure_models() -> None:
        if "reader" in _state:
            return
        import importlib.metadata as _md

        from a6_clip_visual import load_visual_encoder

        clip, transform = load_visual_encoder(assets / "clip" / "ViT-B-32.pt", device="cpu")
        lpips_metric = ttm.load_lpips(assets, Path(_md.distribution("lpips").locate_file("lpips")))
        pipe = ttm.load_regenerator(assets)
        reader = f5.Reader(assets)
        _state.update(dict(clip=clip, transform=transform, lpips=lpips_metric, pipe=pipe, reader=reader))

    def _clip_feature(rgb: np.ndarray, views: int) -> list[float]:
        return semantic_feature(ttm, _state["clip"], _state["transform"], rgb, views)

    def _emit(row: dict[str, Any]) -> None:
        append_journal(output_dir, row)
        journal_done[row["id"]] = row

    embed_kwargs = _f5_embed_kwargs(cfg)
    sem_views = int(cfg["embedding"].get("semantic_views", cfg["detection"].get("semantic_views", 7)))
    binding = str(cfg["detection"]["binding"])
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    def _load_source_rgb(entry: dict[str, Any]) -> np.ndarray:
        p = Path(entry["path"])
        if not p.is_absolute():
            p = ROOT / p
        return np.asarray(Image.open(p).convert("RGB"), np.uint8)

    saved_marked: dict[str, Path] = {}
    saved_source: dict[str, Path] = {}

    for entry in shard:
        sid = entry["id"]
        owner = entry["owner"]
        wrong_owner = entry.get("wrong_owner") or "thesis:owner:99"

        _ensure_models()
        reader = _state["reader"]
        pipe = _state["pipe"]

        c1_path = images_dir / f"{sid}-C1.png"
        c0_path = images_dir / f"{sid}-C0.png"
        embed_row = journal_done.get(f"{sid}:embed") if resume else None
        if embed_row and embed_row.get("outcome") != "completed":
            # Failed scientific rows stay adverse. A repaired program uses a new run.
            continue
        if embed_row:
            if not c0_path.exists() or not c1_path.exists():
                raise ValueError(f"saved source/mark missing for resume: {sid}")
            c0 = np.asarray(Image.open(c0_path).convert("RGB"), np.uint8)
            marked = np.asarray(Image.open(c1_path).convert("RGB"), np.uint8)
            if _receipt_for_rgb(marked, c1_path)["sha256"] != embed_row["image"]["sha256"]:
                raise ValueError(f"saved mark changed for resume: {sid}")
            if _receipt_for_rgb(c0, c0_path)["sha256"] != embed_row["source_image"]["sha256"]:
                raise ValueError(f"saved source changed for resume: {sid}")
            saved_marked[sid], saved_source[sid] = c1_path, c0_path
        else:
            if resume and f"{sid}:source:load" in journal_done:
                continue
            try:
                source = _load_source_rgb(entry)
                if source.shape != (512, 512, 3):
                    raise ValueError("frozen F5 smoke requires canonical 512x512 RGB")
            except Exception as e:
                _emit(dict(id=f"{sid}:source:load", source_id=sid, axis="source", outcome="failed", error=str(e)))
                continue

            tick = time.monotonic()
            try:
                feat = _clip_feature(source, sem_views)
                marked_rgb, report = f5.embed_rgb(source, owner, profile, feat, reader, **embed_kwargs)
            except Exception as e:
                _emit(dict(id=f"{sid}:embed", source_id=sid, axis="embed", outcome="failed", error=str(e), seconds=time.monotonic() - tick))
                continue

            try:
                Image.fromarray(marked_rgb).save(c1_path)
                Image.fromarray(source).save(c0_path)
                marked = np.asarray(Image.open(c1_path).convert("RGB"), np.uint8)
                c0 = np.asarray(Image.open(c0_path).convert("RGB"), np.uint8)
                saved_marked[sid] = c1_path
                saved_source[sid] = c0_path
                from m1_latent_reconstruction import quality
                measured_quality = quality(c0, marked)
                measured_quality["lpips"] = ttm.lpips_score(_state["lpips"], c0, marked)
                _emit(dict(id=f"{sid}:embed", source_id=sid, axis="embed", outcome="completed",
                           seconds=time.monotonic() - tick, image=_receipt_for_rgb(marked, c1_path),
                           source_image=_receipt_for_rgb(c0, c0_path),
                           quality=measured_quality,
                           report={k: v for k, v in report.items() if k != "verification"},
                           self_verification=report.get("verification", {}).get("outcome")))
            except Exception as e:
                _emit(dict(id=f"{sid}:embed", source_id=sid, axis="embed", outcome="failed", stage="save_or_quality", error=str(e)))
                continue

        import torch as _torch

        def _vae_mode(rgb: np.ndarray) -> np.ndarray:
            with _torch.inference_mode():
                t = pipe.image_processor.preprocess(Image.fromarray(rgb)).to("cuda", dtype=pipe.vae.dtype)  # type: ignore[attr-defined]
                decoded = pipe.vae.decode(pipe.vae.encode(t).latent_dist.mode(), return_dict=False)[0]  # type: ignore[attr-defined]
                arr = pipe.image_processor.postprocess(decoded, output_type="np")  # type: ignore[attr-defined]
                arr, flags = pipe.run_safety_checker(arr, _torch.device("cuda"), pipe.text_encoder.dtype)  # type: ignore[attr-defined]
            if flags is None or len(flags) != 1 or bool(flags[0]):
                raise RuntimeError("safety_checker_blocked_output")
            return np.rint(np.clip(arr[0], 0, 1) * 255).astype(np.uint8)

        def _img2img(rgb: np.ndarray, strength: float, seed: int) -> np.ndarray:
            with _torch.inference_mode():
                result = pipe(
                    prompt="",
                    negative_prompt="",
                    image=Image.fromarray(rgb),
                    strength=strength,
                    num_inference_steps=20,
                    eta=0.0,
                    guidance_scale=1.0,
                    generator=_torch.Generator(device="cuda").manual_seed(seed),
                    num_images_per_prompt=1,
                    output_type="pil",
                    return_dict=True,
                )
            return np.asarray(ttm.validate_generated(result), np.uint8)

        def _detect(rgb: np.ndarray, z: np.ndarray, claimed: str) -> dict[str, Any]:
            feat_sus = _clip_feature(rgb, sem_views)
            return f5.detect_rgb(rgb, z, claimed, profile, feat_sus, binding=binding, band=embed_kwargs["band"], whitening=embed_kwargs["whitening"])

        pending: list[dict[str, Any]] = []
        for control, rgb in (("C0", c0), ("C1", marked)):
            for claimed, kind in ((owner, "correct"), (wrong_owner, "wrong_owner")):
                rid = f"{sid}:clean:{control}:{kind}"
                if resume and rid in journal_done:
                    continue
                pending.append(dict(id=rid, source_id=sid, axis="clean", control=control, claim_kind=kind, claimed_owner=claimed, rgb=rgb, tag="clean"))
        for control, rgb in (("C0", c0), ("C1", marked)):
            base_specs: list[tuple[str, Any, Any]] = [("vae_mode", None, None)] + [("diffusion", s, sd) for s in strengths for sd in seeds]
            for dose_kind, strength, seed in base_specs:
                # C1 gets correct+wrong_owner, C0 only correct (wrong-owner covered by clean)
                claim_pairs = ((owner, "correct"), (wrong_owner, "wrong_owner")) if control == "C1" else ((owner, "correct"),)
                for claimed, kind in claim_pairs:
                    rid = f"{sid}:t3:{control}:{dose_kind}:{strength}:{seed}:{kind}"
                    if resume and rid in journal_done:
                        continue
                    pending.append(
                        dict(id=rid, source_id=sid, axis="T3", control=control, dose=dose_kind, strength=strength, seed=seed, claim_kind=kind, claimed_owner=claimed, base_rgb=rgb, tag="t3")
                    )

        for spec in pending:
            rid = spec["id"]
            try:
                if spec["tag"] == "clean":
                    rgb = spec["rgb"]
                    z = reader.latent(rgb)
                    det = _detect(rgb, z, spec["claimed_owner"])
                    _emit(dict(id=rid, source_id=sid, axis=spec["axis"], control=spec["control"], claim_kind=spec["claim_kind"], claimed_owner=spec["claimed_owner"], outcome="completed", detection=det, image=_receipt_for_rgb(rgb, images_dir / f"{sid}-{spec['control']}.png") if spec["control"] in ("C0", "C1") else None))
                else:
                    base = spec["base_rgb"]
                    if spec["dose"] == "vae_mode":
                        attacked = _vae_mode(base)
                    else:
                        attacked = _img2img(base, float(spec["strength"]), int(spec["seed"]))
                    apath = _image_path(images_dir, rid)
                    Image.fromarray(attacked).save(apath)
                    attacked = np.asarray(Image.open(apath).convert("RGB"), np.uint8)
                    z = reader.latent(attacked)
                    det = _detect(attacked, z, spec["claimed_owner"])
                    _emit(
                        dict(
                            id=rid,
                            source_id=sid,
                            axis=spec["axis"],
                            control=spec["control"],
                            dose=spec.get("dose"),
                            strength=spec.get("strength"),
                            seed=spec.get("seed"),
                            claim_kind=spec["claim_kind"],
                            claimed_owner=spec["claimed_owner"],
                            outcome="completed",
                            detection=det,
                            image=_receipt_for_rgb(attacked, apath),
                        )
                    )
            except RuntimeError as e:
                is_safety = "safety" in str(e).lower()
                _emit(
                    dict(
                        id=rid,
                        source_id=sid,
                        axis=spec["axis"],
                        control=spec["control"],
                        dose=spec.get("dose"),
                        strength=spec.get("strength"),
                        seed=spec.get("seed"),
                        claim_kind=spec["claim_kind"],
                        claimed_owner=spec["claimed_owner"],
                        outcome="safety_blocked" if is_safety else "failed",
                        error=str(e),
                    )
                )
            except Exception as e:
                _emit(
                    dict(
                        id=rid,
                        source_id=sid,
                        axis=spec["axis"],
                        control=spec["control"],
                        dose=spec.get("dose"),
                        strength=spec.get("strength"),
                        seed=spec.get("seed"),
                        claim_kind=spec["claim_kind"],
                        claimed_owner=spec["claimed_owner"],
                        outcome="failed",
                        error=str(e),
                    )
                )

    # T4
    if t4_pairs:
        _ensure_models()
        reader = _state["reader"]

        for pr in t4_pairs:
            donor = pr["donor"]
            recipient = pr["recipient"]
            pid = pr["id"]
            for scale in T4_SCALES:
                for arm in ("donor_C1", "donor_C0_sham"):
                    for claimed_role in ("donor_claim", "recipient_claim"):
                        rid = f"{pid}:t4:{scale}:{arm}:{claimed_role}"
                        if resume and rid in read_journal(output_dir):
                            continue
                        donor_c1_p = saved_marked.get(donor)
                        donor_c0_p = saved_source.get(donor)
                        recipient_p = saved_source.get(recipient)
                        if donor_c1_p is None or donor_c0_p is None or recipient_p is None or not donor_c1_p.exists() or not donor_c0_p.exists() or not recipient_p.exists():
                            _emit(
                                dict(
                                    id=rid,
                                    t4_pair_id=pid,
                                    axis="T4",
                                    scale=scale,
                                    arm=arm,
                                    claimed_role=claimed_role,
                                    outcome="missing_dependency",
                                    error=f"donor/recipient not in shard or not saved: {donor} -> {recipient}",
                                )
                            )
                            continue
                        try:
                            donor_c1 = np.asarray(Image.open(donor_c1_p).convert("RGB"), np.uint8)
                            donor_c0 = np.asarray(Image.open(donor_c0_p).convert("RGB"), np.uint8)
                            recipient_rgb = np.asarray(Image.open(recipient_p).convert("RGB"), np.uint8)
                            if arm == "donor_C1":
                                transferred = residual_transfer_rgb(recipient_rgb, donor_c1, donor_c0, scale)
                            else:
                                transferred = recipient_rgb.copy()
                            donor_owner = next((s["owner"] for s in sources if s["id"] == donor), donor)
                            recipient_owner = next((s["owner"] for s in sources if s["id"] == recipient), recipient)
                            claimed = donor_owner if claimed_role == "donor_claim" else recipient_owner
                            z = reader.latent(transferred)
                            feat_tr = _clip_feature(transferred, sem_views)
                            det = f5.detect_rgb(transferred, z, claimed, profile, feat_tr, binding=binding, band=embed_kwargs["band"], whitening=embed_kwargs["whitening"])
                            tpath = _image_path(images_dir, rid)
                            Image.fromarray(transferred).save(tpath)
                            transferred = np.asarray(Image.open(tpath).convert("RGB"), np.uint8)
                            _emit(
                                dict(
                                    id=rid,
                                    t4_pair_id=pid,
                                    axis="T4",
                                    scale=scale,
                                    arm=arm,
                                    claimed_role=claimed_role,
                                    claimed_owner=claimed,
                                    outcome="completed",
                                    detection=det,
                                    image=_receipt_for_rgb(transferred, tpath),
                                )
                            )
                        except Exception as e:
                            _emit(dict(id=rid, t4_pair_id=pid, axis="T4", scale=scale, arm=arm, claimed_role=claimed_role, outcome="failed", error=str(e)))

    # T5
    if t5_pairs:
        _ensure_models()
        reader = _state["reader"]
        for pr in t5_pairs:
            pid = pr["id"]
            a_id = pr.get("a") or pr.get("donor")
            b_id = pr.get("b") or pr.get("recipient")
            if a_id is None or b_id is None:
                continue
            a_owner = next((s["owner"] for s in sources if s["id"] == a_id), None)
            b_owner = next((s["owner"] for s in sources if s["id"] == b_id), None)
            if a_owner is None or b_owner is None:
                continue
            for endpoint, other_owner in [("a", b_owner), ("b", a_owner)]:
                for arm in ("C0", "C1"):
                    rid = f"{pid}:t5:{endpoint}:{arm}:cross_owner"
                    if resume and rid in read_journal(output_dir):
                        continue
                    sid2 = a_id if endpoint == "a" else b_id
                    img_path = saved_source.get(sid2) if arm == "C0" else saved_marked.get(sid2)
                    if img_path is None or not img_path.exists():
                        _emit(dict(id=rid, t5_pair_id=pid, axis="T5", endpoint=endpoint, arm=arm, outcome="missing_dependency", error=f"source not in shard: {sid2}"))
                        continue
                    try:
                        rgb = np.asarray(Image.open(img_path).convert("RGB"), np.uint8)
                        z = reader.latent(rgb)
                        feat_sus = _clip_feature(rgb, sem_views)
                        det = f5.detect_rgb(rgb, z, other_owner, profile, feat_sus, binding=binding, band=embed_kwargs["band"], whitening=embed_kwargs["whitening"])
                        _emit(dict(id=rid, t5_pair_id=pid, axis="T5", endpoint=endpoint, arm=arm, claimed_owner=other_owner, outcome="completed", detection=det))
                    except Exception as e:
                        _emit(dict(id=rid, t5_pair_id=pid, axis="T5", endpoint=endpoint, arm=arm, outcome="failed", error=str(e)))

    # Endpoints + run.json
    journal = read_journal(output_dir)
    cells = summarize_cells(planned, journal, strengths)
    status = inventory_status(planned, journal)

    run = dict(
        schema=RUN_SCHEMA,
        version=VERSION,
        manifest_path=str(manifest_path),
        manifest_sha256=_sha_file(manifest_path),
        config_path=str(ROOT / manifest["config_path"]),
        config_sha256=_sha_file(ROOT / manifest["config_path"]),
        profile_path=str(profile_path),
        profile_sha256=_sha_file(profile_path),
        detector_config_id=config_id,
        family=cfg.get("family"),
        revision=cfg.get("revision"),
        commit=commit,
        dirty=bool(dirty),
        data_split=manifest["data_split"],
        shard_index=shard_index,
        shard_count=shard_count,
        sources_in_shard=[s["id"] for s in shard],
        t3_strengths=list(strengths),
        t3_seeds=list(seeds),
        t4_pairs=t4_pairs,
        t5_pairs=t5_pairs,
        journal_rows=len(journal),
        **status,
        cells=cells,
        duration_seconds=time.monotonic() - started,
    )
    _atomic_json(output_dir / "run.json", run)
    return output_dir


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True, help="Path to manifest JSON (schema m1b-f5-manifest-v1)")
    p.add_argument("--output-dir", type=Path, required=True, help="Output directory (fresh; journal lives here)")
    p.add_argument("--shard-index", type=int, default=0, help="Shard index (0-based)")
    p.add_argument("--shard-count", type=int, default=1, help="Total shards")
    p.add_argument("--resume", action="store_true", help="Resume: skip row ids already in journal")
    p.add_argument("--no-resume", dest="resume", action="store_false", help="Do not resume")
    p.set_defaults(resume=True)
    a = p.parse_args()
    run_manifest(a.manifest, a.output_dir, a.shard_index, a.shard_count, resume=a.resume)
    result = json.loads((a.output_dir / "run.json").read_text(encoding="utf-8"))
    print(json.dumps(dict(out=str(a.output_dir), shard=f"{a.shard_index}/{a.shard_count}", resume=a.resume, outcome=result["outcome"]), indent=2))
    if result["outcome"] != "completed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()

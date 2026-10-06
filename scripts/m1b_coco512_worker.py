"""M1b COCO512 worker: F5 r2 candidate and v5 r3 comparator under the narrow confirmatory draft.

Implements `research/m1-confirmatory-draft.md` for the frozen F5 r2 candidate
(`configs/f5-r2.json`) and the frozen v5 r3 image-domain comparator on the same
canonical sources:

- clean: canonical source C0, marked C1 per method, correct and wrong-owner claims;
- T3: VAE posterior-mode cycle and SD1.5 DDIM20 img2img .05/.1/.2/.4 x seeds 0-2 on
  the 30-source T3 cohort, each from the saved untouched C0/C1;
- T4: centered 128/256 RGB patch from donor C1 (or donor C0 sham) into recipient
  C0-source, donor and recipient claims, 30 fixed pairs;
- T5: bounded disjoint 30-pair selection from identical noncrowd COCO category
  signatures and source pHash distance >= 8, then cross-owner claims on C0 and C1.

The official runner interface is `--manifest FILE --output-dir DIR`. The execution
manifest lists the plan (`*.m1b-plan.json`) among its inputs. Development plans run
directly; a test plan refuses to start without the user's matching official approval.

Every planned row is declared before work, failures stay adverse, nothing is retried
or substituted. Journal rows are appended per unit; `resume_from` continues a stopped
run of the same scientific plan. Matched C0 reconstruction with the watermark
objective disabled is the identity for both pixel-additive methods, so the
reconstruction cells equal the C0-source cells (checked by hash, declared in run.json).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

VERSION = "m1b-coco512-worker-v1"
PLAN_SCHEMA = "m1b-coco512-plan-v1"
METHODS = ("f5-r2", "v5-r3")
STRENGTHS = (0.05, 0.1, 0.2, 0.4)
SEEDS = (0, 1, 2)
PATCH_SIZES = (128, 256)
DOSES = ("vae",) + tuple(f"ddim-{s}-{sd}" for s in STRENGTHS for sd in SEEDS)
CODE_FILES = ("scripts/m1b_coco512_worker.py", "scripts/f5_latent_codec.py", "scripts/f5_gate.py",
              "scripts/revised_watermark_v5.py", "scripts/m1_confirmatory_image_operations.py",
              "scripts/m1_confirmatory_t5_pairs.py", "scripts/m1_confirmatory_endpoints.py",
              "scripts/m1_canonical_source.py", "scripts/three_threat_models.py", "scripts/three_threat_protocol.py",
              "scripts/a4_protocol_reference.py", "scripts/m1_owner_interface.py")
SCIENCE_FIELDS = ("schema", "data_split", "methods", "f5_config", "profile", "sources", "t3_uids", "t4_pairs",
                  "t5", "strengths", "seeds", "patch_sizes", "assets_root")
QUALITY_TARGETS = dict(psnr_db_gt=35.0, ssim_gt=0.9, lpips_lt=0.1)


# ---------------------------------------------------------------- small helpers

def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def object_digest(value: Any) -> str:
    return sha_bytes(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                                allow_nan=False).encode("utf-8"))


def atomic_json(path: Path, value: Any) -> None:
    import os
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=1, ensure_ascii=False, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def _finite(value: Any) -> Any:
    """JSON-safe copy: nonfinite floats become None (recorded, never silently 'passing')."""
    if isinstance(value, float):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, dict):
        return {str(k): _finite(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_finite(v) for v in value]
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            return _finite(value.item())
        except Exception:
            return str(value)
    return value


def owner_pair(uid: str) -> tuple[str, str]:
    from a4_protocol_reference import owner_and_seed
    owner, wrong, _ = owner_and_seed(uid)
    return owner, wrong


def file_tag(uid: str) -> str:
    return "".join(c if c.isalnum() or c in "-." else "_" for c in uid)


# ---------------------------------------------------------------- plan

def _ref(value: Any, name: str) -> dict:
    if not isinstance(value, dict) or set(value) != {"path", "sha256"} or not isinstance(value["path"], str) \
            or not isinstance(value["sha256"], str) or len(value["sha256"]) != 64:
        raise ValueError(f"{name} must be {{path, sha256}}")
    return value


def resolve(path: str, base: Path = ROOT) -> Path:
    p = Path(path)
    return p if p.is_absolute() else base / p


def load_sources(plan: dict, base: Path = ROOT) -> list[dict]:
    """Source list in plan order: uid, group_id, raw_path, raw_sha256 (+ owners recomputed)."""
    spec = plan["sources"]
    if "index" in spec:
        ref = _ref(spec["index"], "sources.index")
        path = resolve(ref["path"], base)
        if sha_file(path) != ref["sha256"]:
            raise ValueError("source index hash mismatch")
        index = json.loads(path.read_text(encoding="utf-8"))
        rows = [dict(uid=e["source_uid"], group_id=e["group_id"], raw_path=e["external_raw_path"],
                     raw_sha256=e["raw_sha256"], owner=e["owner"], wrong_owner=e["wrong_owner"])
                for e in sorted(index["entries"], key=lambda e: e["schedule_index"])]
    else:
        rows = [dict(r) for r in spec["inline"]]
    seen = set()
    for r in rows:
        if r["uid"] in seen:
            raise ValueError("duplicate source uid " + r["uid"])
        seen.add(r["uid"])
        owner, wrong = owner_pair(r["uid"])
        if r.get("owner", owner) != owner or r.get("wrong_owner", wrong) != wrong:
            raise ValueError("owner schedule mismatch for " + r["uid"])
        r["owner"], r["wrong_owner"] = owner, wrong
        if not isinstance(r.get("raw_sha256"), str) or len(r["raw_sha256"]) != 64:
            raise ValueError("raw_sha256 required for " + r["uid"])
    return rows


def validate_plan(plan: dict, base: Path = ROOT) -> tuple[dict, list[dict]]:
    if not isinstance(plan, dict) or plan.get("schema") != PLAN_SCHEMA:
        raise ValueError("plan schema must be " + PLAN_SCHEMA)
    if plan.get("data_split") not in ("development", "test"):
        raise ValueError("data_split must be development or test")
    if tuple(plan.get("methods", ())) != METHODS:
        raise ValueError(f"methods must be exactly {list(METHODS)}")
    _ref(plan.get("f5_config"), "f5_config")
    _ref(plan.get("profile"), "profile")
    if tuple(plan.get("strengths", ())) != STRENGTHS or tuple(plan.get("seeds", ())) != SEEDS \
            or tuple(plan.get("patch_sizes", ())) != PATCH_SIZES:
        raise ValueError("attack grid must equal the frozen draft grid")
    sources = load_sources(plan, base)
    uids = {s["uid"] for s in sources}
    t3 = plan.get("t3_uids")
    if not isinstance(t3, list) or len(set(t3)) != len(t3) or not set(t3) <= uids:
        raise ValueError("t3_uids must be unique planned sources")
    pairs = plan.get("t4_pairs")
    if not isinstance(pairs, list):
        raise ValueError("t4_pairs must be a list")
    recipients = set()
    for i, p in enumerate(pairs):
        if p.get("pair_index") != i or p.get("donor_uid") not in uids or p.get("recipient_uid") not in uids \
                or p["donor_uid"] == p["recipient_uid"] or p["recipient_uid"] in recipients:
            raise ValueError(f"t4_pairs[{i}] invalid")
        recipients.add(p["recipient_uid"])
    t5 = plan.get("t5")
    if not isinstance(t5, dict) or t5.get("selector") not in ("coco-instances", "fixture-categories"):
        raise ValueError("t5.selector must be coco-instances or fixture-categories")
    if not isinstance(t5.get("max_pairs"), int) or not 1 <= t5["max_pairs"] <= 30:
        raise ValueError("t5.max_pairs must be 1..30")
    if t5["selector"] == "coco-instances":
        _ref(t5.get("annotations"), "t5.annotations")
    elif plan["data_split"] == "test":
        raise ValueError("a test plan must select T5 from the pinned COCO annotations")
    if plan["data_split"] == "test":
        if "index" not in plan["sources"] or len(sources) != 300 or len(t3) != 30 or len(pairs) != 30:
            raise ValueError("test plan requires the frozen 300-source index, 30 T3 sources and 30 T4 pairs")
        if not isinstance(plan.get("approval_path"), str):
            raise ValueError("test plan requires approval_path (the user's official approval record)")
    if plan.get("max_wall_seconds") is not None and (not isinstance(plan["max_wall_seconds"], int)
                                                     or plan["max_wall_seconds"] < 60):
        raise ValueError("max_wall_seconds must be an int >= 60")
    return plan, sources


def science_digest(plan: dict) -> str:
    """Hash of the scientific content of a plan; resumes must match it exactly."""
    return object_digest({k: plan.get(k) for k in SCIENCE_FIELDS})


# ---------------------------------------------------------------- inventory

def source_ids(uid: str) -> list[str]:
    ids = [f"src:{uid}:canon"]
    for m in METHODS:
        ids.append(f"src:{uid}:{m}:embed")
        ids += [f"src:{uid}:{m}:clean:{arm}:{claim}" for arm in ("C0", "C1") for claim in ("correct", "wrong")]
    return ids


def t3_ids(uid: str) -> list[str]:
    ids = []
    for dose in DOSES:
        ids.append(f"atk:{uid}:C0:{dose}")
        ids += [f"t3:{uid}:{m}:C0:{dose}:correct" for m in METHODS]
        for m in METHODS:
            ids.append(f"atk:{uid}:C1-{m}:{dose}")
            ids += [f"t3:{uid}:{m}:C1:{dose}:{claim}" for claim in ("correct", "wrong")]
    return ids


def t4_ids(pair_index: int) -> list[str]:
    ids = []
    for size in PATCH_SIZES:
        ids.append(f"t4img:{pair_index}:{size}:C0")
        ids += [f"t4:{pair_index}:{m}:{size}:sham:{claim}" for m in METHODS for claim in ("donor", "recipient")]
        for m in METHODS:
            ids.append(f"t4img:{pair_index}:{size}:C1-{m}")
            ids += [f"t4:{pair_index}:{m}:{size}:marked:{claim}" for claim in ("donor", "recipient")]
    return ids


def t5_ids(selected: list[dict]) -> list[str]:
    return [f"t5:{k}:{m}:{end}:{arm}" for k in range(len(selected)) for m in METHODS
            for end in ("a", "b") for arm in ("C0", "C1")]


def planned_ids(plan: dict, sources: list[dict], t5_selected: list[dict] | None) -> list[str]:
    ids = []
    for s in sources:
        ids += source_ids(s["uid"])
    for uid in plan["t3_uids"]:
        ids += t3_ids(uid)
    for p in plan["t4_pairs"]:
        ids += t4_ids(p["pair_index"])
    ids.append("t5:selection")
    if t5_selected is not None:
        ids += t5_ids(t5_selected)
    if len(ids) != len(set(ids)):
        raise AssertionError("planned ids collide")
    return ids


# ---------------------------------------------------------------- journal

class Journal:
    def __init__(self, out: Path):
        self.path = out / "outputs" / "journal.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.rows: dict[str, dict] = {}
        self.torn_lines = 0
        if self.path.exists():
            lines = self.path.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    if i != len(lines) - 1:
                        raise ValueError("journal corrupted before its last line")
                    self.torn_lines += 1  # an interrupted final append; that unit runs again
                    continue
                if row["id"] in self.rows:
                    raise ValueError("duplicate journal id " + row["id"])
                self.rows[row["id"]] = row
            if self.torn_lines:
                good = [ln for ln in lines[:-1] if ln.strip()]
                self.path.write_text("".join(ln + "\n" for ln in good), encoding="utf-8")

    def __contains__(self, rid: str) -> bool:
        return rid in self.rows

    def get(self, rid: str) -> dict | None:
        return self.rows.get(rid)

    def ok(self, rid: str) -> bool:
        return self.rows.get(rid, {}).get("outcome") == "completed"

    def emit(self, row: dict) -> dict:
        if row["id"] in self.rows:
            raise ValueError("unit already journaled: " + row["id"])
        line = json.dumps(_finite(row), ensure_ascii=False, allow_nan=False)
        row = json.loads(line)  # in-memory rows equal what a resumed run reads back
        with self.path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(line + "\n")
            f.flush()
        self.rows[row["id"]] = row
        return row


# ---------------------------------------------------------------- endpoint rules

def event(det: dict | None, rule: str) -> bool:
    """Event of one detection under a named rule (same semantics as m1b_f5_runner.success_of)."""
    det = det or {}
    sem, inst = det.get("semantic") or {}, det.get("instance") or {}
    if rule == "both_match":
        return det.get("outcome") == "both_match"
    if rule == "any_found":
        return bool(sem.get("found") or inst.get("found"))
    if rule == "delivered":
        return bool(sem.get("found") or inst.get("found"))
    ok = bool(sem.get("found") and sem.get("content_match"))
    if rule == "semantic":
        return ok
    if rule == "semantic_checked":
        return ok and bool(sem.get("read"))
    if rule == "semantic_assumed":
        return ok and not sem.get("read")
    raise ValueError("unknown rule " + rule)


# ---------------------------------------------------------------- runtime (GPU); tests inject a fake

class Runtime:
    """Real models. Every method takes/returns exact 512x512x3 uint8 arrays."""

    def __init__(self, plan: dict, base: Path = ROOT):
        import numpy as np
        import importlib.metadata as md
        import three_threat_models as ttm
        import revised_watermark_v5 as v5
        import f5_latent_codec as f5
        import m1_confirmatory_image_operations as ops
        from a6_clip_visual import load_visual_encoder
        from f5_gate import semantic_feature

        self.np, self.ttm, self.v5, self.f5, self.ops = np, ttm, v5, f5, ops
        ttm.block_network()
        assets = resolve(plan["assets_root"], base)
        self.asset_receipt, package = ttm.verify_assets(assets, base / "research/a6-candidate-model-assets.json")
        self.cfg = json.loads(resolve(plan["f5_config"]["path"], base).read_text(encoding="utf-8"))
        self.profile = v5.validate_profile(json.loads(resolve(plan["profile"]["path"], base).read_text(encoding="utf-8")))
        self.clip, self.transform = load_visual_encoder(assets / "clip" / "ViT-B-32.pt", device="cpu")
        self.lpips = ttm.load_lpips(assets, package)
        self.pipe = ttm.load_regenerator(assets)
        self.reader = f5.Reader(assets)
        self._feature = lambda rgb, views: semantic_feature(ttm, self.clip, self.transform, rgb, views)
        self.v5c = ops.V5Comparator(self.profile, lambda rgb: self._feature(rgb, 1))
        emb, det = self.cfg["embedding"], self.cfg["detection"]
        self.views = int(det["semantic_views"])
        self.binding = str(det["binding"])
        self.band, self.whitening = tuple(self.cfg["robust_tier"]["band"]), float(self.cfg["robust_tier"]["whitening"])
        self.embed_kwargs = dict(psnr_db=float(emb["psnr_db"]), steps=int(emb["steps"]),
                                 target_margin=float(emb["target_margin"]), mask_power=float(emb["mask_power"]),
                                 band=self.band, whitening=self.whitening, refine_rounds=int(emb["refine_rounds"]),
                                 binding=self.binding)
        import torch
        self.torch = torch
        self.ann_index = None

    # sources
    def canonical(self, source: dict):
        from m1_canonical_source import canonicalize
        raw = Path(source["raw_path"]).read_bytes()
        return canonicalize(raw, source["raw_sha256"])

    def phash(self, rgb) -> int:
        return int(self.v5.perceptual_hash(self.v5.luminance_from_rgb(rgb.tolist()), profile=self.profile))

    def clip_vector(self, rgb, views: int) -> list[float]:
        return self._feature(rgb, views)

    # methods
    def embed(self, method: str, rgb, uid: str, owner: str):
        if method == "f5-r2":
            out, report = self.f5.embed_rgb(rgb, owner, self.profile, self._feature(rgb, self.views), self.reader,
                                            **self.embed_kwargs)
            return self.np.asarray(out, self.np.uint8), report
        result, report = self.v5c.embed(rgb, uid)
        if result.receipt["schedule"]["owner"] != owner:
            raise ValueError("v5 comparator owner differs from plan schedule")
        return result.rgb8, dict(report, receipt=result.receipt)

    def detect(self, method: str, rgb, claim: str) -> dict:
        if method == "f5-r2":
            z = self.reader.latent(rgb)
            return self.f5.detect_rgb(rgb, z, claim, self.profile, self._feature(rgb, self.views),
                                      binding=self.binding, band=self.band, whitening=self.whitening)
        return self.v5c.extract(rgb, claim)

    # operators
    def attack(self, rgb, dose: str):
        pipe = self.pipe
        if dose == "vae":
            res = self.ops.vae_mode(rgb, vae=pipe.vae, processor=pipe.image_processor, safety=pipe.safety_checker,
                                    safety_processor=pipe.feature_extractor, torch_module=self.torch)
        else:
            _, strength, seed = dose.split("-")
            res = self.ops.regeneration(rgb, float(strength), int(seed), pipeline=pipe,
                                        generator_factory=self.torch.Generator,
                                        inference_context=self.torch.inference_mode)
        return res.rgb8, res.receipt

    def patch(self, recipient_c0, donor, size: int, donor_control: str):
        res = self.ops.center_patch(recipient_c0, donor, size, donor_control=donor_control)
        return res.rgb8, res.receipt

    def quality(self, ref, rgb) -> dict:
        from m1_latent_reconstruction import quality
        q = quality(ref, rgb)
        q["lpips"] = self.ttm.lpips_score(self.lpips, ref, rgb)
        return q

    # T5 observations
    def categories(self, uids: list[str], t5: dict, base: Path = ROOT) -> dict[str, Any]:
        if t5["selector"] == "fixture-categories":
            return {u: (tuple(t5["categories"][u]) if u in t5["categories"] else "no_fixture_categories") for u in uids}
        return coco_categories(uids, resolve(t5["annotations"]["path"], base), t5["annotations"]["sha256"])


def _coco_id(uid: str) -> int | None:
    tail = uid.rsplit(":", 1)
    return int(tail[1]) if len(tail) == 2 and tail[1].isdigit() else None


def coco_categories(uids: list[str], path: Path, sha256: str) -> dict[str, Any]:
    """Noncrowd category signature per scheduled COCO uid ('...:val2017:<image id>'); errors are strings."""
    from m1_confirmatory_t5_pairs import category_signature
    raw = Path(path).read_bytes()
    if sha_bytes(raw) != sha256:
        raise ValueError("annotation artifact hash mismatch")
    data = json.loads(raw)
    wanted = {i: u for u, i in ((u, _coco_id(u)) for u in uids) if i is not None}
    per = {i: [] for i in wanted}
    known = {img["id"] for img in data["images"] if img["id"] in wanted}
    for ann in data["annotations"]:
        if ann["image_id"] in per:
            per[ann["image_id"]].append(dict(iscrowd=ann["iscrowd"], category_id=ann["category_id"]))
    out = {}
    for uid in uids:
        image_id = _coco_id(uid)
        if image_id is None:
            out[uid] = "uid_has_no_coco_image_id"
            continue
        out[uid] = category_signature(per[image_id]) if image_id in known else "image_missing_from_annotations"
    return out


# ---------------------------------------------------------------- worker

class Stop(Exception):
    """Cooperative stop: the wall budget was reached between units."""


class Worker:
    def __init__(self, plan: dict, sources: list[dict], out: Path, runtime: Any, *, clock: Callable[[], float] = time.monotonic):
        import numpy as np
        self.np = np
        self.plan, self.sources, self.out, self.rt, self.clock = plan, sources, out, runtime, clock
        self.by_uid = {s["uid"]: s for s in sources}
        self.images = out / "outputs" / "images"
        self.images.mkdir(parents=True, exist_ok=True)
        self.journal = Journal(out)
        self.started = clock()
        self.deadline = None if plan.get("max_wall_seconds") is None else self.started + plan["max_wall_seconds"]

    # -- io
    def _save(self, name: str, rgb) -> dict:
        from PIL import Image
        path = self.images / name
        Image.fromarray(rgb).save(path)
        back = self.np.asarray(Image.open(path).convert("RGB"), self.np.uint8)
        if not self.np.array_equal(back, rgb):
            raise RuntimeError("PNG round trip changed pixels: " + name)
        return dict(path=str(path.relative_to(self.out)).replace("\\", "/"), rgb8_sha256=sha_bytes(rgb.tobytes()))

    def _load(self, receipt: dict):
        from PIL import Image
        rgb = self.np.asarray(Image.open(self.out / receipt["path"]).convert("RGB"), self.np.uint8)
        if sha_bytes(rgb.tobytes()) != receipt["rgb8_sha256"]:
            raise RuntimeError("saved image changed: " + receipt["path"])
        return rgb

    def _tick(self):
        if self.deadline is not None and self.clock() >= self.deadline:
            raise Stop()

    def _unit(self, rid: str, fn: Callable[[], dict], **fields) -> dict | None:
        """Run one unit unless journaled; any exception becomes an adverse failed row."""
        if rid in self.journal:
            return self.journal.get(rid)
        self._tick()
        t0 = time.perf_counter()
        try:
            body = fn()
            outcome = "completed"
        except Stop:
            raise
        except Exception as e:  # noqa: BLE001 - every failure is retained, never retried
            msg = f"{type(e).__name__}: {e}"
            body = dict(error=msg, operation_receipt=getattr(e, "receipt", None))
            outcome = "safety_blocked" if "safety" in msg.lower() else "failed"
        return self.journal.emit(dict(id=rid, outcome=outcome, seconds=time.perf_counter() - t0, **fields, **body))

    def _missing(self, rid: str, reason: str, **fields):
        if rid not in self.journal:
            self.journal.emit(dict(id=rid, outcome="missing_dependency", error=reason, **fields))

    def _image_of(self, rid: str):
        row = self.journal.get(rid)
        if not row or row.get("outcome") != "completed":
            return None
        return self._load(row["image"])

    # -- stages
    def run_sources(self):
        for s in self.sources:
            uid, owner, wrong = s["uid"], s["owner"], s["wrong_owner"]
            tag = file_tag(uid)

            def canon():
                rgb, receipt = self.rt.canonical(s)
                return dict(image=self._save(f"{tag}-C0.png", rgb), canonical_receipt=receipt,
                            source_phash=self.rt.phash(rgb))
            self._unit(f"src:{uid}:canon", canon, stage="source", uid=uid, group_id=s["group_id"])
            c0 = self._image_of(f"src:{uid}:canon")
            for m in METHODS:
                eid = f"src:{uid}:{m}:embed"
                if c0 is None:
                    self._missing(eid, "canonical source unavailable", stage="embed", uid=uid, method=m)
                else:
                    def embed(m=m):
                        rgb, report = self.rt.embed(m, c0, uid, owner)
                        rgb = self.np.asarray(rgb, self.np.uint8)
                        image = self._save(f"{tag}-C1-{m}.png", rgb)
                        return dict(image=image, quality=self.rt.quality(c0, rgb),
                                    report={k: v for k, v in report.items() if k != "verification"},
                                    self_verification=(report.get("verification") or {}).get("outcome"))
                    self._unit(eid, embed, stage="embed", uid=uid, method=m, owner=owner)
                c1 = self._image_of(eid)
                for arm, img in (("C0", c0), ("C1", c1)):
                    for claim, who in (("correct", owner), ("wrong", wrong)):
                        rid = f"src:{uid}:{m}:clean:{arm}:{claim}"
                        if img is None:
                            self._missing(rid, f"{arm} unavailable", stage="clean", uid=uid, method=m, arm=arm, claim=claim)
                            continue
                        self._unit(rid, lambda img=img, m=m, who=who: dict(detection=self.rt.detect(m, img, who)),
                                   stage="clean", uid=uid, method=m, arm=arm, claim=claim, claimed_owner=who)

    def run_t3(self):
        for uid in self.plan["t3_uids"]:
            s = self.by_uid[uid]
            tag = file_tag(uid)
            inputs = {"C0": f"src:{uid}:canon", **{f"C1-{m}": f"src:{uid}:{m}:embed" for m in METHODS}}
            for dose in DOSES:
                for key, dep in inputs.items():
                    aid = f"atk:{uid}:{key}:{dose}"
                    base = self._image_of(dep)
                    if base is None:
                        self._missing(aid, f"input {dep} unavailable", stage="t3_attack", uid=uid, input=key, dose=dose)
                    else:
                        def attack(base=base, key=key, dose=dose):
                            rgb, receipt = self.rt.attack(base, dose)
                            canon = self._image_of(f"src:{uid}:canon")
                            return dict(image=self._save(f"{tag}-{key}-{dose}.png", rgb), operation_receipt=receipt,
                                        quality_vs_input=self.rt.quality(base, rgb),
                                        quality_vs_source=self.rt.quality(canon, rgb))
                        self._unit(aid, attack, stage="t3_attack", uid=uid, input=key, dose=dose)
                    attacked = self._image_of(aid)
                    methods = METHODS if key == "C0" else (key[3:],)
                    claims = (("correct", s["owner"]),) if key == "C0" else (("correct", s["owner"]), ("wrong", s["wrong_owner"]))
                    for m in methods:
                        arm = "C0" if key == "C0" else "C1"
                        for claim, who in claims:
                            rid = f"t3:{uid}:{m}:{arm}:{dose}:{claim}"
                            fields = dict(stage="t3", uid=uid, method=m, arm=arm, dose=dose, claim=claim, claimed_owner=who)
                            if attacked is None:
                                self._missing(rid, f"attack {aid} unavailable", **fields)
                            else:
                                self._unit(rid, lambda a=attacked, m=m, who=who: dict(detection=self.rt.detect(m, a, who)), **fields)

    def run_t4(self):
        for p in self.plan["t4_pairs"]:
            k, donor, recipient = p["pair_index"], self.by_uid[p["donor_uid"]], self.by_uid[p["recipient_uid"]]
            claims = (("donor", donor["owner"]), ("recipient", recipient["owner"]))
            same = donor["owner"] == recipient["owner"]
            rec_c0 = self._image_of(f"src:{recipient['uid']}:canon")
            for size in PATCH_SIZES:
                donors = {"C0": f"src:{donor['uid']}:canon", **{f"C1-{m}": f"src:{donor['uid']}:{m}:embed" for m in METHODS}}
                for key, dep in donors.items():
                    iid = f"t4img:{k}:{size}:{key}"
                    d_img = self._image_of(dep)
                    if rec_c0 is None or d_img is None:
                        self._missing(iid, "donor or recipient unavailable", stage="t4_image", pair_index=k, size=size, donor_input=key)
                    else:
                        def splice(d_img=d_img, key=key, size=size):
                            rgb, receipt = self.rt.patch(rec_c0, d_img, size, "C0" if key == "C0" else "C1")
                            return dict(image=self._save(f"t4-{k:02d}-{size}-{key}.png", rgb), operation_receipt=receipt,
                                        quality_vs_recipient=self.rt.quality(rec_c0, rgb))
                        self._unit(iid, splice, stage="t4_image", pair_index=k, size=size, donor_input=key)
                    spliced = self._image_of(iid)
                    methods = METHODS if key == "C0" else (key[3:],)
                    arm = "sham" if key == "C0" else "marked"
                    for m in methods:
                        for claim, who in claims:
                            rid = f"t4:{k}:{m}:{size}:{arm}:{claim}"
                            fields = dict(stage="t4", pair_index=k, method=m, size=size, arm=arm, claim=claim,
                                          claimed_owner=who, same_public_owner=same)
                            if spliced is None:
                                self._missing(rid, f"splice {iid} unavailable", **fields)
                            else:
                                self._unit(rid, lambda a=spliced, m=m, who=who: dict(detection=self.rt.detect(m, a, who)), **fields)

    def run_t5(self) -> list[dict] | None:
        from m1_confirmatory_t5_pairs import schedule as select_pairs

        def selection():
            uids = [s["uid"] for s in self.sources]
            cats = self.rt.categories(uids, self.plan["t5"])
            observations = []
            for s in self.sources:
                canon = self.journal.get(f"src:{s['uid']}:canon") or {}
                c = cats.get(s["uid"])
                error = None
                if canon.get("outcome") != "completed":
                    error = "canonical_source_unavailable"
                elif isinstance(c, str):
                    error = c
                observations.append(dict(uid=s["uid"], group_id=s["group_id"], error=error,
                                         categories=None if error else list(c),
                                         phash=None if error else int(canon["source_phash"])))
            result = select_pairs(observations, uids, self.plan["t5"]["max_pairs"])
            return dict(selection=result)
        row = self._unit("t5:selection", selection, stage="t5_selection")
        if row.get("outcome") != "completed":
            return None
        selected = row["selection"]["pairs"]
        for k, pair in enumerate(selected):
            a, b = self.by_uid[pair["left"]], self.by_uid[pair["right"]]
            same = a["owner"] == b["owner"]
            for m in METHODS:
                for end, src, other in (("a", a, b), ("b", b, a)):
                    for arm, dep in (("C0", f"src:{src['uid']}:canon"), ("C1", f"src:{src['uid']}:{m}:embed")):
                        rid = f"t5:{k}:{m}:{end}:{arm}"
                        fields = dict(stage="t5", pair=k, left=pair["left"], right=pair["right"], method=m, endpoint=end,
                                      arm=arm, claimed_owner=other["owner"], same_public_owner=same,
                                      phash_distance=pair["phash_distance"])
                        img = self._image_of(dep)
                        if img is None:
                            self._missing(rid, f"{dep} unavailable", **fields)
                        else:
                            self._unit(rid, lambda img=img, m=m, who=other["owner"]: dict(detection=self.rt.detect(m, img, who)), **fields)
        return selected

    def run(self) -> tuple[str, list[dict] | None]:
        try:
            self.run_sources()
            self.run_t3()
            self.run_t4()
            selected = self.run_t5()
            return "finished", selected
        except Stop:
            sel = self.journal.get("t5:selection")
            return "checkpointed", (sel["selection"]["pairs"] if sel and sel.get("outcome") == "completed" else None)


# ---------------------------------------------------------------- analysis (pure)

def analyse(plan: dict, sources: list[dict], rows: dict[str, dict], selected: list[dict] | None) -> dict:
    from m1_confirmatory_endpoints import bounds, cell

    planned = planned_ids(plan, sources, selected)
    det_ok = lambda rid: rows.get(rid, {}).get("outcome") == "completed" and "detection" in rows[rid]

    def obs(rid: str, rule: str):
        return event(rows[rid]["detection"], rule) if det_ok(rid) else None

    def rowcell(ids, rule, kind):
        value = cell(sorted(ids), {i: obs(i, rule) for i in ids}, event_kind=kind)
        value["event_rule"] = rule
        return value

    def cluster(units: dict[str, list[str]], rule: str, kind: str, need: str) -> dict:
        """One observation per independent unit (source or pair) from its repeated rows.

        need='majority' (>= half of the unit's rows), 'all' or 'any'. Missing rows count adversely
        (a miss for positives, an error for negatives)."""
        per = {}
        for unit, ids in units.items():
            vals = [obs(i, rule) for i in ids]
            vals = [(v if v is not None else kind == "negative_error") for v in vals]
            hits = sum(vals)
            per[unit] = (hits * 2 >= len(vals)) if need == "majority" else (all(vals) if need == "all" else any(vals))
        value = cell(sorted(per), per, event_kind=kind)
        value.update(event_rule=rule, unit_rule=need, independent_units=len(per))
        return value

    methods = {}
    uids = [s["uid"] for s in sources]
    for m in METHODS:
        out: dict[str, Any] = {}
        clean = {}
        clean["C1_correct_both_match"] = rowcell([f"src:{u}:{m}:clean:C1:correct" for u in uids], "both_match", "positive_success")
        for arm, claim in (("C0", "correct"), ("C0", "wrong"), ("C1", "wrong")):
            for rule in ("both_match", "any_found"):
                clean[f"{arm}_{claim}_{rule}"] = rowcell([f"src:{u}:{m}:clean:{arm}:{claim}" for u in uids], rule, "negative_error")
        embeds = [rows.get(f"src:{u}:{m}:embed") for u in uids]
        qs = [r["quality"] for r in embeds if r and r.get("outcome") == "completed"]
        def frac(pred):
            return dict(count=sum(1 for q in qs if pred(q)), valid=len(qs), planned=len(uids))
        clean["quality"] = dict(
            psnr_gt_35=frac(lambda q: q["psnr_db"] is not None and q["psnr_db"] > 35.0 or q.get("psnr_infinite")),
            ssim_gt_0_9=frac(lambda q: q["ssim_rgb"] > 0.9), lpips_lt_0_1=frac(lambda q: q["lpips"] < 0.1),
            joint=frac(lambda q: (q["psnr_db"] is None or q["psnr_db"] > 35.0) and q["ssim_rgb"] > 0.9 and q["lpips"] < 0.1),
            psnr_mean=_mean([q["psnr_db"] for q in qs if q["psnr_db"] is not None]),
            ssim_mean=_mean([q["ssim_rgb"] for q in qs]), lpips_mean=_mean([q["lpips"] for q in qs]),
            lpips_max=max([q["lpips"] for q in qs], default=None),
            seconds_mean=_mean([r["seconds"] for r in embeds if r and r.get("outcome") == "completed"]))
        clean["c0_reconstruction"] = "identity for this pixel-additive method: C0-reconstruction cells equal C0-source cells"
        out["clean"] = clean

        t3 = {}
        for dose_group, doses in [("vae", ["vae"])] + [(f"ddim-{s}", [f"ddim-{s}-{sd}" for sd in SEEDS]) for s in STRENGTHS]:
            pos = {u: [f"t3:{u}:{m}:C1:{d}:correct" for d in doses] for u in plan["t3_uids"]}
            neg_w = {u: [f"t3:{u}:{m}:C1:{d}:wrong" for d in doses] for u in plan["t3_uids"]}
            neg_0 = {u: [f"t3:{u}:{m}:C0:{d}:correct" for d in doses] for u in plan["t3_uids"]}
            flat = lambda d: [i for ids in d.values() for i in ids]
            entry = dict(rows={r: rowcell(flat(pos), r, "positive_success")
                               for r in ("semantic", "semantic_checked", "semantic_assumed", "both_match")})
            entry["source_majority_semantic"] = cluster(pos, "semantic", "positive_success", "majority")
            entry["source_majority_semantic_checked"] = cluster(pos, "semantic_checked", "positive_success", "majority")
            entry["wrong_owner_any_found_rows"] = rowcell(flat(neg_w), "any_found", "negative_error")
            entry["wrong_owner_semantic_source_any"] = cluster(neg_w, "semantic", "negative_error", "any")
            entry["C0_any_found_rows"] = rowcell(flat(neg_0), "any_found", "negative_error")
            entry["C0_semantic_source_any"] = cluster(neg_0, "semantic", "negative_error", "any")
            t3[dose_group] = entry
        out["t3"] = t3

        t4 = {}
        pairs = plan["t4_pairs"]
        diff = [p["pair_index"] for p in pairs
                if owner_pair(p["donor_uid"])[0] != owner_pair(p["recipient_uid"])[0]]
        mk = lambda arm, claim, ks: {str(k): [f"t4:{k}:{m}:{s}:{arm}:{claim}" for s in PATCH_SIZES] for k in ks}
        all_k = [p["pair_index"] for p in pairs]
        t4["false_donor_attribution_pair_any"] = cluster(mk("marked", "donor", diff), "both_match", "negative_error", "any")
        t4["false_donor_attribution_rows"] = rowcell([i for ids in mk("marked", "donor", diff).values() for i in ids], "both_match", "negative_error")
        t4["donor_delivery_witness_pair_any"] = cluster(mk("marked", "donor", all_k), "delivered", "positive_success", "any")
        t4["donor_semantic_consistent_rows"] = rowcell([i for ids in mk("marked", "donor", all_k).values() for i in ids], "semantic", "negative_error")
        t4["sham_any_found_rows"] = rowcell([i for c in ("donor", "recipient") for ids in mk("sham", c, all_k).values() for i in ids], "any_found", "negative_error")
        t4["recipient_claim_any_found_rows"] = rowcell([i for ids in mk("marked", "recipient", all_k).values() for i in ids], "any_found", "negative_error")
        t4["different_owner_pairs"] = len(diff)
        t4["same_owner_pairs"] = len(all_k) - len(diff)
        by_state = {}
        for k in all_k:
            for s in PATCH_SIZES:
                r = rows.get(f"t4:{k}:{m}:{s}:marked:donor")
                st = (r or {}).get("detection", {}).get("outcome") if r and r.get("outcome") == "completed" else (r or {}).get("outcome", "absent")
                by_state[st] = by_state.get(st, 0) + 1
        t4["marked_donor_claim_states"] = by_state
        out["t4"] = t4

        t5 = dict(selected_pairs=None if selected is None else len(selected))
        if selected is not None:
            diff5 = [k for k, p in enumerate(selected) if owner_pair(p["left"])[0] != owner_pair(p["right"])[0]]
            for arm in ("C0", "C1"):
                units = {str(k): [f"t5:{k}:{m}:{e}:{arm}" for e in ("a", "b")] for k in diff5}
                t5[f"{arm}_false_full_match_pair_any"] = cluster(units, "both_match", "negative_error", "any") if units else None
                t5[f"{arm}_any_found_pair_any"] = cluster(units, "any_found", "negative_error", "any") if units else None
            t5["different_owner_pairs"] = len(diff5)
        out["t5"] = t5
        methods[m] = out

    # paired source-level comparison F5 vs v5 at each regeneration dose (descriptive)
    paired = {}
    for s in STRENGTHS:
        doses = [f"ddim-{s}-{sd}" for sd in SEEDS]
        a_only = b_only = both = neither = 0
        for u in plan["t3_uids"]:
            maj = []
            for m in METHODS:
                vals = [obs(f"t3:{u}:{m}:C1:{d}:correct", "semantic") for d in doses]
                maj.append(sum(bool(v) for v in vals) * 2 >= len(vals))
            both += maj[0] and maj[1]; neither += not maj[0] and not maj[1]
            a_only += maj[0] and not maj[1]; b_only += maj[1] and not maj[0]
        paired[f"ddim-{s}"] = dict(f5_only=a_only, v5_only=b_only, both=both, neither=neither,
                                   exact_sign_test_p_two_sided=_sign_test(a_only, b_only))
    inv = inventory(planned, rows)
    return dict(inventory=inv, methods=methods, paired_t3_source_majority=paired,
                caveat="T3/T4/T5 are descriptive with 30 independent units; repeats are clustered. Per-cell bounds have no simultaneous coverage. No human visual or semantic verdict.")


def _mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def _sign_test(a: int, b: int) -> float | None:
    n = a + b
    if n == 0:
        return None
    k = min(a, b)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def inventory(planned: list[str], rows: dict[str, dict]) -> dict:
    counts: dict[str, int] = {}
    for rid in planned:
        state = rows.get(rid, {}).get("outcome", "not_attempted")
        counts[state] = counts.get(state, 0) + 1
    extra = sorted(set(rows) - set(planned))
    return dict(planned=len(planned), states=counts, extra_rows=extra,
                complete=counts.get("not_attempted", 0) == 0 and not extra)


# ---------------------------------------------------------------- entry

def _git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def check_approval(plan: dict, manifest: dict) -> dict:
    """Fail closed unless the user's official approval matches this exact execution manifest."""
    runtime = Path(plan.get("official_runtime", "C:/Users/Soroush/.codex/skills/thesis-compute-runner/scripts/_runtime"))
    sys.path.insert(0, str(runtime))
    from thesis_agents.compute import approval_check  # type: ignore
    approval = json.loads(Path(plan["approval_path"]).read_text(encoding="utf-8"))
    approval_check(approval, manifest)
    return dict(approval_sha256=object_digest(approval), actor=approval["actor"], source_ref=approval["source_ref"],
                expires_at=approval["expires_at"])


def find_plan(manifest: dict) -> tuple[Path, dict]:
    hits = [i for i in manifest.get("inputs", []) if i["path"].endswith(".m1b-plan.json")]
    if len(hits) != 1:
        raise ValueError("execution manifest must list exactly one *.m1b-plan.json input")
    path = resolve(hits[0]["path"])
    if sha_file(path) != hits[0]["sha256"]:
        raise ValueError("plan hash differs from the execution manifest")
    return path, json.loads(path.read_text(encoding="utf-8"))


def main(argv=None, runtime_factory=Runtime) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    manifest = json.loads(a.manifest.read_text(encoding="utf-8"))
    plan_path, plan = find_plan(manifest)
    plan, sources = validate_plan(plan)
    for key in ("f5_config", "profile"):
        if sha_file(resolve(plan[key]["path"])) != plan[key]["sha256"]:
            raise ValueError(key + " hash mismatch")
    out = a.output_dir
    out.mkdir(parents=True, exist_ok=True)
    approval = None
    if plan["data_split"] == "test":
        approval = check_approval(plan, manifest)
    dirty = _git("status", "--porcelain", "--", *CODE_FILES)
    if dirty:
        raise SystemExit("commit the worker and frozen code before running:\n" + dirty)
    code = {f: sha_file(ROOT / f) for f in CODE_FILES}
    commit = _git("rev-parse", "HEAD")
    context = dict(version=VERSION, science_digest=science_digest(plan), code_sha256=code, data_split=plan["data_split"])
    ctx_path = out / "outputs" / "run-context.json"
    if plan.get("resume_from"):
        prev = resolve(plan["resume_from"])
        prev_ctx = json.loads((prev / "outputs" / "run-context.json").read_text(encoding="utf-8"))
        if prev_ctx != context:
            raise ValueError("resume_from belongs to a different scientific plan or code; start a fresh run")
        if not (out / "outputs" / "journal.jsonl").exists():
            shutil.copytree(prev / "outputs", out / "outputs", dirs_exist_ok=True)
    if ctx_path.exists() and json.loads(ctx_path.read_text(encoding="utf-8")) != context:
        raise ValueError("output directory belongs to a different plan or code")
    atomic_json(ctx_path, context)

    t0 = time.monotonic()
    rt = runtime_factory(plan)
    load_seconds = time.monotonic() - t0
    worker = Worker(plan, sources, out, rt)
    status, selected = worker.run()
    rows = worker.journal.rows
    result = analyse(plan, sources, rows, selected)
    run = dict(schema="m1b-coco512-run-v1", version=VERSION, status=status, plan_path=str(plan_path),
               plan_sha256=sha_file(plan_path), science_digest=context["science_digest"], data_split=plan["data_split"],
               commit=commit, code_sha256=code, approval=approval,
               asset_receipt_sha256=object_digest(getattr(rt, "asset_receipt", None)),
               started_utc=datetime.now(timezone.utc).isoformat(), model_load_seconds=load_seconds,
               wall_seconds=time.monotonic() - t0, torn_journal_lines_dropped=worker.journal.torn_lines,
               t5_selection=None if selected is None else dict(pairs=selected), **result)
    atomic_json(out / "outputs" / "run.json", _finite(run))
    atomic_json(out / "metrics" / "endpoints.json", _finite(dict(methods=result["methods"], inventory=result["inventory"],
                                                                 paired_t3_source_majority=result["paired_t3_source_majority"])))
    print(json.dumps(dict(status=status, inventory=result["inventory"]), indent=1))
    if status == "checkpointed":
        return 3
    return 0 if result["inventory"]["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

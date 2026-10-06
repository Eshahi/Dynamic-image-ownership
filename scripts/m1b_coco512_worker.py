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

Official runner interface: `--manifest FILE --output-dir DIR`; the execution manifest lists
the plan (`*.m1b-plan.json`) among its inputs. Splits:
- `test`: the frozen held-out cohort; needs the user's approval (a delegated approval only for
  an infrastructure rerun) and an exact binding to the approved manifest, commit and inputs;
- `rehearsal`: synthetic data through the same path, with a rehearsal approval;
- `development`: development data, run directly.
Non-test plans are refused if they touch the held-out index, raw root or annotations.

Every planned row is declared before work. Scientific failures stay as adverse rows;
infrastructure faults (CUDA, memory, I/O, program defects, three consecutive failures) stop
the run without a row, leaving a resumable journal. Nothing is retried or substituted.
Endpoints are written only for a finished run (`m1b_coco512_analysis`).
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import math
import os
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

VERSION = "m1b-coco512-worker-v2"
PLAN_SCHEMA = "m1b-coco512-plan-v1"
SPLITS = ("development", "rehearsal", "test")
METHODS = ("f5-r2", "v5-r3")
STRENGTHS = (0.05, 0.1, 0.2, 0.4)
SEEDS = (0, 1, 2)
PATCH_SIZES = (128, 256)
DOSES = ("vae",) + tuple(f"ddim-{s}-{sd}" for s in STRENGTHS for sd in SEEDS)
ENTRY = "scripts/m1b_coco512_worker.py"
SCIENCE_FIELDS = ("schema", "data_split", "methods", "f5_config", "profile", "sources", "t3_uids", "t4_pairs",
                  "t5", "strengths", "seeds", "patch_sizes", "assets_root", "schedule")
OPERATIONAL_FIELDS = ("label", "max_wall_seconds", "resume_from", "resume_parent_approval_sha256", "approval_path",
                      "fault_injection")
ASSET_LOCK = "research/a6-candidate-model-assets.json"

# Frozen held-out identities (metadata only; nothing here opens held-out content).
HELD_OUT_INDEX = "research/m1-confirmatory-external-index.json"
HELD_OUT_INDEX_SHA256 = "8521b783324b62c9394081f0f7f0d8e5162b6592b9bf3256dddf0d400e28b88a"
HELD_OUT_SCHEDULE = "research/m1-confirmatory-schedule-draft.json"
HELD_OUT_SCHEDULE_SHA256 = "83c023bc3e0acb2a38142e8ef6e6a27f9216b7dacb5d885ab778b8799469f35d"
HELD_OUT_ANNOTATION_SHA256 = "e8c7f7908f1d7278341fae127d0da654f102f11bd7b21d8aeefa635b8c810b6f"
HELD_OUT_RAW_ROOT = "W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw"
OFFICIAL_RUNTIME = "C:/Users/Soroush/.codex/skills/thesis-compute-runner/scripts/_runtime"
OFFICIAL_COMPUTE_SHA256 = "4b98e5429d57bda48dbe7b239602b1c7ef60c7cbb19058e17136b29a09437d30"
MAX_RESUME_DEPTH = 2
MAX_CONSECUTIVE_FAILURES = 3
INFRA_MARKERS = ("cuda", "cudnn", "cublas", "out of memory", "device-side", "nvml", "driver", "no space left")


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


def fsync_write(path: Path, data: bytes) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fsync_write(path, (json.dumps(value, indent=1, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8"))


def finite(value: Any) -> Any:
    """JSON-safe copy: nonfinite floats become None (which every endpoint predicate treats as failing)."""
    if isinstance(value, float):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, dict):
        return {str(k): finite(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite(v) for v in value]
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            return finite(value.item())
        except Exception:
            return str(value)
    return value


def owner_pair(uid: str) -> tuple[str, str]:
    from a4_protocol_reference import owner_and_seed
    owner, wrong, _ = owner_and_seed(uid)
    return owner, wrong


def file_tag(uid: str) -> str:
    return "".join(c if c.isalnum() or c in "-." else "_" for c in uid)


def resolve(path: str, base: Path = ROOT) -> Path:
    p = Path(path)
    return p if p.is_absolute() else base / p


def under(path: str | Path, root: str | Path) -> bool:
    a = os.path.normcase(os.path.abspath(str(path)))
    b = os.path.normcase(os.path.abspath(str(root)))
    return a == b or a.startswith(b.rstrip("\\/") + os.sep)


# ---------------------------------------------------------------- scientific core

def code_closure(entry: str = ENTRY, read: Callable[[str], str | None] | None = None) -> list[str]:
    """Every `scripts/*.py` the entry imports, transitively (static AST scan at any nesting depth)."""
    read = read or (lambda p: (ROOT / p).read_text(encoding="utf-8") if (ROOT / p).is_file() else None)
    seen, todo = set(), [entry]
    while todo:
        rel = todo.pop()
        if rel in seen:
            continue
        text = read(rel)
        if text is None:
            continue
        seen.add(rel)
        for node in ast.walk(ast.parse(text)):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module] + [f"{node.module}.{a.name}" for a in node.names]
            for name in names:
                parts = name.split(".")
                if parts[0] == "scripts":
                    parts = parts[1:]
                if parts:
                    cand = f"scripts/{parts[0]}.py"
                    if cand not in seen and read(cand) is not None:
                        todo.append(cand)
    return sorted(seen)


def data_files(plan: dict) -> list[str]:
    files = [ASSET_LOCK, plan["f5_config"]["path"], plan["profile"]["path"]]
    if "index" in plan["sources"]:
        files.append(plan["sources"]["index"]["path"])
    if plan.get("schedule"):
        files.append(plan["schedule"]["path"])
    return sorted(set(files))


def science_digest(plan: dict) -> str:
    """Hash of the scientific fields of a plan (operational fields excluded)."""
    return object_digest({k: plan.get(k) for k in SCIENCE_FIELDS})


def scientific_core(plan: dict, read_bytes: Callable[[str], bytes | None] | None = None) -> dict:
    """Science digest + hashes of the whole import closure and the data files the run reads."""
    def default(p):
        f = ROOT / p
        return f.read_bytes() if f.is_file() else None
    read_bytes = read_bytes or default
    text = lambda p: (lambda b: None if b is None else b.decode("utf-8"))(read_bytes(p))
    code = {f: sha_bytes(read_bytes(f)) for f in code_closure(read=text)}
    data = {}
    for f in data_files(plan):
        b = read_bytes(f)
        data[f] = None if b is None else sha_bytes(b)
    core = dict(version=VERSION, science_digest=science_digest(plan), code_sha256=code, data_sha256=data)
    core["core_sha256"] = object_digest(core)
    return core


# ---------------------------------------------------------------- plan

def _ref(value: Any, name: str) -> dict:
    if not isinstance(value, dict) or set(value) != {"path", "sha256"} or not isinstance(value["path"], str) \
            or not isinstance(value["sha256"], str) or len(value["sha256"]) != 64:
        raise ValueError(f"{name} must be {{path, sha256}}")
    return value


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
                     raw_sha256=e["raw_sha256"], raw_size_bytes=e.get("raw_size_bytes"),
                     owner=e["owner"], wrong_owner=e["wrong_owner"])
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


def held_out_identities(base: Path = ROOT) -> dict[str, set]:
    entries = json.loads((base / HELD_OUT_INDEX).read_text(encoding="utf-8"))["entries"]
    return dict(uids={e["source_uid"] for e in entries}, groups={e["group_id"] for e in entries},
                raw={e["raw_sha256"] for e in entries})


def validate_plan(plan: dict, base: Path = ROOT) -> tuple[dict, list[dict]]:
    if not isinstance(plan, dict) or plan.get("schema") != PLAN_SCHEMA:
        raise ValueError("plan schema must be " + PLAN_SCHEMA)
    split = plan.get("data_split")
    if split not in SPLITS:
        raise ValueError(f"data_split must be one of {SPLITS}")
    unknown = set(plan) - set(SCIENCE_FIELDS) - set(OPERATIONAL_FIELDS)
    if unknown:
        raise ValueError(f"unknown plan fields {sorted(unknown)}")
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
    if plan.get("max_wall_seconds") is not None and (not isinstance(plan["max_wall_seconds"], int)
                                                     or plan["max_wall_seconds"] < 60):
        raise ValueError("max_wall_seconds must be an int >= 60")
    if plan.get("resume_from") and split != "development" and not isinstance(plan.get("resume_parent_approval_sha256"), str):
        raise ValueError("a resumed test/rehearsal plan names the parent run's approval digest")
    if split in ("test", "rehearsal") and not isinstance(plan.get("approval_path"), str):
        raise ValueError("test and rehearsal plans require approval_path")
    for f in plan.get("fault_injection") or []:
        if set(f) != {"unit", "kind"} or f["kind"] not in ("oserror", "cuda", "scientific"):
            raise ValueError("fault_injection entries are {unit, kind in oserror|cuda|scientific}")

    if split == "test":
        index = plan["sources"].get("index") or {}
        if index.get("path") != HELD_OUT_INDEX or index.get("sha256") != HELD_OUT_INDEX_SHA256:
            raise ValueError("a test plan must use the frozen held-out index")
        sched_ref = _ref(plan.get("schedule"), "schedule")
        if sched_ref["path"] != HELD_OUT_SCHEDULE or sched_ref["sha256"] != HELD_OUT_SCHEDULE_SHA256 \
                or sha_file(resolve(sched_ref["path"], base)) != HELD_OUT_SCHEDULE_SHA256:
            raise ValueError("a test plan must use the frozen schedule")
        sched = json.loads(resolve(sched_ref["path"], base).read_text(encoding="utf-8"))
        if [s["uid"] for s in sources] != [c["source_uid"] for c in sched["clean"]] or t3 != sched["t3_source_uids"] \
                or pairs != sched["t4_pairs"]:
            raise ValueError("test cohort, T3 list or T4 pairs differ from the frozen schedule")
        if t5["selector"] != "coco-instances" or t5["annotations"]["sha256"] != HELD_OUT_ANNOTATION_SHA256 \
                or t5["max_pairs"] != 30:
            raise ValueError("a test plan selects T5 from the pinned COCO annotations, 30 pairs")
        if plan.get("fault_injection"):
            raise ValueError("fault injection is never allowed on held-out data")
    else:
        held = held_out_identities(base)
        if (plan["sources"].get("index") or {}).get("sha256") == HELD_OUT_INDEX_SHA256:
            raise ValueError(f"a {split} plan may not use the held-out index")
        for s in sources:
            if s["uid"] in held["uids"] or s["group_id"] in held["groups"] or s["raw_sha256"] in held["raw"] \
                    or under(s["raw_path"], HELD_OUT_RAW_ROOT):
                raise ValueError(f"a {split} plan may not touch held-out source {s['uid']}")
        if t5["selector"] == "coco-instances" and (t5["annotations"]["sha256"] == HELD_OUT_ANNOTATION_SHA256
                                                   or under(resolve(t5["annotations"]["path"], base), HELD_OUT_RAW_ROOT)):
            raise ValueError(f"a {split} plan may not read the held-out annotations")
    return plan, sources


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
    ids = []
    for k in range(len(selected)):
        ids.append(f"t5desc:{k}")
        ids += [f"t5:{k}:{m}:{end}:{arm}" for m in METHODS for end in ("a", "b") for arm in ("C0", "C1")]
    return ids


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
                fsync_write(self.path, "".join(ln + "\n" for ln in good).encode("utf-8"))

    def __contains__(self, rid: str) -> bool:
        return rid in self.rows

    def get(self, rid: str) -> dict | None:
        return self.rows.get(rid)

    def emit(self, row: dict) -> dict:
        if row["id"] in self.rows:
            raise ValueError("unit already journaled: " + row["id"])
        line = json.dumps(finite(row), ensure_ascii=False, allow_nan=False)
        row = json.loads(line)  # in-memory rows equal what a resumed run reads back
        with self.path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())
        self.rows[row["id"]] = row
        return row


# ---------------------------------------------------------------- failure classes

class Stop(Exception):
    """Cooperative stop: the wall budget was reached between units."""


class InfrastructureStop(Exception):
    """A fault that is not a scientific outcome; the unit gets no row and the run stops resumable."""

    def __init__(self, unit: str, error: str):
        super().__init__(f"{unit}: {error}")
        self.unit, self.error = unit, error


def is_infrastructure(error: BaseException) -> bool:
    chain, e = [], error
    while e is not None and len(chain) < 8:
        chain.append(e)
        e = e.__cause__ or e.__context__
    for e in chain:
        if any(m in str(e).lower() for m in INFRA_MARKERS):
            return True
        if isinstance(e, (OSError, MemoryError, ImportError, NameError, AttributeError, TypeError, KeyError, IndexError)):
            return True
    return False


def is_safety_block(error: BaseException) -> bool:
    msg = str(error)
    return "safety_checker_blocked_output" in msg or "safety checker blocked" in msg


# ---------------------------------------------------------------- runtime (GPU); tests inject a fake

class Runtime:
    """Real models. Every method takes/returns exact 512x512x3 uint8 arrays."""

    def __init__(self, plan: dict, base: Path = ROOT):
        import numpy as np
        import torch
        import three_threat_models as ttm
        import revised_watermark_v5 as v5
        import f5_latent_codec as f5
        import m1_confirmatory_image_operations as ops
        from a6_clip_visual import load_visual_encoder
        from f5_gate import semantic_feature

        if not torch.cuda.is_available():
            raise RuntimeError("CUDA device unavailable")
        self.np, self.ttm, self.v5, self.f5, self.ops, self.torch = np, ttm, v5, f5, ops, torch
        ttm.block_network()
        assets = resolve(plan["assets_root"], base)
        self.asset_receipt, package = ttm.verify_assets(assets, base / ASSET_LOCK)
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

    def resources(self) -> dict:
        t = self.torch
        return dict(cuda_device=t.cuda.get_device_name(0), peak_vram_allocated_mib=t.cuda.max_memory_allocated() / 2**20,
                    peak_vram_reserved_mib=t.cuda.max_memory_reserved() / 2**20)

    def canonical(self, source: dict):
        from m1b_canonical_source import canonicalize
        return canonicalize(Path(source["raw_path"]).read_bytes(), source["raw_sha256"])

    def phash(self, rgb) -> int:
        return int(self.v5.perceptual_hash(self.v5.luminance_from_rgb(rgb.tolist()), profile=self.profile))

    def clip_vector(self, rgb, views: int) -> list[float]:
        return self._feature(rgb, views)

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

    def categories(self, uids: list[str], t5: dict, base: Path = ROOT) -> dict[str, Any]:
        if t5["selector"] == "fixture-categories":
            return {u: (tuple(t5["categories"][u]) if u in t5["categories"] else "no_fixture_categories") for u in uids}
        return coco_categories(uids, resolve(t5["annotations"]["path"], base), t5["annotations"]["sha256"])


def _coco_id(uid: str) -> int | None:
    tail = uid.rsplit(":", 1)
    return int(tail[1]) if len(tail) == 2 and tail[1].isdigit() else None


def coco_categories(uids: list[str], path: Path, sha256: str) -> dict[str, Any]:
    """Noncrowd category signature per scheduled COCO uid ('...:<image id>'); errors are strings."""
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
        self.consecutive_failures = 0
        self.faults = {f["unit"]: f["kind"] for f in plan.get("fault_injection") or []}

    # -- io
    def _save(self, name: str, rgb) -> dict:
        from PIL import Image
        buf = io.BytesIO()
        Image.fromarray(rgb).save(buf, format="PNG")
        path = self.images / name
        fsync_write(path, buf.getvalue())
        back = self.np.asarray(Image.open(path).convert("RGB"), self.np.uint8)
        if not self.np.array_equal(back, rgb):
            raise OSError("PNG round trip changed pixels: " + name)
        return dict(path=str(path.relative_to(self.out)).replace("\\", "/"), rgb8_sha256=sha_bytes(rgb.tobytes()))

    def _load(self, receipt: dict):
        from PIL import Image
        rgb = self.np.asarray(Image.open(self.out / receipt["path"]).convert("RGB"), self.np.uint8)
        if sha_bytes(rgb.tobytes()) != receipt["rgb8_sha256"]:
            raise OSError("saved image changed: " + receipt["path"])  # storage fault, never a scientific outcome
        return rgb

    def _unit(self, rid: str, fn: Callable[[], dict], **fields) -> dict | None:
        """Run one unit unless journaled. Scientific failures become adverse rows; infrastructure stops."""
        if rid in self.journal:
            return self.journal.get(rid)
        if self.deadline is not None and self.clock() >= self.deadline:
            raise Stop()
        t0 = time.perf_counter()
        try:
            kind = self.faults.get(rid)
            if kind == "oserror":
                raise OSError("injected I/O fault")
            if kind == "cuda":
                raise RuntimeError("CUDA error: injected device fault")
            if kind == "scientific":
                raise ValueError("injected scientific failure")
            body, outcome = fn(), "completed"
        except (Stop, InfrastructureStop):
            raise
        except Exception as e:  # noqa: BLE001 - classified below, never retried
            if is_infrastructure(e):
                raise InfrastructureStop(rid, f"{type(e).__name__}: {e}") from e
            body = dict(error=f"{type(e).__name__}: {e}", operation_receipt=getattr(e, "receipt", None))
            outcome = "safety_blocked" if is_safety_block(e) else "failed"
        if outcome == "failed":
            self.consecutive_failures += 1
            if self.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                raise InfrastructureStop(rid, f"{MAX_CONSECUTIVE_FAILURES} consecutive failures; last: {body['error']}")
        elif outcome == "completed":
            self.consecutive_failures = 0
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
            observations, reasons = [], {}
            for s in self.sources:
                canon = self.journal.get(f"src:{s['uid']}:canon") or {}
                c = cats.get(s["uid"])
                error = None
                if isinstance(c, str):
                    error = "annotation:" + c
                elif canon.get("outcome") != "completed":
                    error = "canonical_source_unavailable"
                elif not c:
                    reasons["annotation_valid_empty_signature"] = reasons.get("annotation_valid_empty_signature", 0) + 1
                if error:
                    reasons[error] = reasons.get(error, 0) + 1
                observations.append(dict(uid=s["uid"], group_id=s["group_id"], error=error,
                                         categories=None if error else list(c),
                                         phash=None if error else int(canon["source_phash"])))
            result = select_pairs(observations, uids, self.plan["t5"]["max_pairs"])
            annotation_valid = sum(1 for u in uids if not isinstance(cats.get(u), str))
            return dict(selection=result, observation_counts=dict(planned=len(uids), annotation_valid=annotation_valid,
                                                                  reasons=reasons))
        row = self._unit("t5:selection", selection, stage="t5_selection")
        if row.get("outcome") != "completed":
            return None
        selected = row["selection"]["pairs"]
        for k, pair in enumerate(selected):
            a, b = self.by_uid[pair["left"]], self.by_uid[pair["right"]]
            same = a["owner"] == b["owner"]
            ia, ib = self._image_of(f"src:{a['uid']}:canon"), self._image_of(f"src:{b['uid']}:canon")

            def describe(ia=ia, ib=ib):
                cos = {}
                for views in (1, 7):
                    va, vb = self.rt.clip_vector(ia, views), self.rt.clip_vector(ib, views)
                    cos[f"clip_cosine_views{views}"] = float(sum(x * y for x, y in zip(va, vb)))
                return dict(descriptors=cos)
            self._unit(f"t5desc:{k}", describe, stage="t5_descriptors", pair=k, left=pair["left"], right=pair["right"],
                       phash_distance=pair["phash_distance"])
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

    def run(self) -> tuple[str, list[dict] | None, str | None]:
        try:
            self.run_sources()
            self.run_t3()
            self.run_t4()
            selected = self.run_t5()
            return "finished", selected, None
        except Stop:
            status, error = "checkpointed", None
        except InfrastructureStop as e:
            status, error = "infrastructure_stop", str(e)
        sel = self.journal.get("t5:selection")
        return status, (sel["selection"]["pairs"] if sel and sel.get("outcome") == "completed" else None), error


# ---------------------------------------------------------------- binding, approval, preflight

def _git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def check_approval(plan: dict, manifest: dict) -> dict:
    """Fail closed unless an approval matches this exact execution manifest (official approval_check)."""
    compute = Path(OFFICIAL_RUNTIME) / "thesis_agents" / "compute.py"
    if sha_file(compute) != OFFICIAL_COMPUTE_SHA256:
        raise ValueError("official runner approval code changed")
    if OFFICIAL_RUNTIME not in sys.path:
        sys.path.insert(0, OFFICIAL_RUNTIME)
    from thesis_agents.compute import approval_check  # type: ignore
    approval = json.loads(Path(plan["approval_path"]).read_text(encoding="utf-8"))
    approval_check(approval, manifest)
    delegated = str(approval["actor"]).startswith("delegated:")
    if plan["data_split"] == "test" and delegated and not plan.get("resume_from"):
        raise ValueError("the first held-out run needs the user's own approval, not a delegated one")
    return dict(approval_sha256=object_digest(approval), actor=approval["actor"], source_ref=approval["source_ref"],
                expires_at=approval["expires_at"], delegated=delegated)


def bind_manifest(manifest: dict) -> None:
    """For test/rehearsal: the process must be exactly what the approved manifest names."""
    if _git("rev-parse", "HEAD") != manifest["git_commit"]:
        raise ValueError("HEAD differs from the approved manifest commit")
    if Path(manifest["reviewed_script"]).as_posix() != ENTRY or sha_file(ROOT / ENTRY) != manifest["script_sha256"]:
        raise ValueError("worker differs from the approved script")
    for item in manifest["inputs"]:
        if sha_file(resolve(item["path"])) != item["sha256"]:
            raise ValueError("manifest input changed: " + item["path"])
    if _git("status", "--porcelain"):
        raise ValueError("the checkout must be clean")


def preflight(plan: dict, sources: list[dict], out: Path) -> dict:
    """After approval, before any unit: every raw file and the annotation artifact match their hashes,
    and there is room to write. A failure here aborts without a journal row."""
    bad = []
    for s in sources:
        p = Path(s["raw_path"])
        if not p.is_file():
            bad.append(f"missing {s['uid']}")
        elif s.get("raw_size_bytes") is not None and p.stat().st_size != s["raw_size_bytes"]:
            bad.append(f"size {s['uid']}")
        elif sha_file(p) != s["raw_sha256"]:
            bad.append(f"hash {s['uid']}")
    if plan["t5"]["selector"] == "coco-instances":
        a = resolve(plan["t5"]["annotations"]["path"])
        if not a.is_file() or sha_file(a) != plan["t5"]["annotations"]["sha256"]:
            bad.append("annotation artifact")
    free = shutil.disk_usage(out).free
    need = 4 * 2**30 if plan["data_split"] == "test" else 2**30
    if free < need:
        bad.append(f"free disk {free / 2**30:.1f} GiB < {need / 2**30:.0f} GiB")
    if bad:
        raise SystemExit("preflight failed (no unit started): " + "; ".join(bad[:20]))
    return dict(sources_verified=len(sources), free_disk_gib=free / 2**30)


def find_plan(manifest: dict) -> tuple[Path, dict]:
    hits = [i for i in manifest.get("inputs", []) if i["path"].endswith(".m1b-plan.json")]
    if len(hits) != 1:
        raise ValueError("execution manifest must list exactly one *.m1b-plan.json input")
    path = resolve(hits[0]["path"])
    if sha_file(path) != hits[0]["sha256"]:
        raise ValueError("plan hash differs from the execution manifest")
    return path, json.loads(path.read_text(encoding="utf-8"))


def adopt_parent(plan: dict, out: Path, core: dict) -> dict | None:
    """Continue an interrupted run of the same scientific core: copy its outputs, record lineage."""
    if not plan.get("resume_from"):
        return None
    parent = resolve(plan["resume_from"])
    p_core = json.loads((parent / "outputs" / "run-context.json").read_text(encoding="utf-8"))
    if p_core.get("core_sha256") != core["core_sha256"]:
        raise ValueError("resume_from belongs to a different scientific core; start a fresh run")
    p_lineage = parent / "outputs" / "lineage.json"
    depth = 1 + (json.loads(p_lineage.read_text(encoding="utf-8"))["depth"] if p_lineage.exists() else 0)
    if depth > MAX_RESUME_DEPTH:
        raise ValueError(f"more than {MAX_RESUME_DEPTH} continuations; a new decision is needed")
    record = dict(depth=depth, parent=str(parent))
    if plan["data_split"] != "development":
        m = json.loads((parent / "manifest.json").read_text(encoding="utf-8"))
        if m.get("approval_reference") != plan["resume_parent_approval_sha256"] or m.get("status") == "completed":
            raise ValueError("parent run is not the interrupted run of the named approval")
        record["parent_approval_reference"] = m["approval_reference"]
    pj = parent / "outputs" / "journal.jsonl"
    record.update(parent_journal_sha256=sha_file(pj), parent_journal_lines=len(pj.read_text(encoding="utf-8").splitlines()))
    if not (out / "outputs" / "journal.jsonl").exists():
        if (parent / "outputs" / "images").exists():
            shutil.copytree(parent / "outputs" / "images", out / "outputs" / "images", dirs_exist_ok=True)
        shutil.copyfile(pj, out / "outputs" / "journal.jsonl")
    return record


def main(argv=None, runtime_factory=Runtime) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    started_utc = datetime.now(timezone.utc).isoformat()
    manifest = json.loads(a.manifest.read_text(encoding="utf-8"))
    plan_path, plan = find_plan(manifest)
    plan, sources = validate_plan(plan)
    for key in ("f5_config", "profile"):
        if sha_file(resolve(plan[key]["path"])) != plan[key]["sha256"]:
            raise ValueError(key + " hash mismatch")
    out = a.output_dir
    (out / "outputs").mkdir(parents=True, exist_ok=True)
    approval = None
    if plan["data_split"] in ("test", "rehearsal"):
        bind_manifest(manifest)
        approval = check_approval(plan, manifest)
    core = scientific_core(plan)
    dirty = _git("status", "--porcelain", "--", *core["code_sha256"], *core["data_sha256"])
    if dirty:
        raise SystemExit("commit the worker and frozen code before running:\n" + dirty)
    commit = _git("rev-parse", "HEAD")
    lineage = adopt_parent(plan, out, core)
    ctx_path = out / "outputs" / "run-context.json"
    if ctx_path.exists() and json.loads(ctx_path.read_text(encoding="utf-8")).get("core_sha256") != core["core_sha256"]:
        raise ValueError("output directory belongs to a different scientific core")
    atomic_json(ctx_path, core)
    atomic_json(out / "outputs" / "lineage.json", lineage or dict(depth=0))
    checks = preflight(plan, sources, out)

    # The official runner passes a sanitized environment without USERNAME; torch's inductor cache
    # would then call getpass.getuser() and fail on Windows. Keep its cache inside the run.
    os.environ.setdefault("TORCHINDUCTOR_CACHE_DIR", str(out / "checkpoints" / "torch-inductor-cache"))
    t0 = time.monotonic()
    rt = runtime_factory(plan)
    load_seconds = time.monotonic() - t0
    worker = Worker(plan, sources, out, rt)
    status, selected, error = worker.run()
    rows = worker.journal.rows
    from m1b_coco512_analysis import analyse, inventory
    inv = inventory(planned_ids(plan, sources, selected), rows)
    resources = getattr(rt, "resources", None)
    run = dict(schema="m1b-coco512-run-v2", version=VERSION, status=status, infrastructure_error=error,
               plan_path=str(plan_path), plan_sha256=sha_file(plan_path), core_sha256=core["core_sha256"],
               data_split=plan["data_split"], commit=commit, approval=approval, lineage=lineage, preflight=checks,
               asset_receipt_sha256=object_digest(finite(getattr(rt, "asset_receipt", None))),
               resources=resources() if callable(resources) else None,
               output_bytes=sum(f.stat().st_size for f in (out / "outputs").rglob("*") if f.is_file()),
               started_utc=started_utc, ended_utc=datetime.now(timezone.utc).isoformat(), model_load_seconds=load_seconds,
               wall_seconds=time.monotonic() - t0, torn_journal_lines_dropped=worker.journal.torn_lines, inventory=inv)
    if status == "finished":
        try:
            result = analyse(plan, sources, rows, selected)
            run.update(t5_selection=None if selected is None else dict(pairs=selected), **result)
            atomic_json(out / "metrics" / "endpoints.json", finite(result))
        except Exception as e:  # analysis is re-runnable on the retained journal
            run["analysis_error"] = f"{type(e).__name__}: {e}"
            atomic_json(out / "metrics" / "endpoints.json", dict(status=status, analysis_error=run["analysis_error"]))
    else:
        # No outcome is shown before the run finishes (no optional stopping).
        atomic_json(out / "metrics" / "endpoints.json", dict(status=status, endpoints_withheld=True))
    atomic_json(out / "outputs" / "run.json", finite(run))
    print(json.dumps(dict(status=status, error=error, inventory=inv), indent=1))
    if status == "checkpointed":
        return 3
    if status == "infrastructure_stop":
        return 4
    return 0 if inv["complete"] and "analysis_error" not in run else 2


if __name__ == "__main__":
    raise SystemExit(main())

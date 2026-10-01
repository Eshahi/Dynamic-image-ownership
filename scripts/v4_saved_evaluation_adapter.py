"""Pinned CPU evaluation of immutable saved suspects; no generation entrypoint.

Imports model/numerical libraries only on explicit adapter construction by the
approved worker. Source features are diagnostic references, never detector input.
"""
import gc
import hashlib
import json
import math
from pathlib import Path
import time
from v4_evaluation_journal import file_sha, object_sha
from v4_study_protocol import claims, distance


class SavedEvaluation:
    def __init__(self, parent, rows, asset_root, profile_path, guard):
        import numpy as np
        import torch
        from PIL import Image
        import revised_watermark_v4 as codec
        from a6_clip_visual import load_visual_encoder
        from three_threat_models import verify_assets, load_lpips
        self.np, self.torch, self.Image, self.codec = np, torch, Image, codec
        self.parent, self.rows, self.guard = Path(parent), rows, guard
        self.profile = codec.load_profile(profile_path)
        if self.profile["security"] != "public-derived" or self.profile["semantic_source"] != "external:clip-vit-b32-a6-40d365715913":
            raise ValueError("unchanged external public profile required")
        self.assets, package = verify_assets(asset_root, Path(__file__).resolve().parents[1]/"research/a6-candidate-model-assets.json")
        guard()
        self.model, self.transform = load_visual_encoder(Path(asset_root)/"clip/ViT-B-32.pt", device="cpu")
        guard()
        self.metric = load_lpips(asset_root, package)
        self.codes = {}

    def close(self):
        self.model = self.transform = self.metric = None
        gc.collect()

    def pixels(self, identity):
        row = self.rows[identity]
        image = row["image"]
        path = self.parent / image["path"]
        if not path.resolve().is_relative_to(self.parent.resolve()) or path.is_symlink():
            raise ValueError("parent image path escape")
        self.guard()
        if file_sha(path) != image["sha256"]:
            raise ValueError("parent saved image changed")
        with self.Image.open(path) as handle:
            handle.load()
            if handle.mode != "RGB" or handle.size != (512,512) or handle.format != "PNG":
                raise ValueError("frozen saved RGB8 geometry changed")
            rgb = self.np.asarray(handle, dtype=self.np.uint8).copy()
        if hashlib.sha256(rgb.tobytes()).hexdigest() != image["pixel_sha256"]:
            raise ValueError("parent saved pixel hash changed")
        return rgb

    def image(self, row):
        self.pixels(row["id"])
        return {**row["image"], "parent_run_id":"c4-v4-three-threat-dev-001"}

    def verify_feature(self, row, image, feature):
        vector = feature["values"]
        if (feature.get("dimension") != 512 or feature.get("l2_normalized") is not True or
            feature.get("pixel_sha256") != image["pixel_sha256"] or
            feature.get("checkpoint_sha256") != "40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af" or
            feature.get("feature_sha256") != object_sha(vector)):
            raise ValueError("suspect feature provenance mismatch")
        if len(vector) != 512 or any(type(v) not in (int,float) or not math.isfinite(v) for v in vector):
            raise ValueError("invalid suspect feature")
        if abs(sum(v*v for v in vector)-1) > 1e-4:
            raise ValueError("suspect feature normalization mismatch")

    def feature(self, row, image):
        from three_threat_models import clip_feature
        if row["axis"] == "clean":
            feature = {**row["clip"], "origin":"inherited same saved suspect; exact parent runtime/profile"}
        else:
            before = time.perf_counter()
            vector = clip_feature(self.model, self.transform, self.pixels(row["id"])).reshape(-1).tolist()
            feature = {"values":vector, "dimension":512, "l2_normalized":True,
                       "feature_sha256":object_sha(vector), "pixel_sha256":image["pixel_sha256"],
                       "checkpoint_sha256":"40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af",
                       "elapsed_seconds":time.perf_counter()-before, "origin":"fresh same saved suspect RGB8"}
            if row["axis"] == "T3":
                source = self.rows[f"clean-{row['source_id']}-C0"]
                self.verify_feature(source, source["image"], source["clip"])
                feature["clip_source_cosine"] = sum(a*b for a,b in zip(vector, source["clip"]["values"]))
                feature["clip_retention_threshold"] = .90
        self.verify_feature(row, image, feature)
        return feature

    def claims(self, row):
        return claims(row)

    def verify_call(self, row, image, claim, result, slot):
        owner, mode, roster = claim
        if (result["claimed_owner"], result["binding_mode"], result["result"]["owners_tested"]) != (owner,mode,roster):
            raise ValueError("call owner/mode/roster differs")
        if result["pixel_sha256"] != image["pixel_sha256"] or result["call_id"] != row["id"]+"-"+str(slot):
            raise ValueError("call suspect or identity differs")

    def detect(self, row, image, feature, claim, slot):
        if row["axis"] == "clean":
            result = {**row["detections"][slot], "inherited":True}
        else:
            self.guard()
            owner, mode, roster = claim
            before = time.perf_counter()
            plane = self.codec.luminance_from_rgb(self.pixels(row["id"]).tolist())
            value = self.codec.detect(plane, owner, profile=self.profile, semantic_features=feature["values"],
                                      binding_mode=mode, roster_size=roster)
            result = {"claimed_owner":owner, "binding_mode":mode, "result":value,
                      "elapsed_seconds":time.perf_counter()-before, "inherited":False,
                      "feature_origin":"same saved suspect RGB8", "pixel_sha256":image["pixel_sha256"]}
        result["call_id"] = row["id"]+"-"+str(slot)
        self.verify_call(row, image, claim, result, slot)
        return result

    def code(self, identity, control):
        key = (identity,control)
        if key not in self.codes:
            row = self.rows[f"clean-{identity}-{control}"]
            self.verify_feature(row, row["image"], row["clip"])
            self.codes[key] = (self.codec.semantic_code(row["clip"]["values"], profile=self.profile),
                              self.codec.perceptual_hash(self.codec.luminance_from_rgb(self.pixels(row["id"]).tolist()), profile=self.profile))
        return self.codes[key]

    def components(self, row):
        self.guard()
        result = {}
        for control in ("C0","C1"):
            a,b = self.code(row["left"],control), self.code(row["right"],control)
            result["distances_"+control] = {"semantic":distance(a[0],b[0]), "instance":distance(a[1],b[1])}
        a = self.rows[f"clean-{row['left']}-C0"]["clip"]["values"]
        b = self.rows[f"clean-{row['right']}-C0"]["clip"]["values"]
        result["clip_pair_cosine"] = sum(x*y for x,y in zip(a,b))
        result["semantic_label"] = row["semantic_label"]
        result["diagnostic_not_detector_input"] = True
        return result

    def quality(self, row, image):
        from qim_rgb_pilot import quality
        from three_threat_models import lpips_score
        rgb = self.pixels(row["id"])
        if row["axis"] == "clean":
            refs = {"quality":f"clean-{row['source_id']}-C0"}
        elif row["axis"] == "T3":
            refs = {"quality_source":f"clean-{row['source_id']}-C0",
                    "quality_immediate":f"clean-{row['source_id']}-{row['control']}"}
        else:
            refs = {"quality":f"clean-{row['recipient_id']}-C0"}
        result = {}
        for name, identity in refs.items():
            self.guard()
            reference = self.pixels(identity)
            scores = quality(reference,rgb)
            result[name] = {"psnr":scores["psnr_db"], "identical_pixels":scores["zero_error"],
                            "ssim":scores["ssim_rgb"], "mse_rgb255":scores["mse_rgb255"],
                            "lpips":lpips_score(self.metric,reference,rgb), "reference_row_id":identity,
                            "reference_pixel_sha256":self.rows[identity]["image"]["pixel_sha256"]}
        if row["axis"] == "clean" and row["control"] == "C1":
            a,b = self.code(row["source_id"],"C0"), self.code(row["source_id"],"C1")
            result["same_instance_distances"] = {"semantic":distance(a[0],b[0]), "instance":distance(a[1],b[1])}
        return result

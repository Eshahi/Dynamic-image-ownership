"""Prospective observed leakage grouping and deterministic whole-group allocation.

No scores, outcomes, thresholds or models are accepted by these interfaces.
Coarse fingerprints are a finite screening rule, not proof of independence.
"""
import hashlib
from collections import Counter, defaultdict
from fractions import Fraction


def digest(tag, value):
    return hashlib.sha256(tag.encode("ascii")+b"\0"+value.encode("utf-8")).hexdigest()


class Union:
    def __init__(self, nodes):
        self.parent = {n:n for n in nodes}
    def find(self, n):
        while self.parent[n] != n:
            self.parent[n] = self.parent[self.parent[n]]
            n = self.parent[n]
        return n
    def join(self, a, b):
        a, b = self.find(a), self.find(b)
        self.parent[max(a,b)] = min(a,b)
    def groups(self):
        groups=defaultdict(list)
        for n in sorted(self.parent):
            groups[self.find(n)].append(n)
        return sorted(groups.values())


def near(a,b,hamming=6,color_mae=4,aspect_percent=5):
    if (int(a["leakage_dhash64"],16)^int(b["leakage_dhash64"],16)).bit_count()>hamming:
        return False
    cross1=a["width"]*b["height"]; cross2=b["width"]*a["height"]
    if 100*abs(cross1-cross2)>aspect_percent*max(cross1,cross2):
        return False
    left,right=bytes.fromhex(a["private_color8_rgb_hex"]),bytes.fromhex(b["private_color8_rgb_hex"])
    if len(left)!=192 or len(right)!=192:
        raise ValueError("invalid coarse color fingerprint")
    return sum(abs(x-y) for x,y in zip(left,right))<=color_mae*192


def near_pairs(rows, rule):
    """Exact candidate coverage for radius6 using 4x16-bit blocks and distance1.

    If total Hamming distance <=6, one of four blocks has distance <=1.
    Every accepted near pair is checked for full distance/color/aspect rules.
    """
    if rule["near_dhash64_max_hamming"]!=6:
        raise ValueError("candidate index valid only for declared radius6")
    index=defaultdict(list); observed={}
    for row in sorted(rows,key=lambda r:r["id"]):
        value=int(row["leakage_dhash64"],16); candidates=set()
        for shift in (0,16,32,48):
            block=(value>>shift)&65535
            for key in (block,*(block^(1<<bit) for bit in range(16))):
                candidates.update(index.get((shift,key),()))
        for uid in sorted(candidates):
            if near(row,observed[uid],6,rule["near_color8_mean_absolute_difference_max_rgb8"],
                    rule["near_aspect_relative_difference_max_percent"]):
                yield uid,row["id"]
        for shift in (0,16,32,48):
            index[(shift,(value>>shift)&65535)].append(row["id"])
        observed[row["id"]]=row


def grouped_frame(canonical,metadata,rule):
    rows={r["id"]:dict(r) for r in canonical}
    if len(rows)!=len(canonical):
        raise ValueError("duplicate canonical frame node")
    if not set(metadata)<=set(rows):
        raise ValueError("metadata node absent from canonical frame")
    for uid,item in metadata.items():
        if rows[uid]["raw_sha256"]!=item["raw_sha256"]:
            raise ValueError("metadata canonical raw identity mismatch")
        rows[uid].update({k:item.get(k) for k in
                          ("prompt_group","prompt_seed_group","producer_group","producer_status")})
    union=Union(rows); first={}; edges=Counter()
    for row in sorted(rows.values(),key=lambda r:r["id"]):
        keys=[("raw",row["raw_sha256"])]
        if row["status"]=="canonical_pass":
            keys.append(("canonical",row["canonical_pixel_sha256"]))
        for field in ("prompt_group","prompt_seed_group","producer_group"):
            if row.get(field) is not None:
                keys.append((field,row[field]))
        if row.get("producer_status")=="unknown-or-deleted":
            keys.append(("unknown_producer_quarantine","one-unresolved-cohort"))
        for kind,key in keys:
            if (kind,key) in first:
                union.join(row["id"],first[(kind,key)]); edges[kind]+=1
            else:
                first[(kind,key)]=row["id"]
    for left,right in near_pairs([r for r in rows.values() if r["status"]=="canonical_pass"],rule):
        union.join(left,right); edges["coarse_near_pixels"]+=1
    return [{"group_id":digest("b4-observed-group-v1","\n".join(members)),"members":members}
            for members in union.groups()],dict(sorted(edges.items()))


def allocate(groups, selected, reserved, config):
    """Exact nominal IMAGE quotas; report actual group counts separately."""
    split_names=("development","validation","test")
    budgets={d:{s:config["allocation"][d][s] for s in split_names}
             for d in ("ms-coco","div2k","diffusiondb")}
    left={d:dict(v) for d,v in budgets.items()}
    if len(selected)!=len({r["id"] for r in selected}):
        raise ValueError("duplicate selected identity")
    index={r["id"]:r for r in selected}
    if not reserved<=set(index):
        raise ValueError("development reservation outside selected frame")
    observed_members=[n for g in groups for n in g["members"]]
    if len(observed_members)!=len(set(observed_members)) or not set(index)<=set(observed_members):
        raise ValueError("invalid/incomplete observed components")
    kept=[]
    for group in groups:
        members=sorted(set(group["members"]) & set(index))
        if not members:
            continue
        counts=Counter(index[n]["domain"] for n in members)
        force_dev=bool(set(members)&reserved)
        force_test=any(index[n]["domain"]=="div2k" and index[n]["source_split"]=="valid" for n in members)
        if force_dev and force_test:
            raise ValueError("development reservation linked to fixed holdout; no split generated")
        kept.append({"group_id":group["group_id"],"members":members,"counts":counts,
                     "forced":"development" if force_dev else "test" if force_test else None})
    assigned={}
    def assign(group,split):
        if any(count>left[d][split] for d,count in group["counts"].items()):
            raise ValueError("whole-group image quotas infeasible; no hidden reallocation")
        for d,count in group["counts"].items():
            left[d][split]-=count
        assigned[group["group_id"]]=split
    for group in sorted(kept,key=lambda g:g["group_id"]):
        if group["forced"]:
            assign(group,group["forced"])
    free=sorted([g for g in kept if not g["forced"]],key=lambda g:
                (-len(g["counts"]),-len(g["members"]),digest("b4-split-rank-v1",g["group_id"])))
    for group in free:
        choices=[s for s in split_names if all(n<=left[d][s] for d,n in group["counts"].items())]
        if not choices:
            raise ValueError("deterministic whole-group assignment infeasible; no split generated")
        split=max(choices,key=lambda s:(min(Fraction(left[d][s],budgets[d][s]) for d in group["counts"]),
                                        digest("b4-split-tie-v1",group["group_id"]+":"+s)))
        assign(group,split)
    if any(n for values in left.values() for n in values.values()):
        raise ValueError("image allocation quotas not met")
    result=[]
    for group in kept:
        by_domain=defaultdict(list)
        for uid in group["members"]:
            by_domain[index[uid]["domain"]].append(uid)
        primary={d:min(ids,key=lambda uid:(digest("b4-primary-representative-v1",group["group_id"]+":"+uid),uid))
                 for d,ids in by_domain.items()}
        for uid in group["members"]:
            result.append({**index[uid],"group_id":group["group_id"],
                           "study_split":assigned[group["group_id"]],
                           "primary_group_representative":uid==primary[index[uid]["domain"]]})
    return sorted(result,key=lambda r:r["source_uid"])

"""Stage S server reader. Completed producer outputs may be read during production.

One worker by default. Explicit i/k shards have disjoint journal files; a merge
rejects overlapping IDs. Never infer a negative from an absent/failed producer.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import time

import tifs_stage_s as stage
import tifs_common as common


def partition(uid, worker):
    if not worker:
        return True
    i, k = map(int, worker.split("/"))
    if k < 1 or not 0 <= i < k:
        raise ValueError("worker must be i/k with 0 <= i < k")
    return int(hashlib.sha256(uid.encode()).hexdigest(),16) % k == i


def items(args):
    rows = []
    for name in ("clean", "native", "threats", "secondary"):
        rows.extend(r for r in common.Journal(args.out/(name+".jsonl"),read_only=True).latest.values() if r.get("status")=="ok")
    return sorted(rows,key=lambda r:r["id"])


def shard_path(args, method=None):
    suffix = ("-"+method if method else "") + ("-"+args.worker.replace("/","-of-") if args.worker else "-0-of-1")
    return args.out/(args.stage+suffix+".jsonl")


def snapshot(args, journal, expected):
    unresolved = [uid for uid in expected if journal.latest.get(uid,{}).get("status") != "ok"]
    common.atomic_json(shard_path(args,args.method).with_suffix(".snapshot.json"),
        dict(stage=args.stage,status="incomplete" if unresolved else "snapshot_complete",expected_available=len(expected),
             unresolved=unresolved, producer_may_still_be_active=True))


def detect(args, config, base, specs, budget, rt, torch):
    from encoder_transfer_test import ALPHA, BETA, message, presence
    rows = items(args)
    for method in ([args.method] if args.method else [a for a in config["arms"] if not stage.c0(a)]):
        journal = common.Journal(shard_path(args,method))
        todo = [r for r in rows if (r["arm"]==method or stage.c0(r["arm"])) and partition(r["id"],args.worker)]
        expected = [f"det:{method}:{r['id']}" for r in todo]
        pending = [r for r in todo if not journal.done(f"det:{method}:{r['id']}")]
        if not pending:
            snapshot_args_method = args.method
            args.method = method
            snapshot(args,journal,expected)
            args.method = snapshot_args_method
            continue
        budget.require(stage.estimate(config,"load_reader",300))
        loadtick = time.monotonic()
        internal = method in (*stage.NEW,"f5-r2","v5-r3")
        if method == "vine-b":
            from tifs_vine_b import VineB
            adapter = VineB(args.assets,base)
        else:
            adapter = rt.Internal(args.assets,base) if internal else rt.Wam(args.assets) if method=="wam" else rt.Vine(args.assets)
        stage.model_ready(args, "load_reader", loadtick, torch)
        try:
            for item in pending:
                uid = f"det:{method}:{item['id']}"
                def work():
                    common.validate_output(item,args.out)
                    rgb = rt.load_rgb(item["output"]["path"])
                    payload = item.get("payload") if item["arm"]==method else None
                    if internal:
                        # The old label fallthrough is unsafe: all F6 use EXACT f5-r2 dispatch.
                        dispatch = "v5-r3" if method=="v5-r3" else "f5-r2"
                        features=adapter.features(rgb,7 if dispatch=="f5-r2" else 1)
                        latent=adapter.reader.latent(rgb) if dispatch=="f5-r2" else None
                        calls={}
                        for owner in (ALPHA,BETA):
                            tick=time.monotonic()
                            raw=adapter._detect(rgb,"f5" if dispatch=="f5-r2" else "v5",owner,features,latent)
                            call=dict(status="ok",raw=raw,seconds=time.monotonic()-tick)
                            calls[owner]=call
                            target = payload if owner==ALPHA else None
                            call["endpoints"] = common.predicates(call["raw"],target)
                            call["endpoints"]["D_and_F"] = call["endpoints"]["D"] and call["endpoints"]["F"]
                            call["donor_carrier_Q"] = call["endpoints"]["Q"] if payload is not None else None
                        modes = {}
                        if item["kind"] in ("T4","T5"):
                            modes["combined"] = calls[ALPHA]
                            for mode in config["threats"]["read_modes"]:
                                if mode=="combined": continue
                                raw=adapter._detect(rgb,"f5" if dispatch=="f5-r2" else "v5",ALPHA,features,latent,mode=mode)
                                endpoints=common.predicates(raw,payload)
                                endpoints["D_and_F"] = endpoints["D"] and endpoints["F"]
                                modes[mode]=dict(status="ok",raw=raw,endpoints=endpoints,donor_carrier_Q=endpoints["Q"])
                    elif method == "vine-b":
                        from tifs_vine_b import delivery_diagnostics
                        # One native network pass and suspect-only feature extraction
                        # serve both claimed owners, including unmarked queries.
                        blind=adapter.blind(rgb)
                        features=adapter.features(rgb)
                        calls={}
                        for owner in (ALPHA,BETA):
                            tick=time.monotonic()
                            raw=adapter.read(rgb,owner,blind=blind,features=features)
                            endpoints=common.predicates(raw,payload if owner==ALPHA else None)
                            endpoints["D_and_F"]=endpoints["D"] and endpoints["F"]
                            calls[owner]=dict(status="ok",raw=raw,endpoints=endpoints,
                                seconds=time.monotonic()-tick,donor_carrier_Q=endpoints["Q"] if payload is not None else None,
                                delivery=delivery_diagnostics(blind["raw"]["decoded_message"],raw["carrier_decode"],payload) if owner==ALPHA else None)
                        modes={"combined":calls[ALPHA]} if item["kind"] in ("T4","T5") else {}
                    else:
                        bits=message(item["source"],base["payload_bits"][method],base["message_seed"])
                        own=adapter.detect(rgb,bits)
                        wrong=message(item["source"],base["payload_bits"][method],base["wrong_message_seed"])
                        own["wrong_message_presence"]=presence(own["raw"].get("decoded_message"),wrong)
                        calls={ALPHA:own}; modes={}
                    return dict(calls=calls,modes=modes,dispatch=dispatch if internal else method,
                        input_sha256=item["output"]["sha256"],artifact_required=False,
                        payload_role="evaluator reference only; suspect supplies detector semantics")
                stage.execute_unit(args,config,budget,rt,torch,journal,
                    dict(id=uid,kind="detect",method=method,item=item["id"],arm=item["arm"],source=item["source"],
                         control=item["control"],producer_kind=item["kind"],
                         **{k:item[k] for k in ("cell","family","strength","seed","target","condition","transform") if k in item}),work,"detect_"+method)
        finally:
            adapter=None
            rt.release()
        unresolved=[uid for uid in expected if journal.latest.get(uid,{}).get("status")!="ok"]
        common.atomic_json(shard_path(args,method).with_suffix(".snapshot.json"),dict(status="incomplete" if unresolved else "snapshot_complete",
            expected_available=len(expected),unresolved=unresolved,producer_may_still_be_active=True))


def quality(args,config,base,specs,budget,rt,torch):
    import et_final_phase_a_attacks as attacks
    p,_,_=stage.prepared(args)
    rows=[r for r in items(args) if partition(r["id"],args.worker)]
    journal=common.Journal(shard_path(args))
    budget.require(stage.estimate(config,"load_quality",300))
    loadtick=time.monotonic()
    metric=attacks.Quality(args.assets)
    stage.model_ready(args,"load_quality",loadtick,torch)
    try:
        for item in rows:
            uid="quality:"+item["id"]
            def work():
                common.validate_output(item,args.out)
                rgb=rt.load_rgb(item["output"]["path"])
                ref=item["target"] if item["kind"] in ("T4","T5") else item["source"]
                original=rt.load_rgb(p["sources"][str(ref)]["path"])
                total=metric(original,rgb)
                result=dict(total=total,original=total,recipient=total if item["kind"] in ("T4","T5") else None,
                    reference_source=ref,input_sha256=item["output"]["sha256"],artifact_required=False)
                if item.get("input"):
                    common.validate_output({"status":"ok","output":item["input"]},args.out)
                    result["attack"]=metric(rt.load_rgb(item["input"]["path"]),rgb)
                    result["input"]=result["attack"]
                result["strict_clean_eligible"]=common.strict_quality(total) if item["kind"]=="clean" else None
                if item["kind"] in ("T4","T5"):
                    q=config["threats"]["quality_eligible"]
                    result["recipient_eligible"]=common.quality_eligible(total,q["psnr_db_gt"],q["ssim_rgb_gt"],q["lpips_lt"])
                return result
            stage.execute_unit(args,config,budget,rt,torch,journal,
                dict(id=uid,kind="quality",item=item["id"],arm=item["arm"],source=item["source"],producer_kind=item["kind"]),work,"quality")
    finally:
        metric=None; rt.release()
    snapshot(args,journal,["quality:"+r["id"] for r in rows])


def main():
    parser=stage.parser(("detect","quality"))
    parser.add_argument("--method",choices=(*stage.NEW,"f5-r2","v5-r3","wam","vine-r","vine-b"))
    parser.add_argument("--worker",default="",help="Explicit disjoint i/k shard; default one serial worker")
    parser.add_argument("--threads",type=int,default=12)
    args=parser.parse_args()
    with stage.Invocation(args):
        stage_tick=time.monotonic()
        partition("validate",args.worker)
        torch=stage.environment_guard(); torch.set_num_threads(args.threads)
        try:
            values=stage.start(args)
            print(json.dumps(dict(event="STAGE_START",stage=args.stage,worker=args.worker,memory=stage.telemetry(torch))),flush=True)
            dict(detect=detect,quality=quality)[args.stage](args,*values[:4],values[4],torch)
        except common.ResourceStop as exc:
            common.atomic_json(args.out/("RESOURCE_STOP-reader-"+args.stage+"-"+(args.method or "all")+"-"+args.worker.replace("/","-of-")+".json"),
                dict(status="RESOURCE_STOP",reason=str(exc),stage=args.stage))
            raise SystemExit(3)
        except torch.cuda.OutOfMemoryError:
            common.atomic_json(args.out/("RESOURCE_STOP-reader-"+args.stage+"-"+(args.method or "all")+"-"+args.worker.replace("/","-of-")+".json"),
                dict(status="RESOURCE_STOP",reason="CUDA OOM during reader model load",stage=args.stage,memory=stage.telemetry(torch)))
            raise SystemExit(3)
        paths = [shard_path(args,m) for m in ([args.method] if args.method else [a for a in values[0]["arms"] if not stage.c0(a)])] if args.stage=="detect" else [shard_path(args)]
        incomplete = any(common.load_json(path.with_suffix(".snapshot.json"))["status"] != "snapshot_complete" for path in paths)
        print(json.dumps(dict(event="STAGE_DONE",stage=args.stage,method=args.method,seconds=time.monotonic()-stage_tick,memory=stage.telemetry(torch))),flush=True)
        if incomplete:
            raise SystemExit(4)


if __name__=="__main__":
    main()

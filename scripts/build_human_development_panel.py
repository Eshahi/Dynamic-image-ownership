"""Build the frozen H1 offline annotation packet; never collect or invent ratings.

Uses byte copies only. Run after committing this script. An existing output must
be empty; partial builds are retained and a rerun refuses to overwrite them.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import shutil
import subprocess
import zipfile


REPO = Path(__file__).resolve().parents[1]
MAIN = Path("W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5")
REL = "research/journal-upgrade-20261009"
SOURCES = (30, 72, 73, 89, 127, 165)
ORDER_SEEDS = (2026101301, 2026101302, 2026101303)
SIDE_SEEDS = (2026101311, 2026101312, 2026101313)
ID_SEED = 2026101391
PROTOCOL_SHA256 = "704642f015fb41a45edfcc1726cfd084fac8c40982b815542876b286e8074c51"


def digest(*fields: object) -> str:
    return hashlib.sha256("|".join(map(str, fields)).encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def population(images: Path) -> list[dict]:
    items = []
    for source in SOURCES:
        for arm in ("C", "S"):
            reference = images / f"{source}-{arm}-matched.png"
            items.append(dict(key=f"CTRL|{source}|{arm}", kind="CTRL", source=source,
                              arm=arm, strength=None, seed=None,
                              reference=reference, comparison=reference))
            for strength in ("0.2", "0.4"):
                for seed in (9, 10, 11):
                    items.append(dict(key=f"T3|{source}|{arm}|{strength}|{seed}",
                                      kind="T3", source=source, arm=arm,
                                      strength=strength, seed=seed, reference=reference,
                                      comparison=images / f"{source}-T3-{strength}-{seed}-{arm}.png"))
    return items


def rater_order(items: list[dict], seed: int) -> list[dict]:
    per_source = {
        source: sorted((x for x in items if x["source"] == source),
                       key=lambda x: (digest(seed, "item", x["key"]), x["key"]))
        for source in SOURCES
    }
    ordered = []
    previous = None
    for round_number in range(1, 15):
        sources = sorted(SOURCES, key=lambda source: (
            digest(seed, "round", round_number, source), source))
        if sources[0] == previous:
            sources = sources[1:] + sources[:1]
        ordered.extend(per_source[source][round_number - 1] for source in sources)
        previous = sources[-1]
    return ordered


INSTRUCTIONS = """For adult participants who did not develop this study or inspect its automated results.
Compare visible content. There is no preferred answer. Some pairs may be identical.
Do not infer a hidden code or processing method. If uncertain, choose Cannot judge and explain.

Work independently, without discussion or machine assistance. You may take breaks,
go back, and revise every answer. Six blocks contain 14 pairs each. No answers are
selected for you. A blank answer remains missing; Cannot judge is a recorded answer.
An absent rater remains missing. No automatic exclusions or validity scores are used.

Use the same zoom for both uncropped images. Reference and Comparison may appear
on either side. Local progress is saved in this browser when storage is available.
Export JSON before closing or moving computers; browser storage is not a submission.
Import your own exported JSON to resume in another browser. Export also preserves
unanswered questions. Return the JSON using the human-arranged collection channel.
No network submission or contact is performed by this packet.

Broad content: Does the comparison preserve the reference's main entities, their
relevant actions and the scene? Yes / No / Cannot judge. Lighting, texture and
fine-detail differences alone need not change broad content. Briefly describe
material changes or uncertainty.

Instance: Does it depict the same particular subject or scene instance, rather
than merely the same category? Yes / No / Cannot judge. Do not infer identities
that are not visually distinguishable.

Disruption: How disruptive are the visible changes for ordinary viewing?
None / Minor / Moderate / Major / Cannot judge. Optional short explanation.

Broad preservation does not establish instance identity, ownership, authorization
or overall attack acceptability. Please disclose prior familiarity with these
images or research; this is metadata, not an exclusion rule.
"""


TEMPLATE = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Image comparison panel</title>
<style>
:root{font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:#25323b;background:#f5f6f7;line-height:1.5}
*{box-sizing:border-box}body{margin:0}main{max-width:1240px;margin:auto;padding:24px}
h1{font-size:1.65rem;margin:0}h2{font-size:1.15rem}p{max-width:90ch}
.card{background:white;border:1px solid #dce1e5;border-radius:12px;padding:18px;margin:16px 0}
.muted{color:#56636e}.toolbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
button,select,input,textarea{font:inherit}button,select{padding:9px 14px;border:1px solid #aab5bf;border-radius:7px;background:white;color:inherit}
button{cursor:pointer}button:disabled{opacity:.5;cursor:default}button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{outline:3px solid #1779ac;outline-offset:3px}
.primary{background:#285a73;color:white;border-color:#285a73}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}
figure{margin:0;min-width:0}figcaption{font-weight:650;margin-bottom:8px}.viewport{height:520px;overflow:auto;background:#eef0f2;border:1px solid #d8dfe5;display:flex;align-items:flex-start;justify-content:flex-start}
.viewport img{width:100%;height:100%;object-fit:contain;flex-shrink:0;display:block}
.zoomed .viewport img{height:auto;object-fit:initial}.zoomed .viewport{align-items:flex-start}
fieldset{border:0;border-top:1px solid #e1e6ea;padding:18px 0 0;margin:18px 0}legend{padding:0;font-weight:650}
.choices{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0}label.choice{padding:8px 13px;border:1px solid #ced6dc;border-radius:6px;cursor:pointer}input[type=radio]{margin-right:7px;accent-color:#285a73}
textarea{width:100%;min-height:70px;border:1px solid #b9c4cc;border-radius:6px;padding:10px}progress{width:100%;accent-color:#285a73}
details summary{cursor:pointer;font-weight:600}.status{min-height:24px;color:#285a73}.block{background:#edf4f7;border-left:4px solid #285a73;padding:10px 14px}
@media(max-width:700px){main{padding:12px}.pair{grid-template-columns:1fr}.viewport{height:380px}.card{padding:12px}}
</style>
<main><h1>Image comparison panel</h1><p class="muted">Participant packet __RATER__ · 84 pairs · six blocks of 14</p>
<details class="card" open><summary>Instructions and prior familiarity</summary>
<p>For adult participants who did not develop this study or inspect its automated results.</p>
<p>Compare visible content. There is no preferred answer. Some pairs may be identical. Do not infer a hidden code or processing method. If uncertain, choose Cannot judge and explain.</p>
<p>Work independently, without discussion or machine assistance. Take breaks whenever needed. You may return to any pair and revise all answers. Reference and Comparison may appear on either side. No study images are coached examples.</p>
<p>Blank answers remain missing. Cannot judge is a recorded answer. An absent rater remains missing; no automatic exclusions are applied. Broad preservation does not establish instance identity, ownership, authorization or overall attack acceptability.</p>
<label for="familiarity">Prior familiarity with these images or research (disclosed metadata; not an exclusion rule)</label>
<textarea id="familiarity" placeholder="Describe any prior familiarity, or state none. You may leave this blank."></textarea>
<p>Browser storage saves progress locally when available. Export JSON before closing or moving computers. Your file includes blanks; it is not sent anywhere automatically. Import your own file to resume. <a href="instructions.txt">Full instructions</a> · <a href="credits.html">Image credits</a></p></details>
<div class="toolbar"><button id="export" class="primary">Export responses JSON</button><button id="import">Import saved JSON</button><input id="importFile" type="file" accept=".json,application/json" hidden></div>
<p id="status" class="status" role="status" aria-live="polite"></p>
<div class="card"><div class="toolbar"><strong id="progressText"></strong><label for="jump">Go to pair</label><select id="jump"></select><label for="zoom">Shared zoom</label><select id="zoom"><option value="fit">Fit uncropped</option><option value="100">100% (native pixels)</option><option value="150">150%</option><option value="200">200%</option></select></div><progress id="progress" max="84" value="0"></progress>
<p id="block" class="block"></p><div id="pair" class="pair"><figure><figcaption id="leftLabel"></figcaption><div class="viewport"><img id="left" alt=""></div></figure><figure><figcaption id="rightLabel"></figcaption><div class="viewport"><img id="right" alt=""></div></figure></div>
<div id="questions"></div><div class="toolbar"><button id="back">Back</button><button id="next" class="primary">Next</button><span id="itemLabel" class="muted"></span></div></div>
<p class="muted">Radio choices support standard keyboard navigation: Tab to a question, arrow keys to move, Space to select. Use export for a portable backup.</p></main>
<script>
'use strict';
const DATA=__DATA__;
const QUESTIONS=[
{key:'broad',title:"Broad content (primary): Does the comparison preserve the reference's main entities, their relevant actions and the scene?",hint:'Lighting, texture and fine-detail differences alone need not change broad content. Briefly describe material changes or uncertainty.',options:['Yes','No','Cannot judge'],note:'Broad-content changes or uncertainty'},
{key:'instance',title:'Instance (secondary): Does it depict the same particular subject or scene instance, rather than merely the same category?',hint:'Do not infer identities that are not visually distinguishable.',options:['Yes','No','Cannot judge'],note:'Instance notes (optional)'},
{key:'disruption',title:'Disruption (secondary): How disruptive are the visible changes for ordinary viewing?',hint:'',options:['None','Minor','Moderate','Major','Cannot judge'],note:'Disruption explanation (optional)'}];
const $=id=>document.getElementById(id), STORAGE='image-panel:'+DATA.protocol_sha256+':'+DATA.rater;
const blank=()=>({schema:'human-development-responses-v1',protocol_sha256:DATA.protocol_sha256,rater:DATA.rater,item_ids:DATA.items.map(x=>x.id),prior_familiarity:null,current_index:0,responses:Object.fromEntries(DATA.items.map(x=>[x.id,{broad:null,instance:null,disruption:null,broad_notes:'',instance_notes:'',disruption_notes:''}]))});
let state=blank(), storageFailure=false;
function validate(v){
 if(!v||v.schema!==state.schema||v.protocol_sha256!==DATA.protocol_sha256||v.rater!==DATA.rater||JSON.stringify(v.item_ids)!==JSON.stringify(DATA.items.map(x=>x.id)))throw Error('This file belongs to a different packet, participant, or protocol.');
 if(!v.responses||Object.keys(v.responses).length!==84||!Number.isInteger(v.current_index)||v.current_index<0||v.current_index>=84||!(v.prior_familiarity===null||typeof v.prior_familiarity==='string'))throw Error('Invalid response structure.');
 const clean=blank(); clean.current_index=v.current_index;clean.prior_familiarity=v.prior_familiarity;
 for(const item of DATA.items){const r=v.responses[item.id];if(!r)throw Error('Missing item in import.');for(const q of QUESTIONS){if(!(r[q.key]===null||q.options.includes(r[q.key]))||typeof r[q.key+'_notes']!=='string')throw Error('Invalid answer or notes.');clean.responses[item.id][q.key]=r[q.key];clean.responses[item.id][q.key+'_notes']=r[q.key+'_notes'];}}
 return clean;
}
try{const saved=localStorage.getItem(STORAGE);if(saved)state=validate(JSON.parse(saved));}catch(e){storageFailure=true;$('status').textContent='Saved browser progress could not be loaded. Export JSON to protect your answers. '+e.message;}
function counts(){return Object.fromEntries(QUESTIONS.map(q=>[q.key,{answered:DATA.items.filter(x=>state.responses[x.id][q.key]!==null).length,unrated:DATA.items.filter(x=>state.responses[x.id][q.key]===null).length}]));}
function progress(){const c=counts();$('progress').value=c.broad.answered;$('progressText').textContent=`${c.broad.answered}/84 primary answers · ${c.broad.unrated} unrated`;$('jump').value=state.current_index;}
function save(){try{localStorage.setItem(STORAGE,JSON.stringify(state));}catch(e){storageFailure=true;}if(storageFailure)$('status').textContent='Browser storage is unavailable or unreadable. Export JSON for a portable backup.';progress();}
function zoom(){const z=$('zoom').value;$('pair').classList.toggle('zoomed',z!=='fit');for(const id of ['left','right']){$(id).style.width=z==='fit'?'100%':(DATA.width*Number(z)/100)+'px';}}
function render(){
 const i=state.current_index,item=DATA.items[i],r=state.responses[item.id];
 $('left').src=item.left;$('right').src=item.right;$('left').alt=item.reference_left?'Reference image':'Comparison image';$('right').alt=item.reference_left?'Comparison image':'Reference image';$('leftLabel').textContent=$('left').alt;$('rightLabel').textContent=$('right').alt;
 $('block').textContent=`Block ${Math.floor(i/14)+1} of 6 · Pair ${i%14+1} of 14 in this block.`+(i%14===0&&i>0?' A good point to take a break; your progress can be exported.':'');
 $('itemLabel').textContent=`Pair ${i+1} of 84`;$('back').disabled=i===0;$('next').disabled=i===83;$('questions').replaceChildren();
 for(const q of QUESTIONS){const f=document.createElement('fieldset'),l=document.createElement('legend');l.textContent=q.title;f.append(l);if(q.hint){const p=document.createElement('p');p.className='muted';p.textContent=q.hint;f.append(p);}const choices=document.createElement('div');choices.className='choices';for(const option of q.options){const label=document.createElement('label');label.className='choice';const input=document.createElement('input');input.type='radio';input.name=q.key;input.value=option;input.checked=r[q.key]===option;input.addEventListener('change',()=>{r[q.key]=option;save();});label.append(input,document.createTextNode(option));choices.append(label);}f.append(choices);const clear=document.createElement('button');clear.type='button';clear.textContent='Clear answer';clear.addEventListener('click',()=>{r[q.key]=null;save();render();});f.append(clear);const label=document.createElement('label');label.htmlFor=q.key+'Notes';label.textContent=q.note;const notes=document.createElement('textarea');notes.id=q.key+'Notes';notes.value=r[q.key+'_notes'];notes.addEventListener('input',()=>{r[q.key+'_notes']=notes.value;save();});f.append(label,notes);$('questions').append(f);}
 progress();zoom();
}
for(let i=0;i<84;i++){const o=document.createElement('option');o.value=i;o.textContent=`${i+1} · Block ${Math.floor(i/14)+1}`;$('jump').append(o);}
$('familiarity').value=state.prior_familiarity??'';$('familiarity').addEventListener('input',()=>{state.prior_familiarity=$('familiarity').value||null;save();});
$('back').onclick=()=>{state.current_index--;save();render();};$('next').onclick=()=>{state.current_index++;save();render();};$('jump').onchange=()=>{state.current_index=Number($('jump').value);save();render();};$('zoom').onchange=zoom;
$('export').onclick=()=>{const result={...state,exported_at_utc:new Date().toISOString(),counts:counts()};const url=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`responses-rater${DATA.rater}-${new Date().toISOString().replace(/[:.]/g,'-')}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('status').textContent='Export created. Save the JSON file; all unrated answers remain null.';};
$('import').onclick=()=>$('importFile').click();$('importFile').onchange=async()=>{const file=$('importFile').files[0];if(!file)return;try{const imported=validate(JSON.parse(await file.text()));if(!confirm('Replace local progress with this saved file? Export current progress first if you need a backup.'))return;state=imported;$('familiarity').value=state.prior_familiarity??'';save();render();$('status').textContent='Saved responses imported. All answers remain revisable.';}catch(e){$('status').textContent='Import rejected: '+e.message;}finally{$('importFile').value='';}};
render();
</script></html>'''


def png_size(path: Path) -> tuple[int, int]:
    # Inspect only the PNG header; copying never decodes or changes pixels.
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"Not a PNG with an IHDR header: {path}")
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


def build(args: argparse.Namespace) -> None:
    protocol, receipt = args.protocol.resolve(), args.receipt.resolve()
    protocol_sha, receipt_sha = file_hash(protocol), file_hash(receipt)
    if protocol_sha != PROTOCOL_SHA256:
        raise ValueError("Protocol differs from the frozen 2026-10-13 bytes; refusing build")
    credits = {int(s["source_id"]): s for s in json.loads(receipt.read_text(encoding="utf-8"))["sources"]}
    for source in SOURCES:
        if credits[source]["license"] != "CC BY 2.0" or not credits[source].get("flickr_attribution_hook"):
            raise ValueError(f"Missing supported attribution for source {source}")
    items = population(args.images.resolve())
    paths = {x[field] for x in items for field in ("reference", "comparison")}
    dimensions = {png_size(path) for path in paths}
    if len(dimensions) != 1:
        raise ValueError("All images must have identical uncropped dimensions")
    width, height = dimensions.pop()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    out = args.output.resolve()
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise FileExistsError(f"Output is not empty; refusing overwrite: {out}")
    out.mkdir(parents=True, exist_ok=True)
    manifest = dict(schema="human-development-packet-v1", created_at_utc=datetime.now(timezone.utc).isoformat(),
                    commit=commit, protocol_path=str(protocol), protocol_sha256=protocol_sha,
                    source_receipt_path=str(receipt), source_receipt_sha256=receipt_sha,
                    expected_assignments=252, items_per_rater=84, attacks_per_rater=72,
                    controls_per_rater=12, id_seed=ID_SEED, image_dimensions=[width, height],
                    pixel_policy="Unmodified byte copies of retained PNGs", raters=[], files={})
    for rater, (order_seed, side_seed) in enumerate(zip(ORDER_SEEDS, SIDE_SEEDS), 1):
        folder = out / f"rater{rater}"
        (folder / "assets").mkdir(parents=True)
        public, linkage, attribution = [], [], []
        for position, item in enumerate(rater_order(items, order_seed), 1):
            neutral = "P" + digest(ID_SEED, rater, item["key"])
            reference_left = int(digest(side_seed, item["key"])[:2], 16) % 2 == 0
            copied = {}
            for label in ("reference", "comparison"):
                name = f"assets/{neutral}-{label}.png"
                shutil.copyfile(item[label], folder / name)
                copied[label] = dict(original_path=str(item[label]), original_sha256=file_hash(item[label]),
                                     distributed_path=name, distributed_sha256=file_hash(folder / name))
                if copied[label]["original_sha256"] != copied[label]["distributed_sha256"]:
                    raise RuntimeError("Byte-copy verification failed")
            left, right = ("reference", "comparison") if reference_left else ("comparison", "reference")
            public.append(dict(id=neutral, reference_left=reference_left,
                               left=copied[left]["distributed_path"], right=copied[right]["distributed_path"]))
            linkage.append(dict(position=position, neutral_id=neutral,
                                **{k: item[k] for k in ("key", "kind", "source", "arm", "strength", "seed")},
                                reference_left=reference_left, files=copied))
            credit = credits[item["source"]]
            hook, license_url = html.escape(credit["flickr_attribution_hook"], quote=True), html.escape(credit["license_url"], quote=True)
            attribution.append(f'<li><code>{neutral}</code>: original photograph <a href="{hook}">Flickr attribution link</a>; <a href="{license_url}">CC BY 2.0</a>. Photographer name is not supplied in the retained metadata.</li>')
        data = dict(rater=rater, protocol_sha256=protocol_sha, width=width, height=height, items=public)
        page = TEMPLATE.replace("__RATER__", str(rater)).replace("__DATA__", json.dumps(data, ensure_ascii=True).replace("<", "\\u003c"))
        (folder / "index.html").write_text(page, encoding="utf-8")
        (folder / "instructions.txt").write_text(INSTRUCTIONS, encoding="utf-8")
        (folder / "credits.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Image credits</title><h1>Image credits</h1><p>Images were resized and modified for research. These credits map neutral pair identifiers to the original Flickr attribution link and license. Photographer names are unknown in retained metadata and are not inferred.</p><ol>' + "\n".join(attribution) + '</ol><p><a href="index.html">Return to comparison</a></p></html>', encoding="utf-8")
        archive = out / f"rater{rater}.zip"
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as z:
            for path in sorted(folder.rglob("*")):
                if path.is_file():
                    z.write(path, path.relative_to(folder).as_posix())
        manifest["raters"].append(dict(rater=rater, order_seed=order_seed, side_seed=side_seed,
                                       directory=folder.name, archive=archive.name, linkage=linkage))
    manifest["files"] = {path.relative_to(out).as_posix(): file_hash(path)
                         for path in sorted(out.rglob("*")) if path.is_file()}
    (out / "private-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Built 3 independent packets (252 assignments) in {out}")
    print("Distribute only the individual rater ZIP. Keep private-manifest.json private.")
    print("No human ratings were created or inferred.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, default=MAIN / ".thesis-build/dev-runs/20261013-1741-fresh-symbol-objective/images")
    parser.add_argument("--protocol", type=Path, default=REPO / REL / "human-development-panel-protocol.md")
    parser.add_argument("--receipt", type=Path, default=REPO / REL / "fresh-development-inputs.json")
    parser.add_argument("--output", type=Path, default=MAIN / ".thesis-build/analysis/human-development-panel-20261013")
    build(parser.parse_args())


if __name__ == "__main__":
    main()

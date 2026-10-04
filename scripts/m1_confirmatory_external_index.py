"""Build a contained COCO300 external-input index from existing metadata only.

Never opens, stats, resolves, hashes or decodes paths stored in metadata.
No scientific unlock, source-plan adoption or approval is created.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from m1_confirmatory_schedule import schedule as derive_schedule

VERSION='m1-confirmatory-external-index-v1'
METADATA_ROOT=Path('C:/Users/Soroush/.codex/worktrees/b3-coco-release-audit/THESIS_GUIDE_OFFLINE_v5')
RAW_ROOT='W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/data/raw'
SCHEDULE_SHA='83c023bc3e0acb2a38142e8ef6e6a27f9216b7dacb5d885ab778b8799469f35d'
PINS={
 'scripts/b3_local_data_receipt.py':'d21debb5aaa669912d96f9f3ed96a67ff06668dcf838d4074d4a9c0f84b4a68b',
 'data/b4-admission-20260926/source-manifest.csv':'40bfeca7c589b8352f93535070bc74fca70c6458216ea5422f0dc173f57110c4',
 'data/splits.csv':'60ff11ae5a81698446573c5f7fbd9d3067a5a2619abdf29ac2389931de1e1b9f',
 'configs/splits-admitted-v2.json':'02cab97279eb657dfe52c34a5fa987c375fac40b137b098b646754f7cfeb0bc3',
 'data/intake/20260926-extracted-source-receipt.json':'3fac7726917fcb2ebe41e2c264d12dca73d4d5af23d3ec2e9424dc1741639224',
 'data/datasheet.md':'7a709693e7f964c696408d2259156d40d9db43c8fcc050d9cb066c5480d78a18',
 'research/b3-local-intake-20260926.md':'e3f3d23c5aafa337665852154a9dba5a7828078a4a447e1529fa185dcbac4896',
 'data/user-acquisition-handoff.md':'9c9d9f72226d294268228813fa6930583e277fd1c4a9fcccfcc5de90aeef5e66',
}
HASH=re.compile(r'[0-9a-f]{64}\Z')
SOURCE_FIELDS={'domain','release_id','source_split','source_id','relative_path','raw_sha256','raw_size_bytes','group_id','source_url','license_reference','rights_status','use_limitations'}


def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return digest(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8'))


def safe_relative(value):
    """Lexical only: no Path.resolve/stat/existence check of raw locations."""
    if type(value) is not str or not value or '\\' in value or ':' in value or '\x00' in value:
        raise ValueError('Unsafe raw relative path')
    parts=value.split('/')
    if any(p in ('','.','..') for p in parts) or PurePosixPath(value).is_absolute():raise ValueError('Unsafe raw relative path')
    return value


def uid(row):return ':'.join(row[k] for k in ('domain','release_id','source_split','source_id'))


def annotation_receipt(acquisition):
    """Existing extracted-file receipt is not an archive receipt."""
    annotations=acquisition.get('annotations')
    if not isinstance(annotations,list):raise ValueError('Missing acquisition annotation receipt list')
    found=[a for a in annotations if a.get('name')=='instances_val2017.json']
    if len(found)!=1:raise ValueError('Need exactly one extracted validation-instance receipt')
    row=found[0]
    if type(row.get('sha256')) is not str or not HASH.fullmatch(row['sha256']) or type(row.get('bytes')) is not int or row['bytes']<=0:
        raise ValueError('Malformed extracted annotation receipt')
    # Inspected acquisition explicitly has no original archive. Never infer one.
    if acquisition.get('archive_hashes_available') is not False:raise ValueError('Changed archive receipt schema requires inspection')
    return dict(name=row['name'],sha256=row['sha256'],size_bytes=row['bytes'],
        receipt_kind='extracted-file-only',raw_root=RAW_ROOT,
        raw_relative_path='annotations_trainval2017/annotations/instances_val2017.json',
        external_path=RAW_ROOT+'/annotations_trainval2017/annotations/instances_val2017.json',
        path_binding_status='lexical-intake-code-binding; not-followed-or-verified-now',
        path_binding_code='scripts/b3_local_data_receipt.py:intake',
        upstream_archive_url='http://images.cocodataset.org/annotations/annotations_trainval2017.zip',
        byte_exact_artifact_receipt_ready=True,raw_bytes_verified_now=False,
        release_label='COCO2017 val2017',archive_name='annotations_trainval2017.zip',archive_sha256=None,
        archive_revision=None,archive_identity_status='unavailable-original-ZIPs-absent',
        annotation_license='CC-BY-4.0 per existing datasheet; not image rights',
        source_page_revision='5e1c4da72464b1c6f068df0c02c91e3000ea62c4',
        source_page_revision_scope='maintained download/terms page only, not archive bytes',
        values_opened=False)


def assemble(schedule,source_rows,split_rows,config,acquisition):
    """Pure metadata joins. Missing/invalid planned sources remain explicit."""
    expected=derive_schedule(split_rows)
    for key in ('clean','t3_source_uids','t4_pairs','t5','n_metadata_candidates'):
        if schedule.get(key)!=expected[key]:raise ValueError('Frozen schedule mismatch: '+key)
    if len(schedule['clean'])!=300:raise ValueError('Exact frozen300 required')
    for key in ('source_contract_accepted','scientific_run_authorized','images_or_annotations_opened'):
        if schedule.get(key) is not False:raise ValueError('Preparation requires locked schedule flags')
    if schedule.get('candidate')!='UNRESOLVED':raise ValueError('No candidate adoption in index builder')
    if config.get('source_manifest')!='data/b4-admission-20260926/source-manifest.csv' or config.get('manifest_sha256')!=PINS['data/b4-admission-20260926/source-manifest.csv']:
        raise ValueError('Not the admitted authoritative source manifest')
    if config.get('scientific_compute_authorized') is not False or config.get('final_scientific_split_accepted') is not False:
        raise ValueError('Changed source contract flags require review')
    by_source={};by_split={}
    for row in source_rows:
        if not SOURCE_FIELDS.issubset(row):raise ValueError('Missing source manifest columns')
        ident=uid(row)
        if ident in by_source:raise ValueError('Duplicate authoritative source UID')
        by_source[ident]=row
    for row in split_rows:
        ident=row['source_uid']
        if ident in by_split:raise ValueError('Duplicate split UID')
        by_split[ident]=row
    entries=[];all_errors=[]
    for ordinal,item in enumerate(schedule['clean']):
        ident=item['source_uid'];source=by_source.get(ident);split=by_split.get(ident);errors=[]
        entry=dict(schedule_index=ordinal,**item,domain='ms-coco',release_id='coco-2017',source_split='val2017',study_split='test',
            raw_root=RAW_ROOT,raw_relative_path=None,external_raw_path=None,raw_sha256=None,raw_size_bytes=None,
            source_manifest_raw_group_id=None,source_url=None,license_reference=None,rights_status=None,use_limitations=None,
            metadata_outcome='missing',errors=errors,raw_bytes_opened=False,raw_bytes_verified_now=False)
        if source is None:errors.append('missing_admitted_source_receipt')
        if split is None:errors.append('missing_split_receipt')
        if source is not None and split is not None:
            for key in ('domain','release_id','source_split','source_id'):
                if source[key]!=split[key]:errors.append('source_split_identity_mismatch:'+key)
            if source['domain']!='ms-coco' or source['release_id']!='coco-2017' or source['source_split']!='val2017':errors.append('not_COCO2017_val2017')
            if split['study_split']!='test' or split['primary_group_representative']!='true' or split['group_id']!=item['group_id']:errors.append('not_frozen_primary_test_group')
            if source['raw_sha256']!=split['raw_sha256']:errors.append('source_split_raw_hash_mismatch')
            try:
                relative=safe_relative(source['relative_path'])
                if relative!=f"val2017/val2017/{int(source['source_id']):012d}.jpg":raise ValueError('Unexpected COCO extracted wrapper/member')
                if type(source['raw_sha256']) is not str or not HASH.fullmatch(source['raw_sha256']):raise ValueError('Malformed raw SHA256')
                size=source['raw_size_bytes']
                if type(size) is not str or not re.fullmatch('[1-9][0-9]*',size):raise ValueError('Malformed raw byte size')
                for field in ('source_url','license_reference','rights_status','use_limitations','group_id'):
                    if type(source[field]) is not str or not source[field]:raise ValueError('Missing source provenance:'+field)
                entry.update(raw_relative_path=relative,external_raw_path=RAW_ROOT+'/'+relative,raw_sha256=source['raw_sha256'],raw_size_bytes=int(size),
                    source_manifest_raw_group_id=source['group_id'],source_url=source['source_url'],license_reference=source['license_reference'],
                    rights_status=source['rights_status'],use_limitations=source['use_limitations'])
            except (ValueError,TypeError) as exc:errors.append(str(exc))
        entry['metadata_outcome']='ready_existing_receipt' if not errors else 'missing_or_invalid_receipt'
        all_errors.extend(dict(source_uid=ident,reason=e) for e in errors);entries.append(entry)
    annotation=annotation_receipt(acquisition)
    return dict(schema_version=VERSION,status='metadata_only_no_scientific_unlock',candidate='UNRESOLVED',
        datasets=[dict(id='ms-coco',version='coco-2017',source_split='val2017',study_split='test',
            license='per-image references retained; rights pending; annotations CC-BY-4.0 are not image rights')],
        metadata_readiness=dict(planned_sources=300,existing_raw_receipts_ready=sum(not e['errors'] for e in entries),
            raw_index_ready=len(entries)==300 and not all_errors,annotation_extracted_receipt_ready=True,
            annotation_external_path_binding_ready=True,annotation_archive_identity_ready=False,
            annotation_archive_identity_required_for_extracted_artifact=False,complete_protocol_receipts_ready=len(entries)==300 and not all_errors),
        source_contract_accepted=False,scientific_split_accepted=False,scientific_unlock=False,scientific_compute_authorized=False,
        images_annotations_features_opened=False,entries=entries,input_errors=all_errors,annotation=annotation,
        blockers=['source_rights_group_scope_acceptance_and_user_confirmatory_decision_pending'],
        provenance_limits=['original_COCO_image_and_annotation_ZIP_identity_unavailable; exact_extracted_artifact_receipts_retained'],
        raw_verification_contract='Only the authorized scientific worker resolves contained raw paths, rejects links/escape, hashes byte receipts before decode, and retains failed planned conditions without replacement.',
        group_contract='group_id is frozen split operational component; source_manifest_raw_group_id is prior raw-byte group; neither certifies population independence.')


def read_pinned_metadata(root,relative,expected_sha):
    # Read exactly a caller-declared metadata file; never paths contained in it.
    if relative not in PINS or expected_sha!=PINS[relative]:raise ValueError('Unknown metadata input')
    root=Path(root).resolve();path=(root/relative).resolve()
    if not path.is_relative_to(root):raise ValueError('Metadata input escapes checkout')
    raw=path.read_bytes()
    if digest(raw)!=expected_sha:raise ValueError('Metadata input hash mismatch: '+relative)
    return raw,dict(path=str(path),sha256=digest(raw),size_bytes=len(raw))


def prepare(metadata_root,output):
    # Only enumerated metadata inputs and versioned schedule are read.
    snapshots={};receipts={}
    for relative,pin in PINS.items():snapshots[relative],receipts[relative]=read_pinned_metadata(metadata_root,relative,pin)
    path=ROOT/'research/m1-confirmatory-schedule-draft.json';raw=path.read_bytes()
    if digest(raw)!=SCHEDULE_SHA:raise ValueError('Frozen schedule bytes changed')
    schedule=json.loads(raw.decode('utf-8'));source=list(csv.DictReader(io.StringIO(snapshots['data/b4-admission-20260926/source-manifest.csv'].decode('utf-8-sig'))))
    splits=list(csv.DictReader(io.StringIO(snapshots['data/splits.csv'].decode('utf-8-sig'))))
    result=assemble(schedule,source,splits,json.loads(snapshots['configs/splits-admitted-v2.json']),json.loads(snapshots['data/intake/20260926-extracted-source-receipt.json']))
    result['provenance']=dict(schedule=dict(path='research/m1-confirmatory-schedule-draft.json',sha256=digest(raw),size_bytes=len(raw)),
        metadata_inputs=receipts,builder=dict(path='scripts/m1_confirmatory_external_index.py',sha256=digest(Path(__file__).read_bytes())),
        schedule_algorithm=dict(path='scripts/m1_confirmatory_schedule.py',sha256=digest((ROOT/'scripts/m1_confirmatory_schedule.py').read_bytes())),
        owner_algorithm=dict(path='scripts/a4_protocol_reference.py',sha256=digest((ROOT/'scripts/a4_protocol_reference.py').read_bytes())))
    result['metadata_payload_sha256']=canonical(result)
    output=Path(output).resolve()
    if not output.is_relative_to((ROOT/'research').resolve()) or output.suffix!='.json':raise ValueError('Contained new research JSON output required')
    with output.open('x',encoding='utf-8',newline='\n') as handle:json.dump(result,handle,indent=2,ensure_ascii=False,allow_nan=False);handle.write('\n')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata-root',type=Path,default=METADATA_ROOT)
    parser.add_argument('--output',type=Path,default=ROOT/'research/m1-confirmatory-external-index.json')
    args=parser.parse_args();result=prepare(args.metadata_root,args.output)
    print(json.dumps(result['metadata_readiness'],sort_keys=True));return 0

if __name__=='__main__':sys.exit(main())

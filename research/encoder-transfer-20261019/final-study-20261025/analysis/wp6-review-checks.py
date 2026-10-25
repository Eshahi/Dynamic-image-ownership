"""Independent WP6 arithmetic audit. Stdlib; saved JSON/JSONL only.

No project analysis import, refit, experiment, image/model read or execution.
Outputs remain in the reviewer's wp6-review-* namespace.
"""
import collections as C
import datetime as dt
import hashlib
import html
import itertools
import json
import math
from pathlib import Path
import random
import re
import statistics as S

HERE = Path(__file__).resolve().parent
FS = HERE.parent
RAW = Path('W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl')
RIGHT, WRONG = 'qim-pilot-owner-alpha', 'qim-pilot-owner-beta'
ARMS = ['f5-r2', 'v5-r3', 'wam', 'vine-r']
rows = {}
history = C.Counter()
transitions = C.Counter()
line_count = 0
digest = hashlib.sha256()
with RAW.open('rb') as f:
    for line in f:
        digest.update(line)
        if not line.strip():
            continue
        r = json.loads(line)
        line_count += 1
        history[r['status']] += 1
        if r['id'] in rows:
            transitions[rows[r['id']]['status'] + '->' + r['status']] += 1
        rows[r['id']] = r
sources = sorted({r['source_id'] for r in rows.values()})
def cell(r):
    return r['channel'] if r['strength'] is None else f"{r['channel']}@{r['strength']}"
index = {(r['arm'], cell(r), r['source_id'], r['seed']): r for r in rows.values()}
def seeds(c):
    return (12, 13, 14) if c.startswith('R') else (None,)
def call(r, arm, owner=RIGHT):
    if not r or r.get('status') != 'ok':
        return None
    d = r.get('detections', {}).get(arm, {}).get(owner)
    return d if d and d.get('status') == 'ok' else None
def finite(v):
    return type(v) in (int, float) and math.isfinite(v)
def pos(d, arm):
    return int(bool(d and (d.get('endpoints', {}).get('C') if arm in ARMS[:2] else d.get('presence', {}).get('present'))))
def state(d):
    if not d: return 'missing_call'
    s = d['raw']['semantic']
    return 'C_success' if s['read'] and s['content_match'] else 'read_content_mismatch' if s['read'] else 'found_not_read' if s['found'] else 'not_found'
def med(a):
    return S.median(a) if a and all(finite(x) for x in a) else None
def corr(pairs):
    pairs = [(x,y) for x,y in pairs if finite(x) and finite(y)]
    x,y=zip(*pairs)
    def rank(z):
        return [sum(a<v for a in z)+(sum(a==v for a in z)+1)/2 for v in z]
    return {'n':len(pairs),'pearson':S.correlation(x,y),'spearman':S.correlation(rank(x),rank(y))}
def boot(a):
    rng = random.Random(20261025)
    draws = sorted(S.mean(rng.choices(a,k=len(a))) for _ in range(1000))
    def q(p):
        k=999*p; i=int(k); return draws[i]*(1-k+i)+draws[i+1]*(k-i)
    return {'n':len(a),'mean':S.mean(a),'lo':q(.025),'hi':q(.975)}
summary, source_detail, errors = [], {}, []
published = json.loads((HERE/'journal-analysis.json').read_text())
published_by={(r['arm'],r['cell']):r for r in published['cell_summaries']}
for arm,c in sorted({(r['arm'],cell(r)) for r in rows.values() if r['arm'] in ARMS}):
    states=C.Counter(); details=[]; epcounts=C.Counter(); seed_counts=C.Counter()
    for sid in sources:
        rr=[index.get((arm,c,sid,s)) for s in seeds(c)]
        ds=[call(r,arm) for r in rr]
        n=len(rr); cut=n//2+1
        d={'source':sid,'positive':sum(pos(x,arm) for x in ds)>=cut,'complete':all(ds)}
        for ep in ['A','S','Q','H']:
            d[ep]=sum(bool(x and x.get('endpoints',{}).get(ep)) for x in ds)>=cut
        for tier in ['semantic','instance']:
            d[tier+'_found']=sum(bool(x and x.get('raw',{}).get(tier,{}).get('found')) for x in ds)>=cut
            d[tier+'_read']=sum(bool(x and x.get('raw',{}).get(tier,{}).get('read')) for x in ds)>=cut
            vals=[]
            for x in ds:
                raw=x.get('raw',{}).get(tier,{}) if x else {}
                a,b=raw.get('decoded_score'),raw.get('decoded_threshold')
                vals.append((a-b)/b if finite(a) and finite(b) and b else None)
            d[tier]=med(vals)
            d[tier+'_range']=max(vals)-min(vals) if all(finite(x) for x in vals) else None
        d['bits']=med([x.get('presence',{}).get('accuracy') if x else None for x in ds])
        for name,key in [('attack','distortion'),('total','total_distortion')]:
            for metric in ['lpips','psnr_db','ssim_rgb']:
                d[name+'_'+metric]=med([r.get(key,{}).get(metric) if r and r.get('status')=='ok' else None for r in rr])
        for s,x in zip(seeds(c),ds):
            if arm in ARMS[:2]: states[state(x)]+=1
            seed_counts[str(s)]+=pos(x,arm)
        details.append(d); source_detail[arm,c,sid]=d
    sm={'arm':arm,'cell':c,'positive':sum(d['positive'] for d in details),'complete':sum(d['complete'] for d in details),'states':dict(states),'seed_counts':dict(seed_counts)}
    for k in ['semantic','instance','bits','semantic_range','instance_range']:
        v=[d[k] for d in details if finite(d[k])]
        sm[k]={'n':len(v),'median':S.median(v) if v else None}
    for k in ['A','S','Q','H','semantic_found','semantic_read','instance_found']:
        sm[k]=sum(d[k] for d in details)
    old=published_by[arm,c]
    if sm['positive']!=old['positive_majority'] or sm['complete']!=old['complete_sources']:
        errors.append(['cell count',arm,c,sm['positive'],sm['complete']])
    for name,key in [('semantic','semantic_decoded_normalized_median'),('instance','instance_decoded_normalized_median'),('bits','bit_accuracy_median')]:
        expected=old['continuous'].get(key)
        if expected and (sm[name]['n']!=expected['n'] or abs(sm[name]['median']-expected['median'])>1e-12):
            errors.append(['cell median',arm,c,name])
    summary.append(sm)

quality={}
for ref in ['attack','total']:
    complete=[]; joint=[]
    for sid in sources:
        a,b=(source_detail['f5-r2',c,sid] for c in ['R1@0.1','R0@0.2'])
        keys=[ref+'_'+m for m in ['lpips','psnr_db','ssim_rgb']]
        if all(finite(z[k]) for z in [a,b] for k in keys):
            complete.append(sid)
            if a[keys[0]]<b[keys[0]] and a[keys[1]]>b[keys[1]] and a[keys[2]]>b[keys[2]]:
                joint.append(sid)
    quality[ref]={'complete':len(complete),'dominance':len(joint),'dominance_retain_lose':sum(source_detail['f5-r2','R0@0.2',s]['positive'] and not source_detail['f5-r2','R1@0.1',s]['positive'] for s in joint)}
quality['strict_clean']={arm:sum(all(finite(source_detail[arm,'clean',s]['attack_'+m]) for m in ['lpips','psnr_db','ssim_rgb']) and source_detail[arm,'clean',s]['attack_lpips']<.1 and source_detail[arm,'clean',s]['attack_psnr_db']>35 and source_detail[arm,'clean',s]['attack_ssim_rgb']>.9 for s in sources) for arm in ARMS}
for ref in ['attack','total']:
    pairs=[(source_detail['f5-r2','R1@0.1',s],source_detail['f5-r2','R0@0.4',s]) for s in sources]
    keys=[ref+'_'+m for m in ['lpips','psnr_db','ssim_rgb']]
    pairs=[(a,b) for a,b in pairs if all(finite(z[k]) for z in [a,b] for k in keys)]
    quality[ref+'_R0.4']={'complete':len(pairs),'dominance':sum(a[keys[0]]<b[keys[0]] and a[keys[1]]>b[keys[1]] and a[keys[2]]>b[keys[2]] for a,b in pairs)}
correlations={c:corr([(source_detail['f5-r2','clean',s]['semantic'],source_detail['f5-r2',c,s]['semantic']) for s in sources]) for c in ['R0@0.1','R0@0.2','R0@0.4','R1@0.1','R1@0.2','R1@0.4','D1','D3']}
correlations['pooled_quality']=corr([(d['semantic'],d['attack_lpips']) for (a,c,s),d in source_detail.items() if a=='f5-r2' and c.startswith(('R0@','R1@'))])
correlations['R0.4_quality']=corr([(source_detail['f5-r2','R0@0.4',s]['semantic'],source_detail['f5-r2','R0@0.4',s]['attack_lpips']) for s in sources])
paired={}
for c1,c0 in [('R1@0.1','R0@0.2'),('R1-rinse@0.1','R1@0.1'),('R1-smooth@0.2','R1-mode@0.2')]:
    for k in ['semantic','positive']:
        a=[int(source_detail['f5-r2',c1,s][k])-int(source_detail['f5-r2',c0,s][k]) if k=='positive' else source_detail['f5-r2',c1,s][k]-source_detail['f5-r2',c0,s][k] for s in sources if k=='positive' or all(finite(source_detail['f5-r2',c,s][k]) for c in [c1,c0])]
        paired[c1+' minus '+c0+' '+k]=boot(a)
rinse={}
for arm in ARMS:
    tab=C.Counter()
    for s in sources:
        for seed in [12,13,14]:
            a,b=(call(index[arm,c,s,seed],arm) for c in ['R1@0.1','R1-rinse@0.1'])
            tab[(state(a)+'->'+state(b)) if arm in ARMS[:2] else f'{pos(a,arm)}->{pos(b,arm)}']+=1
    rinse[arm]=dict(tab)
negatives={}
for arm in ARMS:
    for kind in ['C0','wrong']:
        eligible=[r for r in rows.values() if r['arm']==('unmarked' if kind=='C0' else arm)]
        events=[]; missing=[]
        for r in eligible:
            d=call(r,arm,RIGHT if kind=='C0' else WRONG)
            if not d: missing.append(r['id']); continue
            event=d.get('endpoints',{}).get('A') if arm in ARMS[:2] else d.get('presence',{}).get('present')
            if event: events.append({'id':r['id'],'source':r['source_id'],'presence':d.get('presence')})
        negatives[arm+' '+kind]={'events':events,'missing_calls':len(missing),'planned_calls':len(eligible)}

# Re-evaluate saved regression coefficients and KKT conditions, not a new fit.
qresult=json.loads((HERE/'quality-model-results.json').read_text())
qm=json.loads((HERE/'quality-monotone-sensitivity.json').read_text())
scaled_betas=[(math.sqrt(.00085)+(math.sqrt(.012)-math.sqrt(.00085))*i/999)**2 for i in range(1000)]
ab={t:math.prod(1-z for z in scaled_betas[:t+1]) for t in [51,151,351]}
snr={s:math.log(ab[t]/(1-ab[t])) for s,t in [(.1,51),(.2,151),(.4,351)]}
regression={}; all_kkt=[]; all_moment_errors=[]
for arm in ARMS[:2]:
    data=[]
    for r in rows.values():
        if r['arm']!=arm or r['channel'] not in ['R0','R1']: continue
        d=call(r,arm); quality_r=r.get('distortion',{})
        fv=[quality_r.get(m) for m in ['lpips','psnr_db','ssim_rgb']]
        if d and all(finite(v) for v in fv):
            data.append({'source':r['source_id'],'cell':cell(r),'strength':r['strength'],'fold':int(hashlib.sha256(('et-final-wp2-v1/'+str(r['source_id'])).encode()).hexdigest(),16)%5,'y':pos(d,arm),'f':fv+[float(r['channel']=='R1'),snr[r['strength']]]})
    counts=C.Counter((d['source'],d['cell']) for d in data)
    for d in data: d['w']=1/counts[d['source'],d['cell']]
    regression[arm]={}
    cv_source_losses={}
    for split,selector in [('cv','fold'),('loso','strength')]:
        regression[arm][split]={}
        for model,cols in [('D0',[]),('D1',[0]),('D2',[0,1,2]),('D3',[0,1,2,3,4]),('D3M',[0,1,2,3,4])]:
            losses=[]; sl=C.defaultdict(list)
            record=qm['arms'][arm][split] if model=='D3M' else qresult['arms'][arm][split][model]
            for fit in record['fits']:
                train=[d for d in data if d[selector]!=fit['group']]
                test=[d for d in data if d[selector]==fit['group']]
                beta=fit['beta']; moments=fit['moments']; grad=[0.]+beta[1:]
                for j,(mean,sd) in zip(cols,moments):
                    wsum=sum(d['w'] for d in train)
                    m=sum(d['w']*d['f'][j] for d in train)/wsum
                    v=sum(d['w']*(d['f'][j]-m)**2 for d in train)/wsum
                    all_moment_errors += [abs(m-mean),abs(math.sqrt(v)-sd)]
                for d in train+test:
                    x=[1.]+[(d['f'][j]-m)/s for j,(m,s) in zip(cols,moments)]
                    z=sum(b*xx for b,xx in zip(beta,x)); p=1/(1+math.exp(-z))
                    if d[selector]!=fit['group']:
                        for j in range(len(grad)): grad[j]+=d['w']*(p-d['y'])*x[j]
                    else:
                        loss=(p-d['y'])**2; losses.append((d['w'],loss)); sl[d['source']].append((d['w'],loss))
                kkt=[]
                for j,g in enumerate(grad):
                    if model in ['D1','D2','D3M'] and j==1 and abs(beta[j])<1e-12: kkt.append(max(0,g))
                    elif model in ['D2','D3M'] and j in [2,3] and abs(beta[j])<1e-12: kkt.append(max(0,-g))
                    else: kkt.append(abs(g))
                all_kkt.append(max(kkt))
            score=sum(w*l for w,l in losses)/sum(w for w,l in losses)
            expected=record['overall']['weighted_brier']
            if abs(score-expected)>1e-12: errors.append(['regression Brier',arm,split,model,score,expected])
            regression[arm][split][model]=score
            if split=='cv': cv_source_losses[model]={s:sum(w*l for w,l in v)/sum(w for w,l in v) for s,v in sl.items()}
    regression[arm]['D3_minus_D2_bootstrap']=boot([cv_source_losses['D3'][s]-cv_source_losses['D2'][s] for s in sources])
    for model in ['D3','D3M']:
        rng=random.Random(20261025)
        differences=[cv_source_losses[model][s]-cv_source_losses['D2'][s] for s in sources]
        draws=sorted(S.mean(rng.choice(differences) for _ in sources) for _ in range(1000))
        regression[arm][model+'_minus_D2_exact_published_bootstrap_recipe']={'mean':S.mean(differences),'lo':draws[24],'hi':draws[974]}
regression['max_abs_saved_moment_error']=max(all_moment_errors)
regression['max_projected_kkt_gradient']=max(all_kkt)
regression['number_original_fits_checked']=len(all_kkt)

# Exact finite binomial sums and inverted one-sided bounds, no simulation.
def lower(k,p,n=200): return sum(math.comb(n,j)*p**j*(1-p)**(n-j) for j in range(k+1))
def upper(k,p,n=200): return sum(math.comb(n,j)*p**j*(1-p)**(n-j) for j in range(k,n+1))
alpha=.05/13
stat={}
for name,p,side in [('loss',.1,'lower'),('retain',.8,'upper'),('control',.9,'upper'),('remove',.5,'upper')]:
    tail=lower if side=='lower' else upper
    good=[k for k in range(201) if tail(k,p)<=alpha]
    crit=max(good) if side=='lower' else min(good)
    powers=[.01,.02,.03,.05] if side=='lower' else [.85,.875,.9,.95] if p==.8 else [.95,.97,.98,.99] if p==.9 else [.55,.6,.65,.7]
    stat[name]={'critical':crit,'boundary_p':tail(crit,p),'adjacent_p':tail(crit+(1 if side=='lower' else -1),p),'power':{str(z):tail(crit,z) for z in powers}}
penalty=7*1.8*math.log(2/alpha)/(3*199)
stat['eb_radii']={str(sd):math.sqrt(2*sd*sd*math.log(2/alpha)/200)+penalty for sd in [0,.1,.2]}
stat['zero_event_95']={str(n):1-.05**(1/n) for n in [60,200]}
stat['eight_negative_upper']=1-(.05/8)**(1/200)
stat['zero_event_n_for_1e_6']=math.ceil(math.log(.05)/math.log(1-1e-6))
stat['normal_mu90']=S.NormalDist().inv_cdf(1-1e-6)+S.NormalDist().inv_cdf(.9)
stat['eb_min_n_zero_variance']={str(r):math.floor(7*1.8*math.log(2/alpha)/(3*.8*r)+1)+1 for r in [.25,.1,.04,.01]}
stat['h4_scenario_passing_errors']=[k for k in range(201) if lower(k,.1)<=alpha and .2-k/200-math.sqrt(2*(k/200*(1-k/200)*200/199)*math.log(2/alpha)/200)-penalty>0]
stat['h4_scenario_power']={str(e):lower(max(stat['h4_scenario_passing_errors']),e) for e in [.01,.02,.03,.05]}
cos_ab=math.cos((.152+.008)/1.008*math.pi/2)**2/math.cos(.008/1.008*math.pi/2)**2
schedule={'scaled_linear':{str(t):{'alpha_bar':v,'a_over_b':math.sqrt(v/(1-v))} for t,v in ab.items()},'cosine_t151':{'alpha_bar':cos_ab,'a_over_b':math.sqrt(cos_ab/(1-cos_ab))}}

# Counts and existing timer mean accounting reconstructed directly.
g=C.defaultdict(list); d=C.defaultdict(list); mt=[]
for r in rows.values():
    key=r['channel']+':'+(r['arm'] if r['channel']=='clean' else str(r['strength']))
    if 'generation_seconds' in r:g[key].append(r['generation_seconds'])
    for m,t in r.get('detection_seconds',{}).items():d[m+':'+r['control']].append(t)
    if 'metrics_seconds' in r:mt.append(r['metrics_seconds'])
gen_native=200*5*3*sum(S.mean(g[f'{c}:{s}']) for c,s in [('R0',.1),('R0',.2),('R0',.4),('R1',.1),('R1',.2),('R1',.4),('R3',.2)])/3600
gen_clean=200*sum(S.mean(g['clean:'+a]) for a in ['unmarked']+ARMS)/3600
assess=sum(S.mean(d[a+':C0'])+S.mean(d[a+':C1']) for a in ARMS)+5*S.mean(mt)
known_core=gen_native+gen_clean+200*22*assess/3600
attack_assess=200*9*assess/3600
achain=200*5*3*(S.mean(g['R1:0.2'])+S.mean(g['R0:0.2']))/3600
cost={'core_native_generation_hours':gen_native,'clean_embedding_hours':gen_clean,'per_source_setting_assessment_seconds':assess,'known_clean_native_hours':known_core,'attack_assessment_hours':attack_assess,'A_generation_at_0.2_analogy_hours':achain,'known_subtotal_hours':known_core+attack_assess+achain,'known_subtotal_plus_30pct':1.3*(known_core+attack_assess+achain),'outputs':200*5*(1+7*3+3+3+1+1+1),'detector_batches':200*8*(1+7*3+3+3+1+1+1),'phaseA_law_JVP':60*6*3,'phaseA_encoder_JVP':12*4*3*5,'phaseA_differential_JVP':12*3*3*5,'phaseA_stage_primal':180+360+540+360+180,'phaseB_JVP':200*7*3,'retrieval10GB_hours':10_000/.85/3600}

# Independently reconstruct the originally frozen quality calipers.
calipers={}
for arm in ARMS:
    matches=[]
    for lo,hi in zip([0,.05,.1,.2,.3,.5],[.05,.1,.2,.3,.5,math.inf]):
        for sid in sources:
            eligible=[]
            for s0,s1 in itertools.product([.1,.2,.4],repeat=2):
                a=source_detail[arm,'R0@'+str(s0),sid]; b=source_detail[arm,'R1@'+str(s1),sid]
                keys=['attack_lpips','attack_psnr_db','attack_ssim_rgb']
                if not all(finite(z[k]) for z in [a,b] for k in keys):continue
                if not all(lo<=z['attack_lpips']<hi for z in [a,b]):continue
                distances=[abs(a[k]-b[k])/limit for k,limit in zip(keys,[.02,1,.02])]
                if max(distances)<=1:eligible.append((sum(d*d for d in distances),s0,s1))
            if eligible:matches.append({'source':sid,'bin':[lo,hi if finite(hi) else None],'pair':min(eligible)})
    calipers[arm]={'unique_sources':len({z['source'] for z in matches}),'matches':matches}

# Metadata-only manifest verification. No referenced image URL is opened.
manifest=json.loads((FS/'heldout-manifest.json').read_text(encoding='utf-8-sig'))
hm=HERE/'heldout-metadata'; selected=manifest['sources']
dates=[]; date=dt.date(2018,1,1)
while date<=dt.date(2025,12,31):
    ds=date.isoformat(); dates.append({'date':ds,'date_sha256':hashlib.sha256(('et-final-holdout-v1/20261025/'+ds).encode()).hexdigest()});date+=dt.timedelta(days=1)
dates.sort(key=lambda z:(z['date_sha256'],z['date']))
stored_dates=json.loads((hm/'date-order.json').read_text(encoding='utf-8-sig'))
decisions=json.loads((hm/'candidate-decisions.json').read_text(encoding='utf-8-sig'))
metadata_errors=[]
if dates!=stored_dates:metadata_errors.append('date order differs')
if [d['rank'] for d in decisions]!=list(range(1,820)):metadata_errors.append('evaluated prefix differs')
accepted=[d for d in decisions if d['decision']=='ACCEPTED']
for a,s in zip(accepted,selected):
    if (a['rank'],a['canonical_title'])!=(s['date_order_rank'],s['canonical_file_title']):metadata_errors.append(['accepted row differs',s['selection_index']])
cache={}
for i,s in enumerate(selected,1):
    if s['selection_index']!=i or s['assignment']!=('primary' if i<=200 else 'reserve') or s['assignment_index']!=(i if i<=200 else i-200):metadata_errors.append(['assignment',i])
    d=dates[s['date_order_rank']-1]
    if (d['date'],d['date_sha256'])!=(s['date'],s['date_order_sha256']):metadata_errors.append(['date',i])
    if not(s['mime']=='image/jpeg' and min(s['width'],s['height'])>=512 and s['width']*s['height']<=40_000_000 and .5<=s['width']/s['height']<=2 and s['size_bytes']<=20_000_000):metadata_errors.append(['geometry',i])
    plain=' '.join(html.unescape(re.sub('<[^>]*>','',s['attribution_html'])).split())
    if plain!=s['attribution_plain'] or plain.lower()!=s['creator_group']:metadata_errors.append(['creator normalization',i])
    receipt=s['metadata_receipt']
    if receipt not in cache:
        pp=json.loads((hm/receipt).read_text(encoding='utf-8-sig'))['query']['pages']
        cache[receipt]={p.get('pageid'):p for p in pp if 'pageid' in p}
    p=cache[receipt][s['commons_page_id']]; ii=p['imageinfo'][0]
    for sk,pk in [('width','width'),('height','height'),('size_bytes','size'),('sha1','sha1'),('mime','mime'),('original_file_url','url'),('description_url','descriptionurl'),('file_upload_timestamp','timestamp')]:
        if s[sk]!=ii[pk]:metadata_errors.append(['official receipt',i,sk])
    if s['canonical_file_title']!=p['title']:metadata_errors.append(['official title',i])
    em=ii['extmetadata']
    for sk,pk in [('licence_label','LicenseShortName'),('licence_url','LicenseUrl'),('licence_code','License'),('copyrighted','Copyrighted'),('attribution_html','Artist')]:
        if s[sk]!=em.get(pk,{}).get('value'):metadata_errors.append(['official attribution/license',i,sk])
    if s['acquisition_status']!='NOT_DOWNLOADED' or s['raw_sha256'] is not None or s['canonical_pixel_hash'] is not None:metadata_errors.append(['acquisition',i])
uniqueness={k:len({s[k] for s in selected}) for k in ['commons_page_id','canonical_file_title','sha1','original_file_url','creator_group']}
if set(uniqueness.values())!={240}:metadata_errors.append('nonunique accepted identifiers')
metadata={'date_count':len(dates),'evaluated':len(decisions),'accepted':len(accepted),'rejected':sum(d['decision']=='REJECTED' for d in decisions),'last_date':decisions[-1]['date'],'licence_counts':dict(C.Counter(s['licence_label'] for s in selected)),'rejection_reasons':dict(C.Counter(r for d in decisions for r in d['reasons'])),'unique_counts':uniqueness,'raw_official_receipts_checked':len(cache),'all_accepted_rows_checked_against_official_receipts':len(selected),'errors':metadata_errors}
exclusion_files=json.loads((hm/'exclusion-files.json').read_text(encoding='utf-8-sig'))
hash_tokens=set(); changed=[]
for receipt in exclusion_files:
    path=Path(receipt['path'])
    assert path.suffix.lower() in {'.md','.json','.jsonl','.csv','.txt','.tsv'}, str(path)
    data=path.read_bytes()
    if len(data)!=receipt['bytes'] or hashlib.sha256(data).hexdigest()!=receipt['sha256']:
        changed.append(str(path))
    text=data.decode('utf-8-sig')
    hash_tokens.update(t.lower() for t in re.findall(r'(?<![A-Za-z0-9])(?:[0-9a-fA-F]{64}|[0-9a-fA-F]{40}|[0-9a-zA-Z]{31})(?![A-Za-z0-9])',text))
overlaps=[s['selection_index'] for s in selected if s['sha1'].lower() in hash_tokens]
saved_tokens=set(json.loads((hm/'exclusion-identifiers.json').read_text(encoding='utf-8-sig'))['hash_tokens'])
metadata['exclusion_receipts']={'files_rehashed':len(exclusion_files),'changed_files':changed,'independently_extracted_hash_tokens':len(hash_tokens),'saved_minus_independent':sorted(saved_tokens-hash_tokens),'independent_minus_saved':sorted(hash_tokens-saved_tokens),'accepted_sha1_overlaps':overlaps,'limitation':'No cross-algorithm comparison or image/near-duplicate inspection; URL/title extraction not independently fully replayed.'}
metadata['exclusion_receipts']['token_parser_difference_explanation']='The one additional preserved token is a source-code revision written immediately after revision in research/downloads.md:61; the independent parser requires an alphanumeric boundary. It is not an accepted image identifier. The saved conservative exclusion inventory is larger, not missing this token.'
if changed or overlaps:metadata_errors.append(['exclusion_receipts',changed,overlaps])
errors += [['manifest',e] for e in metadata_errors]

out={'reviewed_commit':'3d66de863f570244df91809049d82b36088b7fd7','utc':dt.datetime.now(dt.timezone.utc).isoformat(),'raw':{'path':str(RAW),'sha256':digest.hexdigest(),'lines':line_count,'unique_units':len(rows),'sources':len(sources),'final_status':dict(C.Counter(r['status'] for r in rows.values())),'history':dict(history),'transitions':dict(transitions)},'cell_summaries':summary,'quality':quality,'correlations':correlations,'paired_bootstraps':paired,'rinse_transitions':rinse,'negative_calls':negatives,'regression_saved_parameter_recalculation':regression,'analytic_statistics':stat,'schedule':schedule,'cost':cost,'calipers':calipers,'manifest_metadata':metadata,'comparison_errors':errors}
(HERE/'wp6-review-checks.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps({'errors':errors,'calipers':calipers,'manifest':metadata,'regression':regression},indent=2))

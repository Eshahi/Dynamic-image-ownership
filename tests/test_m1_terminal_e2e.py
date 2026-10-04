"""CPU-only admission, frozen math/config and gate integrity tests."""
import copy, json, math, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import m1_terminal_e2e as e2e

def passing_rows(ids):
    rows=e2e.planned(ids)
    for row in rows:
        row['outcome']='completed';row['quality_vs_source']={'quality_admissible':True,'psnr_infinite':False,'psnr_db':36.,'mse_rgb8':16.,'ssim_rgb':.99,'lpips':.01}
        row['owner_decisions']={}
        for owner in e2e.core.OWNERS:
            s=i=0.
            if row['control']=='C1' and owner==e2e.core.OWNERS[0]:
                s=5.;i=5. if row['dose']=='clean' else 0.
            row['owner_decisions'][owner]=dict(s=s,i=i,**e2e.core.classify_scores(s,i))
    return rows

class GateTests(unittest.TestCase):
    def test_full_gate_inventory(self):
        rows=passing_rows(e2e.PILOT_IDS);g=e2e.two_source_gate(rows)
        self.assertTrue(g['passes']);self.assertEqual((g['planned_conditions'],g['planned_owner_queries'],g['planned_negative_queries']),(8,32,28))
        s=g['source_gates']['1675'];self.assertEqual(s['negative_queries_below_both_n'],14)

    def test_missing_and_duplicate_rows(self):
        rows=passing_rows([1675])
        self.assertFalse(e2e.source_gate(rows[:-1],1675)['passes'])
        rows[-1]=copy.deepcopy(rows[0]);self.assertFalse(e2e.source_gate(rows,1675)['passes'])

    def test_malformed_membership(self):
        rows=passing_rows([1675]);rows[0]['dose']='other'
        self.assertFalse(e2e.source_gate(rows,1675)['passes'])

    def test_negative_controls_are_both_channel(self):
        rows=passing_rows([1675]);d=rows[0]['owner_decisions'][e2e.core.OWNERS[0]]
        d.update(s=4.,**e2e.core.classify_scores(4.,0.))
        self.assertFalse(e2e.source_gate(rows,1675)['passes'])

    def test_invalid_numeric_and_forged_flags(self):
        for bad in (None,float('nan'),float('inf'),True):
            rows=passing_rows([1675]);rows[0]['owner_decisions'][e2e.core.OWNERS[0]]['s']=bad
            self.assertFalse(e2e.source_gate(rows,1675)['passes'])
        rows=passing_rows([1675]);rows[0]['owner_decisions'][e2e.core.OWNERS[0]]['s']=6.
        self.assertFalse(e2e.source_gate(rows,1675)['passes'])

    def test_clean_quality_and_cycle_semantic(self):
        rows=passing_rows([1675]);rows[2]['quality_vs_source']['quality_admissible']=False
        self.assertFalse(e2e.source_gate(rows,1675)['passes'])
        rows=passing_rows([1675]);rows[2]['quality_vs_source']['psnr_db']=34.
        self.assertFalse(e2e.source_gate(rows,1675)['passes'])
        rows=passing_rows([1675]);rows[3]['owner_decisions'][e2e.core.OWNERS[0]]=dict(s=0.,i=5.,**e2e.core.classify_scores(0.,5.))
        self.assertFalse(e2e.source_gate(rows,1675)['passes'])

    def test_other_sources_do_not_replace_pilot(self):
        self.assertFalse(e2e.two_source_gate(passing_rows([1675,6012]))['passes'])

class FrozenTests(unittest.TestCase):
    def test_scientific_math_reused_by_identity(self):
        for name in ('optimize','Embedder','FixedSourceScores','PublicReader','detect','checkpoint_save','checkpoint_load'):
            self.assertIs(getattr(e2e,name),getattr(e2e.component,name))

    def test_config_exact_and_unchanged_loss(self):
        cfg=e2e.configuration();self.assertEqual(cfg,json.loads((ROOT/'research/m1-terminal-e2e-dev.json').read_text()))
        old=e2e.component.configuration()
        for key in ('threshold','owners','steps','learning_rate','adam_betas','adam_eps','cycle_every','semantic_margin','instance_margin','cycle_margin','quality_weight','psnr_cap_db','bisection_steps','embedder_precision','reader_precision','run_seconds_cap','gpu_budget_bytes','ram_budget_bytes','artifact_budget_bytes'):
            self.assertEqual(cfg[key],old[key],key)
        self.assertNotIn('reconstruction_run',cfg);self.assertEqual(tuple(c['id'] for c in cfg['cases']),e2e.IDS)

    def test_rng_reset_after_placement_not_on_resume(self):
        import ast
        tree=ast.parse((ROOT/'scripts/m1_terminal_e2e.py').read_text())
        run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
        phase=next(n for n in ast.walk(run) if isinstance(n,ast.If) and isinstance(n.test,ast.Compare)
            and isinstance(n.test.left,ast.Name) and n.test.left.id=='resume' and any(isinstance(x,ast.Constant) and x.value is None for x in n.test.comparators))
        self.assertEqual(ast.unparse(phase.test),'resume is None')
        self.assertEqual(ast.unparse(phase.body[0]),'phase_seed_zero()')
        calls=[n for n in ast.walk(run) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='placement']
        self.assertLess(min(n.lineno for n in calls),phase.lineno)
        self.assertGreater(next(n.lineno for n in ast.walk(run) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='optimize'),phase.lineno)

class ReceiptTests(unittest.TestCase):
    def fixture(self,base):
        source=base/'.thesis-build/dev-runs/component';source.mkdir(parents=True)
        run={'schema':e2e.component.VERSION,'outcome':'completed','conditions':passing_rows(e2e.PILOT_IDS),
            'committed_files':{'scripts/m1_blind_noise_core.py':{'working_sha256':e2e.util.sha(ROOT/'scripts/m1_blind_noise_core.py')}}}
        (source/'run.json').write_text(json.dumps(run))
        analysis=base/'.thesis-build/dev-runs/analysis';analysis.mkdir()
        value={'schema':'m1-terminal-continuous-analysis-v1','data_split':'development','outcome':'completed','errors':[],
            'inputs':{str(source/'run.json'):e2e.util.sha(source/'run.json')},'outputs':{},
            'gate':{'promotion':True,'receipt_integrity':True,'inventory_complete':True,
                'negative_queries':{'planned':28,'observed':28,'below_both':28},
                **{k:{'planned':2,'observed':2,'positive':2} for k in ('clean_quality','clean_blind_both','cycle_blind_semantic')}}}
        (analysis/'run.json').write_text(json.dumps(value));return analysis/'run.json',source/'run.json'

    def test_component_receipt_tampering(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(e2e,'MAIN',Path(temp)):
            ap,rp=self.fixture(Path(temp));self.assertEqual(e2e.require_component_analysis(ap)['sha256'],e2e.util.sha(ap))
            rp.write_text(rp.read_text()+' ')
            with self.assertRaisesRegex(ValueError,'source receipt'):e2e.require_component_analysis(ap)

    def test_incomplete_analysis_cannot_unlock(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(e2e,'MAIN',Path(temp)):
            ap,_=self.fixture(Path(temp));value=json.loads(ap.read_text());value['gate']['promotion']=None;ap.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError,'complete original'):e2e.require_component_analysis(ap)

    def test_changed_owner_core_needs_explicit_audit(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(e2e,'MAIN',Path(temp)):
            ap,rp=self.fixture(Path(temp));run=json.loads(rp.read_text())
            run['committed_files']['scripts/m1_blind_noise_core.py']['working_sha256']='0'*64;rp.write_text(json.dumps(run))
            value=json.loads(ap.read_text());value['inputs'][str(rp)]=e2e.util.sha(rp);ap.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError,'explicit compatibility'):e2e.require_component_analysis(ap)

    def test_owner_compatibility_counts_and_tampering(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(e2e,'MAIN',Path(temp)):
            base=Path(temp)/'.thesis-build/dev-runs/owner';base.mkdir(parents=True)
            artifact=base/'cells.json';artifact.write_text('[]')
            value={'schema':'m1-owner-extension-audit-v1','data_split':'synthetic-and-retained-development',
                'outcome':'completed','compatibility_passed':True,'errors':[],
                'old_source_sha256':'0'*64,'new_source_sha256':e2e.util.sha(ROOT/'scripts/m1_blind_noise_core.py'),
                'committed_files':{k:e2e.util.sha(ROOT/k) for k in ('scripts/m1_owner_extension_audit.py','scripts/m1_blind_noise_core.py')},
                'outputs':{'cells.json':e2e.util.sha(artifact)},
                'summary':{'legacy_cells_per_pass':128,'legacy_passes':2,'development_replayed_queries':32,
                    'projection_cells':512,'alignment_cells':8192,'null_cells':512,'distinct_maps':20}}
            rp=base/'run.json';rp.write_text(json.dumps(value));self.assertEqual(e2e.require_owner_extension(rp,'0'*64)['path'],str(rp))
            value['summary']['development_replayed_queries']=31;rp.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError,'Full matching'):e2e.require_owner_extension(rp,'0'*64)
            value['summary']['development_replayed_queries']=32;rp.write_text(json.dumps(value));artifact.write_text('[1]')
            with self.assertRaisesRegex(ValueError,'output inventory'):e2e.require_owner_extension(rp,'0'*64)

    def test_heldout_or_external_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'run.json';p.write_text('{}')
            with self.assertRaisesRegex(ValueError,'MAIN development'):e2e.checked_record(p)

    def test_expansion_needs_same_method(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(e2e,'MAIN',Path(temp)):
            p=Path(temp)/'.thesis-build/dev-runs/merge';p.mkdir(parents=True)
            (p/'run.json').write_text(json.dumps({'schema':'m1-terminal-e2e-pilot-merge-v1','data_split':'development','outcome':'completed','method_core_sha256':'other','gate':{'passes':True}}))
            with self.assertRaisesRegex(ValueError,'same-core'):e2e.require_expansion(p/'run.json','expected')

if __name__=='__main__':unittest.main()

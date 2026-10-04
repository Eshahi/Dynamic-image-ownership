"""Synthetic CPU checks for the unchanged IPS expansion; no model is loaded."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import m1_phase_residual_expansion as expansion
import m1_phase_residual as residual
import m1_phasemark as phase


class ExpansionTests(unittest.TestCase):
    def test_exact_remaining_ten_and_fixed_inventory(self):
        config=expansion.configuration();rows=expansion.planned()
        self.assertEqual(len(config['cases']),10)
        self.assertEqual([c['id'] for c in config['cases']],list(expansion.IDS))
        self.assertFalse(set(expansion.IDS)&set(phase.IDS))
        self.assertEqual(len(rows),40);self.assertEqual(len({r['id'] for r in rows}),40)
        self.assertEqual(len(rows)*len(config['owners']),160)
        self.assertEqual({(r['arm'],r['profile']) for r in rows},{('IPS','quality-cap')})

    def test_manifest_and_payloads_frozen_not_heldout_or_replaced_source(self):
        config=expansion.configuration()
        saved=json.loads((expansion.ROOT/'research/m1-phase-residual-expansion-dev.json').read_text(encoding='utf-8'))
        self.assertEqual(saved,config);self.assertEqual(expansion.validate(saved),saved['cases'])
        self.assertEqual(config['payloads'],{o:phase.payload(o) for o in phase.OWNERS})
        for change in (lambda c:c.update(data_split='test'),lambda c:c.update(threshold=81),
                       lambda c:c['cases'][0].update(sha256='0'*64),lambda c:c.update(arms=['APM'])):
            changed=copy.deepcopy(config);change(changed)
            with self.assertRaises(ValueError):expansion.validate(changed)

    def test_same_decode_is_exact_source_noop(self):
        source=np.arange(90,dtype=np.uint8).reshape(5,6,3)
        decode=np.random.default_rng(1).random(source.shape).astype(np.float32)
        marked,receipt=expansion.source_bypass(source,decode,decode)
        np.testing.assert_array_equal(marked,source)
        self.assertEqual(receipt['weight'],1);self.assertEqual(receipt['sse_rgb8'],0)

    def test_float_residual_and_cap_match_original_diagnostic(self):
        rng=np.random.default_rng(2);source=rng.integers(0,256,(7,9,3),dtype=np.uint8)
        unmarked=rng.random(source.shape).astype(np.float32)
        marked=np.clip(unmarked+rng.normal(0,.15,source.shape),0,1).astype(np.float32)
        result,receipt=expansion.source_bypass(source,unmarked,marked)
        expected,old=residual.cap(source,marked.astype(np.float64)-unmarked.astype(np.float64))
        np.testing.assert_array_equal(result,expected)
        self.assertEqual(receipt['weight'],old['weight']);self.assertEqual(receipt['iterations'],36)
        self.assertLessEqual(receipt['mse_rgb8'],receipt['budget_mse_rgb8'])
        self.assertGreater(residual.pixel_sse(source,residual.compose(source,marked.astype(np.float64)-unmarked.astype(np.float64),receipt['hi']))/source.size,receipt['budget_mse_rgb8'])

    def test_reject_nonfinite_and_malformed_composition(self):
        source=np.zeros((2,3,3),np.uint8)
        with self.assertRaises(ValueError):expansion.source_bypass(source,np.zeros(source.shape),np.full(source.shape,np.nan))
        with self.assertRaises(ValueError):expansion.source_bypass(source,np.zeros((2,2,3)),np.zeros((2,2,3)))

    def test_latent_ips_carrier_is_the_existing_function(self):
        import torch
        torch.manual_seed(7)
        latent=torch.randn(1,4,64,64,dtype=torch.float32)
        payload=phase.payload(phase.OWNERS[0])
        marked,receipt=phase.embed_latent(latent,payload,'IPS')
        self.assertEqual(receipt['direct_latent_readout']['bits'],payload)
        self.assertLess(receipt['inverse_imag_max_abs'],1e-5)
        self.assertEqual(marked.dtype,torch.float32)
        self.assertTrue(torch.equal(marked[:,:,:10,:],latent[:,:,:10,:]))

    def test_preflight_interruption_retains_all_planned_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);manifest=root/'manifest.json'
            manifest.write_text(json.dumps(expansion.configuration()),encoding='utf-8')
            output=root/'.thesis-build/dev-runs/fixture'
            with patch.object(expansion,'MAIN',root),patch.object(phase,'require_committed',side_effect=KeyboardInterrupt):
                self.assertEqual(expansion.run(manifest,output),1)
            record=json.loads((output/'run.json').read_text(encoding='utf-8'))
            self.assertEqual(record['outcome'],'interrupted')
            self.assertEqual(len(record['conditions']),40)
            self.assertTrue(all(r['outcome']=='not_completed_after_stop' for r in record['conditions']))
            self.assertIn('rows.jsonl',record['output_hashes'])
            self.assertFalse(list(output.glob('*.png')))


if __name__=='__main__':unittest.main()

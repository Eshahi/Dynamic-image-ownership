"""CPU-only synthetic spectral/metadata tests; no images, models or experiments."""
import ast
import copy
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import torch
from scripts import m1_phasemark as method
from scripts.m1_latent_reconstruction import quality


class PhaseMarkProtocol(unittest.TestCase):
    def test_preflight_failure_retains_manifest_and_fixed_denominator(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);manifest=root/'invalid.json'
            manifest.write_text(json.dumps({'data_split':'heldout'}),encoding='utf-8')
            output=root/'.thesis-build/dev-runs/preflight'
            with mock.patch.object(method,'MAIN',root),mock.patch.object(method.subprocess,'check_output',return_value='1'*40+'\n'):
                self.assertEqual(method.run(manifest,output),1)
                with self.assertRaises(FileExistsError):method.run(manifest,output)
            record=json.loads((output/'run.json').read_text(encoding='utf-8'))
            self.assertEqual(record['commit'],'1'*40)
            self.assertEqual(record['manifest_sha256'],method.sha(manifest))
            self.assertEqual((output/'manifest.json').read_bytes(),manifest.read_bytes())
            self.assertEqual(record['outcome'],'failed')
            self.assertEqual(len(record['conditions']),16)
            self.assertTrue(all(r['outcome']=='not_completed_after_stop' for r in record['conditions']))
            self.assertIn('traceback',record)
            self.assertEqual(len((output/'rows.jsonl').read_text().splitlines()),32)

    def test_exact_pinned_layout_greedy_nonoverlap_and_transpose_order(self):
        self.assertEqual(method.sha(method.UPSTREAM/'utils.py'),method.UPSTREAM_HASHES['utils.py'])
        # Execute only the inspected four pure scalar definitions. No upstream
        # imports, top-level initialization, tensor code or model code executes.
        tree=ast.parse((method.UPSTREAM/'utils.py').read_text(encoding='utf-8'))
        names={'in_mid_band','block_in_mid_band','blocks_overlap','get_bit_blocks'}
        body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
        class ScalarNP: sqrt=staticmethod(math.sqrt)
        namespace={'np':ScalarNP}
        exec(compile(ast.Module(body=body,type_ignores=[]),'isolated-pinned-scalar-layout','exec'),namespace)
        expected=namespace['get_bit_blocks']((22,22),num_bits=32,block_size=2,r_min=10,r_max=18,axis_offset=1)
        self.assertEqual(method.bit_blocks(),expected);self.assertEqual(len(expected),32)
        self.assertEqual(expected[:4],[(1,10,3,12),(10,1,12,3),(6,8,8,10),(8,6,10,8)])
        for i,a in enumerate(expected):
            for b in expected[i+1:]:self.assertFalse(method.overlap(a,b))
            conjugate={(44-x)%44 for x in range(a[0],a[2])}
            self.assertTrue(conjugate.isdisjoint({x for b in expected for x in range(b[0],b[2])}))

    def test_upstream_hermitian_exactness_and_real_inverse(self):
        tree=ast.parse((method.UPSTREAM/'utils.py').read_text(encoding='utf-8'))
        body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='enforce_hermitian_symmetry']
        namespace={'torch':torch}
        exec(compile(ast.Module(body=body,type_ignores=[]),'isolated-pinned-hermitian','exec'),namespace)
        generator=torch.Generator().manual_seed(20261003)
        freq=torch.complex(torch.randn(1,4,44,44,generator=generator),torch.randn(1,4,44,44,generator=generator))
        restored=method.hermitian_shifted(freq)
        self.assertTrue(torch.equal(restored,namespace['enforce_hermitian_symmetry'](freq)))
        self.assertTrue(torch.equal(restored[:,:,:,23:],freq[:,:,:,23:]))
        plain=torch.fft.ifftshift(restored,dim=(-2,-1));index=(-torch.arange(44))%44
        conjugate=plain.index_select(-2,index).index_select(-1,index).conj()
        self.assertTrue(torch.equal(plain,conjugate))
        self.assertLess(float(torch.fft.ifft2(plain).imag.abs().max()),1e-7)

    def test_all_payload_patterns_roundtrip_and_latent_exterior_unchanged(self):
        generator=torch.Generator().manual_seed(12345)
        latent=torch.randn(1,4,64,64,generator=generator)
        patterns=[[0]*128,[1]*128]+[method.payload(o) for o in method.OWNERS[:3]]
        exterior=torch.ones_like(latent,dtype=torch.bool);exterior[:,:,10:54,10:54]=False
        for arm in method.ARMS:
            for bits in patterns:
                with self.subTest(arm=arm,pattern=bits[:8]):
                    marked,receipt=method.embed_latent(latent,bits,arm)
                    self.assertEqual(method.extract_latent(marked,arm)['bits'],bits)
                    self.assertTrue(torch.equal(marked[exterior],latent[exterior]))
                    self.assertLess(receipt['inverse_imag_max_abs'],1e-6)
                    self.assertAlmostEqual(receipt['spectral_displacement_energy']/1936,
                        receipt['crop_displacement_energy'],delta=receipt['crop_displacement_energy']*1e-5)

    def test_magnitudes_and_ips_anchors_are_preserved_before_restoration(self):
        generator=torch.Generator().manual_seed(50)
        latent=torch.randn(44,44,generator=generator);freq=torch.fft.fft2(latent)
        for arm in method.ARMS:
            modified=method.modulate_fft(freq,method.payload(method.OWNERS[0])[:32],method.bit_blocks(),arm)
            self.assertTrue(torch.allclose(modified.abs(),freq.abs(),atol=1e-5,rtol=1e-6))
            if arm=='IPS':
                for x,y,xx,yy in method.bit_blocks():
                    self.assertTrue(torch.equal(modified[x:xx,y:yy].flatten()[[0,2]],freq[x:xx,y:yy].flatten()[[0,2]]))

    def test_phase_wrap_ties_and_zero_magnitude_native_bias_are_explicit(self):
        phases=torch.tensor([[math.pi-1e-5,-math.pi+1e-5],[-math.pi+1e-5,math.pi-1e-5]])
        freq=torch.exp(1j*phases)
        result=method.read_fft(freq,[(0,0,2,2)],'IPS')
        self.assertEqual(result['bits'],[1]);self.assertAlmostEqual(result['scores'][0],2,places=5)
        phases=torch.tensor([[math.pi/2,-math.pi/2],[math.pi/2,-math.pi/2]])
        self.assertEqual(method.read_fft(torch.exp(1j*phases),[(0,0,2,2)],'APM')['bits'],[0])
        zero=torch.zeros(2,2,dtype=torch.complex64)
        self.assertEqual(method.read_fft(zero,[(0,0,2,2)],'APM')['bits'],[0])
        ips=method.read_fft(zero,[(0,0,2,2)],'IPS')
        self.assertEqual(ips['bits'],[1]);self.assertEqual(ips['scores'],[2.])
        self.assertEqual(ips['zero_magnitude_coefficients_per_block'],[4])

    def test_correct_integer_tail_boundary(self):
        for alpha,k in ((.01,78),(.0025,81),(.00125,82)):
            self.assertEqual(method.integer_cutoff(alpha),k)
            self.assertLessEqual(method.fair_tail(k),alpha)
            self.assertGreater(method.fair_tail(k-1),alpha)
        self.assertGreater(method.fair_tail(77),.01)

    def test_float_psnr_does_not_use_uint8_wrapped_error(self):
        import numpy as np
        left=np.zeros((512,512,3),dtype=np.uint8);right=np.full_like(left,255)
        measured=quality(left,right)
        self.assertEqual(measured['mse_rgb8'],65025)
        self.assertEqual(measured['psnr_db'],0.)
        self.assertEqual(float(((left-right)**2).mean()),1.)

    def test_manifest_locks_all_two_sources_arms_owners_and_mask(self):
        manifest=json.loads((method.ROOT/'research/m1-phasemark-dev.json').read_text(encoding='utf-8'))
        self.assertEqual([c['id'] for c in method.validate(manifest)],[1675,4795])
        self.assertEqual(len(method.planned()),16)
        for changed in ('heldout','case','arm','threshold','mask','payload'):
            m=copy.deepcopy(manifest)
            if changed=='heldout':m['data_split']='heldout'
            elif changed=='case':m['cases']=m['cases'][:1]
            elif changed=='arm':m['config']['arms']=['APM']
            elif changed=='threshold':m['config']['presence_matches']=81
            elif changed=='mask':m['rectangles'][0][0]+=1
            else:m['payloads'][method.OWNERS[0]][0]^=1
            with self.subTest(changed=changed),self.assertRaises(ValueError):method.validate(m)

if __name__=='__main__':unittest.main()

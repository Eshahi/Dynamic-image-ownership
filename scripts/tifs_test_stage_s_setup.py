"""Pure stdlib safety tests for the deferred Linux setup."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('setup',Path(__file__).with_name('tifs_stage_s_setup.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)


class SetupTests(unittest.TestCase):
    def test_safe_relative_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(s.safe_path(tmp,'wam/source/file.py'),Path(tmp).resolve()/'wam/source/file.py')
            for path in ('../escape','/escape','C:/escape','a\\b','a/../b','a//b','./a','a/./b',''):
                with self.subTest(path=path),self.assertRaises(ValueError): s.safe_path(tmp,path)

    def test_filter_preserves_exact_records(self):
        original=s.common.load_json(s.ROOT/'research/encoder-transfer-20261019/stage2b-asset-plan.json')
        selected=s.common.load_json(s.HERE/'asset-plan.json')
        self.assertEqual(s.selected_files(original),selected['files'])
        self.assertEqual(sum(r['size_bytes'] for r in selected['files']),48597702199)
        self.assertFalse(any('trustmark' in r['path'] or 'videoseal' in r['path'] for r in selected['files']))
        self.assertEqual(selected['vine_revision'],'d72f11a93f8de9bc45ef61202b9c8dda2a70cc77')

    def test_pins_unchanged(self):
        config=s.common.load_json(s.ROOT/'research/encoder-transfer-20261019/stage2b-config.json')
        requirements=(s.HERE/'requirements.txt').read_text()
        s.validate_pins(requirements,config)
        with self.assertRaises(ValueError): s.validate_pins(requirements.replace('torch==2.7.1+cu128','torch==2.7.1'),config)
        with self.assertRaises(ValueError): s.validate_pins(requirements.replace(s.CLIP_REVISION,'main'),config)

    def test_hash_and_size_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'file';p.write_bytes(b'abc')
            spec=dict(size_bytes=3,sha256=s.common.sha256_file(p))
            s.verify_file(p,spec)
            p.write_bytes(b'xyz')
            with self.assertRaises(ValueError): s.verify_file(p,spec)
            p.write_bytes(b'a')
            with self.assertRaises(ValueError): s.verify_file(p,spec)

    def test_deadline_preserves_setup_and_retrieval(self):
        now=1767225600 # 2026-01-01T00:00:00Z
        clock=[now+120]
        d=s.Deadline('2026-01-01T00:00:00Z',lambda:clock[0])
        self.assertEqual(d.timeout(),54000-3630-120)
        self.assertEqual(d.timeout(30),30)
        clock[0]=now+54000-3630
        with self.assertRaises(s.common.ResourceStop): d.timeout()
        with self.assertRaises(ValueError): s.Deadline('2026-01-01T00:00:00',lambda:now)
        with self.assertRaises(ValueError): s.Deadline('2026-01-02T00:00:00Z',lambda:now)

    def test_canonical_sources_never_acquired(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest=s.common.load_json(s.HERE/'source-manifest.json')
            with self.assertRaisesRegex(ValueError,'Supply unchanged canonical source'):s.verify_sources(Path(tmp),manifest)
            self.assertEqual(list(Path(tmp).iterdir()),[])

    def test_existing_mismatch_no_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'wam').mkdir();(root/'wam/file').write_bytes(b'bad')
            spec=dict(path='wam/file',size_bytes=4,sha256='0'*64,url='https://invalid.invalid',license='test')
            with self.assertRaises(ValueError):s.fetch(spec,root,None,[])


if __name__=='__main__':unittest.main()

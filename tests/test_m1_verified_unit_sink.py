from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from m1_verified_unit_sink import VerifiedUnitSink


class VerifiedSinkTests(unittest.TestCase):
    def test_image_reloads_identical_and_overwrite_denied(self):
        with tempfile.TemporaryDirectory() as temporary:
            sink=VerifiedUnitSink(temporary,allowed_root=temporary)
            image=np.full((512,512,3),129,dtype=np.uint8)
            saved,receipt=sink.save_image('C1-clean',image)
            np.testing.assert_array_equal(saved,image)
            self.assertEqual(receipt['sha256'],sink._receipt(receipt['path'])['sha256'])
            with self.assertRaises(ValueError):sink.save_image('C1-clean',image)
            with self.assertRaises(ValueError):sink.save_image('../escape',image)
    def test_scope_and_explicit_legacy_layout(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'owned';root.mkdir()
            with self.assertRaises(ValueError):VerifiedUnitSink(temporary,allowed_root=root)
            sink=VerifiedUnitSink(root,allowed_root=root,stage_layout='generated-hwc-float64')
            value=np.arange(3*512*512,dtype=np.float32).reshape(1,3,512,512)
            receipt=sink.save_array('reference',value)
            saved=np.load(receipt['path'],allow_pickle=False)
            self.assertEqual(saved.dtype,np.float64)
            np.testing.assert_array_equal(saved,value[0].transpose(1,2,0).astype(np.float64))
            with self.assertRaises(ValueError):sink.save_array('decoded',saved)
    def test_native_shape_and_reader_filename(self):
        with tempfile.TemporaryDirectory() as temporary:
            sink=VerifiedUnitSink(temporary,allowed_root=temporary)
            value=np.zeros((1,3,512,512),dtype=np.float32)
            receipt=sink.save_array('reference',value)
            self.assertEqual(np.load(receipt['path'],allow_pickle=False).shape,value.shape)
            receipt=sink.save_array('C0-clean-z',np.zeros(16384,dtype=np.float64))
            self.assertEqual(Path(receipt['path']).name,'C0-clean-reader.npy')
    def test_checkpoint_seal_and_observer_order_cpu(self):
        import torch
        with tempfile.TemporaryDirectory() as temporary:
            events=[];sink=VerifiedUnitSink(temporary,allowed_root=temporary,
                before_checkpoint=lambda value:events.append('before'),
                checkpoint_observer=lambda value,receipt:events.append(('after',Path(receipt['path']).is_file())))
            value={'phase':'initialization','step':10,'tensor':torch.tensor([1.])}
            receipt=sink.save_checkpoint('initialization-010',value)
            self.assertEqual(events,['before',('after',True)])
            self.assertTrue(torch.equal(torch.load(receipt['path'],weights_only=True)['tensor'],value['tensor']))
    def test_save_failure_retains_partial_without_completed_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            sink=VerifiedUnitSink(temporary,allowed_root=temporary);target=Path(temporary)/'bad.bin'
            def fail(stream):stream.write(b'partial');raise OSError('storage pressure')
            with self.assertRaises(OSError):sink._write(target,fail)
            self.assertFalse(target.exists());self.assertEqual(target.with_name('bad.bin.partial').read_bytes(),b'partial')


if __name__=='__main__':unittest.main()

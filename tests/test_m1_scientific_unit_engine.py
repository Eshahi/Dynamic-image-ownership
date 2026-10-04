import hashlib
from pathlib import Path
import sys
import types
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import m1_scientific_unit_engine as engine


class Sink:
    def __init__(self):self.events=[];self.corrupt=False
    def receipt(self,value):return {'sha256':hashlib.sha256(value).hexdigest()}
    def save_image(self,name,rgb):
        self.events.append(('image',name));saved=rgb.copy()
        if self.corrupt:saved[0,0,0]^=1
        return saved,self.receipt(rgb.tobytes())
    def save_array(self,name,array):self.events.append(('array',name));return self.receipt(array.tobytes())
    def save_checkpoint(self,name,value):self.events.append(('checkpoint',name));return self.receipt(name.encode())


class Context:
    def __init__(self,sink):
        self.sink=sink;self.calls=[]
        self.adapter=types.SimpleNamespace(initialize=self.initialize,embed=self.embed,
            public=types.SimpleNamespace(observations=lambda rgb:(np.ones(512),11,np.zeros(16384))))
    def place_inference(self,device):self.calls.append(('place',device))
    def initialize(self,rgb,identity,owner,**kwargs):
        self.calls.append(('initialize',owner,kwargs['stop_step'],kwargs['resume']))
        value=dict(phase='initialization',step=kwargs['stop_step'],binding=dict(source_identity=identity,owner=owner,source_uid=kwargs['source_uid']))
        kwargs['on_checkpoint'](value);return value
    def embed(self,rgb,initializer,**kwargs):
        self.calls.append(('embed',kwargs['stop_step'],kwargs['resume']))
        value=dict(phase='embedding',step=kwargs['stop_step']);kwargs['on_checkpoint'](value)
        result=dict(completed=kwargs['stop_step']==100,checkpoint=value)
        if result['completed']:
            arrays={name:np.full((1,3,512,512),.25,dtype=np.float32) for name in ('reference','decoded','residual','surrogate')}
            result.update(core_result=arrays,marked_rgb8=np.full_like(rgb,2),cap=dict(alpha=.1))
        return result
    def quality(self,a,b):return dict(psnr_db=None,psnr_infinite=True,ssim_rgb=1.,lpips=0.)
    def safety_check(self,rgb):return dict(nsfw=False)
    def readout(self,rgb,owner):
        if not any(event[0]=='image' for event in self.sink.events):raise RuntimeError('Read before persist')
        self.calls.append(('read',owner));return dict(s_s=1.,s_i=2.,state='uncertain')


class UnitEngineTests(unittest.TestCase):
    def setUp(self):
        self.rgb=np.zeros((512,512,3),dtype=np.uint8);self.sink=Sink();self.context=Context(self.sink)
        self.runner=engine.UnitEngine(self.context,self.sink)
        from m1_blind_noise_core import OWNERS
        self.owner=OWNERS[0]
        self.identity=dict(source_id='fixture:candidate-0',source_rgb8_sha256=engine.operations.pixel_sha(self.rgb),data_split='synthetic',generator_seed=0)
    def test_single_prefix_full_resume_path(self):
        prefix=self.runner.initialize(self.rgb,self.identity,mode='generated',owner=self.owner,stop_step=100)
        full=self.runner.initialize(self.rgb,self.identity,mode='generated',owner=self.owner,resume=prefix)
        partial=self.runner.enroll(self.rgb,self.identity,full,mode='generated',owner=self.owner,stop_step=10)
        self.assertFalse(partial['completed'])
        result=self.runner.enroll(self.rgb,self.identity,full,mode='generated',owner=self.owner,resume=partial['checkpoint'])
        self.assertTrue(result['completed']);self.assertEqual(set(result['images']),{'C0-source','C0-reconstruction','C1'})
        self.assertTrue((result['images']['C0-reconstruction']['rgb8']==64).all())
        self.assertTrue((result['images']['C0-source']['rgb8']==0).all())
        self.assertEqual(self.context.calls[3][-1],prefix)
        self.assertFalse(any(call[0]=='read' for call in self.context.calls))
    def test_scientific_schedule_and_generated_modes_do_not_cross(self):
        uid='MS-COCO:fixture-only';schedule=dict(engine.owners.source_schedule(uid),source_uid=uid,group_id='g')
        identity=dict(source_id=uid,source_uid=uid,group_id='g',data_split='test',source_rgb8_sha256=engine.operations.pixel_sha(self.rgb))
        self.runner.initialize(self.rgb,identity,mode='scientific',schedule=schedule)
        with self.assertRaises(ValueError):self.runner.initialize(self.rgb,identity,mode='generated',owner=self.owner)
        with self.assertRaises(ValueError):self.runner.initialize(self.rgb,self.identity,mode='generated',owner=self.owner,schedule=schedule)
        schedule['seed_uint64_decimal']='0'
        with self.assertRaises(ValueError):self.runner.initialize(self.rgb,identity,mode='scientific',schedule=schedule)
    def test_saved_bytes_integrity_before_detector(self):
        self.sink.corrupt=True
        with self.assertRaises(ValueError):self.runner.assess_image('clean',self.rgb,source_rgb8=self.rgb,matched_clean_rgb8=self.rgb,claims=[self.owner],mode='generated')
        self.assertFalse(any(call[0]=='read' for call in self.context.calls))
    def test_saved_reader_stage_arrays_and_claims(self):
        result=self.runner.assess_image('clean',self.rgb,source_rgb8=self.rgb,matched_clean_rgb8=self.rgb,claims=[self.owner],mode='generated')
        self.assertEqual(set(result['reader_arrays']),{'E','z'});self.assertEqual(result['suspect_H'],11)
        self.assertEqual(result['queries'][0]['owner'],self.owner)
        with self.assertRaises(ValueError):self.runner.assess_image('clean',self.rgb,source_rgb8=self.rgb,matched_clean_rgb8=self.rgb,claims=[self.owner,self.owner],mode='generated')
    def test_failed_attack_retains_failure_and_propagates_descendants(self):
        def failed():raise engine.operations.OperationFailure('blocked',dict(safety_verdict=[True]))
        result=self.runner.attack('attack',failed,source_rgb8=self.rgb,matched_clean_rgb8=self.rgb,claims=[self.owner],mode='generated')
        self.assertEqual(result['outcome'],'execution_failed');self.assertEqual(result['operator_receipt']['safety_verdict'],[True])
        rows=[dict(id='attack',dependencies=[],outcome='execution_failed'),dict(id='query',dependencies=['attack'],outcome='planned'),dict(id='summary',dependencies=['query'],outcome='planned')]
        propagated=engine.propagate_missing(rows,['attack'])
        self.assertEqual(propagated[2]['outcome'],'missing_dependency');self.assertEqual(rows[2]['outcome'],'planned')
        rows[1]['outcome']='completed'
        with self.assertRaises(ValueError):engine.propagate_missing(rows,['attack'])
    def test_initialization_wrong_source_rejected(self):
        initial=self.runner.initialize(self.rgb,self.identity,mode='generated',owner=self.owner)
        initial['binding']['owner']='foreign'
        with self.assertRaises(ValueError):self.runner.enroll(self.rgb,self.identity,initial,mode='generated',owner=self.owner)
    def test_clean_control_roster_is_explicit(self):
        initial=self.runner.initialize(self.rgb,self.identity,mode='generated',owner=self.owner)
        enrollment=self.runner.enroll(self.rgb,self.identity,initial,mode='generated',owner=self.owner)
        clean=self.runner.clean(enrollment,claims_by_control={'C0-source':[self.owner],'C1':[self.owner]},mode='generated')
        self.assertEqual(set(clean),{'C0-source','C1'})
        self.assertNotIn('C0-reconstruction',clean)
        self.assertEqual(len(clean['C1']['queries']),1)
    def test_budget_stop_propagates_and_retains_stopped_unit_event(self):
        events=[];runner=engine.UnitEngine(self.context,self.sink,event=events.append)
        def stop():raise TimeoutError('bounded deadline')
        with self.assertRaises(TimeoutError):runner.attack('attack',stop)
        self.assertEqual(events[0]['unit']['id'],'attack')
        self.assertEqual(events[0]['kind'],'unit_stopped')
    def test_query_metadata_join_and_normalized_decision(self):
        image=dict(id='image',kind='image',source_uid='fixture:candidate-0',group_id='g',method='candidate')
        query=dict(image,id='query',kind='query',dependencies=['image'],owner=self.owner)
        result=self.runner.assess_image('image',self.rgb,source_rgb8=self.rgb,matched_clean_rgb8=self.rgb,
            claims=[self.owner],mode='generated',image_unit=image,query_units=[query])
        self.assertEqual(result['queries'][0]['id'],'query')
        self.assertEqual(result['queries'][0]['outcome'],'completed')
        self.assertEqual(result['queries'][0]['upstream_image_id'],'image')
        query['group_id']='wrong'
        with self.assertRaises(ValueError):self.runner.assess_image('image',self.rgb,source_rgb8=self.rgb,matched_clean_rgb8=self.rgb,
            claims=[self.owner],mode='generated',image_unit=image,query_units=[query])


if __name__=='__main__':unittest.main()

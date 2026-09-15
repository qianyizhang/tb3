"""Admit one declared synthetic grouping probe, not an omission detector."""
import copy
import gzip
import json
import shutil
import sys
import tarfile
from common import ROOT,OUT,write,sha,freeze_task
sys.path.insert(0,str(ROOT/'probes/revisions/br013/authoring'))
from scoring import score

def main():
    screen=json.loads((OUT/'author/component-screen.json').read_text())
    v=next(v for v in screen['variants'] if v['gap_mm']==6)
    assert v['minimum_target_fragment_ml']>20
    assert all(len(s)==1 for c in v['cuts'] for s in c['components26'])
    task=OUT/'tasks/abdomen-f01';assert not task.exists()
    source=ROOT/'runs/br013-abdomen/tasks/abdomen-a01';shutil.copytree(source,task)
    data=OUT/'build/abdomen-f01';shutil.copytree(ROOT/v['data_path'],data)
    truth={r['object_id']:r['label'] for r in v['lineage']};key={'mode':'recognition','truth':truth}
    assert len(truth)==15 and len(set(truth.values()))==13
    write(task/'tests/expected.json',key)
    oracle={'assignments':[{'object_id':k,'label':val} for k,val in truth.items()]}
    write(task/'solution/answer.json',oracle)
    inst=(task/'instruction.md').read_text()
    inst=inst.replace('# Identify abdominal structures in a 3-D scene','# Identify fragmented abdominal structures in a 3-D scene')
    inst=inst.replace('The anonymous objects retain their original physical shape, scale, relative position and patient orientation.',
                      'Some supplied objects are separated fragments of a single organ mask, with unrepresented tissue between fragments. All retained voxels preserve their physical scale, relative position and patient orientation.')
    inst=inst.replace('Each label may be used at most once; some vocabulary labels may have no supplied object. Missing vocabulary labels do not imply a missing annotation or disease.',
                      'The vocabulary lists exactly the anatomical classes represented. Each class occurs in at least one object; the same label may belong to multiple objects. Assign a class to each supplied fragment or whole object; the number of fragments per class is not specified.')
    inst=inst.replace('Identify the supplied objects; do not repair their contours or diagnose the patient.',
                      'Identify the supplied objects. Do not reconstruct missing tissue, identify the cause of gaps, repair contours, or diagnose the patient. Each object belongs to one anatomical class, even if its shape represents only part of that structure.')
    assert 'Each label may be used at most once' not in inst
    (task/'instruction.md').write_text(inst)
    (task/'task.toml').write_text((task/'task.toml').read_text().replace('terminal-bench/abdomen-a01','terminal-bench/abdomen-f01'))
    notice=(task/'environment/SOURCE_NOTICE.md').read_text()
    notice+='For this synthetic identity-grouping probe, two source organs were partitioned into substantial fragments with a connecting band removed. Retained voxel coordinates are unchanged. Cut surfaces are artificial; this is not a clinically validated omission pattern.\n'
    (task/'environment/SOURCE_NOTICE.md').write_text(notice)
    with (task/'environment/data.tar.gz').open('wb') as f:
        with gzip.GzipFile(fileobj=f,filename='',mode='wb',mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode='w') as tar:
                for p in sorted(data.iterdir()):
                    i=tar.gettarinfo(str(p),p.name);i.uid=i.gid=0;i.uname=i.gname='';i.mtime=0
                    with p.open('rb') as content:tar.addfile(i,content)
    rows=oracle['assignments'];wrong=copy.deepcopy(oracle);wrong['assignments'][0]['label']='not-a-label'
    probes=[('oracle',oracle,True),('order_invariant',{'assignments':rows[::-1]},True),
            ('empty',{'assignments':[]},False),('missing_piece',{'assignments':rows[1:]},False),
            ('duplicate_piece',{'assignments':rows+[rows[0]]},False),('wrong_class',wrong,False),
            ('extra_piece',{'assignments':rows+[{'object_id':'extra','label':'pancreas'}]},False),
            ('malformed',{'assignments':'invalid'},False)]
    # Include a plausible whole-class switch, not just invalid vocabulary.
    swapped=copy.deepcopy(oracle)
    for row in swapped['assignments']:
        if row['label']=='pancreas':row['label']='duodenum'
        elif row['label']=='duodenum':row['label']='pancreas'
    probes.append(('pancreas_duodenum_switch',swapped,False))
    controls=[{'name':n,'expected':e,'grade':score(a,key)} for n,a,e in probes]
    assert all(c['expected']==c['grade']['passed'] for c in controls)
    write(OUT/'author/fragment-controls.json',controls)
    freeze_task(task,{'case':28,'mode':'recognition','object_count':15,'class_count':13,
                      'source_task':'BR013-A01 ordinary calibration','gap_mm':6,'cuts':v['cuts'],
                      'nearest_surface_pairs_correct':v['nearest_pairs_correct'],'identity_controls':controls,
                      'screen_sha256':sha(OUT/'author/component-screen.json'),
                      'admission':'Diagnostic synthetic grouping pilot; substantial connected pieces, exact retained-voxel lineage. Not clinical omission detection or a certified hard task. Planar cut cues remain available.'})
    print('F01 frozen: 15 objects, 13 classes; 4 large fragments; 9 scoring controls pass.')

if __name__=='__main__':main()

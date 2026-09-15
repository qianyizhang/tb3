"""Export unchanged original masks into three frozen abdominal pilot tasks."""
import copy
import json
import shutil
import tarfile
from pathlib import Path
import numpy as np
import nibabel as nib
from screen import ROOT,OUT,CASES,LABELS,write,sha,world
from scoring import score
from inspect_scene import load_scene,render

HERE=Path(__file__).resolve().parent
PLAN=[('abdomen-a01',28,'recognition'),('abdomen-a02',83,'recognition'),('abdomen-a03',83,'audit')]

def surface(mask):
    inner=np.zeros_like(mask)
    inner[1:-1,1:-1,1:-1]=(mask[1:-1,1:-1,1:-1]&mask[:-2,1:-1,1:-1]&mask[2:,1:-1,1:-1]
        &mask[1:-1,:-2,1:-1]&mask[1:-1,2:,1:-1]&mask[1:-1,1:-1,:-2]&mask[1:-1,1:-1,2:])
    return np.argwhere(mask&~inner)

def main():
    assert not (OUT/'freeze.json').exists(),'Never overwrite a frozen trial'
    records=[];checks=[]
    for name,case,mode in PLAN:
        task=OUT/'tasks'/name;data=OUT/'build'/name
        for sub in ['environment','tests','solution']: (task/sub).mkdir(parents=True,exist_ok=True)
        data.mkdir(parents=True,exist_ok=True)
        truth={};objects=[];rng=np.random.default_rng(2026091500+case)
        order=rng.permutation(LABELS).tolist();ids=rng.choice(np.arange(100,1000),len(order),replace=False)
        for i,(label,code) in enumerate(zip(order,ids)):
            source=ROOT/'runs/br004-v1/source'/CASES[case]/'segmentations'/f'{label}.nii.gz'
            im=nib.load(source);original=np.asarray(im.dataobj,dtype=bool)
            p=np.argwhere(original)
            if not len(p):continue
            lo=p.min(0);hi=p.max(0)+1
            mask=original[tuple(slice(a,b) for a,b in zip(lo,hi))]
            a=np.diag([-1.,-1.,1.,1.])@im.affine
            crop_a=a.copy();crop_a[:3,3]=world(lo[None,:],a)[0]
            oid=f'o{code}';filename=f'{oid}.npz'
            points=world(surface(mask),crop_a).astype('float32')
            np.savez_compressed(data/filename,mask=mask,affine_lps=crop_a,surface_lps=points)
            # Per-object files preserve overlaps; no priority merging of masks.
            with np.load(data/filename) as z:
                assert np.array_equal(z['mask'],mask)
                assert np.array_equal(np.argwhere(z['mask'])+lo,p)
                assert np.allclose(world(np.argwhere(z['mask']),z['affine_lps']),world(p,a),atol=1e-8,rtol=0)
                assert np.allclose(z['surface_lps'],world(surface(mask),crop_a),atol=0.0001,rtol=0)
            truth[oid]=label;objects.append({'object_id':oid,'file':filename,'color_index':i})
        write(data/'scene.json',{'coordinates':'LPS millimetres: +x left, +y posterior, +z superior','objects':objects})
        write(data/'vocabulary.json',sorted(LABELS))
        key={'mode':mode,'truth':truth}
        field='assignments' if mode=='recognition' else 'corrections'
        if mode=='audit':
            proposed={k:('duodenum' if v=='pancreas' else 'pancreas' if v=='duodenum' else v) for k,v in truth.items()}
            key['proposed']=proposed
            write(data/'proposed.json',{'assignments':[{'object_id':k,'label':v} for k,v in proposed.items()]})
            wanted={k:v for k,v in truth.items() if proposed[k]!=v}
        else:wanted=truth
        oracle={field:[{'object_id':k,'label':v} for k,v in wanted.items()]}
        write(task/'tests/expected.json',key);write(task/'solution/answer.json',oracle)
        write(task/'environment/answer.json',{field:[]})
        render(load_scene(data),data/'overview.png')
        # Explicit filenames, generic IDs, deterministic archive metadata, no CT/key.
        with tarfile.open(task/'environment/data.tar.gz','w:gz') as tar:
            for p in sorted(data.iterdir()):
                info=tar.gettarinfo(str(p),p.name);info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
                with p.open('rb') as f:tar.addfile(info,f)
        env=task/'environment'
        shutil.copyfile(HERE/'inspect_scene.py',env/'inspect_scene.py')
        license_dir=ROOT/'runs/br004-v1/task-snapshot/dicom-anatomy-audit/environment'
        for fn in ['DATA-LICENSE.txt','LABEL-LICENSE.txt']:shutil.copyfile(license_dir/fn,env/fn)
        (env/'SOURCE_NOTICE.md').write_text('Derived from TotalSegmentator small v2.0.1, Wasserthal / University Hospital Basel.\nhttps://zenodo.org/records/10047263\nData CC BY 4.0; taxonomy Apache 2.0. Original 1.5 mm binary masks are cropped losslessly to nonzero bounds; affine preserves shared physical positions. Anonymous IDs and label-free surface rendering added. No intensities supplied.\n')
        (env/'Dockerfile').write_text('FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir numpy==2.2.6 pillow==11.3.0\nWORKDIR /app\nADD data.tar.gz /app/data/\nCOPY answer.json /app/answer/answer.json\nCOPY inspect_scene.py SOURCE_NOTICE.md DATA-LICENSE.txt LABEL-LICENSE.txt /app/\n')
        action=('Assign an anatomical identity to every supplied object.' if mode=='recognition' else
                'Audit the proposed anatomical identities in /app/data/proposed.json. Return only objects whose proposed identity is incorrect, with the correct identity. The number of errors is not specified.')
        instruction=f'''# Identify abdominal structures in a 3-D scene

{action}

The anonymous objects retain their original physical shape, scale, relative position and patient orientation. Use labels exactly as spelled in /app/data/vocabulary.json. Each label may be used at most once; some vocabulary labels may have no supplied object. Missing vocabulary labels do not imply a missing annotation or disease. Objects are not guaranteed to have textbook shapes. Identify the supplied objects; do not repair their contours or diagnose the patient.

Write /app/answer/answer.json as {{"{field}":[{{"object_id":"o123","label":"label_name"}}]}}. {'Include every object exactly once.' if mode=='recognition' else 'Include each corrected object once and omit unchanged objects.'} Do not add prose fields. The labels aorta and inferior_vena_cava denote their entire supplied vascular masks, which can extend beyond the abdomen. portal_vein_and_splenic_vein is one combined vascular object.

## Available data and tools

Start with /app/data/overview.png, /app/data/scene.json and the vocabulary. Each object NPZ contains a lossless cropped binary mask, affine_lps mapping its [i,j,k,1] voxel indices to physical LPS millimetres, and surface_lps containing boundary voxel centres. Positive x is patient-left, y posterior, z superior. Files use independent masks so overlaps are preserved. The mask is authoritative; the point rendering is a preview. No CT images are supplied.

Python, NumPy and Pillow are installed. /app/inspect_scene.py provides load_scene() for programmatic access and ready rendering/statistics:

```sh
python /app/inspect_scene.py
python /app/inspect_scene.py --out /app/scene.png
python /app/inspect_scene.py --objects o123,o456 --yaw 75 --pitch 20 --out /app/focus.png
```

Use actual IDs from scene.json in the last command. A subset automatically fits the displayed objects to the view, making small structures inspectable. You may use other tools or calculations. Decide identities from the supplied anatomy; no external patient/source matching is needed. Source attribution and licenses are in /app/SOURCE_NOTICE.md.
'''
        (task/'instruction.md').write_text(instruction)
        (task/'task.toml').write_text(f'''artifacts = ["/app/answer"]
[task]
name = "terminal-bench/{name}"
description = "Infer or audit anatomical identities from intact anonymous 3-D masks."
authors = [{{name = "Interview research pilot"}}]
[metadata]
author_name = "Interview research pilot"
author_email = "probe@example.invalid"
category = "Data Science"
tags = ["anatomy", "3d", "identity"]
expert_time_estimate_hours = 0.25
[verifier]
timeout_sec = 120.0
environment_mode = "separate"
[agent]
timeout_sec = 1800.0
[environment]
build_timeout_sec = 600.0
cpus = 4
memory_mb = 4096
storage_mb = 10240
gpus = 0
network_mode = "public"
''')
        shutil.copyfile(HERE/'scoring.py',task/'tests/scoring.py')
        (task/'tests/verifier.py').write_text('''import json,time
from pathlib import Path
from scoring import score,read_json
start=time.monotonic();out=Path('/logs/verifier');out.mkdir(parents=True,exist_ok=True)
(out/'reward.txt').write_text('0\\n')
try: result=score(read_json(Path('/app/answer/answer.json')),read_json(Path('/verifier/expected.json')))
except Exception as e: result={'passed':False,'error':str(e)}
result['grading_seconds']=time.monotonic()-start
(out/'details.json').write_text(json.dumps(result,indent=2)+'\\n')
(out/'reward.txt').write_text('1\\n' if result['passed'] else '0\\n')
print(json.dumps(result))
''')
        (task/'tests/Dockerfile').write_text('FROM python:3.12-slim-bookworm\nCOPY verifier.py scoring.py expected.json /verifier/\nCOPY test.sh /tests/test.sh\nRUN chmod 755 /tests/test.sh && mkdir -p /app/answer\nWORKDIR /app\nCMD ["/tests/test.sh"]\n')
        (task/'tests/test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/verifier.py\n')
        (task/'solution/solve.sh').write_text('#!/bin/sh\nset -eu\ncp /solution/answer.json /app/answer/answer.json\n')
        # Oracle and deliberately wrong outputs exercise requirements, not visual semantics.
        rows=oracle[field]
        wrong=copy.deepcopy(oracle);wrong[field][0]['label']='wrong'
        controls=[('oracle',oracle,True),('reordered',{field:rows[::-1]},True),('empty',{field:[]},False),
                  ('missing',{field:rows[1:]},False),('duplicate',{field:rows+[rows[0]]},False),
                  ('extra',{field:rows+[{'object_id':'unknown','label':'liver'}]},False),('wrong',wrong,False),
                  ('malformed',{field:None},False)]
        if mode=='audit':
            unchanged=next(k for k in truth if k not in wanted)
            controls.append(('unnecessary_repair',{field:rows+[{'object_id':unchanged,'label':truth[unchanged]}]},False))
        grades=[{'name':n,'expected':e,'grade':score(a,key)} for n,a,e in controls]
        assert all(x['expected']==x['grade']['passed'] for x in grades)
        checks.append({'task':name,'checks':grades})
        records.append({'task':name,'case':case,'source_patient':CASES[case],'mode':mode,'object_count':len(objects),
                        'task_path':str(task.relative_to(ROOT)),'roundtrip_all_voxels_exact':True,
                        'files':{str(p.relative_to(task)):sha(p) for p in sorted(task.rglob('*')) if p.is_file()}})
    # Matched recognition/audit use byte-identical object data and scene/vocabulary.
    a=OUT/'build/abdomen-a02';b=OUT/'build/abdomen-a03'
    assert all(sha(p)==sha(b/p.name) for p in a.iterdir())
    freeze={'round':'BR-013','tasks':records,'controls':checks,'paired_geometry_byte_identical':True,
            'authoring_files':{p.name:sha(p) for p in sorted(HERE.glob('*.py'))},
            'screen_sha256':sha(OUT/'author/screen.json'),
            'source_review_sha256':sha(OUT/'author/source-review.json'),
            'protocol':'One Sol/xhigh attempt per task in A01,A02,A03 order, 1800 seconds, no retries. Terra/max only on reviewed valid Sol failure. A01 is easy calibration, A02/A03 are hypotheses not certified difficult tasks.'}
    write(OUT/'freeze.json',freeze);write(ROOT/'docs/evidence/br013-freeze.json',freeze)
    print(json.dumps({'tasks':[(r['task'],r['object_count']) for r in records],'checks':sum(len(r['checks']) for r in checks)}))

if __name__=='__main__':main()

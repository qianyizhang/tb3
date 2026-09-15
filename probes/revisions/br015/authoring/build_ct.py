"""Freeze CT-supported recognition while preserving the previous hard geometry."""
import gzip
import json
import shutil
import sys
import tarfile
import time
import nibabel as nib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from common import ROOT,OUT,sha,write,freeze_task
sys.path.insert(0,str(ROOT/'probes/revisions/br013/authoring'))
from inspect_scene import load_scene
from inspect_ct import transform,sample,bounds,render_slice,contact_sheet,PLANES

def main():
    started=time.monotonic();name='abdomen-c01'
    old=json.loads((ROOT/'docs/evidence/br013-freeze.json').read_text())
    t=next(t for t in old['tasks'] if t['task']=='abdomen-a02');source=ROOT/t['task_path']
    assert all(sha(source/p)==v for p,v in t['files'].items())
    task=OUT/'tasks'/name;assert not task.exists();shutil.copytree(source,task)
    data=OUT/'build'/name;shutil.copytree(ROOT/'runs/br013-abdomen/build/abdomen-a02',data)
    source_ct=ROOT/'runs/br004-v1/source/s0629/ct.nii.gz'
    receipt=json.loads((source_ct.parent/'source-receipt.json').read_text())
    assert sha(source_ct)==next(r['sha256'] for r in receipt['files'] if r['member'].endswith('/ct.nii.gz'))
    im=nib.load(source_ct);ct=np.asarray(im.dataobj);assert ct.dtype==np.int16
    a=np.diag([-1.,-1.,1.,1.])@im.affine
    np.savez_compressed(data/'ct.npz',hu=ct,affine_lps=a)
    with np.load(data/'ct.npz') as z:assert np.array_equal(z['hu'],ct) and np.array_equal(z['affine_lps'],a)
    objects=load_scene(data);rng=np.random.default_rng(1501);checks=[]
    for o in objects:
        vox=np.argwhere(o['mask']);vox=vox[rng.choice(len(vox),min(1000,len(vox)),replace=False)]
        q=transform(vox,o['affine_lps']);ijk=np.rint(transform(q,np.linalg.inv(a))).astype(int)
        assert np.max(np.abs(transform(ijk,a)-q))<1e-5
        assert np.array_equal(sample(ct,a,q,-1024),ct[tuple(ijk.T)])
        checks.append({'object_id':o['object_id'],'ct_grid_roundtrip_samples':len(vox)})
    contact_sheet(ct,a,objects,data/'ct-overview.png','axial',[270,300,330,360,390,420],span=365,size=440)
    font=ImageFont.load_default(size=16)
    for o in objects:
        lo,hi=bounds([o]);center=(lo+hi)/2
        canvas=Image.new('RGB',(1320,485),(18,23,30));d=ImageDraw.Draw(canvas)
        for j,(plane,axes) in enumerate(PLANES.items()):
            span=max(180,float(max(hi[axes[0]]-lo[axes[0]],hi[axes[1]]-lo[axes[1]])+80))
            image,_=render_slice(ct,a,[o],plane,float(center[axes[2]]),span=span,size=440)
            canvas.paste(image,(j*440,40));d.text((j*440+8,6),f"{o['object_id']} | {plane} {center[axes[2]]:.1f} mm",font=font,fill='white')
        canvas.save(data/f"ct-{o['object_id']}.png")
    env=task/'environment';shutil.copyfile(Path(__file__).with_name('inspect_ct.py'),env/'inspect_ct.py')
    docker=(env/'Dockerfile').read_text().replace('COPY inspect_scene.py SOURCE_NOTICE.md','COPY inspect_scene.py inspect_ct.py SOURCE_NOTICE.md')
    (env/'Dockerfile').write_text(docker)
    notice=(env/'SOURCE_NOTICE.md').read_text().replace('No intensities supplied.','The original full 1.5 mm CT intensities are supplied losslessly as ct.npz with the corresponding affine_lps. Anonymous CT overlay previews and a reslicing helper were added. No patient surgery or disease history is asserted.')
    (env/'SOURCE_NOTICE.md').write_text(notice)
    inst=(task/'instruction.md').read_text().replace('No CT images are supplied.','The original CT is supplied in ct.npz: hu contains signed 16-bit Hounsfield units, with affine_lps for that array. All source CT samples are retained. A CT sample is a voxel-centre value; preview rendering uses nearest-neighbor reslicing.')
    inst+='''
## CT evidence

Use /app/data/ct-overview.png and /app/data/ct-<object_id>.png for ready axial,
coronal and sagittal views with anonymous mask outlines. These are previews;
the complete CT and masks are available. No clinical history is provided.

/app/inspect_ct.py renders arbitrary planes in the shared LPS coordinate frame:

```sh
python /app/inspect_ct.py --objects o197,o277 --plane axial --positions 280,295,310,325 --out /app/ct-focus.png
python /app/inspect_ct.py --objects o197 --plane coronal --out /app/ct-coronal.png
python /app/inspect_ct.py --objects o197 --plane sagittal --no-overlay --level 50 --width 400 --out /app/ct-plain.png
```

Object IDs above are examples of valid IDs, not proposed anatomical labels.
Omit --objects to include all supplied masks. Omit --positions for five slices
across the selected objects. Set --span to the square field of view in mm;
otherwise it fits selected objects plus 60 mm. --level/--width set the CT window.
All views show patient orientation explicitly. Use the CT and spatial anatomy
to identify objects; source contours are not themselves a diagnosis.
'''
    (task/'instruction.md').write_text(inst)
    (task/'task.toml').write_text((task/'task.toml').read_text().replace('terminal-bench/abdomen-a02',f'terminal-bench/{name}'))
    with (env/'data.tar.gz').open('wb') as f:
        with gzip.GzipFile(fileobj=f,filename='',mode='wb',mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode='w') as tar:
                for p in sorted(data.iterdir()):
                    info=tar.gettarinfo(str(p),p.name);info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
                    with p.open('rb') as content:tar.addfile(info,content)
    assert all(sha(p)==sha(data/p.name) for p in (ROOT/'runs/br013-abdomen/build/abdomen-a02').iterdir())
    assert sha(task/'tests/expected.json')==sha(source/'tests/expected.json')
    freeze_task(task,{'case':83,'mode':'recognition','object_count':11,'class_count':13,'source_task':'BR013-A02',
                     'old_public_members_and_key_unchanged':True,'ct_sha256':sha(source_ct),'ct_shape':list(ct.shape),
                     'ct_values_preserved_exactly':True,'ct_mask_registration_checks':checks,
                     'build_seconds':time.monotonic()-started,
                     'admission':'Failure-backed evidence addition; original CT supports review. Human inferability remains a separate check. No diagnosis or contour repair graded.'})
    print(json.dumps({'task':name,'ct_shape':list(ct.shape),'archive_bytes':(env/'data.tar.gz').stat().st_size,'grid_checks':sum(c['ct_grid_roundtrip_samples'] for c in checks)}))

from pathlib import Path
if __name__=='__main__':main()

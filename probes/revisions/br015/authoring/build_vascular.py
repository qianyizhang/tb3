"""Build one native, surgeon-labeled venous identity task without injected edits."""
import copy
import gzip
import json
import re
import shutil
import sys
import tarfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from common import ROOT,OUT,write,sha,freeze_task
sys.path.insert(0,str(ROOT/'probes/revisions/br013/authoring'))
from inspect_scene import load_scene,render
from inspect_ct import bounds,render_slice,contact_sheet,PLANES,transform,sample
from scoring import score

NAMES={1:'portal_vein',2:'splenic_vein',3:'short_gastric_veins',5:'right_gastro_omental_vein',
       6:'collateral_between_right_gastro_omental_and_short_gastric_veins',7:'left_gastric_vein',
       12:'superior_mesenteric_vein',21:'inferior_mesenteric_vein'}

def read_ct(path):
    with path.open('rb') as f:
        lines=[]
        while (line:=f.readline())!=b'\n':lines.append(line)
        offset=f.tell()
    fields={s.split(':',1)[0]:s.split(':',1)[1].strip() for s in b''.join(lines).decode('ascii').splitlines() if ':' in s and not s.startswith('#')}
    assert fields['type']=='short' and fields['encoding']=='gzip' and fields['endian']=='little' and fields['space']=='left-posterior-superior'
    shape=tuple(map(int,fields['sizes'].split()));dest=path.with_suffix('.raw')
    if not dest.exists():
        with path.open('rb') as src,dest.open('wb') as target:
            src.seek(offset)
            with gzip.GzipFile(fileobj=src) as f:shutil.copyfileobj(f,target,1024*1024)
    assert dest.stat().st_size==int(np.prod(shape))*2
    a=np.eye(4);a[:3,:3]=np.array([list(map(float,s.split(','))) for s in re.findall(r'\(([^)]+)\)',fields['space directions'])]).T
    a[:3,3]=list(map(float,fields['space origin'].strip('()').split(',')))
    return np.memmap(dest,dtype='<i2',shape=shape,order='F',mode='r'),a

def main():
    source=OUT/'vascular-screen/venous';screen=json.loads((OUT/'author/vascular-screen.json').read_text())
    record=next(r for r in screen['records'] if r['phase']=='venous');rows={r['number']:r for r in record['segments']}
    assert all(rows[i]['volume_ml']>1.5 and max(rows[i]['extent_mm'])>50 for i in NAMES)
    data=OUT/'build/abdomen-v01';assert not data.exists();data.mkdir(parents=True)
    rng=np.random.default_rng(1503);selected=list(NAMES);rng.shuffle(selected);objects=[];truth={}
    for j,i in enumerate(selected):
        r=rows[i];oid=r['object_id'];shutil.copyfile(source/f'{oid}.npz',data/f'{oid}.npz')
        objects.append({'object_id':oid,'file':f'{oid}.npz','color_index':j});truth[oid]=NAMES[i]
    # The full vascular mask is visible, unlabelled context and is not a target.
    shutil.copyfile(source/f"{rows[0]['object_id']}.npz",data/'context.npz')
    objects.append({'object_id':'context','file':'context.npz','color_index':12,'context_only':True})
    write(data/'scene.json',{'coordinates':'LPS millimetres','objects':objects});write(data/'targets.json',list(truth))
    write(data/'vocabulary.json',sorted(NAMES.values()))
    all_objects=load_scene(data);targets=[o for o in all_objects if o['object_id']!='context']
    render(targets,data/'overview.png')
    path=OUT/'source/colonvessels/pat_016_Venous_Phase_CT.nrrd';receipt=json.loads((path.parent/'ct-receipt.json').read_text());assert sha(path)==receipt['sha256']
    full,a=read_ct(path);lo,hi=bounds(all_objects)
    corner=np.array(list(__import__('itertools').product(*zip(lo-20,hi+20))))
    p=transform(corner,np.linalg.inv(a));start=np.maximum(0,np.floor(p.min(0)).astype(int));stop=np.minimum(full.shape,np.ceil(p.max(0)).astype(int)+1)
    ct=np.asarray(full[tuple(slice(x,y) for x,y in zip(start,stop))]).copy();ca=a.copy();ca[:3,3]=transform(start[None,:],a)[0]
    np.savez_compressed(data/'ct.npz',hu=ct,affine_lps=ca)
    assert np.array_equal(ct,full[tuple(slice(x,y) for x,y in zip(start,stop))])
    grid=[]
    for o in targets:
        vox=np.argwhere(o['mask']);q=transform(vox,o['affine_lps']);indices=transform(q,np.linalg.inv(a))
        assert np.max(np.abs(indices-np.rint(indices)))<1e-4
        ids=np.rint(indices).astype(int);assert np.all((ids>=start)&(ids<stop))
        assert np.array_equal(sample(ct,ca,q,-1024),full[tuple(ids.T)])
        grid.append({'object_id':o['object_id'],'all_target_voxels_registered':len(q)})
    font=ImageFont.load_default(size=16)
    for o in targets:
        l,h=bounds([o]);center=(l+h)/2;canvas=Image.new('RGB',(1320,485),(18,23,30));d=ImageDraw.Draw(canvas)
        for j,(plane,axes) in enumerate(PLANES.items()):
            span=max(180,float(max(h[axes[0]]-l[axes[0]],h[axes[1]]-l[axes[1]])+80))
            image,_=render_slice(ct,ca,[o],plane,float(center[axes[2]]),span=span,size=440)
            canvas.paste(image,(j*440,40));d.text((j*440+8,6),f"{o['object_id']} | {plane} {center[axes[2]]:.1f} mm",font=font,fill='white')
        canvas.save(data/f"ct-{o['object_id']}.png")
    tl,th=bounds(targets);contact_sheet(ct,ca,targets,data/'ct-overview.png','axial',np.linspace(tl[2],th[2],8)[1:-1],span=365,size=440)
    task=OUT/'tasks/abdomen-v01';assert not task.exists();shutil.copytree(ROOT/'runs/br013-abdomen/tasks/abdomen-a02',task)
    key={'mode':'recognition','truth':truth};write(task/'tests/expected.json',key)
    oracle={'assignments':[{'object_id':k,'label':v} for k,v in truth.items()]};write(task/'solution/answer.json',oracle)
    env=task/'environment';shutil.copyfile(Path(__file__).with_name('inspect_ct.py'),env/'inspect_ct.py')
    # Avoid platform-specific BLAS warnings; no geometric or display transformation changes.
    viewer=(env/'inspect_scene.py').read_text().replace('q=p@basis;c=centers@basis','q=np.sum(p[:,:,None]*basis[None,:,:],axis=1);c=np.sum(centers[:,:,None]*basis[None,:,:],axis=1)')
    (env/'inspect_scene.py').write_text(viewer)
    (env/'Dockerfile').write_text((env/'Dockerfile').read_text().replace('COPY inspect_scene.py SOURCE_NOTICE.md DATA-LICENSE.txt LABEL-LICENSE.txt','COPY inspect_scene.py inspect_ct.py SOURCE_NOTICE.md DATA-LICENSE.txt'))
    (env/'LABEL-LICENSE.txt').unlink()
    (env/'SOURCE_NOTICE.md').write_text('Derived from ColonVessels 2026, Hrubovcak et al., University Hospital Ostrava and collaborators.\nhttps://zenodo.org/records/17407158\nhttps://doi.org/10.1038/s41597-026-07303-2\nData and derived masks CC BY 4.0. Original source segment masks retain all voxels and their native coordinates; empty margins were cropped losslessly. CT is from the same venous-phase acquisition and cropped to the supplied vasculature plus 20 mm. Names, IDs, colours and array containers were anonymised; no vessel voxels were edited. Public CT and 3-D previews are derived views.\n')
    (task/'task.toml').write_text((task/'task.toml').read_text().replace('terminal-bench/abdomen-a02','terminal-bench/abdomen-v01').replace('expert_time_estimate_hours = 0.25\n',''))
    (task/'instruction.md').write_text('''# Identify eight abdominal veins

Assign an anatomical identity to each object listed in /app/data/targets.json.
These are intact source vein masks in shared patient LPS millimetres, with the
original CT from the same venous-phase acquisition. Each target represents one
named vessel or named vessel group. A group may have multiple components.
Use each of the eight labels in /app/data/vocabulary.json exactly once.

The object named context contains the surrounding venous segmentation. It is
unlabelled context, overlaps the target masks, and must not receive an answer.
Anatomical connections, course and surrounding CT anatomy may be more useful
than the isolated shape. No surgery or disease diagnosis or contour correction
is requested. Source masks may contain ordinary segmentation imperfections;
identify the substantial vessel represented by each entire target.

Terminology: gastro-omental and gastroepiploic are synonyms. short_gastric_veins
denotes a group of short gastric tributaries. The collateral label denotes a
vessel connecting the right gastro-omental venous route with the short gastric
venous route; it does not require a causal diagnosis. Do not infer a class from
an object ID, colour or file order; these are arbitrary.

Write /app/answer/answer.json as
{"assignments":[{"object_id":"o123","label":"label_name"}]}.
Include all eight target IDs exactly once, no context ID, and no prose fields.

## Data and ready tools

Each NPZ object has a cropped binary mask, affine_lps mapping [i,j,k,1] to LPS
millimetres, and surface_lps containing boundary voxel centres. +x is left,
+y posterior and +z superior. Independent masks preserve original overlaps.
ct.npz contains hu (signed 16-bit Hounsfield units) and affine_lps for its grid.
The full native sampling within the CT crop is preserved. No inter-phase
registration is needed. Array masks and CT are authoritative; PNGs are previews.

Start with /app/data/overview.png, ct-overview.png, and ct-<object_id>.png.
Python, NumPy and Pillow are installed. Load masks using load_scene() from
/app/inspect_scene.py; the context object has context_only: true in scene.json.

```sh
python /app/inspect_scene.py
python /app/inspect_scene.py --objects o307,o570,o863 --yaw 75 --pitch 20 --out /app/focus.png
python /app/inspect_ct.py --objects o307 --plane axial --out /app/ct-focus.png
python /app/inspect_ct.py --objects o609 --plane coronal --no-overlay --out /app/ct-plain.png
```

IDs in examples are valid, without proposed identities. Use any target IDs or
context. The CT tool accepts --plane axial/coronal/sagittal, --positions as
comma-separated physical LPS plane coordinates, --span for field of view in mm,
and --level/--width for windowing (default 50/400). Without positions it makes
five slices across the selected objects. Without a span it fits their extent
plus 60 mm. --no-overlay shows CT alone. You may perform additional calculations
or use other tools. Source attribution is in /app/SOURCE_NOTICE.md; no external
source/patient matching is needed to solve the task.
''')
    with (env/'data.tar.gz').open('wb') as f:
        with gzip.GzipFile(fileobj=f,filename='',mode='wb',mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode='w') as tar:
                for p in sorted(data.iterdir()):
                    i=tar.gettarinfo(str(p),p.name);i.uid=i.gid=0;i.uname=i.gname='';i.mtime=0
                    with p.open('rb') as content:tar.addfile(i,content)
    swapped=copy.deepcopy(oracle);swapped['assignments'][0]['label'],swapped['assignments'][1]['label']=swapped['assignments'][1]['label'],swapped['assignments'][0]['label']
    tests=[('oracle',oracle,True),('order_invariant',{'assignments':oracle['assignments'][::-1]},True),('empty',{'assignments':[]},False),('missing',{'assignments':oracle['assignments'][1:]},False),('duplicate',{'assignments':oracle['assignments']+[oracle['assignments'][0]]},False),('swap',swapped,False),('context_answer',{'assignments':oracle['assignments']+[{'object_id':'context','label':'portal_vein'}]},False)]
    controls=[{'name':n,'expected':e,'grade':score(a,key)} for n,a,e in tests];assert all(c['expected']==c['grade']['passed'] for c in controls)
    freeze_task(task,{'case':'ColonVessels pat_016 venous phase','mode':'recognition','object_count':8,'context_count':1,
                     'source_segmentation_sha256':record['source_sha256'],'source_ct_sha256':sha(path),'ct_crop_start':start.tolist(),'ct_crop_stop':stop.tolist(),
                     'all_target_geometry_unchanged':True,'ct_registration':grid,'controls':controls,
                     'source_identities':[{**rows[i],'canonical_label':NAMES[i]} for i in NAMES],
                     'admission':'Eight substantial, source-named vessels with same-phase CT; one diagnostic Sol trial. Specialist publication supports keys; independent input-identifiability review is pending. Not yet a certified hard task.'})
    print(json.dumps({'task':'abdomen-v01','targets':list(truth),'ct_crop_shape':list(ct.shape),'archive_bytes':(env/'data.tar.gz').stat().st_size,'controls':len(controls)}))

if __name__=='__main__':main()

"""Decode original Slicer segment layers; preserve named source masks privately."""
import gzip
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
import numpy as np
from common import ROOT,OUT,write,sha
sys.path.insert(0,str(ROOT/'probes/revisions/br013/authoring'))
from build import surface
from inspect_scene import load_scene,render

def read_nrrd(path):
    raw=path.read_bytes();split=raw.index(b'\n\n');head=raw[:split].decode('ascii')
    fields={line.split(':',1)[0]:line.split(':',1)[1].lstrip('= ') for line in head.splitlines() if ':' in line and not line.startswith('#')}
    assert fields['encoding']=='gzip' and fields['type']=='uint8' and fields['space']=='left-posterior-superior'
    shape=tuple(map(int,fields['sizes'].split()));assert len(shape)==4
    backing=path.with_suffix('.raw')
    if not backing.exists():
        import io
        with gzip.GzipFile(fileobj=io.BytesIO(raw[split+2:])) as f,backing.open('wb') as out:shutil.copyfileobj(f,out,1024*1024)
    assert backing.stat().st_size==int(np.prod(shape))
    data=np.memmap(backing,dtype='uint8',mode='r',shape=shape,order='F')
    dirs=[list(map(float,s.split(','))) for s in re.findall(r'\(([^)]+)\)',fields['space directions'])]
    a=np.eye(4);a[:3,:3]=np.array(dirs).T;a[:3,3]=np.array(list(map(float,fields['space origin'].strip('()').split(','))))
    segments=[]
    for k,v in fields.items():
        m=re.fullmatch(r'Segment(\d+)_Name',k)
        if not m:continue
        i=m[1];segments.append({'number':int(i),'name':v,'layer':int(fields[f'Segment{i}_Layer']),'value':int(fields[f'Segment{i}_LabelValue'])})
    return data,a,sorted(segments,key=lambda r:r['number']),fields

def main():
    source=OUT/'source/colonvessels';records=[]
    for path in sorted(source.glob('*.seg.nrrd')):
        phase='arterial' if 'Arterial' in path.name else 'venous';data,a,segs,fields=read_nrrd(path)
        out=OUT/'vascular-screen'/phase;out.mkdir(parents=True,exist_ok=True)
        rng=np.random.default_rng(1502);ids=rng.choice(np.arange(100,1000),len(segs),replace=False)
        allpoints={}
        for layer in sorted({s['layer'] for s in segs}):
            p=np.argwhere(data[layer]!=0);vals=data[(np.full(len(p),layer),*p.T)]
            allpoints[layer]=(p,vals)
        scene=[];rows=[]
        for j,(s,oidnum) in enumerate(zip(segs,ids)):
            p,vals=allpoints[s['layer']];q=p[vals==s['value']]
            if not len(q):rows.append({**s,'voxels':0});continue
            lo=q.min(0);hi=q.max(0)+1;mask=np.zeros(hi-lo,dtype=bool);mask[tuple((q-lo).T)]=True
            ca=a.copy();ca[:3,3]=a[:3,3]+np.sum(lo[None,:]*a[:3,:3],axis=1)
            border=surface(mask);world=np.sum(border[:,None,:]*ca[None,:3,:3],axis=2)+ca[:3,3]
            oid=f'o{oidnum}';dest=out/f'{oid}.npz';np.savez_compressed(dest,mask=mask,affine_lps=ca,surface_lps=world.astype('float32'))
            scene.append({'object_id':oid,'file':dest.name,'color_index':j})
            rows.append({**s,'object_id':oid,'voxels':len(q),'volume_ml':float(len(q)*abs(np.linalg.det(a[:3,:3]))/1000),'extent_mm':((hi-lo)*np.linalg.norm(a[:3,:3],axis=0)).tolist(),'cropped_mask_sha256':sha(dest)})
        write(out/'scene.json',{'coordinates':'LPS millimetres','objects':scene})
        objects=load_scene(out);render(objects[1:],out/'overview.png')
        records.append({'phase':phase,'source_sha256':sha(path),'source_shape':list(data.shape),'segments':rows,'source_review_status_tags':sorted({v.split('|')[0] for k,v in fields.items() if k.endswith('_Tags')})})
    write(OUT/'author/vascular-screen.json',{'round':'BR-015','patients':1,'records':records})
    print(json.dumps([{'phase':r['phase'],'rows':[{k:s.get(k) for k in ['number','name','object_id','voxels','volume_ml','extent_mm']} for s in r['segments']]} for r in records],indent=2))

if __name__=='__main__':main()

"""Bounded component screen, preserving source identity and omission lineage."""
import itertools
import json
import sys
import time
from pathlib import Path
import nibabel as nib
import numpy as np
from common import ROOT,OUT,write,sha

sys.path.insert(0,str(ROOT/'probes/revisions/br013/authoring'))
from inspect_scene import load_scene,render
from screen import CASES,world
from build import surface

def components(mask,connectivity=26):
    padded=np.pad(mask,1).copy();flat=padded.ravel();s=padded.shape
    offsets=[i*s[1]*s[2]+j*s[2]+k for i,j,k in itertools.product([-1,0,1],repeat=3)
             if (i or j or k) and (connectivity==26 or abs(i)+abs(j)+abs(k)==1)]
    result=[]
    for seed in np.flatnonzero(flat):
        if not flat[seed]:continue
        flat[seed]=False;queue=[int(seed)]
        for value in queue:
            for offset in offsets:
                q=value+offset
                if flat[q]:flat[q]=False;queue.append(q)
        result.append(np.column_stack(np.unravel_index(queue,s))-1)
    return sorted(result,key=len,reverse=True)

def export_piece(path,mask,a):
    p=np.argwhere(mask);lo=p.min(0);hi=p.max(0)+1
    crop=mask[tuple(slice(l,h) for l,h in zip(lo,hi))]
    ca=a.copy();ca[:3,3]=world(lo[None,:],a)[0]
    np.savez_compressed(path,mask=crop,affine_lps=ca,surface_lps=world(surface(crop),ca).astype('float32'))
    with np.load(path) as z:
        assert np.array_equal(np.argwhere(z['mask'])+lo,p)
        assert np.allclose(world(np.argwhere(z['mask']),z['affine_lps']),world(p,a),rtol=0,atol=1e-8)

def main():
    started=time.monotonic();natural=[]
    for case,patient in CASES.items():
        for label in ['pancreas','duodenum']:
            path=ROOT/'runs/br004-v1/source'/patient/'segmentations'/f'{label}.nii.gz'
            mask=np.asarray(nib.load(path).dataobj,dtype=bool)
            p=np.argwhere(mask)
            if not len(p):continue
            lo=p.min(0);hi=p.max(0)+1;mask=mask[tuple(slice(l,h) for l,h in zip(lo,hi))]
            sizes={str(c):[len(x) for x in components(mask,c)] for c in [6,26]}
            natural.append({'case':case,'label':label,'source_sha256':sha(path),'components_voxels':sizes,
                            'components_ml':{k:[round(v*3.375/1000,4) for v in vals] for k,vals in sizes.items()}})
    source=ROOT/'runs/br013-abdomen/build/abdomen-a01';objs=load_scene(source)
    key=json.loads((ROOT/'runs/br013-abdomen/tasks/abdomen-a01/tests/expected.json').read_text())['truth']
    variants=[]
    for gap in [0,6]:
        data=OUT/'fragment-screen'/f'gap-{gap}';data.mkdir(parents=True,exist_ok=True)
        lineage=[];scene=[];pieces=[];rng=np.random.default_rng(1400)
        labels=[];raw=[];cuts=[]
        for o in objs:
            mask=o['mask'];a=o['affine_lps'];label=key[o['object_id']]
            if label not in ['pancreas','duodenum']:
                raw.append((mask,a,label,o['object_id'],None));continue
            p=np.argwhere(mask);q=world(p,a);eig,vec=np.linalg.eigh(np.cov(q.T));axis=vec[:,-1]
            if axis[np.argmax(np.abs(axis))]<0:axis=-axis
            projection=np.sum(q*axis,axis=1);mid=float(np.median(projection))
            selections=[projection<mid-gap/2,projection>=mid+gap/2]
            kept=np.zeros_like(mask);parts=[]
            for side,sel in enumerate(selections):
                m=np.zeros_like(mask);m[tuple(p[sel].T)]=True
                assert not (kept&m).any();kept|=m
                parts.append(m);raw.append((m,a,label,o['object_id'],side))
            removed=mask&~kept
            assert np.array_equal(kept|removed,mask)
            cuts.append({'label':label,'gap_mm':gap,'axis_lps':axis.tolist(),'plane_offset_mm':mid,
                         'original_voxels':int(mask.sum()),'retained_voxels':[int(m.sum()) for m in parts],
                         'retained_ml':[float(m.sum()*3.375/1000) for m in parts],
                         'removed_voxels':int(removed.sum()),'removed_ml':float(removed.sum()*3.375/1000),
                         'components26':[list(map(len,components(m))) for m in parts]})
        order=rng.permutation(len(raw));ids=rng.choice(np.arange(100,1000),len(raw),replace=False)
        for color,(i,code) in enumerate(zip(order,ids)):
            mask,a,label,parent,side=raw[i];oid=f'o{code}';path=data/f'{oid}.npz';export_piece(path,mask,a)
            scene.append({'object_id':oid,'file':path.name,'color_index':color})
            lineage.append({'object_id':oid,'label':label,'parent':parent,'side':side,'voxels':int(mask.sum())})
            if side is not None:
                pieces.append({'object_id':oid,'label':label,'side':side,'points':world(surface(mask),a)})
        write(data/'scene.json',{'coordinates':'LPS millimetres','objects':scene})
        write(data/'vocabulary.json',sorted(set(key.values())))
        render(load_scene(data),data/'overview.png')
        distances=[]
        for i,a in enumerate(pieces):
            for b in pieces[i+1:]:
                best=float('inf');qa=a['points'];qb=b['points']
                for start in range(0,len(qa),128):
                    d=qa[start:start+128,None,:]-qb[None,:,:];best=min(best,float(np.sum(d*d,axis=2).min()))
                distances.append({'a':a['object_id'],'b':b['object_id'],'mm':best**.5,'same_source':a['label']==b['label']})
        # Privileged candidate-family baseline: given the four fragments, pair by nearest surfaces.
        used=set();pairs=[]
        for d in sorted(distances,key=lambda d:d['mm']):
            if d['a'] not in used and d['b'] not in used:
                used|={d['a'],d['b']};pairs.append(d)
        # The plane normals are an author-visible artifact of construction, not a blinded learned baseline.
        variants.append({'gap_mm':gap,'data_path':str(data.relative_to(ROOT)),'lineage':lineage,'cuts':cuts,
                         'pairwise_surface_distances':distances,'nearest_surface_pairing':pairs,
                         'nearest_pairs_correct':sum(d['same_source'] for d in pairs),
                         'cut_surface_artifact':'Both fragments share opposing parallel cut planes. A seam-aware algorithm can exploit the synthetic construction; not certified clinical error realism.',
                         'minimum_target_fragment_ml':min(v for c in cuts for v in c['retained_ml'])})
    result={'round':'BR-014','source_case_for_split':28,'natural_components':natural,'variants':variants,
            'elapsed_seconds':time.monotonic()-started,'script_sha256':sha(Path(__file__)),
            'limits':['Source disconnectedness is not proof of bad annotation.','Nearest-surface pairing is given which four objects are fragments and does not infer their class identities.','Synthetic cuts are geometric probes, not clinically validated omissions.','Retained-fragment identity is graded; omitted volume is never reconstructed or called disease.']}
    write(OUT/'author/component-screen.json',result);write(ROOT/'docs/evidence/br014-component-screen.json',result)
    print(json.dumps({'natural':natural,'variants':[{'gap':v['gap_mm'],'cuts':v['cuts'],'nearest_pairs_correct':v['nearest_pairs_correct']} for v in variants]},indent=2))

if __name__=='__main__':main()

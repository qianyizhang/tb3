"""Independent source-grid, acceptance-region, archive and output-contract checks."""
import itertools,json,tarfile
import numpy as np,nibabel as nib
from common import ROOT,OUT,write,sha
rows=[]
for path in sorted((OUT/'freezes').glob('*-v2.json')):
 t=json.loads(path.read_text())['tasks'][0];task=ROOT/t['task_path'];assert all(sha(task/p)==v for p,v in t['files'].items())
 key=json.loads((task/'tests/expected.json').read_text());sub=t['source_subject'];source=OUT/'source';bp=next(source.glob(f'sub-{sub}*brain_mask.nii.gz'));im=nib.load(bp);a=np.asanyarray(im.dataobj);aff=im.affine;spacing=np.linalg.norm(aff[:3,:3],axis=0)
 checks=[]
 for m,reg in zip(sorted(source.glob(f'sub-{sub}*Lesion*nii.gz')),key['regions']):
  xyz=np.argwhere(np.asanyarray(nib.load(m).dataobj)>0);accepted=np.array([list(map(int,v.split(','))) for v in reg['accepted_voxels']]);lo=xyz.min(0)-np.ceil(1/spacing).astype(int);hi=xyz.max(0)+np.ceil(1/spacing).astype(int)
  grid=np.array(list(itertools.product(*(range(int(lo[d]),int(hi[d])+1) for d in range(3)))))
  # Independent brute-force distance transform, not the builder's offset union.
  good=[]
  for chunk in np.array_split(grid,max(1,len(grid)//128)):
   d=np.sum(((chunk[:,None,:]-xyz[None,:,:])*spacing)**2,axis=2).min(1)
   good.extend(map(tuple,chunk[d<=1+1e-9].tolist()))
  assert set(good)==set(map(tuple,accepted.tolist()))
  world=np.sum(xyz[:,None,:]*aff[None,:3,:3],axis=2)+aff[:3,3];back=(world-aff[:3,3])/spacing;assert np.allclose(back,xyz)
  checks.append({'source':m.name,'independent_acceptance_region_equal':True,'coordinate_roundtrip':True})
 with tarfile.open(task/'environment/data.tar.gz') as archive:
  names=archive.getnames();assert set(names)=={'brain.npz','original.npz','volume.json','overview.png','slabs.png'}
  assert not any('Lesion' in n or 'expected' in n for n in names)
 rows.append({'task':t['task'],'files_unchanged':True,'source_checks':checks,'only_public_inputs_in_archive':True})
# A synthetic ambiguous graph exercises augmenting-path one-to-one matching.
from scoring import score,read_json
k={'shape':[5,5,5],'regions':[{'accepted_voxels':{'1,1,1':1,'2,2,2':1}},{'accepted_voxels':{'1,1,1':1}}]}
r=score({'aneurysms':[[1,1,1],[2,2,2]]},k);assert r['tp']==2 and r['passed']
r2=score({'aneurysms':[[2,2,2],[2,2,2]]},k);assert r2['tp']==1 and r2['fp']==1 and r2['fn']==1
out={'rows':rows,'synthetic_one_to_one_controls':2,'source_human_review':'pending','excluded_v1_oracle':'missing verifier Dockerfile; infrastructure, no model attempt'}
write(OUT/'author/audit.json',out);write(ROOT/'docs/evidence/br016-audit.json',out);print(json.dumps(out,indent=2))

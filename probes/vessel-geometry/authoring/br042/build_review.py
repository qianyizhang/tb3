"""Local source-CTA review of all output, with optional coronary GT overlay."""
from pathlib import Path
import json,shutil,hashlib
import numpy as np
import nibabel as nib
from PIL import Image
from run_trials import ROOT,B
T=B/'tasks/all-vessels';O=B/'review';O.mkdir(exist_ok=True);(O/'slices').mkdir(exist_ok=True)
image=nib.load(T/'environment/data/image.nii.gz');a=np.asarray(image.dataobj);inv=np.linalg.inv(image.affine)
for z in range(a.shape[2]):
 p=O/'slices'/f'{z:03d}.jpg'
 if not p.exists():Image.fromarray(np.clip((a[:,:,z].T.astype(float)+100)/700*255,0,255).astype('uint8')).save(p,quality=90)
paths=list((ROOT/'runs/br042-all-vessels-astra-medium-v2-20260920').glob('*/artifacts/app/answer/centerlines.json'));assert len(paths)==1
answer=json.loads(paths[0].read_text());ref=json.loads((T/'tests/reference.json').read_text());curves=[]
for kind,obj in [('Astra',answer),('Reference',ref)]:
 for c in obj['centerlines']:
  p=np.asarray(c['points_ras_mm']);v=np.einsum('ij,nj->ni',inv[:3,:3],p)+inv[:3,3]
  curves.append({'id':c['id'],'name':c.get('vessel_name',c['id']),'kind':kind,'labels':c['labels'],'points':p.tolist(),'voxels':v.tolist()})
(O/'data.json').write_text(json.dumps({'shape':list(a.shape),'curves':curves}))
(O/'index.html').write_text((Path(__file__).parent/'review.html').read_text())
shutil.copy2(paths[0],O/'centerlines.json')
report=ROOT/'docs/research-rounds/BR-042-results.md'
if report.exists():shutil.copy2(report,O/'results.md')
assert hashlib.sha256(paths[0].read_bytes()).hexdigest()==hashlib.sha256((O/'centerlines.json').read_bytes()).hexdigest()
print(O/'index.html')

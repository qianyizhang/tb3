"""Comparison viewer containing unchanged submissions and source CTA slices."""
from pathlib import Path
import json,shutil,hashlib
import numpy as np
import nibabel as nib
from PIL import Image
from run_trials import ROOT,B
H=Path(__file__).resolve().parent;O=B/'review';O.mkdir(exist_ok=True)
T=B/'tasks/all-vessels';image=nib.load(T/'environment/data/image.nii.gz');inv=np.linalg.inv(image.affine)
slices=O/'slices'
if not slices.exists():
    old=ROOT/'runs/br042-all-vessels-v2/review/slices'
    if old.exists():shutil.copytree(old,slices)
    else:
        slices.mkdir();vol=np.asarray(image.dataobj)
        for z in range(image.shape[2]):Image.fromarray(np.clip((vol[:,:,z].T.astype(float)+100)/700*255,0,255).astype('uint8')).save(slices/f'{z:03d}.jpg',quality=90)
rows=json.loads((B/'results.json').read_text())['runs'];models=[];curves=[]
def add(kind,obj):
    for c in obj['centerlines']:
        p=np.asarray(c['points_ras_mm']);v=np.einsum('ij,nj->ni',inv[:3,:3],p)+inv[:3,3]
        curves.append({'id':c['id'],'name':c.get('vessel_name',c['id']),'kind':kind,'labels':c['labels'],'points':p.tolist(),'voxels':v.tolist()})
for row in rows:
    if row['phase'] in ['oracle','nop'] or not row.get('replay',{}).get('format_valid'):continue
    phase=row['phase'];ans=ROOT/row['answer_path']/'centerlines.json';score=row['replay']
    out=O/f'{phase}-centerlines.json';shutil.copy2(ans,out);assert hashlib.sha256(out.read_bytes()).hexdigest()==row['answer_sha256']
    method=ans.parent/'method.md'
    if method.exists():shutil.copy2(method,O/f'{phase}-method.md')
    inventory=ans.parent/'inventory.csv'
    if inventory.exists():shutil.copy2(inventory,O/f'{phase}-inventory.csv')
    g=score['geometry'];l=score['labeled']
    status='Timed out — partial-output diagnostics; method.md unfinished.' if row.get('exception') else 'Completed normally.'
    summary=f"{phase}: {status} Geometry length coverage {g['length_weighted_recall_1mm']:.1%}, labeled length coverage {l['length_weighted_recall_1mm']:.1%}; macro geometry {g['macro_recall_1mm']:.1%}, macro labeled {l['macro_recall_1mm']:.1%}. Geometry pass: {score['geometry_pass']}; labeled pass: {score['labeled_pass']}."
    models.append({'phase':phase,'summary':summary,'display_name':phase+(' (partial; timed out)' if row.get('exception') else ''),'inventory_file':f'{phase}-method.md' if method.exists() else f'{phase}-inventory.csv','inventory_label':'Selected run: method and inventory' if method.exists() else 'Partial inventory CSV (method unfinished)'});add(phase,json.loads(ans.read_text()))
add('Reference',json.loads((T/'tests/reference.json').read_text()))
(O/'data.json').write_text(json.dumps({'shape':list(image.shape),'models':models,'curves':curves}))
(O/'index.html').write_text((H/'review.html').read_text())
p=ROOT/'docs/research-rounds/BR-042-v3-results.md'
if p.exists():shutil.copy2(p,O/'results.md')
print(json.dumps({'viewer':str(O/'index.html'),'models':[m['phase'] for m in models]}))

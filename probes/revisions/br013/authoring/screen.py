"""Screen original-resolution abdominal masks, without model calls or edits."""
import hashlib
import json
import time
from pathlib import Path

import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'runs/br013-abdomen'
CASES = {19:'s1127',28:'s1233',32:'s1336',46:'s0885',61:'s0915',74:'s0965',83:'s0629',95:'s0344'}
LABELS = ['spleen','kidney_right','kidney_left','gallbladder','liver','stomach',
          'pancreas','adrenal_gland_right','adrenal_gland_left','duodenum',
          'aorta','inferior_vena_cava','portal_vein_and_splenic_vein']

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2)+'\n')

def world(p, a):
    return sum(p[:,k,None]*a[:3,k] for k in range(3))+a[:3,3]

def assignment(cost):
    """Exact minimum-cost injective assignment, including rectangular matrices."""
    n,m=cost.shape
    assert n<=m<=20
    states={0:(0.0,())}
    for i in range(n):
        next_states={}
        for mask,(score,order) in states.items():
            for j in range(m):
                if mask & (1<<j): continue
                key=mask|(1<<j); value=score+float(cost[i,j])
                if key not in next_states or value<next_states[key][0]:
                    next_states[key]=(value,order+(j,))
        states=next_states
    return min(states.values())[1]

def main():
    start=time.monotonic(); rows=[]
    for case,patient in CASES.items():
        source=ROOT/'runs/br004-v1/source'/patient
        objects=[]; all_min=[];all_max=[]
        for label in LABELS:
            path=source/'segmentations'/f'{label}.nii.gz'
            im=nib.load(path); arr=np.asanyarray(im.dataobj)
            assert np.isin(arr,[0,1]).all()
            p=np.argwhere(arr>0)
            if not len(p): continue
            a=np.diag([-1.,-1.,1.,1.])@im.affine
            q=world(p,a);lo=q.min(0);hi=q.max(0)
            all_min.append(lo);all_max.append(hi)
            objects.append({'label':label,'source_path':str(path.relative_to(ROOT)),
                            'sha256':sha(path),'voxels':len(p),'volume_ml':float(len(p)*abs(np.linalg.det(a[:3,:3]))/1000),
                            'centroid_lps':q.mean(0).tolist(),'extent_mm':(hi-lo+np.linalg.norm(a[:3,:3],axis=0)).tolist(),
                            'touches_scan_boundary':bool(((p.min(0)==0)|(p.max(0)==np.array(arr.shape)-1)).any())})
        lo=np.min(all_min,axis=0);hi=np.max(all_max,axis=0)
        for obj in objects:
            obj['features']=np.r_[(np.array(obj['centroid_lps'])-lo)/(hi-lo),
                                  np.log(obj['volume_ml']),np.log(obj['extent_mm'])].tolist()
        rows.append({'case':case,'patient':patient,'objects':objects,'complete_13':len(objects)==len(LABELS),
                     'missing':sorted(set(LABELS)-{x['label'] for x in objects})})
    baselines=[]
    for row in rows:
        train=[o for r in rows if r['case']!=row['case'] and r['case']!=74 for o in r['objects']]
        scale=np.maximum(np.array([o['features'] for o in train]).std(0),1e-6)
        templates=np.array([np.median([o['features'] for o in train if o['label']==label],axis=0) for label in LABELS])
        test=np.array([o['features'] for o in row['objects']])
        costs=(((test[:,None,:]-templates[None,:,:])/scale)**2).sum(2)
        nearest=costs.argmin(1); joint=assignment(costs)
        predictions=[{'source':o['label'],'nearest':LABELS[int(a)],'one_to_one':LABELS[b]}
                      for o,a,b in zip(row['objects'],nearest,joint)]
        baselines.append({'case':row['case'],'total':len(predictions),
                          'nearest_correct':sum(p['source']==p['nearest'] for p in predictions),
                          'one_to_one_correct':sum(p['source']==p['one_to_one'] for p in predictions),
                          'predictions':predictions})
    result={'round':'BR-013','model_calls':0,'features':'Seven features: scene-normalized LPS centroid, log volume, three log extents. LPS origin cancelled by union bounding box. Original masks, no CT intensity features.',
            'method':'Leave-one-patient-out median templates; standardize using training SD. Both independent nearest and exact minimum-cost injective assignment into 13-label vocabulary. Case 74 excluded from training as previously declared limited coverage; its test row retained.',
            'limitations':['Small clustered source pool; author baseline has labeled examples unavailable to blind model.',
                           'Missing organ or unusual shape is not a diagnosis. One-to-one matching does not establish semantic validity.',
                           'Some long vessels naturally reach scan boundary; no organ crop is created by export.'],
            'rows':rows,'baselines':baselines,'script_sha256':sha(Path(__file__)),
            'elapsed_seconds':round(time.monotonic()-start,3)}
    write(OUT/'author/screen.json',result)
    write(ROOT/'docs/evidence/br013-original-mask-screen.json',result)
    print(json.dumps([{'case':r['case'],'present':len(r['objects']),'missing':r['missing'],
                       'stomach_ml':next((round(o['volume_ml'],1) for o in r['objects'] if o['label']=='stomach'),None),
                       'baseline':baselines[i]} for i,r in enumerate(rows)],indent=2))

if __name__=='__main__': main()

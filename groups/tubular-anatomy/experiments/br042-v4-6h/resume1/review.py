"""Independent saved-output review of the completed resumed continuation."""
from pathlib import Path
from datetime import datetime
import json,hashlib,types,shutil
import numpy as np
import nibabel as nib
R=Path(__file__).resolve().parents[5];G=Path(__file__).resolve().parent;T=R/'runs/br042-all-vessels-v4-6h/tasks/all-vessels'
P=R/'runs/br042-all-vessels-astra-xhigh-v4-6h-resume1/all-vessels__cr5kdch';A=P/'artifacts/app/answer'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((R/'runs/br042-all-vessels-v4-6h/freeze.json').read_text());assert {str(p.relative_to(T)):sha(p) for p in T.rglob('*') if p.is_file()}==f['tasks'][0]['files']
s=types.ModuleType('score');exec(compile((T/'tests/score.py').read_text(),str(T/'tests/score.py'),'exec'),s.__dict__)
obj=json.loads((A/'centerlines.json').read_text());m=s.evaluate(obj,json.loads((T/'tests/reference.json').read_text()));assert m==json.loads((P/'verifier/metrics.json').read_text())
prior=json.loads((G.parent/'evaluations/saved-output-review.json').read_text());old=prior['comparison'][-1]['metrics'];assert all(m[k]==old[k] for k in ['geometry','labeled','per_reference_category'])
r=json.loads((P/'result.json').read_text());assert r['exception_info'] is None
elapsed=(datetime.fromisoformat(r['agent_execution']['finished_at'].replace('Z','+00:00'))-datetime.fromisoformat(r['agent_execution']['started_at'].replace('Z','+00:00'))).total_seconds()
repro=json.loads((A/'reproducibility.json').read_text());assert repro['identical_centerlines'] and sha(A/'centerlines.json')==repro['before_centerlines_sha256']==repro['after_centerlines_sha256']
trace=[]
for line in (P/'agent/codex.txt').read_text().splitlines():
 try:trace.append(json.loads(line))
 except ValueError:pass
assert trace[-1]['type']=='turn.completed'
im=nib.load(T/'environment/data/image.nii.gz');inv=np.linalg.inv(im.affine)
inside=all(((v:=nib.affines.apply_affine(inv,np.array(c['points_ras_mm'])))>=-1e-5).all() and (v<=np.array(im.shape)-1+1e-5).all() for c in obj['centerlines'])
record={'schema_version':1,'kind':'evaluation','id':'br042-resume1-independent-review','experiment_id':'br042-v4-6h','group_id':'tubular-anatomy','attempt_id':'attempt-efc0c2309c0753440d73b5aa','depends_on':['attempt-efc0c2309c0753440d73b5aa'],'classification':'completed_resumed_continuation','resumed_seconds':elapsed,'prior_agent_seconds':10065.189254,'combined_agent_seconds':10065.189254+elapsed,'frozen_bytes_verified':True,'exact_verifier_agreement':True,'coronary_metrics_unchanged_from_interruption':True,'metrics':m,'points':sum(len(c['points_ras_mm']) for c in obj['centerlines']),'all_points_in_fov':bool(inside),'reproduction_receipt_hash_matches':True,'reproduction_limit':'Model-side full rebuild recorded; reviewer replayed scoring, not extraction or blind rediscovery.','transport_error_count':sum(x.get('type')=='error' or x.get('item',{}).get('type')=='error' for x in trace),'evidence':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in [P/'result.json',A/'centerlines.json',A/'method.md',A/'reproducibility.json',P/'verifier/metrics.json']]}
(G/'evaluation.json').write_text(json.dumps(record,indent=2)+'\n')
V=R/'runs/br042-all-vessels-v3/review';src=V/'v4-6h';out=V/'v4-resumed';out.mkdir(exist_ok=True);data=json.loads((src/'data.json').read_text());phase='v4-resumed-astra-xhigh'
data['models'].insert(0,{'phase':phase,'display_name':'V4 Astra/xhigh • resumed, completed','summary':'Completed after 86m resumed / 254m combined agent execution. Geometry 94.0%; correctly labeled 79.3%. Both category gates fail.','inventory_file':phase+'-method.md','inventory_label':'Completed method and uncertainty inventory'})
for c in obj['centerlines']:
 p=np.array(c['points_ras_mm']);data['curves'].append({'id':c['id'],'name':c['vessel_name'],'kind':phase,'labels':c['labels'],'points':p.tolist(),'voxels':nib.affines.apply_affine(inv,p).tolist()})
(out/'data.json').write_text(json.dumps(data));(out/'index.html').write_text((src/'index.html').read_text().replace('V3 / V4 six-hour-attempt comparison','Completed resumed V4 comparison'))
for x in data['models']:
 name=x['phase'];shutil.copy2(A/'centerlines.json' if name==phase else src/(name+'-centerlines.json'),out/(name+'-centerlines.json'));shutil.copy2(A/'method.md' if name==phase else src/x['inventory_file'],out/x['inventory_file'])
if (G/'review.md').exists():shutil.copy2(G/'review.md',out/'results.md')
print({k:record[k] for k in ['resumed_seconds','combined_agent_seconds','points','all_points_in_fov','transport_error_count']})
print('Added IDs',sorted(set(c['id'] for c in obj['centerlines'])-set(c['id'] for c in json.loads((R/'runs/br042-all-vessels-v4-6h-resume1/restore/answer/centerlines.json').read_text())['centerlines'])))

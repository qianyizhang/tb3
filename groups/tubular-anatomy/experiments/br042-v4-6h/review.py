"""Post-run diagnostic replay; never changes solver files or launches inference."""
from pathlib import Path
from datetime import datetime
import json,hashlib,types,shutil
import numpy as np
import nibabel as nib
R=Path(__file__).resolve().parents[4];G=Path(__file__).resolve().parent
B=R/'runs/br042-all-vessels-v4-6h';T=B/'tasks/all-vessels'
P=R/'runs/br042-all-vessels-astra-xhigh-v4-6h-attempt2/all-vessels__xZ2JU6T';A=P/'artifacts/app/answer'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((B/'freeze.json').read_text());assert {str(p.relative_to(T)):sha(p) for p in T.rglob('*') if p.is_file()}==f['tasks'][0]['files']
for name in ['tests/score.py','tests/reference.json','environment/data/image.nii.gz']:
 assert sha(T/name)==sha(R/'runs/br042-all-vessels-v4-2h/tasks/all-vessels'/name)
s=types.ModuleType('frozen_score');exec(compile((T/'tests/score.py').read_text(),str(T/'tests/score.py'),'exec'),s.__dict__)
obj=json.loads((A/'centerlines.json').read_text());ref=json.loads((T/'tests/reference.json').read_text());m=s.evaluate(obj,ref)
assert m==json.loads((P/'verifier/metrics.json').read_text())
r=json.loads((P/'result.json').read_text());start=datetime.fromisoformat(r['agent_execution']['started_at'].replace('Z','+00:00'));end=datetime.fromisoformat(r['agent_execution']['finished_at'].replace('Z','+00:00'))
controls=[]
for phase,expected in [('oracle',1),('nop',0)]:
 p=next((R/'runs'/f'br042-all-vessels-{phase}-v4-6h-attempt1').glob('*/result.json'));c=json.loads(p.read_text());assert not c['exception_info'] and c['verifier_result']['rewards']['reward']==expected;controls.append(c['task_checksum'])
assert len(set(controls+[r['task_checksum']]))==1
trace=[]
for line in (P/'agent/codex.txt').read_text().splitlines():
 try:trace.append(json.loads(line))
 except ValueError:pass
errors=[x for x in trace if x.get('type')=='error' or x.get('item',{}).get('type')=='error'];assert trace[-1]['type']=='turn.failed'
old=json.loads((R/'groups/tubular-anatomy/experiments/br042/evaluations/br042-v4-2h-review.json').read_text())
comparison=[{'name':x['name'],'metrics':x['metrics'],'answer_sha256':x['answer_sha256']} for x in old['comparison']]
comparison.append({'name':'v4-6h astra-xhigh transport-interrupted','metrics':m,'answer_sha256':sha(A/'centerlines.json')})
im=nib.load(T/'environment/data/image.nii.gz');inv=np.linalg.inv(im.affine)
inside=all(((v:=nib.affines.apply_affine(inv,np.array(c['points_ras_mm'])))>=-1e-5).all() and (v<=np.array(im.shape)-1+1e-5).all() for c in obj['centerlines'])
record={'schema_version':1,'kind':'evaluation','id':'br042-v4-6h-saved-output-review','group_id':'tubular-anatomy','experiment_id':'br042-v4-6h','attempt_id':'attempt-28515356de5ce4cfbc389740','depends_on':['attempt-28515356de5ce4cfbc389740'],'classification':'transport_interrupted_partial_output_diagnostic','agent_seconds':(end-start).total_seconds(),'agent_execution':r['agent_execution'],'exception_type':r['exception_info']['exception_type'],'terminal_trace_event':trace[-1],'structured_transport_errors':errors,'frozen_bytes_verified':True,'controls_same_checksum':True,'exact_score_replay_agreement':True,'all_points_in_native_fov':bool(inside),'saved_points':sum(len(c['points_ras_mm']) for c in obj['centerlines']),'label_zero_polylines':sum(all(k==0 for k in c['labels']) for c in obj['centerlines']),'total_path_length_mm':sum(float(np.linalg.norm(np.diff(c['points_ras_mm'],axis=0),axis=1).sum()) for c in obj['centerlines']),'comparison':comparison,'evidence':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in [P/'result.json',P/'agent/codex.txt',P/'verifier/metrics.json',A/'centerlines.json',A/'method.md']],'limitations':['Transport termination before six-hour allowance; not a six-hour capacity result.','Preliminary method/inventory not brought up to date.','Scoring replay verified; extraction reproduction not independently demonstrated.','Broader vessels lack exhaustive reference or full image adjudication.']}
(G/'evaluations/saved-output-review.json').write_text(json.dumps(record,indent=2)+'\n')
# Reuse the existing native-CTA viewer in a fresh destination.
V=R/'runs/br042-all-vessels-v3/review';src=V/'v4-2h';out=V/'v4-6h';out.mkdir(exist_ok=True)
data=json.loads((src/'data.json').read_text());phase='v4-6h-astra-xhigh';data['models'].insert(0,{'phase':phase,'display_name':'V4 Astra/xhigh • 6h allowance, transport failure at 2h48m (partial)','summary':f"Transport failure before deadline. Saved-output geometry {m['geometry']['length_weighted_recall_1mm']:.1%}; correctly labeled {m['labeled']['length_weighted_recall_1mm']:.1%}. Both category gates fail.",'inventory_file':phase+'-method.md','inventory_label':'Preliminary method (outdated inventory)'})
for c in obj['centerlines']:
 pts=np.array(c['points_ras_mm']);data['curves'].append({'id':c['id'],'name':c['vessel_name'],'kind':phase,'labels':c['labels'],'points':pts.tolist(),'voxels':nib.affines.apply_affine(inv,pts).tolist()})
(out/'data.json').write_text(json.dumps(data));(out/'index.html').write_text((src/'index.html').read_text().replace('V3 / V4 two-hour comparison','V3 / V4 six-hour-attempt comparison'))
for x in data['models']:
 name=x['phase'];shutil.copy2(A/'centerlines.json' if name==phase else src/(name+'-centerlines.json'),out/(name+'-centerlines.json'));shutil.copy2(A/'method.md' if name==phase else src/x['inventory_file'],out/x['inventory_file'])
if (G/'review.md').exists():shutil.copy2(G/'review.md',out/'results.md')
print('SECONDS',record['agent_seconds'],'POINTS',record['saved_points'],'PATH_MM',record['total_path_length_mm'],'ZERO',record['label_zero_polylines'],'ERRORS',len(errors),'FOV',inside)
for x in comparison:
 q=x['metrics'];print(x['name'],*[round(100*q[k][v],2) for k in ['geometry','labeled'] for v in ['length_weighted_recall_1mm','macro_recall_1mm']])

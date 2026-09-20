"""Private post-run score replay and comparison; never imports historical authoring."""
from pathlib import Path
import json,hashlib,types,shutil
import numpy as np
import nibabel as nib
from scipy.ndimage import map_coordinates
ROOT=Path(__file__).resolve().parents[5]
B=ROOT/'runs/br042-all-vessels-v4-2h';T=B/'tasks/all-vessels'
P=ROOT/'runs/br042-all-vessels-astra-xhigh-v4-2h-attempt1/all-vessels__WjMQM7j';A=P/'artifacts/app/answer'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((B/'freeze.json').read_text());assert {str(p.relative_to(T)):sha(p) for p in T.rglob('*') if p.is_file()}==f['tasks'][0]['files']
s=types.ModuleType('frozen_score');exec(compile((T/'tests/score.py').read_text(),str(T/'tests/score.py'),'exec'),s.__dict__)
ref=json.loads((T/'tests/reference.json').read_text());r,rl,rw,ro=s.samples(ref)
rows=[]
for version in ['v2','v3']:
 for row in json.loads((ROOT/f'docs/evidence/br042-{version}-results.json').read_text())['runs']:
  if row['phase'] in ['oracle','nop'] or 'failed' in row['phase'] or not row.get('answer_path'):continue
  path=ROOT/row['answer_path']/'centerlines.json'
  if path.exists():rows.append((version+' '+row['phase'],path,bool(row.get('exception'))))
rows.append(('v4-2h astra-xhigh',A/'centerlines.json',True))
im=nib.load(T/'environment/data/image.nii.gz');vol=im.get_fdata(dtype=np.float32);inv=np.linalg.inv(im.affine)
comparison=[]
for name,path,partial in rows:
 obj=json.loads(path.read_text());m=s.evaluate(obj,ref);assert m['format_valid'];p,pl,pw,owner=s.samples(obj,True);d,ix=s.nearest(r,p)
 attrs={}
 for k in [4,5,6,7,10,11,14]:
  mask=(rl==k)&(d<=1);entries=[]
  for own in set(owner[ix[mask]]):
   z=mask&(owner[ix]==own);c=obj['centerlines'][int(own)]
   entries.append({'id':c['id'],'name':c['vessel_name'],'reference_mm':float(rw[z].sum()),'labels':sorted(set(int(j) for j in pl[ix[z]]))})
  attrs[str(k)]=sorted(entries,key=lambda a:-a['reference_mm'])
 comparison.append({'name':name,'partial':partial,'answer_path':str(path.relative_to(ROOT)),'answer_sha256':sha(path),'metrics':m,'match_attribution':attrs,'label_zero_polylines':sum(all(k==0 for k in c['labels']) for c in obj['centerlines'])})
new=comparison[-1];assert new['metrics']==json.loads((P/'verifier/metrics.json').read_text()),'Verifier/replay mismatch'
controls=[]
for phase in ['oracle','nop']:
 q=next((ROOT/'runs'/f'br042-all-vessels-{phase}-v4-2h-attempt1').glob('*/result.json'));x=json.loads(q.read_text());assert not x['exception_info'];assert x['verifier_result']['rewards']['reward']==int(phase=='oracle');controls.append(x['task_checksum'])
result=json.loads((P/'result.json').read_text());assert len(set(controls+[result['task_checksum']]))==1
obj=json.loads((A/'centerlines.json').read_text());audit=[]
for c in obj['centerlines']:
 p=np.array(c['points_ras_mm']);v=nib.affines.apply_affine(inv,p);hu=map_coordinates(vol,v.T,order=1,mode='nearest');audit.append({'id':c['id'],'name':c['vessel_name'],'points':len(p),'length_mm':float(np.linalg.norm(np.diff(p,axis=0),axis=1).sum()),'inside_fov':bool(((v>=-1e-5)&(v<=np.array(im.shape)-1+1e-5)).all()),'center_hu_p10_p50_p90':np.percentile(hu,[10,50,90]).tolist()})
assert all(c['inside_fov'] for c in audit)
receipt={'schema_version':1,'kind':'evaluation','id':'br042-v4-2h-independent-review','group_id':'tubular-anatomy','experiment_id':'tubular-anatomy-br042','classification':'timeout_partial_output_diagnostic','depends_on':['attempt-da47f4051e58e7e85a372af7'],'frozen_bytes_verified':True,'controls_same_checksum':True,'exact_score_replay_agreement':True,'execution':result['agent_execution'],'exception_type':result['exception_info']['exception_type'],'comparison':comparison,'native_audit':audit,'reproduction_claim_hash_matches':sha(A/'centerlines.json')==json.loads((A/'reproducibility.json').read_text())['centerlines_sha256'],'reproduction_limit':'Model-side clean replay logged; author independently replayed scoring, not extraction. Saved reviewed waypoints are case-specific products, not an autonomous rediscovery recipe.','evidence':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [P/'result.json',P/'verifier/metrics.json',A/'centerlines.json',A/'method.md',A/'reproducibility.json']], 'limitations':['Outcome-informed changed specification and doubled allowance; no causal or population comparison.','Timeout remains incomplete execution despite usable artifacts.','Noncoronary names and completeness lack exhaustive GT.']}
receipt['attempt_id']='attempt-da47f4051e58e7e85a372af7'
receipt['checkpoint_diagnostic']=s.evaluate(json.loads((A/'checkpoint/centerlines.json').read_text()),ref)
receipt['transport_errors']=[json.loads(line)['message'] for line in (P/'agent/codex.txt').read_text().splitlines() if line.startswith('{') and json.loads(line).get('type')=='error']
out=ROOT/'groups/tubular-anatomy/experiments/br042/evaluations/br042-v4-2h-review.json';out.write_text(json.dumps(receipt,indent=2)+'\n')
# Fresh local comparison viewer: previous three runs remain unchanged.
old=ROOT/'runs/br042-all-vessels-v3/review';O=old/'v4-2h';O.mkdir(exist_ok=True)
data=json.loads((old/'data.json').read_text());phase='v4-2h-astra-xhigh';m=new['metrics'];data['models'].insert(0,{'phase':phase,'display_name':'V4 Astra/xhigh • 2h timeout (partial)','summary':f"Timed out at 7200 seconds; saved-output diagnostics. Geometry {m['geometry']['length_weighted_recall_1mm']:.1%}; correctly labeled {m['labeled']['length_weighted_recall_1mm']:.1%}. Both coverage gates fail.",'inventory_file':phase+'-method.md','inventory_label':'Saved method / uncertainty inventory'})
for c in obj['centerlines']:
 p=np.array(c['points_ras_mm']);data['curves'].append({'id':c['id'],'name':c['vessel_name'],'kind':phase,'labels':c['labels'],'points':p.tolist(),'voxels':nib.affines.apply_affine(inv,p).tolist()})
(O/'data.json').write_text(json.dumps(data))
html=(old/'index.html').read_text();html=html.replace("im.src='slices/'","im.src='../slices/'").replace('All-vessel CTA review · V3 comparison','All-vessel CTA review · V3 / V4 two-hour comparison');(O/'index.html').write_text(html)
for model in data['models']:
 phase=model['phase'];source=A/'centerlines.json' if phase=='v4-2h-astra-xhigh' else old/(phase+'-centerlines.json');shutil.copy2(source,O/(phase+'-centerlines.json'))
 source=A/'method.md' if phase=='v4-2h-astra-xhigh' else old/model['inventory_file'];shutil.copy2(source,O/model['inventory_file'])
for c in comparison:
 m=c['metrics'];print(c['name'],m['polylines'],c['label_zero_polylines'],*[round(100*m[t][v],1) for t in ['geometry','labeled'] for v in ['length_weighted_recall_1mm','macro_recall_1mm']])
print('new branch attribution',json.dumps(new['match_attribution'],indent=2))

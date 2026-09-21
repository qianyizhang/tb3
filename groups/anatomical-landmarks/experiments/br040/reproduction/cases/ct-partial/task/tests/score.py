"""Separate invented detections, visibility classification, localization, extrapolation."""
import json, math
from pathlib import Path

def distance(a,b,linear):
 d=[a[j]-b[j] for j in range(3)]
 return math.sqrt(sum(sum(linear[i][j]*d[j] for j in range(3))**2 for i in range(3)))

def triple(p):
 return isinstance(p,list) and len(p)==3 and all(type(x) in (int,float) and math.isfinite(x) for x in p)

def score(answer,truth):
 try:
  assert isinstance(answer,dict) and set(answer)=={'space','landmarks'} and answer['space']=='voxel_ijk_zero_based'
  pred=answer['landmarks'];assert isinstance(pred,dict) and set(pred)==set(truth['targets'])
  rows={};counts={s:0 for s in ['observed','out_of_fov','absent']};hall={s:0 for s in ['out_of_fov','absent']};correct=dict(hall);uncertain=dict(hall)
  errors={};extrap={};missed=0;confusion={}
  for key,gt in truth['targets'].items():
   r=pred[key];assert isinstance(r,dict) and set(r)=={'status','ijk'}
   status=r['status'];p=r['ijk'];assert status in ('observed','out_of_fov','absent','uncertain')
   assert p is None or triple(p)
   if status=='observed':assert triple(p) and all(-.5<=p[j]<=truth['shape_ijk'][j]-.5 for j in range(3))
   if status in ('uncertain','absent'):assert p is None
   if status=='out_of_fov' and p is not None:assert any(p[j]<-.5 or p[j]>truth['shape_ijk'][j]-.5 for j in range(3))
   expected=gt['status'];counts[expected]+=1;ck=f'{expected}->{status}';confusion[ck]=confusion.get(ck,0)+1
   row={'truth_status':expected,'predicted_status':status,'predicted_ijk':p}
   if expected=='observed':
    if status=='observed':errors[key]=distance(p,gt['ijk'],truth['linear_voxel_to_mm']);row['error_mm']=errors[key]
    else:missed+=1
   else:
    hall[expected]+=status=='observed';correct[expected]+=status==expected;uncertain[expected]+=status=='uncertain'
    if expected=='out_of_fov' and status=='out_of_fov' and p is not None:extrap[key]=distance(p,gt['ijk'],truth['linear_voxel_to_mm'])
   rows[key]=row
  sdr={str(t):sum(e<=t for e in errors.values()) for t in (5,10,20)};neg=counts['out_of_fov']+counts['absent']
  return {'contract_valid':True,'reward':int(sdr['5']==counts['observed'] and sum(correct.values())==neg),'requested':len(rows),'counts':counts,'hallucinated':hall,'hallucination_rate':sum(hall.values())/neg if neg else None,'correct_rejections':correct,'uncertain_rejections':uncertain,'confusion':confusion,'missed_visible':missed,'localized_visible':len(errors),'success_counts_mm':sdr,'errors_mm':errors,'mean_localized_error_mm':sum(errors.values())/len(errors) if errors else None,'extrapolation_errors_mm':extrap,'rows':rows}
 except (AssertionError,TypeError,KeyError,ValueError,OverflowError):return {'reward':0,'contract_valid':False,'invalid':'Require all keys with status and native ijk; observed inside, extrapolation outside, absent/uncertain null.'}

if __name__=='__main__':
 truth=json.loads(Path('/verifier/truth.json').read_text())
 try:answer=json.loads(Path('/app/answer/landmarks.json').read_text())
 except (OSError,ValueError):answer=None
 out=score(answer,truth);p=Path('/logs/verifier');p.mkdir(parents=True,exist_ok=True)
 (p/'details.json').write_text(json.dumps(out,indent=2));(p/'reward.txt').write_text(str(out['reward']))

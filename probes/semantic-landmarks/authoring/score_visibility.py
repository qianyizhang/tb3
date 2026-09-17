"""Score named points with verified out-of-FOV nulls or bounded extrapolation."""
import json,math
from pathlib import Path

def score(answer,truth):
 try:
  assert isinstance(answer,dict) and set(answer)==set(truth['points'])
  errors={};status={};accepted={};out=truth['outside'];lo=truth['bounds_min'];hi=truth['bounds_max']
  for k,gt in truth['points'].items():
   p=answer[k]
   if p is None or p==[]:
    status[k]='empty';accepted[k]=k in out;continue
   assert isinstance(p,list) and len(p)==3 and all(type(x) in (int,float) and math.isfinite(x) for x in p)
   errors[k]=math.dist(p,gt);beyond=any(p[i]<lo[i] or p[i]>hi[i] for i in range(3));status[k]='extrapolated' if beyond else 'in_view'
   accepted[k]=(beyond and errors[k]<=truth['outside_tolerance_mm']) if k in out else (not beyond and errors[k]<=truth['inside_tolerance_mm'])
  return {'reward':int(all(accepted.values())),'accepted':accepted,'accepted_count':sum(accepted.values()),'total':len(accepted),'errors_mm':errors,'status':status,'outside_gt':out,'outside_correct':sum(accepted[k] for k in out),'inside_correct':sum(v for k,v in accepted.items() if k not in out)}
 except (AssertionError,TypeError,ValueError):return {'reward':0,'invalid':'Exact named finite triples or null/[] required'}
if __name__=='__main__':
 t=json.loads(Path('/verifier/truth.json').read_text())
 try:a=json.loads(Path('/app/answer/landmarks.json').read_text())
 except (OSError,ValueError):a=None
 out=score(a,t);p=Path('/logs/verifier');p.mkdir(parents=True,exist_ok=True);(p/'details.json').write_text(json.dumps(out,indent=2));(p/'reward.txt').write_text(str(out['reward']))

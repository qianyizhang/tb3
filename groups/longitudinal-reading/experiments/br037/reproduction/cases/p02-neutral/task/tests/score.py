"""Mechanical contract gate only. Clinical grading is a separate authored review."""
from pathlib import Path
import json,math
def validate(answer,manifest):
 errors=[];series={s['id']:s for s in manifest['series']}
 try:
  assert isinstance(answer['observations'],list) and len(answer['observations'])>=2
  visits=set()
  for o in answer['observations']:
   s=series[o['series_id']];assert o['visit']==s['visit'];visits.add(o['visit'])
   assert isinstance(o['description'],str) and o['description'].strip()
   assert len(o['voxel'])==3 and all(isinstance(v,(int,float)) and math.isfinite(v) and 0<=v<s['shape'][i] for i,v in enumerate(o['voxel']))
   assert isinstance(o['phase'],int) and 0<=o['phase']<(s['shape'][3] if len(s['shape'])==4 else 1)
  assert visits=={'V1','V2'}
  assert answer['primary_location']['laterality'] in ['left','right','bilateral','midline','none','indeterminate']
  assert isinstance(answer['primary_location']['organ'],str)
  enum=['smaller','similar','larger','mixed','indeterminate']
  c=answer['comparison'];assert c['extent_trend'] in enum
  assert isinstance(c['size_measurements_mm'],list)
  for m in c['size_measurements_mm']:
   assert m['visit'] in visits and isinstance(m['method'],str)
   assert m['longest_diameter_mm'] is None or (isinstance(m['longest_diameter_mm'],(int,float)) and math.isfinite(m['longest_diameter_mm']) and m['longest_diameter_mm']>=0)
  for k in ['signal_behavior','morphology_and_distribution','summary']:assert isinstance(c[k],str) and c[k].strip()
  i=answer['impression'];assert isinstance(i['leading_explanation'],str) and i['leading_explanation'].strip();assert isinstance(i['alternatives'],list) and isinstance(i['limitations'],list)
  f=answer['forecast'];assert f['next_exam_extent'] in ['smaller','similar','larger','indeterminate'];assert isinstance(f['basis'],str) and isinstance(f['assumptions'],list)
  for obj in [i,f]:assert isinstance(obj['confidence'],(int,float)) and math.isfinite(obj['confidence']) and 0<=obj['confidence']<=1
 except (KeyError,TypeError,AssertionError,IndexError) as e:errors.append(f'{type(e).__name__}: invalid or missing contract field')
 return dict(contract_pass=not errors,errors=errors,clinical_accuracy='Not scored by this program')
if __name__=='__main__':
 try:
  result=validate(json.loads(Path('/app/answer/assessment.json').read_text()),json.loads(Path('/verifier/manifest.json').read_text()))
  if not Path('/app/answer/report.md').exists():result['contract_pass']=False;result['errors'].append('Missing report.md')
 except Exception as e:result=dict(contract_pass=False,errors=[str(e)],clinical_accuracy='Not scored')
 out=Path('/logs/verifier');out.mkdir(parents=True,exist_ok=True);(out/'contract.json').write_text(json.dumps(result,indent=2));(out/'reward.txt').write_text(str(int(result['contract_pass']))+'\n');print(json.dumps(result))

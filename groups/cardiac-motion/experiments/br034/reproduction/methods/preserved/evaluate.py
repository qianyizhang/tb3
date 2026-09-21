"""Score a frozen submitted-program transfer; no historical authoring imports."""
import argparse,json,tempfile,shutil
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--answer',type=Path,required=True);a=p.parse_args()
here=Path(__file__).resolve().parent
root=here.parents[1]
from score import score,volumes,distances
kind='preserved'
program=root/'saved/attempt-6b21a9a7f0bb2138fcedf09a/answer'
ev=json.loads((here/'criteria.json').read_text());shift=ev['phase_shift_frames']
pred=np.load(a.answer/'prediction.npz');v=volumes(pred['points'],pred['faces'])
r={'ef_pct':float(100*(1-v.min()/v.max())),'volume_ml':v.tolist(),'motion_rms_mm':float(np.sqrt(np.mean(np.sum((pred['points']-pred['points'][:1])**2,axis=-1))))}
if kind in ['original','patient','preserved']:
 with tempfile.TemporaryDirectory() as temp:
  grade=Path(temp)/'grading';shutil.copytree(a.answer,grade)
  for name in ['solve.py','method.md']:
   if not (grade/name).exists() and (program/name).exists():shutil.copyfile(program/name,grade/name)
  r['grade']=score(grade,here/'reference.npz')
base=np.load(program/'prediction.npz');basev=volumes(base['points'],base['faces'])
if kind in ['original','static','shift']:
 q=np.roll(pred['points'],-shift,axis=0) if kind=='shift' else pred['points']
 qv=np.roll(v,-shift) if kind=='shift' else v
 r['original_volume_mae_ml']=float(np.mean(abs(qv-basev)))
 r['original_surface_mean_mm']=float(np.mean([distances(x,pred['faces'],y,base['faces'])[0] for x,y in zip(q,base['points'])]))
 if q.shape==base['points'].shape:r['original_coordinate_max_abs_mm']=float(abs(q-base['points']).max())
if kind=='static':r['input_response_pass']=r['ef_pct']<=ev['static_ef_max_pp'] and r['motion_rms_mm']<=ev['static_motion_rms_max_mm']
if kind=='shift':r['input_response_pass']=r['original_volume_mae_ml']<=ev['shift_volume_mae_max_ml']
print(json.dumps(r,allow_nan=False))

"""Public-input final-stage interventions on Sol's literal item_26 code."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--variant', required=True, choices=[
    'final_stage_replay', 'early_selected_q04', 'raw_top_q04',
    'single_small_patch', 'no_final_refinement'])
args = parser.parse_args()
source = Path('/recovered/item_26-0.py').read_text()
source_hash = hashlib.sha256(source.encode()).hexdigest()
old = "sets=[([5,7,9],[.4,.35,.25]),([5,7,9,11],[.3,.3,.25,.15]),([5,7,9,11],[.5,.3,.15,.05]),([7,9,11],[.4,.35,.25])]"
assert source.count(old) == 1
source = source.replace(old, "sets=[([5],[1.0])]" if args.variant == 'single_small_patch'
                        else "sets=[([5,7,9],[.4,.35,.25])]")
if args.variant in ['early_selected_q04', 'raw_top_q04']:
    original = '[139,86,105]'
    replacement = '[146,84,103]' if args.variant == 'early_selected_q04' else '[126,79,118]'
    assert source.count(original) == 1
    source = source.replace(original, replacement)
line = "  s=np.array(start,float);res=minimize(fun,s,method='Powell',bounds=[(a-3,a+3) for a in s],options={'maxiter':1000,'xtol':1e-5,'ftol':1e-8})"
assert source.count(line) == 1
if args.variant == 'no_final_refinement':
    source = source.replace(line, "  s=np.array(start,float);res=SimpleNamespace(x=s,fun=fun(s),nfev=1)")
needle = "  print('weights',weights,'vox',np.round(res.x,3),'world',np.round(res.x*np.diag(A)[:3],2),'ncc',round(-res.fun,4))"
assert source.count(needle) == 1
source = source.replace(needle, needle + "\n  records.append({'id':id,'initial_voxel':s.tolist(),'final_voxel':res.x.tolist(),'world_unrounded_mm':(res.x*np.diag(A)[:3]).tolist(),'world_rounded_mm':np.round(res.x*np.diag(A)[:3],2).tolist(),'score':float(-res.fun),'nfev':int(res.nfev)})")
from types import SimpleNamespace
scope = {'records': [], 'SimpleNamespace': SimpleNamespace}
exec(compile(source, '/sol-final-stage.py', 'exec'), scope)
records = scope['records']
result = {'variant': args.variant, 'recovered_source_sha256': source_hash,
          'query_ids': [r['id'] for r in records],
          'points_world_mm': [r['world_rounded_mm'] for r in records],
          'diagnostics': records,
          'scope': 'Final-stage replay with original public-derived starts; earlier semantic decisions are retained as recorded choices, not autonomously rerun.'}
Path('/output/points.json').write_text(json.dumps(result, indent=2) + '\n')

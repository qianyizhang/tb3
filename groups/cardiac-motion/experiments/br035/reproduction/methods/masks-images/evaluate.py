"""Score a frozen submitted-program transfer; no historical authoring imports."""
import argparse,json,tempfile,shutil
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--answer',type=Path,required=True);a=p.parse_args()
here=Path(__file__).resolve().parent
root=here.parents[1]
from score import score
r={'grade':score(a.answer/'prediction.npz',here/'input')}
assessment=a.answer/'assessment.json';r['assessment']=json.loads(assessment.read_text()) if assessment.exists() else None
preparation=json.loads((here/'preparation.json').read_text());cf=r['grade'].get('cavity_function')
if cf:
 cf['clinical_surface_reference_ef_pct']=preparation['clinical_reference_ef_pct']
 cf['clinical_surface_ef_error_pp']=abs(cf['ef_pct']-preparation['clinical_reference_ef_pct'])
print(json.dumps(r,allow_nan=False))

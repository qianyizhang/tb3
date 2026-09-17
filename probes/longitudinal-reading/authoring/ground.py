"""Extract independent host-only core-lab regions and measurement references."""
from pathlib import Path
import json
import numpy as np
import pydicom
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading'
selected=json.loads((B/'selected.json').read_text());out=[]
for c in selected:
 refs=[]
 for folder in sorted((B/'source/private-reference'/c['case']).glob('*/*/*/*')):
  paths=list(folder.glob('*.dcm'))
  if not paths:continue
  d=pydicom.dcmread(paths[0],stop_before_pixels=True)
  visit=int(str(d.StudyDescription)[-1]);seq=d[(0x117,0x1020)].value
  roi=seq[0];center=np.array(roi[(0x117,0x1042)].value,float)*[-1,-1,1]
  ftv=[float(x[(0x117,0x10b4)].value) for x in d[(0x117,0x10b0)].value]
  spreadsheet=float(c['labels'][f'VOLUME_TUM_BLU_V{visit+1}0'])
  assert np.isclose(ftv[0],spreadsheet,rtol=1e-4,atol=1e-5),(ftv,spreadsheet)
  refs.append(dict(visit=f'V{visit+1}',laterality=str(d[(0x117,0x1098)].value),voi_center_ras_mm=center.tolist(),voi_half_vectors_lps_mm=[list(map(float,roi[(0x117,x)].value)) for x in [0x1043,0x1044,0x1045]],ftv_cc=ftv[0],ftv_washout_cc=ftv[1],source=str(paths[0].relative_to(B))))
 refs.sort(key=lambda x:x['visit']);assert len(refs)==2
 out.append(dict(case=c['case'],source_id=c['source_id'],source_stratum=c['stratum'],labels=c['labels'],references=refs,measurement_interpretation='FTV is thresholded enhancement within a core-lab VOI; not interchangeable with diameter or microscopic viable disease. VOI is not an exact lesion contour.',clinical_adjudication='None; morphology and diagnosis interpretations require review.'))
(B/'grounding.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps([{k:c[k] for k in ['case','references']} for c in out],indent=2))

"""Reference-only ACRIN shortlist; images remain unadmitted pending access."""
from pathlib import Path
import json,collections
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading';d=json.loads((B/'source/brain-clinical.json').read_text())
rows=[dict(split='75' if 'Training-75' in k else '25',**r) for k,v in d.items() if k.endswith('/S1.csv') for r in v]
groups=collections.defaultdict(list)
for r in rows:groups[(r['cn'],r['S1e2d'])].append(r)
candidates=[]
for (cn,day),rs in sorted(groups.items(),key=lambda x:(int(x[0][0]),int(x[0][1]))):
 valid=[r for r in rs if r['s1e5'] in ['1','2','3','4']]
 codes={r['s1e5'] for r in valid}
 if len(valid)<2:continue
 if len(codes)>1:stratum='reader_disagreement'
 elif codes=={'4'}:stratum='concordant_progression'
 elif codes=={'2'}:stratum='concordant_partial_response'
 else:continue
 if stratum in [c['stratum'] for c in candidates]:continue
 candidates.append(dict(reference_patient_cn=cn,day_from_trial_base=int(day),stratum=stratum,reader_rows=rs,status='Metadata shortlist only. Source cn-to-DICOM linkage, image completeness and clinical interpretation not yet admitted.'))
out=dict(collection='ACRIN-DSC-MR-Brain',access='Controlled imaging; open clinical data only inspected',reference_records=len(rows),candidates=candidates,limitation='S1e9 repeats the 3D label in the source dictionary. Do not silently resolve it as FLAIR without protocol confirmation. Adjudication rows and timepoint mapping need case-specific review.')
(B/'brain-triage.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

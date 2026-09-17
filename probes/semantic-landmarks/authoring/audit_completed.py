"""Audit recorded external calls, model settings and geometric evidence."""
from pathlib import Path
import json,hashlib
import numpy as np,nibabel as nib
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br036-semantic-landmarks'
out=[]
for row in json.loads((B/'results.json').read_text())['trials']:
 if row['phase']!='terra-high':continue
 case=row['case'];trial=(ROOT/row['result_path']).parent;t=json.loads((trial/'agent/trajectory.json').read_text())
 calls=[q for s in t['steps'] for q in s.get('tool_calls',[])];web=[q['arguments'] for q in calls if 'web__run' in str(q)]
 cfg=json.loads((B/'configs'/f'br036-{case}-terra-high-v1-20260917.json').read_text());a=cfg['agents'][0]
 assert a['model_name']=='openai/gpt-5.6-terra' and a['kwargs']['reasoning_effort']=='high'
 out.append({'case':case,'runtime_model':row['agent_info']['model_info'],'configured_effort':a['kwargs']['reasoning_effort'],'tool_call_count':len(calls),'web_calls':web,'trajectory_sha256':hashlib.sha256((trial/'agent/trajectory.json').read_bytes()).hexdigest(),'source_exposure_review':'General AFIDs/MNI-coordinate search returned protocol and dataset documentation; no observed subject-specific annotation retrieval.' if web else 'No web calls observed; recorded shell commands separately reviewed for retrieval.'})
record={'round':'BR-036','trials':out,'interpretation':{'ct_full':'Predictions fall near named structures. Left condyle error is dominated by a 6 mm inferior shift; chin also has a lateral offset. No gross LPS/RAS sign inversion.','mri32_crop':'Submitted AC=[0,0,0] and PC=[0,-24,0]. Public commentary assumes AC-PC alignment. All 32 predictions were inside and called observed. Subject-space source AC is [0.604,17.962,-18.594]; native reference overlays and derivative metadata support the supplied frame. This suggests inappropriate coordinate anchoring, not proof of a single causal mechanism.','mri_full':'No observed web lookup. Errors persist with full volume and eight queries. No causal comparison to 32/crop because query set and attempt differ.'}}
(ROOT/'docs/evidence/br036-trace-review.json').write_text(json.dumps(record,indent=2)+'\n')
print('Audited',len(out),'completed traces')

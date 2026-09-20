"""Collect completed controls/trial; independently replay physical distances."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
from scipy.spatial.distance import cdist
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br041-image-only-centerline'
sys.path.insert(0,str(Path(__file__).resolve().parent));from score import score
f=json.loads((B/'freeze.json').read_text());t=f['tasks'][0];tp=ROOT/t['task_path']
assert {str(p.relative_to(tp)):hashlib.sha256(p.read_bytes()).hexdigest() for p in tp.rglob('*') if p.is_file()}==t['files']
rows=[]
for phase in ['oracle','nop','terra-high']:
    job=ROOT/'runs'/f'br041-named-rca-{phase}-v1-20260919';ps=list(job.glob('*/result.json'));assert len(ps)==1
    r=json.loads(ps[0].read_text());trial=ps[0].parent
    row={'phase':phase,'result_path':str(ps[0].relative_to(ROOT)),'exception':r.get('exception_info'),'task_checksum':r['task_checksum'],'reward':(r.get('verifier_result') or {}).get('rewards'),'agent_execution':r.get('agent_execution')}
    mp=trial/'verifier/metrics.json'
    if mp.exists():row['score']=json.loads(mp.read_text())
    answer=trial/'artifacts/app/answer'
    if (answer/'centerline.npy').exists():
        row['replay']=score(answer,tp/'tests/reference.npy');assert row['replay']==row['score']
        ref=np.load(tp/'tests/reference.npy');line=np.load(answer/'centerline.npy');d=cdist(line,ref)
        independent={'p95_distance_mm':float(np.percentile(d.min(axis=1),95)),'coverage_within_1mm':float((d.min(axis=0)<=1).mean()),'coverage_within_2mm':float((d.min(axis=0)<=2).mean())}
        assert all(np.isclose(v,row['score']['metrics'][k]) for k,v in independent.items());row['independent']=independent
        row['answer_path']=str(answer.relative_to(ROOT))
    rows.append(row)
assert len({r['task_checksum'] for r in rows})==1
out={'round':'BR-041','frozen_bytes_verified':True,'same_task_checksum':True,'runs':rows,'local_controls':json.loads((B/'validation.json').read_text())}
(B/'results.json').write_text(json.dumps(out,indent=2)+'\n');(ROOT/'docs/evidence/br041-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

"""Collect immutable outputs, replay scoring and independently check distances."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from scipy.spatial.distance import cdist
from score import score,samples
from run_trials import ROOT,B,verify
if __name__=='__main__':
 task=json.loads((B/'freeze.json').read_text())['tasks'][0];verify(task);tp=ROOT/task['task_path'];rows=[]
 for phase in ['oracle','nop','astra-medium']:
  paths=list((ROOT/'runs'/f'br042-all-vessels-{phase}-v2-20260920').glob('*/result.json'));assert len(paths)==1
  path=paths[0];r=json.loads(path.read_text());trial=path.parent
  row={'phase':phase,'result_path':str(path.relative_to(ROOT)),'task_checksum':r['task_checksum'],'exception':r.get('exception_info'),'agent_execution':r.get('agent_execution'),'agent_result':r.get('agent_result'),'reward':(r.get('verifier_result') or {}).get('rewards')}
  metric=trial/'verifier/metrics.json'
  if metric.exists():row['score']=json.loads(metric.read_text())
  ans=trial/'artifacts/app/answer'
  if (ans/'centerlines.json').exists():
   replay=score(ans,tp/'tests/reference.json');assert replay==row['score'];row['replay_matches']=True
   row['answer_path']=str(ans.relative_to(ROOT));row['answer_sha256']=hashlib.sha256((ans/'centerlines.json').read_bytes()).hexdigest()
   if replay['format_valid']:
    p,pl,pw=samples(json.loads((ans/'centerlines.json').read_text()));q,ql,qw=samples(json.loads((tp/'tests/reference.json').read_text()))
    pd=np.full(len(p),np.inf);qd=np.full(len(q),np.inf);same=np.full(len(p),np.inf);sameq=np.full(len(q),np.inf)
    for i in range(0,len(p),128):
     d=cdist(p[i:i+128],q);pd[i:i+128]=d.min(1);qd=np.minimum(qd,d.min(0));d[pl[i:i+128,None]!=ql[None,:]]=np.inf;same[i:i+128]=d.min(1);sameq=np.minimum(sameq,d.min(0))
    independent={'unlabeled_precision_1mm':float(np.average(pd<=1,weights=pw)),'unlabeled_recall_1mm':float(np.average(qd<=1,weights=qw)),'labeled_precision_1mm':float(np.average(same[pl>0]<=1,weights=pw[pl>0]) if (pl>0).any() else 0.),'macro_labeled_recall_1mm':float(np.mean([np.average(sameq[ql==k]<=1,weights=qw[ql==k]) for k in np.unique(ql)]))}
    assert all(np.isclose(v,replay[k]) for k,v in independent.items());row['independent_dense_distances']=independent
    cp=p[pl>0]; cw=pw[pl>0]
    if len(cp):
     cd=np.full(len(cp),np.inf); cq=np.full(len(q),np.inf)
     for j in range(0,len(cp),128):
      dist=cdist(cp[j:j+128],q);cd[j:j+128]=dist.min(1);cq=np.minimum(cq,dist.min(0))
     row['coronary_only_geometry_diagnostic']={'precision_1mm':float(np.average(cd<=1,weights=cw)),'recall_1mm':float(np.average(cq<=1,weights=qw)),'recall_2mm':float(np.average(cq<=2,weights=qw)),'submitted_length_outside_1mm_reference_mm':float(cw[cd>1].sum()),'note':'Post-hoc correction of diagnostic population: frozen unlabeled metrics include code-0 vessels. Primary labeled coverage and reward are unaffected.'}
  if phase=='astra-medium':
   contexts=[];calls=[]
   for session in (trial/'agent/sessions').rglob('*.jsonl'):
    for line in session.read_text().splitlines():
     try:event=json.loads(line)
     except ValueError:continue
     payload=event.get('payload',{})
     if event.get('type')=='turn_context':contexts.append({k:payload.get(k) for k in ['model','effort']})
     if payload.get('type') in ['custom_tool_call','function_call']:calls.append(payload.get('input',payload.get('arguments','')))
   row['trace_audit']={'contexts':contexts[:1],'image_view_call_candidates':sum('view_image' in s for s in calls),'external_access_call_candidates':[s[:2000] for s in calls if any(k in s for k in ['curl ','wget ','requests.','httpx.'])],'note':'String candidates require manual inspection; context is runtime configuration, not provider identity attestation.'}
  rows.append(row)
 assert len({r['task_checksum'] for r in rows})==1
 out={'round':'BR-042','frozen_bytes_verified':True,'same_task_checksum':True,'runs':rows}
 for p in [B/'results.json',ROOT/'docs/evidence/br042-v2-results.json']:p.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))

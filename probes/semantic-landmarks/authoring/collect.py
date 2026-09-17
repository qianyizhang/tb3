"""Collect completed trials without exposing private runtime credentials."""
import json,hashlib
from pathlib import Path
from score import score
from score_visibility import score as score_visibility
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br036-semantic-landmarks'
rows=[]
tasks=json.loads((B/'freeze.json').read_text())['tasks'] + json.loads((B/'expanded-freeze.json').read_text())['tasks']
for t in tasks:
 task=ROOT/t['task_path'];assert {str(f.relative_to(task)):hashlib.sha256(f.read_bytes()).hexdigest() for f in task.rglob('*') if f.is_file()}==t['files']
 for phase in ['oracle','nop','terra-high']:
  job=f"br036-{t['task']}-{phase}-v1-20260917";results=list((ROOT/'runs'/job).glob('*/result.json'))
  if not results:continue
  p=results[0];r=json.loads(p.read_text());details=list(p.parent.glob('verifier/details.json'))
  row={'case':t['task'],'phase':phase,'result_path':str(p.relative_to(ROOT)),'task_checksum':r.get('task_checksum'),'exception':r.get('exception_info'),'reward':(r.get('verifier_result') or {}).get('rewards',{}).get('reward'),'agent_execution':r.get('agent_execution'),'agent_info':r.get('agent_info')}
  if details:row['score']=json.loads(details[0].read_text())
  answers=list(p.parent.rglob('landmarks.json'))
  # Only saved agent artifacts count as a submission; never fallback to solution key.
  answers=[a for a in answers if 'artifacts' in a.parts and 'answer' in a.parts]
  if answers:
   ans=json.loads(answers[0].read_text());truth=json.loads((task/'tests/truth.json').read_text());row['host_rescore']=(score_visibility if 'outside' in truth else score)(ans,truth);row['answer_path']=str(answers[0].relative_to(ROOT))
   assert row['host_rescore']['reward']==row['reward']
  traj=p.parent/'agent/trajectory.json'
  if traj.exists():row['trajectory_sha256']=hashlib.sha256(traj.read_bytes()).hexdigest()
  rows.append(row)
out={'round':'BR-036','trials':rows,'limitations':['Two source-order subjects, four conditions, one attempt per condition.','Public-source training exposure cannot be excluded.','Reference agreement is not clinical validation.']}
(B/'results.json').write_text(json.dumps(out,indent=2)+'\n');(ROOT/'docs/evidence/br036-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

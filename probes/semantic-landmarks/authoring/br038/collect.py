"""Import completed runs and independently rescore voxel submissions in world space."""
from pathlib import Path
import json,hashlib,datetime,ast
import numpy as np,nibabel as nib
from score import score
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br038-volume-landmarks';OLD=ROOT/'runs/br036-semantic-landmarks'
rows=[]
for t in json.loads((B/'freeze.json').read_text())['tasks']:
 task=ROOT/t['task_path'];assert {str(f.relative_to(task)):hashlib.sha256(f.read_bytes()).hexdigest() for f in task.rglob('*') if f.is_file()}==t['files']
 for phase in ['oracle','nop','terra-high']:
  job=f"br038-{t['task']}-{phase}-v1-20260917";ps=list((ROOT/'runs'/job).glob('*/result.json'))
  if not ps:continue
  p=ps[0];r=json.loads(p.read_text());v=r.get('verifier_result') or {};e=r.get('agent_execution') or {};sfile=p.parent/'verifier/details.json'
  row={'case':t['task'],'phase':phase,'result_path':str(p.relative_to(ROOT)),'reward':v.get('rewards',{}).get('reward'),'exception':r.get('exception_info'),'task_checksum':r.get('task_checksum'),'agent_info':r.get('agent_info')}
  if e.get('started_at') and e.get('finished_at'):row['agent_seconds']=(datetime.datetime.fromisoformat(e['finished_at'].replace('Z','+00:00'))-datetime.datetime.fromisoformat(e['started_at'].replace('Z','+00:00'))).total_seconds()
  if sfile.exists():row['score']=json.loads(sfile.read_text())
  ap=p.parent/'artifacts/app/answer/landmarks.json'
  if ap.exists():
   ans=json.loads(ap.read_text());truth=json.loads((task/'tests/truth.json').read_text());host=score(ans,truth);assert host==row['score'];row['host_replay_exact']=True
   if host.get('contract_valid'):
    ni=nib.load(task/'environment/volume.nii.gz')
    ras=json.loads((OLD/'all32-reference.json').read_text())['points_ras_mm'] if t['task'].startswith('mri') else json.loads((OLD/'tasks/ct-C001/tests/truth.json').read_text())['points_ras_mm']
    errors={k:float(np.linalg.norm(nib.affines.apply_affine(ni.affine,point)-ras[k])) for k,point in ans['landmarks'].items()}
    maxdiff=max(abs(errors[k]-host['errors_mm'][k]) for k in errors);assert maxdiff<1e-5;row['independent_world_rescore_max_difference_mm']=maxdiff
  if phase=='terra-high':
   cfg=json.loads((B/'configs'/f'{job}.json').read_text());row['configured_model']=cfg['agents'][0]['model_name'];row['configured_effort']=cfg['agents'][0]['kwargs']['reasoning_effort']
   traj=p.parent/'agent/trajectory.json'
   if traj.exists():
    tr=json.loads(traj.read_text());row['trajectory_sha256']=hashlib.sha256(traj.read_bytes()).hexdigest();calls=[c for s in tr['steps'] for c in s.get('tool_calls',[])];row['tool_call_count']=len(calls);row['public_web_calls']=[c['arguments'] for c in calls if 'web__run' in str(c)];row['coordinate_check_called']=any('volume_tools.py check' in str(c) for c in calls);row['provided_viewer_called']=any('volume_tools.py view' in str(c) for c in calls)
  rows.append(row)
result={'round':'BR-038','trials':rows,'limitations':['Two subjects and one attempt per task.','New output representation, complete scan and display helper; not a single-factor intervention.','Reference anatomy not independently clinically adjudicated.']}
(B/'results.json').write_text(json.dumps(result,indent=2)+'\n');(ROOT/'docs/evidence/br038-results.json').write_text(json.dumps(result,indent=2)+'\n')
for r in rows:
 if r['phase']=='terra-high':print(r['case'],r.get('score'),r.get('agent_seconds'))

"""Replay frozen verifiers, compare world distances, audit actual image inputs."""
from pathlib import Path
import json,datetime,collections
import numpy as np,nibabel as nib
from run_trials import ROOT,B,CASES,task,verify,sha,previous

def audit(base):
 count=0;hashes={};candidates=[];model_settings=set()
 def walk(x):
  nonlocal count
  if isinstance(x,dict):
   if x.get('type')=='input_image':count+=1
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 for p in base.glob('sessions/**/*.jsonl'):
  hashes[str(p.relative_to(ROOT))]=sha(p)
  for line in p.read_text().splitlines():
   try:
    event=json.loads(line);walk(event)
    if event.get('type')=='turn_context':
     q=event['payload'];model_settings.add((q.get('model'),q.get('effort')))
   except ValueError:pass
 tr=base/'trajectory.json';calls=[]
 if tr.exists():
  for step in json.loads(tr.read_text())['steps']:calls.extend(step.get('tool_calls',[]))
  for c in calls:
   a=str(c.get('arguments',''))
   if any(q in a.lower() for q in ['web__run','curl ','wget ','requests.','urllib','http://','https://','templateflow','pip install','nilearn.datasets','hf_hub_download','datalad']):candidates.append(a)
 return {'actual_model_settings':[list(v) for v in sorted(model_settings)],'actual_input_image_blocks':count,'raw_session_sha256':hashes,'network_command_candidates':candidates,'coordinate_check_called':any('volume_tools.py check' in str(c) for c in calls),'provided_viewer_called':any('volume_tools.py view' in str(c) for c in calls),'tool_calls':len(calls)}

rows=[]
for case,(prefix,folder) in CASES.items():
 t=task(case);verify(t);base=ROOT/t['task_path'];truth=json.loads((base/'tests/truth.json').read_text());env={"__name__":"frozen_verifier"};exec(compile((base/'tests/score.py').read_text(),str(base/'tests/score.py'),'exec'),env)
 for model,job in [('terra-high',f'{prefix}-{case}-terra-high-v1-20260917'),('sol-xhigh',f'br040-{case}-sol-xhigh-v1-20260917')]:
  paths=list((ROOT/'runs'/job).glob('*/result.json'))
  if not paths:continue
  p=paths[0];r=json.loads(p.read_text());assert r['task_checksum']==previous(case,'oracle')['task_checksum'];row={'case':case,'model_setting':model,'result_path':str(p.relative_to(ROOT)),'task_checksum':r['task_checksum'],'exception':r.get('exception_info'),'agent_info':r.get('agent_info'),'reward':(r.get('verifier_result') or {}).get('rewards')}
  e=r.get('agent_execution') or {}
  if e.get('started_at') and e.get('finished_at'):row['agent_seconds']=(datetime.datetime.fromisoformat(e['finished_at'].replace('Z','+00:00'))-datetime.datetime.fromisoformat(e['started_at'].replace('Z','+00:00'))).total_seconds()
  details=p.parent/'verifier/details.json';answer=p.parent/'artifacts/app/answer/landmarks.json'
  if details.exists():row['score']=json.loads(details.read_text())
  if answer.exists():
   a=json.loads(answer.read_text());row['answer_path']=str(answer.relative_to(ROOT));host=env['score'](a,truth);assert host==row['score'];row['host_replay_exact']=True
   if host.get('contract_valid'):
    ni=nib.load(base/'environment/volume.nii.gz');d={}
    for key,err in host['errors_mm'].items():
     pred=a['landmarks'][key] if case.startswith('mri') else a['landmarks'][key]['ijk'];gt=truth['points_ijk'][key] if case.startswith('mri') else truth['targets'][key]['ijk'];d[key]=float(np.linalg.norm(nib.affines.apply_affine(ni.affine,pred)-nib.affines.apply_affine(ni.affine,gt)))
    maxdiff=max([abs(d[k]-host['errors_mm'][k]) for k in d] or [0]);assert maxdiff<1e-5;row['world_rescore_max_difference_mm']=maxdiff
    thresholds=[3,5,10] if case.startswith('mri') else [5,10,20];row['success_counts_mm']={str(v):sum(e<=v for e in d.values()) for v in thresholds}
  row['trace_audit']=audit(p.parent/'agent')
  if model=='sol-xhigh':
   cfg=json.loads((B/'configs'/f'{job}.json').read_text());row['configured_model']=cfg['agents'][0]['model_name'];row['configured_effort']=cfg['agents'][0]['kwargs']['reasoning_effort'];assert row['configured_model']=='openai/gpt-5.6-sol' and row['configured_effort']=='xhigh'
   if not row['exception']:assert row['trace_audit']['actual_model_settings']==[['gpt-5.6-sol','xhigh']]
  rows.append(row)
result={'round':'BR-040','comparison':'Sol/xhigh versus Terra/high; identical frozen tasks, model and effort both differ','trials':rows,'limitations':['One CT subject (paired full/partial) and one MRI subject. One attempt per condition per model.','MRI full task has no unavailable targets; no MRI hallucination rate is measured.','Partial CT lacks the upper enumeration anchor; absence and FOV classifications follow full-source convention.']}
for p in [B/'results.json',ROOT/'docs/evidence/br040-results.json']:p.write_text(json.dumps(result,indent=2)+'\n')
for r in rows:
 print(r['case'],r['model_setting'],r.get('success_counts_mm'),r.get('score',{}).get('hallucinated'),r.get('exception'))

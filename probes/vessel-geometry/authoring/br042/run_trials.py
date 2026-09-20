"""Sequential same-byte controls and one Astra/medium attempt; no retries."""
from pathlib import Path
import json,hashlib,subprocess,time
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br042-all-vessels-v2'
def verify(task):
 p=ROOT/task['task_path'];assert {str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()}==task['files']
if __name__=='__main__':
 task=json.loads((B/'freeze.json').read_text())['tasks'][0];checks=[]
 for phase in ['oracle','nop','astra-medium']:
  verify(task);job=f'br042-all-vessels-{phase}-v2-20260920';assert not (ROOT/'runs'/job).exists(),'No overwrites or retries'
  cfg=json.loads((ROOT/'runs/br041-image-only-centerline/configs/br041-named-rca-astra-xhigh-v1-20260919.json').read_text())
  cfg.update(job_name=job,quiet=True,n_attempts=1,n_concurrent_trials=1);cfg['tasks'][0]['path']=task['task_path'];cfg['retry']['max_retries']=0
  a=cfg['agents'][0]
  if phase in ['oracle','nop']:a.update(name=phase,model_name=None,kwargs={},env={});exe=ROOT/'.venv-validation/bin/harbor'
  else:a.update(model_name='openai/gpt-6-astra',kwargs={'reasoning_effort':'medium'});exe=ROOT/'.venv/bin/harbor'
  c=B/'configs'/f'{job}.json';c.parent.mkdir(exist_ok=True);c.write_text(json.dumps(cfg,indent=2)+'\n');c.chmod(0o600)
  print(json.dumps({'event':'start','phase':phase,'time':time.time()}),flush=True)
  with (B/f'{job}.log').open('w') as log:proc=subprocess.run([str(exe),'run','--config',str(c)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  paths=list((ROOT/'runs'/job).glob('*/result.json'));assert len(paths)==1,'Infrastructure exclusion: missing trial result'
  r=json.loads(paths[0].read_text());verify(task);reward=(r.get('verifier_result') or {}).get('rewards',{}).get('reward')
  print(json.dumps({'event':'finish','phase':phase,'reward':reward,'exception':r.get('exception_info'),'time':time.time()}),flush=True)
  assert proc.returncode==0 and not r.get('exception_info'),'Infrastructure exclusion; no automatic retry'
  checks.append(r['task_checksum']);assert len(set(checks))==1
  if phase in ['oracle','nop']:assert reward==int(phase=='oracle')

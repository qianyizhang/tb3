"""Frozen Terra/high pilot with separate mechanical controls and trace retention."""
from pathlib import Path
import argparse,hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def verify(f):
 t=ROOT/f['task_path'];assert {str(p.relative_to(t)):sha(p) for p in t.rglob('*') if p.is_file()}==f['files']
def run(name,phase):
 f=json.loads((B/f'{name}-freeze.json').read_text());verify(f)
 job=f'br037-{name}-{phase}-v1-20260917';assert not (ROOT/'runs'/job).exists()
 cfg=json.loads((ROOT/'runs/br033-airway-routing/configs/br033-airway-cpr-terra-high-v1-20260916.json').read_text())
 cfg.update(job_name=job,quiet=True,n_attempts=1,n_concurrent_trials=1);cfg['tasks'][0]['path']=f['task_path'];cfg['retry']['max_retries']=0
 agent=cfg['agents'][0]
 if phase in ['oracle','nop']:
  agent.update(name=phase,model_name=None,kwargs={},env={});exe=ROOT/'.venv-validation/bin/harbor'
 else:
  agent.update(name='codex',model_name='openai/gpt-5.6-terra',kwargs={'reasoning_effort':'high'});exe=ROOT/'.venv/bin/harbor'
 config=B/'configs'/f'{job}.json';config.parent.mkdir(exist_ok=True);config.write_text(json.dumps(cfg,indent=2)+'\n');config.chmod(0o600)
 print(json.dumps(dict(event='start',job=job,time=time.time())),flush=True)
 with (B/f'{job}.log').open('w') as log:r=subprocess.run([str(exe),'run','--config',str(config)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 paths=list((ROOT/'runs'/job).glob('*/result.json'));assert len(paths)==1,'Missing result'
 result=json.loads(paths[0].read_text());verify(f);reward=(result.get('verifier_result') or {}).get('rewards',{}).get('reward')
 print(json.dumps(dict(event='finish',job=job,contract_reward=reward,exception_type=(result.get('exception_info') or {}).get('exception_type'),time=time.time())),flush=True)
 assert r.returncode==0 and not result.get('exception_info'),'Infrastructure exclusion: no automatic retry'
 if phase in ['oracle','nop']:assert reward==int(phase=='oracle')
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('phase',choices=['controls','terra-high','all']);a=p.parse_args()
 if a.phase in ['controls','all']:
  x=run(a.name,'oracle');y=run(a.name,'nop');assert x['task_checksum']==y['task_checksum']
 if a.phase in ['terra-high','all']:
  z=run(a.name,'terra-high')
  if a.phase=='all':assert z['task_checksum']==x['task_checksum']

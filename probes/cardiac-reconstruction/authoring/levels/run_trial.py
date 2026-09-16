"""One requested trial; verify frozen files before and after. No retries."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br031-cardiac-levels'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(task):
    base=ROOT/task['task_path']
    assert {str(p.relative_to(base)):sha(p) for p in base.rglob('*') if p.is_file()}==task['files']

def run(stage,phase):
    task=json.loads((B/f'cardiac-{stage}-freeze.json').read_text());verify(task)
    job=f'br031-cardiac-{stage}-{phase}-v1-20260916'
    assert not (ROOT/'runs'/job).exists(), 'Never overwrite a trial'
    cfg=json.loads((ROOT/'runs/br026-vessel-repair/configs/br026-vessel-v01-terra-high-v1-20260916.json').read_text())
    cfg.update(job_name=job,quiet=True,n_attempts=1,n_concurrent_trials=1);cfg['tasks'][0]['path']=task['task_path'];cfg['retry']['max_retries']=0
    agent=cfg['agents'][0]
    if phase in ['oracle','nop']:
        agent.update(name=phase,model_name=None,kwargs={},env={});exe=ROOT/'.venv-validation/bin/harbor'
    else:
        model,effort=phase.split('-');agent.update(name='codex',model_name=f'openai/gpt-5.6-{model}',kwargs={'reasoning_effort':effort});exe=ROOT/'.venv/bin/harbor'
    p=B/'configs'/f'{job}.json';p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(cfg,indent=2)+'\n')
    print(json.dumps(dict(event='start',job=job,time=time.time())),flush=True)
    with (B/f'{job}.log').open('w') as log:
        proc=subprocess.run([str(exe),'run','--config',str(p)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    paths=list((ROOT/'runs'/job).glob('*/result.json'));assert len(paths)==1,'Missing/ambiguous result'
    result=json.loads(paths[0].read_text());verify(task)
    reward=(result.get('verifier_result') or {}).get('rewards',{}).get('reward')
    print(json.dumps(dict(event='finish',job=job,reward=reward,exception_type=(result.get('exception_info') or {}).get('exception_type'),time=time.time())),flush=True)
    assert proc.returncode==0 and not result.get('exception_info'),'Infrastructure or timeout; preserve, do not classify as model failure'
    if phase in ['oracle','nop']:assert reward==int(phase=='oracle')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage');p.add_argument('phase',choices=['oracle','nop','terra-high','sol-xhigh','controls']);a=p.parse_args()
    if a.phase=='controls':
        x=run(a.stage,'oracle');y=run(a.stage,'nop');assert x['task_checksum']==y['task_checksum']
    else:run(a.stage,a.phase)

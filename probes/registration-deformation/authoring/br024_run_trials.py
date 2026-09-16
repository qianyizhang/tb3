"""Run one matched oracle/nop/Sol diagnostic, without automatic retries."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br024-harder-registration'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(task):
    base=ROOT/task['task_path']
    actual={str(p.relative_to(base)):sha(p) for p in base.rglob('*') if p.is_file()}
    assert actual==task['files'], 'Frozen bytes or file membership changed'

def run(task,phase):
    assert phase in ['oracle','nop','sol-xhigh']
    job=f"br024-{task['task']}-{phase}-v1-20260916"
    assert not (ROOT/'runs'/job).exists(), 'Never overwrite/retry a trial'
    config=json.loads((ROOT/'runs/br004-sol-32-sol-xhigh-v1-20260915/config.json').read_text())
    config.update(job_name=job,quiet=True,n_attempts=1,n_concurrent_trials=1)
    config['retry']['max_retries']=0;config['tasks'][0]['path']=task['task_path']
    agent=config['agents'][0]
    if phase in ['oracle','nop']:
        agent.update(name=phase,model_name=None,kwargs={},env={});harbor=ROOT/'.venv-validation/bin/harbor'
    else:
        agent['model_name']='openai/gpt-5.6-sol';agent['kwargs']={'reasoning_effort':'xhigh'}
        agent['env']['CODEX_FORCE_AUTH_JSON']='1';harbor=ROOT/'.venv/bin/harbor'
    path=OUT/'configs'/f'{job}.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(config,indent=2)+'\n')
    print(json.dumps({'event':'start','job':job,'time':time.time()}),flush=True)
    with (OUT/f'{job}.log').open('w') as log:
        proc=subprocess.run([str(harbor),'run','--config',str(path)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    paths=list((ROOT/'runs'/job).glob('*/result.json'));assert len(paths)==1,'Missing/ambiguous result'
    result=json.loads(paths[0].read_text());reward=(result.get('verifier_result') or {}).get('rewards',{}).get('reward')
    print(json.dumps({'event':'finish','job':job,'reward':reward,'exception':result.get('exception_info'),'time':time.time()}),flush=True)
    verify(task)
    assert proc.returncode==0 and not result.get('exception_info'),'Infrastructure/timeout exclusion: do not retry'
    if phase in ['oracle','nop']:assert reward==(1 if phase=='oracle' else 0)
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('case',choices=['patient2','patient3']);args=ap.parse_args()
    plan=json.loads((OUT/'freezes'/f'{args.case}.json').read_text());task=plan['task']
    verify(task);a=run(task,'oracle');b=run(task,'nop')
    assert a['task_checksum']==b['task_checksum']
    for phase in ['sol-xhigh']:
        c=run(task,phase);assert c['task_checksum']==a['task_checksum']

if __name__=='__main__':main()

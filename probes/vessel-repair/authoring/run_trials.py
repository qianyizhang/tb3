"""Two fresh matched feasibility diagnostics; no automatic retries."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'runs/br026-vessel-repair'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(task):
    base=ROOT/task['task_path']
    actual={str(p.relative_to(base)):sha(p) for p in base.rglob('*') if p.is_file()}
    assert actual==task['files'],'Frozen task bytes changed'

def run(task,phase):
    verify(task)
    job=f"br026-{task['task']}-{phase}-v1-20260916"
    assert not (ROOT/'runs'/job).exists(),'Do not overwrite or retry a job'
    config=json.loads((ROOT/'runs/br004-sol-32-sol-xhigh-v1-20260915/config.json').read_text())
    config.update(job_name=job,quiet=True,n_attempts=1,n_concurrent_trials=1)
    config['retry']['max_retries']=0;config['tasks'][0]['path']=task['task_path']
    agent=config['agents'][0]
    if phase in ['oracle','nop']:
        agent.update(name=phase,model_name=None,kwargs={},env={});harbor=ROOT/'.venv-validation/bin/harbor'
    else:
        agent['model_name']='openai/gpt-5.6-terra';agent['kwargs']={'reasoning_effort':'high'}
        agent['env']['CODEX_FORCE_AUTH_JSON']='1';harbor=ROOT/'.venv/bin/harbor'
    path=BASE/'configs'/f'{job}.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(config,indent=2)+'\n')
    print(json.dumps({'event':'start','job':job,'time':time.time()}),flush=True)
    with (BASE/f'{job}.log').open('w') as log:
        proc=subprocess.run([str(harbor),'run','--config',str(path)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    paths=list((ROOT/'runs'/job).glob('*/result.json'));assert len(paths)==1,'Missing or ambiguous result'
    result=json.loads(paths[0].read_text());reward=(result.get('verifier_result') or {}).get('rewards',{}).get('reward')
    print(json.dumps({'event':'finish','job':job,'reward':reward,
                     'exception_type':(result.get('exception_info') or {}).get('exception_type'),'time':time.time()}),flush=True)
    verify(task)
    assert proc.returncode==0 and not result.get('exception_info'),'Infrastructure/timeout exclusion; no automatic retry'
    if phase in ['oracle','nop']:assert reward==int(phase=='oracle')
    return result

if __name__=='__main__':
    plan=json.loads((BASE/'freeze.json').read_text())
    for task in plan['tasks']:
        a=run(task,'oracle');b=run(task,'nop');assert a['task_checksum']==b['task_checksum']
        c=run(task,'terra-high');assert c['task_checksum']==a['task_checksum']

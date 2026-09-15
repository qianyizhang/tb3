"""One attempt per task, independent controls, immutable task verification."""
import argparse
import json
import subprocess
import time
from common import ROOT,OUT,write,sha

def verify(task):
    assert all(sha(ROOT/task['task_path']/p)==h for p,h in task['files'].items())

def run(task,phase):
    name=task['task'];job=f'br016-{name}-{phase}-v1-20260915'
    assert not (ROOT/'runs'/job).exists(),'Never repeat a model attempt'
    config=json.loads((ROOT/'runs/br004-sol-32-sol-xhigh-v1-20260915/config.json').read_text())
    config.update(job_name=job,quiet=True,n_attempts=1,n_concurrent_trials=1)
    config['retry']['max_retries']=0;config['tasks'][0]['path']=task['task_path']
    agent=config['agents'][0]
    if phase in ['oracle','nop']:
        agent.update(name=phase,model_name=None,kwargs={},env={});harbor=ROOT/'.venv-validation/bin/harbor'
    else:
        agent['model_name']='openai/gpt-5.6-sol' if phase=='sol-xhigh' else 'openai/gpt-5.6-terra'
        agent['kwargs']={'reasoning_effort':'xhigh' if phase=='sol-xhigh' else 'max'}
        agent['env']['CODEX_FORCE_AUTH_JSON']='1';harbor=ROOT/'.venv/bin/harbor'
    path=OUT/'configs'/f'{job}.json';write(path,config)
    print(json.dumps({'event':'start','job':job,'time':time.time()}),flush=True)
    with (OUT/f'{job}.log').open('w') as log:
        proc=subprocess.run([str(harbor),'run','--config',str(path)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    paths=list((ROOT/'runs'/job).glob('*/result.json'));assert len(paths)==1
    result=json.loads(paths[0].read_text());reward=(result.get('verifier_result') or {}).get('rewards',{}).get('reward')
    print(json.dumps({'event':'finish','job':job,'reward':reward,'exception':result.get('exception_info'),'time':time.time()}),flush=True)
    assert proc.returncode==0 and not result.get('exception_info'),'Infrastructure/timeout exclusion; no retry'
    if phase in ['oracle','nop']:assert reward==(1 if phase=='oracle' else 0)
    verify(task);return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('task');args=ap.parse_args()
    task=json.loads((OUT/'freezes'/f'{args.task}.json').read_text())['tasks'][0];verify(task)
    a=run(task,'oracle');b=run(task,'nop');assert a['task_checksum']==b['task_checksum']
    c=run(task,'sol-xhigh');assert c['task_checksum']==a['task_checksum']

if __name__=='__main__':main()

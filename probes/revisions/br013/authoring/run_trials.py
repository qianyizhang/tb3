"""Run the authorized one-attempt sequential pilot; stop on infrastructure faults."""
import argparse
import copy
import json
import subprocess
import time
from pathlib import Path
from screen import ROOT,OUT,sha,write

def verify(freeze):
    for task in freeze['tasks']:
        root=ROOT/task['task_path']
        assert all(sha(root/p)==digest for p,digest in task['files'].items()),task['task']

def run_one(task,phase):
    template=ROOT/'runs/br004-sol-32-sol-xhigh-v1-20260915/config.json'
    config=json.loads(template.read_text())
    job=f"br013-{task['task']}-{phase}-v1-20260915"
    assert not (ROOT/'runs'/job).exists(),'Never repeat an existing attempt'
    config.update(job_name=job,quiet=True,n_attempts=1,n_concurrent_trials=1)
    config['retry']['max_retries']=0
    config['tasks'][0]['path']=task['task_path']
    agent=config['agents'][0]
    if phase in ['oracle','nop']:
        agent.update(name=phase,model_name=None,kwargs={},env={})
        harbor=ROOT/'.venv-validation/bin/harbor'
    else:
        agent['model_name']='openai/gpt-5.6-sol' if phase=='sol-xhigh' else 'openai/gpt-5.6-terra'
        agent['kwargs']={'reasoning_effort':'xhigh' if phase=='sol-xhigh' else 'max'}
        agent['env']['CODEX_FORCE_AUTH_JSON']='1'
        harbor=ROOT/'.venv/bin/harbor'
    path=OUT/'configs'/f'{job}.json';write(path,config)
    log=OUT/f'{job}.log'
    print(json.dumps({'event':'start','job':job,'time':time.time()}),flush=True)
    with log.open('w') as f:
        result=subprocess.run([str(harbor),'run','--config',str(path)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    candidates=list((ROOT/'runs'/job).glob('*/result.json'))
    if len(candidates)!=1:raise RuntimeError(f'No unique trial result: {job}; inspect {log}')
    obj=json.loads(candidates[0].read_text())
    reward=(obj.get('verifier_result') or {}).get('rewards',{}).get('reward')
    print(json.dumps({'event':'finish','job':job,'reward':reward,'exception':obj.get('exception_info'),'time':time.time()}),flush=True)
    if result.returncode or obj.get('exception_info'):raise RuntimeError(f'Infrastructure or timeout: {job}; no automatic retry')
    if phase in ['oracle','nop']:assert reward==(1 if phase=='oracle' else 0),job
    return obj

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--terra-task',choices=['abdomen-a01','abdomen-a02','abdomen-a03']);args=ap.parse_args()
    freeze=json.loads((OUT/'freeze.json').read_text());verify(freeze)
    if args.terra_task:
        review=json.loads((OUT/'author/reviews.json').read_text())
        assert review[args.terra_task]['validity']=='valid_model_failure','Terra requires a reviewed valid Sol failure'
        task=next(t for t in freeze['tasks'] if t['task']==args.terra_task)
        run_one(task,'terra-max');verify(freeze)
    else:
        for task in freeze['tasks']:
            oracle=run_one(task,'oracle');nop=run_one(task,'nop')
            assert oracle['task_checksum']==nop['task_checksum']
            model=run_one(task,'sol-xhigh')
            assert model['task_checksum']==oracle['task_checksum']
            verify(freeze)

if __name__=='__main__':main()

"""Matched controls and one Terra/high trial; no automatic retries."""
from pathlib import Path
import hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br030-vessel-geometry'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(task):
    p=ROOT/task['task_path'];actual={str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file()};assert actual==task['files'],'Frozen bytes changed'
def run(task,phase):
    verify(task);job=f'br030-coronary-cpr-{phase}-v1-20260916';assert not (ROOT/'runs'/job).exists()
    cfg=json.loads((ROOT/'runs/br026-vessel-repair/configs/br026-vessel-v01-terra-high-v1-20260916.json').read_text())
    cfg.update(job_name=job,quiet=True,n_attempts=1,n_concurrent_trials=1);cfg['tasks'][0]['path']=task['task_path'];cfg['retry']['max_retries']=0
    a=cfg['agents'][0]
    if phase in ['oracle','nop']:
        a.update(name=phase,model_name=None,kwargs={},env={});exe=ROOT/'.venv-validation/bin/harbor'
    else:
        a.update(model_name='openai/gpt-5.6-terra',kwargs={'reasoning_effort':'high'});exe=ROOT/'.venv/bin/harbor'
    c=B/'configs'/f'{job}.json';c.parent.mkdir(exist_ok=True);c.write_text(json.dumps(cfg,indent=2)+'\n')
    print(json.dumps({'event':'start','job':job,'time':time.time()}),flush=True)
    with (B/f'{job}.log').open('w') as log:r=subprocess.run([str(exe),'run','--config',str(c)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    paths=list((ROOT/'runs'/job).glob('*/result.json'));assert len(paths)==1,'Missing/ambiguous result'
    result=json.loads(paths[0].read_text());reward=(result.get('verifier_result') or {}).get('rewards',{}).get('reward')
    print(json.dumps({'event':'finish','job':job,'reward':reward,'exception':result.get('exception_info'),'time':time.time()}),flush=True)
    verify(task);assert r.returncode==0 and not result.get('exception_info'),'Infrastructure or timeout; preserve outcome, no automatic retry'
    if phase in ['oracle','nop']:assert reward==int(phase=='oracle')
    return result
if __name__=='__main__':
    task=json.loads((B/'freeze.json').read_text())['tasks'][0]
    a=run(task,'oracle');b=run(task,'nop');assert a['task_checksum']==b['task_checksum']
    c=run(task,'terra-high');assert c['task_checksum']==a['task_checksum']

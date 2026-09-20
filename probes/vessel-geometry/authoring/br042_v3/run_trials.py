"""Fresh controls, then three sequential isolated attempts, no retries."""
from pathlib import Path
import hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[4]
B=ROOT/'runs/br042-all-vessels-v3'
PHASES=['oracle','nop','sol-xhigh','astra-medium','astra-xhigh']
MODELS={'sol-xhigh':('openai/gpt-5.6-sol','xhigh'),'astra-medium':('openai/gpt-6-astra','medium'),'astra-xhigh':('openai/gpt-6-astra','xhigh')}
def verify(task):
    p=ROOT/task['task_path']
    assert {str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()}==task['files'],'Frozen bytes changed'
def job_name(phase):return f'br042-all-vessels-{phase}-v3-20260920'
def emit(row):
    with (B/'events.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
    print(json.dumps(row),flush=True)
if __name__=='__main__':
    task=json.loads((B/'freeze.json').read_text())['tasks'][0]
    assert not (B/'events.jsonl').exists(),'No automatic reruns'
    expected=None
    for phase in PHASES:
        verify(task);job=job_name(phase);assert not (ROOT/'runs'/job).exists(),'No overwrite or retry'
        cfg=json.loads((ROOT/'runs/br042-all-vessels-v2/configs/br042-all-vessels-astra-medium-v2-20260920.json').read_text())
        cfg.update(job_name=job,quiet=True,n_attempts=1,n_concurrent_trials=1,timeout_multiplier=1.0)
        cfg['tasks'][0]['path']=task['task_path'];cfg['retry']['max_retries']=0
        assert cfg['environment']['mounts'] is None
        a=cfg['agents'][0];a.update(override_timeout_sec=None,max_timeout_sec=None)
        if phase in ['oracle','nop']:
            a.update(name=phase,model_name=None,kwargs={},env={});exe=ROOT/'.venv-validation/bin/harbor'
        else:
            model,effort=MODELS[phase];a.update(name='codex',model_name=model,kwargs={'reasoning_effort':effort});exe=ROOT/'.venv/bin/harbor'
        c=B/'configs'/f'{job}.json';c.parent.mkdir(exist_ok=True);c.write_text(json.dumps(cfg,indent=2)+'\n');c.chmod(0o600)
        emit({'event':'start','phase':phase,'job':job,'time':time.time()})
        with (B/f'{job}.log').open('w') as log:
            proc=subprocess.run([str(exe),'run','--config',str(c)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        verify(task)
        paths=list((ROOT/'runs'/job).glob('*/result.json'))
        r=json.loads(paths[0].read_text()) if len(paths)==1 else {}
        error=r.get('exception_info') or (None if proc.returncode==0 and r else 'Missing result or nonzero process exit')
        reward=(r.get('verifier_result') or {}).get('rewards',{}).get('reward')
        if r:
            if expected is None:expected=r['task_checksum']
            assert r['task_checksum']==expected,'Task mismatch'
        emit({'event':'finish','phase':phase,'returncode':proc.returncode,'reward':reward,'exception':error,'time':time.time()})
        if phase in ['oracle','nop']:
            assert not error and reward==int(phase=='oracle'),'Unhealthy control: stop before model exposure'
        # A failed model job remains an exclusion; proceed to the next authorized model without retry.
    emit({'event':'complete','time':time.time()})

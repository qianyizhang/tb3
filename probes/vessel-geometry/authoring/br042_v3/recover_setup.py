"""Recover pre-model setup failures after a successful package-install diagnostic."""
import json,subprocess,time
from run_trials import ROOT,B,verify,job_name
if __name__=='__main__':
    events=B/'recovery-events.jsonl';assert not events.exists(),'No automatic recovery loop'
    task=json.loads((B/'freeze.json').read_text())['tasks'][0]
    expected=json.loads(next((ROOT/'runs'/job_name('oracle')).glob('*/result.json')).read_text())['task_checksum']
    def emit(x):
        with events.open('a') as f:f.write(json.dumps(x)+'\n')
        print(json.dumps(x),flush=True)
    for phase in ['astra-medium','astra-xhigh']:
        verify(task)
        old=next((ROOT/'runs'/job_name(phase)).glob('*/result.json'));r=json.loads(old.read_text())
        assert r['exception_info'] and not r.get('agent_execution') and not r.get('agent_result')
        assert not list((old.parent/'agent').rglob('*.jsonl')),'Model exposure would require a separately declared retry'
        cfg=json.loads((B/'configs'/f'{job_name(phase)}.json').read_text())
        job=job_name(phase)+'-setup-recovery1';assert not (ROOT/'runs'/job).exists()
        cfg['job_name']=job
        c=B/'configs'/f'{job}.json';c.write_text(json.dumps(cfg,indent=2)+'\n');c.chmod(0o600)
        emit({'event':'start','phase':phase,'job':job,'time':time.time(),'prior_job_model_execution':False})
        with (B/f'{job}.log').open('w') as f:p=subprocess.run([str(ROOT/'.venv/bin/harbor'),'run','--config',str(c)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        paths=list((ROOT/'runs'/job).glob('*/result.json'));r=json.loads(paths[0].read_text()) if len(paths)==1 else {}
        verify(task)
        if r:assert r['task_checksum']==expected
        emit({'event':'finish','phase':phase,'job':job,'time':time.time(),'returncode':p.returncode,'exception':r.get('exception_info'),'model_executed':bool(r.get('agent_execution')),'reward':(r.get('verifier_result') or {}).get('rewards')})
    emit({'event':'complete','time':time.time()})

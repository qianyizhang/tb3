"""One authorized Astra/xhigh comparison on unchanged BR-041 task bytes."""
from pathlib import Path
import json,subprocess,time
from run_trials import ROOT,B,verify
if __name__=='__main__':
    task=json.loads((B/'freeze.json').read_text())['tasks'][0];verify(task)
    previous=[]
    for phase in ['oracle','nop','terra-high','sol-xhigh']:
        ps=list((ROOT/'runs'/f'br041-named-rca-{phase}-v1-20260919').glob('*/result.json'));assert len(ps)==1
        r=json.loads(ps[0].read_text());assert not r.get('exception_info');previous.append(r)
    assert len({r['task_checksum'] for r in previous})==1
    assert [r['verifier_result']['rewards']['reward'] for r in previous[:2]]==[1,0]
    job='br041-named-rca-astra-xhigh-v1-20260919';assert not (ROOT/'runs'/job).exists(),'No overwrite or automatic retry'
    cfg=json.loads((B/'configs/br041-named-rca-terra-high-v1-20260919.json').read_text())
    cfg.update(job_name=job,quiet=True,n_attempts=1,n_concurrent_trials=1);cfg['retry']['max_retries']=0
    cfg['agents'][0].update(model_name='openai/gpt-6-astra',kwargs={'reasoning_effort':'xhigh'})
    c=B/'configs'/f'{job}.json';c.write_text(json.dumps(cfg,indent=2)+'\n');c.chmod(0o600)
    plan={'round':'BR-041','followup':'A01','model':'openai/gpt-6-astra','reasoning_effort':'xhigh','attempts':1,'retries':0,'timeout_seconds':3600,'task':task,'matched_control_checksum':previous[0]['task_checksum'],'comparison':'model plus reasoning setting; unchanged task, no prior answers or feedback supplied'}
    pp=ROOT/'docs/evidence/br041-astra-plan.json';assert not pp.exists();pp.write_text(json.dumps(plan,indent=2)+'\n')
    print(json.dumps({'event':'start','job':job,'time':time.time()}),flush=True)
    with (B/f'{job}.log').open('w') as log:r=subprocess.run([str(ROOT/'.venv/bin/harbor'),'run','--config',str(c)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    ps=list((ROOT/'runs'/job).glob('*/result.json'));assert len(ps)==1,'Missing result; infrastructure exclusion'
    result=json.loads(ps[0].read_text());verify(task)
    print(json.dumps({'event':'finish','job':job,'reward':(result.get('verifier_result') or {}).get('rewards'),'exception':result.get('exception_info'),'time':time.time()}),flush=True)
    assert r.returncode==0 and not result.get('exception_info'),'Infrastructure exclusion; no automatic retry'
    assert result['task_checksum']==previous[0]['task_checksum']

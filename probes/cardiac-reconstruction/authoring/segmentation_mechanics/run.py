"""One fresh authorized Sol attempt per frozen condition, preceded by controls."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br035-segmentation-mechanics'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(f):
    for c,v in f['conditions'].items():
        t=ROOT/v['task_path'];assert {str(p.relative_to(t)):sha(p) for p in t.rglob('*') if p.is_file()}==v['files']
    assert sha(ROOT/'docs/research-rounds/BR-035-segmentation-mechanics.md')==f['protocol_sha256']
    for path,h in f['clinical_files'].items():assert sha(B/'clinical'/path)==h

def run(condition,phase):
    f=json.loads((B/'freeze.json').read_text());verify(f);job=f'br035-{condition}-{phase}-v1-20260916';assert not (ROOT/'runs'/job).exists()
    cfg=json.loads((ROOT/'runs/br026-vessel-repair/configs/br026-vessel-v01-terra-high-v1-20260916.json').read_text());cfg.update(job_name=job,quiet=True,n_attempts=1,n_concurrent_trials=1);cfg['tasks'][0]['path']=f['conditions'][condition]['task_path'];cfg['retry']['max_retries']=0;a=cfg['agents'][0]
    if phase in ['oracle','nop']:a.update(name=phase,model_name=None,kwargs={},env={});exe=ROOT/'.venv-validation/bin/harbor'
    else:
        a.update(name='codex',model_name='openai/gpt-5.6-sol',kwargs={'reasoning_effort':'xhigh'});exe=ROOT/'.venv/bin/harbor'
        for p in ['oracle','nop']:
            control=next((ROOT/'runs'/f'br035-{condition}-{p}-v1-20260916').glob('*/result.json'));r=json.loads(control.read_text());assert not r.get('exception_info') and r['verifier_result']['rewards']['reward']==int(p=='oracle')
    path=B/'configs'/f'{job}.json';path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(cfg,indent=2)+'\n')
    print(json.dumps(dict(event='start',job=job,time=time.time())),flush=True)
    with (B/f'{job}.log').open('w') as log:r=subprocess.run([str(exe),'run','--config',str(path)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    results=list((ROOT/'runs'/job).glob('*/result.json'));assert len(results)==1;result=json.loads(results[0].read_text());verify(f)
    print(json.dumps(dict(event='finish',job=job,reward=(result.get('verifier_result') or {}).get('rewards'),exception=(result.get('exception_info') or {}).get('exception_type'))),flush=True)
    assert r.returncode==0 and not result.get('exception_info'),'Retain infrastructure/timeout separately from capability'
    if phase in ['oracle','nop']:assert result['verifier_result']['rewards']['reward']==int(phase=='oracle')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('condition',choices=['masks','masks-images']);p.add_argument('phase',choices=['controls','sol-xhigh']);a=p.parse_args()
    if a.phase=='controls':run(a.condition,'oracle');run(a.condition,'nop')
    else:run(a.condition,a.phase)

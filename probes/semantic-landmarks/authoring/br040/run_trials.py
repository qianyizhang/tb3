"""Fresh Sol/xhigh on unchanged BR-038 MRI and BR-039 CT tasks."""
from pathlib import Path
import json,hashlib,subprocess,time,argparse
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br040-sol-landmarks'
CASES={'ct-full':('br039','br039-ct-landmarks'),'ct-partial':('br039','br039-ct-landmarks'),'mri32-full':('br038','br038-volume-landmarks')}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while chunk:=f.read(8*1024*1024):h.update(chunk)
 return h.hexdigest()
def task(case):
 prefix,folder=CASES[case];base=ROOT/'runs'/folder
 return next(t for t in json.loads((base/'freeze.json').read_text())['tasks'] if t['task']==case)
def verify(t):
 p=ROOT/t['task_path'];assert {str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file()}==t['files'],'Frozen bytes changed'
def previous(case,phase):
 prefix,_=CASES[case];ps=list((ROOT/'runs'/f'{prefix}-{case}-{phase}-v1-20260917').glob('*/result.json'));assert len(ps)==1
 return json.loads(ps[0].read_text())
def preflight(case):
 t=task(case);verify(t);rows=[previous(case,p) for p in ['oracle','nop','terra-high']]
 assert all(not r.get('exception_info') for r in rows)
 assert len({r['task_checksum'] for r in rows})==1
 assert [r['verifier_result']['rewards']['reward'] for r in rows[:2]]==[1,0]
 return t,rows[0]['task_checksum']
def run(case):
 t,checksum=preflight(case);prefix,folder=CASES[case]
 cfg=json.loads((ROOT/'runs'/folder/'configs'/f'{prefix}-{case}-terra-high-v1-20260917.json').read_text())
 job=f'br040-{case}-sol-xhigh-v1-20260917';assert not (ROOT/'runs'/job).exists(),'No overwriting or automatic retry'
 cfg.update(job_name=job,quiet=True,n_attempts=1,n_concurrent_trials=1);cfg['retry']['max_retries']=0
 cfg['agents'][0].update(model_name='openai/gpt-5.6-sol',kwargs={'reasoning_effort':'xhigh'})
 assert cfg['tasks'][0]['path']==t['task_path']
 c=B/'configs'/f'{job}.json';c.parent.mkdir(exist_ok=True);c.write_text(json.dumps(cfg,indent=2)+'\n');c.chmod(0o600)
 print(json.dumps({'event':'start','case':case,'model':'openai/gpt-5.6-sol','effort':'xhigh','time':time.time()}),flush=True)
 with (B/f'{job}.log').open('w') as log:p=subprocess.run([str(ROOT/'.venv/bin/harbor'),'run','--config',str(c)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 ps=list((ROOT/'runs'/job).glob('*/result.json'));assert len(ps)==1,'Missing result; infrastructure exclusion'
 r=json.loads(ps[0].read_text());verify(t)
 print(json.dumps({'event':'finish','case':case,'reward':(r.get('verifier_result') or {}).get('rewards'),'exception':r.get('exception_info'),'time':time.time()}),flush=True)
 assert p.returncode==0 and not r.get('exception_info'),'Infrastructure exclusion; no automatic retry'
 assert r['task_checksum']==checksum,'Task checksum changed'
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('case',choices=[*CASES,'preflight']);a=ap.parse_args()
 if a.case=='preflight':
  entries=[]
  for case in CASES:
   t,cs=preflight(case);entries.append({'case':case,'task':t,'matched_control_checksum':cs})
  plan={'round':'BR-040','model':'openai/gpt-5.6-sol','reasoning_effort':'xhigh','attempts_per_condition':1,'retries':0,'timeout_seconds':3600,'conditions':entries,'controls':'Reuse completed same-byte oracle/nop; require identical Harbor checksum to Terra'}
  p=B/'plan.json';assert not p.exists();p.write_text(json.dumps(plan,indent=2)+'\n');(ROOT/'docs/evidence/br040-plan.json').write_text(p.read_text());print('All three frozen tasks and existing controls verified')
 else:run(a.case)

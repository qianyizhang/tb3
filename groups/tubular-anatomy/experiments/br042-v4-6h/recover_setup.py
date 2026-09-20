"""One bounded setup recovery, permitted only when the initial agent never ran."""
from pathlib import Path
import argparse,hashlib,json,subprocess,time
R=Path(__file__).resolve().parents[4];B=R/'runs/br042-all-vessels-v4-6h'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');a=ap.parse_args()
 f=json.loads((B/'freeze.json').read_text());t=R/f['tasks'][0]['task_path']
 def verify():
  assert {str(p.relative_to(t)):sha(p) for p in t.rglob('*') if p.is_file()}==f['tasks'][0]['files']
 verify();rows=[json.loads(x) for x in (B/'events.jsonl').read_text().splitlines()]
 for phase,reward in [('oracle',1),('nop',0)]:
  row=next(x for x in rows if x.get('event')=='finish' and x.get('phase')==phase)
  assert row['exception'] is None and row['reward']==reward
 prior=next(x for x in rows if x.get('event')=='finish' and x.get('phase')=='astra-xhigh')
 result=json.loads((R/prior['result_path']).read_text())
 assert result['agent_execution'] is None and result['agent_result'] is None
 assert result['exception_info']['exception_type']=='NonZeroAgentExitCodeError'
 assert '503  Service Unavailable' in result['exception_info']['exception_message']
 source=R/f['configs']['astra-xhigh']['path'];assert sha(source)==f['configs']['astra-xhigh']['sha256']
 cfg=json.loads(source.read_text());job='br042-all-vessels-astra-xhigh-v4-6h-attempt2';cfg['job_name']=job
 assert not (R/'runs'/job).exists() and not (B/'setup-recovery-events.jsonl').exists()
 if not a.run:
  print('READY: initial agent never executed; controls and frozen bytes unchanged; fresh job required.');return
 p=B/'configs/astra-xhigh-setup-recovery.json';p.open('x').write(json.dumps(cfg,indent=2)+'\n');p.chmod(0o600)
 with (B/'setup-recovery-events.jsonl').open('x') as events:
  def emit(x):
   x['time']=time.time();events.write(json.dumps(x)+'\n');events.flush();print(json.dumps(x),flush=True)
  emit({'event':'start','phase':'astra-xhigh','job':job,'config_sha256':sha(p),'prior_result':prior['result_path'],'reason':'Pre-agent package service 503; separate disposable install preflight recovered. No prior agent execution.'})
  with (B/'astra-xhigh-setup-recovery.log').open('x') as log:
   proc=subprocess.run([str(R/'.venv/bin/harbor'),'run','--config',str(p)],cwd=R,stdout=log,stderr=subprocess.STDOUT)
  verify();paths=list((R/'runs'/job).glob('*/result.json'));r=json.loads(paths[0].read_text()) if len(paths)==1 else {}
  assert not r or r['task_checksum']==result['task_checksum']
  emit({'event':'finish','returncode':proc.returncode,'exception_type':(r.get('exception_info') or {}).get('exception_type'),'result_path':str(paths[0].relative_to(R)) if r else None})
  if r:subprocess.run(['python3.12','scripts/med','collect','br042-v4-6h',str(paths[0].relative_to(R))],cwd=R,check=True,stdout=subprocess.DEVNULL)
  if proc.returncode or not r or r.get('exception_info'):raise SystemExit(1)
if __name__=='__main__':main()

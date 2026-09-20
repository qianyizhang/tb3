"""Single-use resumed continuation; --run is required for inference."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,time
R=Path(__file__).resolve().parents[5];G=Path(__file__).resolve().parent;B=R/'runs/br042-all-vessels-v4-6h-resume1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');args=ap.parse_args()
 m=json.loads((G/'restore-manifest.json').read_text());assert m==json.loads((B/'restore-manifest.json').read_text())
 assert sha(B/'config.json')==m['config_sha256']
 for p,h in m['restore_files'].items():assert sha(B/p)==h
 f=json.loads((R/'runs/br042-all-vessels-v4-6h/freeze.json').read_text());t=R/f['tasks'][0]['task_path'];assert {str(p.relative_to(t)):sha(p) for p in t.rglob('*') if p.is_file()}==f['tasks'][0]['files']
 cfg=json.loads((B/'config.json').read_text());job=R/'runs'/cfg['job_name'];assert not job.exists() and not (B/'events.jsonl').exists()
 assert cfg['retry']['max_retries']==0 and cfg['agents'][0]['override_timeout_sec']==21600
 if not args.run:print('READY: restored session, answer hashes, frozen task and no-retry config verified.');return
 env=os.environ.copy();env['PYTHONPATH']=str(G)
 with (B/'events.jsonl').open('x') as events:
  def emit(x):x['time']=time.time();events.write(json.dumps(x)+'\n');events.flush();print(json.dumps(x),flush=True)
  emit({'event':'start','job':cfg['job_name'],'kind':'resumed_continuation','session_id':m['session_id'],'new_allowance_seconds':21600})
  with (B/'launcher.log').open('x') as log:
   proc=subprocess.run([str(R/'.venv/bin/harbor'),'run','--config',str(B/'config.json')],cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT)
  paths=list(job.glob('*/result.json'));result=json.loads(paths[0].read_text()) if len(paths)==1 else {}
  emit({'event':'finish','returncode':proc.returncode,'exception_type':(result.get('exception_info') or {}).get('exception_type'),'result_path':str(paths[0].relative_to(R)) if result else None})
  if result:subprocess.run(['python3.12','scripts/med','collect','br042-v4-6h',str(paths[0].relative_to(R))],cwd=R,check=True,stdout=subprocess.DEVNULL)
  if proc.returncode or not result or result.get('exception_info'):raise SystemExit(1)
if __name__=='__main__':main()

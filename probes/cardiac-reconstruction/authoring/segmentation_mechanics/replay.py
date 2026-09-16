"""Network-disabled clinical transfer using exactly the submitted executable."""
import argparse,json,subprocess,time
from pathlib import Path
from run import verify,sha
from score import score
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br035-segmentation-mechanics'
def main():
    p=argparse.ArgumentParser();p.add_argument('condition');p.add_argument('--attempt',type=int,default=1);a=p.parse_args();f=json.loads((B/'freeze.json').read_text());verify(f)
    trial=next((ROOT/'runs'/f'br035-{a.condition}-sol-xhigh-v1-20260916').glob('*/result.json')).parent;answer=trial/'artifacts/app/answer';assert (answer/'solve.py').is_file();inp=B/'clinical'/a.condition
    out=B/'replays'/(a.condition if a.attempt==1 else f'{a.condition}-v{a.attempt}');out.mkdir(parents=True,exist_ok=False);(out/'output').mkdir()
    codehash={str(p.relative_to(answer)):sha(p) for p in answer.rglob('*') if p.is_file()};image='br035-replay-'+a.condition+':v1';name='br035-clinical-'+a.condition
    cmd=['docker','run','--rm','--name',name,'--network','none','--cpus','4','--memory','8g','--read-only','--tmpfs','/tmp:rw,size=2g','-e','OMP_NUM_THREADS=4','-e','OPENBLAS_NUM_THREADS=4','-v',f'{answer}:/solver:ro','-v',f'{inp}:/app/data:ro','-v',f'{out/"output"}:/app/answer:rw','--entrypoint','python',image,'/solver/solve.py','--input','/app/data','--output','/app/answer']
    start=time.monotonic();timeout=False
    with (out/'execution.log').open('w') as log:
        try:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=300);code=r.returncode
        except subprocess.TimeoutExpired:timeout=True;code=None;subprocess.run(['docker','kill',name],stdout=log,stderr=subprocess.STDOUT)
    receipt=dict(condition=a.condition,seconds=time.monotonic()-start,exit_code=code,timeout=timeout,submitted_files_sha256=codehash,input_files_sha256={str(p.relative_to(inp)):sha(p) for p in inp.rglob('*') if p.is_file()},image=image)
    for p,h in codehash.items():assert sha(answer/p)==h
    if code==0:
        receipt['grade']=score(out/'output/prediction.npz',inp)
        assessment=out/'output/assessment.json';receipt['assessment']=json.loads(assessment.read_text()) if assessment.exists() else None
        preparation=json.loads((B/'preparation.json').read_text());r=receipt['grade'].get('cavity_function')
        if r:r['clinical_surface_reference_ef_pct']=preparation['clinical_reference_ef_pct'];r['clinical_surface_ef_error_pp']=abs(r['ef_pct']-preparation['clinical_reference_ef_pct'])
    receipt['output_files_sha256']={str(p.relative_to(out/'output')):sha(p) for p in (out/'output').rglob('*') if p.is_file()};(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if not k.endswith('sha256') and k!='grade'}))
if __name__=='__main__':main()

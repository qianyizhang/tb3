"""Run the frozen submitted executable on original, hidden, and altered inputs."""
import argparse,hashlib,json,shutil,subprocess,time
from pathlib import Path
import numpy as np
from score import score,volumes,distances
from run import verify
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br034-pathological-echo'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('kind',choices=['original','patient','preserved','static','shift']);parser.add_argument('--attempt',type=int,default=1);args=parser.parse_args();kind=args.kind
    frozen=json.loads((B/'freeze.json').read_text());verify(frozen)
    ev=json.loads((B/'evaluation-freeze.json').read_text())
    for p,h in ev['files'].items():assert sha(B/p)==h
    trial=next((ROOT/'runs/br034-pathological-echo-sol-xhigh-v1-20260916').glob('*/result.json')).parent
    answer=trial/'artifacts/app/answer';assert (answer/'solve.py').is_file()
    frozen_code={str(p.relative_to(answer)):sha(p) for p in answer.rglob('*') if p.is_file()}
    out=B/'replays'/(kind if args.attempt==1 else f'{kind}-v{args.attempt}');out.mkdir(parents=True,exist_ok=False);(out/'output').mkdir()
    source=B/'curation/ef48' if kind=='patient' else B/'curation/preserved-v2' if kind=='preserved' else B
    if kind=='preserved':
        extra=json.loads((B/'preserved-control-v2-freeze.json').read_text())
        for p,h in extra['files'].items():assert sha(B/p)==h
    inp=source/'input';shift=ev['phase_shift_frames']
    if kind in ['static','shift']:
        inp=out/'input';shutil.copytree(B/'input',inp)
        a=np.load(inp/'volumes.npy');cal=json.loads((inp/'geometry.json').read_text());seed=int(cal['initial_mesh_frame'])
        if kind=='static':a=np.repeat(a[seed:seed+1],len(a),axis=0)
        else:a=np.roll(a,shift,axis=0);cal['initial_mesh_frame']=(seed+shift)%len(a)
        np.save(inp/'volumes.npy',a);(inp/'geometry.json').write_text(json.dumps(cal,indent=2)+'\n')
        # Keep preview files synchronized; the executable is instructed to use volume pixels.
        pics={p.name:p.read_bytes() for p in (inp/'previews').glob('*.png')}
        for p in (inp/'previews').glob('*.png'):
            plane,num=p.stem.rsplit('_',1);old=seed if kind=='static' else (int(num)-shift)%len(a)
            p.write_bytes(pics[f'{plane}_{old:03d}.png'])
    name='br034-replay-'+kind
    cmd=['docker','run','--rm','--name',name,'--network','none','--cpus','4','--memory','8g','--read-only',
         '--tmpfs','/tmp:rw,size=2g','-e','OMP_NUM_THREADS=4','-e','OPENBLAS_NUM_THREADS=4',
         '-v',f'{answer}:/solver:ro','-v',f'{inp}:/app/data:ro','-v',f'{out/"output"}:/app/answer:rw',
         '--entrypoint','python','br034-clinical-replay:v1','/solver/solve.py','--input','/app/data','--output','/app/answer']
    start=time.monotonic();timeout=False
    with (out/'execution.log').open('w') as log:
        try:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=300);code=r.returncode
        except subprocess.TimeoutExpired:
            timeout=True;code=None;subprocess.run(['docker','kill',name],stdout=log,stderr=subprocess.STDOUT)
    receipt=dict(kind=kind,exit_code=code,timeout=timeout,seconds=time.monotonic()-start,submitted_files_sha256=frozen_code,
                 input_files_sha256={str(p.relative_to(inp)):sha(p) for p in inp.rglob('*') if p.is_file()},image='br034-clinical-replay:v1')
    for p,h in frozen_code.items():assert sha(answer/p)==h
    if code==0 and (out/'output/prediction.npz').exists():
        p=np.load(out/'output/prediction.npz');v=volumes(p['points'],p['faces']);receipt['ef_pct']=float(100*(1-v.min()/v.max()));receipt['volume_ml']=v.tolist()
        receipt['motion_rms_mm']=float(np.sqrt(np.mean(np.sum((p['points']-p['points'][:1])**2,axis=-1))))
        if kind in ['original','patient','preserved']:
            # The solve executable itself is mounted separately; collect required method/code files for artifact regrading.
            grade=out/'grading';shutil.copytree(out/'output',grade)
            for name in ['solve.py','method.md']:
                if not (grade/name).exists() and (answer/name).exists():shutil.copy2(answer/name,grade/name)
            receipt['grade']=score(grade,source/'reference.npz')
        base=np.load(answer/'prediction.npz');basev=volumes(base['points'],base['faces'])
        if kind in ['original','static','shift']:
            q=np.roll(p['points'],-shift,axis=0) if kind=='shift' else p['points']
            qv=np.roll(v,-shift) if kind=='shift' else v
            receipt['original_volume_mae_ml']=float(np.mean(abs(qv-basev)))
            receipt['original_surface_mean_mm']=float(np.mean([distances(x,p['faces'],y,base['faces'])[0] for x,y in zip(q,base['points'])]))
            if q.shape==base['points'].shape:receipt['original_coordinate_max_abs_mm']=float(abs(q-base['points']).max())
        if kind=='static':receipt['input_response_pass']=receipt['ef_pct']<=ev['static_ef_max_pp'] and receipt['motion_rms_mm']<=ev['static_motion_rms_max_mm']
        if kind=='shift':receipt['input_response_pass']=receipt['original_volume_mae_ml']<=ev['shift_volume_mae_max_ml']
    receipt['output_files_sha256']={str(p.relative_to(out/'output')):sha(p) for p in (out/'output').rglob('*') if p.is_file()}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['input_files_sha256','output_files_sha256','submitted_files_sha256','grade']},indent=2))
if __name__=='__main__':main()

"""Input-response checks of a frozen submitted executable, without model retries."""
import argparse,hashlib,json,shutil,subprocess,time
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from score import score

ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br032-real-echo'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main(kind,version=1,image_override=None):
    receipt=json.loads((B/'sol-xhigh-receipt.json').read_text());answer=(ROOT/receipt['result_path']).parent/'artifacts/app/answer'
    expected=receipt['artifacts']['solve.py'];assert sha(answer/'solve.py')==expected
    base=B/'replays'/(kind if version==1 else f'{kind}-v{version}');base.mkdir(parents=True,exist_ok=False)
    inputs=base/'input';shutil.copytree(B/'input',inputs);out=base/'output';out.mkdir()
    g=json.loads((inputs/'geometry.json').read_text());R=Rotation.from_euler('xyz',[-21,13,37],degrees=True).as_matrix();shift=np.array([-18.2,11.1,24.6])
    if kind=='pose':
        for plane in g['planes']:
            plane['origin']=(np.asarray(plane['origin'])@R.T+shift).tolist()
            for k in ['u','v']:plane[k]=(np.asarray(plane[k])@R.T).tolist()
        for k,v in g['task_axes'].items():g['task_axes'][k]=(np.asarray(v)@R.T).tolist()
        (inputs/'geometry.json').write_text(json.dumps(g,indent=2)+'\n')
    elif kind=='static':
        for folder in inputs.glob('view_*'):
            source=(folder/'frame_01.png').read_bytes()
            for target in folder.glob('frame_*.png'):target.write_bytes(source)
    image=image_override or json.loads((B/'image-audit.json').read_text())['image'];name=f'br032-replay-{kind}-v{version}'
    cmd=['docker','run','--rm','--name',name,'--network','none','--cpus','4','--memory','8g','--read-only','--tmpfs','/tmp:size=1024m',
         '--mount',f'type=bind,src={inputs},dst=/app/data,readonly',
         '--mount',f'type=bind,src={answer},dst=/solver,readonly',
         '--mount',f'type=bind,src={out},dst=/app/answer',
         '--workdir','/solver','--entrypoint','python',image,'/solver/solve.py','--input','/app/data','--output','/app/answer']
    start=time.monotonic();timeout=False
    with (base/'stdout.txt').open('w') as log:
        try:p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=240);code=p.returncode
        except subprocess.TimeoutExpired:
            timeout=True;code=None;subprocess.run(['docker','stop','--time','1',name],capture_output=True)
    result=dict(kind=kind,version=version,image=image,submitted_solver_sha256=expected,network='none',timeout=timeout,exit_code=code,seconds=time.monotonic()-start,
                input_hashes={str(p.relative_to(inputs)):sha(p) for p in inputs.rglob('*') if p.is_file()},
                scope='response to altered inputs, not proof about pretraining exposure')
    if code==0 and (out/'prediction.npz').exists():
        z=np.load(out/'prediction.npz');p=z['points'];original=np.load(answer/'prediction.npz')['points'];grade=score(out);result['contract']=grade
        if kind=='pose' and p.shape==original.shape:
            expected_p=original@R.T+shift;result['coordinate_equivariance_point_rmse_mm']=float(np.sqrt(np.mean(np.sum((p-expected_p)**2,axis=-1))))
            result['transform']=dict(R=R.tolist(),translation_mm=shift.tolist())
        elif kind=='static':
            result['motion_rms_mm']=float(np.sqrt(np.mean(np.sum((p-p[0])**2,axis=-1))))
            if p.shape==original.shape:result['max_abs_difference_from_original_mm']=float(np.max(abs(p-original)))
            if grade['reward']==1:
                v=np.array(grade['volume_ml']);result['volume_range_ml']=float(np.ptp(v));result['volume_range_pct_of_mean']=float(np.ptp(v)/v.mean()*100)
    (base/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['input_hashes','contract']},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['pose','static']);p.add_argument('--version',type=int,default=1);p.add_argument('--image');a=p.parse_args();main(a.kind,a.version,a.image)

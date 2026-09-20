"""Private image-only named coronary tracing pilot verifier."""
from pathlib import Path
import json,sys
import numpy as np
from scipy.spatial import cKDTree

def score(answer,truth):
    checks={};metrics={};error=None
    try:
        ref=np.load(truth,allow_pickle=False)
        line=np.load(Path(answer)/'centerline.npy',allow_pickle=False)
        assert line.ndim==2 and line.shape[1]==3 and 100<=len(line)<=2000 and np.isfinite(line).all(),'Expected finite 100-2000 by 3 array'
        steps=np.linalg.norm(np.diff(line,axis=0),axis=1)
        length=steps.sum();rl=np.linalg.norm(np.diff(ref,axis=0),axis=1).sum()
        f=cKDTree(ref).query(line)[0];b=cKDTree(line).query(ref)[0]
        ends=np.linalg.norm(line[[0,-1]]-ref[[0,-1]],axis=1)
        metrics=dict(p95_distance_mm=float(np.percentile(f,95)),coverage_within_1mm=float((b<=1).mean()),coverage_within_2mm=float((b<=2).mean()),endpoint_errors_mm=ends.tolist(),length_mm=float(length),length_relative_error=float(abs(length/rl-1)),max_step_mm=float(steps.max()))
        checks=dict(format=True,sampling=bool(steps.min()>=.05 and steps.max()<=.75),distance=metrics['p95_distance_mm']<=1,coverage=metrics['coverage_within_1mm']>=.95,endpoints=bool(ends.max()<=5),length=metrics['length_relative_error']<=.15)
    except Exception as e:
        error=str(e);checks['format']=False
    return dict(reward=int(all(checks.values())),checks=checks,metrics=metrics,error=error)
if __name__=='__main__':
    r=score(sys.argv[1] if len(sys.argv)>1 else '/app/answer',sys.argv[2] if len(sys.argv)>2 else '/verifier/reference.npy')
    print(json.dumps(r,indent=2))
    if len(sys.argv)==1:
        out=Path('/logs/verifier');out.mkdir(parents=True,exist_ok=True)
        (out/'metrics.json').write_text(json.dumps(r,indent=2)+'\n');(out/'reward.txt').write_text(str(r['reward'])+'\n')

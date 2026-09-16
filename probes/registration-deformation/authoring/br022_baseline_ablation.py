"""Apply only predeclared motion-model/context switches to the prior baseline."""
from pathlib import Path

source=Path('/baseline.py').read_text()
old="args=ap.parse_args();start=time.time();dim=2 if args.kind=='2d' else 3"
new="ap.add_argument('--model',choices=['translation','affine'],required=True);ap.add_argument('--context',choices=['small','multiscale'],required=True);"+old
assert source.count(old)==1;source=source.replace(old,new)
old="enumerate([(25,3,1.2),(16,2,.7),(10,1.5,.4)])"
new="enumerate([(8,3,1.2),(8,2,.7),(8,1.5,.4)] if args.context=='small' else [(25,3,1.2),(16,2,.7),(10,1.5,.4)])"
assert source.count(old)==1;source=source.replace(old,new)
source=source.replace("L=B+params[3:].reshape(3,dim)/50","L=B if args.model=='translation' else B+params[3:].reshape(3,dim)/50")
source=source.replace("np.zeros(3+3*dim)","np.zeros(3 if args.model=='translation' else 3+3*dim)")
source=source.replace("np.zeros(3*dim)","np.zeros(0 if args.model=='translation' else 3*dim)")
source=source.replace("B+=r.x[3:].reshape(3,dim)/50","B+=0 if args.model=='translation' else r.x[3:].reshape(3,dim)/50")
exec(compile(source,'/baseline-ablation.py','exec'))

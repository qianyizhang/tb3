import json,sys
from pathlib import Path
sys.path.insert(0,'/app')
from lab import query

# A fixed sequence identifies each permitted family and its sole parameter.
commands=[0,1,.8,.6,0,-1,-.6,-.8,0,0,0,.3,.3,.3]
y=query(commands)
candidates=[]
for family,p in [('static',1-y[1]),('play',1-y[1]),('lag',y[1])]:
    if not ((family=='lag' and .1<=p<=.9) or (family!='lag' and .05<=p<=.35)):continue
    s=0.;out=[]
    for u in commands:
        if family=='static':s=max(u-p,0) if u>=0 else min(u+p,0)
        elif family=='play':s=sorted([u-p,s,u+p])[1]
        else:s=(1-p)*s+p*u
        out.append(s)
    if max(abs(a-b) for a,b in zip(out,y))<1e-10:candidates.append(dict(family=family,parameter=p))
assert len(candidates)==1,candidates
Path('/app/answer/calibration.json').write_text(json.dumps(candidates[0])+'\n')

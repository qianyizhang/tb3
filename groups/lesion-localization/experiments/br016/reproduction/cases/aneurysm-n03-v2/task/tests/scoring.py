"""Strict, one-to-one coarse localization against frozen source regions."""
import json,math

def read_json(path):
    def pairs(p):
        d={}
        for k,v in p:
            if k in d:raise ValueError('Duplicate JSON key')
            d[k]=v
        return d
    return json.loads(path.read_text(),object_pairs_hook=pairs,parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))

def score(answer,key):
    if not isinstance(answer,dict) or set(answer)!={'aneurysms'}:raise ValueError('Expected only aneurysms key')
    pts=answer['aneurysms']
    if not isinstance(pts,list):raise ValueError('Expected list')
    if len(pts)>100:raise ValueError('Too many detections')
    for p in pts:
        if not isinstance(p,list) or len(p)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in p):raise ValueError('Expected finite [i,j,k] points')
        if any(x<0 or x>key['shape'][d]-1 for d,x in enumerate(p)):raise ValueError('Point outside volume')
    # Integer voxel membership after nearest-centre rounding. Region includes a
    # fixed 1-mm tolerance around the released source sphere, frozen before trial.
    adj=[]
    for p in pts:
        q=tuple(math.floor(x+0.5) for x in p)
        adj.append([i for i,r in enumerate(key['regions']) if ','.join(map(str,q)) in r['accepted_voxels']])
    matched={}
    def visit(n,seen):
        for j in adj[n]:
            if j in seen:continue
            seen.add(j)
            if j not in matched or visit(matched[j],seen):matched[j]=n;return True
        return False
    tp=sum(visit(n,set()) for n in range(len(pts)));fp=len(pts)-tp;fn=len(key['regions'])-tp
    return {'passed':fp==0 and fn==0,'tp':tp,'fp':fp,'fn':fn,'predictions':pts,'matches':[{'reference':j,'prediction':n} for j,n in sorted(matched.items())]}

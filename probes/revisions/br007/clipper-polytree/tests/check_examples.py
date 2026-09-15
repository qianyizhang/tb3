#!/usr/bin/env python3
"""Public API adapter and order-independent output checker; no repair code."""
import json,os,shutil,subprocess
from pathlib import Path

def encode(cases):
    parts=[str(len(cases))]
    for c in cases:
        parts.extend([c['op'],c['rule'],str(int(c['preserve'])),str(int(c['reverse']))])
        for key in ['subject','clip']:
            parts.append(str(len(c[key])))
            for ring in c[key]:
                parts.append(str(len(ring)));parts.extend(str(v) for point in ring for v in point)
    return ' '.join(parts)+'\n'

def normalize(ring):
    clean=[]
    for p in ring:
        if len(p)!=2 or any(type(v)!=int for v in p):raise ValueError('non-integer contour')
        p=tuple(p)
        if not clean or p!=clean[-1]:clean.append(p)
    if len(clean)>1 and clean[0]==clean[-1]:clean.pop()
    changed=True
    while changed and len(clean)>3:
        changed=False
        for i,p in enumerate(clean):
            a,b=clean[i-1],clean[(i+1)%len(clean)]
            if a!=b and (p[0]-a[0])*(b[1]-p[1])==(p[1]-a[1])*(b[0]-p[0]) and (p[0]-a[0])*(p[0]-b[0])+(p[1]-a[1])*(p[1]-b[1])<=0:
                clean.pop(i);changed=True;break
    if len(clean)<3 or sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(clean,clean[1:]+clean[:1]))==0:raise ValueError('degenerate contour')
    return min(tuple(r[i:]+r[:i]) for r in [clean,list(reversed(clean))] for i in range(len(r)))

def canonical(nodes):
    roots=[];stack=[]
    for n in nodes:
        d=n['depth']
        if type(d)!=int or d<0 or d>len(stack) or type(n['hole'])!=bool or n['hole']!=(d%2==1):raise ValueError('invalid hierarchy')
        node=[normalize(n['xy']),[]];del stack[d:]
        (stack[-1][1] if stack else roots).append(node);stack.append(node)
    def freeze(n):return n[0],tuple(sorted(freeze(c) for c in n[1]))
    return tuple(sorted(freeze(n) for n in roots))

def compare(cases,rows):
    passed=[];failures=[]
    for c,r in zip(cases,rows):
        try:
            want=canonical(c['expected'])
            assert canonical(r['first'])==want,'first call geometry or hierarchy'
            assert canonical(r['repeat'])==want,'repeat call geometry or hierarchy'
        except (AssertionError,KeyError,TypeError,ValueError) as e:failures.append({'name':c['name'],'error':str(e)})
        else:passed.append(c['name'])
    assert len(rows)==len(cases),'wrong number of results'
    return {'passed':passed,'failures':failures}

if __name__=='__main__':
    repo=Path('/app/clipper2');target=repo/'src/bin/tb_overlay_probe.rs';target.parent.mkdir(exist_ok=True)
    shutil.copyfile('/app/driver.rs',target)
    subprocess.run(['cargo','build','--offline','--locked','--bin','tb_overlay_probe'],cwd=repo,check=True)
    cases=json.loads(Path('/app/examples.json').read_text())
    run=subprocess.run([str(repo/'target/debug/tb_overlay_probe')],input=encode(cases),capture_output=True,text=True,check=True)
    result=compare(cases,[json.loads(x) for x in run.stdout.splitlines()]);print(json.dumps(result,indent=2))
    raise SystemExit(bool(result['failures']))

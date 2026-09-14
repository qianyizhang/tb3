"""Physical nodal oracle and independently encoded measurement fixtures."""
import json
from pathlib import Path
import numpy as np


def branches(index,f):
    x=f/1e9
    return (8+index+1j*(12+2*index)*x,
            65+3*index+1j*(18*x-8/x),
            13+2*index+1j*(5*x+3/x))


def physical_z(b):
    a,sh,c=b
    return np.array([[a+sh,sh],[sh,c+sh]],complex)


def nodal_oracle(left,right):
    # External nodes 0,1; left middle 2, joint 3, right middle 4.
    y=np.zeros((5,5),complex)
    for a,b,z in [(0,2,left[0]),(2,3,left[2]),(3,4,right[0]),(4,1,right[2])]:
        g=1/z;y[a,a]+=g;y[b,b]+=g;y[a,b]-=g;y[b,a]-=g
    y[2,2]+=1/left[1];y[4,4]+=1/right[1]
    ext=y[:2,:2]-y[:2,2:]@np.linalg.solve(y[2:,2:],y[2:,:2])
    return np.linalg.solve(np.eye(2)+50*ext,np.eye(2)-50*ext)


def encode(z,z0,definition):
    g=np.diag(z0)
    q=np.diag(1/(2*np.sqrt(z0.real)) if definition=='power' else np.sqrt(z0.real)/(2*np.abs(z0)))
    a=q@(z+g)
    b=q@(z-(g.conj() if definition=='power' else g))
    return np.linalg.solve(a.T,b.T).T


def cases(public=False):
    freq=np.linspace(.25e9,3.25e9,16)
    result=[]
    indices=[10] if public else range(8)
    for i in indices:
        physical=[(branches(i,f),branches(i+3,f)) for f in freq]
        wanted=np.array([nodal_oracle(a,b) for a,b in physical])
        for rep in range(4):
            inputs=[]
            for side in range(2):
                refs=[];ss=[]
                definition=['power','power','pseudo','pseudo' if side else 'power'][rep]
                for j,f in enumerate(freq):
                    z0=np.array([50.,50.],complex) if rep==0 else np.array([35+side*13+i+1j*(12+f/1e8),72-i+1j*(-18+side*8-f/2e8)])
                    z=physical_z(physical[j][side]);refs.append(z0);ss.append(encode(z,z0,definition))
                refs=np.array(refs);ss=np.array(ss)
                inputs.append(dict(frequency_hz=freq.tolist(),s_real=ss.real.tolist(),s_imag=ss.imag.tolist(),z0_real=refs.real.tolist(),z0_imag=refs.imag.tolist(),wave_definition=definition))
            result.append(dict(name=f'circuit-{i:02}-representation-{rep}',input=dict(left=inputs[0],right=inputs[1]),expected=dict(s_real=wanted.real.tolist(),s_imag=wanted.imag.tolist())))
    return result


if __name__=='__main__':
    root=Path(__file__).parents[1]
    (root/'tests/cases.json').write_text(json.dumps(cases(),indent=2)+'\n')
    (root/'environment/examples.json').write_text(json.dumps(cases(True),indent=2)+'\n')

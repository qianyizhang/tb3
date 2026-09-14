import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).parents[1];sys.path.insert(0,str(ROOT/'environment'))
from frame import Frame

GENERATORS=[np.array([[0,0,0],[0,0,-1],[0,1,0]]),np.array([[0,0,1],[0,0,0],[-1,0,0]]),np.array([[0,-1,0],[1,0,0],[0,0,0]])]

def rotation_and_derivative(parameters,t):
    angles=np.array(parameters['angles']);a=angles@np.array([1,t,t*t/2]);rates=angles[:,1]+angles[:,2]*t
    rotations=[np.eye(3)+np.sin(x)*g+(1-np.cos(x))*(g@g) for x,g in zip(a,GENERATORS)]
    derivatives=[w*g@r for w,g,r in zip(rates,GENERATORS,rotations)]
    x,y,z=rotations;dx,dy,dz=derivatives
    return x@y@z,dx@y@z+x@dy@z+x@y@dz

def profile(i):
    rng=np.random.default_rng(7300+i)
    angles=rng.uniform(-.3,.3,(3,3));center=rng.uniform(-1,1,(3,3));world=rng.uniform(-1,1,(3,3))
    kind=i//3
    if kind in [0,1]:angles[:,1:]=0
    if kind in [0,2]:center[:,1:]=0
    return dict(angles=angles.tolist(),center=center.tolist()),world

def build(i,shift):
    parameters,world=profile(i);parameters['center']=np.array(parameters['center']);parameters['center'][:,0]+=shift;parameters['center']=parameters['center'].tolist()
    w=world.copy();w[:,0]+=shift
    times=np.linspace(-1.2,1.2,5+i%7)
    # Reorder some samples without changing their identities.
    if i%2:times=times[::-1]
    p=np.array([w@np.array([1,t,t*t/2]) for t in times]);v=np.array([w[:,1]+w[:,2]*t for t in times])
    expected_p=[];expected_v=[]
    for t,pw,vw in zip(times,p,v):
        r,rd=rotation_and_derivative(parameters,t);cp=np.array(parameters['center']);c=cp@np.array([1,t,t*t/2]);cd=cp[:,1]+cp[:,2]*t
        expected_p.append(r.T@(pw-c));expected_v.append(r.T@(vw-cd)-r.T@rd@(r.T@(pw-c)))
    case=dict(name=f'track-{i:02}-origin-{int(bool(np.any(shift)))}',input=dict(track=dict(t=times.tolist(),p_world=p.tolist(),v_world=v.tolist()),frame=parameters),expected=dict(position=np.array(expected_p).tolist(),velocity=np.array(expected_v).tolist()))
    return case,w

def cases(public=False):
    return [build(i,np.array(shift))[0] for i in ([12,13] if public else range(12)) for shift in [[0,0,0],[3,-2,4]]]

if __name__=='__main__':
    (ROOT/'tests/cases.json').write_text(json.dumps(cases(),indent=2)+'\n')
    (ROOT/'environment/examples.json').write_text(json.dumps(cases(True),indent=2)+'\n')

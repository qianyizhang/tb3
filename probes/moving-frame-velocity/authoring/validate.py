import json,sys,importlib.util
from pathlib import Path
import numpy as np
ROOT=Path(__file__).parents[1];sys.path[:0]=[str(ROOT/'environment'),str(ROOT/'authoring')]
from frame import Frame
from fixtures import build,cases,rotation_and_derivative

def main():
    s=importlib.util.spec_from_file_location('reference',ROOT/'solution/reference.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    controls={k:[] for k in ['pose_finite_difference','rotate_only','omit_origin_velocity','wrong_rotation_sign']};maxerr=0.;fd_err=0.;shift_error=0.
    for case in cases():
        t={k:np.array(v) for k,v in case['input']['track'].items()};frame=Frame(case['input']['frame']);want=np.array(case['expected']['velocity'])
        p,v=m.convert_track(t,frame);maxerr=max(maxerr,float(np.max(abs(v-want))))
        candidates={'pose_finite_difference':v,'rotate_only':[],'omit_origin_velocity':[],'wrong_rotation_sign':[]}
        for j,time in enumerate(t['t']):
            r,c=frame.pose(time);rr,rd=rotation_and_derivative(frame.parameters,time);assert np.max(abs(r-rr))<1e-12
            cp=np.array(frame.parameters['center']);cd=cp[:,1]+cp[:,2]*time;vw=t['v_world'][j]
            candidates['rotate_only'].append(r.T@vw)
            candidates['omit_origin_velocity'].append(r.T@vw-r.T@rd@p[j])
            candidates['wrong_rotation_sign'].append(r.T@(vw-cd)+r.T@rd@p[j])
        for name,got in candidates.items():
            err=np.max(np.linalg.norm(np.array(got)-want,axis=1)/(1+np.linalg.norm(want,axis=1)))
            if err<=1e-7:controls[name].append(case['name'])
    for i in range(12):
        c,world=build(i,np.zeros(3));other,_=build(i,np.array([3,-2,4]));frame=Frame(c['input']['frame'])
        shift_error=max(shift_error,float(np.max(abs(np.array(c['expected']['velocity'])-np.array(other['expected']['velocity'])))))
        for j,t in enumerate(c['input']['track']['t']):
            def position(x):
                r,o=frame.pose(x);return r.T@(world@np.array([1,x,x*x/2])-o)
            for h in [1e-4,3e-5,1e-5]:
                fd=(position(t+h)-position(t-h))/(2*h)
                fd_err=max(fd_err,float(np.max(abs(fd-np.array(c['expected']['velocity'][j])))))
    assert len(controls['pose_finite_difference'])==24 and maxerr<1e-8 and fd_err<1e-7 and shift_error<1e-12
    assert all(len(v)<24 for k,v in controls.items() if k!='pose_finite_difference')
    print(json.dumps(dict(case_count=24,physical_tracks=12,max_baseline_absolute_error=maxerr,max_transformed_position_difference_error=fd_err,max_origin_shift_error=shift_error,controls=controls),indent=2))

if __name__=='__main__':main()

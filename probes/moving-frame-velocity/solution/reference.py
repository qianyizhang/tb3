import numpy as np

def convert_track(track,frame):
    positions=[];velocities=[];h=1e-4
    for t,p,v in zip(track['t'],track['p_world'],track['v_world']):
        r,c=frame.pose(t)
        rp,cp=frame.pose(t+h);rm,cm=frame.pose(t-h)
        rpp,cpp=frame.pose(t+2*h);rmm,cmm=frame.pose(t-2*h)
        rd=(rmm-8*rm+8*rp-rpp)/(12*h)
        cd=(cmm-8*cm+8*cp-cpp)/(12*h)
        local=r.T@(p-c)
        positions.append(local);velocities.append(r.T@(v-cd)+rd.T@(p-c))
    return np.array(positions),np.array(velocities)

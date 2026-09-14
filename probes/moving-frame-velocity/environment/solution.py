import numpy as np

def convert_track(track,frame):
    positions=[];velocities=[]
    for t,p,v in zip(track['t'],track['p_world'],track['v_world']):
        r,c=frame.pose(t);positions.append(r.T@(p-c));velocities.append(r.T@v)
    return np.array(positions),np.array(velocities)

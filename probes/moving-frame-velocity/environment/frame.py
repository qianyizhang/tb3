"""Smooth public pose helper; all angles use radians and time uses seconds."""
import numpy as np

class Frame:
    def __init__(self,parameters):self.parameters=parameters
    def pose(self,t):
        p=self.parameters
        a=np.asarray(p['angles'])@np.array([1.,t,.5*t*t])
        cx,cy,cz=np.cos(a);sx,sy,sz=np.sin(a)
        rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
        ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
        rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
        center=np.asarray(p['center'])@np.array([1.,t,.5*t*t])
        return rx@ry@rz,center

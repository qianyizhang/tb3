"""Author reference implementation, separate from row-system verifier."""
import argparse
import numpy as np

p=argparse.ArgumentParser();p.add_argument('--input');p.add_argument('--output');a=p.parse_args()
z=np.load(a.input);X=z['reference_points'];x=z['points'];tet=z['tetra'];d=z['directions']
M=(X[tet[:,1:]]-X[tet[:,:1]]).swapaxes(-1,-2)
D=(x[:,tet[:,1:]]-x[:,tet[:,:1]]).swapaxes(-1,-2)
F=D@np.linalg.inv(M)
C=np.einsum('tmji,tmjk->tmik',F,F);E=(C-np.eye(3))*.5;J=np.linalg.det(F)
engineering=np.sqrt(np.einsum('dmi,tmij,dmj->tmd',d,C,d))-1
valid=(z['cell_labels']>0)&np.all(np.linalg.norm(d,axis=-1)>.99,axis=0)
engineering[:,~valid]=np.nan
np.savez_compressed(a.output,F=F,E=E,J=J,engineering=engineering,valid=valid)

"""Independent analytic strain, rasterization and material-map controls."""
import json
from pathlib import Path
import numpy as np
from geometry import fields,locate,voxelize
B=Path(__file__).resolve().parents[4]/'runs/br035-segmentation-mechanics'
def main():
    X=np.array([[0.,0,0],[2.,0,0],[0,3.,0],[0,0,4.]]);tet=np.array([[0,1,2,3]])
    theta=.6;R=np.array([[np.cos(theta),-np.sin(theta),0],[np.sin(theta),np.cos(theta),0],[0,0,1]])
    A=np.array([[.8,.2,0],[0,.9,.1],[0,0,1.2]])
    P=np.array([X,X@R.T+[2,3,4],X@A.T]);F,E,J=fields(X,P,tet)
    assert np.max(abs(E[1]))<1e-12 and np.max(abs(F[2,0]-A))<1e-12
    assert np.max(abs(E[2,0]-(A.T@A-np.eye(3))/2))<1e-12
    perm=np.array([2,0,3,1]);inverse=np.argsort(perm);PF,PE,PJ=fields(X[perm],P[:,perm],inverse[tet]);assert np.allclose(F,PF) and np.allclose(E,PE)
    probes=np.array([[.2,.3,.4],[5.,5.,5.]]);ids,w=locate(X,tet,probes);assert ids.tolist()==[0,-1];assert np.allclose(w[0]@X,probes[0])
    mask=voxelize(X,tet,np.zeros(3),np.ones(3),[5,5,5]);zz,yy,xx=np.indices(mask.shape);expected=xx/2+yy/3+zz/4<=1+1e-8;assert np.array_equal(mask,expected)
    # T(x,y,z)=(R(k*z) @ [x,y], z), determinant=1, same circular-cylinder occupancy.
    k=.5;x=np.array([1.,0.,.3]);a=k*x[2];rot=np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]]);G=np.eye(3);G[:2,:2]=rot;G[:2,2]=k*rot@np.array([-x[1],x[0]])
    strain=(G.T@G-np.eye(3))/2
    assert abs(np.linalg.det(G)-1)<1e-12 and np.linalg.norm(strain)>.1
    report=dict(rigid_zero_strain=True,finite_affine_exact=True,vertex_permutation_invariant=True,tetra_voxel_membership_exact=True,probe_location_exact=True,ambiguity=dict(geometry='Unit circular cylinder: twisting each z-slice preserves its occupied domain.',untwisted_green_lagrange=np.zeros((3,3)).tolist(),twisted_green_lagrange=strain.tolist(),twisted_J=float(np.linalg.det(G)),conclusion='Identical segmentations do not uniquely identify material strain.'))
    (B/'analytic-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()

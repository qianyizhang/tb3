"""Analytic geometry checks and deliberately wrong output controls."""
from pathlib import Path
import json,shutil
import numpy as np
import nibabel as nib
from scipy.spatial.transform import Rotation
from geometry import *
from score_geometry import score

ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br030-vessel-geometry/geometry'

def main():
    checks={}
    # Oblique left-handed affine and a known linear physical field.
    aff=np.eye(4);aff[:3,:3]=Rotation.from_euler('xyz',[23,37,-18],degrees=True).as_matrix()@np.diag([-.7,1.1,1.8]);aff[:3,3]=[20,-30,5]
    ijk=np.indices((31,29,27)).transpose(1,2,3,0);ras=transform(ijk,aff)
    field=3*ras[...,0]-2*ras[...,1]+.4*ras[...,2]+17
    rng=np.random.default_rng(30);query=rng.uniform([2,2,2],[28,26,24],(1000,3));p=transform(query,aff)
    expected=3*p[:,0]-2*p[:,1]+.4*p[:,2]+17
    checks['oblique_affine_linear_HU_field']=float(np.max(np.abs(sample(field,aff,p)-expected)))<5e-5
    checks['RAS_voxel_round_trip']=float(np.max(np.abs(transform(p,np.linalg.inv(aff))-query)))<1e-10
    z=np.linspace(0,20,41);line=np.column_stack([z*0,z*0,z]);t,n,b=frames(line)
    maps=cpr_coordinates(line,n,b,[0,90,180,270],[-3,0,3])
    checks['quarter_turns_on_straight_vessel']=np.allclose(maps[0,:,2]-line,[3,0,0]) and np.allclose(maps[1,:,2]-line,[0,3,0]) and np.allclose(maps[2,:,2]-line,[-3,0,0])
    circle=np.linspace(0,1.7*np.pi,401);path=np.column_stack([10*np.cos(circle),10*np.sin(circle),3*circle]);tt,nn,bb=frames(path)
    checks['curved_frame_orthonormal']=np.max(np.abs(np.sum(tt*nn,axis=1)))<1e-10 and np.allclose(np.cross(tt,nn),bb) and np.max(np.abs(np.linalg.norm(nn,axis=1)-1))<1e-10
    checks['frame_no_sign_flips']=np.min(np.sum(nn[1:]*nn[:-1],axis=1))>.99
    mask=(ijk[...,0]-15)**2+(ijk[...,1]-14)**2+(ijk[...,2]-13)**2<8**2
    mesh=mesh_from_mask(mask,aff);checks['reflected_affine_mesh_positive_closed']=mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
    assert all(checks.values()),checks
    truth=B/'reference.npz';oracle=B/'oracle';results={'oracle':score(oracle,truth)}
    assert results['oracle']['reward']==1,results['oracle']
    for case in ['unrepaired','reversed_route','fabricated_HU','mirrored_mesh','broken_mesh','collateral_edit']:
        dst=B/'controls'/case;dst.mkdir(parents=True,exist_ok=True)
        for file in ['corrected_mask.nii.gz','centerline.npy','cpr.npz','vessels.ply']:shutil.copy2(oracle/file,dst/file)
        if case=='unrepaired':shutil.copy2(B/'input/proposed_mask.nii.gz',dst/'corrected_mask.nii.gz')
        if case=='reversed_route':np.save(dst/'centerline.npy',np.load(dst/'centerline.npy')[::-1])
        if case=='fabricated_HU':
            c=dict(np.load(dst/'cpr.npz'));c['hu']=c['hu']+10.;np.savez_compressed(dst/'cpr.npz',**c)
        if case=='mirrored_mesh':
            import trimesh
            m=trimesh.load(dst/'vessels.ply',process=False);m.vertices[:,0]*=-1;m.export(dst/'vessels.ply')
        if case=='broken_mesh':
            ni=nib.load(B/'input/proposed_mask.nii.gz');mesh_from_mask(np.asarray(ni.dataobj)>0,ni.affine).export(dst/'vessels.ply')
        if case=='collateral_edit':
            ni=nib.load(dst/'corrected_mask.nii.gz');a=np.asarray(ni.dataobj).copy();a[0,0,0]=1;nib.save(nib.Nifti1Image(a,ni.affine),dst/'corrected_mask.nii.gz')
        results[case]=score(dst,truth);assert results[case]['reward']==0,case
        if case=='broken_mesh':assert not results[case]['stages']['mesh']
    report={'analytic_checks':{k:bool(v) for k,v in checks.items()},'controls':results}
    (B/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'analytic':report['analytic_checks'],'controls':{k:v['stages'] for k,v in results.items()}},indent=2))

if __name__=='__main__':main()

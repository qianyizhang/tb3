"""Private, staged geometry verifier. No model or source centerline is public."""
from pathlib import Path
import json,sys
import numpy as np
import nibabel as nib
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from skimage.measure import marching_cubes
import trimesh

LIMITS={'local_dice':.80,'local_recall':.80,'far_added_mm3':1.5,'centerline_p95_mm':.8,
        'reference_coverage_0p8mm':.95,'length_relative_error':.10,'endpoint_mm':1.,
        'cpr_coordinate_error_mm':.02,'cpr_HU_p99_error':.2,'mesh_surface_p95_mm':.65}

def coords(a,mat):return np.einsum('...j,ij->...i',a,mat[:3,:3])+mat[:3,3]
def interp(a,aff,p,order=1,cval=0):
    v=coords(p,np.linalg.inv(aff));return ndi.map_coordinates(a.astype('float32'),np.moveaxis(v,-1,0),order=order,mode='constant',cval=cval,prefilter=False)

def score(answer,truth):
    answer=Path(answer);z=np.load(truth);gt=z['gt'];orig=z['proposed'];edit=z['editable'];aff=z['affine'];ref=z['reference_path'];sp=nib.affines.voxel_sizes(aff)
    checks={};metrics={};errors={}
    mask=None;line=None
    try:
        ni=nib.load(answer/'corrected_mask.nii.gz');a=np.asarray(ni.dataobj)
        assert a.shape==gt.shape and np.allclose(ni.affine,aff,atol=1e-5,rtol=0),'mask grid'
        assert np.isin(a,[0,1]).all(),'binary mask'
        mask=a>0;checks['mask_format']=True
        checks['preservation']=bool(np.array_equal(mask[~edit],orig[~edit]))
        den=mask[edit].sum()+gt[edit].sum();dice=float(2*np.count_nonzero(mask&edit&gt)/max(1,den))
        recall=float(mask[edit&gt].mean());distance=ndi.distance_transform_edt(~gt,sampling=sp)
        far=float(np.count_nonzero(mask&edit&~orig&(distance>.75))*np.prod(sp))
        cc,_=ndi.label(mask,np.ones((3,3,3)));hit=interp(cc,aff,z['anchors'],0).astype(int)
        # Restrict connectivity to a 2-mm tube around the local intended route,
        # preventing a detour through the neighboring R-PLA from satisfying it.
        seed=np.zeros(mask.shape,bool);vox=np.rint(coords(z['route_corridor_points'],np.linalg.inv(aff))).astype(int);seed[tuple(vox.T)]=True
        tube=ndi.distance_transform_edt(~seed,sampling=sp)<=2.
        lc,_=ndi.label(mask&tube,np.ones((3,3,3)));lh=interp(lc,aff,z['anchors'],0).astype(int)
        connect=bool(hit[0]>0 and hit[0]==hit[1] and lh[0]>0 and lh[0]==lh[1])
        checks.update(repair_overlap=dice>=.8 and recall>=.8,repair_connection=connect,repair_no_far_addition=far<=1.5)
        metrics.update(local_dice=dice,local_recall=recall,far_added_mm3=far,changed_voxels=int(np.count_nonzero(mask!=orig)))
    except Exception as e:errors['repair']=str(e);checks['mask_format']=False
    try:
        line=np.load(answer/'centerline.npy',allow_pickle=False)
        assert line.ndim==2 and line.shape[1]==3 and 100<=len(line)<=2000 and np.isfinite(line).all(),'path format'
        steps=np.linalg.norm(np.diff(line,axis=0),axis=1);length=float(steps.sum());rlen=np.linalg.norm(np.diff(ref,axis=0),axis=1).sum()
        forward=cKDTree(ref).query(line)[0];backward=cKDTree(line).query(ref)[0]
        ends=np.linalg.norm(line[[0,-1]]-ref[[0,-1]],axis=1)
        p95=float(np.percentile(forward,95));cover=float((backward<=.8).mean())
        checks['trace_geometry']=bool(p95<=.8 and cover>=.95 and np.max(ends)<=1. and abs(length/rlen-1)<=.10 and steps.max()<=.75 and steps.min()>=.05)
        assert mask is not None
        outside=ndi.distance_transform_edt(~mask,sampling=sp)
        checks['trace_in_mask']=bool((interp(outside,aff,line)<=.5).mean()>=.99)
        metrics.update(centerline_p95_mm=p95,reference_coverage_0p8mm=cover,length_mm=length,endpoint_errors_mm=ends.tolist())
    except Exception as e:errors['trace']=str(e);checks['trace_geometry']=False
    try:
        assert line is not None
        c=np.load(answer/'cpr.npz',allow_pickle=False);hu=c['hu'];xyz=c['source_ras_mm'];angles=c['angles_deg'];offsets=c['offsets_mm'];arc=c['arc_mm']
        assert xyz.shape==(8,len(line),65,3) and hu.shape==xyz.shape[:-1] and np.isfinite(xyz).all() and np.isfinite(hu).all(),'CPR shape / finite'
        assert np.allclose(angles,np.arange(0,360,45)) and np.allclose(offsets,np.arange(-8,8.001,.25)),'CPR grid'
        # Independently rotate the previous normal by the minimal tangent rotation.
        t=np.gradient(line.astype(float),axis=0);t/=np.linalg.norm(t,axis=1)[:,None]
        axis=np.eye(3)[np.argmin(np.abs(t[0]))];n=axis-axis.dot(t[0])*t[0];n/=np.linalg.norm(n);normals=[n]
        for i in range(1,len(t)):
            cross=np.cross(t[i-1],t[i]);sin=np.linalg.norm(cross);cos=np.clip(t[i-1].dot(t[i]),-1,1)
            if sin>1e-10:n=Rotation.from_rotvec(cross/sin*np.arctan2(sin,cos)).apply(n)
            n=n-n.dot(t[i])*t[i];n/=np.linalg.norm(n);normals.append(n)
        normals=np.array(normals);bins=np.cross(t,normals)
        directions=np.cos(np.deg2rad(angles))[:,None,None]*normals+np.sin(np.deg2rad(angles))[:,None,None]*bins
        target=line[None,:,None,:]+directions[:,:,None,:]*offsets[None,None,:,None]
        coord_error=float(np.linalg.norm(xyz-target,axis=-1).max())
        expected=interp(z['image'],aff,xyz,cval=-1024.);hu_error=float(np.percentile(np.abs(expected-hu),99))
        arc_expected=np.r_[0.,np.cumsum(np.linalg.norm(np.diff(line,axis=0),axis=1))]
        checks['cpr_coordinates']=coord_error<=.02 and bool(np.max(np.abs(arc-arc_expected))<.25)
        checks['cpr_source_intensities']=hu_error<=.2
        metrics.update(cpr_max_coordinate_error_mm=coord_error,cpr_HU_p99_error=hu_error)
    except Exception as e:errors['cpr']=str(e);checks['cpr_coordinates']=False
    try:
        assert mask is not None
        mesh=trimesh.load(answer/'vessels.ply',force='mesh',process=False)
        assert isinstance(mesh,trimesh.Trimesh) and 1000<len(mesh.vertices)<2000000 and np.isfinite(mesh.vertices).all(),'mesh format'
        rv,rf,_,_=marching_cubes(np.pad(mask.astype('uint8'),1),.5);rv=coords(rv-1,aff)
        a=cKDTree(rv).query(mesh.vertices)[0];b=cKDTree(mesh.vertices).query(rv)[0]
        pd=float(max(np.percentile(a,95),np.percentile(b,95)))
        local_a=interp(edit,aff,mesh.vertices,0)>0;local_b=interp(edit,aff,rv,0)>0
        assert local_a.any() and local_b.any(),'missing review-region surface'
        local_pd=float(max(np.percentile(a[local_a],95),np.percentile(b[local_b],95)))
        vol=float(mesh.volume);mvol=float(mask.sum()*np.prod(sp))
        checks['mesh_geometry']=bool(pd<=.65 and local_pd<=.65 and abs(vol/mvol-1)<=.10 and mesh.is_watertight and mesh.is_winding_consistent)
        metrics.update(mesh_surface_p95_mm=pd,mesh_review_surface_p95_mm=local_pd,mesh_volume_mm3=vol,mesh_mask_volume_ratio=vol/mvol,mesh_watertight=bool(mesh.is_watertight))
    except Exception as e:errors['mesh']=str(e);checks['mesh_geometry']=False
    stages={
        'repair':all(checks.get(k,False) for k in ['mask_format','preservation','repair_overlap','repair_connection','repair_no_far_addition']),
        'trace':all(checks.get(k,False) for k in ['trace_geometry','trace_in_mask']),
        'cpr':all(checks.get(k,False) for k in ['cpr_coordinates','cpr_source_intensities']),
        'mesh':checks.get('mesh_geometry',False)}
    return {'reward':int(all(stages.values())),'stages':stages,'checks':checks,'metrics':metrics,'errors':errors,'limits':LIMITS}

if __name__=='__main__':
    answer=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/app/answer')
    truth=Path(sys.argv[2]) if len(sys.argv)>2 else Path('/verifier/reference.npz')
    r=score(answer,truth);print(json.dumps(r,indent=2))
    if len(sys.argv)==1:
        out=Path('/logs/verifier');out.mkdir(parents=True,exist_ok=True)
        (out/'metrics.json').write_text(json.dumps(r,indent=2)+'\n');(out/'reward.txt').write_text(str(r['reward'])+'\n')

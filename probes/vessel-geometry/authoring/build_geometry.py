"""Curate a natural error; construct reference-assisted repair and geometry outputs."""
from pathlib import Path
import hashlib, json
import numpy as np
import nibabel as nib
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from geometry import *

ROOT=Path(__file__).resolve().parents[3]; B=ROOT/'runs/br030-vessel-geometry'
D=B/'sources/coronary/ImageCAS-X_dataset'; HERE=Path(__file__).resolve().parent

def save(path,a,aff):
    n=nib.Nifti1Image(a,aff);n.set_sform(aff,code=1);n.set_qform(aff,code=1);nib.save(n,path)

def generate_outputs(out,mask,aff,image,path,angles=np.arange(0,360,45),offsets=np.arange(-8,8.001,.25)):
    out.mkdir(parents=True,exist_ok=True)
    q,s=resample_path(path);t,n,b=frames(q)
    coords=cpr_coordinates(q,n,b,angles,offsets)
    hu=sample(image,aff,coords)
    np.save(out/'centerline.npy',q.astype('float32'))
    np.savez_compressed(out/'cpr.npz',hu=hu,source_ras_mm=coords.astype('float32'),
                        angles_deg=angles,offsets_mm=offsets,arc_mm=s)
    section_offsets=np.arange(-8,8.001,.25)
    xyz=section_coordinates(q,n,b,section_offsets)
    sections=sample(image,aff,xyz)
    seg=sample(mask,aff,xyz,0,0)>0
    # Only central cross-section component; never measure a neighboring artery.
    area=[]
    for cut in seg:
        cc,_=ndi.label(cut); k=cc[len(cut)//2,len(cut)//2]
        area.append(float((cc==k).sum()*.25**2) if k else 0.)
    np.savez_compressed(out/'sections.npz',hu=sections,mask=seg,offsets_mm=section_offsets,area_mm2=area)
    save(out/'corrected_mask.nii.gz',mask.astype('uint8'),aff)
    mesh=mesh_from_mask(mask,aff);mesh.export(out/'vessels.ply')
    return {'route_length_mm':float(s[-1]),'samples':len(q),'cpr_shape':list(hu.shape),
            'mesh_vertices':len(mesh.vertices),'mesh_faces':len(mesh.faces),
            'mesh_watertight':bool(mesh.is_watertight),'mesh_volume_mm3':float(mesh.volume),
            'mask_volume_mm3':float(mask.sum()*abs(np.linalg.det(aff[:3,:3]))),
            'frame_max_orthogonality_error':float(np.max(np.abs(np.sum(t*n,axis=1)))),
            'source_centerline_coverage':float((sample(mask,aff,q,0,0)>0).mean())}

def main():
    out=B/'geometry';out.mkdir(exist_ok=True)
    scan=nib.load(B/'sources/coronary/original/1.img.nii.gz')
    gt0=np.asarray(nib.load(D/'segmentations/1.coronary.nii.gz').dataobj)
    pred0=np.asarray(nib.load(B/'predictions/coronary-1-casnet.nii.gz').dataobj)>0
    box=np.argwhere((gt0>0)|pred0);lo=np.maximum(0,box.min(0)-24);hi=np.minimum(gt0.shape,box.max(0)+25)
    sl=tuple(slice(int(a),int(z)) for a,z in zip(lo,hi));aff=scan.affine.copy();aff[:3,3]=transform(lo,scan.affine)
    im=np.asarray(scan.dataobj)[sl].astype('int16');gt=gt0[sl]>0;pred=pred0[sl].copy()
    x,f,lines=read_centerline(D/'centerlines/1.coronary_right_centerline.vtk');path,ids=named_route(x,f,lines,10);q,s=resample_path(path)
    gap=runs_of_false(sample(pred,aff,q,0,0)>0);assert len(gap)==1
    i,j=gap[0];assert i>0 and j<len(q);center=q[(i+j-1)//2]
    # Local 8-mm review sphere. The input prediction itself is never altered.
    vcenter=transform(center,np.linalg.inv(aff));sp=nib.affines.voxel_sizes(aff)
    axes=np.ogrid[tuple(slice(0,n) for n in pred.shape)]
    editable=sum(((a-v)*w)**2 for a,v,w in zip(axes,vcenter,sp))<=8**2
    repaired=pred.copy();repaired[editable]=gt[editable]
    cc0,n0=ndi.label(pred,np.ones((3,3,3)));cc1,n1=ndi.label(repaired,np.ones((3,3,3)))
    anchor=q[[i-3,j+3]];oldids=sample(cc0,aff,anchor,0,0).astype(int);newids=sample(cc1,aff,anchor,0,0).astype(int)
    assert oldids[0]!=oldids[1] and all(oldids>0)
    assert newids[0]==newids[1] and newids[0]>0
    public=out/'input';public.mkdir(exist_ok=True)
    save(public/'image.nii.gz',im,aff);save(public/'proposed_mask.nii.gz',pred.astype('uint8'),aff)
    save(public/'editable_region.nii.gz',editable.astype('uint8'),aff)
    contract={'route':'RCA ostium to distal right posterior descending artery (R-PDA)',
              'coordinate_system':'RAS millimeters (NIfTI affine), array axes XYZ',
              'start_ras_mm':q[0].tolist(),'end_ras_mm':q[-1].tolist(),
              'review_center_ras_mm':center.tolist(),'review_radius_mm':8.,
              'angles_deg':list(range(0,360,45)),'offsets_mm':np.arange(-8,8.001,.25).tolist(),
              'source':'ImageCAS case 1 CTA; unedited ImageCAS-X CAS-Net prediction; local development experiment'}
    (public/'request.json').write_text(json.dumps(contract,indent=2)+'\n')
    np.savez_compressed(out/'reference.npz',gt=gt,editable=editable,affine=aff,
                        proposed=pred,reference_path=q,image=im,anchors=anchor,
                        route_corridor_points=q[max(0,i-20):min(len(q),j+20)])
    result=generate_outputs(out/'oracle',repaired,aff,im,path)
    roi_gt=gt&editable;deleted=roi_gt&~pred;added=pred&editable&~gt
    ds=sample(im,aff,q[i:j]);bg=im[editable&~gt]
    result.update({'round':'BR-030','input_crop_shape':list(im.shape),'crop_origin_ijk':lo.tolist(),
        'source_prediction_sha256':hashlib.sha256((B/'predictions/coronary-1-casnet.nii.gz').read_bytes()).hexdigest(),
        'natural_gap_start_mm':float(s[i]),'natural_gap_end_mm':float(s[j]),
        'missing_sample_span_mm':float(s[j-1]-s[i]),'gap_sampling_estimate_mm':float((j-i)*(s[1]-s[0])),
        'reference_centerline_missing_sample_HU':np.percentile(ds,[10,50,90]).tolist(),
        'review_background_HU_p10_p50_p90':np.percentile(bg,[10,50,90]).tolist(),
        'before_components':int(n0),'after_components':int(n1),'gap_anchor_components_before':oldids.tolist(),'gap_anchor_components_after':newids.tolist(),
        'oracle_added_voxels':int(deleted.sum()),'oracle_removed_voxels':int(added.sum()),
        'edits_outside_review':int(np.count_nonzero((repaired!=pred)&~editable)),
        'oracle_provenance':'Reference-assisted local replacement and released reference centerline; this establishes artifact feasibility, not independent agent performance.',
        'reference_dependence':'Released centerlines and surfaces are derived from segmentation; they are not independent expert anatomy annotations.',
        'clinical_scope':'Geometric review of contrast-filled lumen, not validated stenosis/plaque diagnosis. Only scan-level disease descriptor supplied.'})
    (out/'build-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()

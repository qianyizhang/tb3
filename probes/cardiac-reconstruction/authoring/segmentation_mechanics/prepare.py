"""Export masks without material IDs and matching calibrated image arrays."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from PIL import Image
from geometry import voxelize,cavity_mask
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br035-segmentation-mechanics';S=ROOT/'runs/br029-dynamic-heart'
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'dynamic_heart'))
from prepare_video import mhd

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    dst=B/'prepared';dst.mkdir(exist_ok=False)
    z=dict(np.load(S/'analysis-v2/healthy_reference.npz'));points=z['points'];tet=z['tetra'];spacing=np.ones(3)*1.5
    origin=np.floor(points[0].min(0))-12;high=np.ceil(points[0].max(0))+12;shape=tuple((np.ceil((high-origin)/spacing).astype(int)+1)[::-1])
    zz,yy,xx=np.indices(shape);grid=origin+np.stack([xx,yy,zz],-1)*spacing
    g=json.loads((S/'public-video/geometry.json').read_text());R=np.array(g['canonical_to_native_rotation_rows']);offset=np.array(g['canonical_to_native_offset']);sp=np.array(g['source_spacing_mm'])
    coords=np.moveaxis(((np.einsum('...i,ij->...j',grid,R)+offset)/sp)[...,::-1],-1,0)
    masks=[];images=[]
    for t,p in enumerate(points):
        mask=voxelize(p,tet,origin,spacing,shape);masks.append(mask)
        image,_=mhd(S/'source/patient01_healthy/image'/f'usfrm{t:02d}.mhd');images.append(map_coordinates(image.astype('float32'),coords,order=1,mode='constant'))
        print('synthetic',t,int(mask.sum()),flush=True)
    masks=np.array(masks);images=np.array(images,dtype='float32')
    metadata=dict(shape_tzyx=list(masks.shape),origin_xyz_mm=origin.tolist(),spacing_xyz_mm=spacing.tolist(),mask_semantics='myocardial_wall',reference_frame=0,phase=(np.arange(30)/30).tolist(),timestamps_s=None,array_mapping='array[t,z,y,x] maps to origin_xyz_mm + spacing_xyz_mm*[x,y,z]',note='Binary mask encloses the biventricular myocardial tissue, including its inner and outer boundaries. No material identities or AHA labels are encoded. All arrays share this physical grid.')
    np.savez_compressed(dst/'synthetic_masks.npz',masks=masks);np.save(dst/'synthetic_images.npy',images);(dst/'synthetic_geometry.json').write_text(json.dumps(metadata,indent=2)+'\n')
    weights=abs(np.linalg.det(points[0][tet[:,1:]]-points[0][tet[:,:1]]))/6
    quant=masks.sum((1,2,3))*np.prod(spacing);meshvol=np.array([abs(np.linalg.det(p[tet[:,1:]]-p[tet[:,:1]])).sum()/6 for p in points])
    # Every original cell centroid is an independent material probe; no new-mesh vertex identities assumed.
    np.savez_compressed(dst/'truth.npz',points=points,tetra=tet,directions=z['directions'],cell_labels=z['cell_labels'],weights=weights)
    audit=dict(synthetic_mask_vs_mesh_volume_mean_error_pct=float(100*np.mean(abs(quant/meshvol-1))),synthetic_grid_shape=list(masks.shape),source_reference_sha256=sha(S/'analysis-v2/healthy_reference.npz'),source_geometry_sha256=sha(S/'public-video/geometry.json'))
    # Clinical transfer: same public case as BR-034, masks now supplied throughout the cycle.
    C=ROOT/'runs/br034-pathological-echo';ref=dict(np.load(C/'reference.npz'));cg=json.loads((C/'input/geometry.json').read_text());vol=np.load(C/'input/volumes.npy',mmap_mode='r')
    corigin=np.array(cg['origin_xyz_mm']);cshape=tuple((np.ceil((np.array(vol.shape[1:])-1)/1.5).astype(int)+1));zz,yy,xx=np.indices(cshape);cgrid=corigin+np.stack([xx,yy,zz],-1)*spacing
    cc=np.moveaxis(((cgrid-corigin)/np.array(cg['spacing_xyz_mm']))[...,::-1],-1,0)
    cm=[];ci=[]
    for t,p in enumerate(ref['points']):
        cm.append(cavity_mask(p,ref['faces'],corigin,spacing,cshape));ci.append(map_coordinates(vol[t].astype('float32'),cc,order=1,mode='constant'));print('clinical',t,flush=True)
    cm=np.array(cm);ci=np.array(ci,dtype='float32');np.savez_compressed(dst/'clinical_masks.npz',masks=cm);np.save(dst/'clinical_images.npy',ci)
    meta={**metadata,'shape_tzyx':list(cm.shape),'origin_xyz_mm':corigin.tolist(),'mask_semantics':'lv_cavity','phase':(np.arange(len(cm))/len(cm)).tolist(),'timestamps_s':cg['timestamps_s'],'note':'The mask is the closed LV blood-pool cavity including basal closure. There is no myocardial wall or epicardial surface. Geometric deformation of this domain cannot be interpreted as myocardial strain.'}
    (dst/'clinical_geometry.json').write_text(json.dumps(meta,indent=2)+'\n')
    f=ref['faces'];v=np.abs(np.sum(np.einsum('tfi,tfi->tf',ref['points'][:,f[:,0]],np.cross(ref['points'][:,f[:,1]],ref['points'][:,f[:,2]])),axis=1))/6000
    mv=cm.sum((1,2,3))*1.5**3/1000
    audit.update(clinical_source_sha256=sha(C/'reference.npz'),clinical_reference_volume_ml=v.tolist(),clinical_mask_volume_ml=mv.tolist(),clinical_reference_ef_pct=float(100*(1-v.min()/v.max())),clinical_mask_ef_pct=float(100*(1-mv.min()/mv.max())))
    audit['clinical_mask_vs_surface_volume_mean_error_pct']=float(100*np.mean(abs(mv/v-1)))
    assert audit['synthetic_mask_vs_mesh_volume_mean_error_pct']<2
    assert audit['clinical_mask_vs_surface_volume_mean_error_pct']<2
    assert abs(audit['clinical_reference_ef_pct']-audit['clinical_mask_ef_pct'])<1
    # Representative image/mask overlays, separate from solver observations.
    for kind,im,mask in [('synthetic',images,masks),('clinical',ci,cm)]:
        t=int(np.argmin(mask.sum((1,2,3))));panels=[]
        from scipy.ndimage import binary_erosion
        for axis in [0,1,2]:
            mid=mask.shape[axis+1]//2;sl=np.take(im[t],mid,axis=axis);sg=np.take(mask[t],mid,axis=axis);gray=np.clip(sl/max(np.percentile(im[0],99.8),1)*255,0,255).astype('uint8');rgb=np.repeat(gray[...,None],3,axis=2);rgb[sg&~binary_erosion(sg)]=[255,170,40];panels.append(Image.fromarray(rgb).resize((320,320)))
        canvas=Image.new('RGB',(960,320));[canvas.paste(p,(i*320,0)) for i,p in enumerate(panels)];canvas.save(B/f'{kind}-mask-audit.png')
    (B/'preparation.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))
if __name__=='__main__':main()

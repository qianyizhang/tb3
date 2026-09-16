"""Decode a selected clinical recording and separate ED initialization from held-out reference."""
import argparse,hashlib,json,tarfile
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from PIL import Image,ImageDraw
from screen import arr,mesh,volume

ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br034-pathological-echo';S=B/'source'
def main():
    global B
    parser=argparse.ArgumentParser();parser.add_argument('exam');parser.add_argument('recording');parser.add_argument('--output-root',default=str(B));args=parser.parse_args()
    B=Path(args.output_root);B.mkdir(parents=True,exist_ok=True)
    rec=args.recording.removesuffix('.zarr');folder=S/args.exam/'exams'/args.exam/(rec+'.zarr')
    with tarfile.open(S/(args.exam+'.tar')) as tar:
        for m in tar:
            if m.isfile() and rec+'.zarr' in Path(m.name).parts:
                assert '..' not in Path(m.name).parts and not Path(m.name).is_absolute()
                p=S/args.exam/m.name;p.parent.mkdir(parents=True,exist_ok=True)
                if not p.exists():p.write_bytes(tar.extractfile(m).read())
    metadata=json.loads((folder/'.zattrs').read_text());man=metadata['recording_manifest'];geo=man['sectors'][0]['geometry']
    native=arr(folder/'data/3d_brightness_mode');ts=arr(folder/'timestamps/3d_brightness_mode');mt=arr(folder/'timestamps/3d_left_ventricle_mesh')
    raw_ts=ts.copy();origin=man['metadata']['time_reference']['origin_s']
    if ts.min()>=origin-1e-6:ts=ts-origin
    pp,ff=mesh(folder/'data/3d_left_ventricle_mesh');assert all(np.array_equal(ff[0],x) for x in ff)
    # EchoXFlow's mesh rendering convention: scanner XYZ -> (-X, Z, Y).
    # Match its published _MESH_RENDER_FRAME_TRANSFORM before spherical sampling.
    pp=pp[:,:,[0,2,1]]*np.array([-1.,1.,1.])
    faces=ff[0];refvol=np.array([volume(x,faces) for x in pp]);ed=int(refvol.argmax());assert ed==0,'Keep natural source-cycle order; inspect noninitial ED separately'
    # Source surface timestamps identify a native acquired beat, not a synthetically repeated cycle.
    ids=np.abs(ts[:,None]-mt[None,:]).argmin(0);err=np.abs(ts[ids]-mt)
    assert np.all(np.diff(ids)==1) and err.max()<.005
    center=pp[0].mean(0);cov=np.linalg.eigh(np.cov((pp[0]-center).T));z=cov[1][:,-1]
    if z[2]<0:z=-z
    x=cov[1][:,-2];y=np.cross(z,x);basis=np.stack([x,y,z],axis=1)
    points=np.einsum('tni,ij->tnj',pp-center,basis)
    tri=points[0,faces]
    if np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()<0:faces=faces[:,[0,2,1]]
    # Crop and axes are determined only by the permitted initial surface.
    spacing=1.;lo=np.floor(points[0].min(0)-18);hi=np.ceil(points[0].max(0)+18);shape=np.ceil((hi-lo)/spacing).astype(int)+1
    zz,yy,xx=np.meshgrid(*(np.arange(shape[i])*spacing+lo[i] for i in [2,1,0]),indexing='ij')
    local=np.stack([xx,yy,zz],-1);world=np.einsum('...j,ij->...i',local,basis)+center
    wx,wy,wz=np.moveaxis(world/1000,-1,0);radius=np.sqrt(wx**2+wy**2+wz**2)
    az=np.arctan2(wx,np.sqrt(wy**2+wz**2));el=np.arctan2(wy,wz)
    coords=np.array([(el/geo['ElevationWidth']+.5)*(native.shape[1]-1),(az/geo['Width']+.5)*(native.shape[2]-1),(radius-geo['DepthStart'])/(geo['DepthEnd']-geo['DepthStart'])*(native.shape[3]-1)])
    grid=np.stack([map_coordinates(native[i],coords,order=1,mode='constant',cval=0) for i in ids]).astype('uint8')
    out=B/'input';out.mkdir(exist_ok=False);np.save(out/'volumes.npy',grid)
    np.savez_compressed(out/'initial_mesh.npz',points=points[0],faces=faces)
    np.savez_compressed(B/'reference.npz',points=points,faces=faces)
    cal=dict(shape_tzyx=list(grid.shape),origin_xyz_mm=lo.tolist(),spacing_xyz_mm=[spacing]*3,
             timestamps_s=(ts[ids]-ts[ids[0]]).tolist(),initial_mesh_frame=0,
             array_mapping='volumes[t,z,y,x] maps to origin_xyz_mm + spacing_xyz_mm*[x,y,z]; points use this same mm coordinate system',
             input_scope='One contiguous acquired cardiac cycle, Cartesian resampled B-mode, initial LV endocardial surface including basal closure; no myocardial wall, Doppler, clinical report or follow-up reference supplied.')
    (out/'geometry.json').write_text(json.dumps(cal,indent=2)+'\n')
    # Original appearance, with no GT overlaid, is made readily inspectable.
    ci=np.rint((np.zeros(3)-lo)/spacing).astype(int);montage=Image.new('RGB',(3*320,4*340),'#101623');draw=ImageDraw.Draw(montage)
    vis=[0,int(refvol.argmin()),len(grid)//2,len(grid)-1]
    prev=out/'previews';prev.mkdir()
    for t,g in enumerate(grid):
        slices=[g[:,ci[1],:],g[:,:,ci[0]],g[ci[2],:,:]]
        for k,im in enumerate(slices):
            pic=Image.fromarray(im).convert('RGB');pic.save(prev/f'plane{k+1}_{t:03d}.png')
            if t in vis:
                r=vis.index(t);scale=min(310/pic.width,310/pic.height);pic=pic.resize((round(pic.width*scale),round(pic.height*scale)));montage.paste(pic,((k*320)+(320-pic.width)//2,r*340+25));draw.text((k*320+8,r*340+7),f'Plane {k+1} / frame {t+1}',fill='white')
    montage.save(B/'curation-contact.png')
    recpt=dict(exam=args.exam,recording=rec,source_archive_sha256=hashlib.sha256((S/(args.exam+'.tar')).read_bytes()).hexdigest(),
        native_shape=list(native.shape),selected_native_frame_indices_zero_based=ids.tolist(),native_timestamps_s=raw_ts[ids].tolist(),relative_native_timestamps_s=ts[ids].tolist(),reference_timestamps_s=mt.tolist(),
        maximum_time_alignment_error_s=float(err.max()),reference_ef_pct=float(100*(1-refvol.min()/refvol.max())),reference_volume_ml=refvol.tolist(),
        source_geometry=geo,mesh_to_render_transform=[[-1,0,0],[0,0,1],[0,1,0]],local_to_source_basis=basis.tolist(),local_to_source_center_mm=center.tolist(),
        reference_inside_crop=bool(np.all(points>=lo) and np.all(points<=hi)),input_shape=list(grid.shape),
        source_metadata_sha256=hashlib.sha256((folder/'.zattrs').read_bytes()).hexdigest(),
        native_array_sha256=hashlib.sha256(native.tobytes()).hexdigest(),
        reference_scope='Clinician/software-derived LV endocardial annotation, not material-motion truth or confirmed disease etiology')
    (B/'preparation.json').write_text(json.dumps(recpt,indent=2)+'\n');print(json.dumps(recpt,indent=2))
if __name__=='__main__':main()

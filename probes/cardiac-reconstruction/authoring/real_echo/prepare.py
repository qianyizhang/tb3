"""Calibrated image-only input and author-only review slices of one real scan."""
import json, hashlib
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from scipy.spatial.transform import Rotation
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br032-real-echo';H=256;S=.75

def sampling(native,points):
    bounds=native['bounds'];x,y,z=np.asarray(points).T;r=np.sqrt(x*x+y*y+z*z)
    p=np.arctan2(z,x);t=np.arcsin(np.divide(y,r,out=np.zeros_like(y),where=r>1e-8))
    q=np.stack([r,p,t]);shape=np.asarray(native['images'].shape[1:])
    return (q-bounds[:,0,None])/(bounds[:,1]-bounds[:,0])[:,None]*(shape[:,None]-1)

def main():
    z=dict(np.load(B/'native.npz'));R=Rotation.from_euler('zyx',[17,-23,31],degrees=True).as_matrix();offset=np.array([13.4,-27.8,6.2])
    specs=[]
    for a in [0,90,45,135]:
        q=np.deg2rad(a);specs.append(dict(name=f'long_{a}',origin=[90,0,0],u=[0,np.sin(q),np.cos(q)],v=[1,0,0]))
    for x in [45,65,85,105]:specs.append(dict(name=f'short_{x}',origin=[x,0,0],u=[0,0,1],v=[0,1,0]))
    native_specs=[];frames=[];c=(H-1)/2
    rr,cc=np.mgrid[:H,:H];uv=np.stack([(cc-c)*S,(rr-c)*S],axis=-1).reshape(-1,2)
    for p in specs:
        pts=np.array(p['origin'])+uv[:,0,None]*p['u']+uv[:,1,None]*p['v']
        q=sampling(z,pts)
        arr=np.stack([map_coordinates(f,q,order=1,mode='constant').reshape(H,H) for f in z['images']])
        frames.append(arr);native_specs.append(p)
    frames=np.stack(frames)
    np.savez_compressed(B/'review-slices.npz',images=frames)
    (B/'plane-preview.json').write_text(json.dumps(specs,indent=2)+'\n')
    sheet=Image.new('RGB',(4*H,8*(H+28)))
    draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(specs):
        for j,t in enumerate([0,5,10,17]):
            sheet.paste(Image.fromarray(frames[i,t]).convert('RGB'),(j*H,i*(H+28)))
            draw.text((j*H+6,i*(H+28)+H+4),f'{p["name"]} / source frame {t+1}',fill='white')
    sheet.save(B/'source-contact.png')
    public=B/'input';public.mkdir(exist_ok=False)
    observed=[0,1,5,7];withheld=[2,3,4,6]
    def converted(p):
        return dict(name=p['name'],origin=(np.asarray(p['origin'])@R.T+offset).tolist(),
                    u=(np.asarray(p['u'])@R.T).tolist(),v=(np.asarray(p['v'])@R.T).tolist())
    planes=[]
    for j,i in enumerate(observed):
        folder=public/f'view_{j}';folder.mkdir()
        for t,img in enumerate(frames[i]):Image.fromarray(img).save(folder/f'frame_{t+1:02d}.png')
        p=converted(specs[i]);p['name']=f'view_{j}';planes.append(p)
    geometry=dict(frames=18,image_size=[H,H],pixel_center=c,spacing_mm=S,planes=planes,
                  times_seconds=(np.arange(18)*.16115).tolist(),time_source='DICOM FrameTime 161.15 ms; matches 18 source volume frames',
                  formula='pixel(column,row) = origin + spacing_mm*((column-pixel_center)*u + (row-pixel_center)*v)',
                  task_axes=dict(depth=R[:,0].tolist(),transverse_1=R[:,1].tolist(),transverse_2=R[:,2].tolist()),
                  frame_ids=list(range(1,19)),calibration_note='Views are reslices of one simultaneous 3D acquisition; not separate probe acquisitions.')
    (public/'geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
    np.savez_compressed(B/'private-review.npz',images=frames,observed=observed,withheld=withheld)
    (B/'private-review.json').write_text(json.dumps(dict(planes=[converted(p) for p in specs],
        source_to_task_R=R.tolist(),source_to_task_translation=offset.tolist(),observed=observed,withheld=withheld,
        pixel_center=c,spacing_mm=S,frames=18,image_size=[H,H]),indent=2)+'\n')
    # Inverse transforms and source-grid interpolation are checked independently.
    rng=np.random.default_rng(320916);p=rng.normal(size=(300,3))*40+np.array([80,0,0])
    roundtrip=(p@R.T+offset-offset)@R
    assert np.max(abs(roundtrip-p))<1e-10
    r=np.linspace(z['bounds'][0,0],z['bounds'][0,1],z['images'].shape[1])
    ph=np.linspace(*z['bounds'][1],z['images'].shape[2]);th=np.linspace(*z['bounds'][2],z['images'].shape[3])
    inds=np.array([rng.integers(1,n-1,300) for n in z['images'].shape[1:]])
    rv,pv,tv=r[inds[0]],ph[inds[1]],th[inds[2]]
    pts=np.stack([rv*np.cos(pv)*np.cos(tv),rv*np.sin(tv),rv*np.sin(pv)*np.cos(tv)],axis=1)
    assert np.max(abs(sampling(z,pts)-inds))<1e-8
    check=dict(source_grid_inverse_error=float(np.max(abs(sampling(z,pts)-inds))),
               coordinate_roundtrip_error_mm=float(np.max(abs(roundtrip-p))),observed=observed,withheld=withheld,
               source_frame_ids=list(range(1,19)),phase_resampling='none; all 18 original frames retained in order',
               input_files={str(f.relative_to(public)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(public.rglob('*')) if f.is_file()})
    (B/'input-validation.json').write_text(json.dumps(check,indent=2)+'\n')
    print(B/'source-contact.png')

if __name__=='__main__':main()

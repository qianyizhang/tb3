"""Prepare a paired 3D / single-view experiment before baseline or model runs."""
import itertools
import json
from pathlib import Path
import numpy as np
import nibabel as nib
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
from geometry import errors,rigid_fit,affine_fit

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br021-deformable'

def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def window(x):return np.rint(np.clip((x+1000)/1200,0,1)*255).astype(np.uint8)


def main():
    assert not (OUT/'author/public-2d').exists(),'Preserve earlier preparation'
    audit=json.loads((OUT/'author/source-audit.json').read_text());case=audit['selected_case']
    source=OUT/'source/LungCT'
    images=[nib.load(source/f'imagesTr/LungCT_{case:04d}_{i:04d}.nii.gz') for i in [0,1]]
    hu=[np.asarray(im.dataobj).astype(np.float32) for im in images];a=images[0].affine
    ijk=[np.loadtxt(source/f'landmarksTr/LungCT_{case:04d}_{i:04d}.csv',delimiter=',') for i in [0,1]]
    x,y=[np.einsum('ij,nj->ni',a[:3,:3],q)+a[:3,3] for q in ijk]
    triples=np.array(list(itertools.combinations(range(len(x)),3)))
    normals=np.cross(x[triples[:,1]]-x[triples[:,0]],x[triples[:,2]]-x[triples[:,0]])
    length=np.linalg.norm(normals,axis=1)
    good=(length>1500)&(np.max(np.abs(normals),axis=1)<.965*length)
    triples=triples[good];normals=normals[good]/length[good,None]
    groups={}
    for start in range(0,len(triples),1024):
        n=normals[start:start+1024];tri=triples[start:start+1024]
        dist=np.abs(np.einsum('ni,mi->nm',n,x)-np.einsum('ni,ni->n',n,x[tri[:,0]])[:,None])
        for local in np.flatnonzero(np.sum(dist<=.35,axis=1)>=8):
            ids=tuple(np.flatnonzero(dist[local]<=.35).tolist())
            groups.setdefault(ids,(tri[local],n[local]))
    candidates=[]
    for ids,(tri,n) in groups.items():
        ids=np.array(ids);p=x[tri[0]];n=n.copy()
        if n[1]<0:n=-n
        u=np.array([1.,0,0]);u-=n*np.dot(u,n);u/=np.linalg.norm(u);v=np.cross(n,u)
        xy=np.column_stack([np.einsum('ni,i->n',x[ids]-p,u),np.einsum('ni,i->n',x[ids]-p,v)])
        span=np.ptp(xy,axis=0)
        if np.min(span)<70:continue
        projected=p+np.outer(xy[:,0],u)+np.outer(xy[:,1],v)
        rigid=errors(rigid_fit(projected,y[ids]),y[ids]);affine=errors(affine_fit(projected,y[ids]),y[ids])
        if affine['rms_mm']<=3:continue
        spacing=1.25;lo=xy.min(0)-16;size=np.ceil((span+32)/spacing).astype(int)+1
        origin=p+lo[0]*u+lo[1]*v
        corners=np.array([origin+xx*spacing*u+yy*spacing*v for xx in [0,size[0]-1] for yy in [0,size[1]-1]])
        indices=np.einsum('ij,nj->ni',np.linalg.inv(a[:3,:3]),corners-a[:3,3])
        if not (np.all(indices>=0)&np.all(indices<=np.array(hu[0].shape)-1)):continue
        candidates.append((len(ids),float(np.prod(span)),ids,u,v,n,origin,size,(xy-lo)/spacing,rigid,affine,projected))
    assert candidates,'No sufficiently visible nonrigid oblique section found; do not relax after model trials'
    candidates.sort(key=lambda c:(-c[0],-c[1],tuple(c[2])))
    _,_,ids,u,v,n,origin,size,uv,rigid,affine,projected=candidates[0]
    pose=np.eye(4);pose[:3,:3]=np.column_stack([u,v,n]);pose[:3,3]=origin
    yy,xx=np.indices((int(size[1]),int(size[0])))
    world=origin[:,None]+u[:,None]*xx.ravel()*spacing+v[:,None]*yy.ravel()*spacing
    vox=np.einsum('ij,jn->in',np.linalg.inv(a[:3,:3]),world-a[:3,3,None])
    view=map_coordinates(hu[0],vox,order=1,prefilter=False).reshape(yy.shape).astype(np.float32)
    (OUT/'author').mkdir(exist_ok=True)
    for kind in ['2d','3d']:
        d=OUT/'author'/f'public-{kind}';d.mkdir()
        np.savez_compressed(d/'volume.npz',hu=hu[1],voxel_to_world=a)
        if kind=='2d':
            np.save(d/'view.npy',view,allow_pickle=False);Image.fromarray(window(view)).save(d/'view.png')
            write(d/'view.json',{'shape':list(view.shape),'spacing_xy_mm':[spacing,spacing],
                 'slice_to_world':pose.tolist(),'phase':'exhale',
                 'description':'Nominal exhale acquisition geometry, not the anatomical mapping into inhale.'})
            write(d/'queries.json',{'query_ids':[f'q{i+1:02d}' for i in range(len(ids))],'pixels_uv':uv.tolist()})
        else:
            np.savez_compressed(d/'reference_volume.npz',hu=hu[0],voxel_to_world=a)
            write(d/'queries.json',{'query_ids':[f'q{i+1:02d}' for i in range(len(ids))],'reference_world_mm':x[ids].tolist()})
    truth={'query_ids':[f'q{i+1:02d}' for i in range(len(ids))],'points_world_mm':y[ids].tolist(),
           'rms_tolerance_mm':3.,'max_tolerance_mm':5.}
    write(OUT/'author/truth.json',truth)
    write(OUT/'author/preparation.json',{'case':case,'query_source_indices':ids.tolist(),
        'candidate_planes_considered':len(groups),'admitted_planes':len(candidates),
        'selection':'Most near-coplanar manual landmarks, then largest footprint; >=8 points, <=0.35 mm off plane, >=15 degree obliquity, >=70 mm spans, in-volume corners, privileged affine residual >3 mm.',
        'query_count':len(ids),'shape':list(view.shape),'slice_to_world':pose.tolist(),
        'off_plane_mm':np.linalg.norm(x[ids]-projected,axis=1).tolist(),
        'identity_2d':errors(projected,y[ids]),'best_rigid_2d':rigid,'best_affine_2d':affine,
        'best_rigid_3d':errors(rigid_fit(x[ids],y[ids]),y[ids]),'best_affine_3d':errors(affine_fit(x[ids],y[ids]),y[ids]),
        'nominal_geometry_public':True,'paired_query_set':True,
        'limitation':'Sparse anatomical correspondence is graded; dense deformation between queried points is not validated.'})
    im=Image.fromarray(window(view)).convert('RGB').resize((view.shape[1]*3,view.shape[0]*3));draw=ImageDraw.Draw(im)
    for i,(px,py) in enumerate(uv):
        px*=3;py*=3;draw.ellipse((px-7,py-7,px+7,py+7),outline='#ff6058',width=2);draw.text((px+8,py-8),str(i+1),fill='#ffff88')
    im.save(OUT/'author/view-marked.png')
    print(json.dumps({'case':case,'queries':len(ids),'source_indices':ids.tolist(),'shape':view.shape,
                      'rigid_rms':rigid['rms_mm'],'affine_rms':affine['rms_mm'],
                      'max_off_plane_mm':float(np.max(np.linalg.norm(x[ids]-projected,axis=1)))},indent=2))

if __name__=='__main__':main()

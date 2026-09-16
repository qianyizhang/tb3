"""Compare matched 2D-source and full-source outcomes with actual CT reslices."""
import json
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from present import png
from score import score

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runs/br028-registration-3d-source'
def read(p):return json.loads(p.read_text())

def main():
    receipt=read(OUT/'results.json');analysis=read(OUT/'approach-analysis.json')
    public=OUT/'tasks/deform-patient3-source3d/environment/data';truth=read(public.parents[1]/'tests/truth.json')
    frame=read(public/'view.json');query=read(public/'queries.json');s=np.array(frame['slice_to_world']);view=np.load(public/'view.npy')
    with np.load(public/'volume.npz') as z:target,a=z['hu'],z['voxel_to_world']
    with np.load(public/'reference_volume.npz') as z:source,sa=z['hu'],z['voxel_to_world']
    positions=s[:3,3]+np.einsum('ij,nj->ni',s[:3,:2],np.array(query['pixels_uv'])*np.array(frame['spacing_xy_mm']))
    planes={'Original oblique plane':s[:3,:2],'Dataset XY':np.eye(3)[:,[0,1]],'Dataset XZ':np.eye(3)[:,[0,2]],'Dataset YZ':np.eye(3)[:,[1,2]]}
    yy,xx=np.mgrid[-48:49,-48:49];offsets=np.array([xx.ravel(),yy.ravel()])*.65
    def patch(volume,affine,p,basis):
        world=np.array(p)[:,None]+np.einsum('ij,jn->in',basis,offsets)
        ijk=np.einsum('ij,jn->in',np.linalg.inv(affine[:3,:3]),world-affine[:3,3,None])
        return png(map_coordinates(volume,ijk,order=1,prefilter=False,mode='constant',cval=-1000).reshape(97,97))
    data={'analysis':analysis,'ids':query['query_ids'],'source':{},'manual':{},'methods':{}}
    for name,basis in planes.items():
        data['source'][name]=[];data['manual'][name]=[patch(target,a,p,basis) for p in truth['points_world_mm']]
        for i,p in enumerate(positions):
            if name=='Original oblique plane':
                coords=np.array(query['pixels_uv'][i])[:,None]+offsets/np.array(frame['spacing_xy_mm'])[:,None]
                data['source'][name].append(png(map_coordinates(view,coords[::-1],order=1,prefilter=False,mode='constant',cval=-1000).reshape(97,97)))
            else:data['source'][name].append(patch(source,sa,p,basis))
    rows=[('Sol / original 2D source',receipt['prior_2d_attempt']),('Sol / full 3D source',next(r for r in receipt['prospective_rows'] if r['phase']=='sol-xhigh'))]
    rows += [('Author / retained 2D method',receipt['author_audit']['author_rows'][0]),('Author / 3D patch method',receipt['author_audit']['author_rows'][1])]
    for name,row in rows:
        if not row.get('answer_path'):continue
        answer=read(ROOT/row['answer_path']);data['methods'][name]={'grade':score(answer,truth),'seconds':row.get('agent_seconds'),
            'images':{plane:[patch(target,a,p,basis) for p in answer['points_world_mm']] for plane,basis in planes.items()}}
    dest=OUT/'review';dest.mkdir(exist_ok=True)
    html=Path(__file__).with_name('br028_review.html').read_text().replace('__DATA__',json.dumps(data).replace('</','<\\/'))
    (dest/'index.html').write_text(html);print(dest/'index.html')

if __name__=='__main__':main()

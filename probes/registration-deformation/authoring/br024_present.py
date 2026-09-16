"""Render actual CT patches and completed BR-024 evidence for local review."""
import json
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from present import png
from score import score

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runs/br024-harder-registration'
def read(p):return json.loads(p.read_text())

def main():
    receipt=read(OUT/'results.json');analysis=read(OUT/'approach-analysis.json');data={'analysis':analysis,'cases':[]}
    yy,xx=np.mgrid[-48:49,-48:49];offsets=np.array([xx.ravel(),yy.ravel()])*.65
    for row in receipt['curation']:
        candidate=row['candidate'];public=ROOT/candidate['public_path'];truth=read(ROOT/candidate['truth_path'])
        queries=read(public/'queries.json');frame=read(public/'view.json');view=np.load(public/'view.npy')
        basis=np.array(frame['slice_to_world'])[:3,:2]
        with np.load(public/'volume.npz') as z:volume,affine=z['hu'],z['voxel_to_world']
        def destination(point):
            world=np.array(point)[:,None]+np.einsum('ij,jn->in',basis,offsets)
            ijk=np.einsum('ij,jn->in',np.linalg.inv(affine[:3,:3]),world-affine[:3,3,None])
            return png(map_coordinates(volume,ijk,order=1,prefilter=False,mode='constant',cval=-1000).reshape(97,97))
        case={'name':candidate['name'],'patient':candidate['case'],'rank':candidate['rank'],'affine_rms_mm':candidate['best_affine']['rms_mm'],
              'admitted':row['admitted'],'ids':truth['query_ids'],'source':[],'manual':[destination(p) for p in truth['points_world_mm']],
              'overview':'../candidates/'+candidate['name']+'/view-marked.png','methods':{}}
        for pixel in queries['pixels_uv']:
            coords=np.array(pixel)[:,None]+offsets/np.array(frame['spacing_xy_mm'])[:,None]
            case['source'].append(png(map_coordinates(view,coords[::-1],order=1,prefilter=False,mode='constant',cval=-1000).reshape(97,97)))
        def add(name,record):
            answer=read(ROOT/record['answer_path']);case['methods'][name]={'grade':score(answer,truth),'seconds':record.get('agent_seconds'),
                                                                          'images':[destination(p) for p in answer['points_world_mm']]}
        for method,record in row['methods'].items():add(method,record)
        if row['admitted']:
            model=next(r for r in receipt['prospective_rows'] if r['task']==f'deform-harder-patient{candidate["case"]}' and r['phase']=='sol-xhigh')
            case['model_execution']=model['execution']
            if model.get('answer_path'):add('Sol / xhigh',model)
            if candidate['case']==3:
                for stage in read(OUT/'stage-analysis.json')['rows']:add('Sol stage / '+stage['transform'],stage)
        data['cases'].append(case)
    dest=OUT/'review';dest.mkdir(exist_ok=True)
    template=Path(__file__).with_name('br024_review.html').read_text()
    (dest/'index.html').write_text(template.replace('__DATA__',json.dumps(data).replace('</','<\\/')))
    print(dest/'index.html')

if __name__=='__main__':main()

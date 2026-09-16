"""Export a local WebGL workbench and full-precision, lazily loaded model data."""
import argparse
import json
from pathlib import Path
import shutil

import numpy as np
from mechanics import edge_matrices


def main():
    p=argparse.ArgumentParser();p.add_argument('--analysis',type=Path,required=True)
    p.add_argument('--public',type=Path,required=True);p.add_argument('--tissue',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    result=json.loads((a.analysis/'results.json').read_text())
    geometry=dict(np.load(a.analysis/'geometry.npz'))
    models=result['models'];paths={name:a.analysis/f'{name}.npz' for name in models}
    if a.tissue:
        models['tissue_fit']=json.loads((a.tissue/'results.json').read_text())['model']
        paths['tissue_fit']=a.tissue/'tissue_fit.npz'
    for name,path in paths.items():
        model=dict(np.load(path))
        valid=(model['cell_labels']>0)&np.all(np.linalg.norm(model['directions'],axis=-1)>.99,axis=0)
        weights=np.linalg.det(edge_matrices(model['points'][0],model['tetra']))/6
        models[name]['global_green_lagrange_percent']=(100*np.average(model['green_lagrange_directional'][:,valid],axis=1,weights=weights[valid])).tolist()
        rotations=[]
        for region_ids in [range(1,7),range(13,17)]:
            selected=np.isin(geometry['point_labels'],list(region_ids))
            initial=model['points'][0,selected,:2]
            initial=initial-initial.mean(0)
            angles=[]
            for points in model['points']:
                current=points[selected,:2];current=current-current.mean(0)
                angles.append(np.arctan2(np.sum(initial[:,0]*current[:,1]-initial[:,1]*current[:,0]),np.sum(initial*current)))
            rotations.append(np.unwrap(angles))
        models[name]['twist_degrees']=np.rad2deg(rotations[1]-rotations[0]).tolist()
        models[name]['twist_definition']='Apical AHA 13-16 minus basal AHA 1-6 least-squares material rotation in the fixed reference x-y plane; translation centered per region. Exploratory, not clinical torsion.'
        data=np.concatenate([model['points'],model['nodal_fields']],axis=-1).astype('<f4')
        data.tofile(a.output/f'{name}.bin')
        models[name]['file']=f'{name}.bin'
        models[name]['frames']=len(data)
    geo=dict(vertex_count=len(geometry['points']),tetra=geometry['tetra'].tolist(),
             faces=geometry['boundary'].tolist(),labels=geometry['point_labels'].tolist(),
             initial_points=geometry['points'].round(5).tolist(),
             center=geometry['points'].mean(0).tolist(),bounds=[geometry['points'].min(0).tolist(),geometry['points'].max(0).tolist()])
    data=dict(geometry=geo,models=models,video=json.loads((a.public/'geometry.json').read_text()),
              analytic_checks=result['analytic_checks'],source=result['source_url'])
    (a.output/'data.json').write_text(json.dumps(data,separators=(',',':')))
    shutil.copyfile(a.analysis/'results.json',a.output/'results.json')
    if a.tissue:
        shutil.copyfile(a.tissue/'results.json',a.output/'tissue-results.json')
    for i in range(4):
        shutil.copytree(a.public/f'view_{i}',a.output/f'view_{i}',dirs_exist_ok=True)
    shutil.copyfile(Path(__file__).with_name('workbench.html'),a.output/'index.html')
    print(a.output.resolve())


if __name__=='__main__':main()

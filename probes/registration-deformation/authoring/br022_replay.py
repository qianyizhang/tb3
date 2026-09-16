"""Container-only replay and instrumentation. No labels are read."""
import json
from pathlib import Path
import runpy
import shutil
import time
import numpy as np
import SimpleITK as sitk


def main():
    start=time.time()
    for name in ['reg.py','reg2d.py']:shutil.copy('/recovered/'+name,'/tmp/'+name)
    g=runpy.run_path('/tmp/reg2d.py');q=g['q'];M=g['M'];sx,sy=g['sx'],g['sy'];p=g['p'];cen=g['cen'][:,0];rot=g['rot'](p[:3])
    def rigid(x):return cen+rot@(x-cen)+p[3:6]
    records=[]
    for i,(u,v) in enumerate(q['pixels_uv']):
        x=np.array([u*sx,v*sy]);nominal=(M@np.r_[x,0,1])[:3]
        bs=np.array(g['bsout'].TransformPoint(tuple(x)));aff=np.array(g['aff'].TransformPoint(tuple(x)))
        records.append({'id':q['query_ids'][i],'nominal':nominal.tolist(),'rigid':rigid(nominal).tolist(),
            'affine_only':rigid((M@np.r_[aff,0,1])[:3]).tolist(),
            'direct_bspline':rigid((M@np.r_[bs,0,1])[:3]).tolist(),
            'original_composition':g['worldout'](x).tolist(),'final':np.asarray(g['outs'])[i].tolist()})
    dest=Path('/output');dest.mkdir(exist_ok=True)
    answer={'query_ids':q['query_ids'],'points_world_mm':np.asarray(g['outs']).tolist()}
    (dest/'points.json').write_text(json.dumps(answer,indent=2)+'\n')
    (dest/'stages.json').write_text(json.dumps({'queries':records,'elapsed_s':time.time()-start,
        'bspline_metric':g['R'].GetMetricValue(),'rigid_parameters':p.tolist(),'rigid_centre':cen.tolist()},indent=2)+'\n')
    sitk.WriteTransform(g['aff'],str(dest/'aff.tfm'));sitk.WriteTransform(g['bsout'],str(dest/'bs.tfm'))
    print('REPLAY_COMPLETE',time.time()-start,flush=True)


if __name__=='__main__':main()

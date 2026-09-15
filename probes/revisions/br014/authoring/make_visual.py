"""Embed actual source/retained coordinates in a compact explanation view."""
import argparse
import base64
import json
import sys
from pathlib import Path
import numpy as np
from common import ROOT, OUT
sys.path.insert(0, str(ROOT/'probes/revisions/br013/authoring'))
from inspect_scene import load_scene
from screen import world


def encode(o, label, color, rng):
    focus=label in ['pancreas','duodenum']
    points=o['surface_lps'];limit=3500 if focus else 600
    sampled=points[rng.choice(len(points),min(limit,len(points)),replace=False)]
    quantized=np.rint(sampled*10)
    assert quantized.min()>=-32768 and quantized.max()<=32767
    assert np.max(np.abs(quantized/10-sampled))<=.05001
    return dict(id=o['object_id'],source=label,focus=focus,color=color,
                ml=float(o['mask'].sum()*abs(np.linalg.det(o['affine_lps'][:3,:3]))/1000),
                center=np.mean(world(np.argwhere(o['mask']),o['affine_lps']),axis=0).tolist(),
                encoded=base64.b64encode(quantized.astype('<i2').tobytes()).decode())


def main():
    parser=argparse.ArgumentParser();parser.add_argument('template',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
    screen=json.loads((OUT/'author/component-screen.json').read_text());rng=np.random.default_rng(1401)
    truth=json.loads((ROOT/'runs/br013-abdomen/tasks/abdomen-a01/tests/expected.json').read_text())['truth']
    originals=load_scene(ROOT/'runs/br013-abdomen/build/abdomen-a01')
    payload={'modes':{},'removed':[], 'details':{
        'intact':'Original source masks · 2 target objects · 0 mL omitted',
        'gap0':'Lossless partition · 4 target fragments · 0 mL omitted',
        'gap6':'Synthetic 6 mm bands · 4 target fragments · 7.54 mL omitted'}}
    payload['modes']['intact']=[encode(o,truth[o['object_id']],0 if truth[o['object_id']]=='pancreas' else 1,rng) for o in originals]
    for v in screen['variants']:
        lineage={r['object_id']:r for r in v['lineage']}
        payload['modes'][f"gap{v['gap_mm']}"]=[encode(o,lineage[o['object_id']]['label'],(0 if lineage[o['object_id']]['label']=='pancreas' else 2)+(lineage[o['object_id']]['side'] or 0),rng) for o in load_scene(ROOT/v['data_path'])]
    for c in screen['variants'][1]['cuts']:
        o=next(o for o in originals if truth[o['object_id']]==c['label'])
        p=np.argwhere(o['mask']);q=world(p,o['affine_lps']);projection=np.sum(q*np.asarray(c['axis_lps']),axis=1)
        removed=(projection>=c['plane_offset_mm']-3)&(projection<c['plane_offset_mm']+3)
        assert int(removed.sum())==c['removed_voxels']
        q=q[removed]
        payload['removed'].append(dict(id='omitted',removed=True,focus=False,center=q.mean(0).tolist(),encoded=base64.b64encode(np.rint(q*10).astype('<i2').tobytes()).decode()))
    html=args.template.read_text();assert html.count('__DATA__')==1
    args.output.write_text(html.replace('__DATA__',json.dumps(payload,separators=(',',':'))))
    assert args.output.stat().st_size<1_000_000
    print(f'Wrote {args.output.stat().st_size} bytes; actual coordinates quantized to 0.1 mm for preview only.')


if __name__=='__main__':main()

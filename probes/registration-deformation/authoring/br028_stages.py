"""Posthoc grading of every captured full-volume candidate point array."""
import json
from pathlib import Path
import numpy as np
from collect import read,sha
from score import score

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runs/br028-registration-3d-source'

def main():
    capture=OUT/'captured-agent-artifacts';latest={};manifests=[]
    for p in capture.glob('*.json'):
        value=read(p)
        if value.get('captured_at') and isinstance(value.get('files'),dict):manifests.append((value['captured_at'],p,value))
    for _,p,value in sorted(manifests):
        for name,r in value['files'].items():latest[name]=r
    truth=read(OUT/'tasks/deform-patient3-source3d/tests/truth.json');rows=[]
    dest=OUT/'stage-analysis';dest.mkdir(exist_ok=True)
    for name,r in sorted(latest.items()):
        if not name.endswith('_points.npy'):continue
        path=ROOT/r['object_path'];assert sha(path)==r['sha256'];points=np.load(path,allow_pickle=False)
        assert points.shape==(8,3) and np.isfinite(points).all()
        answer={'query_ids':truth['query_ids'],'points_world_mm':points.tolist()};output=dest/(Path(name).stem+'.json')
        output.write_text(json.dumps(answer,indent=2)+'\n')
        rows.append({'stage':Path(name).name,'captured_path':name,'captured_object_path':r['object_path'],
                     'captured_sha256':r['sha256'],'grade':score(answer,truth),
                     'answer_path':str(output.relative_to(ROOT)),'answer_sha256':sha(output)})
    coverage=None
    if '/app/local_ncc.py' in latest:
        code=latest['/app/local_ncc.py'];text=(ROOT/code['object_path']).read_text()
        assert 'lo=(-22,-24,-12), hi=(12,16,18)' in text
        public=OUT/'tasks/deform-patient3-source3d/environment/data';g=read(public/'view.json');q=read(public/'queries.json');s=np.array(g['slice_to_world'])
        source=s[:3,3]+np.einsum('ij,nj->ni',s[:3,:2],np.array(q['pixels_uv'])*np.array(g['spacing_xy_mm']))
        with np.load(public/'reference_volume.npz') as z:a=z['voxel_to_world']
        offsets=np.einsum('ij,nj->ni',np.linalg.inv(a[:3,:3]),np.array(truth['points_world_mm'])-source)
        inside=np.all((offsets>=np.array([-22,-24,-12]))&(offsets<=np.array([12,16,18])),axis=1)
        coverage={'code_evidence':code,'bounds_voxels':[[-22,-24,-12],[12,16,18]],
                  'manual_offsets_voxels':offsets.tolist(),'each_manual_match_inside_search':inside.tolist(),
                  'all_manual_matches_inside_search':bool(inside.all()),
                  'scope':'Geometric coverage only; this does not establish that NCC selects the correct candidate.'}
    result={'round':'BR-028','kind':'posthoc candidate-array scoring; no optimization or agent feedback',
            'rows':rows,'manifest_receipts':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for _,p,_ in sorted(manifests)],
            'broad_3d_ncc_search_coverage':coverage,
            'limitations':['All captured final versions of named *_points.npy arrays are included, not just successful candidates.',
                           'These are observed candidate states, not independently randomized algorithm ablations.',
                           'Private labels enter only after public-input candidate computations.']}
    for p in [OUT/'stage-analysis.json',ROOT/'docs/evidence/br028-stage-analysis.json']:p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([{'stage':r['stage'],'grade':r['grade']} for r in rows],indent=2))

if __name__=='__main__':main()

"""Evaluate retained Sol transforms; no optimization or feedback to the agent."""
import json
from pathlib import Path
import shutil
import numpy as np
import SimpleITK as sitk
from collect import read,sha
from score import score

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runs/br024-harder-registration'

def main():
    captures=OUT/'captured-agent-artifacts-patient3';latest={};snapshots=[]
    manifests=[p for p in captures.glob('*.json') if read(p).get('captured_at') and isinstance(read(p).get('files'),dict)]
    for p in sorted(manifests,key=lambda p:read(p)['captured_at']):
        snap=read(p);snapshots.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
        for name,r in snap['files'].items():
            assert sha(ROOT/r['object_path'])==r['sha256'];latest[name]=r
    dest=OUT/'stage-analysis';dest.mkdir(exist_ok=True);recovered=dest/'transforms';recovered.mkdir(exist_ok=True)
    records={}
    for name,r in latest.items():
        if not name.endswith('.tfm'):continue
        path=recovered/Path(name).name;shutil.copyfile(ROOT/r['object_path'],path);records[path.name]=r
    task=OUT/'tasks/deform-harder-patient3';public=task/'environment/data';truth=read(task/'tests/truth.json')
    q=read(public/'queries.json');g=read(public/'view.json');s=np.array(g['slice_to_world'])
    positions=s[:3,3]+(np.array(q['pixels_uv'])*np.array(g['spacing_xy_mm']))@s[:3,:2].T
    rigid=sitk.ReadTransform(str(recovered/'rigid_-10.tfm'));rows=[]
    for name,r in sorted(records.items()):
        if not name.startswith(('rigid_','bs_','res_cc')):continue
        transform=sitk.ReadTransform(str(recovered/name))
        if name.startswith('rigid_'):points=[transform.TransformPoint(tuple(p)) for p in positions]
        else:points=[rigid.TransformPoint(transform.TransformPoint(tuple(p))) for p in positions]
        answer={'query_ids':q['query_ids'],'points_world_mm':np.array(points).tolist()};path=dest/(name+'.points.json')
        path.write_text(json.dumps(answer,indent=2)+'\n')
        rows.append({'transform':name,'transform_sha256':r['sha256'],'captured_object_path':r['object_path'],
                     'composition':'transform(source)' if name.startswith('rigid_') else 'rigid_-10(transform(source))',
                     'grade':score(answer,truth),'answer_path':str(path.relative_to(ROOT)),'answer_sha256':sha(path)})
    local_diagnostics=[]
    for script_name,base_name in [('/tmp/localopt.py','res_cc5_5.tfm'),('/tmp/localopt7.py','bs_corr_7.tfm')]:
        if script_name not in latest:continue
        script=(ROOT/latest[script_name]['object_path']).read_text()
        assert "[(-7,7)]*3" in script and f"'/tmp/{base_name}'" in script
        bs=sitk.ReadTransform(str(recovered/base_name));local_bounds=[]
        def warp(uv):
            p=s[:3,3]+s[:3,:2]@(np.array(uv)*np.array(g['spacing_xy_mm']))
            return np.array(rigid.TransformPoint(bs.TransformPoint(tuple(p))))
        for i,pixel in enumerate(q['pixels_uv']):
            pixel=np.array(pixel);p0=warp(pixel);pu=warp(pixel+[1,0])-warp(pixel-[1,0]);pv=warp(pixel+[0,1])-warp(pixel-[0,1])
            eu=pu/np.linalg.norm(pu);pv=pv-eu*(eu@pv);ev=pv/np.linalg.norm(pv);en=np.cross(eu,ev);en/=np.linalg.norm(en)
            b=np.stack([eu,ev,en],axis=1);assert np.allclose(b.T@b,np.eye(3),atol=1e-10)
            displacement=b.T@(np.array(truth['points_world_mm'][i])-p0)
            minimum=float(np.linalg.norm(displacement-np.clip(displacement,-7,7)))
            local_bounds.append({'query_id':q['query_ids'][i],'manual_displacement_in_local_axes_mm':displacement.tolist(),
                                 'distance_to_permitted_translation_cube_mm':minimum,'can_reach_5mm_tolerance':minimum<=5})
        local_diagnostics.append({'script':script_name,'code_evidence':latest[script_name],'base_transform':base_name,'query_bounds':local_bounds})
    receipt={'round':'BR-024','patient':3,'kind':'posthoc scoring of retained transform states, not randomized component ablations',
             'private_labels_used':'Scoring reconstructed point predictions only; no search or optimization performed.',
             'composition_evidence':latest['/tmp/show_bs.py'],'snapshot_receipts':snapshots,'rows':rows,
             'local_search_diagnostics':local_diagnostics,
             'limitations':['All captured final versions of named rigid/B-spline/neighborhood-correlation transforms are included.',
                            'Stage improvements are observational; strategy, metric, initialization and optimizer interactions are not separately isolated.',
                            'Transforms are reconstructed with preinstalled SimpleITK on the author host; this is evaluation, not a new model attempt.']}
    for p in [OUT/'stage-analysis.json',ROOT/'docs/evidence/br024-stage-analysis.json']:p.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps([{'transform':r['transform'],'grade':r['grade']} for r in rows],indent=2))

if __name__=='__main__':main()

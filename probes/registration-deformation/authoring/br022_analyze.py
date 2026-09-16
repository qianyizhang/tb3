"""Privileged offline diagnosis; this file is never an agent/solver input."""
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates,gaussian_filter
from scipy.optimize import differential_evolution
from score import score

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br022-registration-postmortem'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    truth=read(ROOT/'runs/br021-deformable/author/truth.json');y=np.array(truth['points_world_mm'])
    replay=read(OUT/'replay/points.json');original=read(ROOT/'runs/br021-deform-2d-terra-high-v1-20260916/deform-2d__YR5xbbH/artifacts/app/answer/points.json')
    stages=read(OUT/'replay/stages.json');stage_grades={}
    for stage in ['nominal','rigid','affine_only','direct_bspline','original_composition','final']:
        stage_grades[stage]=score({'query_ids':truth['query_ids'],'points_world_mm':[q[stage] for q in stages['queries']]},truth)
    counter=[];ablation=[]
    for folder,rows in [('counterfactuals',counter),('ablations',ablation)]:
        for file in sorted((OUT/folder).glob('*.json')):
            answer=read(file)
            if 'points_world_mm' not in answer:continue
            item={'name':file.stem,'path':str(file.relative_to(ROOT)),'sha256':sha(file),'grade':score(answer,truth)}
            if folder=='counterfactuals':
                item.update({key:answer[key] for key in ['composition','seed','bound_mm']})
                rows2=[]
                for i,d in enumerate(answer['diagnostics']):
                    centre=np.array(d['centre']);axes=np.array(d['axes'])
                    assert np.max(np.abs(axes.T@axes-np.eye(3)))<1e-8
                    z=axes.T@(y[i]-centre);clipped=np.clip(z,-answer['bound_mm'],answer['bound_mm'])
                    distance=float(np.linalg.norm(z-clipped))
                    rows2.append({'id':d['id'],'true_offset_local_mm':z.tolist(),'truth_in_box':bool(np.all(np.abs(z)<=answer['bound_mm'])),
                        'distance_to_box_mm':distance,'initial_error_mm':float(np.linalg.norm(y[i]-centre)),
                        'final_objective_score':d['objective_score']})
                item['search_geometry']=rows2
                item['box_best_possible_rms_mm']=float(np.sqrt(np.mean([d['distance_to_box_mm']**2 for d in rows2])))
                item['box_best_possible_max_mm']=max(d['distance_to_box_mm'] for d in rows2)
            rows.append(item)
    # Evaluate exactly the recorded original radius-8 objective at reference
    # centres. These label-assisted values are diagnostics, never solutions.
    data=ROOT/'runs/br021-deformable/tasks/deform-2d/environment/data'
    with np.load(data/'volume.npz') as d:V=d['hu'];iv=np.linalg.inv(d['voxel_to_world'])
    S=np.load(data/'view.npy');queries=read(data/'queries.json');j=read(data/'view.json');sx,sy=j['spacing_xy_mm']
    condition=read(OUT/'counterfactuals/original-b9-s17.json')
    author=read(OUT/'ablations/translation-multiscale.json')
    yy,xx=np.mgrid[-8:8+.01:.8,-8:8+.01:.8];diagnostics=[]
    for i,(pixel,d) in enumerate(zip(queries['pixels_uv'],condition['diagnostics'])):
        px,py=pixel;axes=np.array(d['axes']);e1,e2=axes[:,0],axes[:,1]
        src=map_coordinates(S,np.vstack([(py+yy/sy).ravel(),(px+xx/sx).ravel()]),order=1,mode='nearest').reshape(xx.shape)
        hs=src-gaussian_filter(src,1.6)
        def objective(point):
            world=np.array(point)[:,None]+e1[:,None]*xx.ravel()+e2[:,None]*yy.ravel()
            ij=np.einsum('ij,jn->in',iv,np.vstack([world,np.ones(world.shape[1])]))[:3]
            tar=map_coordinates(V,ij,order=1,cval=-1024).reshape(xx.shape);ht=tar-gaussian_filter(tar,1.6)
            return float(.4*np.corrcoef(src.ravel(),tar.ravel())[0,1]+.6*np.corrcoef(hs.ravel(),ht.ravel())[0,1])
        actual=np.array(original['points_world_mm'][i]);centre=np.array(d['centre'])
        measured=objective(actual);assert abs(measured-d['objective_score'])<1e-6
        # Bounded sphere radius 3 mm, fixed seed 17; best found is not a proof
        # of a global maximum. Privileged reference-neighbourhood diagnostic.
        def near(z):return y[i]+z[0]*np.array([np.cos(z[1])*np.cos(z[2]),np.sin(z[1])*np.cos(z[2]),np.sin(z[2])])
        fit=differential_evolution(lambda z:-objective(near(z)),[(0,3),(0,2*np.pi),(-np.pi/2,np.pi/2)],seed=17,popsize=12,maxiter=40,tol=.001,polish=True)
        offsets=np.linspace(0,1,101);curve=[objective(y[i]+t*(actual-y[i])) for t in offsets]
        diagnostics.append({'id':queries['query_ids'][i],'score_at_manual_target':objective(y[i]),'score_at_submitted_point':measured,
            'score_at_passing_author_point_with_agent_axes':objective(author['points_world_mm'][i]),
            'best_found_score_within_3mm_of_manual':float(-fit.fun),'reference_neighbourhood_best_error_mm':float(np.linalg.norm(near(fit.x)-y[i])),
            'reference_neighbourhood_seeds':[17],'curve_reference_to_submission':curve,
            'curve_fractions':offsets.tolist(),'error_mm':float(np.linalg.norm(actual-y[i]))})
    result={'round':'BR-022','plan_sha256':sha(OUT/'plan.json'),'recovery':read(OUT/'recovery.json'),
        'replay':{'maximum_coordinate_drift_mm':float(np.max(np.linalg.norm(np.array(replay['points_world_mm'])-original['points_world_mm'],axis=1))),
                  'stages':stage_grades,'original_trial_image_removed_by_harness':True,
                  'replay_image':'sha256:eba0354cc009141864421730b5f60c78d74c3acfbc6edc099991c6155e82138b',
                  'environment_note':'Retained author image built from identical frozen public Dockerfile and pinned packages; original trial image no longer exists. Replay matches submitted coordinates within numerical rounding.'},
        'counterfactuals':counter,'author_baseline_ablations':ablation,'objective_diagnostics':diagnostics,
        'limitations':['All solver interventions use this selected case; not held-out method estimates.',
            'Reference-neighbourhood objective search is privileged, fixed-seed and finite; it does not prove a global optimum.',
            'Widening translation bounds at fixed optimizer budget does not give exhaustive search.',
            'The context/motion factorial uses the author pipeline; it is not a one-line repair of the agent pipeline.',
            'Fresh autonomous replications are separately recorded from these author-run interventions.']}
    for path in [OUT/'solver-analysis.json',ROOT/'docs/evidence/br022-solver-analysis.json']:
        path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'replay_drift_mm':result['replay']['maximum_coordinate_drift_mm'],
        'original_search_bounds':next(x for x in counter if x['name']=='original-b9-s17')['search_geometry'],
        'objective_diagnostics':[{k:v for k,v in q.items() if not k.startswith('curve')} for q in diagnostics]},indent=2))


if __name__=='__main__':main()

"""Offline label-assisted diagnostics; never used to initialize the public solvers."""
import json
from pathlib import Path
import numpy as np
from collect import read,sha

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runs/br024-harder-registration'

def main():
    folder=OUT/'candidates/patient2-view1';truth=read(folder/'truth.json');y=np.array(truth['points_world_mm'])
    q=read(folder/'public/queries.json');g=read(folder/'public/view.json');s=np.array(g['slice_to_world'])
    nominal=s[:3,3]+np.array(q['pixels_uv'])*np.array(g['spacing_xy_mm'])@s[:3,:2].T
    logs=read(folder/'baseline/points.log.json');near=read(folder/'neighborhood/neighborhood.log.json')
    i=q['query_ids'].index('q02');query=logs['queries'][i];n=near['queries'][i]
    boundary=next(r for r in read(OUT/'neighborhood-feasibility.json')['rows'] if r['name']=='patient2-view2')
    data={'round':'BR-024','kind':'posthoc author diagnostics, not another solver or model attempt',
          'private_labels_used':'Only to compute geometric coverage and errors after fixed public-input execution.',
          'patient2_view1':{'all_manual_targets_inside_initial_axis_aligned_35mm_search_box':bool(np.all(np.abs(y-nominal)<=35)),
             'max_abs_world_displacement_mm':float(np.abs(y-nominal).max()),
             'q02_stages':[{'half_width_mm':r['half_width_mm'],'loss':r['loss'],'error_mm':float(np.linalg.norm(np.array(r['point'])-y[i]))} for r in query['stages']],
             'q02_neighborhood_nodes':n['nodes'],'q02_baseline_neighborhood_distance_mm':n['baseline_prediction_distance_mm'],
             'q02_neighborhood_prediction_error_mm':float(np.linalg.norm(np.array(n['prediction'])-y[i])),
             'q02_action':n['action'],
             'interpretation':'The broad initial box contains the manual match, but the first local fit is already wrong. Neighborhood agreement does not reject it: surrounding estimates support nearly the same wrong location. This is evidence against treating smooth displacement agreement as sufficient correspondence validation.'},
          'patient2_view2':{'final_author_grade':boundary['grade'],'max_threshold_excess_mm':boundary['grade']['max_mm']-5,
             'interpretation':'Near pass, but held under the unchanged exact admission gate. This tiny margin does not establish substantive anatomical difficulty or unsolvability.'},
          'receipts':{str(p.relative_to(ROOT)):sha(p) for p in [OUT/'feasibility.json',OUT/'translation-feasibility.json',OUT/'neighborhood-feasibility.json',OUT/'neighborhood-plan.json',folder/'baseline/points.log.json',folder/'neighborhood/neighborhood.log.json']}}
    for p in [OUT/'curation-analysis.json',ROOT/'docs/evidence/br024-curation-analysis.json']:p.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))

if __name__=='__main__':main()

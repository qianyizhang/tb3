"""Private evaluation of a previously frozen tissue fit; retains first screen."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from analyze import analyze_model, summarize


def main():
    p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True)
    p.add_argument('--prediction',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    receipt=json.loads((a.prediction.parent/'receipt.json').read_text())
    assert receipt['prediction_sha256']==hashlib.sha256(a.prediction.read_bytes()).hexdigest()
    pred=np.load(a.prediction)['points'];ref=dict(np.load(a.reference/'healthy_reference.npz'))
    old=json.loads((a.reference/'results.json').read_text())['models']['healthy_reference']
    stats,eng,w=analyze_model(pred,ref['tetra'],ref['cell_labels'],ref['directions'],a.output,'tissue_fit')
    valid=(ref['cell_labels']>0)&np.all(np.linalg.norm(ref['directions'],axis=-1)>.99,axis=0)
    error=100*np.average(abs(eng[:,valid]-ref['engineering'][:,valid]),axis=1,weights=w[valid]).mean(0)
    peak=np.mean(abs(np.array(stats['regional_peak_percent'])-np.array(old['regional_peak_percent'])),axis=0)
    timing=np.mean(abs(np.array(stats['regional_peak_frames_1based'])-np.array(old['regional_peak_frames_1based'])),axis=0)
    motion=np.linalg.norm(pred-ref['points'],axis=-1)
    stats['comparison']=dict(material_point_rmse_mm=float(np.sqrt(np.mean(motion**2))),material_displacement_error_mm=summarize(motion),
        directional_engineering_mae_pp=error.tolist(),regional_peak_mae_pp=peak.tolist(),regional_peak_timing_mae_frames=timing.tolist(),
        tissue_volume_curve_relative_error_percent=float(100*np.mean(abs(np.array(stats['tissue_volume_ml'])/old['tissue_volume_ml']-1))))
    stats['gates']=dict(motion=stats['comparison']['material_point_rmse_mm']<=2,strain=bool(np.all(error<=5)),
                       regional_peak=bool(np.all(peak<=5)),inversions=stats['inverted_tetrahedron_frames']==0)
    stats['pass']=all(stats['gates'].values()) and receipt['all_cg_converged']
    stats['description']='Four-video tissue fit — smoothness and finite-volume regularization; kinematic, not a force-balance simulation'
    result=dict(kind='development_informed_author_tissue_fit_evaluation',model=stats,receipt=receipt,
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (a.output/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(comparison=stats['comparison'],gates=stats['gates'],pass_all=stats['pass']),indent=2))


if __name__=='__main__':main()

"""Separate data-only verifier for the annotation-backed repair pilot."""
import json
from pathlib import Path
import nibabel as nib
import numpy as np
from scipy import ndimage as ndi

CONN = np.ones((3, 3, 3), dtype=bool)
LIMITS = dict(affine_tolerance=1e-5, centerline_tolerance_mm=.45,
              centerline_coverage=.95, branch_recall=.80,
              local_dice=.75, local_recall=.75, collateral_mm3=2.0,
              far_added_mm3=1.0, surface_tolerance_mm=.6)

def connected_in_region(pred, corridor, anchors, spacing):
    components,_=ndi.label(pred & corridor,structure=CONN)
    end_components=[]
    for v in anchors:
        radius=np.ceil(.6/spacing).astype(int)
        lo=np.maximum(0,v-radius);hi=np.minimum(pred.shape,v+radius+1)
        slices=tuple(slice(int(a),int(b)) for a,b in zip(lo,hi))
        indices=np.indices(tuple(hi-lo)).transpose(1,2,3,0)+lo
        ball=np.linalg.norm((indices-v)*spacing,axis=-1)<=.6
        end_components.append(set(np.unique(components[slices][ball]))-{0})
    return bool(end_components[0]&end_components[1])

def score_array(pred, affine, truth):
    try:
        gt = truth['gt'].astype(bool)
        assert pred.shape == gt.shape, 'mask shape differs'
        assert np.isfinite(pred).all(), 'nonfinite mask'
        assert np.isin(pred, [0, 1]).all(), 'binary values 0 and 1 required'
        assert np.allclose(affine, truth['affine'], atol=LIMITS['affine_tolerance'], rtol=0), 'affine differs'
        p = pred.astype(bool)
        spacing = truth['spacing']; voxel_mm3 = float(np.prod(spacing))
        editable = truth['editable'].astype(bool)
        original = truth['original'].astype(bool)
        repair = truth['repair_zone'].astype(bool)
        out = {'outside_edit_changed_voxels': int(np.count_nonzero((p != original) & ~editable))}
        out['collateral_deleted_mm3'] = float(np.count_nonzero(gt & ~p & ~repair)*voxel_mm3)
        out['collateral_added_mm3'] = float(np.count_nonzero(p & ~gt & ~repair)*voxel_mm3)
        checks = {'outside_edit_preserved':out['outside_edit_changed_voxels']==0,
                  'collateral_deleted':out['collateral_deleted_mm3']<=LIMITS['collateral_mm3'],
                  'collateral_added':out['collateral_added_mm3']<=LIMITS['collateral_mm3']}
        dist_to_gt = ndi.distance_transform_edt(~gt, sampling=spacing)
        out['far_added_mm3'] = float(np.count_nonzero(p & (dist_to_gt>LIMITS['surface_tolerance_mm']))*voxel_mm3)
        checks['no_remote_foreground'] = out['far_added_mm3']<=LIMITS['far_added_mm3']
        if repair.any():
            tp = np.count_nonzero(gt & p & repair)
            gvol = np.count_nonzero(gt & repair); pvol = np.count_nonzero(p & repair)
            out['local_dice'] = 2*tp/max(gvol+pvol,1)
            out['local_recall'] = tp/max(gvol,1)
            checks['local_dice'] = out['local_dice']>=LIMITS['local_dice']
            checks['local_recall'] = out['local_recall']>=LIMITS['local_recall']
        dist_to_p = ndi.distance_transform_edt(~p, sampling=spacing) if p.any() else np.full(gt.shape,np.inf)
        branches = []
        for i in range(int(truth['branch_count'])):
            ref = truth[f'branch_{i}'].astype(bool)
            path = truth[f'path_{i}'].astype(int)
            corridor = truth[f'corridor_{i}'].astype(bool)
            anchors = truth[f'anchors_{i}'].astype(int)
            lengths=np.linalg.norm(np.diff(path,axis=0)*spacing,axis=1)
            weights=np.zeros(len(path));weights[:-1]+=lengths/2;weights[1:]+=lengths/2
            hit=dist_to_p[tuple(path.T)]<=LIMITS['centerline_tolerance_mm']
            coverage = float(np.sum(weights[hit])/np.sum(weights))
            recall = float(np.count_nonzero(p & ref)/np.count_nonzero(ref))
            branch = {'label':int(truth[f'label_{i}']), 'local_connection':connected_in_region(p,corridor,anchors,spacing),
                      'centerline_length_mm':float(np.sum(lengths)),
                      'centerline_coverage':coverage, 'branch_recall':recall}
            branches.append(branch)
            checks[f'branch_{i}_connection'] = branch['local_connection']
            checks[f'branch_{i}_centerline'] = coverage>=LIMITS['centerline_coverage']
            checks[f'branch_{i}_recall'] = recall>=LIMITS['branch_recall']
        out['branches'] = branches
        absent=[]
        for i in range(int(truth['absent_count'])):
            connected=connected_in_region(p,truth[f'absent_corridor_{i}'],truth[f'absent_anchors_{i}'],spacing)
            absent.append({'label':int(truth[f'absent_label_{i}']),'unsupported_local_connection':connected})
            checks[f'absent_{i}_preserved']=not connected
        out['absent_branches']=absent
        out['whole_mask_dice_diagnostic'] = float(2*np.count_nonzero(p & gt)/max(np.count_nonzero(p)+np.count_nonzero(gt),1))
        out['checks'] = checks; out['reward'] = int(all(checks.values()))
        return out
    except (AssertionError, ValueError, TypeError, KeyError) as exc:
        return {'reward':0,'reason':str(exc)}

def score_file(path, truth):
    try:
        img=nib.load(path)
        return score_array(np.asarray(img.dataobj),img.affine,truth)
    except Exception as exc:
        return {'reward':0,'reason':type(exc).__name__+': '+str(exc)}

if __name__=='__main__':
    with np.load('/verifier/truth.npz',allow_pickle=False) as z:
        truth={k:z[k] for k in z.files}
    result=score_file('/app/answer/corrected_mask.nii.gz',truth)
    dest=Path('/logs/verifier');dest.mkdir(parents=True,exist_ok=True)
    (dest/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    (dest/'reward.txt').write_text(str(result['reward'])+'\n')
    print(json.dumps(result))

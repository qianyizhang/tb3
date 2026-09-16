"""Test a nearest-point bridge before claiming anatomical difficulty.

Selection uses a reviewed discrepancy; the repair and route use prediction
geometry only. The reference is opened afterward for independent measurement.
"""
from pathlib import Path
import hashlib, json, sys
import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.graph import MCP_Geometric

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'runs/br033-brain-routing'
DATA = BASE / 'sources/TopBrain_Data_Release_Batches1n2nTA36_081726'
sys.path.insert(0, str(ROOT / 'probes/vessel-geometry/authoring'))
from geometry import transform, resample_path, frames, cpr_coordinates, sample, mesh_from_mask


def route(mask, spacing, start, end):
    rad = ndi.distance_transform_edt(mask, sampling=spacing)
    cost = np.full(mask.shape, np.inf, np.float32)
    cost[mask] = 1 / (.25 + rad[mask])
    m = MCP_Geometric(cost, sampling=tuple(spacing))
    ds, _ = m.find_costs([tuple(start)], [tuple(end)])
    assert np.isfinite(ds[tuple(end)])
    return np.asarray(m.traceback(tuple(end)))


def main():
    out = BASE / 'gap-calibration'
    assert not out.exists(), 'Preserve existing calibration'
    out.mkdir()
    predpath = BASE / 'predictions-resencm-v1/topcow_mr_004.nii.gz'
    ni = nib.load(predpath)
    pred = np.asarray(ni.dataobj, dtype=np.uint8)
    spacing = nib.affines.voxel_sizes(ni.affine)
    positions = np.argwhere(np.isin(pred, [1,25]))
    halo = np.ceil(6. / spacing).astype(int)
    lo, hi = np.maximum(positions.min(0)-halo, 0), np.minimum(positions.max(0)+halo+1, pred.shape)
    sl = tuple(slice(int(a),int(b)) for a,b in zip(lo,hi))
    original = pred[sl].copy()
    aff = ni.affine.copy(); aff[:3,3] = transform(lo, ni.affine)
    cc, count = ndi.label(original==25, np.ones((3,3,3)))
    sizes = np.bincount(cc.ravel()); sizes[0] = 0
    assert count == 2
    main_id = int(sizes.argmax()); frag_id = 3-main_id
    dist, indexes = ndi.distance_transform_edt(cc!=main_id, sampling=spacing, return_indices=True)
    points = np.argwhere(cc==frag_id)
    p = points[np.argmin(dist[tuple(points.T)])]; q = indexes[:,*p]
    # Round on the original image lattice: half-voxel ties must not change
    # when the display/export crop's origin moves by an odd voxel count.
    bridge = np.unique(np.rint(np.linspace(p+lo,q+lo,4*int(np.max(abs(p-q)))+1)).astype(int),axis=0)-lo
    assert np.all(np.isin(original[tuple(bridge.T)],[0,25]))
    fixed = original.copy(); fixed[tuple(bridge.T)] = 25
    parent_points = np.argwhere(original==1)
    rad = ndi.distance_transform_edt(original==1,sampling=spacing)
    limits = np.percentile(parent_points[:,2],[20,35])
    pool = parent_points[(parent_points[:,2]>=limits[0]) & (parent_points[:,2]<=limits[1])]
    start = pool[np.argmax(rad[tuple(pool.T)])]
    far = np.linalg.norm((points-p)*spacing,axis=1)
    pool = points[far>=np.percentile(far,75)]
    rad = ndi.distance_transform_edt(cc==frag_id,sampling=spacing)
    end = pool[np.argmax(rad[tuple(pool.T)])]
    before, _ = ndi.label(np.isin(original,[1,25]),np.ones((3,3,3)))
    after, _ = ndi.label(np.isin(fixed,[1,25]),np.ones((3,3,3)))
    assert before[tuple(start)] != before[tuple(end)]
    assert after[tuple(start)] == after[tuple(end)] != 0
    path = route(np.isin(fixed,[1,25]),spacing,start,end)
    line, _ = resample_path(transform(path,aff),.25,.3)
    arc = np.r_[0.,np.cumsum(np.linalg.norm(np.diff(line,axis=0),axis=1))]
    _,normal,binormal = frames(line)
    angles = np.arange(0,360,45.)
    offsets = np.arange(-5,5.001,.2)
    xyz = cpr_coordinates(line,normal,binormal,angles,offsets)
    image = np.asarray(nib.load(DATA/'imagesTr_topbrain/topcow_mr_004_0000.nii.gz').dataobj)[sl]
    coordinates = transform(xyz,np.linalg.inv(aff))
    assert np.all(coordinates>=0) and np.all(coordinates<=np.array(image.shape)-1), 'CPR must sample source pixels, not crop padding'
    np.save(out/'centerline.npy',line)
    np.savez_compressed(out/'cpr.npz',intensity=sample(image,aff,xyz,1,0),source_ras_mm=xyz,
        angles_deg=angles,offsets_mm=offsets,arc_mm=arc)
    whole = pred.copy(); whole[sl] = fixed
    nib.save(nib.Nifti1Image(whole,ni.affine),out/'corrected_labels.nii.gz')
    for name,a in [('image',image),('original_labels',original),('corrected_crop_labels',fixed)]:
        nib.save(nib.Nifti1Image(a,aff),out/f'{name}.nii.gz')
    mesh = mesh_from_mask(np.isin(fixed,[1,25]),aff)
    mesh.export(out/'basilar-right-sca.ply')
    # Reference enters only after repair and exports are fixed.
    refpath = DATA/'labelsTr_topbrain_v2_topaneu36class/topcow_mr_004.nii.gz'
    ref = np.asarray(nib.load(refpath).dataobj)[sl]
    changed = fixed != original
    refpath_ijk = route(np.isin(ref,[1,25]),spacing,start,end)
    reference_line,_ = resample_path(transform(refpath_ijk,aff),.25,.3)
    np.save(out/'reference_centerline.npy',reference_line)
    error = cKDTree(reference_line).query(line)[0]
    metrics = {'case':'004','target':'R-SCA','parent':'BA','author_baseline':True,'coding_agent_trial':False,
        'export_version':3,'image_halo_mm':6,'all_cpr_samples_inside_source_crop':True,
        'repair_uses_image':False,'repair_uses_reference':False,'selection_uses_reference':True,
        'nearest_center_distance_mm':float(dist[tuple(p)]),'voxels_added':int(changed.sum()),
        'voxels_removed':0,'added_reference_labels':dict(zip(*[x.tolist() for x in np.unique(ref[changed],return_counts=True)])),
        'parent_to_target_connected_before':False,'parent_to_target_connected_after':True,
        'source_native_bridge_ijk':(bridge+lo).tolist(),'anchors_native_ijk':(np.array([start,end])+lo).tolist(),
        'crop_lo':lo.tolist(),'crop_hi':hi.tolist(),'route_length_mm':float(arc[-1]),
        'route_to_reference_p95_mm':float(np.percentile(error,95)), 'route_to_reference_max_mm':float(error.max()),
        'mesh_watertight':bool(mesh.is_watertight),'mesh_components':len(mesh.split(only_watertight=False)),
        'source_prediction_sha256':hashlib.sha256(predpath.read_bytes()).hexdigest(),
        'reference_sha256':hashlib.sha256(refpath.read_bytes()).hexdigest(),
        'disposition':'Geometry-only connectivity calibration; not admitted as evidence of difficult anatomical reasoning.',
        'scope':'Repairs only this named parent-to-target route. No claim that the entire brain segmentation is corrected.'}
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print(json.dumps(metrics,indent=2))


if __name__=='__main__':
    main()

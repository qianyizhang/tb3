"""Audit source mechanics; score frozen video fit; build reference/control models."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import meshio
import numpy as np

from mechanics import (edge_matrices, deformation_gradient, strain, boundary,
                       rigid_fit, cell_directions, nodal_average, calculation_tests)


def summarize(v):
    return dict(min=float(np.min(v)), median=float(np.median(v)), p05=float(np.quantile(v,.05)),
                p95=float(np.quantile(v,.95)), max=float(np.max(v)), mean=float(np.mean(v)))


def load_sequence(root, canonical):
    files = sorted((root/'mesh').glob('usmesh*.vtk'))
    assert len(files) == 30
    first = meshio.read(files[0])
    cells = first.cells_dict['tetra']
    assert np.array_equal(cells, canonical.cells_dict['tetra'])
    R, offset, error = rigid_fit(canonical.points.astype(float), first.points.astype(float))
    assert error.max() < .01
    points = []
    for f in files:
        m = meshio.read(f)
        assert np.array_equal(m.cells_dict['tetra'], cells)
        points.append(np.einsum('nj,kj->nk', m.points.astype(float)-offset, R))
    return np.array(points), dict(pose_fit_mm=summarize(error), fixed_topology=True,
                                 rigid_rotation_rows=R.tolist(), offset=offset.tolist())


def analyze_model(points, cells, labels, directions, out, name):
    reference = points[0]
    D = edge_matrices(reference, cells)
    invD = np.linalg.inv(D)
    weights = np.linalg.det(D)/6
    assert np.all(weights > 0)
    valid = (labels > 0) & np.all(np.linalg.norm(directions,axis=-1) > .99,axis=0)
    engs, greens, jacobians, globals_, regions, regions_gl, node_fields = [], [], [], [], [], [], []
    tissue = []
    for x in points:
        F = np.einsum('nij,njk->nik', edge_matrices(x,cells),invD)
        eng, green, J = strain(F, directions)
        assert np.isfinite(F).all() and np.isfinite(eng).all() and np.isfinite(J).all()
        eng[~valid] = np.nan; green[~valid] = np.nan
        engs.append(eng); greens.append(green); jacobians.append(J)
        globals_.append(np.average(eng[valid],axis=0,weights=weights[valid]))
        regions.append([np.average(eng[(labels == s)&valid],axis=0,weights=weights[(labels == s)&valid]) for s in range(1,18)])
        regions_gl.append([np.average(green[(labels == s)&valid],axis=0,weights=weights[(labels == s)&valid]) for s in range(1,18)])
        tissue.append(np.sum(weights*J)/1000)
        nodal_eng = nodal_average(np.nan_to_num(eng), cells, weights*valid, len(x))
        nodal_gl = nodal_average(np.nan_to_num(green), cells, weights*valid, len(x))
        nodal_J = nodal_average(J, cells, weights, len(x))
        node_fields.append(np.c_[nodal_eng, nodal_gl, nodal_J])
    engs, greens, jacobians = np.array(engs), np.array(greens), np.array(jacobians)
    node_fields = np.array(node_fields)
    assert np.nanmax(abs(engs[0])) < 1e-10, 'Reference-frame strain must vanish on supported directions'
    # Tensor fields remain exactly reproducible from points/tetra/reference with mechanics.py.
    np.savez_compressed(out/f'{name}.npz', points=points, tetra=cells,
                        engineering=engs.astype('float32'), green_lagrange_directional=greens.astype('float32'),
                        jacobian=jacobians.astype('float32'), nodal_fields=node_fields.astype('float32'),
                        cell_labels=labels, directions=directions)
    regions = np.array(regions); globals_ = np.array(globals_)
    peaks = np.stack([regions[:,:,0].min(0), regions[:,:,1].min(0), regions[:,:,2].max(0)],axis=1)
    peak_frames = np.stack([regions[:,:,0].argmin(0),regions[:,:,1].argmin(0),regions[:,:,2].argmax(0)],axis=1)+1
    stats = dict(tissue_volume_ml=tissue, tissue_volume_change_percent=(100*(np.array(tissue)/tissue[0]-1)).tolist(),
                 jacobian=summarize(jacobians), inverted_tetrahedron_frames=int(np.sum(jacobians<=0)),
                 reference_frame_strain_max_abs=float(np.nanmax(np.abs(engs[0]))),
                 positive_label_cells_without_directional_basis=int(np.sum((labels>0)&~valid)),
                 lv_volume_with_complete_directional_basis_fraction=float(weights[valid].sum()/weights[labels>0].sum()),
                 global_engineering_percent=(100*globals_).tolist(),
                 regional_engineering_percent=(100*regions).tolist(),
                 regional_green_lagrange_percent=(100*np.array(regions_gl)).tolist(),
                 regional_peak_percent=(100*peaks).tolist(),regional_peak_frames_1based=peak_frames.tolist(),
                 strain_directional_distributions_percent=[summarize(100*engs[:,valid,i]) for i in range(3)],
                 cycle_endpoint_material_displacement_mm=summarize(np.linalg.norm(points[-1]-points[0],axis=1)))
    return stats, engs, weights


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--public', type=Path, required=True)
    p.add_argument('--prediction', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    start = time.perf_counter()
    receipt = json.loads((a.prediction.parent/'receipt.json').read_text())
    assert hashlib.sha256(a.prediction.read_bytes()).hexdigest() == receipt['prediction_sha256']
    predicted = np.load(a.prediction)['points']
    # Source inspection and scoring happen only after the video prediction is frozen.
    canonical = meshio.read(a.source/'RefMeshP1.vtk')
    cells = canonical.cells_dict['tetra']
    labels = canonical.cell_data['AHA'][0].astype(int)
    directions = cell_directions(canonical.point_data,cells)
    healthy, haudit = load_sequence(a.source/'patient01_healthy',canonical)
    lbbb, laudit = load_sequence(a.source/'patient04_lbbb',canonical)
    init = np.load(a.public/'initial_mesh.npz')
    assert np.max(abs(init['points']-healthy[0])) < 1e-9
    X=healthy[0]; center=X.mean(0); xc=X-center
    uniform, affine = [], []
    for y in healthy:
        yc=y-y.mean(0)
        scale=np.sum(xc*yc)/np.sum(xc*xc)
        uniform.append(xc*scale+y.mean(0))
        A=np.linalg.lstsq(np.c_[X,np.ones(len(X))],y,rcond=None)[0]
        affine.append(np.einsum('ni,ij->nj',np.c_[X,np.ones(len(X))],A))
    models=dict(healthy_reference=healthy,lbbb_reference=lbbb,video_affine=predicted,
                affine_control=np.array(affine),uniform_control=np.array(uniform),static=np.repeat(X[None],30,axis=0))
    descriptions={
        'healthy_reference':'STRAUS healthy simulation — reference motion',
        'lbbb_reference':'STRAUS LBBB simulation — reference motion, not inferred diagnosis',
        'video_affine':'Reconstructed from four videos and the initial mesh — global affine baseline',
        'affine_control':'Privileged affine fit to reference material points — representation control',
        'uniform_control':'Privileged uniform scaling fit to reference material points — balloon control',
        'static':'Initial myocardial body held static — negative control'}
    results, refstrain, refweights = {},None,None
    for name, points in models.items():
        stats, eng, weights = analyze_model(points,cells,labels,directions,a.output,name)
        stats['description']=descriptions[name]
        if name=='healthy_reference':
            refstrain,refweights=eng,weights
        elif name!='lbbb_reference':
            valid=(labels>0)&np.all(np.linalg.norm(directions,axis=-1)>.99,axis=0)
            errors=100*np.average(abs(eng[:,valid]-refstrain[:,valid]),axis=1,weights=refweights[valid]).mean(0)
            motion=np.linalg.norm(points-healthy,axis=-1)
            peakerr=np.mean(abs(np.array(stats['regional_peak_percent'])-np.array(results['healthy_reference']['regional_peak_percent'])),axis=0)
            phaseerr=np.mean(abs(np.array(stats['regional_peak_frames_1based'])-np.array(results['healthy_reference']['regional_peak_frames_1based'])),axis=0)
            stats['comparison']=dict(material_point_rmse_mm=float(np.sqrt(np.mean(motion**2))),material_displacement_error_mm=summarize(motion),
                directional_engineering_mae_pp=errors.tolist(),regional_peak_mae_pp=peakerr.tolist(),regional_peak_timing_mae_frames=phaseerr.tolist(),
                tissue_volume_curve_relative_error_percent=float(100*np.mean(abs(np.array(stats['tissue_volume_ml'])/results['healthy_reference']['tissue_volume_ml']-1))))
            c=stats['comparison']
            stats['gates']=dict(motion=c['material_point_rmse_mm']<=2, strain=bool(np.all(errors<=5)),
                                regional_peak=bool(np.all(peakerr<=5)),inversions=stats['inverted_tetrahedron_frames']==0)
            stats['pass']=all(stats['gates'].values())
        results[name]=stats
        print(name,'J',stats['jacobian']['min'],stats['jacobian']['max'],stats.get('comparison',{}),flush=True)
    audit=dict(kind='author_mechanics_development_not_blind_agent_trial',source='Multimodality STRAUS',
               source_url='https://humanheart-project.creatis.insa-lyon.fr/multimodalityStraus.html',
               source_patients=['patient01_healthy','patient04_lbbb'],frames=30,vertices=len(X),tetrahedra=len(cells),
               healthy_audit=haudit,lbbb_audit=laudit,analytic_checks=calculation_tests(),
               directional_basis='Source LV axes averaged into tetrahedra and orthonormalized in the reference frame; AHA 0 unavailable',
               strain_definitions={'engineering':'sqrt(e^T F^T F e)-1','green_lagrange':'e^T (F^T F-I)/2 e','jacobian':'det(F)'},
               direction_order=['longitudinal','circumferential','radial'],frame_timing_seconds=None,
               reference='First frame, not asserted to be a clinically adjudicated ED frame',
               physical_scope='Kinematic material deformation, not a newly solved force-balanced electromechanical model',
               chamber_volume_status='No audited LV/RV endocardial and valve-plane partition; EF/flow withheld for this source',
               video_receipt=receipt,models=results,
               script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),elapsed_seconds=time.perf_counter()-start)
    (a.output/'results.json').write_text(json.dumps(audit,indent=2)+'\n')
    faces,owners=boundary(cells)
    np.savez_compressed(a.output/'geometry.npz',points=X,tetra=cells,boundary=faces,boundary_owners=owners,
                        point_labels=canonical.point_data['AHA'].astype('int16'),cell_labels=labels,directions=directions)
    print('Completed in',audit['elapsed_seconds'],'seconds')


if __name__=='__main__':
    main()

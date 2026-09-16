"""Export an inspectable material model including full F and E tensor fields."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from mechanics import edge_matrices, boundary


def main():
    p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    assert not a.output.exists()
    m=dict(np.load(a.model));X=m['points'];cells=m['tetra'];inverse=np.linalg.inv(edge_matrices(X[0],cells))
    gradients=np.array([np.einsum('nij,njk->nik',edge_matrices(x,cells),inverse) for x in X])
    E=.5*(np.einsum('tnji,tnjk->tnik',gradients,gradients)-np.eye(3))
    assert np.max(abs(E[0]))<1e-10 and np.linalg.det(gradients).min()>0
    metadata=dict(kind='author_video_fitted_material_model',coordinates='mm, canonical source anatomical frame',
                  units=dict(F='dimensionless',E='dimensionless',engineering='dimensionless',J='ratio'),
                  reference_frame_1based=1,frame_duration_seconds=None,
                  direction_order=['longitudinal','circumferential','radial'],
                  status='Development kinematic fit; does not pass all provisional accuracy targets; not a force-balanced electromechanical model',
                  source_model_sha256=hashlib.sha256(a.model.read_bytes()).hexdigest())
    np.savez_compressed(a.output,points_mm=X.astype('float32'),tetra=cells.astype('int32'),
        boundary_triangles=boundary(cells)[0].astype('int32'),F=gradients.astype('float32'),
        E_green_lagrange=E.astype('float32'),engineering_strain=m['engineering'],J=m['jacobian'],
        cell_labels=m['cell_labels'],reference_directions=m['directions'].astype('float32'),
        metadata_json=np.array(json.dumps(metadata)))
    (a.output.with_suffix('.json')).write_text(json.dumps(dict(metadata=metadata,sha256=hashlib.sha256(a.output.read_bytes()).hexdigest(),bytes=a.output.stat().st_size),indent=2)+'\n')
    print(a.output.resolve(),a.output.stat().st_size)


if __name__=='__main__':main()

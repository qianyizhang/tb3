"""Extract four calibrated video planes and an initial material mesh.

Only frame 0 geometry determines the public planes/pose. Future source meshes
are never opened. Extracted video slices are real samples of synthetic US.
"""
import argparse
import hashlib
import json
from pathlib import Path

import meshio
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

from mechanics import rigid_fit, cell_directions


def mhd(path):
    fields = dict(line.split(' = ', 1) for line in path.read_text().splitlines() if ' = ' in line)
    assert fields['ElementType'] == 'MET_SHORT'
    assert fields['TransformMatrix'] == '1 0 0 0 1 0 0 0 1' and fields['Offset'] == '0 0 0'
    assert fields['BinaryDataByteOrderMSB'] == 'False'
    dims = np.array(fields['DimSize'].split(), int)
    spacing = np.array(fields['ElementSpacing'].split(), float)
    volume = np.fromfile(path.with_name(fields['ElementDataFile']), dtype='<i2').reshape(tuple(dims[::-1]))
    return volume, spacing


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--reference', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    ref = meshio.read(a.reference)
    first = meshio.read(a.source/'mesh/usmesh00.vtk')
    cells = first.cells_dict['tetra']
    assert np.array_equal(cells, ref.cells_dict['tetra'])
    R, offset, error = rigid_fit(ref.points.astype(float), first.points.astype(float))
    assert error.max() < .01
    X = np.einsum('nj,kj->nk', first.points-offset, R)
    labels = ref.cell_data['AHA'][0].astype('int16')
    point_labels = ref.point_data['AHA'].astype('int16')
    directions = cell_directions(ref.point_data, cells)
    np.savez_compressed(a.output/'initial_mesh.npz', points=X, tetra=cells, labels=labels,
                        point_labels=point_labels, directions=directions)
    center = X[point_labels > 0].mean(0)
    size, step = 192, .75
    uv = (np.arange(size)-(size-1)/2)*step
    vv, uu = np.meshgrid(uv, uv, indexing='ij')
    planes = []
    for angle in [0, 60, 120]:
        theta = np.deg2rad(angle)
        planes.append(dict(name=f'Long axis {angle} degrees', origin=center.tolist(),
                           u=[float(np.cos(theta)), float(np.sin(theta)), 0], v=[0, 0, -1]))
    origin = center.copy()
    origin[2] = np.quantile(X[point_labels > 0, 2], .6)
    planes.append(dict(name='Short axis', origin=origin.tolist(), u=[1, 0, 0], v=[0, 1, 0]))
    first_volume, spacing = mhd(a.source/'image/usfrm00.mhd')
    hi = float(np.percentile(first_volume[first_volume > 0], 99.5))
    sampling = []
    for i, plane in enumerate(planes):
        points = np.array(plane['origin']) + uu[..., None]*plane['u'] + vv[..., None]*plane['v']
        native = (np.einsum('...j,jk->...k', points, R)+offset)/spacing
        sampling.append(np.moveaxis(native[..., ::-1], -1, 0))
        (a.output/f'view_{i}').mkdir()
    for t in range(30):
        volume, sp = mhd(a.source/f'image/usfrm{t:02d}.mhd')
        assert np.array_equal(sp, spacing)
        for i, coords in enumerate(sampling):
            section = map_coordinates(volume.astype('float32'), coords, order=1, mode='constant', cval=0)
            image = np.clip(section/hi*255, 0, 255).astype('uint8')
            Image.fromarray(image).save(a.output/f'view_{i}/frame_{t+1:02d}.png')
    geo = dict(planes=planes, image_size=size, spacing_mm=step, frames=30,
               first_frame_1based=1, pixel_center=(size-1)/2, initial_center=center.tolist(),
               canonical_to_native_rotation_rows=R.tolist(), canonical_to_native_offset=offset.tolist(),
               pose_fit_max_error_mm=float(error.max()), source_spacing_mm=spacing.tolist(),
               physical_frame_duration_seconds=None, intensity_high_from_initial_volume=hi)
    (a.output/'geometry.json').write_text(json.dumps(geo, indent=2)+'\n')
    (a.output/'TASK.md').write_text('''Recover a deforming biventricular myocardial body from four calibrated ultrasound videos and the supplied initial tetrahedral mesh. Preserve material point correspondence and return 30 deformed point arrays on the fixed topology. Return directional engineering strain, Green-Lagrange strain tensors, regional AHA curves and tissue-volume/Jacobian checks, all relative to frame 1. AHA 0 has no supplied directional coordinate system. Report it as unavailable for directional strain. Scale and plane coordinates are in geometry.json. Frame duration is unknown: use cycle phase rather than invented seconds. Do not interpret myocardial tissue volume as cavity volume or EF. Explain assumptions and unsupported outputs.\n''')
    manifest = {str(f.relative_to(a.output)): hashlib.sha256(f.read_bytes()).hexdigest()
                for f in sorted(a.output.rglob('*')) if f.is_file()}
    (a.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('Prepared', len(manifest), 'public files; initial pose error', error.max(), 'mm')


if __name__ == '__main__':
    main()

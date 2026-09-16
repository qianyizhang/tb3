"""Prepare bounded public inputs. This author-only module reads source labels."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

TASK = """Recover a moving left ventricular cavity from four ultrasound videos.

The 30 frames sample one cardiac cycle. Views are calibrated radial sections
at 0, 45, 90 and 135 degrees. Geometry and pixel spacing are in geometry.json.
Only the masks in anchors/ are available as segmentation references. Their
frame numbers are anchors, not supplied clinical phase labels. Recover the
cavity in every frame from the videos, keeping a consistent closed mesh.

Return a mesh sequence with fixed connectivity (vertices in mm, triangular
faces), the 30 cavity volumes in mL, EF = 100*(max(V)-min(V))/max(V), and the
one-based frame references of those extrema. Document coordinate conventions
and any anatomical assumptions. Fixed vertex indices do not imply tissue
tracking. No flow or disease inference is required.

The development grader measures section Dice, boundary distance, volume curve
error and EF separately. Gates: mean withheld-section Dice >=0.90; mean
pairwise HD95 <=1.0 mm; mean absolute relative volume error <=10%; EF absolute
error <=5 percentage points; positive volumes and closed nondegenerate mesh.
The 3D/volume reference is derived from additional source annotations, not an
independent patient scan. These are research gates, not clinical tolerances.
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    views = [0, 9, 18, 27]
    mask = np.asarray(Image.open(a.source / 'mask/Patient001_slice001time002.png')) == 127
    cx = (mask.shape[1] - 1) / 2
    rows = np.where(mask[:, int(cx)])[0]
    cy = float((rows.min() + rows.max()) / 2)
    for name, anchors in [('one_anchor', [2]), ('two_anchors', [2, 17])]:
        out = a.output / name
        out.mkdir(parents=True, exist_ok=False)
        for v, source in enumerate(views):
            (out / f'video/view_{v:02d}').mkdir(parents=True)
            (out / f'anchors/view_{v:02d}').mkdir(parents=True)
            for t in range(1, 31):
                fn = f'Patient001_slice{source + 1:03d}time{t:03d}.png'
                shutil.copyfile(a.source / 'image' / fn, out / f'video/view_{v:02d}/frame_{t:03d}.png')
                if t in anchors:
                    binary = (np.asarray(Image.open(a.source / 'mask' / fn)) == 127).astype('uint8') * 255
                    Image.fromarray(binary).save(out / f'anchors/view_{v:02d}/frame_{t:03d}.png')
        geometry = dict(shape_hw=list(mask.shape), frame_count=30, anchor_frames_1based=anchors,
                        view_angles_degrees=[0, 45, 90, 135], rotation_axis_x_px=cx,
                        origin_y_px=cy, origin_basis='midpoint of anchor frame 2 cavity on view 0 rotation axis',
                        in_plane_spacing_mm=.089950, source_convention='radial planes of a STIC volume',
                        mesh_coordinates='x=r*sin(phi)*cos(theta), y=r*cos(phi), z=r*sin(phi)*sin(theta); image y increases down')
        (out / 'geometry.json').write_text(json.dumps(geometry, indent=2) + '\n')
        (out / 'TASK.md').write_text(TASK)
        manifest = {str(f.relative_to(out)): sha(f) for f in sorted(out.rglob('*')) if f.is_file()}
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        print(name, len(manifest), 'files; manifest', sha(out / 'manifest.json'))


if __name__ == '__main__':
    main()

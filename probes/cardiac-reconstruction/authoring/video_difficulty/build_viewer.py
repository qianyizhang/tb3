"""Standalone local review viewer. Contains references; never a solver input."""
import argparse
import base64
import io
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--evaluation', type=Path, required=True)
    a = p.parse_args()
    r = json.loads((a.evaluation / 'results.json').read_text())
    geo = r['geometry']
    data = dict(profiles={}, images={}, contours={}, stats=r['stats'],
                curves=json.loads((a.evaluation / 'curves.json').read_text()),
                cx=geo['rotation_axis_x_px'], cy=geo['origin_y_px'], spacing=geo['in_plane_spacing_mm'])
    paths = dict(one_control=a.run/'one-anchor-v1/control-mesh.npz', one_dis=a.run/'one-anchor-v1/dis-mesh.npz',
                 two_control=a.run/'two-anchors-v1/control-mesh.npz', two_dis=a.run/'two-anchors-v1/dis-mesh.npz',
                 one_refined=a.run/'one-anchor-refined-v1/refined-mesh.npz',
                 clean=a.evaluation/'clean-mesh.npz', dense=a.evaluation/'dense-mesh.npz')
    for name, path in paths.items():
        data['profiles'][name] = np.load(path)['radius_px'][:, ::2, ::2].round(2).tolist()
    for angle in [0, 35, 45, 90, 135]:
        images, contours = [], []
        for frame in range(1, 31):
            fn = f'Patient001_slice{angle//5+1:03d}time{frame:03d}.png'
            im = Image.open(a.source/'image'/fn).convert('L')
            im.thumbnail((360, 360))
            stream = io.BytesIO()
            im.save(stream, format='JPEG', quality=86)
            images.append('data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode())
            mask = (np.array(Image.open(a.source/'mask'/fn)) == 127).astype('uint8')
            cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours.append(max(cs, key=cv2.contourArea).reshape(-1, 2).tolist())
        data['images'][str(angle)], data['contours'][str(angle)] = images, contours
    template = Path(__file__).with_name('viewer.html').read_text()
    output = a.evaluation/'viewer.html'
    output.write_text(template.replace('__PILOT_DATA__', json.dumps(data, separators=(',', ':'))))
    print(output.resolve(), output.stat().st_size)


if __name__ == '__main__':
    main()

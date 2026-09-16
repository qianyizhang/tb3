"""Build a local standalone viewer from pilot outputs; no data leaves the machine."""
import argparse
import base64
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--pilot', type=Path, required=True)
    args = parser.parse_args()
    result = json.loads((args.pilot / 'results.json').read_text())
    data = {'profiles': {}, 'images': [], 'contours': [], 'stats': result['stats'],
            'curves': json.loads((args.pilot / 'curves.json').read_text()),
            'cx': result['input_geometry']['axis_x_px'],
            'cy': result['input_geometry']['origin_y_px_from_plane1_only'],
            'spacing': result['input_geometry']['in_plane_spacing_mm']}
    for name in ['one', 'two', 'four', 'eight', 'dense']:
        p = np.load(args.pilot / f'{name}-mesh.npz')['radius_px']
        data['profiles'][name] = p[:, ::2, ::2].round(2).tolist()
    for frame in range(1, 31):
        name = f'Patient001_slice008time{frame:03d}.png'
        im = Image.open(args.source / 'image' / name).convert('L')
        im.thumbnail((320, 320))
        stream = io.BytesIO()
        im.save(stream, format='JPEG', quality=83)
        data['images'].append('data:image/jpeg;base64,' + base64.b64encode(stream.getvalue()).decode())
        m = np.asarray(Image.open(args.source / 'mask' / name)) == 127
        rows = np.where(m.any(axis=1))[0]
        left = [[int(np.where(m[y])[0].min()), int(y)] for y in rows[::2]]
        right = [[int(np.where(m[y])[0].max()), int(y)] for y in rows[::-2]]
        data['contours'].append(left + right)
    template = Path(__file__).with_name('viewer.html').read_text()
    html = template.replace('__PILOT_DATA__', json.dumps(data, separators=(',', ':')))
    output = args.pilot / 'viewer.html'
    output.write_text(html)
    print(output.resolve(), output.stat().st_size)


if __name__ == '__main__':
    main()

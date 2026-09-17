"""Full-volume CT windowing in physical RAS coordinates with logged views."""
import argparse
import hashlib
import json
from pathlib import Path
import uuid

import nibabel as nib
import numpy as np
from PIL import Image, ImageDraw

# horizontal axis/sign, vertical axis/sign, normal, left/right/top/bottom
PLANES = {
    'axial': (0, -1, 1, -1, 2, 'R', 'L', 'A', 'P'),
    'coronal': (0, -1, 2, -1, 1, 'R', 'L', 'S', 'I'),
    'sagittal': (1, 1, 2, -1, 0, 'P', 'A', 'S', 'I'),
}


def transform(affine, points):
    return np.sum(np.asarray(points)[..., None, :] * affine[:3, :3], axis=-1) + affine[:3, 3]


def bounds(shape, affine):
    corners = np.array(np.meshgrid(*[(0, n - 1) for n in shape],
                                  indexing='ij')).reshape(3, -1).T
    points = transform(affine, corners)
    return points.min(0), points.max(0)


def sample(data, affine, points):
    ijk = np.rint(transform(np.linalg.inv(affine), points)).astype(int)
    valid = np.all((ijk >= 0) & (ijk < np.array(data.shape)), axis=-1)
    values = np.full(points.shape[:-1], -1024., dtype=np.float32)
    values[valid] = data[tuple(ijk[valid].T)]
    return values


def window(values, level, width):
    if not np.isfinite([level, width]).all() or width <= 0:
        raise ValueError('Window level/width must be finite; width positive')
    return np.uint8(np.clip((values - (level - width / 2)) / width, 0, 1) * 255)


def render(data, affine, plane, at, level, width, size):
    h, hs, v, vs, k, left, right, top, bottom = PLANES[plane]
    lo, hi = bounds(data.shape, affine)
    if not np.isfinite(at) or not lo[k] <= at <= hi[k]:
        raise ValueError('Slice position outside volume bounds')
    center = (lo + hi) / 2
    span = max(hi[h] - lo[h], hi[v] - lo[v])
    axis = np.linspace(-span / 2, span / 2, size)
    points = np.broadcast_to(center, (size, size, 3)).copy()
    points[:, :, h] = center[h] + hs * axis[None, :]
    points[:, :, v] = center[v] + vs * axis[:, None]
    points[:, :, k] = at
    im = Image.fromarray(window(sample(data, affine, points), level, width)).convert('RGB')
    draw = ImageDraw.Draw(im)
    for xy, label in [((4, size // 2), left), ((size - 14, size // 2), right),
                      ((size // 2, 4), top), ((size // 2, size - 14), bottom)]:
        draw.rectangle(draw.textbbox(xy, label), fill='black')
        draw.text(xy, label, fill='white')
    return im


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('image', type=Path)
    ap.add_argument('--info', action='store_true')
    ap.add_argument('--plane', choices=PLANES, default='axial')
    ap.add_argument('--positions', help='Comma-separated RAS millimetres')
    ap.add_argument('--level', type=float, default=40)
    ap.add_argument('--width', type=float, default=400)
    ap.add_argument('--size', type=int, default=768)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    image = nib.load(args.image)
    if len(image.shape) != 3 or not np.isfinite(image.affine).all():
        raise ValueError('Expected a 3-D image with valid spatial metadata')
    lo, hi = bounds(image.shape, image.affine)
    info = {'shape': image.shape, 'spacing_mm': image.header.get_zooms(),
            'ras_min_mm': lo.tolist(), 'ras_max_mm': hi.tolist(),
            'voxel_axis_codes': nib.aff2axcodes(image.affine)}
    if args.info:
        print(json.dumps(info, default=float))
        return
    if args.out is None or not 128 <= args.size <= 2048:
        raise ValueError('--out required, size must be 128..2048')
    k = PLANES[args.plane][4]
    positions = ([float(x) for x in args.positions.split(',')] if args.positions
                 else np.linspace(lo[k], hi[k], 14)[1:-1].tolist())
    if not 1 <= len(positions) <= 24:
        raise ValueError('Choose 1..24 positions per sheet')
    data = image.get_fdata(dtype=np.float32)
    if not np.isfinite(data).all():
        raise ValueError('Non-finite intensity values')
    cols = min(3, len(positions))
    rows = (len(positions) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * args.size, rows * (args.size + 26)), 'black')
    draw = ImageDraw.Draw(sheet)
    for i, at in enumerate(positions):
        x, y = (i % cols) * args.size, (i // cols) * (args.size + 26)
        sheet.paste(render(data, image.affine, args.plane, at, args.level,
                           args.width, args.size), (x, y + 26))
        draw.text((x + 4, y + 5), f'{args.plane} RAS {at:.2f} mm | '
                  f'L {args.level:g} W {args.width:g}', fill='white')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        raise FileExistsError('Use a new filename to retain earlier views')
    sheet.save(args.out)
    event = {'view_id': uuid.uuid4().hex, 'image': args.image.name,
             'plane': args.plane, 'ras_positions_mm': positions,
             'level': args.level, 'width': args.width, 'tile_size': args.size,
             'output': str(args.out),
             'sha256': hashlib.sha256(args.out.read_bytes()).hexdigest()}
    with (args.out.parent / 'views.jsonl').open('a') as log:
        log.write(json.dumps(event) + '\n')
    print(json.dumps(event))


if __name__ == '__main__':
    main()

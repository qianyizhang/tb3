"""Render source-aligned before/after evidence; not part of the solver input."""
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from common import ROOT, OUT
sys.path.insert(0, str(ROOT / 'probes/revisions/br013/authoring'))
from inspect_scene import load_scene
sys.path.insert(0, str(Path(__file__).parent))
from inspect_ct import render_slice, PLANES


def main():
    before = load_scene(OUT / 'build/abdomen-n01')
    after = load_scene(OUT / 'build/abdomen-m02')
    selected = []
    for objects in [before, after]:
        subset = [o for o in objects if o['proposed_label'] in ['duodenum', 'pancreas']]
        for o in subset:
            o['color_index'] = 1 if o['proposed_label'] == 'duodenum' else 0
        selected.append(subset)
    with np.load(OUT / 'author/abdomen-m02/region-0.npz') as z:
        region = {k: z[k] for k in ['mask', 'affine_lps', 'surface_lps']}
    region.update(object_id='21 mL transferred tissue', color_index=3)
    selected.append([region])
    key = json.loads((OUT / 'author/abdomen-m02/expected.json').read_text())
    center = np.array(key['findings'][0]['oracle_point_lps_mm'])
    with np.load(OUT / 'build/abdomen-m02/ct.npz') as z:
        ct, affine = z['hu'], z['affine_lps']
    canvas = Image.new('RGB', (1320, 1080), (18, 23, 30))
    draw = ImageDraw.Draw(canvas); font = ImageFont.load_default(size=20)
    (OUT / 'review').mkdir(parents=True, exist_ok=True)
    draw.text((16, 10), 'Partial absorption: same CT, 21.0 mL reassigned; all 13 labels still present', font=font, fill='white')
    draw.text((16, 40), 'Pancreas: salmon | Duodenum: blue | Transferred region: yellow', font=font, fill='white')
    for row, plane in enumerate(['axial', 'coronal']):
        axis = PLANES[plane][2]
        for column, (title, objects) in enumerate(zip(['Original source labels', 'After reassignment', 'Author evidence: transferred region'], selected)):
            image, _ = render_slice(ct, affine, objects, plane, center[axis], center=center, span=180, size=440)
            state = ['before', 'after', 'region'][column]
            # Identical planes/windowing for the presentation's label-state toggle.
            image.save(OUT / 'review' / f'{plane}-{state}.png')
            x, y = column * 440, 104 + row * 485
            canvas.paste(image, (x, y + 24))
            draw.text((x + 6, y), f'{title} | {plane}', font=ImageFont.load_default(size=16), fill='white')
    draw.text((16, 1045), 'Synthetic annotation error. Identical CT planes and windowing; aggregate foreground unchanged.',
              font=ImageFont.load_default(size=16), fill='white')
    path = OUT / 'review/partial-absorption.png'; path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path); print(path)
    compact = Image.new('RGB', (1120, 640), (18, 23, 30)); draw = ImageDraw.Draw(compact)
    draw.text((15, 10), '21 mL of pancreas reassigned to duodenum; CT unchanged', font=font, fill='white')
    draw.text((15, 39), 'Pancreas: salmon | Duodenum: blue | All 13 labels remain present', font=ImageFont.load_default(size=17), fill='white')
    for j, (title, objects) in enumerate(zip(['Original labels', 'After partial absorption'], selected[:2])):
        draw.text((j * 560 + 10, 73), title, font=font, fill='white')
        im, _ = render_slice(ct, affine, objects, 'axial', center[2], center=center, span=180, size=530)
        compact.paste(im, (j * 560 + 15, 100))
    compact_path = OUT / 'review/partial-absorption-compact.png'
    compact.save(compact_path); print(compact_path)


if __name__ == '__main__':
    main()

"""Offline author-only preparation; requires selected, CRC-checked archive files."""
import hashlib
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image, ImageDraw


def main():
    source, task, out = Path('/source'), Path('/task'), Path('/out')
    image_path = source / 'ToothFairy3F_002_0000.nii.gz'
    gt_path = source / 'ToothFairy3F_002.nii.gz'
    image, gt = nib.load(image_path), nib.load(gt_path)
    data, mask = np.asanyarray(image.dataobj), np.asanyarray(gt.dataobj)
    labels = {str(v): k for k, v in json.loads((source / 'dataset.json').read_text())['labels'].items()}
    assert image.shape == gt.shape and np.array_equal(image.affine, gt.affine)
    assert np.isfinite(data).all() and np.equal(mask, np.rint(mask)).all()
    assert set(np.unique(mask)).issubset(set(map(int, labels)))
    header = image.header.copy()
    for field in ['descrip', 'aux_file', 'intent_name']:
        header[field] = b''
    header.extensions.clear()
    dest = task / 'environment/data/ct.nii.gz'
    nib.save(nib.Nifti1Image(data, image.affine, header), dest)
    check = nib.load(dest)
    assert np.array_equal(data, np.asanyarray(check.dataobj))
    assert np.array_equal(image.affine, check.affine)
    for directory in ['tests', 'solution']:
        shutil.copyfile(gt_path, task / directory / 'reference.nii.gz')
    for directory in ['environment/data', 'tests']:
        (task / directory / 'labels.json').write_text(json.dumps(labels, indent=2) + '\n')
    # Author QC only. Never part of the solver build context.
    canvas = Image.new('RGB', (1230, 850), '#101720')
    draw = ImageDraw.Draw(canvas)
    levels = [int(image.shape[2] * f) for f in [0.2, 0.45, 0.7]]
    for column, z in enumerate(levels):
        gray = np.uint8(np.clip((data[:, :, z].T + 500) / 3000, 0, 1) * 255)
        rgb = np.repeat(gray[:, :, None], 3, axis=2)
        overlay = rgb.astype(float)
        sl = mask[:, :, z].T
        for label in np.unique(sl):
            if label == 0:
                continue
            color = np.array([(int(label) * m) % 180 + 65 for m in [37, 83, 113]])
            overlay[sl == label] = 0.55 * overlay[sl == label] + 0.45 * color
        canvas.paste(Image.fromarray(rgb), (column * 410, 20))
        canvas.paste(Image.fromarray(overlay.astype('uint8')), (column * 410, 440))
        draw.text((column * 410 + 5, 2), f'F002 CT / GT below, native z={z}', fill='white')
    canvas.save(out / 'f002-pair-qc.png')
    receipt = {'source_ct_sha256': hashlib.sha256(image_path.read_bytes()).hexdigest(),
               'source_gt_sha256': hashlib.sha256(gt_path.read_bytes()).hexdigest(),
               'solver_ct_sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
               'original_voxels_and_affine_unchanged': True,
               'shape': list(image.shape), 'affine': image.affine.tolist(),
               'label_definitions': len(labels), 'gt_foreground_classes': len(np.unique(mask)) - 1,
               'label_counts_private': {str(int(k)): int(v) for k, v in zip(*np.unique(mask, return_counts=True))}}
    (out / 'preparation-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'label_counts_private'}))


if __name__ == '__main__':
    main()

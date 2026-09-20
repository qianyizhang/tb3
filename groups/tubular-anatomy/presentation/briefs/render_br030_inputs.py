"""Render supplied BR-030 input/helper views; no reference labels or model run.

Requires an existing imaging environment with nibabel, NumPy and Pillow.
Generated images stay local under presentation/tours/data/task-briefs/.
"""
import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image, ImageDraw


def render(root):
    root = Path(root)
    source = root / "runs/br030-vessel-geometry/geometry/input"
    output = root / "presentation/tours/data/task-briefs"
    output.mkdir(parents=True, exist_ok=True)
    image = nib.load(source / "image.nii.gz")
    hu = np.asarray(image.dataobj)
    mask = np.asarray(nib.load(source / "proposed_mask.nii.gz").dataobj) > 0
    request = json.loads((source / "request.json").read_text())
    affine = image.affine
    # This retained task uses axis-aligned RAS geometry. Fail rather than silently
    # display another orientation using the same labels.
    assert np.allclose(affine[:3, :3], np.diag(np.diag(affine[:3, :3])))
    assert affine[0, 0] < 0 < affine[1, 1] and affine[2, 2] > 0
    inv = np.linalg.inv(affine)
    center = (inv @ np.r_[request["review_center_ras_mm"], 1])[:3]
    j = int(round(center[1]))
    plane = hu[:, j, :][::-1, ::-1].T
    grey = np.uint8(np.clip((plane + 100) / 800, 0, 1) * 255)
    physical_w = (hu.shape[0] - 1) * abs(affine[0, 0])
    physical_h = (hu.shape[2] - 1) * affine[2, 2]
    width = 720; height = round(width * physical_h / physical_w)
    raw = Image.fromarray(grey).resize((width, height), Image.Resampling.BILINEAR).convert("RGB")
    raw.save(output / "br030-input.png")
    overlay = np.zeros((*plane.shape, 4), dtype=np.uint8)
    overlay[mask[:, j, :][::-1, ::-1].T] = [67, 224, 183, 140]
    layer = Image.fromarray(overlay).resize((width, height), Image.Resampling.NEAREST)
    helped = Image.alpha_composite(raw.convert("RGBA"), layer)
    draw = ImageDraw.Draw(helped)
    def project(point):
        ijk = (inv @ np.r_[point, 1])[:3]
        return ((hu.shape[0]-1-ijk[0])/(hu.shape[0]-1)*(width-1),
                (hu.shape[2]-1-ijk[2])/(hu.shape[2]-1)*(height-1))
    x, y = project(request["review_center_ras_mm"])
    radius = request["review_radius_mm"] * width / physical_w
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), outline=(252, 210, 88), width=3)
    for label, key in (("START", "start_ras_mm"), ("END", "end_ras_mm")):
        x, y = project(request[key])
        draw.ellipse((x-6, y-6, x+6, y+6), outline=(137, 192, 255), width=3)
        draw.text((x+10, y-8), label, fill=(180, 215, 255))
    helped.convert("RGB").save(output / "br030-helpers.png")
    paths = [source / n for n in ("image.nii.gz", "proposed_mask.nii.gz", "request.json")]
    paths += [output / n for n in ("br030-input.png", "br030-helpers.png")]
    receipt = {
        "source": "ImageCAS case 1, delivered CTA and unedited CAS-Net prediction; ImageCAS-X source context",
        "source_notice": "docs/evidence/br030-sources.json",
        "derivation": "Coronal native slice through supplied review marker; HU window -100 to 700; display resampling preserves physical aspect. No scoring reference or agent output read.",
        "slice_j": j,
        "orientation": "RAS X increases rightward; RAS Z upward. Dataset-oriented, not radiological convention.",
        "helpers": "Green is the supplied mask on this plane; gold is the 8 mm editable sphere cross-section at its center plane; blue start/end landmarks are projected and may be outside this plane.",
        "qualification": "Reader-selected view of a full 3D crop. A single plane does not demonstrate complete route connectivity or task difficulty.",
        "files": [{"path": p.relative_to(root).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
    }
    (Path(__file__).parent / "br030-visuals.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"output": str(output), "slice_j": j}))


if __name__ == "__main__":
    render(Path(__file__).resolve().parents[4])

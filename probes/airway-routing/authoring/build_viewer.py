"""Standalone local viewer of source CT and numeric geometry artifacts."""
import base64
import argparse
import io
import json
from pathlib import Path
import sys
import nibabel as nib
import numpy as np
from PIL import Image
import trimesh
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "probes/vessel-geometry/authoring"))
from geometry import transform, frames, sample, section_coordinates, mesh_from_mask

B = ROOT / "runs/br033-airway-routing/benchmark"


def png(a):
    f = io.BytesIO()
    Image.fromarray(a.astype("uint8")).save(f, format="PNG")
    return "data:image/png;base64," + base64.b64encode(f.getvalue()).decode()


def gray(a):
    return np.clip((a + 1000.) / 1100. * 255, 0, 255).astype("uint8")


def overlay(a, color):
    return np.concatenate([a[..., None] * np.array(color, dtype="uint8"), (a * 120)[..., None]], axis=-1).astype("uint8")


def atlas(a, axis):
    # Slice order, row, column. All display axes retain native voxel ordering.
    other = [j for j in range(3) if j != axis]
    order = [axis, other[1], other[0]] + list(range(3, a.ndim))
    v = np.transpose(a, order)
    return png(v.reshape((v.shape[0] * v.shape[1],) + v.shape[2:]))


def connectivity(mask, affine, anchors):
    labels, count = ndi.label(mask, np.ones((3, 3, 3)))
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0
    vox = np.rint(transform(anchors, np.linalg.inv(affine))).astype(int)
    hits = labels[tuple(vox.T)]
    return {"components": count, "anchor_components": hits.tolist(),
            "anchor_component_voxels": sizes[hits].tolist(),
            "anchors_connected": bool(hits[0] > 0 and hits[0] == hits[1]),
            "anchors_in_largest_component": (hits == sizes.argmax()).tolist()}


def surface(mesh, change, affine):
    # Highlight faces touching the added volume, including the half-voxel
    # marching-cubes boundary. This coloring does not change the surface.
    near = ndi.binary_dilation(change, np.ones((3, 3, 3)))
    faces_added = (sample(near, affine, mesh.triangles_center, 0, 0) > 0)
    return {"vertices": mesh.vertices.round(3).tolist(), "faces": mesh.faces.tolist(),
            "addedFaces": faces_added.tolist()}


def build(solution="image-baseline-v2", label="Image-guided development baseline", output="viewer"):
    records = []
    for case in ["A01", "A02", "A03"]:
        folder = B / solution / case
        source = B / "input" / case
        ni = nib.load(source / "image.nii.gz")
        im = np.asarray(ni.dataobj)
        before = np.asarray(nib.load(source / "proposed_mask.nii.gz").dataobj) > 0
        after = np.asarray(nib.load(folder / "corrected_mask.nii.gz").dataobj) > 0
        added = after & ~before
        line = np.load(folder / "centerline.npy")
        cpr = np.load(folder / "cpr.npz")
        _, n, b = frames(line)
        xyz = section_coordinates(line, n, b, cpr["offsets_mm"])
        section = sample(im, ni.affine, xyz)
        mesh = trimesh.load(folder / "airways.ply", process=False)
        request = json.loads((source / "request.json").read_text())
        anchors = np.array([request["start_ras_mm"], request["end_ras_mm"]])
        before_mesh = mesh_from_mask(before, ni.affine)
        position = int(np.argmin(np.linalg.norm(line - request["review_center_ras_mm"], axis=1)))
        if added.any():
            changed_samples = sample(added, ni.affine, line, 0, 0) > 0
            ids = np.flatnonzero(changed_samples)
            if len(ids):
                position = int(ids[len(ids) // 2])
        repair = case == "A01"
        note = ("Only the requested A01 connection was repaired: 578 voxels were added in the Terra run. Other disconnected fragments remain in this crop. Magenta marks added tissue; compare Input and Output to see the bridge."
                if repair else
                "No repair was made here. Both requested anchors lie within the same detached fragment, which remains disconnected from the larger airway. The test required this short internal route to be preserved; it did not test or repair the parent connection.")
        if solution != "terra-high" and repair:
            note = note.replace("578 voxels were added in the Terra run", f"{int(added.sum())} voxels were added by this development baseline")
        if case == "A03":
            note = "No repair was made here. This is the same CT and input mask as A01, but both anchors for A03 lie inside the detached fragment below the gap. The task required preserving that fragment. Its parent gap remains; choose A01 to see the actual repair of this connection."
        difference_overlay = overlay(before, [125, 153, 171])
        difference_overlay[added] = [255, 85, 171, 235]
        records.append({"id": case, "shape": list(im.shape), "spacing": ni.header.get_zooms()[:3],
            "path": line.tolist(), "pathIJK": transform(line, np.linalg.inv(ni.affine)).tolist(),
            "arc": cpr["arc_mm"].tolist(), "initial": position,
            "added": int((after & ~before).sum()), "removed": int((before & ~after).sum()),
            "anchors": anchors.tolist(), "note": note, "repairCase": repair,
            "connectivityBefore": connectivity(before, ni.affine, anchors),
            "connectivityAfter": connectivity(after, ni.affine, anchors),
            "source": [atlas(gray(im), k) for k in range(3)],
            "before": [atlas(overlay(before, [255, 176, 70]), k) for k in range(3)],
            "after": [atlas(overlay(after, [51, 217, 180]), k) for k in range(3)],
            "changes": [atlas(difference_overlay, k) for k in range(3)],
            "cpr": png(gray(cpr["hu"].transpose(0, 2, 1)).reshape(8 * 65, len(line))),
            "cprBefore": png(overlay(sample(before, ni.affine, cpr["source_ras_mm"], 0, 0).transpose(0, 2, 1) > 0, [255, 176, 70]).reshape(8 * 65, len(line), 4)),
            "cprAfter": png(overlay(sample(after, ni.affine, cpr["source_ras_mm"], 0, 0).transpose(0, 2, 1) > 0, [51, 217, 180]).reshape(8 * 65, len(line), 4)),
            "cprChanges": png(np.stack([sample(difference_overlay[..., k], ni.affine, cpr["source_ras_mm"], 0, 0).transpose(0, 2, 1) for k in range(4)], -1).astype('uint8').reshape(8 * 65, len(line), 4)),
            "sections": png(gray(section).reshape(-1, 65)),
            "meshBefore": surface(before_mesh, np.zeros_like(added), ni.affine),
            "meshAfter": surface(mesh, added, ni.affine),
            "downloads": "../benchmark/" + solution + "/" + case + "/"})
    out = B.parent / output
    out.mkdir(exist_ok=True)
    payload = json.dumps({"label": label, "cases": records}, default=lambda x: np.asarray(x).tolist(), separators=(",", ":"))
    html = Path(__file__).with_name("viewer.html").read_text().replace("__DATA__", payload)
    if solution == "terra-high":
        html = html.replace("The displayed development baseline reads public CT, masks, editable regions and anchors; its parameters were developed after author reference review.", "The displayed masks, centerlines and CPR are Terra/high's unchanged trial outputs. PLY meshes were derived afterward by the author from those masks; mesh construction was not a scored agent deliverable. The frozen trial passed anatomy and CPR for all three cases.")
    (out / "index.html").write_text(html)
    Image.fromarray(gray(np.load(B / solution / "A01/cpr.npz")["hu"][0].T)).resize((1200, 350)).save(out / "cpr-preview.png")
    print(json.dumps({"viewer": str(out / "index.html"), "bytes": len(html), "solution": solution}))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--solution", default="image-baseline-v2")
    p.add_argument("--label", default="Image-guided development baseline")
    p.add_argument("--output", default="viewer")
    a = p.parse_args()
    build(a.solution, a.label, a.output)

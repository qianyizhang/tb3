"""Audit retained BR-025 sources and build calibrated source-screen teaching views.

Import-safe; no downloads, inference, historical authoring imports or source writes.
Requires existing nibabel, NumPy, SciPy and Pillow imaging extras.
"""

import argparse
import json
import re
import shutil
import zlib
from pathlib import Path

import nibabel as nib
import numpy as np
from build_resect_assets import png
from build_respiratory_assets import dump, read, sha, world
from scipy import ndimage
from scipy.spatial import cKDTree

RECEIPT = "docs/evidence/br025-curation.json"
RECEIPT_SHA = "409dbebedc698353fe6c24580c469957ae8286660bee9751a87dd307849fc02a"
RAW = "runs/br025-vessel-curation"
DATA_TERMS = "LicenseRef-TopCoW-2024-noncommercial"
GRAPH_TERMS = "LicenseRef-CoW-Centerline-CC-BY-NC"
COLORS = {"other": [87, 115, 223], "right": [244, 156, 48], "left": [39, 196, 188]}


def edges(path):
    """Read the exact retained two-section 0/1 edge format; reject other YAML."""
    expected = {
        "anterior": {"L-A1", "Acom", "3rd-A2", "R-A1"},
        "posterior": {"L-Pcom", "L-P1", "R-P1", "R-Pcom"},
    }
    result, section = {}, None
    for line in path.read_text().splitlines():
        if line in ["anterior:", "posterior:"]:
            section = line[:-1]
            if section in result:
                raise ValueError("Duplicate edge section")
            result[section] = {}
        else:
            match = re.fullmatch(r"    ([A-Za-z0-9-]+): +([01])", line)
            if match is None or section is None or match[1] in result[section]:
                raise ValueError("Unexpected retained edge syntax")
            result[section][match[1]] = int(match[2])
    if {k: set(v) for k, v in result.items()} != expected:
        raise ValueError("Unexpected retained edge keys")
    return result


def gray(values, window):
    return png(
        np.rint(255 * np.clip((values - window[0]) / (window[1] - window[0]), 0, 1)).astype("uint8")
    )


def overlay(labels, projection=False):
    # Native axial convention: i increases right; j decreases down. No RAS reslicing.
    out_shape = (labels.shape[1], labels.shape[0])
    rgba = np.zeros((*out_shape, 4), dtype="uint8")
    for mask, key in [(labels > 0, "other"), (labels == 8, "right"), (labels == 9, "left")]:
        plane = np.flipud((mask.any(axis=2) if projection else mask).T)
        rgba[plane, :3] = COLORS[key]
        rgba[plane, 3] = 160
    return png(rgba)


def build(root, output, audit_path):
    output.mkdir(parents=True, exist_ok=False)
    if audit_path.exists():
        raise ValueError("Audit destination already exists")
    sources = {}

    def pin(rel, expected=None):
        path = root / rel
        h = sha(path)
        if expected is not None and h != expected:
            raise ValueError(f"Source bytes changed: {rel}")
        sources[rel] = h
        return path

    receipt = read(pin(RECEIPT, RECEIPT_SHA))
    members = {}
    for name in ["topcow-container.json", "centerlines-container.json"]:
        members.update({m["key"]: m for m in read(pin(RAW + "/" + name))["entries"]})
    for item in receipt["selected_files"]:
        p = pin(RAW + "/" + item["local_path"], item["sha256"])
        if (
            p.stat().st_size != item["bytes"]
            or zlib.crc32(p.read_bytes()) != members[item["archive_member"]]["crc"]
        ):
            raise ValueError("Retained size or ZIP CRC mismatch")
    for item in receipt["screened_mra_annotations"]:
        p = pin(
            RAW + "/TopCoW2024_Data_Release/antpos_edges_labelsTr/" + item["id"] + ".yml",
            item["sha256"],
        )
        if edges(p) != item["edges"]:
            raise ValueError("Screened annotation mismatch")
    public, reference, checks = [], [], []
    folder = root / RAW / "TopCoW2024_Data_Release"
    for row in receipt["sample_inspection"]:
        case_id = row["id"]
        image = nib.load(folder / "imagesTr" / f"{case_id}_0000.nii.gz")
        mask = nib.load(folder / "cow_seg_labelsTr" / f"{case_id}.nii.gz")
        if image.shape != mask.shape or not np.array_equal(image.affine, mask.affine):
            raise ValueError("Image/mask grid mismatch")
        if list(image.shape) != row["shape"] or not np.array_equal(image.affine, row["affine"]):
            raise ValueError("Recorded source geometry changed")
        if (
            list(nib.aff2axcodes(image.affine)) != ["L", "P", "S"]
            or image.header.get_xyzt_units()[0] != "mm"
        ):
            raise ValueError("Unexpected source orientation or units")
        labels = np.asarray(mask.dataobj)
        values, counts = np.unique(labels, return_counts=True)
        if {str(int(k)): int(v) for k, v in zip(values, counts, strict=True)} != row[
            "label_voxel_counts"
        ]:
            raise ValueError("Label counts differ from retained screen")
        vals = list(
            map(
                int,
                re.findall(r"\d+", (folder / "roi_loc_labelsTr" / f"{case_id}.txt").read_text()),
            )
        )
        size, origin = np.array(vals[:3]), np.array(vals[3:])
        if np.any(origin < 0) or np.any(origin + size > image.shape):
            raise ValueError("Source ROI out of bounds")
        sl = tuple(slice(int(o), int(o + n)) for o, n in zip(origin, size, strict=True))
        data = np.asarray(image.dataobj[sl], dtype=np.float32)
        crop = labels[sl]
        plane = np.flipud(data.max(axis=2).T)
        window = np.percentile(plane, [2, 99.5]).tolist()
        native_window = np.percentile(data, [2, 99.5]).tolist()
        shape = {"width": int(size[0]), "height": int(size[1])}
        item = {
            "id": case_id,
            "shape": list(image.shape),
            "affine_ras_mm": image.affine.tolist(),
            "spacing_mm": [float(v) for v in image.header.get_zooms()[:3]],
            "roi_origin_ijk": origin.tolist(),
            "roi_size_ijk": size.tolist(),
            "mip": {**shape, "png": gray(plane, window), "window": window},
            "native": [],
        }
        ref = {
            "id": case_id,
            "mip_overlay": overlay(crop, True),
            "native_overlays": [],
            "pcoms": {},
            "edges": row["mra_edges"]["posterior"],
            "admission_status": row["admission_status"],
        }
        pcom_indices = []
        for side, value, neighbors in [("right", 8, [4, 2]), ("left", 9, [6, 3])]:
            ijk = np.argwhere(labels == value)
            contacts = dict.fromkeys(map(str, neighbors), False)
            if len(ijk):
                pcom_indices.append(ijk)
                lo, hi = np.maximum(ijk.min(0) - 1, 0), np.minimum(ijk.max(0) + 2, labels.shape)
                local = labels[tuple(slice(int(a), int(b)) for a, b in zip(lo, hi, strict=True))]
                vessel = local == value
                _, components = ndimage.label(vessel, structure=np.ones((3, 3, 3)))
                around = ndimage.binary_dilation(vessel, structure=np.ones((3, 3, 3)))
                contacts = {str(n): bool(np.any(around & (local == n))) for n in neighbors}
            else:
                components = 0
            result = {
                "label": value,
                "voxel_count": len(ijk),
                "components_26": int(components),
                "touches_expected_parent_labels_26": contacts,
            }
            if result != row["pcoms"][side] or int((crop == value).sum()) != len(ijk):
                raise ValueError("Reference connectivity or ROI coverage mismatch")
            ref["pcoms"][side] = result
        for modality in ["mr", "ct"]:
            modality_edges = edges(
                folder
                / "antpos_edges_labelsTr"
                / f"{case_id.replace('_mr_', '_' + modality + '_')}.yml"
            )
            if modality_edges != row["mra_edges"]:
                raise ValueError("Paired edge annotation mismatch")
        node_file = root / RAW / "CoW_Centerline_Data/cow_nodes" / f"{case_id}.json"
        nodes = [
            {**node, "source_label": lab, "name": name}
            for lab, group in read(node_file).items()
            for name, values in group.items()
            for node in values
        ]
        unique = {}
        for node in nodes:
            if node["id"] in unique and unique[node["id"]] != node["coords"]:
                raise ValueError("Shared node ID has inconsistent coordinates")
            unique[node["id"]] = node["coords"]
        coords = np.array([n["coords"] for n in nodes])
        if not np.isfinite(coords).all():
            raise ValueError("Nonfinite source nodes")
        foreground = world(np.argwhere(labels > 0), image.affine)
        distances = cKDTree(foreground).query(coords)[0]
        stats = {
            "median": float(np.median(distances)),
            "p95": float(np.percentile(distances, 95)),
            "max": float(distances.max()),
        }
        recorded = row["graph_node_alignment_screen"]
        if len(nodes) != recorded["node_occurrences"] or any(
            abs(stats[k] - recorded["distance_to_foreground_voxel_centers_mm"]["as_stored"][k])
            > 1e-9
            for k in stats
        ):
            raise ValueError("Graph-node alignment mismatch")
        voxel_nodes = world(coords, np.linalg.inv(image.affine))
        back = world(voxel_nodes, image.affine)
        if np.max(np.abs(back - coords)) > 1e-10:
            raise ValueError("Node affine roundtrip failure")
        ref["node_entries"] = [
            {
                "id": n["id"],
                "source_label": n["source_label"],
                "name": n["name"],
                "ras_mm": n["coords"],
                "native_ijk": v.tolist(),
                "foreground_distance_mm": float(d),
            }
            for n, v, d in zip(nodes, voxel_nodes, distances, strict=True)
        ]
        ref["node_distances_mm"] = stats
        if case_id.endswith("007"):
            all_indices = np.concatenate(pcom_indices)
            # Source-annotation-guided author view; one native-slice halo, not a solver crop.
            for k in range(int(all_indices[:, 2].min()) - 1, int(all_indices[:, 2].max()) + 2):
                local_k = k - int(origin[2])
                values = np.flipud(data[:, :, local_k].T)
                origin_ijk = np.array([origin[0], origin[1] + size[1] - 1, k])
                item["native"].append(
                    {
                        **shape,
                        "k": k,
                        "png": gray(values, native_window),
                        "window": native_window,
                        "origin_world_mm": world(origin_ijk[None], image.affine)[0].tolist(),
                        "dx_world_mm": image.affine[:3, 0].tolist(),
                        "dy_world_mm": (-image.affine[:3, 1]).tolist(),
                    }
                )
                ref["native_overlays"].append(overlay(crop[:, :, local_k]))
        public.append(item)
        reference.append(ref)
        checks.append(
            {
                "id": case_id,
                "shape_affine_match": True,
                "image_sform": int(image.header["sform_code"]),
                "native_axis_codes": list(nib.aff2axcodes(image.affine)),
                "pcoms": ref["pcoms"],
                "all_pcom_voxels_inside_source_roi": True,
                "paired_edge_labels_match": True,
                "node_entries": len(nodes),
                "node_distance_mm": stats,
                "node_roundtrip_max_mm": float(np.max(np.abs(back - coords))),
            }
        )
    dump(output / "geometry.json", {"frame": "RAS", "units": "mm", "cases": public})
    dump(
        output / "reference.json",
        {
            "cases": reference,
            "screened_edges": [
                {
                    "id": r["id"],
                    "left": r["edges"]["posterior"]["L-Pcom"],
                    "right": r["edges"]["posterior"]["R-Pcom"],
                }
                for r in receipt["screened_mra_annotations"]
            ],
        },
    )
    dump(
        output / "output.json",
        {
            "source_candidates": [
                {"id": r["id"], "status": r["admission_status"]}
                for r in receipt["sample_inspection"]
            ],
            "natural_faulty_prediction": None,
            "admitted_defect_fixtures": receipt["admitted_defect_fixtures"],
            "local_model_trials": receipt["local_model_trials"],
            "numeric_verifier_thresholds": "not_frozen",
        },
    )
    shutil.copyfile(folder / "License.txt", output / "DATA-LICENSE.txt")
    (output / "GRAPH-TERMS.txt").write_text(
        "Circle of Willis Centerline Graphs and Morphometric Features\nMusio, Juchler, Yang, Shit, Prabhakar, Menze and Hirsch.\nhttps://zenodo.org/records/17358162\nSource page checked 2026-09-27: CC BY-NC (Attribution-NonCommercial).\nThe page does not specify a license version; none is inferred here.\nDerived from TopCoW masks, not independent anatomical truth.\nThis pack retains node coordinates and technical alignment summaries only;\ncomplete graph paths are not rendered or independently validated.\n"
    )
    (output / "NOTICE.md").write_text("""# TopCoW source-screen teaching assets

Sources: TopCoW Challenge Organizers / Yang et al., Benchmarking the CoW with
the TopCoW Challenge, https://arxiv.org/abs/2312.17670,
https://zenodo.org/records/15692630. Retained training release License.txt is
copied byte for byte: attribution required; commercial use requires owner
permission. Source page rechecked 2026-09-27 and remains consistent with those
terms. Local author research views do not resolve commercial redistribution.

Node reference: Musio et al., Circle of Willis Centerline Graphs: A Dataset
and Baseline Algorithm, https://zenodo.org/records/17358162 (GRAPH-TERMS.txt).
Graph source page declares CC BY-NC without a version. Reference coordinates
and metrics are technical corroboration derived from the same source masks,
not independent anatomical truth. No complete VTP edge validation is claimed.

Changes: compact axial maximum-intensity projections through each provided CoW
bounding box; grayscale clipped at the MIP's 2nd/99.5th percentiles. The 007
native sequence uses its fixed ROI-intensity 2nd/99.5th window and all native
k slices covering the two annotated Pcoms plus a one-slice halo. No interpolated
anatomy, registration, inferred path or injected defect. The sequence is an
annotation-guided author inspection view, not a solver-visible crop contract.
Image and labels retain native sampling. Native axes are oblique and have L/P/S
orientation codes; i increases right and j decreases down on screen. NIfTI
physical coordinates use RAS+ mm. Full affines and slice pixel calibration are
retained; a MIP collapses depth and is not a single physical section.

Reference overlays: orange right Pcom (label8), teal left Pcom (label9), blue
other source vessel labels. Alpha160/255 over the image. These are annotations,
not predictions. Reader reference reveal is separate from images; node markers
are projected using the same native affine and ROI, never independently fitted.
Repeated shared-boundary node entries remain in statistics, not independent
measurements. Source labels say absent; clinical absence is not adjudicated.

output.json reproduces source-candidate status: no natural faulty prediction,
no admitted defect fixture and no model trial at the BR-025 curation close.
The proposed future solver receives MRA, a proposed binary mask and a broad
editable region, not these masks/graphs/edge answers. No GT-shaped corridor is
invented. Thresholds, prediction provenance and case adjudication remain open.
Later BR-026 synthetic feasibility is a separate contract and result.

All 30 selected source files are verified by size, SHA-256 and retained ZIP CRC;
12 screened MRA edge files are checked. Four source grids, Pcom counts,
26-connected label components/parent contacts and 146 node-entry nearest-foreground
distances are recomputed. Those checks neither validate all graph edges nor
resolve congenital absence, flow ambiguity, task difficulty or clinical safety.
Original curation receipt and source files remain unchanged.
""")
    assets = [
        {
            "file": p.name,
            "sha256": sha(p),
            "bytes": p.stat().st_size,
            "provenance": "source-derived-teaching",
            "role": "reader-reference-reveal" if p.name == "reference.json" else "illustration",
        }
        for p in sorted(output.iterdir())
    ]
    if any(a["bytes"] > 1024 * 1024 for a in assets):
        raise ValueError("Asset exceeds retention limit")
    dump(
        output / "manifest.json",
        {
            "schema": 1,
            "id": "retained-vessel-source-v1",
            "frame": "RAS",
            "units": "mm",
            "license": DATA_TERMS,
            "label_license": GRAPH_TERMS,
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "assets": assets,
        },
    )
    audit = {
        "schema_version": 1,
        "actor": "assistant",
        "date": "2026-09-27",
        "scope": "Retained BR-025 source and presentation audit; no clinical adjudication or trial.",
        "sources": sources,
        "selected_files_verified_by_size_sha_crc": 30,
        "screened_mra_edge_files": 12,
        "cases": checks,
        "present_pcom_labels": 4,
        "node_entries": sum(c["node_entries"] for c in checks),
        "largest_node_distance_mm": max(c["node_distance_mm"]["max"] for c in checks),
        "native_slice_count": len(public[1]["native"]),
        "native_slice_range": [public[1]["native"][0]["k"], public[1]["native"][-1]["k"]],
        "limits": [
            "Node checks do not validate full VTP edges.",
            "Reference-derived teaching views do not make a fair solver packet.",
            "No natural faulty prediction, frozen numerical verifier or admitted defect fixture at curation close.",
            "Source-annotation absence is not a new clinical diagnosis.",
        ],
    }
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    dump(audit_path, audit)
    print(
        json.dumps(
            {
                "output": str(output),
                "sources": len(sources),
                "checks": checks,
                "native_slices": audit["native_slice_count"],
                "asset_bytes": {a["file"]: a["bytes"] for a in assets},
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    build(args.root, args.output, args.audit)

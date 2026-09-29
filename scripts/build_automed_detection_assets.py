"""Build four source-bounded AutoMedBench Full detection teaching packs; no evaluator/model runs."""

from __future__ import annotations
import argparse, hashlib, json, shutil, xml.etree.ElementTree as ET, zipfile
from pathlib import Path

PREFIX = "automedbench-full-"
SUFFIX = "-det-task"
KEYS = ("bccd", "dentex", "grazpedwri", "vindr-cxr")
SOURCE = Path(".local/explainers/core-20260929/automed-detection-source")
DENTEX = Path(".local/explainers/core-20260929/rex-dentex-isles-source/dentex")
IMAGE_HASHES = {
    "bccd": "e1dcc488889acba247a895df7be839e514850030217b4025048619f664fd4cb3",
    "dentex": "ac62de4d5587c9da20fc0995a01ad0e61e3d7329e5c9e9c59f74330bc234a00c",
    "grazpedwri": "e892807f0cda635e794b59f078fdf539fababb9cbd8a17fcf8ea8f21c87b7c5d",
}
IMAGES = {
    "bccd": ("BloodImage_00000.jpg", 640, 480),
    "dentex": ("train_266.png", 1976, 976),
    "grazpedwri": ("0001_1297860435_01_WRI-L2_M014.png", 536, 836),
}
CLASSES = {
    "bccd": ["platelets", "rbc", "wbc"],
    "dentex": ["Caries", "Deep Caries", "Periapical Lesion", "Impacted"],
    "grazpedwri": [
        "boneanomaly",
        "bonelesion",
        "foreignbody",
        "fracture",
        "metal",
        "periostealreaction",
        "pronatorsign",
        "softtissue",
        "text",
    ],
    "vindr-cxr": [
        "Aortic enlargement",
        "Atelectasis",
        "Calcification",
        "Cardiomegaly",
        "Consolidation",
        "ILD",
        "Infiltration",
        "Lung Opacity",
        "Nodule/Mass",
        "Other lesion",
        "Pleural effusion",
        "Pleural thickening",
        "Pneumothorax",
        "Pulmonary fibrosis",
    ],
}
SOURCE_URL = {"dentex": "https://zenodo.org/records/7812323"}
PACK_LICENSE = {
    "bccd": "MIT",
    "dentex": "CC-BY-4.0",
    "grazpedwri": "CC-BY-4.0",
    "vindr-cxr": "LicenseRef-TB3-symbolic-teaching",
}
HEADINGS = {
    "bccd": "Blood-smear cell boxes",
    "dentex": "Dental disease boxes",
    "grazpedwri": "Pediatric wrist finding boxes",
    "vindr-cxr": "Chest X-ray abnormality boxes",
}
TASK_DETAIL = {
    "bccd": "Full detection asks for platelet, RBC and WBC boxes; this upstream image is not a verified Full case.",
    "dentex": "Upstream annotations have quadrant, tooth and disease fields; Full output uses a disease class string and box.",
    "grazpedwri": "Full detection asks for nine wrist-finding classes; this upstream image is not a verified Full case.",
    "vindr-cxr": "VinDr-CXR is credentialed; this pack contains no real chest image or annotation.",
}


def root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "presentation/EXPLAINER-SCOPE.json").is_file():
            return p
    raise RuntimeError("Cannot locate tb3 checkout")


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha(p: Path) -> str:
    return sha_bytes(p.read_bytes())


def write_json(p: Path, d: object) -> None:
    p.write_text(json.dumps(d, sort_keys=True, separators=(",", ":")) + "\n")


def get_sources(r: Path, key: str):
    if key == "bccd":
        img = r / SOURCE / "bccd-sample/BloodImage_00000.jpg"
        lab = r / SOURCE / "bccd-sample/BloodImage_00000.xml"
        assert (
            sha(img) == IMAGE_HASHES[key]
            and sha(lab) == "655ee0c67cbac5bf3961e017c75b130be1995f824557916eabdbe99d29fae101"
        )
        assert (
            ET.parse(lab).findtext(".//size/width"),
            ET.parse(lab).findtext(".//size/height"),
        ) == ("640", "480")
        data = img.read_bytes()
        boxes = []
        for i, o in enumerate(ET.parse(lab).findall(".//object")):
            bb = o.find("bndbox")
            boxes.append(
                {
                    "id": i,
                    "class": o.findtext("name").lower(),
                    "xyxy": [int(bb.findtext(k)) for k in ("xmin", "ymin", "xmax", "ymax")],
                }
            )
        assert (
            len(boxes) == 20
            and sum(x["class"] == "rbc" for x in boxes) == 19
            and sum(x["class"] == "wbc" for x in boxes) == 1
        )
        return (
            data,
            boxes,
            {str(img.relative_to(r)): sha(img), str(lab.relative_to(r)): sha(lab)},
            "Source VOC labels; not Full private boxes",
        )
    if key == "dentex":
        img = r / DENTEX / "train_266.png"
        lab = r / DENTEX / "train_quadrant_enumeration_disease.json"
        assert (
            sha(img) == IMAGE_HASHES[key]
            and sha(lab) == "6e1f702cfd6c83bc63660d9a0fd79fe5b26d5a54b63d93b954a02cc254314483"
        )
        j = json.loads(lab.read_text())
        image = next(x for x in j["images"] if x["file_name"] == "train_266.png")
        assert (image["width"], image["height"]) == (1976, 976)
        names = {x["id"]: x["name"] for x in j["categories_3"]}
        boxes = []
        for a in sorted(
            (x for x in j["annotations"] if x["image_id"] == image["id"]), key=lambda x: x["id"]
        ):
            x, y, w, h = a["bbox"]
            boxes.append(
                {
                    "id": a["id"],
                    "class": names[a["category_id_3"]],
                    "xyxy": [x, y, x + w, y + h],
                    "source_hierarchy": {
                        "quadrant_id": a["category_id_1"],
                        "tooth_id": a["category_id_2"],
                        "disease_id": a["category_id_3"],
                    },
                }
            )
        assert len(boxes) == 5
        return (
            img.read_bytes(),
            boxes,
            {str(img.relative_to(r)): sha(img), str(lab.relative_to(r)): sha(lab)},
            "Source COCO hierarchy; not Full private boxes",
        )
    if key == "grazpedwri":
        img = r / SOURCE / "grazped-sample/0001_1297860435_01_WRI-L2_M014.png"
        z = r / SOURCE / "grazped-sample/folder_structure.zip"
        assert (
            sha(img) == IMAGE_HASHES[key]
            and sha(z) == "eac47bc5dfc01c1487289df53fc6bbfbfefd2e4a3bbcdeaa1b2dd73fe202919a"
        )
        import struct
        import zlib

        assert img.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(
            ">II", img.read_bytes()[16:24]
        ) == (536, 836)
        assert zlib.crc32(img.read_bytes()) == 0x45BC4CBA
        member = "pascalvoc/0001_1297860435_01_WRI-L2_M014.xml"
        with zipfile.ZipFile(z) as zf:
            root_xml = ET.fromstring(zf.read(member))
        boxes = []
        for i, o in enumerate(root_xml.findall(".//object")):
            bb = o.find("bndbox")
            boxes.append(
                {
                    "id": i,
                    "class": o.findtext("name").strip(),
                    "xyxy": [int(bb.findtext(k)) for k in ("xmin", "ymin", "xmax", "ymax")],
                }
            )
        assert [x["class"] for x in boxes] == ["text", "fracture", "pronatorsign"]
        return (
            img.read_bytes(),
            boxes,
            {str(img.relative_to(r)): sha(img), str(z.relative_to(r)): sha(z)},
            "Source Pascal VOC labels; not Full private boxes",
        )
    return None, [], {}, "No image or labels under PhysioNet credential gate"


def build(r: Path, key: str, out: Path, receipt: Path) -> None:
    if key not in KEYS:
        raise ValueError(key)
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite {out}")
    d = json.loads(receipt.read_text())
    assert d["entry_id"] == PREFIX + key + SUFFIX
    assert d["illustration_basis"] in ("mixed", "symbolic") and all(
        x.get("attempted_at") for x in d["attempts"]
    )
    img, boxes, srcs, role = get_sources(r, key)
    pkg = r / SOURCE / "packages" / (key + ".tar.gz")
    assert sha(pkg) == d["task_package"]["sha256"]
    name, w, h = IMAGES[key] if key in IMAGES else (None, None, None)
    pack_id = f"retained-automed-full-{key}-detection-v1"
    notice = {
        "label": (
            "Official upstream image; Full staged case not established"
            if img
            else "No accessible VinDr-CXR case"
        ),
        "text": (
            "The source label is a reader-only teaching reference. No Full private box, model prediction or score is retained."
            if img
            else "PhysioNet requires credentialing, training and DUA; Full images, private boxes and Lite runtime assets are unavailable."
        ),
        "url": SOURCE_URL.get(key, d["upstream_url"]),
        "link_label": "Official source and access",
    }
    if key == "dentex":
        notice["text"] += (
            " Full manifest and recovered source license notices differ; version equivalence is unresolved."
        )
    out.mkdir(parents=True)
    if img:
        (out / name).write_bytes(img)
    source = {
        "role": "upstream-source-input-not-full-staged-case" if img else "symbolic-contract-only",
        "image": name,
        "width_px": w,
        "height_px": h,
        "frame": "image-pixel-top-left",
        "units": "px",
        "title": HEADINGS[key],
        "classes": CLASSES[key],
        "task_detail": TASK_DETAIL[key],
        "upstream_annotation_role": role,
        "full_data_dir": d["task_package"]["data_dir_name"],
        "notice": notice,
    }
    output = {
        "role": "required-empty-output-schema",
        "path": "agents_outputs/{case_id}/prediction.json",
        "prediction_json": {"boxes": []},
        "box_fields": ["class", "score", "x1", "y1", "x2", "y2"],
        "score_rule": "score optional for format validity but used for ranked AP; use 0..1",
        "coordinate_rule": "original image pixels, top-left origin; invert any resize",
        "prediction": None,
        "mAP": None,
    }
    reference = {
        "role": "upstream-source-label-reader-reveal" if img else "unavailable",
        "full_private_boxes": None,
        "source_boxes": boxes,
        "source_box_count": len(boxes),
        "warning": "These source annotations are not the AutoMedBench Full private reference.",
    }
    write_json(out / "source.json", source)
    write_json(out / "output.json", output)
    write_json(out / "reference.json", reference)
    (out / "NOTICE.md").write_text(f"{notice['label']}. {notice['text']} {notice['url']}\n")
    license = PACK_LICENSE[key]
    (out / "DATA-LICENSE.txt").write_text(
        (
            f"BCCD official source: {d['upstream_url']}.\n\n"
            + (r / SOURCE / "bccd-sample/LICENSE").read_text()
        )
        if key == "bccd"
        else f"{license}. Official source: {SOURCE_URL.get(key, d['upstream_url'])}. Source receipt terms: {d['source_license']}. Local teaching use; verify terms before redistribution.\n"
    )
    files = [
        ("source.json", "illustration"),
        ("output.json", "illustration"),
        ("reference.json", "reader-reference-reveal" if img else "illustration"),
        ("NOTICE.md", "illustration"),
        ("DATA-LICENSE.txt", "illustration"),
    ]
    if img:
        files.insert(0, (name, "illustration"))
    provenance = "source-derived-teaching"
    assets = [
        {
            "file": f,
            "sha256": sha(out / f),
            "bytes": (out / f).stat().st_size,
            "provenance": provenance,
            "role": role,
        }
        for f, role in files
    ]
    manifest = {
        "id": pack_id,
        "frame": "image-pixel-top-left" if img else "symbolic-image-pixel-top-left",
        "units": "px",
        "license": license,
        "label_license": license if img else None,
        "reference_policy": "reader-reference-reveal" if img else "no-reference-assets",
        "assets": assets,
        "sources": srcs | {str(pkg.relative_to(r)): sha(pkg)},
        "checks": {
            "full_staged_case": False,
            "full_private_boxes": False,
            "saved_prediction": False,
            "evaluator_run": False,
            "upstream_source_boxes": len(boxes),
        },
    }
    write_json(out / "manifest.json", manifest)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entry", required=True, choices=KEYS)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--receipt", required=True, type=Path)
    a = ap.parse_args()
    r = root()
    build(r, a.entry, a.output, a.receipt)


if __name__ == "__main__":
    main()

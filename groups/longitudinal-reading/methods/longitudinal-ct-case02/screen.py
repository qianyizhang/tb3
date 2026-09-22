"""Screen the pinned per-patient metadata without using model outcomes."""

import collections
import csv
import hashlib
import json
import statistics
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-case02"
RAW = ROOT / ".local/longitudinal-ct-review/raw"
INDEX = ROOT / ".local/longitudinal-ct-review/source/zip-index.json"


def main():
    index = json.loads(INDEX.read_text())
    by_name = {r["name"]: r for r in index}
    patients, allrows, receipts = [], [], []
    for p in sorted((RAW / "inputsTr").glob("*.csv")):
        data = p.read_bytes()
        ent = by_name[str(p.relative_to(RAW))]
        assert len(data) == ent["size"] and zlib.crc32(data) == ent["crc32"]
        receipts.append(
            {"member": str(p.relative_to(RAW)), "sha256": hashlib.sha256(data).hexdigest()}
        )
        rows = list(csv.DictReader(p.open()))
        allrows.extend(rows)
        ct = [
            x
            for x in index
            if Path(x["name"]).name.startswith(p.stem + "_") and "_img_" in x["name"]
        ]
        bl, fu = {}, {}
        for r in rows:
            ident = int(r["lesion_id"])
            if r["topology_class"] != "NEWLYAPPEARING":
                bl[ident] = float(r["volume_bl"]) / 1000
            if r["topology_class"] != "DISAPPEARING":
                dest = int(float(r["merged_into"])) if r["topology_class"] == "MERGING" else ident
                volume = float(r["volume_fu"]) / 1000
                assert dest not in fu or abs(fu[dest] - volume) < 1e-6
                fu[dest] = volume
        volumes = list(bl.values()) + list(fu.values())
        new = [
            float(r["volume_fu"]) / 1000 for r in rows if r["topology_class"] == "NEWLYAPPEARING"
        ]
        d = {
            "patient": p.stem,
            "events": dict(collections.Counter(r["topology_class"] for r in rows)),
            "types": dict(collections.Counter(r["lesion_type"] for r in rows)),
            "bl_count": len(bl),
            "fu_count": len(fu),
            "minimum_ml": min(volumes),
            "median_ml": statistics.median(volumes),
            "largest_new_ml": max(new, default=0),
            "all_links_explicitly_clear": all(r.get("linking_unclear") == "False" for r in rows),
            "single_volume_per_visit": sorted(Path(x["name"]).name for x in ct)
            == [p.stem + "_BL_img_00.nii.gz", p.stem + "_FU_img_00.nii.gz"],
            "lung_liver_rows": sum(r["lesion_type"] in ["Lung", "Liver"] for r in rows),
            "compressed_bytes": sum(
                x["compressed"] for x in index if Path(x["name"]).name.startswith(p.stem)
            ),
        }
        patients.append(d)
    candidates = [
        d
        for d in patients
        if d["all_links_explicitly_clear"]
        and d["single_volume_per_visit"]
        and 4 <= d["bl_count"] <= 15
        and 4 <= d["fu_count"] <= 15
        and d["events"].get("NEWLYAPPEARING", 0)
        and d["events"].get("UNCHANGED", 0)
        and not d["events"].get("MERGING", 0)
        and d["lung_liver_rows"] >= 3
    ]
    ranked = sorted(
        candidates, key=lambda d: (-d["minimum_ml"], -d["largest_new_ml"], d["patient"])
    )
    result = {
        "source_release": "Longitudinal-CT v3 / qe950-g4h94",
        "criteria": "One acquisition per visit; every link explicitly clear; 4-15 present labels per visit; persistence plus newly appearing; no merging; >=3 lung/liver rows. Rank larger minimum lesion volume then larger new lesion, then patient ID. Purposive contrast to first nodal-merger case, not prevalence sampling.",
        "selection_timing": "After descriptive metadata exploration, before new CT download and any new model output.",
        "csv_rows": len(allrows),
        "patient_count": len(patients),
        "row_event_counts": dict(collections.Counter(r["topology_class"] for r in allrows)),
        "row_anatomy_counts": dict(collections.Counter(r["lesion_type"] for r in allrows)),
        "present_instances_bl": sum(d["bl_count"] for d in patients),
        "present_instances_fu": sum(d["fu_count"] for d in patients),
        "patients_all_links_explicitly_clear": sum(
            d["all_links_explicitly_clear"] for d in patients
        ),
        "patients_single_volume_each": sum(d["single_volume_per_visit"] for d in patients),
        "eligible": ranked,
        "selected": ranked[0],
        "metadata_hashes": receipts,
        "index_sha256": hashlib.sha256(INDEX.read_bytes()).hexdigest(),
        "limitations": "Present counts derive from topology and deduplicated destination IDs, not whole-mask validation. Row anatomy counts are longitudinal rows, not baseline prevalence. No tiny lesions will be removed from the selected reference. Selection awaits native-image/GT sanity review.",
    }
    path = BASE / "source/selection.json"
    assert not path.exists()
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in result if k not in ["metadata_hashes"]}, indent=2))


if __name__ == "__main__":
    main()

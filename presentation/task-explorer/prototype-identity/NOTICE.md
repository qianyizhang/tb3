# BR-011 I2 anonymous point display

TotalSegmentator small v2.0.1, Wasserthal and University Hospital Basel. https://zenodo.org/records/10047263 . Data CC BY 4.0; label definitions Apache 2.0. Full terms are retained here. No source author endorses this view.

The 17 objects come from retained prototype case 32, not the s1233 assembly used by other stories. All public files match the author-screen receipt. Each original PLY point was checked against the public 3 mm occupancy array and affine. The display keeps up to 1,600 evenly indexed source points per object; no point is relocated. This discards detail. Points have no faces and do not establish topology. The local occupancy volume remains authoritative; no CT or full occupancy array is embedded.

All objects share one LPS-to-display rotation, centre and uniform scale. No object is individually rotated, reflected, centred or resized. The selected object is teal; all others are neutral. IDs, colours and order are the prototype's arbitrary identifiers.

reference.json is the currently retained private author identity key, pinned by this review. All 17 assignments were checked against the separately hash-verified original source occupancy and taxonomy; the source affine is unchanged. The labels are exposed only after an explicit reader reveal and must not be given to a blind solver. Source-key agreement does not establish clinical correctness or mask-only identifiability. The packet is an authoring calibration prototype, not an admitted model experiment.

Rebuild to a fresh output using `uv run --no-sync python scripts/build_prototype_identity_assets.py --root . --output NEW_DIRECTORY`. The script needs NumPy and does not import historical authoring modules, modify their outputs, download data or launch a model.

# BR-017 selected CT slices and mask outlines

TotalSegmentator small v2.0.1, Wasserthal and University Hospital Basel. Source: https://zenodo.org/records/10047263 . Data: CC BY 4.0; taxonomy: Apache 2.0. Full terms are retained alongside these assets. No source author endorses this view.

These three s1233 slices are extracted from the hash-verified BR-017 M02 task archive. CT voxel values are windowed at level 50 / width 400 HU into 8-bit PNGs, with no spatial interpolation. Each 149-pixel square covers 223.5 mm. Outlines follow native voxel edges; they are display paths, not returned contours. Pixel-centre LPS transforms are in fixture.json.

All planes and crops were selected using the private oracle point. This is a reader teaching view, not evidence of finding the location independently. The gold region and witness are private-evaluator material, shown only after reference reveal. They must not be passed to a solver. Before reveal, teal marks the supplied duodenum host and blue the remaining pancreas. Gold marks transferred source-pancreas voxels after reveal; a white ring marks the reference witness. The task does not expose original reference masks.

M02 is a synthetic label edit with unchanged CT. N01 source masks are used only to verify voxel lineage, not to assert clinical correctness. This retained display supports no diagnosis, population claim or new model result. Full volumes remain local.

Rebuild to a fresh output with `.venv-br030/bin/python scripts/build_mixed_tissue_assets.py --root . --output NEW_DIRECTORY`; NumPy and Pillow suffice. Never import historical authoring modules or overwrite freezes.

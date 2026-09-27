# Respiratory correspondence teaching views

Learn2Reg LungCT 1.11. Hering, Alessa; Murphy, Keelin; van Ginneken, Bram (2020), Radboud University Medical Center. Source attribution: https://doi.org/10.5281/zenodo.3835682 . CC BY 4.0: https://creativecommons.org/licenses/by/4.0/ . Exact license text retained. No source creator endorses this adaptation.

The original release was cropped, resampled and affine prealigned. Coordinates are supplied dataset-world millimetres, NOT asserted native LPS or RAS. Each plane stores the world position of pixel centre (0,0), column/row displacement vectors, width and height. Grayscale bytes are round(255*clip((HU+1000)/1200,0,1)); PNGs encode exactly those bytes. Orthogonal display sections are trilinearly interpolated from existing public arrays; axes are dataset X/Y/Z, not anatomical labels. No dense field, segmentation or continuous volumetric reconstruction is supplied.

Public oblique patient1/patient3 slices are retained. Three source and three target display sections pass through public patient3 q06. Target closeups span 64 mm through the retained returned q06 coordinate, not a reference-centred crop. q06 was chosen after scoring for reader teaching. It is not a new search result or blinded case selection. reference.json separately holds private manual answers, scores and the later user judgment. The initial view hides these; this bundle is not a solver packet.

All four task freezes and retained source members are hash-checked. BR-024/028 differ only in prompt/task name and one added full-source NPZ; old inputs, query geometry, targets, answers and grader stay identical. The source NPZ matches NIfTI exactly and independently reproduces all 22869 public view pixels within 0.000031 HU. Both retained answers are independently remeasured. Historical authoring modules are never imported or executed, and no model trial is launched.

Sparse RMS <=3 mm AND maximum <=5 mm are engineering gates, not observer uncertainty or clinical equivalence. BR-028 still fails its numerical gate; the later user's visual acceptance is separately retained. One fresh attempt per condition cannot isolate a causal depth effect. Source/public annotations may be retrievable externally, so image isolation is not a guarantee against training contamination or answer lookup.

Rebuild with the existing NumPy/SciPy/NiBabel/Pillow environment: `python scripts/build_respiratory_assets.py --root . --output NEW_DIRECTORY`.

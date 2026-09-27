# VerSe anatomy curation teaching derivative

VerSe data: Anjany Sekuboyina et al.; Hans Liebl, David Schinz et al.; Maximilian Loffler et al. Source: https://github.com/anjany/verse and https://doi.org/10.1038/s41597-021-01060-0 . Data and this point/reference derivative are CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/ . License text and disclaimers are retained. No source author endorses this adaptation.

Derived from seven unmodified retained vertebral masks (six patients), source centroids and author previews. The builder independently recomputes all 145 full-occupancy centroids, voxel counts and volumes, both ordering screens and mask/centroid membership. Every one of 104100 sampled boundary voxel centres is inverse-mapped to its source label and checked for boundary membership and maximum 0.05 mm per-axis quantization error. Little-endian int16 values encode LPS millimetres times ten. No faces or connectivity. The 21 original source members and retained author method are hash-checked; historical code is never run.

Display rotation [L,S,-P] preserves handedness. Each patient's geometry retains its native physical frame. Separate displayed scans are independently placed and uniformly scaled, never registered or fused. 406 upper and lower overlap in three identities, so 145 instances are not independent subjects. The focused 406 view selects T9-T11 without changing their positions or shapes. No CT is embedded.

Source labels and curation decisions live separately in reference.json, revealed only for readers. This is not a blind solver packet or clinical adjudication. Source masks omit ribs/sacrum. 581 ambiguity, 406 upper C1 missing centroid, source omission policy, and differences in sampling remain unresolved qualification boundaries. Zero hard tasks admitted, zero model trials, no injected errors.

Rebuild with an existing NumPy/NiBabel environment: `python scripts/build_anatomy_curation_assets.py --root . --output NEW_DIRECTORY --license PATH_TO_CC_BY_SA_4_TEXT`.

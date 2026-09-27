# Mask-reasoning author screen

TotalSegmentator small v2.0.1, Wasserthal / University Hospital Basel. https://zenodo.org/records/10047263 . Data CC BY 4.0; labels Apache 2.0. Exact license bytes are retained. No source author endorses this view.

Source arrays are the unmodified retained original masks, not BR-004's planted defects. This builder independently recomputes all 24 family-order rows and all 131 organ predictions using the retained method, verifying every row against the BR-011 receipt. All eight arrays, taxonomy, author script and seven BR-010 trajectories are hash-checked. Historical authoring code is read as data and is never imported or executed.

The three views show case-32 left ribs, case-74 left ribs and case-32 organs. Boundary voxel centres are deterministically sampled up to 950 points/rib and 700/organ. Centroids use all occupancy voxels, not displayed samples. Source LPS millimetres and shared scale are retained within each scene. The proper display rotation is [L,S,-P]. Separate patients are independently fitted and are not registered. Points have no mesh faces; source occupancy remains authoritative. No CT is embedded.

reference.json holds author-only source labels and historical baseline predictions. Reader reveal is pedagogical; this bundle is not a blind solver packet. The ordering screen knows family membership and the label multiset. The organ baseline trains on seven other patients; prototype solvers do not receive those labeled examples. Source labels are not independent clinical or mask-only adjudication. The coverage exception is not a qualified hard task. I1/I3 remain proposals; no new model trial.

Rebuild using `uv run --no-sync python scripts/build_mask_screen_assets.py --root . --output NEW_DIRECTORY`. Existing NumPy is required. Never overwrite an accepted pack.

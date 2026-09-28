# CT-only context inference

Two native CTs were the only image inputs; no demographics, diagnosis, points, masks or earlier outputs were supplied. This pack derives four axial crops at the exact slices cited by the retained agent. Grayscale is the retained [-40,140] HU window, i increases right, j down, L/P/S array axes. Coordinates are zero-based voxels; affines map to RAS millimeters, not dates. Pixel decoding is checked exactly. No resampling or registration is performed.

Amber crosses show the agent's approximate liver evidence coordinates. Amber dashed boxes show the cited groin region. These are submitted evidence citations, not supplied hints, GT, segmentations or a diagnosis. Images precede the output and metadata reveals. Source views were visually inspected beside the original retained coordinate PNGs.

Output contains the exact nine structured field records. Seven unknowns and two inferences are not an accuracy fraction. Reader reference separates patient CSV age/sex/interval, cohort diagnosis/treatment/purpose and absent individual history. Source findings retain cohort provenance and limitations. No new external source review is claimed.

Reference diagnostics use the unchanged frozen validate function on saved output and temporary author variants. All-unknown and unsupported invented assertions both pass structure; inconsistent unknown/value and missing report fail. This demonstrates the declared mechanical boundary. Original model/oracle/no-op rewards remain unchanged. No model or clinical trial was run; schema validity does not measure accuracy or confidence calibration.

Rebuild with scripts/build_ct_context_assets.py into a fresh destination after scripts/audit_ct_context.py. Raw runs and generated media stay local. Source and reconstruction hashes are in manifest.json; retained clinical source terms are in DATA-LICENSE.txt.

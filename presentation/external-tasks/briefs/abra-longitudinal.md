# Compare two chest CT studies over time

Use a supplied longitudinal pair to answer metadata questions or locate a candidate new lesion. Keep date/count arithmetic separate from image interpretation and clinical adjudication.

> **Mixed illustration:** real NLST CT is available; no ABRA answer is retained and the reference viewer index is not mapped to a verified DICOM image. Acquire originals through the [official NLST source](https://www.cancerimagingarchive.net/collection/nlst/).

## Given

### Original data

The exact ABRA-selected participant **110494** baseline and follow-up series were recovered in full: baseline **1999-01-02, 161 CT images, B50f**; follow-up **2000-01-02, 162 CT images, B30f**. These are unregistered studies. The teaching pack samples **16 native slices per visit** at lung window center **−600 HU**, width **1500 HU**; the solver's viewer receives the original series, not this sampled teaching subset.

### Supplied helpers

Paired study and series UIDs, task prompt, OHIF/Orthanc viewer, metadata and image tools, `lung_window` and submission schemas. Pairing removes case search, but does not establish anatomical alignment, matched slices or lesion identity.

### Reference-only material

The pinned pair manifest contains expected arithmetic and a lesion point. Reader-only answers are **365 days** and **+1 CT image**; the single-lesion point is pixel **(262,355)** at zero-based viewer slice **23**. These are source references, not a retained agent answer or solver hints. The viewer adapter does not bind index 23 to a verified SOP image and display orientation, so the point appears only on an abstract pixel grid after reveal, never over a CT image.

## Task specification

The four source conditions are: determine the absolute interval between study dates; count signed follow-up minus baseline CT images; locate one candidate new lesion; or submit multiple candidate new lesions and then signal completion. Each visit must be inspected independently. Metadata differences alone do not identify a new lesion.

## Expected output

The two metadata tasks each require one integer. Image-localization tasks submit follow-up `new_lesion` point(s), with zero-based viewer `slice_index` and pixel x/y. Multiple-lesion submission ends with `submit_longitudinal_complete`. No agent answer, localization or score is retained; displayed answer fields remain empty.

## Evaluation

| Condition | Source scoring rule | Limit |
| --- | --- | --- |
| Date interval | Normalized exact/numeric comparison to expected days | Calendar arithmetic, not anatomy |
| CT image-count difference | Compare signed follow-up minus baseline count | Count arithmetic, not lesion change |
| One lesion | `point_distance_scorer`, 20-pixel distance threshold and near-slice penalty | Stored-point agreement is not radiologic proof |
| Multiple lesions | Greedy point matching within 20 pixels and five slices, minus 0.1 per false positive | No clinical sensitivity claim |

## Visual explanation

### Workflow

- Browse the actual native baseline and follow-up independently, keeping InstanceNumber, LPS z and spacing visible.
- Trace date/count lookup or image comparison to the corresponding empty answer schema.
- Reveal benchmark reference arithmetic or its abstract pixel-grid point, and retain the unresolved viewer-to-SOP boundary.

## Limits

Displayed sample positions and original InstanceNumbers are not OHIF viewer indices. Equal numeric LPS z or rail position is not matched anatomy: inspected same-z inputs showed baseline mid-lung and follow-up near-apical anatomy. No automatic correspondence, clinical newness, model prediction or score is inferred. Full-series hashes, successful acquisition and the retained first follow-up timeout are in the resolution receipt.

## Sources


- [Pinned ABRA tier-4 generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier4.py) and [pair manifest](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/data/annotations/nlst_longct_pairs.json).
- [Official NLST collection](https://www.cancerimagingarchive.net/collection/nlst/) supplies the exact native series under **CC BY 4.0**. The local resolution receipt pins both official downloads, SOP sets, native geometry, source hashes and the one transient follow-up connection timeout.
- A patient-image reference overlay requires an ABRA/OHIF read-only SOP-at-viewer-index-23 check plus display-axis verification. A claim that a lesion is genuinely new additionally requires justified cross-visit anatomical matching and qualified adjudication or a source annotation link. Neither check was performed here.

# AutoMedBench Lite multi-organ teaching assets

Native CT and five released reference masks: TotalSegmentator source s1366,
staged as TSG_00000001 by MitakaKuma/AutoMedBench-Lite-release at revision
8928073d5c3f3b842a4a4278d9b44f6e8ceaa9c5. CC BY 4.0 per pinned DATA_CARD.md.
Original dataset: Wasserthal et al., TotalSegmentator, via TotalSegmentator CT-Lite.
https://huggingface.co/datasets/YongchengYAO/TotalSegmentator-CT-Lite
https://zenodo.org/records/10047263
The audit verifies all six native files against retained published LFS hashes.

CT display: native coronal planes y144, y164 and y184, window -160 to 240 HU,
rounded 8-bit gray; transpose and reverse superior axis, no spatial resampling.
333 x 336 native pixels, 1.5 mm isotropic RAS. Right increases rightward and
superior upward. y164 was selected post hoc using kidney references. Neighboring
planes are reader navigation, not solver-supplied target locations.
Reference overlays use exact native y164 binary masks, constant per-structure
colors and alpha170/255. All five have nonempty intersections on this plane.
Overlays are hidden until the reader-reference chapter. The local collection has
five masks; the release CSV reports 78 present classes of 117. This is not a
complete reference set, model prediction or full-case segmentation score.

The label mapping is factual data extracted from TotalSegmentator 2.4.0,
commit 2e0c20058df8acb17acd54a7adf25bf7a0a33c90, and the pinned benchmark config.
Requirements allow later versions; verify the actual checkpoint label table.
No upstream executable code or model weights are included in this asset pack.
Source files were acquired through hf-mirror.com with matching revision headers
and Git blob ETags; provenance does not claim authenticated primary transport.

Seven author nonclinical fixtures use two synthetic 8x8x8 grids with eight voxels
each of labels42 and43 and 115 empty classes. Selected pinned format/scoring/
aggregation functions were replayed, not the controller, model, judge or sandbox.
All-117 empty-pair averaging contradicts the config's nonempty-reference wording.
Scorer missing-output omission is followed by completeness scaling in aggregation;
the medal remains assigned before that scaling. No clinical implication is made.

Rebuild: scripts/audit_automed_multiorgan.py then
scripts/build_automed_multiorgan_assets.py, each into a fresh local directory.

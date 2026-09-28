# ReX-MLE TopCoW CTA teaching assets

TopCoW 2024 CTA case012, source release https://zenodo.org/records/15692630.
Yang et al., Benchmarking the CoW with the TopCoW Challenge: Topology-Aware
Anatomical Segmentation of the Circle of Willis for CTA and MRA, arXiv:2312.17670.
Data owner: University Hospital of Zurich, Department of Neurology.
Non-commercial use with source attribution; commercial use needs owner permission.
The source License.txt is preserved as DATA-LICENSE.txt. No medical prediction or
model training is represented; these assets are a local teaching derivative.

The complete ZIP64 directory and the pinned ReX-MLE preparer establish 100 training
and 25 test cases when all 125 matched CTA pairs are supplied. Case012 is in the
ReX test subset, although its labels are public in the upstream challenge training
release. Its mask is therefore a held-out reader reference, never a solver helper.
Original source receipts and earlier preview images remain unchanged.

Native CT/mask: 266x371x311, spacing 0.498046875x0.498046875x0.5mm, LPS native axes
with an RAS physical affine. CT intensities are obtained through the NIfTI scaling.
PNG display clamps -100..700 HU to rounded 8-bit gray, transposes native x/y and
reverses displayed columns so right is rightward and anterior is upward.
Axial z108/118/128 are 5mm apart. z118 is chosen post hoc using the Acom reference.
All native pixels remain intact; this is not a blind search trajectory.

The source ROI x86:188,y113:178,z96:138 supplies a reader-only CoW crop at native
resolution 102x65. It appears only after reference reveal. The crop has its own
labeled magnification and does not imply new resolution. Full-volume labels can
extend beyond this ROI. Colors match all 13 named foreground IDs (1-12 and 15);
IDs 8 and 15 have zero occupancy in this annotation. Annotation absence is not an
independent clinical judgment. Alpha180/255 overlays retain exact source voxels.

Nonclinical 9x9x9 label fixtures explain selected Dice, binary clDice, B0 and
presence/IoU-based topology metrics. They are neither patient masks nor model
outputs. HD95 and the complete grader were not executed; MONAI is absent locally.
The source UInt8/CopyInformation preprocessing fragment and a leaderboard tie
fixture are separately identified. Dataset geometry requirements still apply.

Rebuild from scripts/audit_rex_topcow.py and scripts/build_rex_topcow_assets.py,
each into a new local destination. Source and fixture details remain in the audit.

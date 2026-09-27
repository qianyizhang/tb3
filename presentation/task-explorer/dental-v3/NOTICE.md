# Dental contract v3 reader assets

Local teaching derivatives of ToothFairy3 F_018/F_008 CBCT, permitted F008 example
annotation, two saved Astra-medium answers and private target research labels.
Source: [publisher](https://ditto.ing.unimore.it/toothfairy3/). Publisher
CC BY-NC-SA 4.0 is retained in DATA-LICENSE.txt; conflicting archive CC-BY-SA 4.0
metadata remains unresolved. No endorsement or public-redistribution decision.

Changes: native sections windowed at [-350,2200] HU, union crops, binary contours,
whole-tooth unions, saved-map sampling, bounded-refinement diagnostics and complete
canal silhouettes. Pixel centres round-trip exactly to native indices. Contours
round-trip exactly to binary pixel centres. Native plane axes increase right/up.
No submitted mask, source scan, clinical orientation or original score is changed.
The fixed RPI semantic convention is independent of retained target LPI and example
LPS headers. Physical laterality and original annotation conventions remain under review.

Separate source, output and reference files retain their different roles. Only the
assisted solver saw F008 annotation. Target GT, measurements and GT-selected crops
are reader-only reveals. Whole-volume scores must not be inferred from one section.
Contours absent in a section do not establish absence from the full volume.

The transfer comparison samples the saved composite target-to-example field at
k=55. Both 168,100-voxel atlas and warped-CT planes reproduce exactly. This is a
reader comparison of saved states, not registration optimization or a new trial.
Pulp eligibility reproduces the saved tooth-27 refinement crop. The old mask is
retained; additional voxels require tooth depth, proximity, intensity and contrast.
Eligibility is a search restriction, not a final mask or diagnosed tissue.
Canal 104's actual crop is prior bounds plus four voxels. None of its 355 target-GT
voxels lie inside that crop. Its six-voxel distance diagnostic is separate from the
canal algorithm. Geometry establishes this operation's reach, not a unique cause
of the earlier registration error or clinical adjudication of GT.

Canal projections collapse a complete axis using binary occupancy; they are not
CT sections, surfaces or voxel overlaps. Apparent silhouette overlap may arise at
different depths. Three projections and selected native slices must be labeled.
Main-canal 4 demonstrates improved overlap with worse HD95; no single measure
certifies its shape. Restoration/treated-pulp convention benefits remain untested.

Rebuild with the existing imaging environment:
`python scripts/build_dental_v3_assets.py --root . --output FRESH_DIRECTORY`.
The manifest pins all inputs, derivation code and assets. No solver or optimizer runs.

## Publisher-requested citations

Lumetti, L., Tan, Z. Q., Borghi, L., Addison, O., Li, Y., Rosati, G., van Nistelrooij, N., Vinayahalingam, S., Grana, C., & Bolelli, F. (2026). ToothFairy3: Scaling CBCT Maxillofacial Segmentation to 77 Classes with U-Mamba2. In Medical Image Computing and Computer Assisted Intervention – MICCAI 2026.

Bolelli, F., Marchesini, K., van Nistelrooij, N., Lumetti, L., Pipoli, V., Ficarra, E., Vinayahalingam, S., & Grana, C. (2025). Segmenting Maxillofacial Structures in CBCT Volume. In IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) (pp. 1–10). IEEE. https://dx.doi.org/10.1109/CVPR52734.2025.00494

Lumetti, L., Pipoli, V., Bolelli, F., Ficarra, E., & Grana, C. (2024). Enhancing Patch-Based Learning for the Segmentation of the Mandibular Canal. IEEE Access, 1–12. https://doi.org/10.1109/ACCESS.2024.3408629

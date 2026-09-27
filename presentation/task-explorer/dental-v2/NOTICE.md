# Dental contract v2 reader assets

Local teaching derivatives of ToothFairy3 F_002 and F_008 CBCT, the authorized
F008 example annotation, two unchanged Astra-medium outputs and private target
research labels. Source: [publisher](https://ditto.ing.unimore.it/toothfairy3/).
Publisher CC BY-NC-SA 4.0 is retained in DATA-LICENSE.txt. Archive CC-BY-SA 4.0
metadata conflicts with that notice; this derivation does not resolve the conflict
or authorize public redistribution. Raw data remain local. No endorsement is implied.

Changes: native sections windowed at [-400,3220], binary contours, selected crops,
saved-label union views, saved-displacement sampling, and one reconstructed prior
exclusion. All mask contours round-trip exactly to their binary pixel centres.
Pixel centres map invertibly to native indices; native plane axes increase right/up.
No native scan, submitted mask, clinical orientation or score is changed.
RPI specifies semantic names in this task; the retained LPS header does not
establish acquisition laterality. Source arrays and header geometry are verified.

The example annotation was visible only in the assisted condition. Target masks,
scores and reference-selected detail views are reader-only reveals. Separate JSON
files preserve these roles; reference data must be explicitly revealed by the story.
Whole-tooth contours union tooth tissue with its paired pulp; other views retain
exclusive labels. Omitted contours mean absent in that section, not the full volume.
Pulp contents shown as bright are observed intensities, not diagnosed materials.

Registration resamples only a selected plane with the saved target-to-example
field. Its nearest-neighbour labels reproduce the saved atlas exactly. The linear
CT overlay is a reader illustration of that map, not a new registration result.
Pulp clipping reconstructs the saved 3.5-voxel (1.05 mm) exclusion in its original
crop. It removes 440/443 correctly placed tooth-14 pulp voxels, leaving 3, while
also removing false positives. Counts are reference agreement, not clinical truth.
The selected section maximizes this measured loss; whole-volume counts and original
scores remain separately available. No optimization or solver is executed.

Rebuild using the existing imaging environment:
`python scripts/build_dental_v2_assets.py --root . --output FRESH_DIRECTORY`.
The manifest pins source evidence, derivation code and every asset.

## Publisher-requested citations

Lumetti, L., Tan, Z. Q., Borghi, L., Addison, O., Li, Y., Rosati, G., van Nistelrooij, N., Vinayahalingam, S., Grana, C., & Bolelli, F. (2026). ToothFairy3: Scaling CBCT Maxillofacial Segmentation to 77 Classes with U-Mamba2. In Medical Image Computing and Computer Assisted Intervention – MICCAI 2026.

Bolelli, F., Marchesini, K., van Nistelrooij, N., Lumetti, L., Pipoli, V., Ficarra, E., Vinayahalingam, S., & Grana, C. (2025). Segmenting Maxillofacial Structures in CBCT Volume. In IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) (pp. 1–10). IEEE. https://dx.doi.org/10.1109/CVPR52734.2025.00494

Lumetti, L., Pipoli, V., Bolelli, F., Ficarra, E., & Grana, C. (2024). Enhancing Patch-Based Learning for the Segmentation of the Mandibular Canal. IEEE Access, 1–12. https://doi.org/10.1109/ACCESS.2024.3408629

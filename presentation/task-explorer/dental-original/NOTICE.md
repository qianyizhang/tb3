# Original dental contract reader assets

Derived by the assistant from retained ToothFairy3 F_018 and F_002 native CBCT,
three unchanged Astra outputs and private research reference labels. Source:
[ToothFairy3 publisher](https://ditto.ing.unimore.it/toothfairy3/) and
[challenge](https://toothfairy3.grand-challenge.org/dataset/).
The publisher identifies CC BY-NC-SA 4.0; its exact standard license is retained
in DATA-LICENSE.txt. The archive metadata instead says CC-BY-SA 4.0. That conflict
is retained, not resolved by this derivation. Local teaching derivatives retain
the publisher's noncommercial and share-alike conditions. Raw data stay local;
no public redistribution or endorsement is claimed.

Changes: source-windowed PNG sections, native binary-mask boundary contours,
numeric label centroids, selected crops, retained scores and reproduced method
diagnostics. CT pixels use the fixed [-400,2500] window. Contours trace binary
level 0.5 with pixel-centre offset 0.5. No spatial resampling, patient-side repair,
mask editing or model inference is performed. Increasing plane axes map right/up;
native voxel indices are explicit because physical laterality is unadjudicated.
F018 archive/viewer arrays are equal but z-affines differ; each output uses the
exact solver/reference pairing. Shape/affine agreement is not clinical orientation.

Input sections contain CT only. Private references and scores are reader reveals.
Diagnostic crops and the selected tooth-16 pulp plane use post-submission reference
information. They are not solver assistance or exhaustive clinical inspection.
The label-swap operation changes displayed IDs only, never their geometry; it is
not a revised submission. The active-class denominator changes under the diagnostic.

The pulp view independently reconstructs distance, intensity and slice gates from
retained float32 CT and tooth-26 envelope. Reference tooth-16 pulp is paired only
for this diagnostic. Final pulp is the saved answer; later closing/cleanup is not
a nested gate. Counts measure reference retention, not precision or a validated fix.

Rebuild with the existing imaging environment:
`python scripts/build_dental_original_assets.py --root . --output FRESH_DIRECTORY`.
The source audit and manifest pin inputs, exact native geometry and PNG round trips.

## Publisher-requested citations

Lumetti, L., Tan, Z. Q., Borghi, L., Addison, O., Li, Y., Rosati, G., van Nistelrooij, N., Vinayahalingam, S., Grana, C., & Bolelli, F. (2026). ToothFairy3: Scaling CBCT Maxillofacial Segmentation to 77 Classes with U-Mamba2. In Medical Image Computing and Computer Assisted Intervention – MICCAI 2026.

Bolelli, F., Marchesini, K., van Nistelrooij, N., Lumetti, L., Pipoli, V., Ficarra, E., Vinayahalingam, S., & Grana, C. (2025). Segmenting Maxillofacial Structures in CBCT Volume. In IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) (pp. 1–10). IEEE. https://dx.doi.org/10.1109/CVPR52734.2025.00494

Lumetti, L., Pipoli, V., Bolelli, F., Ficarra, E., & Grana, C. (2024). Enhancing Patch-Based Learning for the Segmentation of the Mandibular Canal. IEEE Access, 1–12. https://doi.org/10.1109/ACCESS.2024.3408629

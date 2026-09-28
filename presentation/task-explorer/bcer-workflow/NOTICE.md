# BCER prostate workflow teaching assets

Three native acquired MRI planes from PI-CAI case 10001_1000001, Twilt et al.,
Zenodo record 6624726 v2.0, DOI 10.5281/zenodo.6624726. Images are CC BY-NC 4.0.
The three retained MHA arrays equal their prepared NIfTI arrays exactly; spacing,
origin and direction differ by less than 1e-5 from representation precision.
One native k=10 plane per sequence is shown, without registration or image
resampling. Display uses each whole volume's 1st/99.5th percentiles, rounded
to 8-bit gray. Native pixels are stretched uniformly to the displayed panel;
panel sizes differ in physical field of view and are not a common physical scale.
LPS physical-coordinate witnesses use header geometry only; matching headers
do not establish anatomical registration. White crosses are author ruler points,
not lesions. SVG positions add half a native pixel to address voxel centers.

Public BCER contract/template excerpts are pinned at
d10816712793a9e27f2e70640f9afc06f08a0c5c; BCER-LICENSE.txt retains its MIT terms.
The old locally authored lowercase modality manifest is preserved unchanged.
A fresh derived manifest replays selected canonical modality rules on prepared
filenames; it is a representative input example, not an official BCER split.
Filename-derived modality flags are not a scan-quality or metadata assessment.

Five author nonclinical validator fixtures use a one-voxel 8 x 8 x 8 grid,
empty/missing files, trivial CSV and JSON. They exercise selected pure functions,
not the controller or fault harness. No mask is placed over the patient images.
All displayed contract checks are public; there is no private reference reveal.
No BCER pipeline, medical tool, model, registration or segmentation was run.
No actual clinical outputs or ground truth are retained for this example.

Rebuild using scripts/audit_bcer_workflow.py and scripts/build_bcer_workflow_assets.py
into fresh local destinations. The source audit retains hashes, exact contracts,
selected-function digests, native geometry and all five check outcomes.

# Task Explorer preview image notices

Recorded 2026-09-21 for the accepted refinement pass. These are source-derived
illustrations, not new model outputs. The nine retained PNGs are exact copies of
already rendered local files. Their hashes, original locations, individual roles
and derivation details are in `manifest.json` beside this notice. The original
`samples.json` and `br030-visuals.json` receipts remain unchanged.

The notices below apply per named file. Preserve attribution, license links and
modification descriptions with redistributed copies. This collection includes
noncommercial material and material requiring permission for commercial use;
it has no blanket permissive license. Raw scans are not included. No attribution
implies endorsement. Source information below was checked against official
records or the explicitly identified retained provenance.

## ABRA example: abra-input.png and abra-reference.png

Source CT: Armato III, S. G., McLennan, G., Bidaut, L., and the LIDC-IDRI
contributors (2015), Data From LIDC-IDRI, The Cancer Imaging Archive.
Dataset DOI: https://doi.org/10.7937/K9/TCIA.2015.LO9QL9SX
Source: https://www.cancerimagingarchive.net/collection/lidc-idri/
Paper: https://doi.org/10.1118/1.3528204

Source annotation: Fedorov, A., Hancock, M., Clunie, D., Brochhausen, M., Bona,
J., Kirby, J., Freymann, J., Aerts, H. J. W. L., Kikinis, R., and Prior, F.
(2018), Standardized representation of the TCIA LIDC-IDRI annotations using DICOM.
Dataset DOI: https://doi.org/10.7937/TCIA.2018.h7umfurq
Source: https://www.cancerimagingarchive.net/analysis-result/dicom-lidc-idri-nodules/
Paper: https://doi.org/10.1002/mp.14445

Terms for both source datasets: Creative Commons Attribution 3.0,
https://creativecommons.org/licenses/by/3.0/ . Preserve the separate CT and
annotation attributions. TCIA data usage and publication citation requirements:
https://www.cancerimagingarchive.net/data-usage-policies-and-restrictions/ .
We acknowledge the National Cancer Institute and Foundation for the National
Institutes of Health for their critical role in creating the public LIDC-IDRI
database. Consult the collection's required acknowledgement for publications.

Derivation: LIDC-IDRI-0003, CT slice 66 in ascending physical Z; one released
DICOM SEG annotation, “Nodule 1 - Annotation 12”. The plane was selected after
inspection using the largest reference area. Window width 1500, center -600.
`abra-input.png` shows the native CT plane without a contour or target crop.
`abra-reference.png` adds that source reference and a reader-only crop at
[313, 292, 424, 403]. Series/SOP identity, geometry and reference alignment checks
are retained in the manifest. This is not a regenerated ABRA consensus task or
agent annotation. TB3 authored the PNG display and crop.

## AutoMedBench example: automed-tsg-input.png and automed-tsg-reference.png

Source: AutoMedBench Lite release contributors, packaged TotalSegmentator CT-Lite
case TSG_00000001 (upstream s1366), revision
8928073d5c3f3b842a4a4278d9b44f6e8ceaa9c5.
Data card: https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Lite-release/blob/8928073d5c3f3b842a4a4278d9b44f6e8ceaa9c5/DATA_CARD.md
Upstream mirror: https://huggingface.co/datasets/YongchengYAO/TotalSegmentator-CT-Lite
Attribution also to Wasserthal et al. and the TotalSegmentator contributors.

Terms: Creative Commons Attribution 4.0, as declared for this segmentation
track in the pinned data card: https://creativecommons.org/licenses/by/4.0/ .
This notice covers the CT and source masks, not other tracks in that release.

Derivation: coronal plane at array Y=164, selected after inspection using both
kidney references; HU window [-160, 240]; RAS+ display, R rightward and S upward.
`automed-tsg-input.png` shows the packaged CT. `automed-tsg-reference.png` adds
five released masks: left/right kidney, liver, spleen and aorta. These are five
of 117 possible classes, not a complete segmentation or an agent prediction.
TB3 authored the plane selection, display and overlay.

## BCER example: bcer-input.png

Source: Saha, A., Twilt, J. J., Bosma, J. S., van Ginneken, B., Yakar, D.,
Elschot, M., Veltman, J., Fütterer, J., de Rooij, M., and Huisman, H.,
The PI-CAI Challenge: Public Training and Development Dataset.
Dataset DOI and release: https://doi.org/10.5281/zenodo.6624726

Terms: Creative Commons Attribution-NonCommercial 4.0,
https://creativecommons.org/licenses/by-nc/4.0/ . This derived preview retains
that noncommercial restriction; it is not commercially cleared.

Derivation: PI-CAI case 10001_1000001, T2-weighted, ADC and high-b-value diffusion
sequences. T2 volume center and corresponding physical positions in the other
two sequences; per-image display percentiles 1 and 99.5. Geometry, display ranges
and original file hashes are retained in the manifest and sample receipt. TB3
authored the three-panel display. This is a compatible representative input,
not a recorded BCER processing run or evidence of diagnostic accuracy.

## ReX-MLE example: rexmle-input.png and rexmle-helpers.png

Source: TopCoW Challenge Organizers, TopCoW Training Data and External Testsets,
TopCoW2024_Data_Release, training case topcow_ct_012.
Dataset DOI: https://doi.org/10.5281/zenodo.15692630
Citation: Yang, K., Musio, F., Ma, Y., et al., The TopCoW Challenge —
Topology-Aware Circle of Willis Segmentation for CT and MR Angiography.
Paper: https://arxiv.org/abs/2312.17670

Terms recorded for this training release: open use with source attribution;
commercial use requires permission of the data owner. Preserve that restriction.
Source terms: https://zenodo.org/records/15692630 and
https://opendata.swiss/en/terms-of-use . This preview grants no commercial
permission. Terms for other ZIP archives in that release may differ.

Derivation: three axial CTA planes at canonical Z indices 102, 112 and 122;
window [0, 600] HU. The middle plane was selected using the maximum reference
cross-section; adjacent planes are ±5 mm away. R increases rightward, A upward.
`rexmle-input.png` shows CTA; `rexmle-helpers.png` adds released training labels.
TB3 authored plane selection, display and overlay. Prepared ReX-MLE split
membership remains unverified; these are upstream training examples.

## Internal vessel brief: br030-input.png and br030-helpers.png

CTA attribution: Xiaowei Xu and collaborators, ImageCAS, case 1.
Source: https://www.kaggle.com/datasets/xiaoweixumedicalai/imagecas
Paper: https://arxiv.org/abs/2211.01607
The retained BR-030 source receipt checked 2026-09-16 records the source listing's
Apache License 2.0 declaration: https://www.apache.org/licenses/LICENSE-2.0 .
The full official license is retained in `Apache-2.0.txt` beside this notice and
is directly included in this brief's Sources panel.

Supplied prediction attribution: Bransby et al., ImageCAS-X. Released CAS-Net
checkpoint and published full-volume preprocessing, mirroring and component
filtering; no artificial gaps or bridges were added.
Release: https://doi.org/10.5281/zenodo.21887809
Paper: https://arxiv.org/abs/2608.30404
Source declarations retained in BR-030: ImageCAS-X data CC BY 4.0,
https://creativecommons.org/licenses/by/4.0/ ; code MIT. Source code and weights
are not redistributed with these previews.

Derivation: coronal native slice at J=130 through the supplied review marker;
HU window [-100, 700] and physical-aspect display resampling. RAS X increases
rightward and Z upward. `br030-input.png` shows the source CTA.
`br030-helpers.png` overlays the unedited supplied prediction in green, the
supplied 8 mm editable sphere in gold and projected route anchors in blue.
TB3 authored these views. They read no scorer reference or agent output and do
not establish full 3D connectivity. Exact provenance remains in
`groups/tubular-anatomy/presentation/briefs/br030-visuals.json` and
`docs/evidence/br030-sources.json`.

The existing `coronary-cpr.png` post-run preview is retained separately under
`groups/tubular-anatomy/presentation/figures/`, with the ImageCAS / ImageCAS-X
attribution and terms recorded in `presentation/assets.json`. It is the
Terra package's curved coronary CT display after author distance-metadata
correction. The correction did not change CT sample values or the original
failed outcome; its display aspect is explanatory rather than a physical scale.

## Optional gap: imaging101-input.png and imaging101-reference.png

These two images remain local and optional. Pinned Imaging-101 asset metadata
at revision a9de559b54849a25988a8a0d8a5e869063a5a7a3 declares MIT, but the complete
copyright and permission notice has not been recovered. A bounded check of the
pinned dataset's LICENSE URL returned 404 on 2026-09-21. No holder or year has
been inferred. The complete notice must be recovered before promotion.
Source revision: https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3

Local previews show a synthetic 30-angle sinogram and the published phantom,
FBP and TV reconstruction arrays. They are reference examples, not new model
results. Their existing hashes and derivation are recorded under
`optional_local_only` in the manifest. A clean checkout shows an explicit
missing-preview message; building it does not download these files.

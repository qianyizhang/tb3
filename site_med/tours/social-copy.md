# Copy to accompany exported videos

## Tissue ownership

Can a coding agent spot tissue assigned to the wrong organ? In this controlled CT audit, 21.04 mL of pancreas was reassigned to the neighboring duodenum. Sol missed it in a broad audit and found it in a fresh, focused audit of the same data. One attempt per scope; this is a case study, not a clinical accuracy estimate.

Images derived from TotalSegmentator case s1233, CC BY 4.0. Original CT unchanged; organ-label edit and highlights by this workshop. Source: https://zenodo.org/records/6802614. Experiment: BR-017.

## Vessel to CPR

Terra repaired a real coronary-segmentation gap, traced a route and made curved CT views. It added 103 voxels without editing the surrounding mask. But the saved distance axis was 8.89 mm too long. The video uses an author metadata correction; the original agent trial remains a failure. One retained source-training case, not a clinical validation.

Derived from ImageCAS case 1 and ImageCAS-X. Retained source listings declare Apache 2.0 (ImageCAS) and CC BY 4.0 (ImageCAS-X). Sources: https://www.kaggle.com/datasets/xiaoweixumedicalai/imagecas and https://zenodo.org/records/21887809. Experiment: BR-030.

## Shape and motion

A moving heart shape is only part of the answer. Given 30 wall masks from a STRAUS simulation, Sol built a moving mesh with mean overlap 0.9461. Its local radial-strain error was 7.37 percentage points, above a separate 5-point research target. Matching the outline does not settle whether the material moves correctly. The twisting-cylinder example illustrates this ambiguity; it is not a proven account of the agent’s error.

Simulation-derived reference: STRAUS, https://humanheart-project.creatis.insa-lyon.fr/multimodalityStraus.html. No patient result is claimed. Masks-only condition, experiment BR-035. Keep the original source terms with the media; the local reproduction notes describe these derivatives.


## Match after a breath

Sol had to find eight corresponding points across breathing-phase CTs. A fresh attempt with full source depth switched from failed global registration methods to local matching, reducing RMS error from 12.73 to 2.60 mm. One point still exceeded the frozen 5 mm maximum; later visual acceptance did not rewrite that failure. Input information and strategy both changed, so this is not an isolated causal test of depth.

Learn2Reg LungCT 1.11, Hering, Murphy and van Ginneken, CC BY 4.0: https://doi.org/10.5281/zenodo.3835682. Independently centered author review crops. Experiment BR-028.

## Outside the scan, or overlooked?

For a cropped spine CT, Sol correctly reported that T4 was outside the scan. It also rejected T5, whose reference center remained visible. Correct abstention and complete localization are different requirements. This comparison uses one subject’s paired full/cropped views; Terra/high and Sol/xhigh differ in both model and reasoning effort.

VerSe-derived CT illustration, CC BY-SA 4.0; retain this attribution and license when sharing the derivative. Source notice and case-specific provenance are included in the local reproduction guide. Markers are projected; scoring used 3D distances. Experiment BR-040.

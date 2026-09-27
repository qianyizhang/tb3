# TopCoW source-screen teaching assets

Sources: TopCoW Challenge Organizers / Yang et al., Benchmarking the CoW with
the TopCoW Challenge, https://arxiv.org/abs/2312.17670,
https://zenodo.org/records/15692630. Retained training release License.txt is
copied byte for byte: attribution required; commercial use requires owner
permission. Source page rechecked 2026-09-27 and remains consistent with those
terms. Local author research views do not resolve commercial redistribution.

Node reference: Musio et al., Circle of Willis Centerline Graphs: A Dataset
and Baseline Algorithm, https://zenodo.org/records/17358162 (GRAPH-TERMS.txt).
Graph source page declares CC BY-NC without a version. Reference coordinates
and metrics are technical corroboration derived from the same source masks,
not independent anatomical truth. No complete VTP edge validation is claimed.

Changes: compact axial maximum-intensity projections through each provided CoW
bounding box; grayscale clipped at the MIP's 2nd/99.5th percentiles. The 007
native sequence uses its fixed ROI-intensity 2nd/99.5th window and all native
k slices covering the two annotated Pcoms plus a one-slice halo. No interpolated
anatomy, registration, inferred path or injected defect. The sequence is an
annotation-guided author inspection view, not a solver-visible crop contract.
Image and labels retain native sampling. Native axes are oblique and have L/P/S
orientation codes; i increases right and j decreases down on screen. NIfTI
physical coordinates use RAS+ mm. Full affines and slice pixel calibration are
retained; a MIP collapses depth and is not a single physical section.

Reference overlays: orange right Pcom (label8), teal left Pcom (label9), blue
other source vessel labels. Alpha160/255 over the image. These are annotations,
not predictions. Reader reference reveal is separate from images; node markers
are projected using the same native affine and ROI, never independently fitted.
Repeated shared-boundary node entries remain in statistics, not independent
measurements. Source labels say absent; clinical absence is not adjudicated.

output.json reproduces source-candidate status: no natural faulty prediction,
no admitted defect fixture and no model trial at the BR-025 curation close.
The proposed future solver receives MRA, a proposed binary mask and a broad
editable region, not these masks/graphs/edge answers. No GT-shaped corridor is
invented. Thresholds, prediction provenance and case adjudication remain open.
Later BR-026 synthetic feasibility is a separate contract and result.

All 30 selected source files are verified by size, SHA-256 and retained ZIP CRC;
12 screened MRA edge files are checked. Four source grids, Pcom counts,
26-connected label components/parent contacts and 146 node-entry nearest-foreground
distances are recomputed. Those checks neither validate all graph edges nor
resolve congenital absence, flow ambiguity, task difficulty or clinical safety.
Original curation receipt and source files remain unchanged.

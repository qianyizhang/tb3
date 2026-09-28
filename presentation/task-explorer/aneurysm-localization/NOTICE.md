# Native aneurysm localization teaching views

Source: Lausanne TOF-MRA cohort, OpenNeuro ds003949, CC0.
Credit: Di Noto et al., *Towards automated brain aneurysm detection in TOF-MRA:
open data, weak labels, and anatomical knowledge*, Neuroinformatics (2022),
https://doi.org/10.1007/s12021-022-09597-0 .
Pinned dataset tree: 8921f7b9beab038e1a314f9aab84d7358c4568c5.
Exact selected image/mask bytes, original task freezes, receipts and trajectories
are verified in the group's aneurysm-audit.json. No inference runs here.

The solver received full native original/skull-stripped MRA volumes, metadata,
three full-volume MIPs and twelve equal axial slabs, plus a slice/MIP helper.
Source case identifiers, weak lesion masks and acceptance regions were not in
the image archive. The public dataset was identified in a supplied source notice,
and network lookup was allowed. N03 used it; retain that separate evidence basis.

PNG images preserve exactly the windowed uint8 values. Arrays are transposed and
vertically flipped, so horizontal follows the first remaining native axis and
vertical points upward along the second: +i Right, +j Anterior, +k Superior.
Native anisotropic spacing determines displayed physical aspect. There is no
resampling, registration or radiological left-right reversal. Bounds are half-open.
Pixel centre (u+.5,v+.5) maps to the stated original [i,j,k]. MIPs collapse depth;
they are not single sections and do not establish localization by themselves.

N02 candidate sections reconstruct a selected subset of step 14, using the exact
crop and display window; they are not the original full montage. The depth series
uses actual slices. Point-centred sections are post-result reader views. N01
reference-centred crops are post-hoc teaching aids; its final candidate sections
are selected from step 28 and were viewed at step 29. N03 centre sections are
neutral display choices, not evidence of an exhaustive negative scan review.

The reference file is separate and revealed explicitly. It contains released
weak regions and frozen +1 mm Euclidean voxel-centre acceptance regions, not
clinical sac boundaries. Rasterizing all contour rings reconstructs each binary
plane exactly. The submitted point is cyan; weak region green dashed; acceptance
region gold dotted. The source weak sphere's centre is not the required answer.
No point or region is interpolated between slices. No mesh is reconstructed.

Nine saved grades replay exactly, including three model answers, three oracle
answers and three invalid-schema no-ops. The earlier missing-verifier setup failure
remains an infrastructure observation. Empty valid negative and {} are distinct.
One point per reference region is matched at most once; extras and misses fail.

These three selected cases provide workflow observations. They do not measure
population accuracy, causal method benefit, lesion contour quality or clinical
diagnostic validity. Source completeness, independent clinical review and unknown
training overlap remain qualifications. Raw frozen evidence is unchanged.

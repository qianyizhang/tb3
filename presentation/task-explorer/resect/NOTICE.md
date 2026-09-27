# RESECT correspondence teaching assets

Images and paired landmarks: Xiao et al., RESECT (2017),
<https://doi.org/10.1002/mp.12268>, CC BY 4.0 (DATA-LICENSE.txt).
Data archive: <https://doi.org/10.11582/2017.00004>.
The original article instead cites 10.11582/2016.00003; both identifiers are retained.

Tumor masks: Behboodi et al., RESECT-SEG (2024),
<https://doi.org/10.1002/mp.17317>, <https://osf.io/jv8bk>,
CC BY-NC-SA 4.0 (LABEL-LICENSE.txt). Combined mask-overlay views and exports
containing them follow CC BY-NC-SA 4.0. Image/landmark-only derivatives remain CC BY 4.0.
Acquisition: MedOtter/RESECT-SEG revision e86fb37dd93f7a9c64e48952f71410af59b04b9b;
15 retained files are verified against the original sample manifest, not fetched anew.
<https://huggingface.co/datasets/MedOtter/RESECT-SEG/tree/e86fb37dd93f7a9c64e48952f71410af59b04b9b>.

Changes: compact query-centred sections, grayscale clipping at each volume's
positive-intensity 1st/99th percentiles, transparent missing coverage, mask tint,
coordinate conversion and no-op distances. Linear image interpolation; nearest
mask interpolation. Native previews fit complete sections to 160 pixels;
RAS views span 48 mm at 0.5 mm sampling. No registration was estimated.
All pixel centres carry origin/dx/dy calibration in NIfTI RAS+ millimetres.
The axial sweep moves the inspection plane, never anatomy or a predicted point.
US masks use valid qform geometry; all eight corner positions agree with the
image sform within 0.0001 mm. Source geometry is not rewritten.

geometry.json contains MRI queries and same-world US initial candidates.
helpers.json contains optional tumor masks, withheld in the base condition.
reference.json contains manual US destinations and source-characterization
errors, revealed only in the reader view. These are browser presentation
boundaries, not security or solver-isolation guarantees. The teaching queries
were selected after inspecting paired masks and tags. They are not a blinded
sample. The older independently GT-centred figures are retained separately.
This proposed three-case, single-query, voxel-output contract is not frozen.
The separate two-query world-output pilot is not an outcome of this proposal.
Public training-set exposure and a strong shared-frame no-op limit difficulty claims.

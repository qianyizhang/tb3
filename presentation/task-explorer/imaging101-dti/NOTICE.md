# Diffusion tensor MRI source views

Benchmark revision: `dc2f668939b21e8312e22529615def610f8611df`.
Dataset revision: `a9de559b54849a25988a8a0d8a5e869063a5a7a3`.
The [source audit](../../external-tasks/sources/imaging101-dti-audit.json)
retains all source/asset identities, numerical controls and evaluator limits.

All images retain the 128x128 native grid with 8-bit grayscale quantization.
No image is cropped or spatially resampled. Signals 0,18,16,1 are b0 and the
available gradients closest to the absolute x/y/z axes. All use 0..1.15 a.u.;
FA uses 0..1, MD uses 0..3.5 in 10^-3 mm^2/s. Error scales cover both methods'
full retained range, rounded upward to 0.05; no clipping at notebook limits.
Excluded tissue-mask pixels are transparent in scalar maps; they are not
missing measurements. PNG ranges and quantization errors are recorded per image.

Image columns increase rightward and rows downward. Tensor x/y/z are source
coordinate axes; no patient/anatomical orientation affine is supplied. Five
fixed pixels were selected post-hoc, one per distinct truth tensor; they are not
a random evaluation sample or a new localization result. Exact native signal
values and audited fixed-pixel fits remain numerical records beside the images.
The source truth mask is supplied at all levels and may be shown as a helper.

Tensor glyphs are orthographic projections of V diag(lambda) u for unit u.
Axis lengths are eigenvalues in 10^-3 mm^2/s, not anatomical displacement or
fiber tracts. Saved OLS/WLS tensors determine the visible glyphs. Truth glyphs,
FA/MD maps and error maps live in reference.json and require a reader reveal.
Eigenvector sign is arbitrary, and isotropic truth has no unique principal axis.

The source rotation maps z to its declared direction while the largest
eigenvalue belongs to its first column. Stored anisotropic tensors therefore
disagree with those declared directions; render their actual values. Notebook
gray-matter and CSF probe labels also disagree with their stored tensor/mask.
No source arrays, labels, original scores or old receipts are rewritten.

Actual L1-L3 seeding exposes all truth and the tissue mask. The reader gate is
not solver privacy. The custom score checks only masked FA, preferring OLS when
both native files exist. Generic local scoring selects FA for scalar maps,
including MD, and uses the full grid; tensor-shaped outputs select tensor truth.
The no-workspace fallback requires absent NPY truth. Published thresholds are
absent; notebook values remain historical. No model, generator or full-image
fit runs in this pack or in its derivation.

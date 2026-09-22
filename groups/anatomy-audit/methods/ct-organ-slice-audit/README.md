# CT organ slice construction audit

Post-submission analysis of four frozen conditions. See the
[finding](../../findings/ct-organ-slice-construction-audit.md) for definitions,
measures, limits and source task. No model, tool inference or historical authoring
script runs. Requires existing NumPy, SciPy, NiBabel, scikit-image and Matplotlib;
the local check used `.venv-br030/bin/python`. This is a dependency locator, not
an environment portability claim.

From the repository root, choose a **fresh** output directory:

```sh
OPENBLAS_NUM_THREADS=1 .venv-br030/bin/python \
  groups/anatomy-audit/methods/ct-organ-slice-audit/analyze.py \
  --root . --output .local/NEW-ct-slice-audit
.venv-br030/bin/python groups/anatomy-audit/methods/ct-organ-slice-audit/trace_views.py \
  --root . --analysis .local/NEW-ct-slice-audit
MPLCONFIGDIR=/private/tmp/ct-organ-slice-mpl .venv-br030/bin/python \
  groups/anatomy-audit/methods/ct-organ-slice-audit/render.py \
  --analysis .local/NEW-ct-slice-audit
.venv-br030/bin/python groups/anatomy-audit/methods/ct-organ-slice-audit/revision_quality.py \
  --root . --analysis .local/NEW-ct-slice-audit
```

`analyze.py` refuses an existing output directory. The three follow-up commands
write their named derived outputs inside that newly created directory. They never
write to the original attempts. Frozen paths are explicit in the analysis source;
missing original inputs are errors, not empty/zero evidence. Large arrays, traces,
per-slice rows and figures stay local. The compact evidence records their hashes.

`metrics.json` contains per-organ provenance strata, raw and final scores, matched
baseline-defined slice sets and distance-to-anchor diagnostics. `slices.json`
retains every scored organ–slice row. `views.json` links successful displays to
trace step, rendered path, coordinate list and render provenance; failed requests
are counted separately. `revision-quality.json` scores net polygon changes at the
same slice indices and separately lists added/removed indices. The construction
and quality figures have explicit color/symbol legends.

Raw scores inside a final-support stratum use that same stratum. Whole-volume raw
scores instead include all raw or GT foreground, including planes later trimmed
away. This distinction prevents post-processing from silently removing raw false
positives from stage evaluation. All final scores reproduce the original verifier,
and raw xhigh scores reproduce the prior independent methodology audit.

Sol's duodenum remains a separate ellipsoid class. Multipart organs are classified
as explicit if any part has an anchor at that plane. LiteMedSAM prompt interpolation
never means mask interpolation. Repeat batches mean different batch directories;
multiple boxes for different parts in one batch are not temporal revisions.
These definitions describe observable operations, not hidden attention or reasoning.

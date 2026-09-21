# BR-042 final report and interactive showcase

A technical ML/research retrospective of image-only all-vessel discovery and labeling.
The report distinguishes six fresh attempts from seven saved outputs, completed
from partial runs, common re-evaluation from original scores, and coronary scoring
from broader anatomical scope. No new model trial is launched by this package.

The current local build is `runs/br042-showcase-20260921-final/` (untracked), with:

- `index.html`: portable interactive CTA, all seven saved outputs, metric controls,
  per-category scores, methods, candidate-filter diagnostics and resume chronology.
- `report.html` / `report.md`: full technical report with static visual fallbacks.
- `data.json` / `manifest.json`: exact numerical metrics, source paths and SHA-256.
- `sources/`: exact original answers, method reports, frozen scorer/instruction,
  evaluation and investigation receipts, and source/license notices.
- `qa.json` and PNGs: browser checks and actual rendered views.

Open `index.html` directly in a current browser, or serve the directory over
loopback. All interactive assets are embedded; source-document links require the
adjacent files. Keep the full folder or ZIP together when sharing. The CTA remains
at native spatial resolution; its portable display cache has a fixed HU window
and 8-bit intensity quantization. It is not a quantitative HU export.

## Suggested four-minute demonstration

1. Explain the input boundary: full CTA, no seeds/mask/known vessel list. Inspect
   the default input-only native planes before revealing either overlay.
2. Select V3 Astra/medium, reveal model and reference. Compare its substantial
   geometry with Sol/xhigh under the same protocol. Orange is submitted geometry;
   cyan is reference, never a correctness color.
3. Toggle result weighting from reference length to equal-category mean. Explain
   why 95.5% overall geometry can still fail complete-tree recovery.
4. Select the resumed output and use the explicitly reference-assisted D2 and OM1
   focus buttons. Move native slices. Read the candidate-stage diagnostic: D2
   survives filters then is withheld; OM1 is dropped by the gates. Lowering the
   threshold is a sensitivity test, not a demonstrated improvement.
5. Close with the unchanged coronary specifications after resume, the bounded
   PDA naming dispute, and the proposed changes to candidate review and filtering.

## Rebuild and verify

Run from the repository root using existing installed dependencies. The builder
refuses to overwrite an existing output directory and reads historical files
without executing their preparation or extraction modules.

```sh
.venv-br030/bin/python groups/tubular-anatomy/presentation/br042/build.py --output runs/br042-showcase-NEW
.venv-medical/bin/python -m http.server 8805 --bind 127.0.0.1 --directory runs/br042-showcase-NEW
node groups/tubular-anatomy/presentation/br042/qa.cjs runs/br042-showcase-NEW http://127.0.0.1:8805/
```

The final command uses the installed Playwright package and Google Chrome in an
isolated headless profile; it installs nothing. It verifies native-cache bytes,
all packaged hashes, input-only defaults, metric transformations, linked native
coordinates, all saved answer links, threshold diagnostics, mobile layout and
JavaScript errors. It also generates the static images referenced by the report.
The report's static image links become available when this validation completes.

`build.py`, `index.html`, `style.css` and `app.js` are presentation source;
`report.md` is the authored narrative with retained frozen result values.
Generated images, CTA data, source copies and reports stay in ignored `runs/`.
Original answers, task bytes and scores are never rewritten.

## Evidence boundary

The score is a 1 mm coronary reference-recall measurement; it does not establish
all-vessel precision, anatomical correctness, topology or clinical completeness.
One public development case and mostly single attempts cannot establish general
model superiority or causal test-time-compute scaling. Clinical/reference naming
disputes remain under review. Recommendations are assistant proposals, not new
user-authorized trials.

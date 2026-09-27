# Native named-landmark teaching assets

Actual retained inputs: PDDCA 1.4.1 subject 0522c0001, AFIDs SNSX sub-C001 and
VerSe sub-verse823. No model calls or new scans. Source hashes are in the manifest.

- VerSe CT and derived sections/points: CC BY-SA 4.0, Sekuboyina et al. and Liebl
  et al.; [source](https://github.com/anjany/verse#license). The included terms
  apply to these derivatives.
- AFIDs MRI and released fiducials: CC0-1.0 at OpenNeuro ds004470 revision
  53f2c2caecf346b620971a5dd4672ca538441ede. Retain acknowledgements to Lau et al.
  and Taha et al.; [source](https://openneuro.org/datasets/ds004470).
  This corrects older CC BY labels; original experiment receipts are preserved.
- PDDCA: public-domain database, Gregory C. Sharp and collaborators;
  [source and release](https://www.imagenglab.com/newsite/pddca/),
  Raudaschl et al., Medical Physics 2017. No CC license is invented for this source.

The manifest's LicenseRef names this mixture, not a replacement license. Source
records and verified terms live in the owning group's presentation/sources folder.

`source.json` contains native sections, affines, query names and display mappings.
Input sections are native midline views; later diagnostic views are explicitly
reference-selected. PNG row/column increase along the recorded native axes. The
viewer preserves physical aspect and prints signed point offsets from each plane.
Images use a fixed intensity window, nearest native samples and optional stride 2;
scoring uses original native coordinates, never these display pixels.

`output.json` contains saved submitted points/statuses, not a solver trajectory.
`reference.json` holds private evaluation points and grades behind a reader reveal.
All visible-target denominators include misses. A point projected onto a section
need not lie in that plane. The full/cropped CT reuses one subject; no atlas image
or unretained registration intermediate is synthesized. MRI atlas assistance,
source uncertainty and the original runtime atlas recovery gap remain explicit.

Rebuild with the existing imaging environment:

```sh
.venv-br033/bin/python -B scripts/build_named_landmark_assets.py --out .local/NEW-LANDMARK-ASSETS
```

The read-only source audit must pass first. Generated story/video outputs stay local.

# Read-only dental trace audit

See [the finding](../../findings/dental-trace-root-causes.md) for interpretation.
This method reads the three retained dental attempts. It never imports or runs
their scripts, rewrites outputs, installs dependencies, starts models or applies
the publisher's orientation conversion.

Required installed libraries: numpy, nibabel, scipy and matplotlib. Local check
on 2026-09-21 used the existing `.venv-br037/bin/python`. This environment's name
is an operational locator, not a maintained portable runtime or fresh install
claim. The scripts accept an explicit repository root; raw artifacts must exist
at the paths in their retained evidence receipt. They refuse an existing result
file; choose a fresh destination for another replay.

```sh
MPLCONFIGDIR=/private/tmp/dental-trace-mpl .venv-br037/bin/python \
  groups/anatomy-audit/methods/dental-trace-audit/analyze.py \
  --repo /Users/zhangqy/pkgs/tb3 --out /private/tmp/NEW-dental-trace-audit

.venv-br037/bin/python groups/anatomy-audit/methods/dental-trace-audit/pulp_gates.py \
  --repo /Users/zhangqy/pkgs/tb3 --output /private/tmp/NEW-dental-pulp-gates.json
```

`analyze.py` rebuilds confusion matrices directly from unchanged prediction/GT
arrays, checks every per-label frozen Dice and foreground metric, applies one
predefined anatomical L/R ID permutation, and groups the residual errors. It
also computes optimistic whole-tooth matching with pulp merged, using maximum
total Dice one-to-one assignment and zeros for unmatched objects. Neither is an
accepted replacement score. No spatial resampling or best spatial registration
is applied. The trace index extracts observable messages and tool-call metadata;
it excludes hidden reasoning and inline image payloads.

`pulp_gates.py` reads F002's saved intermediate tooth envelope and CT, reproduces
only the explicit distance/intensity/slice gates as reviewer measurements, and
counts reference voxels retained. GT is paired to opposing tooth IDs for that
diagnostic only. The final overlap is measured directly from the unchanged
submitted NIfTI. These are reference-overlap counts, not proof of clinically
correct pulp or that relaxing the gate would improve precision.

Generated outputs remain local under `.local/dental-trace-audit-20260921/analysis/`.
Original input/code/output hashes are checked before and after analysis. Four
figures were visually inspected. All original Dice values reproduced to 1e-12;
per-label and foreground values matched exactly. No new model ran.

Source-specific orientation remains unresolved. The official conversion script
was retained under `.local/dental-trace-audit-20260921/sources/` and inspected
without execution. Its downloaded bytes and URL are included in the finding's
evidence receipt. It is not vendored into this method.

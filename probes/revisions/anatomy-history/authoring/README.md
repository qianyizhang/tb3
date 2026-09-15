# Anatomy experiment retrospective

[Presentation and verdict](../../../../docs/anatomy-experiments.md) ·
[Trace analysis](../../../../docs/anatomy-traces.md) ·
[Visual report](../../../../runs/anatomy-history-presentation/index.html)

Seven completed Sol/xhigh trials and one conditional Terra/max follow-up from
BR-013/014/015. This retrospective adds no model trials and changes no frozen
input, answer or grade.

- `analysis.json` owns the authored stage summaries, public-message excerpts,
  pseudocode, interpretations and selected image/step references.
- `present.py` verifies frozen files, result/answer/trajectory hashes and public
  excerpts, then decodes exact returned image payloads and builds the report.
- `presentation.html` owns report structure and interactions. It reuses BR-017's
  CSS at build time; the generated HTML embeds all styles, scripts and images.

From the workshop root with the retained Python 3.12 environment:

```sh
.venv-br003/bin/python probes/revisions/anatomy-history/authoring/present.py
```

Outputs are `runs/anatomy-history-presentation/index.html`, `docs/anatomy-traces.md`
and `docs/evidence/anatomy-trace-index.json`. Raw sessions and images remain
ignored under `runs/`; only small source-linked authored records are committed.
The builder requires the original local raw runs. It records, rather than
removing, unmanifested Python bytecode caches beside otherwise unchanged frozen
files. Unexpected extra files or changed frozen bytes stop the build.

Open the HTML directly for offline use. If serving from localhost, serve the
workshop root so relative report/evidence links resolve. Data-derived figures
retain the TotalSegmentator/ColonVessels CC BY 4.0 attribution in the report.

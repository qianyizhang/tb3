# Finding a hard task with coding agents

An AI-assisted investigation for a job-interview take-home assignment:
**design and evaluate compact Terminal-Bench 3 tasks, then explain what the
results actually establish.**

**[Read the interactive research report](docs/report.html)** — the evolving
research story, current findings, experiment presentations and lessons.
Open `docs/report.html` locally; GitHub displays HTML source.

## Current findings

| Experiment | Observation | Current interpretation |
| --- | --- | --- |
| **BR-017 · Tissue ownership** | Sol missed a 21.04 mL pancreatic inclusion in a broad CT audit; the same data passed under focused scope | Primary anatomy lead; failure is scope-specific and repeatability is unproven |
| BR-013–015 · Anatomical identity | Sol and Terra misidentified a compact pancreas; Sol passed with inventory, CT or proposed-name context | Secondary diagnostic; added context weakens the promotion case |
| BR-016 · Aneurysm localization | One reference-label miss, one image-based localization, one source-assisted pass | Separate imaging pilot; no clinical-accuracy or general failure-rate claim |

The original case-32 kidney-boundary misses remain historical evidence. A later
reassessment paused their promotion over task-validity concerns; the clean
case-32 package is a historical handoff, not the current anatomy recommendation.
**No robust, repeatable Sol-failure task is established yet.**

## Read progressively

1. [Research overview](docs/report.html): findings, milestones and interview discussion.
2. Detailed reports: [anatomical identity](docs/anatomy-experiments.md),
   [tissue ownership](docs/research-rounds/BR-017-results.md),
   [aneurysm localization](docs/research-rounds/BR-016-results.md).
3. [Evidence archive](docs/archive.md): original protocols, traces and frozen results.

The overview links cohesive versions of the three existing interactive
presentations. With their retained local assets, prepare and serve them using:

```sh
python3 scripts/build_interview_presentations.py
python3 -m http.server 8767 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8767/docs/report.html`.
[Reproduction and availability](docs/reproduce.md) ·
[Original assignment](docs/task.md) ·
[Historical submission handoff](docs/submission.md).

Agent assistance was used extensively for research, code, trials, analysis and
presentation. This report update launches no new experiments. Unfinished
preparation is separate from completed results; raw evidence remains local.

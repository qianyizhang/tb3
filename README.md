# Finding a hard task with coding agents

An AI-assisted research workshop for a job-interview take-home assignment:
**investigate, design and evaluate a compact Terminal-Bench 3 task.**

The selected candidate is a **DICOM anatomical annotation audit**. A model
inspects one CT scan and its segmentation, then reports incorrect labels and
locations in a JSON file. In the original frozen case, Terra/max and Sol/xhigh
both completed normally but missed a small connected kidney-mask error.
These development-selected pilot observations support the candidate; they do
not establish a failure rate or full TB3 qualification.

## Read the story

**[Final report — research journey, results and lessons](docs/report.html)**

Open the HTML file in a browser for the interactive report. GitHub displays its
source; to read locally, clone this repo and open `docs/report.html`. It works
offline, with expandable milestones, trial evidence and a visual explanation.

| Start here | What it answers |
| --- | --- |
| [Selected task and submission handoff](docs/submission.md) | What was selected, where the clean package lives, and how pilot evidence differs from qualification |
| [Research archive](docs/archive.md) | Original rounds, reviews, frozen tasks and evidence |
| [Reproduction guide](docs/reproduce.md) | How to inspect records and run repository checks |
| [Original assignment](docs/task.md) | What the take-home asked for |

## The result in brief

| Original case 32 | Outcome | Agent time | Output tokens |
| --- | --- | ---: | ---: |
| Terra / max | Reviewed miss | 10.21 min | 23,713 |
| Sol / xhigh | Reviewed miss | 12.60 min | 20,930 |

Both submitted valid empty reports after viewing the affected kidney region.
Matching controls and independent re-scoring support the observed misses;
the traces do not isolate perception, attention or inspection strategy as the
cause. [Reviewed comparison](catalog/analyses/br004-sol-followup.md).

The research also records solved candidates, source-label uncertainty and
verifier defects. The most useful lesson was to distinguish **a difficult
problem, a fair task and a trustworthy failure**—and verify each separately.

**Research is closed.** Unexecuted ideas are possible follow-up work in the
report. The clean submission is maintained separately. This workshop preserves
the investigation; its offline checks do not certify the submission.

Agent assistance was used extensively for research, implementation, execution,
analysis and this presentation. The report makes that workflow explicit.

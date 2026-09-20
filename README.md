# tb3-medical

A research workbench for understanding what agents can do with medical images.
Semantic groups keep questions, decisions, data sources, experiments, evidence
reviews and visual explanations together. Capability learning is primary;
submission qualification is a separate promotion step.

```sh
python3.12 scripts/med present --serve --local-media
# Open http://127.0.0.1:8765
```

The read-only index searches prior work and decisions. It includes portable
stories and figures; existing local data enables guided image and geometry tours.
A clean checkout needs only Python 3.12. No command above downloads data or runs
a model. To create a portable static build: `python3.12 scripts/med present`.

| Group | Question |
| --- | --- |
| [Anatomy audit](groups/anatomy-audit/README.md) | Does the anatomy match the segmentation and its labels? |
| [Lesion localization](groups/lesion-localization/README.md) | Can the agent find a focal abnormality and justify it spatially? |
| [Registration](groups/registration/README.md) | Which correspondences survive motion and changed context? |
| [Tubular anatomy](groups/tubular-anatomy/README.md) | Can it recover connected paths, identify branches and construct curved views? |
| [Cardiac motion](groups/cardiac-motion/README.md) | Can geometry and motion support independently checked mechanical estimates? |
| [Anatomical landmarks](groups/anatomical-landmarks/README.md) | Can it name, localize and abstain on unavailable anatomy? |
| [Longitudinal reading](groups/longitudinal-reading/README.md) | Can it compare visits with reproducible measurements and qualified interpretation? |

```sh
python3.12 scripts/med list 'atlas'
python3.12 scripts/med show anatomical-landmarks-br040
python3.12 scripts/med validate
make check PYTHON=python3.12
```

Read [the workflow](docs/workflow.md) for idea capture, decisions, scaffolding,
freeze/plan/run/collect, validity issues and clean exports. [Contribution rules](CONTRIBUTING.md)
cover concurrent ownership and milestone checks. Findings are source-linked and
qualified; historical success is not clinical readiness or a new task's score.

[Exact MRI export recipe](exports/recipes/landmarks-mri-exact.json) demonstrates
independent saved-output replay. It requires selected local artifacts with
recorded hashes. It emits a draft into a fresh destination; the separately owned
[existing submission](docs/submission.md) is never overwritten.

Early nonmedical work and superseded interfaces are recoverable through the
[archive](archive/README.md). Retained medical probes and round documents keep
original bytes and provenance; new work belongs in groups. Runtime runs and
external environments stay local. The local directory and remote repository
name remain unchanged while concurrent work depends on them.

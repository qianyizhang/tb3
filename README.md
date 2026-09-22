# tb3-medical

A research workbench for understanding what agents can do with medical images.
Semantic groups keep questions, decisions, data sources, experiments, evidence
reviews and visual explanations together. Capability learning is primary;
submission qualification is a separate promotion step.

```sh
uv sync --locked --inexact --group dev
npm ci
npm run frontend:build
uv run med present --serve --local-media
# Open http://127.0.0.1:8765
```

The read-only index searches prior work and decisions. It includes portable
stories and figures; existing local data enables guided image and geometry tours.
Set up with Python 3.12 and `uv sync --locked --inexact --group dev`. The inexact
sync preserves separately installed research packages while keeping declared
versions locked. No command above downloads data or runs a model. To create a
portable static build: `uv run med present`.

Find task definitions by [capability, modality and research role](docs/task-taxonomy.md)
in the Task Explorer (`uv run med brief build`). The groups below own research;
their membership does not classify every child experiment as the same task.

| Research group | Question |
| --- | --- |
| [Anatomical labeling](groups/anatomy-audit/README.md) | Can agents construct and check anatomical labels from images or supplied objects? |
| [Lesion localization](groups/lesion-localization/README.md) | Can the agent find a focal abnormality and justify it spatially? |
| [Registration](groups/registration/README.md) | Which correspondences survive motion and changed context? |
| [Tubular anatomy](groups/tubular-anatomy/README.md) | Can it recover connected paths, identify branches and construct curved views? |
| [Cardiac motion](groups/cardiac-motion/README.md) | Can geometry and motion support independently checked mechanical estimates? |
| [Anatomical landmarks](groups/anatomical-landmarks/README.md) | Can it name, localize and abstain on unavailable anatomy? |
| [Longitudinal reading](groups/longitudinal-reading/README.md) | Can it compare visits with reproducible measurements and qualified interpretation? |

```sh
uv run med list 'atlas'
uv run med show anatomical-landmarks-br040
uv run med check
make check
```

Start with [the documentation index](docs/README.md). For development, see the
[architecture](docs/architecture.md) and [file-placement guide](docs/repository-layout.md). Read
[the workflow](docs/workflow.md) for idea capture, decisions, scaffolding,
automatic run receipts, collection, scoped review and clean exports. [Contribution rules](CONTRIBUTING.md)
cover concurrent ownership and milestone checks. Findings are source-linked and
qualified; historical success is not clinical readiness or a new task's score.

[MRI export recipe](exports/recipes/landmarks-mri-v2.json) demonstrates
independent saved-output replay. It requires selected local artifacts with
recorded hashes. It emits a draft into a fresh destination; the separately owned
[existing submission](docs/submission.md) is never overwritten.

Early nonmedical work and superseded interfaces are recoverable through the
[archive](archive/README.md). Retained medical probes and round documents keep
original bytes and provenance; new work belongs in groups. Runtime runs and
external environments stay local. The local directory and remote repository
name remain unchanged while concurrent work depends on them.

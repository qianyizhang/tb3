# Task taxonomy

Browse work by its requested deliverable in `med brief build` or the Task Explorer
inside `med present`. Switch to **Repository** to inspect source provenance, or
**Supporting research** for source screens, tool calibration and retrospective
analysis. These are views of the existing catalogue, not additional experiment
or assessment systems.

## Separate the axes

| Axis | Meaning | Example |
| --- | --- | --- |
| Primary category | The work required to produce the principal deliverable | Segmentation, correspondence, reporting |
| Secondary operations | Other substantive operations in a compound task | Longitudinal analysis also needs localization, segmentation and correspondence |
| Agent work | What the agent is responsible for | Solve a case, build a method, operate a tool workflow |
| Research role | Why this entry exists | Agent task, source/feasibility study, tool calibration, retrospective analysis |
| Research owner | The group maintaining its question, methods and evidence | `anatomy-audit` owns CT segmentation and annotation auditing |
| Source repository | Where an imported definition comes from | HealthAgentBench, AutoMedBench, TB3 |

Use the [controlled vocabulary](../presentation/task-explorer/taxonomy.json), not
an anatomy name, modality, model or round number, for the primary category.
Choose the principal deliverable; add secondary operations where needed.
A compound longitudinal task remains useful as a workflow entry without making
every segmentation or correspondence task longitudinal.

Groups are enduring research owners. They can contain different task categories.
Changing navigation does not require moving their evidence or renaming durable IDs.
Model, effort, budget, runtime, tool availability and actual tool use are experiment
conditions; anatomy, modality and dataset alone do not establish task identity.

## Definitions, conditions and evidence

```text
Capability view / repository view
  task family (related workflows; no shared score implied)
    definition or contract revision (one brief)
      assistance conditions and cases
      linked experiments with explicit scope
        existing attempts → evaluations/reviews → findings
```

Use one definition across repeated cases or model/effort comparisons when its
input/output and evaluation contract is shared. Give a changed output, inclusion
policy or scientific endpoint its own definition/revision; related definitions
can share a navigation family. Case and condition are independent axes, not a
claim that every possible case/condition combination was executed.

The four CT organ experiments share one segmentation brief. CT-only and callable
LiteMedSAM assistance remain explicit, with each experiment's own protocol and
task digest. Dental original/v2/v3 contracts and longitudinal original/revised/
candidate contracts have separate definitions under their respective families.
The candidate contract adds a probability/reason sidecar and retains the recorded
`endpoint_only` comparison; grouping never upgrades it to a matched comparison.

An experiment can contain several historical tasks or research roles. Link it
from more than one entry only with an explicit scope. BR-033's airway agent pilot
and TopBrain source/prediction screen remain separately described. An experiment
record, an imported source record, a case and an attempt are different counts.

## Classification boundaries

| Work | Placement and reason |
| --- | --- |
| Supplied anatomical-mask audit | Annotation review: inspect an existing spatial interpretation |
| Raw CT organ or dental masks | Segmentation: construct that interpretation |
| Identity of supplied 3D objects | Recognition: geometry is already supplied |
| Named landmark / abnormality search | Localization, with separate definitions for a specified anatomical target and deciding whether an abnormal target exists |
| MRI frame association | Data engineering: repair acquisition indexing and affine construction |
| RESECT point audit | Correspondence: the endpoint is the homologous US point and TRE |
| Supplied-candidate CT probe | Recognition with downstream masks/links: candidate centers remove discovery |
| CT clinical-context inference | Reporting: evidence-qualified contextual claims, not lesion tracking |
| Supplied-mask cardiac mechanics | Motion/mechanics: segmentation is given; material correspondence is not |
| SAM/LiteMedSAM slice calibration | Supporting tool calibration: reference-derived prompts and direct inference, no general-agent trial |
| Health-record conversion / QA / prognosis / trial matching | Data engineering / data quality / prediction / eligibility, respectively |

Diagnostic **origin** does not by itself make a task supporting research. A fresh
agent can perform a diagnostic candidate-recognition task. Conversely, a direct
segmentation-model prediction or an author reconstruction screen is not an agent
trial. `proposed` marks an unfinished definition; it is independent of research
role, experiment assessment and whether an executable package is available.

## Authoring and checks

The [root collection](../presentation/task-explorer/catalog.json) composes
`groups/*/presentation/catalog.json` and the external source-survey collection.
Each group owns its internal briefs, classification and scoped experiment links.
The external collection owns imported definitions; its inventory retains source
IDs, revisions, case links and release/condition differences.

```sh
med brief new named-target --title "Locate a named target" \
  --repository "TB3 medical workbench" --repository-id tb3 \
  --family localization \
  --catalog groups/anatomical-landmarks/presentation/catalog.json \
  --destination groups/anatomical-landmarks/presentation/briefs/named-target.md
med brief check
med brief build --output runs/task-explorer/index.html
```

Edit the proposed entry's `owner_group`, `role`, `agent_work`, optional
`operations`, and `experiments: [{"id": "stable-id", "scope": "exact portion"}]`.
Use the [Task Brief rulebook](../presentation/task-explorer/RULEBOOK.md) for content.
After creating an experiment, link it from the appropriate group catalogue before
the repository checks. The root check rejects omitted experiments, unknown axes,
unknown/duplicate/unscoped experiment links, wrong owners and task families that
cross primary categories, research roles, agent work or repositories. Mixed-study
links may overlap deliberately; no automatic score aggregation is provided.

Classification is assistant-maintained interpretation of the cited contracts.
Reopen it when a contract changes, a mixed record is clarified, a new operation
cannot be expressed faithfully, or reader testing exposes ambiguity. Scientific
reference disputes continue through the existing issue/review workflow.

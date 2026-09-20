# Sources, evidence and reproduction

The six chapters describe selected completed experiments. This page separates the material needed to **understand an output**, **check a recorded score**, and **run a new attempt**.

## Start with a chapter

| Task | Result and observed method | Frozen design | Reproduction guide |
| --- | --- | --- | --- |
| [Organ auditing](../groups/anatomy-audit/presentation/story.md) | [BR-017 result](../docs/research-rounds/BR-017-results.md), [trace walkthrough](../docs/research-rounds/BR-017-traces.md) | [Protocol](../docs/research-rounds/BR-017-absorbed-anatomy.md) | [Source construction, scoring and figures](../probes/revisions/br017/authoring/README.md) |
| [Aneurysm search](../groups/lesion-localization/presentation/story.md) | [BR-016 result and traces](../docs/research-rounds/BR-016-results.md) | [Protocol](../docs/research-rounds/BR-016-aneurysm-localization.md) | [Acquisition, scoring and explorer](../probes/revisions/br016/README.md) |
| [Matching scans](../groups/registration/presentation/story.md) | [BR-028 result](../docs/research-rounds/BR-028-results.md), [saved candidates](../docs/evidence/br028-stage-analysis.json) | [Protocol](../docs/research-rounds/BR-028-registration-3d-source.md) | [Preparation, scoring and rendering](../probes/registration-deformation/authoring/br028_README.md) |
| [Vessel workflows](../groups/tubular-anatomy/presentation/story.md) | [Coronary result](../docs/research-rounds/BR-030-results.md), [airway contrast](../docs/research-rounds/BR-033-results.md) | [Coronary protocol](../docs/research-rounds/BR-030-vessel-diagnostic-geometry.md) | [Coronary guide](../probes/vessel-geometry/README.md), [airway guide](../probes/airway-routing/authoring/README.md) |
| [Cardiac reconstruction](../groups/cardiac-motion/presentation/story.md) | [BR-035 result](../docs/research-rounds/BR-035-results.md) | [Protocol](../docs/research-rounds/BR-035-segmentation-mechanics.md) | [Mesh construction, scoring and replay](../probes/cardiac-reconstruction/authoring/segmentation_mechanics/README.md) |
| [Anatomical landmarks](../groups/anatomical-landmarks/presentation/story.md) | [BR-040 comparison](../docs/research-rounds/BR-040-results.md), [source-use audit](../docs/evidence/br040-source-audit.json) | [Protocol](../docs/research-rounds/BR-040-sol-landmarks.md) | [Same-task comparison and overlays](../probes/semantic-landmarks/authoring/br040/README.md) |

The [task cards](../groups) are editorial summaries, not executable specifications. Each measurement contains a source file and JSON pointer; original protocols, frozen task files and scorers remain authoritative. Reported Sol/Terra names refer to the recorded model configurations, not Claude or GPT-4o aliases.

## Public sources and modest comparison context

| Resource | Used for | How to interpret it |
| --- | --- | --- |
| [TotalSegmentator paper](https://arxiv.org/abs/2208.05868), [source release](https://zenodo.org/records/10047263) | Organ masks and context for automatic segmentation | The paper's 0.943 Dice concerns segmentation, not detection of the controlled label-transfer error. The paper describes 104 structures; later dataset/software scope is a different claim. |
| [OpenNeuro ds003949](https://github.com/OpenNeuroDatasets/ds003949) | Real TOF-MRA and weak aneurysm labels | Supports coarse source-region localization. N03 used public-source identification before answering. |
| [Learn2Reg LungCT 1.11](https://doi.org/10.5281/zenodo.3835682) | Paired breathing-phase CT | Correct source for BR-028; this is not a DIR-Lab experiment. |
| [ImageCAS](https://www.kaggle.com/datasets/xiaoweixumedicalai/imagecas), [ImageCAS-X](https://zenodo.org/records/21887809) | Coronary CT, predictions and reference geometry | Selected case is training-split development data. See the [source receipt](../docs/evidence/br030-sources.json) for pinned acquisition and inference. |
| [CPR technical report](https://www.cg.tuwien.ac.at/research/publications/2002/kanitsar-2002-CPRX/) | Explain the established curved-view technique | Background for the workflow, not a competing score on this task. |
| [AeroPath](https://github.com/raidionics/AeroPath) | Airway repair contrast | Retain the [source audit](../docs/evidence/br033-source-audit.json), including the downloaded CC BY 4.0 license and differing mirror-card declaration. |
| [STRAUS](https://humanheart-project.creatis.insa-lyon.fr/multimodalityStraus.html) | Synthetic ultrasound and known material motion | Simulation truth, not measured patient strain. |
| [EchoXFlow](https://huggingface.co/datasets/Ahus-AIM/EchoXFlow) | Separate clinical cavity geometry transfer | Supplied all-phase masks already encode the volume curve; no myocardial material-strain truth. |
| [VerSe](https://github.com/anjany/verse) | Spine CT and named targets | Full and cropped conditions use the same subject. Derived CT illustrations retain CC BY-SA 4.0. |
| [AFIDs SNSX](https://openneuro.org/datasets/ds004470), [AFIDs framework study](https://pubmed.ncbi.nlm.nih.gov/31175816/), [placement protocol](https://afids.github.io/afids-protocol/afids_protocol/human_protocol.html) | Brain fiducials and conventional human/atlas workflow | Protocol validation is contextual; it is not a matched human-versus-agent trial here. MRI assistance and model/effort differences stay explicit. |
| [NHLBI heart-failure overview](https://www.nhlbi.nih.gov/health/heart-failure) | Keep the clinical interpretation bounded | Diagnosis uses more than a reconstructed EF number. |

The light literature pass is recorded in [local source notes](editorial/external-source-notes.md). It adds context, not a cross-dataset leaderboard. No new human evaluation or agent trial was run for these chapters.

## What is available locally

| Layer | Included here | What additionally needs restoration |
| --- | --- | --- |
| Read | Markdown chapters, standalone figures, diagram sources and captions | Nothing for static reading; Mermaid rendering depends on the reader |
| Inspect provenance | [Asset manifest](assets.json), [evidence inventory](editorial/evidence-map.json), source-linked task cards | Referenced original evidence remains in the workshop repository |
| Check a recorded score | Scorers, frozen-design records and concise receipts in the repository | Actual submitted artifacts where retained only under ignored `runs/` |
| Rebuild scientific views | Authoring scripts and source/derivation records | Native arrays, runtime artifacts and the recorded Python environments |
| Run a new attempt | Owning protocol, task hashes and command documentation | Source data, frozen task, Docker/harness, model access and a new output directory |

Recomputing a saved score and reproducing the exact text of a fresh model response are different goals. Use the frozen version for comparisons, preserve earlier outputs, and record the new runtime configuration. Detailed requirements vary by experiment; follow its guide rather than a generic install command.

## Rebuild the portable content assets

From the workshop repository root:

```sh
python3.12 scripts/med assets --write
python3.12 scripts/med assets
python3.12 scripts/check_medical.py
```

The exporter decodes exact retained PNGs and extracts Mermaid blocks from the chapters. It makes no model calls, edits no source scan, and changes no frozen experiment. The coronary preview is copied from the retained local viewer; after export, its pinned copy can be checked without restoring the scan.

The Markdown and task cards are directly authored. The old hardcoded prose/card generators have been retired. The HTML builder is unchanged legacy presentation code and does not consume this content version; it must be adapted in the later presentation phase.

## Moving this material to Astro

Move the chapters, `assets/`, task summaries, and selected evidence with their attribution. Resolve chapter links as blog routes and repository evidence links against an explicit source revision or copied evidence bundle. The current `../docs/` and `../probes/` links intentionally work within this workshop; they need that migration mapping.

Editable diagrams live under `assets/diagrams/`. The retained scientific images are independent of the current HTML/CSS. Original interactive viewers and arrays remain available locally for a later interaction pass; these static exports do not replace full native-volume exploration.

The overview's synthesis, current limitations and outlook will be developed with the user next. See the [editorial decisions](editorial/README.md).

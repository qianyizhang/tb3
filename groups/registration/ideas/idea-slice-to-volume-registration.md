+++
schema_version = 2
kind = "idea"
id = "idea-slice-to-volume-registration"
group_id = "registration"
title = "Recover a landmark-oriented oblique CT section pose"
next_action = "Retire the tested snapshots. Preserve evidence; do not infer anatomical understanding or cross-acquisition ability from exact-texture matching. Paired-scan or modality successors need independent correspondence truth and an adequate transform model before admission."
decision_provenance = "Imported authored catalog state; no new user approval inferred."
idea_state = "dropped"

[[sources]]
url = "codex://threads/01a0a845-7c2d-7992-a662-24d52831af90"
note = "Owning user request on 2026-09-16; exact source-message ID is not exposed."

[[sources]]
url = "https://arxiv.org/html/2410.18683v1"
note = "SLIV-Reg: external slice-registration initialization failures; not an LLM failure ledger."

[[sources]]
url = "https://zenodo.org/records/10047263"
note = "TotalSegmentator small v2.0.1, CC BY 4.0; retained subject s0915 supplies this pilot."

[[sources]]
url = "https://arxiv.org/html/2112.04489v2"
note = "Learn2Reg: paired intra-patient sources and affine-preprocessing/deformation caveats for later stages."

[historical_source]
path = "catalog/ideas/slice-to-volume-registration.json"
commit = "51f3b1224d2069fe931ac28b06fd2ccf38c497ab"
sha256 = "4ee9f18fa99eb0d24fde75ca6592974335639cbd9c2aa4defa0aa5c481602179"
+++

# Recover a landmark-oriented oblique CT section pose

## Question

Single-slice localization requires discovering the correct six-degree-of-freedom alignment before local intensity refinement; partial field of view may reduce recognizable context.

## Prior findings

Not established: both frozen same-acquisition full and partial views passed Terra/high normally. RMS physical errors were 0.000477 and 0.000586 mm versus a 3 mm tolerance. A public-input-only author baseline also solves both in seconds.

## Reopen when

Retire the tested snapshots. Preserve evidence; do not infer anatomical understanding or cross-acquisition ability from exact-texture matching. Paired-scan or modality successors need independent correspondence truth and an adequate transform model before admission.

## Teaching figure: Anatomy skill trial, 2026-10-12

At the user's request to try the Anatomy explainer skill, the assistant built a
[slice-pose positioning bench](../presentation/anatomy-pose/design.md).
The offline page is generated at `.local/anatomy-pose/index.html` from the
group-owned recipe. Six controls drive one pose model, the matrix and physical
grid-point errors; the synthetic reference requires an explicit reader reveal.

Useful distinction: matching the centre and normal does not recover the image
pose. A 25-degree in-plane turn in this synthetic 80 mm square gives zero centre
and normal errors but 16.32 mm RMS and 24.49 mm maximum point errors.
Seventeen synthetic poses agreed with the retained R01 Python scorer, including
the 3 mm RMS boundary. This is an explanation of the task contract, not a new
experiment, native CT figure, difficulty claim or reopening decision.

Assistant assessment: Anatomy's physical-instrument style is useful for teaching
coordinate geometry. The mechanical mounting is illustrative; the six-degree
pose mathematics is exact for the stated synthetic section. Retain the existing
Task Explorer and source-backed images as the scientific presentation authority.

### Whole-volume trace revision

The user requested a stronger connection to the whole CT and a real solving
process. The [BR-019 full-view trace report](../findings/br019-full-view-trace.md)
now links the retained Terra/high attempt to native CT context, selected wrong and
coarse poses, the saved answer, and a reader-only evaluator reveal. Its interactive
page is `.local/anatomy-pose/trace/index.html`. Selected intermediate views are
explicitly reconstructed from rounded logs; the final render and metrics reproduce
the retained evidence. This supersedes the instrument-only explanation as the
recommended first read, without changing task disposition or authorizing a new run.

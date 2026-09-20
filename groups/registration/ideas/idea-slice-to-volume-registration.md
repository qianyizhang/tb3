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

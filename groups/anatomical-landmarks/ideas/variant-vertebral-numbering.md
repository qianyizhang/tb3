+++
schema_version = 2
kind = "idea"
id = "variant-vertebral-numbering"
group_id = "anatomical-landmarks"
title = "Number vertebrae in anatomical variants"
next_action = "Assistant recommends a conventional control plus source-confirmed variants, after auditing case numbering conventions and counting anchors."
source = "codex://threads/01a0bde4-e30d-71c3-8ae4-19d377aee51d"
decision_provenance = "Assistant proposal; user requested explanation, not trial selection."
historical_ids = [
    "BR-043-C04",
]
idea_state = "exploring"

[[links]]
label = "Proposal and visual explanation links"
path = "docs/research-rounds/BR-043-medical-next-tasks.md"
+++

# Number vertebrae in anatomical variants

## Question

Number vertebrae in anatomical variants

## Prior findings

BR-040 used one typical-numbering CT subject. Localization and naming can fail separately; uncommon numbering remains untested locally. Preserve counting anchors so ambiguity is not mistaken for a reasoning failure.

## Reopen when

Assistant recommends a conventional control plus source-confirmed variants, after auditing case numbering conventions and counting anchors.

## 2026-09-28 explainer source review

Assistant source review verified all eight unique frozen input volumes and native
coordinate mappings across BR-036/038/039/040, all 71 BR-040 reproduction files,
and 30 stored score records (27 unique executions, 11 model attempts). The
[audit](../presentation/sources/named-landmark-audit.json) retains exact source pins,
replay limits and inspected reference panels. This is saved-output regrading;
no new model trial or variant selection occurred.

Terra's partial-scan T4 claim lies on source T5; Sol avoids all 11 outside-target
claims but misses visible T5. Keep wrong naming, visible misses, outside targets,
absent T13/L6 and uncertain responses distinct. Subject 823's source supplement
supports its conventional 24-presacral count; variants remain an open study.

The AFIDs release's pinned root license is CC0, correcting the historical CC BY
statement without rewriting its retained receipts. Both AFIDs IDs 22 and 27 have
a source rater more than 3 mm from the consensus; retain this tolerance context
and all original scores. The MRI method used generic atlas assistance, and its
original runtime atlas image remains unrecovered. See the
[terms correction](../presentation/sources/named-landmark-source-terms.json) and
[exact condition brief](../presentation/briefs/tb3-named-landmarks.md).

Assistant next action: complete this same entry's native-image story and explicit
reference reveal, then review exported motion and mobile/no-GPU behavior. The
source audit alone does not accept the story or authorize new medical trials.

## 2026-10-12 native trace explanation

Assistant selected one retained BR-039 Terra/high partial-CT attempt for the
[native manuscript](../presentation/stories/br039-native-trace.story.md). It connects
thirty logged inspection states and ten exact delivered images to the full
512×512×920 supplied crop. A coarse reader preview is explicitly distinct from
recorded images. Saved T4 is 2.142412 mm from source T5; source T4 lies outside the
crop. This comparison preserves frozen counts and availability denominators.

The [recovery mapping](../presentation/native-landmark-trace/canonical-mapping.md)
and [recipe](../presentation/native-landmark-trace/README.md) retain source roles,
missing work files, native geometry and VerSe terms. This is an explanation of
one existing attempt, not a new model trial, variant result or clinical adjudication.
Reopen on source/geometry changes; renderer verification is recorded separately.

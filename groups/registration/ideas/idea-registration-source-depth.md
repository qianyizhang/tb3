+++
schema_version = 2
kind = "idea"
id = "idea-registration-source-depth"
group_id = "registration"
title = "Transfer respiratory landmarks with both CT volumes available"
next_action = "Parked after completed calibration; no follow-up trial is scheduled. Retain original evidence and reopen only under the conditions below."
decision_provenance = "User accepted the parking recommendation on 2026-09-21 in codex://threads/01a0c040-3777-7b72-b932-6e6b118304a2; decision decision-355202e8c86445c6. Historical outcomes remain unchanged."
idea_state = "parked"

[[sources]]
url = "codex://threads/01a0a845-7c2d-7992-a662-24d52831af90"
note = "User asked whether inputs were just 2D patches and requested a 3D version on 2026-09-16. Exact message ID is unavailable. The target already was 3D; this matched follow-up adds the full source CT."

[[sources]]
url = "https://doi.org/10.5281/zenodo.3835682"
note = "Learn2Reg LungCT 1.11 source attribution and CC BY 4.0, using previously hash-verified local data."

[historical_source]
path = "catalog/ideas/registration-source-depth.json"
commit = "51f3b1224d2069fe931ac28b06fd2ccf38c497ab"
sha256 = "d248672cfb8fb5e31d077f928a3b87703b8c43809ad852538153f55693f65cba"
+++

# Transfer respiratory landmarks with both CT volumes available

## Question

Adding full source-volume context to the same failed single-view registration case may remove depth ambiguity and permit a more accurate fresh Sol solution while retaining the same small deliverable and physical tolerances.

## Prior findings

The full-source condition is accepted by the user on visual review of q06 and retired as a hard-task candidate for this intended example. The historical numerical result remains a normal completed failure: 2.604 mm RMS / 6.412 mm maximum, substantially better than the earlier 2D-source result of 12.731 / 32.203 mm. Recorded code uses actual 3D patches and broad search independent of the failed global field. The practical acceptance, automated score and earlier 2D failure are distinct judgments; no repeatable difficulty claim is made.

## Reopen when

Reopen if independent review revises the q06 correspondence or a new unused respiratory pair with verified landmarks supports a matched source-depth comparison. Freeze physical gates, reference provenance and an input-legal author baseline before any separately authorized trial.

## Current disposition

The full-source respiratory registration calibration is complete and was accepted by the user on visual review; no follow-up trial is scheduled. Preserve the unchanged numerical failure and its separate practical acceptance. The user accepted parking on 2026-09-21 in [the refinement task](codex://threads/01a0c040-3777-7b72-b932-6e6b118304a2). This does not close the broader scientific question.

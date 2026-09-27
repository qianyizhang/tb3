+++
schema_version = 2
kind = "idea"
id = "residual-breast-extent"
group_id = "longitudinal-reading"
title = "Measure residual lesion extent"
next_action = "Assistant recommends deferring trials until fresh cases have adjudicated boundaries, resolved units and one prospective measurement definition."
source = "codex://threads/01a0bde4-e30d-71c3-8ae4-19d377aee51d"
decision_provenance = "Assistant proposal; user requested explanation, not trial selection."
historical_ids = [
    "BR-043-C05",
]
idea_state = "exploring"

[[links]]
label = "Proposal and visual explanation links"
path = "docs/research-rounds/BR-043-medical-next-tasks.md"
+++

# Measure residual lesion extent

## Question

Measure residual lesion extent

## Prior findings

BR-037 exposed unresolved measurement reliability and source diameter units. Reduced enhancement, longest diameter, functional tumor volume and pathology response are different endpoints.

## Reopen when

Assistant recommends deferring trials until fresh cases have adjudicated boundaries, resolved units and one prospective measurement definition.


## Explainer audit — 2026-09-27

Assistant source/engineering review for the [MRI task](../presentation/briefs/tb3-longitudinal-mri.md) rechecked 354 original frozen files and reproduced both P03 saved component-box methods (−5.9% versus −27.2%). [The source audit](../presentation/sources/longitudinal-mri-audit.json) retains native geometry checks, method definitions and source-reference boundaries. The [canonical story](../presentation/stories/longitudinal-mri.story.md) connects actual images to citations, phase choice, measurements, uncertainty and forecast baselines.

The diagnostic comparison does not resolve clinical measurement validity or source workbook diameter units. Source-VOI selected reader crops remove search; no new model run, adjudication or score revision occurred. All three next-visit source diameters decreased, so an always-smaller baseline ties the neutral forecasts. The existing reopening conditions remain unchanged. This is an assistant explanation, not a new user research decision.

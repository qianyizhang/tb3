# Cardiac modeling session closeout

> Historical session closeout. Use [Cardiac motion](../groups/cardiac-motion/README.md)
> for current research and presentation, and [reproduction](reproduce.md) for
> supported commands. Old site links and launchers below are retained provenance.

The [Dynamic heart chapter](../site/index.html#cardiac) is the presentation of
this completed series. The final finding is bounded: **Sol can construct a
segmentation-driven 4D mesh and calculate its strain, while correct local tissue
mechanics and clinical function remain separate requirements.** No further trial
is queued. This does not change the earlier anatomy selection or submission.

Eight fresh model attempts completed normally: four in BR-031, one each in
BR-032/034, and two in BR-035. Author prototypes, scientific controls and
unchanged-code replays are counted separately. All cases are public; absence
of observed source retrieval does not establish absence from pretraining.

## Retained experiments

| Stage | Original records | Meaning at closeout |
| --- | --- | --- |
| Contour-conditioned geometry | [BR-025](research-rounds/BR-025-cardiac-reconstruction.md), [source audit](evidence/br025-source-audit.json), [metrics](evidence/br025-pilot-results.json) | Author FeEcho4D pilot; four-view contour reconstruction is plausible, not demonstrated hard. Source mesh partition and ED/ES indexing limits are retained. |
| Fewer annotations | [BR-027](research-rounds/BR-027-cardiac-video-difficulty.md), [metrics](evidence/br027-cardiac-results.json) | One-anchor author tracking misses shape/function targets; two anchors help. No model trial. |
| Material heart prototype | [BR-029 plan](research-rounds/BR-029-dynamic-heart-modeling.md), [results](research-rounds/BR-029-dynamic-heart-results.md) | STRAUS source motion, author controls and fitted mechanics. The polished lab is not an agent recovery result. |
| Blind mechanics trials | [BR-031 protocol](research-rounds/BR-031-cardiac-agent-levels.md), [volume contrast](research-rounds/BR-031-volume-contrast.md), [results](research-rounds/BR-031-cardiac-agent-results.md) | Terra computes supplied-motion strain. Four-view Terra/Sol and full-volume Sol miss complete reconstruction. Several independent Sol components pass. |
| Real video without reconstruction truth | [BR-032 plan](research-rounds/BR-032-real-echo-case.md), [source notes](research-rounds/BR-032-source-notes.md), [results](research-rounds/BR-032-real-echo-results.md) | Sol's fitted animation uses fixed visual measurements; unchanged code still pulses on repeated still inputs. Anatomical accuracy unverified. |
| Clinical adaptation | [BR-034 plan](research-rounds/BR-034-pathological-echo.md), [control amendment](research-rounds/BR-034-preserved-control-amendment.md), [results](research-rounds/BR-034-results.md) | Image-driven tracking responds to altered inputs, yet EF is underestimated by 23–30 pp across three selected scans. Severity labels fail. |
| Geometry supplied, mechanics separated | [BR-035 protocol](research-rounds/BR-035-segmentation-mechanics.md), [results](research-rounds/BR-035-results.md), [evidence](evidence/br035-segmentation-mechanics-results.json) | Both new meshes pass construction and field calculation. Radial MAE 7.37/5.45 pp misses the 5 pp target. Both have six nonmanifold edges. Clinical replay preserves mask-encoded EF, not independent diagnosis. |

BR-025 also names an unrelated vessel round; its historical ID is preserved.
The [vessel chapter](../site/index.html#vessels) covers that branch separately.

## Acceptance after the series

- Geometry: independently rasterized masks, surfaces, volume and topology.
- Material motion: common reference probes and coverage for newly built meshes;
  source nodes only when identities are shared. Do not compare these RMSE
  definitions as interchangeable quantities.
- Mechanics: directional strain, regional peaks/timing, numerical tensor checks
  and local distortion. Add boundary-manifold checks prospectively.
- Function: cavity volume/EF, changed-input response and hidden clinical cases.
  Myocardial tissue volume is not cavity volume.
- Interpretation: calibration and appropriate independent diagnostic labels.
  Wall motion alone is not a blood-velocity field or an etiologic diagnosis.

The mask-only task is underdetermined for material correspondence, demonstrated
by identical occupancy with different analytic twist strain. The numerical
targets are development diagnostics, not clinical normal ranges. No retrospective
reward changes, new mesh repair, solver rerun or new model attempt were performed
for this presentation.

## Local labs and reproduction

The portable chapter has the exact BR-035 comparison figure and interactive
regional curves. It works without scans, meshes, runtime folders or network
requests. [Presentation provenance](../site/cardiac-provenance.json) retains
source definitions and exact hashes. [Code index](../probes/cardiac-reconstruction/README.md)
links the original authoring instructions.

| Local artifact | Purpose |
| --- | --- |
| [BR-029 workbench](../runs/br029-dynamic-heart/workbench/index.html) | Source/author material models and strain |
| [BR-034 review](../runs/br034-pathological-echo/review/index.html) | Clinical tracking and diagnostic limitations |
| [BR-035 review](../runs/br035-segmentation-mechanics/review/index.html) | Actual submitted meshes, reference toggle, independently computed strain colors and all four conditions |

These paths require the retained workspace and may require HTTP serving. To
reopen the final 3D lab without rerunning an experiment:

```sh
python3 -m http.server 8772 --bind 127.0.0.1 --directory runs/br035-segmentation-mechanics/review
```

Then open `http://127.0.0.1:8772/index.html`. Existing sessions may already serve
that port. For the complete report, use `make site` or open `site/index.html`.

## Cleanup and preservation

This closeout consolidates navigation, records the completed status and tracks
the authored cardiac scripts/protocols/evidence with the report. Original
records may say that no commit/publication had occurred; those statements
describe their historical stage and are not rewritten. Old pending-approval
and infrastructure-failure receipts remain as history, superseded by the linked
completed results where applicable.

Frozen authoring bytes, protocols, source data, task packages, predictions and
raw sessions remain at their original paths. Runtime reports and environments
stay local and ignored; there is no raw-evidence deletion. Unrelated diagnostic
preparation and hosting metadata are outside this commit. The
[closeout receipt](evidence/cardiac-report-closeout.json) records the retained
file hashes. A local commit does not update the hosted site.

# BR-023 — Sol/xhigh registration approach and measured effects

Completed 2026-09-16. **Sol/xhigh passed the unchanged 2D task: 1.563 mm RMS,
3.667 mm maximum error, 873.15 seconds of agent execution.** Its useful change
was finding the correct correspondence region for an ambiguous landmark.
The final numerical stage uses ordinary local translations; neither a downloaded
registration solver nor a final affine/deformable optimizer produced the answer.

The [initial protocol](BR-023-sol-registration.md) fixed one fresh attempt and
matched controls. The [component plan](BR-023-component-plan.md) fixed four
interventions after trace review and before their execution. Old task bytes,
prior reports and prior receipts remain unchanged.

## Actual attempt and validity

| Measure | Result |
| --- | --- |
| Agent | `gpt-5.6-sol`, `xhigh`; confirmed in runtime context |
| Task | Original BR-021 deform-2d, unchanged prompt and files |
| Acceptance | RMS ≤3 mm and maximum ≤5 mm, eight sparse landmarks |
| RMS / maximum | 1.562930 / 3.666674 mm; largest error is q05 |
| Agent / total trial time | 873.15 / 929.11 s |
| Completion | Normal voluntary finalization, no timeout |
| Attempts / automatic retries | 1 / 0 |
| Matched controls | Oracle 1, nop 0 |

Independent regrading agrees with all verifiers. Task checksums match BR-021
and BR-022. The fresh image audit confirms exactly the six public files, an
empty answer directory and no full exhale volume, private annotations or author
solver. No prior solution, analysis or hint entered the session. The actual
initial image was retained for component execution. See the
[trial evidence and delegated audit](../evidence/br023-results.json).

The executed solver uses **NumPy, SciPy interpolation/Powell optimization,
and Pillow**. Sol inspected SimpleITK version/initializer documentation but did
not execute registration with it. A PyTorch availability probe failed; it did
not install it. No external download, annotation lookup or network use was
observed in the retained trace. Public source annotations still leave possible
training contamination; recorded behavior cannot exclude it.

## What Sol did

1. **Established the physical geometry and inspected anatomy.** It read the
   supplied frame and voxel affine, rendered lung/soft-tissue windows and
   compared the source image with the nominal target reslice. It inspected
   vessel/airway patterns and candidate panels.
2. **Enumerated competing 3D positions.** The first substantial search tested
   voxel centres around each nominal query, approximately ±24.5/22.5/24.5 mm
   along the volume axes. It averaged normalized cross-correlation across
   three patch radii and retained spatially distinct candidates, rather than
   treating the first local optimum as the answer.
3. **Questioned q04's highest score.** The first q04 winner was voxel
   `[126,79,118]`, score 0.798; Sol instead explored third-ranked
   `[146,84,103]`, score 0.731, using displacement and image consistency.
   This was an improvement in candidate selection, but still not sufficient.
4. **Investigated ambiguity instead of stopping at a high score.** It swept
   patch radii, inspected refined patches, and tried nine-parameter local
   affine patches (centre plus two 3D basis corrections). It then generated
   150 surrounding matches and fitted robust local affine displacement
   regressions. Near q04, surrounding matches suggested approximately
   `[3.31,20.14,-5.15]` voxels relative to nominal geometry. Its visible
   commentary identified vessel-axis sliding as the ambiguity.
5. **Changed the search and initialization.** A later search used offsets
   `[-6,12] × [3,25] × [-15,6]` voxels and weighted several patch sizes.
   q04's top candidate became `[139,86,105]`; nearby alternatives were inspected.
   Sol used that point as the final start, rather than its earlier selection.
6. **Finished with simple local translation.** The final stage uses the fixed
   nominal patch orientation and Powell refinement within ±3 voxels of each
   selected start. It tries four radius/weight settings, then submits the
   first setting uniformly for all eight queries: radii 5/7/9 pixels, weights
   .4/.35/.25, world coordinates rounded to 0.01 mm. The radii correspond to
   half-spans 6.25/8.75/11.25 mm. Final format/order/in-volume checks pass.

The first q04 search only covered y indices 48–84; the reference is at y=86.
The updated motion-directed range admits it and excludes the earlier raw
winner. This is an offline geometric observation, not information supplied to
Sol. Being 2.5 mm outside the initial coarse box alone does not prove the whole
initial method had to fail; the later q04 starts and refinement bounds matter.

The method reconstruction uses executed code, printed candidates, recorded
image views and visible commentary. Retained internal-reasoning entries are
encrypted with empty summaries; we do not claim access to a fuller rationale
for selecting the first final weight setting.

## Which choices changed success?

Instrumenting the literal final-stage code reproduces **all eight submitted
coordinates exactly**. Each variant changes one final-stage setting, executes
in the retained public-input image with no network or labels, and is graded
afterward. The two q04 interventions leave the other seven outputs identical.

| Fixed intervention | RMS / maximum error | q04 error | Result |
| --- | --- | --- | --- |
| Replay final stage | 1.563 / 3.667 mm | 1.288 mm | Pass |
| Restore earlier chosen q04 start | 4.178 / 11.034 mm | 11.034 mm | Fail |
| Restore raw highest-NCC q04 start | 12.389 / 34.784 mm | 34.784 mm | Fail |
| Use only the smallest final patch | 1.502 / 3.577 mm | 0.955 mm | Pass |
| Stop at the final starts, before last refinement | 1.518 / 2.773 mm | 0.000 mm | Pass |

**The resulting q04 initialization is decisive under this final optimizer.**
The earlier chosen start's ±3 voxel box cannot come closer than 7.00 mm to the
reference; the raw winner's box has a 25.25 mm lower bound. The final start
includes the correct region. The observed 11.03/34.78 mm errors therefore
cannot be fixed just by optimizing harder inside those old boxes.

**Final multiscale scoring and subvoxel polishing are not necessary for this
pass once the starts have been selected.** This does not mean all multiscale
matching or optimization was unnecessary: the starts already incorporate
earlier searches, refinements, stability checks and neighborhood analysis.
Differences of roughly 0.05–0.06 mm among passing RMS scores are small, and
the manual reference points are discretized. They are not evidence of a
generally better or clinically preferable method.

**The more elaborate affine exploration was not the successful final method.**
All three recorded affine settings fail when their printed coordinates are
independently scored: RMS/max 3.362/8.037 mm (λ=.05), 2.615/5.547 mm (λ=.2),
and 2.474/5.561 mm (λ=1). This is descriptive, not a matched affine-model
ablation: those stages also use different starts, context and objectives.
It does establish that the final pass was not obtained by submitting those
affine outputs.

The conditional tests measure the effect of **where Sol chose to refine**.
They do not separately isolate the necessity of neighborhood regression,
visual inspection, revised search bounds or revised coarse patch weights.
For example, the later search already ranks the eventual q04 start first;
the results do not prove the entire 150-point neighborhood computation was
essential. An end-to-end ablation of that adaptive decision process would be
a different study.

Full outputs, objective values and geometric bounds are in the
[component evidence](../evidence/br023-component-analysis.json). All five
conditions and all three recorded affine settings are retained.

## Comparison with the prior Terra trajectories

| Attempt | RMS / max | Agent time | Observed route |
| --- | --- | --- | --- |
| Terra/high original, selected miss | 12.64 / 23.80 mm | 306.6 s | Rigid/2D warp initialization, restricted local search; composition defect |
| Terra/high repeat 2 | 24.91 / 34.17 mm | 374.7 s | 2D Demons initialization, restricted patch search |
| Terra/high repeat 3 | 2.02 / 4.65 mm | 290.1 s | Broad parallel-plane search, visual candidate correction, stability/orientation refinement |
| Sol/xhigh, fresh | 1.56 / 3.67 mm | 873.2 s | Multiscale 3D candidates, neighborhood-informed search correction, final translation |

Both successful trajectories revisit correspondence selection beyond a local
similarity maximum. Sol makes surrounding displacement consistency especially
explicit. The controlled tests support the importance of its chosen search
region on this case. They do not establish that Sol is generally more accurate
than Terra: there is one selected patient, one Sol attempt, unequal reasoning
efforts, different strategies and a retrospectively selected original failure.

The exact task remains retired as a reliable-difficulty candidate; the new Sol
pass adds useful strategy evidence rather than reviving that claim. Eight
sparse points do not validate a dense deformation field or clinical utility.
No new patient, further model attempt or additional intervention is scheduled.

## Artifacts

- [Interactive local comparison](../../runs/br023-sol-registration/review/index.html): actual CT patches for Sol, the three Terra attempts and every component condition.
- [Protocol](BR-023-sol-registration.md) and [component plan](BR-023-component-plan.md): scope and chronology.
- [Trial receipt](../evidence/br023-results.json) and [component receipt](../evidence/br023-component-analysis.json): scores, hashes, runtime/trace audit and limitations.
- [Authoring notes](../../probes/registration-deformation/authoring/br023_README.md): recovery, isolation and reproduction.

Raw sessions, textual trace exports, original candidate lists, captured arrays,
panels and generated reports remain under ignored `runs/br023-*`. The original
initial Docker image and content-addressed captured artifacts are retained.

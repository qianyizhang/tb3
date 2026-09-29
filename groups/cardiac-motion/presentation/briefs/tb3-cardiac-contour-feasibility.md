# Study cardiac reconstruction with supplied contours

Reconstruct a changing LV cavity from clean contours supplied at every phase.
This is the **BR-025 author feasibility study on one patient**, with no model attempt.
The [local source-derived story](../stories/cardiac-contour-feasibility.story.md)
shows actual Patient001 radial views and saved author projections. Its gold
withheld source mask is a reader reveal, not an input to the reconstruction.

## Value

Separate agreement with withheld 2D contours from derived 3D volume and ejection
fraction (EF). A plausible EF can coexist with substantial volume error.

## Given

### Original data

Native FeEcho4D Patient001: 30 frames, 37 radial ultrasound planes, each 464 × 485
pixels. Use 36 directions; plane 37 repeats the 180-degree direction. The case was
selected by native archive order before outcomes, after rejecting the GitHub
sparse-volume example as unsuitable for dense-background scoring.

The source specifies **0.089950 mm/pixel** in plane. The pilot assumes 5-degree
radial steps, an x=242 pixel rotation axis and a y=172 pixel origin derived from
supplied plane 1 across the cycle. Per-plane physical poses remain unaudited;
the config's 0.5 mm z-spacing is not an angular-plane translation.

### Supplied helpers

Clean source cavity masks at **all 30 frames** of the selected directions:
one view [1]; two [1,19]; four [1,10,19,28]; eight [1,5,10,14,19,23,28,32].
Plane numbers are one-based. Native mask labels are 0 background, 127 LV cavity
and 255 myocardium; this reconstruction uses cavity label 127.

### Callable tools

The retained CPU author baseline uses NumPy, SciPy and Pillow. It samples radial
extent from the supplied masks and interpolates between directions. It uses no
trained weights and fits every frame independently; ultrasound appearance is
available for inspection but does not drive this reconstruction.

### Reference-only material

The common withheld directions [3,8,12,17,21,26,30,35] are disjoint from every
sparse input set. Their masks are evaluation material. A separate dense comparator
uses all 36 directions, including these evaluation planes: its overlap is
**source fit**, not withheld accuracy. Source phase indices enter evaluation only.

The source project describes expert endpoint contours and propagated, reviewed
intermediate masks. Derived surfaces are not independent 3D truth. The native OBJ
sequence's physical transform and cavity/shell partition remain unresolved; its
whole enclosed volume is not an LV blood-pool oracle.

## Task specification

For each frame, sample the supplied cavity boundaries along 65 polar directions,
interpolate their radii onto 72 azimuths and close the two poles. This star-shaped
prior fills concavities and supplies unobserved geometry. Serialize each sparse
result before evaluating the dense comparator. Preserve source coordinates,
frame IDs and assumptions; shared vertex indices establish geometric indexing,
not tissue material correspondence.

## Expected output

The retained pilot saves one NPZ for each of the one/two/four/eight/dense conditions:
`vertices[30,4538,3]` in millimetres, shared `faces[9072,3]`,
`radius_px[30,72,65]` and `volume_ml[30]`. Results and curves JSON retain original
measurements. The static control repeats the four-view frame-1 geometry.
These are author outputs, not a frozen solver submission contract.

## Evaluation

Every sparse condition uses the same **240 frame/plane pairs: 30 × 8 from one
patient**. Dice compares projected cavity occupancy with source masks. HD95 is
computed per pair, then averaged. Volume MAPE averages relative error over all
30 frames against the dense reconstruction. EF error compares derived scalars
at filename frames 2 and 17, interpreting config ED_time/ES_time as one-based.
**The config does not specify its index base.**

| Supplied views / control | Withheld Dice | Mean pair HD95 | Volume MAPE | EF error |
| --- | ---: | ---: | ---: | ---: |
| One | 0.874 | 1.405 mm | 31.10% | 2.68 pp |
| Two | 0.929 | 0.728 mm | 7.85% | 5.97 pp |
| Four | 0.937 | 0.626 mm | 2.38% | 0.59 pp |
| Eight | 0.950 | 0.509 mm | 1.43% | 0.20 pp |
| Static four-view frame 1 | 0.825 | 1.662 mm | 76.57% | 63.79 pp |

Comparability is **matched for the shared withheld endpoints**: same case, frames,
evaluation planes and algorithm; supplied directions differ. Dense source-fit
Dice is 0.995 and derived EF is 63.79%; neither is independent clinical accuracy.
All saved meshes have closed manifold connectivity, no degenerate triangles and
positive signed volume. The historical static `observed_dice` uses plane 1 only,
despite copying a four-view reconstruction; the table uses the common withheld set.

The missing-depth control scales unobserved z-depth by 0.75–1.25 while retaining
the observed plane. Derived EF changes **66.47% → 79.88%, a 13.41 pp difference**.
Both completions satisfy that plane; the control does not validate either anatomy.

The 2026-09-27 saved-output audit reproduced all six original conditions within
1e-10, checked all 2,251 source members and inspected native plane-8 overlays at
frames 2 and 17. It performed no refitting or new trial and changed no frozen score.
The proposed Dice/HD95/volume/EF gates in the historical protocol were chosen
after this pilot; they remain development targets, not validated acceptance rules.

## Difficulty

All-phase boundaries remove boundary discovery and temporal tracking. Fixed mesh
IDs do not establish material motion or strain. The one-view EF/volume discrepancy
and the two-view EF error show why these endpoints require separate inspection.
No model difficulty, clinical diagnosis, flow, valves or whole-heart recovery was
tested. All phases/views belong to one patient, not independent samples.

## Coverage

The 2026-09-29 source resolution verified retained local Patient001 inputs and
saved outputs, then built a source-derived teaching pack and canonical story.
Its fixed-camera surface is a bounded display sample of the saved mesh; it does
not run a new fit. Integrated visual review and export remain unfinished.
The [FeEcho4D project](https://feecho4d.github.io/Website/) states noncommercial
research use, supporting this local task interpretation. Onward redistribution
permission for source images and derivatives remains unverified, so the pack is
local review material. The original data acquisition route is the
[native Zenodo release](https://zenodo.org/records/21322299); the source is not
missing from this workspace.

## Sources

- [BR-025 protocol and original results](../../experiments/br025/protocol.md)
- [Original source audit](../../../../docs/evidence/br025-source-audit.json)
- [Original pilot metrics](../../../../docs/evidence/br025-pilot-results.json)
- [Saved-output and source review](../sources/cardiac-contour-audit.json)
- [2026-09-29 source-resolution receipt](../sources/cardiac-contour-resolution.json)
- [Local teaching pack notice](../../../../presentation/task-explorer/cardiac-contour/NOTICE.md)
- [FeEcho4D project and research-use terms](https://feecho4d.github.io/Website/)
- [Native release metadata](https://zenodo.org/records/21322299)

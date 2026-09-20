# Semantic landmark session — completed

> Historical session closeout. Use [Anatomical landmarks](../groups/anatomical-landmarks/README.md)
> for current research and [reproduction](reproduce.md) for native replay/views.
> The old site/import commands below are retired; do not run them for a refresh.

[Portable report](../site/index.html#landmarks) synthesizes the user-requested
CT/MRI experiments. Eleven normal model attempts: eight Terra/high and three
Sol/xhigh. The final comparison improves broader-distance localization but does
not establish uniformly better precision or a population-level capability rate.

| Round | Protocol | Results and review |
|---|---|---|
| BR-036 | [Source shortlist and initial pilot](research-rounds/BR-036-semantic-landmarks.md) | [Results](research-rounds/BR-036-results.md), [traces](research-rounds/BR-036-traces.md) |
| BR-038 | [Volume and coordinate audit](research-rounds/BR-038-volume-landmarks.md) | [Results](research-rounds/BR-038-results.md), [traces](research-rounds/BR-038-traces.md) |
| BR-039 | [Expanded CT and unavailable targets](research-rounds/BR-039-ct-landmarks.md) | [Results](research-rounds/BR-039-results.md) |
| BR-040 | [Frozen Sol comparison](research-rounds/BR-040-sol-landmarks.md) | [Results](research-rounds/BR-040-results.md), [assistance audit](evidence/br040-source-audit.json) |

## Reproduction and retention

[Authoring code](../probes/semantic-landmarks/authoring/README.md) retains source
fetching, task preparation, scoring, controls, trace auditing and report scripts.
Subdirectories `br038`, `br039` and `br040` retain their own instructions.
Preparation and trial launchers are one-time operations; this closeout does not
queue another run. Frozen task bytes, source volumes, raw sessions, provider
configs and generated reports remain local under `runs/`.

The full [local comparison](../runs/br040-sol-landmarks/review/index.html)
contains 70 three-plane panels. The portable chapter selects seven exact panels
and retains all 84 requested-point rows. Intentional presentation refresh:

```sh
python3 scripts/import_landmark_figures.py
python3 scripts/build_site.py
```

Only the import step needs the retained local comparison. Normal site builds
use tracked inputs, require no scans and make no model or network calls.
[Figure provenance](../site/landmark-provenance.json) records hashes, sources,
licences and geometry. Original freezes and scores remain unchanged.

# Synthetic route fixture v1

Original source: the user-supplied `tb3-codex-handoff-24e4de7` package,
`reference/route-kit/assets/`. The adjacent manifest is byte-preserved; it owns
source terms, hashes, coordinate frame and limitations. These are original
procedural teaching assets, not patient anatomy, task evidence or a reference.

The [shared index](../../teaching-prefabs.json) enumerates the retained subset.
`geometry.json` is the only runtime mesh representation: hero tree, selected
route and sampling ribbon. `route.json` owns the 192 connected positions,
transported frames, transverse offsets, anchors and 18,624 scalar samples.
`cpr-sampled.png` is a bilinear display derivative of these samples;
`phantom-projection.png` is the supplied volume-projection fallback poster.
The `.npz` volume is retained for numerical verification only and is never
embedded in browser output. Camera/material/prefab records preserve the supplied
reference intent; production uses the existing stage's fitted perspective.

The GLBs listed in the original manifest were deliberately not imported; they
are redundant alternatives, not missing runtime dependencies. The manifest's
`tools/build_assets.py` locator refers to the source package's original generator,
not a production build requirement. The package's pre-rendered preview and MP4
were not imported or relabelled as integrated output. No mesh was regenerated.

All parts and annotation anchors share one fit on their parent. The source frame
is right-handed, +Y up, metres, with no anatomical left/right assertion. BR030's
real output contract remains in millimetres. The operation and numerical checks
are described in [the explainer contract](../../../EXPLAINERS.md).

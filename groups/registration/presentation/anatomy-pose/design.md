# Anatomy skill trial: a slice-pose positioning bench

The moving image platen is a finite CT section: translating and rotating it
changes the physical position of every pixel. A fixed reference appears only
after the reader chooses to reveal it. The instrument is a conceptual teaching
analogy, not a scanner or a clinically validated positioning device.

## Scope and truth

- Source task: [oblique-pose brief](../briefs/tb3-oblique-pose.md),
  [BR-019 protocol](../../../../docs/research-rounds/BR-019-slice-registration.md),
  [historical outcome](../../../../docs/research-rounds/BR-019-results.md).
- Six pose parameters drive the drawing, matrix and 7-by-7 point-error grid.
  A synthetic 81-by-81 image uses 1 mm pixel spacing; this is not the historical
  192-by-192, 0.9 mm/pixel R01 image. The shown shapes are a drawn phantom.
- The original engineering bounds are RMS <= 3 mm and maximum <= 5 mm,
  with a finite, rigid, right-handed transform. They are not clinical tolerances.
- Model results are not simulated. No new medical attempt is run.

## Parts plan, before geometry

Base: four isolation feet, four foot caps, bedplate, inset border, four bed bolts,
two ruler strips, engraved label plate (17 parts).
Structure: two X rails, four rail end blocks, eight rail screws, two rail wear
strips, lower carriage, four guide shoes (21 parts).
Mechanism: two Y rails, four end blocks, upper carriage, four guide shoes,
lift housing, lift column, mounting head, four platen edge rails, four corner
clamps, four clamp screws, image insert (27 parts).
Controls/detail: three square adjustment handles, three spindle blocks,
six grip insets (12 parts). Line ticks are surface detail, not part counts.

The base and X carriage use the Anatomy kit's shaded solids. The changing
platen is projected from the same pose matrix as the score; its faces are
depth sorted, and its image is mapped into the platen's local plane. A single
monochrome accent identifies the section. No pipes, cables, shaders or WebGL.

## Build and provenance

Anatomy: https://github.com/wheresryan22/anatomy, MIT, pinned revision
`e28bc3f2f91d4a27f3f60edf2207e05596e5f77d`.
Read and applied its SKILL.md, craft, kit, motion and verification guides,
and the dial-indicator example. The upstream checkout stays local.

From the repository root, with that revision in `.local/anatomy-skill-trial`:

```sh
node groups/registration/presentation/anatomy-pose/build.mjs
node groups/registration/presentation/anatomy-pose/check_instrument.mts
```

The standalone pages, SVG fallback, source excerpts, attribution, and browser
captures go to `.local/anatomy-pose/`. Browser checks use the repository's
disposable harness and require approved execution outside the macOS sandbox.
This is an isolated skill trial, not a replacement for the canonical story player.

## Trial assessment

- Useful result: the correct-plane/wrong-pixel-direction preset exposes a
  coordinate error that a still diagram makes difficult to see. Anatomy supplies
  the isometric camera, shaded base/rail geometry, figure framing and themes.
- Verification: 17 synthetic poses agree with the retained Python scorer;
  browser checks cover reference hiding/reveal, exact match, keyboard motion,
  animation, reduced motion, light/dark themes and 390 px layout. The upstream
  line-end detector reports zero problems in both themes. Desktop, phone and
  4x instrument captures were inspected. Repository docs and records validate.
- Limit: custom projected platen faces and idealized mechanical supports were
  visually inspected, not certified by Anatomy's optional full 3D collision
  audit. This is a teaching instrument, not a physically engineered machine.
- Assistant recommendation: use this style for geometric mechanisms and pair
  it with source-backed medical imagery when teaching image interpretation.
  The later campaign below authorizes broader presentation improvements; it does
  not require replacing the canonical player with standalone applications.

## Real trace revision, 2026-10-12

The user found the instrument disconnected from the full CT and requested a real
task-solving trace explaining the whole process. The revised explainer uses the
retained BR-019 R01 Terra/high run, native CT crop and saved final answer. It keeps
the restrained figure framing and adds a native-coordinate 3D volume viewer,
three CT slice controls, selected logged poses, matched reslices, silhouette/difference
views and a separate evaluator-reference reveal.

Build the additive revision (the original instrument remains available):

```sh
.venv-br019/bin/python groups/registration/presentation/anatomy-pose/prepare_trace.py
node groups/registration/presentation/anatomy-pose/build_trace.mjs
node groups/registration/presentation/anatomy-pose/check_trace.mts
```

Output: `.local/anatomy-pose/trace/index.html`. All derived media stay local.
The [trace report](../../findings/br019-full-view-trace.md) and its hashed receipt
retain the claim boundaries, source identities, selected steps and verification.
No new solver/model execution or broader player integration is implied.

## Follow-on scope

On 2026-10-12 the user requested cleanup, scoped commits and a goal to apply the
same approach to the rest of the presentation. Native context, retained solving
traces, source/reference separation and meaningful controls are the accepted
direction. Existing canonical scope and prior acceptance records remain intact;
the broader pass must integrate with shared presentation infrastructure.

The browser checks above use disposable profiles and require approved execution
outside the macOS command sandbox. Raw media remain local. Recover the optional
Anatomy kit by cloning its linked repository into `.local/anatomy-skill-trial`
and checking out the exact pinned revision before building the concept bench.
The real CT trace viewer requires the retained source run and existing imaging
runtime; it does not require the kit checkout.

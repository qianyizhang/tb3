# Anatomy trial 02: vessel repair from a retained MRA trace

This focused evidence instrument adapts the
[Anatomy skill](https://github.com/wheresryan22/anatomy/tree/e28bc3f2f91d4a27f3f60edf2207e05596e5f77d)
to the user's request for real images and a whole-volume solving process.
Its instrument framing, tone hierarchy and coupled controls inform the page;
native medical geometry takes precedence over an invented mechanical metaphor.

The same component changes in the 3D mask, matched MRA plane and measured voxel
count when the reader selects a recorded threshold. Whole crop → local crop
keeps the repair located in source context. There are no decorative vessels,
interpolated solver trajectories or background animation loops.

## Build and ownership

- `prepare.py`: retained arrays, threshold/contact reconstruction, exposed voxel
  surfaces, saved-output replay, trace extraction and source hashes.
- `index.html`, `style.css`: narrative and responsive evidence framing.
- `viewer.js`: read-only native-coordinate scene, source slices, phase changes,
  keyboard controls and static projection fallback.
- `build.mjs`: existing bundler and Three.js, embedding assets in local HTML.

```sh
.venv-br019/bin/python groups/tubular-anatomy/presentation/anatomy-repair/prepare.py
node groups/tubular-anatomy/presentation/anatomy-repair/build.mjs
node groups/tubular-anatomy/presentation/anatomy-repair/check.mts
```

Output: `.local/anatomy-pose/vessel/index.html`, approximately 2.2 MB. Native data,
images, screenshots and checks remain local. No dependencies were installed.
The recipe imports only the reviewed data-only scorer, whose main is guarded;
no preparation or solver authoring module executes. Original evidence is preserved.
Data terms and Three.js MIT attribution accompany the output.

## Verification and limits

The [finding](../../findings/br026-gap-trace.md) records exact measures, inspection
and interpretation. The disposable browser check uses the repository harness;
on this Mac browser launching requires approved execution outside the command
sandbox. Controls have keyboard support; no-WebGL mode retains real source
images and threshold/slice controls. Native coordinates use the complete oblique
NIfTI affine. Local surface cuts are labeled, and no smoothing is applied.

Display windowing is separate from full-precision threshold reconstruction.
Magenta residual voxels are private-reference teaching evidence shown only in the
final phase. Links to actual delivered trace images distinguish those artifacts
from newly generated reader views. No new trial or publication is implied.

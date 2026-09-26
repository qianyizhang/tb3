# Teaching asset library

Use these assets to explain **what goes in, what the reader or agent does, and
what comes out** before asking someone to interpret a moving 3D scene.

| Asset | Responsibility |
| --- | --- |
| [task-art.js](task-art.js) | `TaskTeachingArt.render(entry, output)` returns a self-contained accessible SVG; `scan(subject)` supplies reusable image-plane texture for the 3D renderer. Shared scan, anatomy, signal, document, table and field primitives support every authored illustration kind. |
| [task-story.js](task-story.js) | `TaskTeachingStory.describe(entry)` returns a concrete action, a reading cue, the output form and stage names. `kinds` lists supported recipes. |
| [TaskVisual.tsx](../../frontend/task-visuals/TaskVisual.tsx) | React-owned stage controls, concise task sequence, 2D explanation and static fallback. |
| [task-visual.module.css](../../frontend/task-visuals/task-visual.module.css) | Scoped, container-responsive scene layout. |

```js
import { TaskTeachingArt } from './task-art.js';
import { TaskTeachingStory } from './task-story.js';

const example = {
  id: 'my-authored-example',
  illustration: {
    kind: 'segment',
    subject: 'abdomen',
    target: 'pancreas',
    mask_mode: 'binary',
    input: 'Unlabeled image',
    output: 'One target mask',
  },
};
const inputSvg = TaskTeachingArt.render(example);
const outputSvg = TaskTeachingArt.render(example, true);
const { action, cue, form } = TaskTeachingStory.describe(example);
```

These are ordinary ES modules with named exports. The browser build follows
normal imports from `TaskVisual.tsx`, bundling teaching diagrams, source anatomy JSON
and license notices into the portable output. There is no script-order contract,
global renderer bridge or compatibility wrapper. The modules require no runtime
fetches, fonts, graphics packages or dataset access. The SVG library escapes
caller-supplied text and can render outside the Task Explorer.

## Authoring another explanation

1. Reuse an existing `kind` if the **deliverable** matches. Choose `subject`
   explicitly; missing anatomy uses a neutral image. Keep binary masks,
   multiclass maps, organ/lesion pairs, point coordinates, boxes, scalar
   probabilities, spectral bands and written reports distinct.
2. Extend a primitive in `task-art.js` when a new subject needs recognizable
   context. Maintain spatial correspondence between the input sketch and its
   output marks. Prefer named targets to a generic blob. Existing source-derived
   3D anatomy is reusable through `AnatomyAssets`, with its original provenance.
3. A new deliverable needs an explicit SVG recipe and story recipe. The routing in
   [mode.ts](../../frontend/task-visuals/mode.ts) determines which tasks also need
   a 3D recipe in [recipes.ts](../../frontend/task-visuals/recipes.ts). Keep static
   tasks in the SVG library; do not add parallel, unreachable 3D recipes. Teaching
   actions and cues belong in `task-story.js`.
4. Keep the input/action/output sequence readable at rest. Spatial tasks use one
   compact stage selector; 2D tasks show paired input/output diagrams. Animate only the actual
   operation: region labeling, correspondence, phase change or reconstruction.
   Retain a legible reduced-motion state and the static fallback.
5. Keep output diagrams labeled illustrative. Never choose an arbitrary
   diagnosis, fabricate a numeric result, or reveal an evaluator answer.
   Original geometries are explanatory drawings, not anatomical validation.
6. Run `node tests/task_scene_models.cjs` (which bundles the real modules through
   the production Vite transforms), build the standalone Explorer, and
   inspect representative desktop and mobile scenes with the existing browser
   harness. Source/reference reveal behavior is covered by the full Explorer
   browser check.

The palette agrees with 3D scene legends: teal `#299786`, gold `#c38a36`, blue
`#548ab0`, rose `#bc708a`. Use a dashed line only when its meaning is named in the
legend. Local SVG text and card captions provide a useful explanation even if
Canvas and WebGL are unavailable.

See the [Task Brief rulebook](../../task-explorer/RULEBOOK.md) for the complete
content, provenance and reference-visibility contract.

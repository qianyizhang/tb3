# Task Brief authoring rules

Follow the [presentation design](../DESIGN.md) for language, reading hierarchy,
typography and provenance disclosure. Update it when a reader-facing decision
changes; this rulebook owns the brief's detailed content contract.

Accepted by the user on 2026-09-21 in [the design discussion](../../discussions/task-brief-format.md).
A **Task Brief** explains one task definition; the **Task Explorer** makes definitions,
assistance conditions and cases navigable. Write for technical readers without
specialist medical knowledge. Use the same format for existing and proposed tasks.

## Content contract

Start from the [Markdown template](brief-template.md). Its headings are the small
renderer interface, grouped into six reader questions:

1. **Task and value:** a concrete action and a short clinical/scientific motivation.
2. **Given:** original data, supplied helpers, callable tools and reference-only material.
3. **Contract:** required actions, meaningful constraints and permitted assistance.
4. **Deliverable:** a concrete output shape/example and the actual scoring scope.
5. **Visual explanation:** input, helper overlay and a reference/output reveal.
6. **Difficulty and evidence:** work remaining after assistance, sources and gaps.

Aim for a 60–90 second first read (about 150–250 words plus visuals). Put full
schemas, methods and result analysis behind links or expandable sections. Explain
necessary terminology where it appears. Clinical motivation is not a claim of
clinical validity. A model score is not required for a brief to be useful.

Keep the exact solver prompt and scorer authoritative. Reader-only answer reveals
must not become solver inputs. Proposed briefs explicitly identify unresolved
references, scoring and resources; their presence never launches a trial.

## Assistance and variants

Describe what is actually supplied, including derived artifacts: masks, crops,
landmarks, answer lists, algorithms, code, checkpoints and tool-generated outputs.
Separate pre-supplied files from callable tools and evaluator-only references.
If source staging was not inspected, say so rather than assuming data is hidden.

One common brief covers repeated cases. The catalogue offers capability and
repository views, then family → definition/revision → conditions and cases.
The [task taxonomy](../../docs/task-taxonomy.md) separates primary deliverable,
secondary operations, agent work, research role and group ownership.
Give meaningful changes in the
contract their own definition or condition. Every imported case remains reachable;
do not treat one illustrated case as exhaustive coverage. Source-published counts,
imported identifiers, authored briefs and available media are distinct coverage facts.

## Visual contract

- Start with input. Supplied-helper views are separately selectable. Reference
  answers and actual predictions appear only after an explicit reader reveal.
- Use a native/source-derived example when available. Identify any post-hoc crop,
  selected plane or camera, especially when it reduces the localization problem.
  Keep that selection caption beside the image in Overview as well as Example.
- Label reference, illustrative output and actual agent prediction separately.
  Preserve orientation/physical aspect; avoid caliper claims on explanatory layouts.
- Describe why assistance makes the task easier and what remains difficult.
  Evidence supports a difficulty claim; a conceptual drawing alone does not.
- Retain figure source, caption, attribution, relevant terms and derivation.
  Reuse existing tours as optional modules; keep a useful static fallback.
- Missing assets stay explicit. Dataset acquisition and model execution are
  separate actions. When the user requests sample acquisition, fetch bounded
  individual cases, retain source terms and checksums, and label exact task cases
  versus representative examples. Downloading inputs does not authorize model runs.
- The user explicitly requested original SVG illustrations when real examples are
  unavailable. Put a meaningful input/output picture directly in Overview. Use
  source images where curated; otherwise label the figure “Conceptual illustration”
  and “Drawn, not a dataset sample.” A drawing closes an explanation gap, not a
  native-data or anatomical-validation gap.
- The collection's `illustration` metadata selects an authored drawing type and
  concise visual labels/caption. Use an explicit `subject` for anatomical drawings;
  never infer anatomy from substrings in a task ID. Without a specified subject,
  use a neutral image sketch. Keep drawings tied to the brief's actual deliverable:
  one probability is not a time curve, a binary mask is not a multiclass map,
  and an organ/lesion pair is not one undifferentiated segmentation. Do not fabricate
  measured improvements, patient findings, clinical thresholds or reference answers.
  Geometry and textures are stylized. Cite the task source for any numerical dimensions.
  `presentation/assets/teaching/` owns reusable SVG primitives, task art and
  plain-language action recipes, shared by storyboards and the static fallback.
  See [asset reuse](../assets/README.md). The typed modules under
  `presentation/frontend/task-visuals/` own rendering: `anatomy.ts` adapts retained
  geometry, `geometry.ts` builds shared shapes, `recipes.ts` owns task choreography,
  `stage.ts` renders Three.js surfaces and projected labels, and `TaskVisual.tsx`
  owns accessible React controls and the static fallback. `use-scene-player.ts`
  owns the on-demand animation lifecycle. All assets remain embedded offline.
- Every named entry, including supporting research and each grouped variant,
  needs an Overview visual. The composed catalogue enforces this with
  `require_overview_visuals: true`. Spatial illustrations open as conceptual 3D scenes, paused on the input stage; 2D-first illustrations show input and output together. Curated input
  images remain above the teaching scene in the normal reading path with their
  complete captions, and in Example. The animation remains available when optional
  media are absent. Keep the missing-media notice visible beside that fallback.
  The 2D-first routing is explicit in `taskSceneMode` in `mode.ts`; a new kind must be
  reviewed against its output form before adding it there. A named segmentation
  target without a matched reusable 3D surface stays 2D-first rather than
  borrowing an unrelated organ or generic lesion shape. The Chinese view
  translates scene controls and marks untranslated authored recipe text as
  English source copy.
  For supporting research, label the right panel “Study output” and show the
  actual comparison or curation question rather than an implied agent success.

### Animated 3D scenes

On 2026-09-22 the user requested replacing the ordinary infographics with animated
3D illustrations, citing [OnCo Technologies](https://onco.cc/technologies/).
The user subsequently asked for more detailed, distinguishable shared organ
assets. Source-derived organ surfaces and authored schematics use that visual
direction; no site geometry or code is copied. The three stages are Input,
Process and Output (Study output for
supporting research). Their text comes from the task's illustration metadata.
These explain task structure; they are not presented as reconstructions or
evaluated results for the selected case.

The user later asked for clearer, more intuitive animation. Keep a labeled
input → action → illustrative output sequence in the stage selector, including
when playback is paused. Avoid duplicating the 3D stage with SVG thumbnails. Prefer recognizable image planes,
anatomical context and explicit targets over unmarked generic volumes. The
storyboard explains the expected output format; native references remain under
their separate reveal. Shared assets and action descriptions have one owner in
`presentation/assets/teaching/`.

- Common anatomy lives in `anatomy/` and `anatomy.ts`. Eighteen compact
  source surfaces retain source/output hashes and derivation in their manifest.
  Normal builds embed the retained assets without scans or scientific runtimes.
  Keep source-case provenance, attribution and licenses in the expandable model
  notice. Describe them as shared teaching anatomy, not a selected-case result.
- Preserve relative size and position within a source-derived assembly. Fit
  individual organs independently only for explanatory display. The distant torso
  uses lower-detail meshes; the close abdomen and individual organs keep fuller detail.
  Brain and dental procedural shapes remain explicitly authored schematics.
  Display-only subdivision softens retained organ surfaces without changing
  source assets. Weld procedural seams and poles; use bounded relief and rounded
  dental roots. Transport vessel cross sections along their paths to avoid twists.
  See [asset provenance and rebuilding](anatomy/NOTICE.md).

- Use one material language across the catalogue: softly shaded physical forms,
  shallow image/signal/document panels, restrained colors and a quiet background.
  Sculpted Atlas uses warm neutral anatomy for context, teal for the selected
  structure and gold for the operation or spatial witness.
  Imported anatomy and procedural shapes share the same triangle material and
  lighting. Detailed anatomy is a reusable content asset, not a separate style.
  Do not expose tessellation edges or add decorative background grids and rings.
- Choose the representation from the actual deliverable. Segmentation, motion,
  correspondence and routes use surfaces with explicit marks; reconstruction and
  physical estimates use image/slice panels, fields or directional glyphs; records,
  classification and reports use planar evidence cards. A scalar stays a scalar.
  Supporting audits and calibration reuse these forms with labeled comparisons.
- Reserve linework for information: supplied contours, localization boxes,
  correspondence paths, graph connections and explicitly dashed references.
  Draw annotations above physical surfaces so solid geometry cannot hide a
  landmark, nucleus center or graph node. This is explanatory display layering,
  not a claim that the point lies on a source-derived anatomical surface.
  Show registration source and target in separate frames so both remain legible.

- `recipes.ts` explicitly maps each illustration kind to a scene recipe. Use
  `subject`, optional `target` and optional `scene_variant` metadata for anatomy
  and target-specific geometry; do not infer anatomy from task IDs.
- Preserve distinctions between binary/multiclass masks, separate organ/lesion
  masks, points, boxes, paths, scalar probabilities, wavelength stacks and reports.
  Legend colors and line styles must agree with the scene and its caption.
  Image detections use planar boxes; volume detections retain depth. Moving cavity
  surfaces do not imply tracked material particles. Classification shows an output
  schema, with the authored possible labels expandable below it, rather than an
  arbitrary diagnosis assigned to the conceptual input.
- Explicit playback makes one ten-second pass through three stages, then settles
  on the output. Replay starts again at input. Stage selection pauses; Play resumes
  from input or process; Reset restores the initial input and camera. Stage changes settle immediately into a deterministic still. Keep the camera fixed
  during playback so motion belongs to the task rather than a spinning presentation.
  Pointer dragging and keyboard arrows rotate the model. Reduced-motion starts paused and pauses an
  already running scene when the preference changes. Do not add decorative transitions under reduced motion. Use bounded, eased task movement rather than continuous decorative motion.
- Only visible scenes animate, targeting at most 60 frames per second with a
  capped pixel ratio; static stages reuse their pose without repainting. A shared
  Three.js WebGL2 renderer provides smooth matte lighting and depth-tested surfaces, with a
  bounded geometry cache. Navigation releases buffers, callbacks and observers;
  hidden tabs and off-screen canvases stop scheduling frames.
- The standalone build contains the renderer and all geometry, with no remote
  scripts, models or textures. If WebGL is unavailable or lost, the accessible SVG input/output pair is built
  on demand. The fallback is also available when Canvas is unavailable. Native references still require the
  separate Example reveal.
- The browser matrix renders all three stages for every variant, preserves source
  captions and checks motion, pause, reset, pointer/keyboard controls, reduced
  motion, single-pass/replay behavior, transitions, off-screen suspension, navigation
  cleanup, GPU and Canvas fallbacks, mobile layout
  and zero remote requests. Browser-free geometry checks cover dimensionality,
  mask classes, motion semantics and reference styles. Geometric schematics do
  not certify anatomical accuracy.

## Small authoring surface

- The brief Markdown owns its explanatory content. The collection `catalog.json`
  owns navigation metadata and points to it; it does not duplicate the prose.
  A brief ID identifies a definition. An optional `repository_id` connects several
  distinct briefs to the same imported repository inventory (`--repository-id`
  when scaffolding). Inventory rows point to their shared `brief_id` when authored.
- A collection can set `require_brief_coverage: true` once its imported inventory
  is backfilled. Checks then reject unlinked entries, cross-repository brief links
  and invalid condition indices. This guarantees an explanation, not a native image.
- Offer capability and repository navigation and list each shared task definition once.
  Modality is a separate authored filter axis: retain explicit `modalities` IDs
  from the shared taxonomy, allow multiple tags for source/target or alternative
  conditions, and do not derive modality from a task ID. Unspecified imaging and
  non-image inputs must remain distinguishable. Filters compose and survive URL
  navigation without merging different task contracts.
  Put repeated cases beneath their task, with short labels and only sourced differences
  (for example candidate-pool size). Never infer a clinical description from a case ID.
  Selecting a case must retain its source and condition across reload/back navigation.
- Consolidate repeated workflows into one task-family entry when their differences
  are datasets, targets, modalities or label taxonomies. `task_families` owns the
  shared navigation title and selector label; each brief's `task_family` links to it.
  `nav_label` gives the concise variant name. Changing the variant loads its exact
  input, helpers, output, scoring and source; it does not assert executable equivalence.
  Preserve release labels and compatible assistance selection. Keep fundamentally
  different transformations or deliverables separate, even in the same anatomy.
- Use `nav_group` for collapsible subject/workflow sections containing distinct
  tasks, such as MRI methods. Do not merge their scientific methods merely because
  they share an input modality. Search opens matching sections; deep links select
  the exact variant. Source identities and historical briefs remain intact.
- Show one task explanation with Overview, Requirements, optional Example and Sources
  sections. Do not repeat it in a separate catalogue preview, or mark every record with
  a universal availability badge. Omit summaries that only restate their title.
- Keep family/definition IDs, source conditions, counts and revisions in expandable
  provenance. Surface details that change the reader's understanding of the selected
  task. Missing examples do not need a repeated pseudo-visual made from the input text;
  authored geometric drawings should show the actual transformation or output structure.
- The optional `Cases` brief section explains what varies between cases and which
  inputs have actually been imported. Inventory `case_context` facts are specific to
  one source record and carry their own source URL. Repository introductions remain
  small navigation metadata; substantive task explanations stay in Markdown.
- Shared explanations across releases must label their scope. Similar task names
  do not establish identical data, model guidance or scoring. Keep the exact source
  link visible, and call out any unresolved difference next to the shared brief.
- Internal briefs live with the group's presentation. External survey briefs
  live with their source discussion. Existing evidence cards and frozen protocols
  remain source records; link them rather than modifying historical outcomes.
- `proposed: true` in a catalogue entry labels an unfinished task definition.
  This is a content qualifier, not a new experiment assessment/status system.
- The inventory records source IDs, source URLs/revisions and coverage limitations.
  It need not contain native datasets or materialize generated benchmark tasks.

```sh
# Scaffold only; creates a proposed brief and navigation entry, never an experiment.
med brief new my-task --title "Locate a named landmark" \
  --repository "TB3 medical workbench" --repository-id tb3 --family localization \
  --catalog groups/anatomical-landmarks/presentation/catalog.json \
  --destination groups/anatomical-landmarks/presentation/briefs/my-task.md

# Standalone HTML; inputs and images are embedded, no server or remote assets required.
med brief build --output runs/task-explorer/index.html
med brief check
```

The default collection is `presentation/task-explorer/catalog.json`. It composes
group-owned internal catalogues and the external survey catalogue. Use `--catalog`
with an owning leaf collection when scaffolding; the root composition is not a
content owner. Each entry uses controlled category, role and agent-work IDs;
scoped experiment links resolve current protocol locations without changing
frozen bytes. Supporting entries are excluded from agent-task counts.
The reusable `author-task-brief` skill discovers this rulebook; keep domain-specific
rules here. It does not copy this file into user-level skill storage.

Check rendered input/helper/reveal states, condition switching, navigation and
mobile layout after renderer changes. Offline checks cover source resolution,
stable identities and build safety. They do not certify anatomical correctness,
reference quality or reproduction of an external benchmark.

The optional browser regression check uses an existing Playwright installation
and Chrome; it does not install dependencies or retrieve external data:

```sh
node tests/task_explorer_ui.cjs runs/task-explorer/index.html runs/task-explorer/qa.json
```

Set `PLAYWRIGHT_MODULE` to the module path when it is outside the normal Node
lookup path. `TASK_EXPLORER_SCREENSHOTS` optionally selects a local screenshot
directory. The check covers every imported source link and assistance condition,
case differences, legacy routes, reference reveals, search and narrow layouts.

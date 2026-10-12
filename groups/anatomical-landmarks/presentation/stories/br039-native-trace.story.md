---
schema: 2
id: br039-native-trace
title: Follow a native CT landmark inspection and its wrong-level claim
locale: en
purpose: Explain selected recorded views, weighted centres and saved availability
  judgments inside the supplied CT crop, then reveal the frozen reference boundary.
scope: One retained BR-039 Terra/high partial-CT attempt on VerSe sub-verse823.
  Source centroids and availability conventions are engineering references;
  this condition does not establish population performance or clinical precision.
recipe: native-trace-v1
manifest: groups/anatomical-landmarks/presentation/native-landmark-trace/native-trace.json
fps: 24
reference_policy: reader-reference-reveal
source_class: source-derived-teaching
source_locators:
- groups/anatomical-landmarks/presentation/native-landmark-trace/canonical-mapping.md
- groups/anatomical-landmarks/presentation/native-landmark-trace/README.md
- groups/anatomical-landmarks/presentation/briefs/tb3-named-landmarks.md
- groups/anatomical-landmarks/presentation/sources/named-landmark-audit.json
- groups/anatomical-landmarks/presentation/sources/named-landmark-source-terms.json
---

# Follow a native CT landmark inspection and its wrong-level claim

Seven discrete 168-frame chapters at 24 fps; 1176 frames total. Holds
are reader timing, not elapsed agent time. The retained original story and historical acceptance remain separate; renderer
regression is documented by the group-owned review record.

## 1. Receive the crop and names

```beat
id: input
scene: input
frames: 168
caption: Twenty-six names, one supplied native crop.
narration: The solver received a 512 × 512 × 920 CT crop, 26 target definitions and an index-to-RAS affine. Native i, j and k increase left, anterior and superior. The original full scan was not this input.
visual: Native indices and physical spacing connect the entire supplied crop;
  the coarse preview and unmarked poster are reader displays derived from it.
state: crop
trace_steps: [7, 12]
reference: false
```

## 2. Inspect long views

```beat
id: search
scene: search
frames: 168
caption: Requested views expose the spine inside the crop.
narration: The solver requested long spine views at two native centres, each with a 180 mm radius. Switch recorded inspections to connect an exact delivered image to its location in the crop. Cyan marks requested views, not detected landmarks.
visual: Exact delivered images at steps 11, 15 and 17; physical requested-view
  extents are distinct from the bounded whole-crop preview.
state: spine-body
trace_steps: [9, 10, 11, 14, 15, 16, 17]
reference: false
```

## 3. Compare planes and projections

```beat
id: projection
scene: projection
frames: 168
caption: A native slice and a slab projection show different evidence.
narration: The solver compared three sagittal planes and two maximum-intensity projections. A slab combines multiple native slices; a plane does not. Select a recorded inspection to see its exact bounds and the image actually delivered.
visual: Toggle the retained sagittal planes and the two bone projections;
  the delivered panel pixels remain exact original observations.
state: sagittal-mip
trace_steps: [18, 19, 20, 21, 22, 23, 24]
reference: false
```

## 4. Check candidate levels in depth

```beat
id: levels
scene: levels
frames: 168
caption: Axial checks test fourteen selected body levels.
narration: The solver inspected fourteen axial levels, then local T4-labelled and L5-labelled views and a lower montage. Those names and levels were its choices, not the reference inventory. Switch recorded inspections to follow the checks.
visual: Exact step-27 axial montage, steps 29 and 30 local views and step-33
  lower montage; keep the native k list beside the crop.
state: candidate-levels
trace_steps: [26, 27, 28, 29, 30, 32, 33]
reference: false
```

## 5. Compute image centres

```beat
id: centres
scene: centres
frames: 168
caption: Weighted centres cross-check the chosen body regions.
narration: The solver calculated intensity-weighted centres inside chosen bone regions. Select a logged 2D or 3D centre to inspect its point and ROI. These rounded coordinates carry solver-authored names; they are not ground-truth segmentations.
visual: Logged 2D centres at step 35, 3D centres at step 37 and their actual ROI
  bounds; no invented point motion or corrected vertebral naming.
state: body-centres
trace_steps: [31, 34, 35, 36, 37]
reference: false
```

## 6. Save positions and availability

```beat
id: output
scene: output
frames: 168
caption: A valid output contract can still carry a wrong level name.
narration: The answer saved all 26 statuses, including a T4 point at [269.8,154.6,906.1]. It rejected C1–T3 as outside the crop and T13/L6 as absent. The final contract check validated format and coordinates, not anatomical naming.
visual: Exact saved JSON and evidence account. Positions are fractional native
  indices; world coordinates derive from the supplied affine.
state: saved
trace_steps: [39, 40, 41]
reference: false
```

## 7. Reveal source and frozen outcome

```beat
id: reference
scene: reference
frames: 168
caption: Compare the saved name and position with the source reference.
narration: The saved T4 claim is 2.142 mm from source T5. Source T4 lies beyond the crop. The frozen result separates visible-target localization from outside/absent judgments; this reader comparison does not rerun or revise that evaluation.
visual: Reveal private point/status references only here; preserve saved state
  and show availability and localization denominators separately. Correct outside
  rejections 10/11; correct absent rejections 2/2. Source full-CT intensities excluded.
state: saved
trace_steps: [40, 41]
reference: true
```

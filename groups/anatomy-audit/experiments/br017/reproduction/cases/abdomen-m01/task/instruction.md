# Audit mixed anatomical content in abdominal masks

The proposed label of each object is in /app/data/scene.json. Inspect the CT
and masks for substantial tissue from a different named organ included under
that proposed label. An erroneous inclusion may encompass a whole organ or
only part of it, so a correct label elsewhere does not rule out an error.
Report every affected host mask and the anatomical identity of the included
tissue. The number of findings is unspecified and may be zero.

Only substantial inclusions (at least 5 mL of another organ) are in scope.
Ordinary thin contour differences, native mask overlaps, incomplete scan
coverage and missing class names alone are not reportable findings. A label
need not occur separately. Do not infer surgery or disease. The combined class
portal_vein_and_splenic_vein is intentionally one vessel group. Class spellings
are in /app/data/vocabulary.json.

For each finding, provide one representative physical LPS point within the
wrongly included tissue. The evaluator accepts a point within 3 mm of a voxel
centre in that region. Choose a clear internal point; you do not need to
reconstruct its boundary or quantify its volume precisely. Report the HOST
object ID, not the ID of any remaining correctly labeled donor tissue.

Write /app/answer/answer.json as:
{"findings":[{"object_id":"o123","included_label":"class_name","point_lps_mm":[1.0,2.0,3.0]}]}

Use {"findings":[]} if no inclusion is present. Include each host/class pair
once and no prose fields. Missing, extra or wrong host/class findings fail;
localization is graded with the stated tolerance. Correct portions need no
finding. The starter answer is invalid until you write your decision.

## Data and inspection tools

All masks and original CT samples share physical LPS millimetres: +x patient
left, +y posterior and +z superior. Each object NPZ holds mask (binary),
affine_lps ([i,j,k,1] to LPS) and surface_lps (boundary voxel centres). Independent
masks may overlap. The CT NPZ holds hu (int16 Hounsfield units) and affine_lps.
The arrays are authoritative; PNGs are previews. No original reference masks
or clinical diagnosis are supplied. Object IDs, order and colours are arbitrary.

Start with overview.png, ct-overview.png and ct-<object_id>.png in /app/data/.
Every target has a ready axial/coronal/sagittal CT outline preview. Python,
NumPy and Pillow are installed. Additional calculations and tools are allowed.

```sh
python /app/inspect_scene.py
python /app/inspect_scene.py --objects o123,o456 --yaw 75 --pitch 20 --out /app/focus.png
python /app/inspect_ct.py --objects o123 --plane axial --out /app/ct-focus.png
python /app/inspect_ct.py --objects o123 --plane coronal --no-overlay --out /app/ct-plain.png
```

Replace example IDs with actual ones from scene.json. load_scene() from
inspect_scene.py gives the masks, transforms and proposed labels. The CT helper
supports axial/coronal/sagittal views, --positions for comma-separated physical
plane coordinates, --span for field of view in mm, --level/--width for windowing
(default 50/400), and --no-overlay. Without positions it shows five slices
through the selected objects. For negative lists, --positions=-195,-185 works.
No external source/patient matching is needed. See /app/SOURCE_NOTICE.md for
attribution. Decide whether each supplied mask includes the wrong anatomy.

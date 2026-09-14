# H04 — DICOM patient planes to SVG

BR-003; user-recalled SVG difficulty is a sourcing lead, not a recovered prior
benchmark failure. This task isolates geometric reconstruction/rendering from
the anatomical judgment in H03.

One TotalSegmentator CT/mask source is sampled at 3 mm and rigidly tilted by
17 degrees about z and 11 degrees about x, around its volume center. The pose
change is synthetic and disclosed; it is not a claim about the source scanner.
All fields are consistently transformed. There are 91 derived CT instances and
2,116 sparse BINARY SEG frames. Filenames/Instance Numbers are permuted, local
Segment Numbers differ from upstream class IDs, and Segment Sequence is reversed.
The DICOM source references, geometry and pixel content remain valid.

Four query points yield twelve views. The reference reconstructs DICOM pixels
by source UID and acquisition geometry. Independent expected masks come from
the original NIfTI label array and the transformed affine, bypassing all DICOM
ordering and decoder logic. The returned SVG is rendered with CairoSVG and
compared per label. All 72 author label/view comparisons have Dice 1; absent
labels are retained as empty controls. Mirrors, transposes, empty canvases and
rectangular envelopes fail each view. These are controls, not model trials.

The tested surface is one regular oblique acquisition and one fixed cohort of
queries. No nonuniform slice stacks, deformable registration, fractional SEG,
multi-frame CT, external images, or clinical conclusions are implied. Agent
may use highdicom and may embed raster masks in SVG. No artificial vector-only
rule, Internet restriction, or short reasoning timeout creates the difficulty.

`build_imaging.py` owns fixture production for H03/H04. Author raw NIfTI inputs
stay local. Required derived DICOM archives and verifier truth are tracked with
exact artifact-policy hashes. Source licenses/attribution accompany both tasks.

# BR-003: history-derived prototype inspection

The owning [round](../../docs/research-rounds/BR-003-work-history.md) records the
user's authorization, source retrieval, predeclared protocol and dispositions.
[Exact receipts](../../docs/evidence/br003-round-summary.json) retain individual
results, source hashes, timings and matching historical task checksums.

## PDF table lineage

Terra completed normally and passed all four content/geometry checks. Its
trajectory rendered the PDF, inspected text and word coordinates with Poppler
and pdfplumber, inspected rotation and line geometry, and wrote the requested
JSON. Using manual interpretation with libraries is permitted. It recovered
the cross-page row identities, inherited families and local footnotes. The
historical crop failures therefore did not transfer to this small fixed
table-transcription artifact. Retire v1; do not add OCR, a batch requirement or
shorter time limits merely to turn this pass into a miss.

## Chat round recovery

Terra completed normally and passed all 22 traces, including timeout boundaries,
stale worker incarnations, retries, retransmission, cancellation and per-room
FIFO. It implemented a durable JSON state machine and ran its own boundary
checks. The last shell command also attempted Git operations in an image
without Git, after successful examples and Python checks. That incidental
exit 127 did not prevent normal model completion or verification and is not
an infrastructure-only model attempt. Retire v1. Real Tavern availability and
external adapter behavior remain outside this deterministic simulation.

## Patient-coordinate SVG

Terra completed normally and passed all 12 views: all 72 label comparisons,
including empty labels, have Dice 1.0. Its submitted renderer derives a CT grid
from IOP, IPP and pixel spacing; uses source UID references for sparse SEG
frames; and maps patient-space samples into acquisition indices. It applies
the specified pixel-center and nearest-voxel conventions and emits exact-color
SVG. The model also rendered its outputs through CairoSVG. The independent
verifier's source-mask truth agrees, so there is no orientation or anatomy
placement failure on this snapshot. Retire v1.

A later user-requested [provenance audit](br003-svg-provenance-audit.md) reviewed
all eight recorded tool calls, verified the prompt and reconstructed the final
artifact from the model's patch. No private reference/generator retrieval was
observed. The task is explicitly mask resampling with supplied coordinate and
rasterization rules; Dice 1.0 does not establish independent anatomical drawing.

## Anatomical annotation QA

Terra completed normally and passed all five packets. It read local segment
numbers by Segment Label, estimated a midline from spine/cord annotations,
used neighboring anatomy to judge coverage, and sampled rescaled CT intensities
under target masks. An intermediate row/column mapping error caused false
laterality findings. The model diagnosed and corrected it before submission;
the final independent verifier passed. This is a successful repair, not a
genuine benchmark failure. The artifact contains reusable geometry and tissue
checks, rather than packet-ID lookup. Its anatomy thresholds remain bounded
heuristics; the five correlated packets do not validate its behavior on other
patients, unusual anatomy or additional label classes. Retire v1.

## Interpretation boundary

Recovered historical reports involve earlier models and uncontrolled sessions;
they are not local Terra failures. The exact historical verdict-timeout and SVG
incidents were not recovered. Passing source controls and rejecting deliberately
wrong implementations establishes a meaningful executable test, not difficulty.
The candidate set has four deliverables, not four independent domain capability
estimates. H03 and H04 share one source CT; all medical-case observations are
correlated. No final standard or adversarial qualification has run.

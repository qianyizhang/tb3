# BR-036 — what the completed trials establish

[Results](BR-036-results.md) · [Source shortlist/protocol](BR-036-semantic-landmarks.md) ·
[Trace audit](../evidence/br036-trace-review.json)

Four normal Terra/high completions, no retries, and eight healthy matched
oracle/nop controls. Host rescoring agrees with every saved submission. Model
runtime identifies gpt-5.6-terra and retained configurations select high effort.
This is trace/config consistency, not independent provider-side identity proof.

## Observed approach and errors

- **Full CT:** generated orthogonal and targeted views, inspected the affine,
  and manually submitted coordinates near each intended structure. One of four
  points met 5 mm. Left-condyle error is mainly 6 mm in the inferior direction;
  the chin also has a substantial lateral error. All four are within 10 mm.
  This is a precision/reference-placement result, not evidence of wholly
  unrecognized anatomy. CT slices are 3 mm thick.
- **Full MRI, eight points:** generated native orthogonal views and submitted
  affine-derived coordinates. Zero of eight met 3 mm; mean 11.18 mm, maximum
  21.13 mm. Only one met 5 mm and four met 10 mm. Recorded calls show no web
  search. There is no controlled intervention isolating perception, selection
  or plotting/coordinate use.
- **Cropped MRI, 32 points:** rendered multiple views, searched general AFIDs/MNI
  coordinates, and submitted AC=[0,0,0], PC=[0,-24,0] with all 32 points called
  observed and inside the FOV. No point met its acceptance rule; none of seven
  absent targets was recognized as out of view. A public progress message
  asserted AC-PC alignment. This assumption does not follow from a RAS-oriented
  affine. Source derivative metadata says native subject space; source AC is
  [0.604,17.962,-18.594] mm. Matching NIfTI qform/sform and reference overlays
  support the supplied geometry. The trace supports inappropriate anatomical
  coordinate anchoring, but not a claim that this alone explains every miss.
  The general search returned protocol/dataset material, with no observed
  source-subject coordinate retrieval; this was permitted reference use.
- **Cropped CT:** correctly marked chin and dens outside the acquired field and
  returned null. Both visible condyles were localized but missed 5 mm (12.03 and
  5.63 mm). Thus 2/2 outside decisions succeeded, 0/2 visible localizations met
  tolerance, and 2/4 total query rules passed. This is a positive missing-FOV
  handling control, despite the overall task reward of zero.

## Interpretation

The user proposed this as an expected easy capability. These observations do
not support reliable millimetric accuracy on this small pilot. They also do not
justify promoting it immediately to a validated hard benchmark: only two subjects
were used, no repeats were run, and no independent blind author solver or clinical
adjudication was performed. The source points remain reference annotations.

The expanded MRI queries and crop were fixed before its outcome; original task
snapshots were not edited. One in-view MRI point has a 3.138 mm maximum rater-to-mean
deviation, which matters near the 3 mm cutoff, but does not explain errors of
roughly 8–28 mm in that condition. Null and bounded extrapolation were both
accepted for out-of-view targets; Terra was not required to guess.

CT full/crop share four queries but use different fresh attempts. MRI full/crop
also change from eight to 32 queries, so their contrast does not isolate the
causal effect of cropping. Crops are deliberate truncations of a complete scan;
results do not measure natural acquisition variability or anatomical absence.

The old investigation, published presentation and sibling submission are unchanged.
No further model trials are queued. Keep these as calibration/reference-disagreement
results until a separately requested replication or validity review is performed.

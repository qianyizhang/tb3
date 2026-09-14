# E05: clean pass; retire

Terra/high passed all 36 canonical tensor cases with normal completion,
reward 1 and no exception in 27.022245 agent seconds. The model and oracle/nop
share Harbor checksum
`0e94c95a503552860e53e6ea7963ce200d2920b24444904c369f29882daee105`;
the pretrial workshop hash is unchanged.

The delivered function expands six values in standard Voigt order and
converts virial by `-W / abs(det(C))`. It keeps components in the laboratory
basis and passes the three public examples. The private checks cover six
cells, two rotations and three equivalent encodings; H05 is not supported.
The source benchmark's larger API/parsing/round-trip misses do not transfer
to this smaller original task. Retire without adding format ambiguities.

The reference and an independent extxyz reader baseline both pass 36/36 on
host and Linux. Targeted wrong-order, sign and volume controls fail. Transpose
of a symmetric tensor correctly remains accepted. An unavailable initial
Linux package pin was corrected before the freeze and before any model run;
it is an author environment issue, not a failed trial.

Evidence: [freeze](../../docs/evidence/stress-pilot-freeze.json),
[summary](../../docs/evidence/stress-trial-summary.json),
[controls](../../docs/evidence/stress-author-controls.json).
This is the eleventh valid local Terra pass. Static sanity is 21/22; only
final human-authored README material is absent. Final submission gates remain
open and this calibration pass is not an original hard-task submission.

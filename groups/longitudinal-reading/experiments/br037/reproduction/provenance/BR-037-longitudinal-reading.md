Source: `docs/research-rounds/BR-037-longitudinal-reading.md`; original SHA-256: `87241ff4ac45643cf4c54fa4b65ee445d157c030bc50ecbdaa2bb3472410f975`.
Repository source locators below are provenance; they are not required runtime inputs.

# BR-037 — longitudinal imaging synthesis

## Authorization and scope

2026-09-17, current conversation (exact source message ID unavailable): the user
approved ACRIN-DSC-MR-Brain and I-SPY2 as candidate pools and requested curation of
a few longitudinal cases, explicit neutral deliverables, grounded targets,
Terra/high trials, prompt-cue controls where needed, and trace/behavior analysis.
Sol and task refinement after failures are reserved for a later user decision.
This is an exploratory capability experiment, not a known benchmark-backed
failure or a continuation of the closed submission.

## Prospective design

- Inspect access and source dictionaries for both pools; never bypass a controlled
  access requirement. Select a small, source-ordered, reference-stratified cohort
  before any model outcomes. Retain all exclusions and source receipts.
- Supply full available source image volumes at selected visits, with acquisition
  metadata and neutral relative timing. Withhold source identifiers, outcome
  fields, masks, measurement annotations and diagnosis-bearing private tags.
  Record any omitted imaging sequences. No answer-conditioned slice selection.
- Ask for findings with image locations, longitudinal changes, an evidence-bounded
  impression, uncertainty, and a prospective forecast if supportable. The same
  schema applies across cases; do not demand a diagnosis-specific artifact.
- Separate source-backed measurements/outcomes, curator imaging hypotheses and
  unadjudicated clinical interpretations. A forecast mismatch alone is not a
  demonstrated reasoning failure. No clinical expert adjudication is implied.
- Freeze packets and targets before Terra/high. One natural attempt per frozen
  condition, ample time, no automatic retries after infrastructure/timeout errors.
  A matched prompt-cue condition may add a leading interpretation without changing
  image bytes or the required output. Keep it explicitly separate from baseline.
- Preserve tool traces, returned image evidence, revisions and output. Analyze
  visible behavior, not hidden reasoning. Public-data training exposure remains
  unknown even without source-case lookup.

## Ownership

Own only `probes/longitudinal-reading/`, `runs/br037-longitudinal-reading/`,
`runs/br037-*` trial jobs, this document and `docs/evidence/br037-*`. Preserve
concurrent BR-018 and BR-036 work. Raw DICOM, clinical spreadsheets, prepared
volumes, frozen runnable packages and trajectories stay in ignored `runs/`.

## Status

**Completed 2026-09-17:** source and behavior review (repository source locator: `BR-037-results.md`).
Three I-SPY2 neutral attempts and one paired cue attempt completed normally on
Terra/high; all eight mechanical controls were healthy. No composite clinical
success rate or independently adjudicated diagnostic failure is claimed. P02's
full-phase extent assessment and P03's method-dependent cue contrast are the
main follow-up candidates. No further run is queued. The access findings below
record the source audit that preceded these trials.

ACRIN-DSC-MR-Brain is currently controlled-access and absent from the current
public IDC index. Its open clinical archive has been fetched for metadata
triage; no controlled image access has been attempted. Approved access/local-copy
availability was asked asynchronously. I-SPY2 is publicly available under CC BY
4.0 and its clinical/measurement dictionaries have been fetched with hashes.

## Prospective I-SPY2 selection

Join the 384-case four-visit measurement table to the clinical workbook and
current public IDC index. Sort by numeric subject ID. Choose the first case in
each prespecified source-label stratum: (1) early functional tumor volume (FTV)
reduction >=50% with pCR=1, (2) reduction >=50% with pCR=0, (3) reduction <=20%
or increase with pCR=0. These thresholds define sampling strata, not clinical
diagnostic rules. This is a deliberately stratified three-case sample, not a
prevalence or calibration cohort. Selection has occurred before model outcomes.

P01=ISPY2-102011, P02=ISPY2-111344, P03=ISPY2-100899. Download every released
non-VOLSER MR series for all four visits; VOLSER objects are core-lab cropped or
derived analysis data and are excluded from solver input. Only first two visits
will be visible to the model; later visits and surgical pCR stay host-only.
Native scouts may require per-plane handling rather than a fictitious 3D stack.

Source FTV/longest-diameter trajectories are measurement references, not a
complete clinical report. FTV uses an enhancement threshold and operator VOI;
it is not interchangeable with anatomical diameter or viable cancer volume.
Later imaging and pCR predictions are exploratory and scored separately from
present-image evidence. Curator morphological impressions remain provisional.

After geometry and image validation, run one neutral Terra/high attempt per
case and one same-image P03 prompt-control attempt with a deliberately unverified
claim of complete disappearance. This tests susceptibility to a misleading
interpretation, not malicious tool behavior. Both use the same deliverable schema.
No Sol trial or iterative task hardening is authorized in this round.

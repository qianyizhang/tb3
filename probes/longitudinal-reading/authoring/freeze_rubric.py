"""Freeze an evidence-tiered review rubric before reading model answers."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading'
out=B/'review-rubric.json';assert not out.exists()
cases=json.loads((B/'grounding.json').read_text())
rubric=dict(
 scoring='No composite clinical pass/fail. Contract reward is separate from this review.',
 criteria=[
  'Correct source-annotated dominant breast side and image citations within the source VOI; report geometric distance without claiming precise contour truth.',
  'Compare reported longest diameter with the source longest diameter for each visible visit; report absolute disagreement, not a fabricated clinical tolerance.',
  'Describe extent, signal behavior and morphology separately. Compare any quantitative enhancement-burden claim to FTV, while preserving the distinction between FTV and intensity/diameter.',
  'Identify persistent abnormality where visible; do not equate lower enhancement or size with histologically proven clearance.',
  'Diagnostic specificity must be bounded by missing pathology/treatment details. Source cancer status supports malignancy context, not an exact imaging-only subtype.',
  'Forecast is exploratory. Compare it to the withheld next-visit diameter/FTV. An uncertain or incorrect forecast on one case is not by itself a clinical reasoning failure.',
  'Assess search coverage, image delivery, phase selection, coordinate/laterality handling, numerical methods, and explicit revision from observable tool calls and artifacts.',
  'P03 cue comparison: did the false disappearance suggestion change persistent-lesion reporting, measurements, confidence or interpretation? Single attempts cannot isolate a population prompt effect.'
 ],
 evidence_tiers=dict(independent='Published clinical worksheet, core-lab FTV/diameter values and annotated VOIs; source pixels.',provisional='Curator visual morphology and interpretation, no independent radiologist adjudication.',unknown='Training exposure, exact histological subtype, general performance, biological certainty of future behavior.'),
 cases=[dict(case=c['case'],side=c['references'][0]['laterality'],diameter_mm=[10*c['labels'][f'LD_T{i}'] for i in range(4)],ftv_cc=[c['labels'][f'VOLUME_TUM_BLU_V{i+1}0'] for i in range(4)],pcr=c['labels']['pCR'],visible_visits=['V1','V2'],withheld_visits=['V3','V4'],important_contrast={'P01':'Early FTV collapse with nearly unchanged source longest diameter; later pCR=1.','P02':'Early FTV decreases substantially, diameter decreases little and measurable abnormality persists; later pCR=0.','P03':'Early source FTV rises while source diameter decreases; later both decrease, pCR=0.'}[c['case']]) for c in cases])
out.write_text(json.dumps(rubric,indent=2)+'\n');print(hashlib.sha256(out.read_bytes()).hexdigest())

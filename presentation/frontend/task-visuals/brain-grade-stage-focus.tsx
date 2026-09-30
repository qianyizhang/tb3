import { useState } from 'react';
import styles from './brain-grade-stage-focus.module.css';
import type { BrainGradeStage } from './interpretation-b';

/** Source-rule inspection only. It never computes a case grade. */
export function BrainGradeStageFocus({
  operation,
  progress,
}: {
  operation: { stages: BrainGradeStage[] };
  progress: number;
}) {
  const [manualFocus, setFocus] = useState<number | null>(null);
  const focus =
    manualFocus ??
    Math.min(
      operation.stages.length - 1,
      Math.max(0, Math.floor(progress * operation.stages.length)),
    );
  const stage = operation.stages[focus] ?? operation.stages[0];
  if (!stage) return null;
  return (
    <section className={styles.root} aria-label="Static BCER workflow source rule">
      <nav className={styles.stages} aria-label="Inspect required stages">
        {operation.stages.map((item, index) => (
          <button
            key={item.id}
            type="button"
            aria-pressed={index === focus}
            onClick={() => setFocus(index)}
          >
            {index + 1}. {item.id.replaceAll('_', ' ')}
          </button>
        ))}
        <button type="button" onClick={() => setFocus(null)}>
          Follow story focus
        </button>
      </nav>
      <div className={styles.detail} data-stage-focus={stage.id}>
        <h3 className={styles.stageTitle}>{stage.id.replaceAll('_', ' ')}</h3>
        <dl>
          <dt>Requires</dt>
          <dd>{stage.input}</dd>
          <dt>Would produce</dt>
          <dd>{stage.produces}</dd>
          <dt>Structural check</dt>
          <dd>{stage.check}</dd>
        </dl>
        {stage.id === 'brats_mri_segmentation' && (
          <p>
            Declared source labels: 0 background, 1 NCR, 2 edema, 4 enhancing; whole tumor uses 1 ∪
            2 ∪ 4. Dependency failure can trigger a FLAIR/T1c heuristic fallback. Missing bundle
            files can instead raise an error. No segmentation ran.
          </p>
        )}
        {stage.id === 'extract_roi_features' && (
          <p>
            Selected mask is resampled into each image grid. ROI voxels × image spacing product ÷
            1,000 yields volume in ml. No voxels or spacing values are supplied here.
          </p>
        )}
        {stage.id === 'classify_brain_glioma_grade' && (
          <div className={styles.rule}>
            <p>
              <strong>Static code rule:</strong> prefer whole-tumor rows; else consider all rows.
              Use maximum valid nonnegative volume. Default HGG branch is ≥35 ml; below gives LGG.
            </p>
            <p>
              With no valid volume, at least two available texture fields select HGG; fewer select
              LGG. This tests field availability, not learned radiomic values. Formula-derived
              confidence is uncalibrated.
            </p>
            <p className={styles.unset}>
              Case feature value: unset · Predicted grade: unset · True grade: unavailable
            </p>
          </div>
        )}
      </div>
    </section>
  );
}

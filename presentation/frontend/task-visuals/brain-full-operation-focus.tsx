import { useState } from 'react';
import css from './brain-full-operation-focus.module.css';
import type { BrainFullOperation } from './interpretation-b';

const panels = [
  {
    id: 'registration',
    label: 'Route',
    source: 'T1 · T1c · T2 · FLAIR',
    next: 'Check geometry before registration',
  },
  {
    id: 'segmentation',
    label: 'Segmentation',
    source: 'Four aligned modalities',
    next: 'Segmentation and WT mask',
  },
  {
    id: 'features-grade',
    label: 'Features → grade',
    source: 'Segmentation and feature CSV',
    next: 'Rule-based classification JSON',
  },
  { id: 'report', label: 'Report', source: 'Run state and feature evidence', next: 'Report JSON' },
] as const;

/** Source-contract teaching only. Component-local manual focus resets when unmounted. */
export function BrainFullOperationFocus({
  operation,
  progress,
}: {
  operation: Pick<BrainFullOperation, 'report_consumption'>;
  progress: number;
}) {
  const [manualFocus, setManualFocus] = useState<number | null>(null);
  const storyFocus = Math.min(3, Math.max(0, Math.floor(Math.max(0, Math.min(1, progress)) * 4)));
  const focus = manualFocus ?? storyFocus;
  const panel = panels[focus];

  return (
    <section
      className={css.root}
      aria-label="BCER brain workflow source contract"
      data-brain-full-focus={panel.id}
    >
      <header className={css.header}>
        <div>
          <strong>Brain artifact chain</strong>
          <span>Source-code rule · no case, image or observed result</span>
        </div>
        <button
          type="button"
          aria-pressed={manualFocus === null}
          onClick={() => setManualFocus(null)}
        >
          Follow story focus
        </button>
      </header>
      <div className={css.controls} role="group" aria-label="Inspect workflow boundary">
        {panels.map((item, index) => (
          <button
            key={item.id}
            type="button"
            aria-pressed={focus === index}
            onClick={() => setManualFocus(index)}
          >
            <span>{String(index + 1).padStart(2, '0')}</span> {item.label}
          </button>
        ))}
      </div>
      <div className={css.body} aria-live="polite">
        <div className={css.route}>
          <small>REQUIRES</small>
          <p>{panel.source}</p>
          <span aria-hidden="true">↓</span>
          <small>WOULD PRODUCE</small>
          <p>{panel.next}</p>
          <em>All values unset · no tool trace</em>
        </div>
        <div className={css.explanation}>
          <h3>{panel.label}</h3>
          {focus === 0 && (
            <>
              <p>
                Register T2 and FLAIR to T1c only if geometry requires it. Registration is not one
                of the five required success stages.
              </p>
              <p className={css.caution}>
                The suite template mentions registration; the runner-loaded registry makes it
                conditional.
              </p>
            </>
          )}
          {focus === 1 && (
            <>
              <p>
                Segmentation supplies the mask used by later features. If dependencies fail, code
                can use a T1c/FLAIR heuristic; a tiny mask can become an ellipsoid.
              </p>
              <p className={css.caution}>
                Missing bundle files with dependencies present raise instead of taking that
                fallback. A nonempty mask is not anatomical validation.
              </p>
            </>
          )}
          {focus === 2 && (
            <>
              <p>
                ROI features come from the mask. A rule uses whole-tumor volume with a texture-field
                fallback to assign HGG/LGG.
              </p>
              <p className={css.caution}>
                Confidence is formula-derived and uncalibrated. Feature values, predicted grade and
                true grade are all unset here.
              </p>
            </>
          )}
          {focus === 3 && (
            <>
              <p>
                The report reads case state, modality mapping, segmentation status, feature previews
                and WT/TC/ET volumes. A separate configured VLM/QC step defaults to server mode;
                none ran here.
              </p>
              <p className={css.caution}>
                It does not directly read the grade classifier result.{' '}
                {operation.report_consumption.caution}
              </p>
            </>
          )}
        </div>
      </div>
      <footer className={css.footer}>
        <span>Completion ratio: 5 stages + 5 artifact paths</span>
        <span>Separate success: 5 tools · invariants: 7</span>
      </footer>
    </section>
  );
}

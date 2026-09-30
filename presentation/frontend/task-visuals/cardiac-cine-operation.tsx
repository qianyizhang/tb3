import { useState } from 'react';
import styles from './cardiac-cine-operation.module.css';
import type { CardiacPhaseMode } from './interpretation-b';

/** Source-contract branches, never patient measurements. */
export function CardiacCineOperation({
  operation,
  detail = 0,
}: {
  operation: { phase_modes: CardiacPhaseMode[] };
  detail?: number;
}) {
  const [route, setRoute] = useState<'nifti' | 'h5'>('nifti');
  const [chosenPhase, setChosenPhase] = useState<string | null>(null);
  const phase =
    operation.phase_modes.find((p) => p.id === chosenPhase) ??
    operation.phase_modes[
      Math.min(
        operation.phase_modes.length - 1,
        Math.floor(Math.max(0, Math.min(0.999, detail)) * operation.phase_modes.length),
      )
    ];
  return (
    <section
      className={styles.root}
      aria-label="Symbolic BCER cine operation"
      data-cardiac-cine-mechanism
    >
      <div className={styles.controls}>
        <h3>Source route</h3>
        <div className={styles.buttons} role="group" aria-label="Inspect source type">
          <button type="button" aria-pressed={route === 'nifti'} onClick={() => setRoute('nifti')}>
            Cine NIfTI
          </button>
          <button type="button" aria-pressed={route === 'h5'} onClick={() => setRoute('h5')}>
            Raw cine H5
          </button>
        </div>
        <p data-cine-route={route}>
          {route === 'h5'
            ? 'Conditional reconstruction to NIfTI, then segmentation.'
            : 'Enter cine segmentation directly.'}
        </p>
        <h3>Phase provenance</h3>
        <div className={styles.buttons} role="group" aria-label="Inspect phase handling">
          {operation.phase_modes.map((item) => (
            <button
              key={item.id}
              type="button"
              aria-pressed={phase?.id === item.id}
              onClick={() => setChosenPhase(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
        <p data-phase-mode={phase?.id}>{phase?.behavior}</p>
        <button
          type="button"
          onClick={() => {
            setRoute('nifti');
            setChosenPhase(null);
          }}
        >
          Follow story focus
        </button>
      </div>
      <div className={styles.diagram}>
        <h3>Static artifact route</h3>
        <div className={styles.row}>
          <span>Input · absent</span>
          <b>→</b>
          <span>RV / myocardium / LV mask · absent</span>
        </div>
        <div className={styles.fork}>
          <div>
            <span>Mask + image grids</span>
            <b>→</b>
            <strong>ROI-feature CSV · absent</strong>
            <small>Parallel required artifact</small>
          </div>
          <div>
            <span>Mask phase geometry</span>
            <b>→</b>
            <strong>Rule-group JSON · absent</strong>
            <small>Classifier does not read feature CSV</small>
          </div>
        </div>
        <div className={styles.row}>
          <span>Run state + artifacts</span>
          <b>→</b>
          <span>Report JSON · absent</span>
        </div>
        <p className={styles.legend}>
          Source labels: 1 RV · 2 myocardium · 3 LV. EF = (EDV − ESV) / EDV × 100, when EDV &gt; 0.
        </p>
        <p className={styles.limit}>
          No source frame, phase volume, EF, disease group, or report finding is displayed.
        </p>
      </div>
    </section>
  );
}

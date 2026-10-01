import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  images,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  type ImagingUsctFwiState,
} from './imaging101-usct-fwi';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging101-usct-fwi.module.css';
function ReaderRules({ state }: { state: ImagingUsctFwiState }) {
  const [requested, setRequested] = useState(false);
  const previous = useRef(state.frame);
  const backward = state.frame < previous.current;
  useLayoutEffect(() => {
    if (backward) setRequested(false);
    previous.current = state.frame;
  }, [state.frame, backward]);
  const visible = referenceVisible(state, requested && !backward);
  return (
    <>
      <button
        type="button"
        className={css.readerButton}
        disabled={state.reference <= 0.5}
        aria-pressed={visible}
        onClick={() => setRequested((v) => !v)}
      >
        {visible ? 'Cover public reference rules' : 'Reveal public reference rules'}
      </button>
      {visible ? (
        <div className={css.socket} data-imaging-usct-fwi-reference-revealed>
          <b>{reference.role}</b>
          <p>
            Filesystem selects a saved reconstruction, not true speed; source uses the visible
            baseline. All 230,400 cells.
          </p>
          <small>
            No-filesystem scorer requires absent ground_truth.npy. No participant map, score or
            private truth. Exit / backward / reset covers these rules.
          </small>
        </div>
      ) : (
        <p>Public reference rules covered; actual output absent.</p>
      )}
    </>
  );
}
function Native({ index = 0 }: { index?: number }) {
  return (
    <figure className={css.native}>
      <img
        src={images[index]}
        alt={`Native numerical phantom complex observations at ${branches[index]}; real component, receiver rows and source columns, stride two`}
        data-imaging-usct-fwi-native={index}
      />
      <figcaption>
        {branches[index]} · receiver rows / source columns, every second cell. Black − / gray 0 /
        white +; ±{source.native_display.ranges[index].toPrecision(4)} uncalibrated amplitude.
      </figcaption>
    </figure>
  );
}
export function ImagingUsctFwiScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingUsctFwiState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-imaging-usct-fwi-scene={state.scene}
      data-imaging-usct-fwi-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Native phantom signals; true speed / output absent</h3>
          <div className={css.two}>
            <Native />
            <div>
              <b>20 frequencies × 256 receivers × 256 sources</b>
              <p>
                1,310,720 complex cells from a numerical phantom. No time waveform, calibrated Pa or
                patient recordings.
              </p>
              <small>
                Real-component display only. No wave simulation, speed reconstruction or metric.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Keep observed signals separate from the inverse method</h3>
          <nav className={css.controls} aria-label="USCT steps">
            {steps.map((s, j) => (
              <button
                key={s}
                type="button"
                aria-pressed={i === j}
                disabled={!onSeekFrame}
                onClick={() => onSeekFrame?.(operationFrame(plan, j, m))}
              >
                {s}
              </button>
            ))}
          </nav>
          <div className={css.socket}>
            {i === 0 ? (
              <>
                <b>480 × 480 cells · 50 µm · 256 ring positions</b>
                <p>
                  Nominal width 24 mm (2.4 cm); metadata says 24 cm. Preserve this conflict, not a
                  clinical FOV.
                </p>
                <small>
                  Near-source pairs below 7,500 µm muted; zero observations additionally excluded
                  from misfit. No time sampling or density map.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Select native frequency">
                  {branches.map((s, j) => (
                    <button
                      key={s}
                      type="button"
                      aria-pressed={m === j}
                      disabled={!onSeekFrame}
                      onClick={() => onSeekFrame?.(operationFrame(plan, 1, j))}
                    >
                      {s}
                    </button>
                  ))}
                </nav>
                <div className={css.two}>
                  <Native index={m} />
                  <div>
                    <b>Different native frequency, separate display scale</b>
                    <p>
                      128 × 128 direct stride-two receiver/source cells. Color shows signed real
                      amplitude; complex profiles retained.
                    </p>
                    <small>
                      No wave solve, interpolation, amplitude calibration or reconstructed speed.
                    </small>
                  </div>
                </div>
              </>
            ) : (
              <>
                <b>α = Σ(conj(dsrc) y) / Σ|dsrc|²</b>
                <p>
                  Authored dsrc = [1, 2], y = [2, 4] gives α = {fixture.toy_alpha}. Native fitted α
                  and update remain unknown.
                </p>
                <small>
                  Initial speed 1480 m/s; max 3 NCG steps per frequency, low-to-high continuation, 9
                  × 9 gradient smoothing. No gradient/adjoint certification or current convergence.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Participant speed map absent</h3>
          <code>output/reconstruction.npy · 480 × 480 · m/s</code>
          <p>
            Source main saves to evaluation/reference_outputs instead. Saved speed maps are audit
            provenance, never participant output or phantom truth.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later source / generic reference rules</h3>
          <ReaderRules state={state} key={state.beatId} />
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Resolve geometry, calibration and reference identity</h3>
          <p>{source.actual_data_gap}</p>
          <small>
            No clinical property, reconstruction quality, current CUDA success or convergence claim.
          </small>
        </>
      )}
    </section>
  );
}
export function ImagingUsctFwiOutput({ state }: { state: ImagingUsctFwiState }) {
  return (
    <aside
      data-imaging-usct-fwi-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Numerical phantom observations; participant map empty</b>
      <p>Native frequency cells and authored fitting rules.</p>
      <small>
        True speed / calibrated pressure absent. Reader-controlled reference rules; reset / exit
        covers.
      </small>
    </aside>
  );
}

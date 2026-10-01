import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  coilImages,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  type ImagingSenseState,
} from './imaging101-mri-sense';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging101-mri-sense.module.css';
function Coil({ m }: { m: number }) {
  return (
    <figure className={css.native}>
      <img
        src={coilImages[m]}
        alt={`Actual synthetic sensitivity magnitude, ${branches[m]}; no reconstructed image`}
      />
      <figcaption>
        Gray: |S|, fixed 0–.16 display; phase lost. Native 128² stored indices.
      </figcaption>
    </figure>
  );
}
function Mask() {
  return (
    <figure className={css.mask}>
      <svg
        viewBox="0 0 128 8"
        role="img"
        aria-label="Native R3 mask; 54 of 128 rows including 16 ACS"
      >
        {source.native_mask.map((v, j) => (
          <rect key={j} x={j} y="0" width="1" height="8" fill={v ? '#57d1cc' : '#122939'} />
        ))}
      </svg>
      <figcaption>Teal sampled rows ·dark missing; 54/128, ACS 16.</figcaption>
    </figure>
  );
}
export function ImagingSenseScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingSenseState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [showRules, setShowRules] = useState(false);
  const previousFrame = useRef(state.frame);
  useLayoutEffect(() => {
    if (state.scene !== 'reference' || state.frame < previousFrame.current) setShowRules(false);
    previousFrame.current = state.frame;
  }, [state.frame, state.scene]);
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-imaging-sense-scene={state.scene}
      data-imaging-sense-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Actual synthetic coil map; no reconstructed image</h3>
          <div className={css.two}>
            <Coil m={0} />
            <div>
              <b>8 coils · 128×128 · complex source data</b>
              <p>Native masked keys mismatch full-kspace loader; main R4 differs from native R3.</p>
              <Mask />
              <small>
                54 rows ×128 columns ×8 coils=55296 complex values; no patient/FOV/time claim.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Separate coil encoding from a reconstruction outcome</h3>
          <nav className={css.controls} aria-label="SENSE steps">
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
                <b>y_c=M F(S_c x), spatial axes 0/1; coil last</b>
                <p>
                  Centered default FFT, inverse scale 1/16384. Complex sensitivity phase matters;
                  map magnitude is display only.
                </p>
                <small>
                  Authored matrix [[1,2],[3,1]], x=[1,2]→y=[{fixture.toy_values.join(',')}];
                  illustrative encoding, no native solve.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Select native sensitivity display coil">
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
                  <Coil m={m} />
                  <div>
                    <b>Supplied maps, no calibration estimation</b>
                    <p>
                      Stored real/imag float32; complex128 loader convention. Native R3 mask, ACS
                      16; main requests absent full data then R4.
                    </p>
                    <small>
                      Display coil only; no FFT/CG or solver input change. Supplied map power not
                      unity.
                    </small>
                  </div>
                </div>
              </>
            ) : (
              <>
                <b>CG: helper(Ax)=helper(data)</b>
                <p>
                  helper sums conj(S)·IFFT; no mask, scaled inverse rather than arbitrary-domain
                  Euclidean adjoint. Zero start; rtol 1e−5, max 163840; no explicit
                  λ/preconditioner.
                </p>
                <small>
                  First-coil nonzero mask can miss sampled zeros. info discarded; magnitude/max
                  output normalization. No iteration/convergence/result measured.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual reconstruction.npy absent</h3>
          <code>output/reconstruction.npy · 128×128 comparison</code>
          <p>
            Participant image/score empty. Saved source SENSE/RSS outputs remain separate from fresh
            execution.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later source-truth and evaluator rules</h3>
          <button
            type="button"
            aria-expanded={showRules}
            aria-controls="sense-reader-rules"
            onClick={() => setShowRules(!showRules)}
          >
            {showRules ? 'Hide source rules' : 'Reveal source rules'}
          </button>
          {referenceVisible(state, showRules) ? (
            <div
              id="sense-reader-rules"
              className={css.socket}
              data-imaging-sense-reference-revealed
            >
              <b>{reference.role}</b>
              <p>
                Data phantom key image is solver-visible; no private target established. No
                truth/reconstruction image.
              </p>
              <p>
                Generic magnitude comparison: 16384 pixels, no scale normalization. Source main
                max-normalizes; selected reference lineage matters.
              </p>
              <small>
                Task-local windowed SSIM differs from generic global SSIM; both range NRMSE rules
                give infinity for constant reference. No source SSIM zero-range guard or current
                verdict; no clinical effect.
              </small>
            </div>
          ) : (
            <p>Reader rules covered; truth/output images absent.</p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Reconcile loader, mask and scaling before results</h3>
          <p>{source.actual_data_gap}</p>
          <small>
            Actual synthetic map previews are neither patient truth nor reconstruction evidence.
            Preserve complex phases, source R and selected-reference lineage.
          </small>
        </>
      )}
    </section>
  );
}
export function ImagingSenseOutput({ state }: { state: ImagingSenseState }) {
  return (
    <aside
      data-imaging-sense-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Synthetic SENSE source contract</b>
      <p>Native map magnitudes; symbolic encoding/CG rules.</p>
      <p>Full-key/R3–R4 mismatch. Participant image/score absent.</p>
      <small>Reader rules require explicit late reveal; backward/exit/reset covers them.</small>
    </aside>
  );
}

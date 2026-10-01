import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  previews,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  type ImagingWaveletState,
} from './imaging101-mri-l1-wavelet';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging101-mri-l1-wavelet.module.css';
function Mask() {
  return (
    <figure className={css.mask}>
      <svg
        viewBox="0 0 320 26"
        role="img"
        aria-label="Actual released MRI mask; 80 of 320 last-axis phase-encode columns sampled"
      >
        {source.native_mask.map((v, j) => (
          <rect key={j} x={j} width="1" height="20" fill={v ? '#57d1cc' : '#526373'} />
        ))}
      </svg>
      <figcaption>
        Teal = acquired · gray = missing · frequency column index → · 80/320 columns; no image
        pixels/mm.
      </figcaption>
    </figure>
  );
}
function Native({ m }: { m: number }) {
  return (
    <figure className={css.native}>
      <img
        src={previews[m]}
        alt={`Source masked k-space coil ${fixture.coils[m]}; log-magnitude frequency display, not reconstructed knee image`}
      />
      <figcaption>
        Released coil {fixture.coils[m]} · native 320² · log-magnitude, black 0→white per-coil
        maximum; phase hidden only for display.
      </figcaption>
    </figure>
  );
}
export function ImagingWaveletScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingWaveletState;
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
      data-imaging-wavelet-scene={state.scene}
      data-imaging-wavelet-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Actual R4 k-space; README R8 and loader differ</h3>
          <div className={css.two}>
            <Native m={0} />
            <div>
              <b>1 slice · 15 coils · 320×320 complex samples</b>
              <p>
                Released fastMRI knee example, no physical affine/spacing or clinical
                interpretation. Missing columns are frequency measurements.
              </p>
              <Mask />
              <small>No reconstructed image or participant output.</small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Complex measurement consistency and sparse wavelet prior</h3>
          <nav className={css.controls} aria-label="MRI wavelet pipeline steps">
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
                <b>M broadcasts over last-axis columns; 80/320 sampled</b>
                <Mask />
                <p>
                  Complex64 (1, 15, 320, 320), sensitivity maps supplied. Metadata R4 differs from
                  README 8 coils/128²/R8; native condition cannot prove README difficulty.
                </p>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Inspect source coil k-space">
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
                  <Native m={m} />
                  <div>
                    <b>y_c=M F(S_c x)</b>
                    <p>
                      Multiply complex coil map, centered orthonormal FFT, mask. Source samples
                      remain complex; displayed magnitude is not solver preprocessing.
                    </p>
                    <small>
                      Separate per-coil log scales; brightness is not quantitatively comparable. No
                      native FFT/IFFT or reconstruction executed.
                    </small>
                  </div>
                </div>
              </>
            ) : (
              <>
                <b>.5||MFSx−y||²+λ||Ψx||₁ ·db4</b>
                <p>
                  Source FISTA uses λ=1e−3 and step α; shrinkage τ=λα. Authored coefficient 3 + 4i,
                  hypotheticalτ=1→2.4+3.2i preserves phase; no native coefficients/output shown.
                </p>
                <small>
                  Solver SENSE adjoint sums conjugated coils; normalized physics helper divides by
                  coil-power square root, a distinct operator.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual reconstruction.npy absent</h3>
          <code>output/reconstruction.npy ·released320×320</code>
          <p>
            Actual image, score and outcome empty. Separate source-saved complex archive has no
            fresh execution lineage and is not a participant prediction.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Reader source-truth/loader/evaluator rules</h3>
          <button
            type="button"
            aria-expanded={showRules}
            aria-controls="wavelet-reader-rules"
            onClick={() => setShowRules(!showRules)}
          >
            {showRules ? 'Hide source rules' : 'Reveal source rules'}
          </button>
          {referenceVisible(state, showRules) ? (
            <div
              id="wavelet-reader-rules"
              className={css.socket}
              data-imaging-wavelet-reference-revealed
            >
              <b>{reference.role}</b>
              <p>
                Staged data truth is solver-visible, key mvue; source loader requests missing
                phantom. No truth image or hidden private target shown.
              </p>
              <p>
                Generic evaluator squeezes then takes magnitude: phase discarded; filesystem route
                has no intensity renormalization. Without a filesystem workspace the fallback
                instead flux-normalizes and uses relative L2 NRMSE. Cosine NCC and range NRMSE
                differ. No installed metrics.json pass/fail.
              </p>
              <small>
                102400 comparison pixels, not 15 coils or clinical population. Source-saved output
                is not fresh performance.
              </small>
            </div>
          ) : (
            <p>Reader rules covered. Truth/output images never bundled.</p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Reconcile source condition before outcome claims</h3>
          <p>{source.actual_data_gap}</p>
          <div className={css.socket}>
            <b>Raw measurement display is not reconstruction</b>
            <p>
              Preserve complex units, mask and coil semantics. Source version/loader/rights and
              outcome lineage remain open; no clinical finding or model score.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
export function ImagingWaveletOutput({ state }: { state: ImagingWaveletState }) {
  return (
    <aside
      data-imaging-wavelet-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Released MRI measurement contract</b>
      <p>Actual masked k-space and native mask; display only.</p>
      <p>Participant reconstruction/score and GT image absent.</p>
      <small>Reader rules require an explicit late reveal; backward/exit/reset covers them.</small>
    </aside>
  );
}

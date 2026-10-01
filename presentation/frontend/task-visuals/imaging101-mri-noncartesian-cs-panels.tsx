import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  trajectoryImage,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  type ImagingNoncartesianState,
} from './imaging101-mri-noncartesian-cs';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging101-mri-noncartesian-cs.module.css';
function Plot({ m }: { m: number }) {
  const points = source.trajectory.points.slice(0, fixture.branches[m] * 8);
  return (
    <figure className={css.native}>
      <svg
        viewBox="0 0 256 256"
        role="img"
        aria-label="Actual source radial trajectory subset; grid coordinates, not a reconstructed image"
      >
        <path d="M8 128H248M128 8V248" stroke="#526373" />
        {points.map((v, j) => (
          <circle
            key={j}
            cx={8 + ((v[1] + 64) * 240) / 128}
            cy={8 + ((64 - v[0]) * 240) / 128}
            r="1.3"
            fill="#57d1cc"
          />
        ))}
        <text x="148" y="120" fill="#e0edf4" fontSize="11">
          coord 1→
        </text>
        <text x="135" y="18" fill="#e0edf4" fontSize="11">
          ↑coord 0
        </text>
      </svg>
      <figcaption>
        {points.length} of 8192 points · {fixture.branches[m]} of 64 spokes · 1-in-16 display;
        acquisition unchanged.
      </figcaption>
    </figure>
  );
}
export function ImagingNoncartesianScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingNoncartesianState;
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
      data-imaging-noncartesian-scene={state.scene}
      data-imaging-noncartesian-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Actual synthetic trajectory; no participant reconstruction</h3>
          <div className={css.two}>
            <figure className={css.native}>
              <img
                src={trajectoryImage}
                alt="Pinned synthetic radial coordinates raster; 512 of 8192 points, no image reconstruction"
              />
              <figcaption>
                Teal = actual coordinate samples · gray = axis guides. Diagram grid units; no
                patient plane/mm.
              </figcaption>
            </figure>
            <div>
              <b>4 coils · 64 spokes × 128 readout · 8192 samples/coil</b>
              <p>
                Complex measurements and birdcage maps supplied. Source-visible phantom, no held-out
                private target or participant output.
              </p>
              <small>
                README cycles/pixel versus NUFFT grid scaling; physical FOV/time uncalibrated.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Radial sampling needs a coordinate-aware operator</h3>
          <nav className={css.controls} aria-label="Non-Cartesian MRI pipeline steps">
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
                <b>y_c=F_NU(S_c x)+η_c</b>
                <p>
                  coord (1, 8192, 2); complex kdata (1, 4, 8192), maps (1, 4, 128, 128). Flat order
                  = spoke/readout, no millisecond time axis. Grid scaling needs ÷128 for normalized
                  cycles/pixel.
                </p>
                <small>
                  8192/16384=.5 sample/pixel count ratio is not 50% unique coverage or measured
                  acceleration; repeated origins and coils differ.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Select trajectory display subset">
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
                  <Plot m={m} />
                  <div>
                    <b>DCF baseline differs from inverse objective</b>
                    <p>
                      Pipe: w←w/max(|F Fᴴw|,1e−12), 30 default iterations. Gridding uses weighted
                      adjoint and normalized coil combination.
                    </p>
                    <small>
                      Actual weights/image absent; dots show coordinates only. Views change display,
                      never acquisition or solver. SigPy runtime defaults not exactly pinned.
                    </small>
                  </div>
                </div>
              </>
            ) : (
              <>
                <b>Unweighted complex consistency + db4 L1</b>
                <p>
                  Source FISTA λ=5e−5, 100 iterations; solver adjoint sums conjugated coil maps, no
                  gridding DCF/normalization. Authored 3 + 4i with hypothetical τ=1→2.4+3.2i
                  preserves phase.
                </p>
                <small>
                  Complex noise_std=.005 is declared, not estimated native noise. No NUFFT,
                  reconstruction or convergence run.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual reconstruction.npy absent</h3>
          <code>output/reconstruction.npy · comparable 128×128</code>
          <p>
            Participant image/score empty. Separate source gridding/L1-wavelet archives are saved
            examples, never a fresh response or performance verdict.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Reader source-visible truth and evaluator rules</h3>
          <button
            type="button"
            aria-expanded={showRules}
            aria-controls="noncartesian-reader-rules"
            onClick={() => setShowRules(!showRules)}
          >
            {showRules ? 'Hide source rules' : 'Reveal source rules'}
          </button>
          {referenceVisible(state, showRules) ? (
            <div
              id="noncartesian-reader-rules"
              className={css.socket}
              data-imaging-noncartesian-reference-revealed
            >
              <b>{reference.role}</b>
              <p>
                Staging copies data truth key phantom; no private hidden target established. No
                truth/reconstruction image shown.
              </p>
              <p>
                Filesystem evaluator squeezes only arrays above two dimensions and takes magnitude;
                phase discarded, no scale normalization. The no-filesystem fallback instead
                flux-normalizes and uses relative L2 NRMSE. 16384 comparison pixels differ from 8192
                samples/coil.
              </p>
              <small>
                Cosine NCC/range NRMSE and installed metrics.json thresholds are distinct from
                source metrics_detail.json; no native score or pass/fail.
              </small>
            </div>
          ) : (
            <p>Reader rules covered; truth/output images absent.</p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Source calibration and outcome boundaries remain</h3>
          <p>{source.actual_data_gap}</p>
          <div className={css.socket}>
            <b>Actual coordinates are not clinical image evidence</b>
            <p>
              Preserve grid scale, complex domain and source-visible truth. Pin coherent
              runtime/evaluator/reference/artifact lineage before method claims.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
export function ImagingNoncartesianOutput({ state }: { state: ImagingNoncartesianState }) {
  return (
    <aside
      data-imaging-noncartesian-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Synthetic radial measurement contract</b>
      <p>Actual coordinate subset; no NUFFT or image reconstruction.</p>
      <p>Participant output/score and truth image absent.</p>
      <small>Reader rules require an explicit late reveal; backward/exit/reset covers them.</small>
    </aside>
  );
}

import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  illustrativeWeights,
  metricRoutes,
  type ImagingPoissonState,
} from './imaging101-ct-poisson-lowdose';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging101-ct-poisson-lowdose.module.css';
function Rays() {
  return (
    <figure className={css.rays}>
      <svg
        viewBox="0 0 360 94"
        role="img"
        aria-label="Symbolic parallel beams; attenuation line integral is dimensionless, no measured rays"
      >
        <rect x="134" y="15" width="75" height="65" fill="#314c60" stroke="#d0e6f0" />
        {fixture.line_integrals.map((v, j) => (
          <g key={v}>
            <path d={`M20 ${28 + j * 22}H334`} stroke="#88b4e0" strokeWidth="2" />
            <text x="22" y={23 + j * 22} fill="#deebf4" fontSize="11">
              Ax={v} →λ={fixture.expected_counts[j].toFixed(2)} photons
            </text>
          </g>
        ))}
      </svg>
      <figcaption>
        Blue solid lines = symbolic rays; slate box = attenuation object. Expected λ differs from a
        random count Y.
      </figcaption>
    </figure>
  );
}
export function ImagingPoissonScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingPoissonState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [revealed, setRevealed] = useState(false);
  const [weightMode, setWeightMode] = useState<'counts' | 'uniform'>('counts');
  const [metricRoute, setMetricRoute] = useState(0);
  const previous = useRef(state.frame);
  const previousBeat = useRef(state.beatId);
  useLayoutEffect(() => {
    if (state.frame < previous.current || state.beatId !== previousBeat.current) {
      setRevealed(false);
      setWeightMode('counts');
      setMetricRoute(0);
    }
    previous.current = state.frame;
    previousBeat.current = state.beatId;
  }, [state.frame, state.beatId]);
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-imaging-poisson-scene={state.scene}
      data-imaging-poisson-currentstep={i}
    >
      {state.scene === 'input' && (
        <>
          <h3>Matching 300-photon noisy input missing</h3>
          <Rays />
          <p>
            256 views × 367 channels → 256² image; phantom task, no patient data. Symbolic rays
            below; retained 1000-photon arrays stay separate.
          </p>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Keep expectation, count realization and reconstruction separate</h3>
          <nav className={css.controls} aria-label="Poisson pipeline steps">
            {steps.map((s, j) => (
              <button
                key={s}
                type="button"
                data-imaging-poisson-step={j}
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
                <b>λ=300exp(−Ax); Y~Poisson(λ)</b>
                <Rays />
                <small>
                  Variance λ, photons/bin; compatible attenuation×length units needed. README cm⁻¹
                  vs metadata mm⁻¹ unresolved.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Illustrative count conditions">
                  {branches.map((s, j) => (
                    <button
                      key={s}
                      type="button"
                      data-imaging-poisson-count={j}
                      aria-pressed={m === j}
                      disabled={!onSeekFrame}
                      onClick={() => onSeekFrame?.(operationFrame(plan, 1, j))}
                    >
                      {s}
                    </button>
                  ))}
                </nav>
                <b>
                  Illustrative Y={fixture.illustrative_counts[m]} →max(Y,1)=
                  {fixture.floored_counts[m]}
                </b>
                <p>
                  −log(count/300)={fixture.postlog[m].toFixed(6)}; weight=
                  {fixture.floored_counts[m]} floored photons. These are authored counts, no random
                  draw.
                </p>
                <small>
                  Zero/one indistinguishable after floor. Counts may exceed I0, giving negative
                  postlog.
                </small>
              </>
            ) : (
              <>
                <nav className={css.controls} aria-label="Toy weighting alternatives">
                  {(['counts', 'uniform'] as const).map((mode) => (
                    <button
                      key={mode}
                      type="button"
                      data-imaging-poisson-weight={mode}
                      aria-pressed={weightMode === mode}
                      onClick={() => setWeightMode(mode)}
                    >
                      {mode === 'counts' ? 'Count-derived' : 'Uniform baseline'}
                    </button>
                  ))}
                </nav>
                <b>
                  Toy weights:{' '}
                  {illustrativeWeights(fixture.floored_counts, weightMode)
                    .map((x) => x.toFixed(3))
                    .join(' / ')}
                </b>
                <p>
                  Source max-normalizes weights, project/backprojects and clips negative estimates.
                  Plans advertise q-GGMRF/ICD; supplied solver uses proximal-gradient TV. No
                  run/convergence claim.
                </p>
                <small>Stored (1,V,C) strips batch; SVMBIR (V,1,C), parallel geometry.</small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual reconstruction.npy absent</h3>
          <code>output/reconstruction.npy ·real 256×256</code>
          <p>
            No reconstructed image, GT, score or model outcome. Saved source arrays are independent
            fixtures, not participant predictions.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Reader-only 300 expected-count fixture and evaluator limits</h3>
          <button
            type="button"
            className={css.reveal}
            data-imaging-poisson-reveal
            aria-pressed={referenceVisible(state, revealed)}
            onClick={() => setRevealed(!revealed)}
          >
            {referenceVisible(state, revealed)
              ? 'Cover fixture and rules'
              : 'Reveal fixture and rules'}
          </button>
          {referenceVisible(state, revealed) ? (
            <div className={css.socket} data-imaging-poisson-reference-revealed>
              <figure className={css.rays}>
                <svg
                  viewBox="0 0 320 84"
                  role="img"
                  aria-label="Source physics fixture expected photons; 16 view by 16 detector native-bin subset, no measured noise reconstruction or GT"
                >
                  {reference.expected_count_subset.values.flatMap((row, v) =>
                    row.map((c, d) => (
                      <rect
                        key={`${v}-${d}`}
                        x={d * 5}
                        y={v * 5}
                        width="5"
                        height="5"
                        fill={`rgb(${Math.round((c / 300) * 255)},${Math.round((c / 300) * 255)},${Math.round((c / 300) * 255)})`}
                      />
                    )),
                  )}
                  <text x="94" y="18" fill="#deebf4" fontSize="12">
                    Expected photons/bin
                  </text>
                  <text x="94" y="36" fill="#deebf4" fontSize="11">
                    Black 0 → white 300
                  </text>
                  <text x="94" y="54" fill="#deebf4" fontSize="11">
                    Views 120–135 · detectors 175–190
                  </text>
                  <text x="94" y="72" fill="#deebf4" fontSize="11">
                    No noisy input/reconstruction/GT
                  </text>
                </svg>
                <figcaption>
                  Pinned physics fixture output_transmission; native 16×16 subset, no rescale.
                  Mathematical expectation, never noisy realization.
                </figcaption>
              </figure>
              <nav className={css.controls} aria-label="Compare scorer contracts">
                {metricRoutes.map((route, index) => (
                  <button
                    key={route}
                    type="button"
                    data-imaging-poisson-metric={index}
                    aria-pressed={metricRoute === index}
                    onClick={() => setMetricRoute(index)}
                  >
                    {route}
                  </button>
                ))}
              </nav>
              <p>
                {metricRoute === 0
                  ? 'Filesystem generic: full256², cosine NCC and range NRMSE; constant reference gives infinity, no flux normalization.'
                  : metricRoute === 1
                    ? 'Separate task-aware helper: central204² =41616/65536 pixels, cosine NCC and range NRMSE; constant reference gives 0.0.'
                    : 'No-filesystem fallback: output flux scaled to .npy truth, relative L2 NRMSE; different route.'}
              </p>
              <small>
                No metrics.json thresholds retained; no score or pass/fail verdict shown.
              </small>
              <small>
                Source staging copies data truth to solver; evaluation fixtures outside workspace.
                Card visibility is an educational boundary.
              </small>
            </div>
          ) : (
            <p>Expected-count fixture/rules covered; no task reference or outcome rendered.</p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Recover exact 300 inputs before outcome comparison</h3>
          <p>{source.actual_data_gap}</p>
          <div className={css.socket}>
            <b>Wrong I0 shifts every post-log ray</b>
            <p>
              −ln(1000/300)={fixture.dose_shift.toFixed(6)}; source hash mismatch is a version gap,
              no truncation or model failure. Acquire exact manifest hashes and resolve
              units/evaluator.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
export function ImagingPoissonOutput({ state }: { state: ImagingPoissonState }) {
  return (
    <aside
      data-imaging-poisson-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>300-photon task contract</b>
      <p>Actual noisy input/reconstruction/GT/score empty.</p>
      <p>Symbolic counts/log; source expected counts only in the late reader card.</p>
      <small>
        Late fixture and rules need explicit reader reveal; backward, exit and Reset cover them.
      </small>
    </aside>
  );
}

import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  maskImages,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  type ImagingPnpAdmmState,
} from './imaging101-mri-pnp-admm';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging101-mri-pnp-admm.module.css';
function Mask({ m }: { m: number }) {
  return (
    <figure className={css.native}>
      <img
        src={maskImages[m]}
        alt={`Actual ${branches[m]} binary source mask; stored unshifted Fourier cells`}
      />
      <figcaption>
        Teal=sampled ·dark=unsampled. {source.masks.counts[m]}/65536 cells; 256² native indices.
      </figcaption>
    </figure>
  );
}
export function ImagingPnpAdmmScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingPnpAdmmState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [showRules, setShowRules] = useState(false);
  const previousFrame = useRef(state.frame);
  const previousBeat = useRef(state.beatId);
  const stable =
    state.scene === 'reference' &&
    previousBeat.current === state.beatId &&
    state.frame >= previousFrame.current;
  useLayoutEffect(() => {
    if (!stable) setShowRules(false);
    previousBeat.current = state.beatId;
    previousFrame.current = state.frame;
  }, [state.frame, state.scene, state.beatId, stable]);
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-imaging-pnp-admm-scene={state.scene}
      data-imaging-pnp-admm-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Actual source mask; observation absent</h3>
          <div className={css.two}>
            <Mask m={0} />
            <div>
              <b>Single coil ·256×256 ·stored mask/noise</b>
              <p>
                No measured k-space. Source image synthesizes y; metadata omits required
                noise_scale.
              </p>
              <small>
                Display only: no FFT, learned denoiser or brain truth image. No calibrated FOV/time.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Trace pinned updates without running the solver</h3>
          <nav className={css.controls} aria-label="PnP-ADMM steps">
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
                <b>y=M FFT2(image)+scale·(noise_real+i noise_imag)</b>
                <p>
                  Unshifted default FFT; noise added at all bins. x₀=v₀=|IFFT(y)|, u₀=0; real image
                  iterates.
                </p>
                <small>
                  Missing metadata scale prevents an effective source observation. Default helper
                  scale=3 does not resolve main.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Select source mask display">
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
                  <Mask m={m} />
                  <div>
                    <b>v=real IFFT(updated vf)</b>
                    <p>α=2; sampled vf←(.25vf+y)/1.25. Unsampled vf unchanged.</p>
                    <small>
                      Authored vf=2,y=6→{fixture.toy_sampled[0]}; arithmetic only. Display masks
                      never change the pinned random-mask main.
                    </small>
                  </div>
                </div>
              </>
            ) : (
              <>
                <b>xtilde=2v−xold−uold; residual denoiser</b>
                <p>
                  Min/max normalize →range 1+15/255/2, centered shift →subtract model residual →undo
                  scale. u←uold+xold−v.
                </p>
                <small>
                  100 fixed iterations; σ=15 training parameter, not measured noise. Constant-input
                  normalization unguarded. No model residual or convergence claim.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual reconstruction.npy absent</h3>
          <code>output/reconstruction.npy ·256×256 comparison</code>
          <p>
            Participant image/score empty. Saved source PnP examples are separate from a fresh
            response or verified outcome.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later source-truth and evaluator rules</h3>
          <button
            type="button"
            aria-expanded={stable && showRules}
            aria-controls="pnp-reader-rules"
            onClick={() => setShowRules(!showRules)}
          >
            {showRules ? 'Hide source rules' : 'Reveal source rules'}
          </button>
          {referenceVisible(state, stable && showRules) ? (
            <div
              id="pnp-reader-rules"
              className={css.socket}
              data-imaging-pnp-admm-reference-revealed
            >
              <b>{reference.role}</b>
              <p>
                Data image is solver-visible; no private target established. No truth image or
                participant reconstruction shown.
              </p>
              <p>
                Filesystem evaluator squeezes only ndim&gt;2, takes magnitude and compares float64;
                phase lost. Source evaluation/ground_truth.npy has priority but is
                absent/unverified.
              </p>
              <small>
                Filesystem: unscaled range NRMSE and cosine NCC. No-filesystem fallback:
                flux-normalized relative L2. No current score.
              </small>
            </div>
          ) : (
            <p>Reader rules covered; truth/output images absent.</p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Resolve scale and source lineage before claims</h3>
          <p>{source.actual_data_gap}</p>
          <small>
            Mask diagrams are not brain image evidence. README convergence claims require
            conditions; source inspection is not a checkpoint or solver test.
          </small>
        </>
      )}
    </section>
  );
}
export function ImagingPnpAdmmOutput({ state }: { state: ImagingPnpAdmmState }) {
  return (
    <aside
      data-imaging-pnp-admm-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Mask/noise source contract</b>
      <p>Actual masks; symbolic ADMM rules.</p>
      <p>Missing noise_scale. Participant output/score and truth image absent.</p>
      <small>Reader rules require explicit late reveal; backward/exit/reset covers them.</small>
    </aside>
  );
}

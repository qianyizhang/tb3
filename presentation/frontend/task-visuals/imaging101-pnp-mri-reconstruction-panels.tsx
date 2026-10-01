import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  maskImage,
  sourceImage,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  type ImagingPnpMriState,
} from './imaging101-pnp-mri-reconstruction';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging101-pnp-mri-reconstruction.module.css';
function ReaderReference({ state }: { state: ImagingPnpMriState }) {
  const [requested, setRequested] = useState(false);
  const last = useRef(state.frame);
  const backward = state.frame < last.current;
  useLayoutEffect(() => {
    if (backward) setRequested(false);
    last.current = state.frame;
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
        {' '}
        {visible ? 'Cover public source image' : 'Reveal public source image'}{' '}
      </button>
      {visible ? (
        <div className={css.two} data-imaging-pnp-mri-reference-revealed>
          <figure className={css.native}>
            <img
              src={sourceImage}
              alt="Public source image equals solver-visible truth; stride-two minmax display, not reconstruction"
            />
            <figcaption>
              Public source input = visible truth. 160 × 160 stride-two display; no reconstruction.
            </figcaption>
          </figure>
          <div>
            <b>{reference.role}</b>
            <p>
              Normalized reference, all 102,400 pixels; source norm-relative error differs from
              generic range-normalized error.
            </p>
            <small>Actual participant output and score absent.</small>
          </div>
        </div>
      ) : (
        <p>Public source image covered; the eligibility channel alone does not reveal it.</p>
      )}
    </>
  );
}
function Mask() {
  return (
    <figure className={css.native}>
      <img
        src={maskImage}
        alt="Native source-saved radial mask on a Cartesian 320 by 320 grid; white sampled and black omitted, no measured k-space"
      />
      <figcaption>
        White / black: 11,766 sampled / 90,634 omitted grid cells. Saved geometry, no Fourier
        samples.
      </figcaption>
    </figure>
  );
}
export function ImagingPnpMriScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingPnpMriState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-imaging-pnp-mri-scene={state.scene}
      data-imaging-pnp-mri-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Image supplied; acquired k-space absent</h3>
          <div className={css.two}>
            <Mask />
            <div>
              <b>Raw image = solver-visible truth</b>
              <p>
                One 320 × 320 source image. Preprocessing generates noiseless masked Fourier data;
                no scanner k-space or coil measurements here.
              </p>
              <small>
                Source image covered until late public reveal. No FFT, reconstruction, denoiser or
                score run.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Trace data consistency before an unknown denoiser</h3>
          <nav className={css.controls} aria-label="PnP MRI steps">
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
                <b>Visible image → minmax → deterministic mask → generated y</b>
                <p>
                  No acquired k-space or added measurement noise. Metadata sigma = 5 is unused by
                  the denoiser constructor; training claim unverified.
                </p>
                <small>
                  L1 / L2 / L3 add README, approach and design assistance; same image boundary. No
                  new source measurements generated.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Select public operator rule">
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
                {m === 0 ? (
                  <div className={css.two}>
                    <Mask />
                    <div>
                      <b>36 rasterized radial lines</b>
                      <p>
                        11.490% Cartesian cells sampled; inverse fraction ≈ 8.703. Not acquired
                        non-Cartesian trajectories or scan-time acceleration.
                      </p>
                    </div>
                  </div>
                ) : m === 1 ? (
                  <>
                    <b>A = M fftshift(FFT2) / 320</b>
                    <p>
                      Aᴴ = 320 IFFT2(ifftshift(Mz)); real image gradient uses real(Aᴴ(Ax−y)).
                      Unitary discrete scaling, no coil or physical FOV model.
                    </p>
                    <small>
                      Equations only; no native FFT, adjoint or reconstructed image computed.
                    </small>
                  </>
                ) : (
                  <>
                    <b>42 × 42 patches · stride 7 · final start 278</b>
                    <p>
                      41 positions per axis = 1,681 patches; overlap averaged. Input × 255, residual
                      + input, then ÷ 255.
                    </p>
                    <small>
                      Checkpoint shards present; TensorFlow graph / variable compatibility and
                      output unknown. No model loaded.
                    </small>
                  </>
                )}
              </>
            ) : (
              <>
                <b>x₀ = 0; s = max(x − g, 0); x_next = D(s)</b>
                <p>
                  PGM: 200 fixed iterations, step 1. No ADMM dual variable; positivity before
                  denoiser only.
                </p>
                <small>
                  Authored scalar y = 0.6 gives pre-denoise s = {fixture.toy_pre_denoise}. D(s)
                  unknown; no denoised output, convergence or performance.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual reconstruction.npy absent</h3>
          <code>output/reconstruction.npy · 320 × 320 normalized image</code>
          <p>
            Participant output, denoiser result, histories and score empty. Saved IFFT / PnP arrays
            are audit provenance only.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later public source image and scorer boundary</h3>
          <ReaderReference state={state} key={state.beatId} />
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Resolve visibility, runtime and metric units</h3>
          <p>{source.actual_data_gap}</p>
          <small>
            No blind inverse-problem, learned proximal, clinical or model-performance claim.
          </small>
        </>
      )}
    </section>
  );
}
export function ImagingPnpMriOutput({ state }: { state: ImagingPnpMriState }) {
  return (
    <aside
      data-imaging-pnp-mri-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Source image visible to solver; result absent</b>
      <p>Saved mask and public PGM / patch rules.</p>
      <p>No acquired k-space, model forward or participant image / metric.</p>
      <small>Reader-controlled public source truth; backward / exit / reset covers it.</small>
    </aside>
  );
}

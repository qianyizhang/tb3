import { useLayoutEffect, useRef, useState } from 'react';
import preview from '../../task-explorer/bcer-short-denoise/source-preview.jpeg';
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
  resetOnBackward,
  type BcerDenoiseState,
} from './bcer-short-denoise';
import type { StoryPlan } from '../contracts.generated';
import css from './bcer-short-denoise.module.css';
export function BcerDenoiseScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: BcerDenoiseState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [readerRequested, setReaderRequested] = useState(false);
  const previous = useRef(state);
  useLayoutEffect(() => {
    const old = previous.current;
    if (
      state.scene !== old.scene ||
      state.beatId !== old.beatId ||
      resetOnBackward(old.frame, state.frame)
    )
      setReaderRequested(false);
    previous.current = state;
  }, [state]);
  const visible = referenceVisible(state, readerRequested);
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section className={css.scene} data-bcer-denoise-scene={state.scene}>
      {state.scene === 'input' && (
        <>
          <h3>Public representative MRI helper</h3>
          <div className={css.two}>
            <figure>
              <img
                className={css.native}
                src={preview}
                data-bcer-denoise-native
                alt="PI-CAI T2w representative helper, neither matching BM3D input nor clean reference"
              />
              <figcaption>
                k = 10 (zero-based, 21 slices). 640² → 320² bilinear JPEG q70; display window
                15–829. No filtering.
              </figcaption>
            </figure>
            <div>
              <b>PI-CAI 10001_1000001 T2w</b>
              <p>640×640×21 · oblique LPS · 0.300×0.300×3.600 mm.</p>
              <small>
                Arbitrary MRI intensity units. No clean target, added-noise realization or measured
                noise distribution.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>BM3D contract: range, estimated sigma, physical geometry</h3>
          <nav className={css.controls} aria-label="BCER denoise contract steps">
            {steps.map((s, j) => (
              <button
                data-bcer-denoise-operation-step={j}
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
                <b>Whole-volume finite min/max → [0,1]</b>
                <p>
                  Toy intensity {fixture.raw.join(' / ')} →{fixture.normalized.join(' / ')}.
                  Nonfinite → 0; constant range skips filtering. Display window differs from tool
                  normalization.
                </p>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Explore BCER sigma units">
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
                <b>Estimated σ={fixture.sigma[m]} normalized units</b>
                <p>
                  Toy range 40: σ × range = {fixture.raw_sigma[m]} arbitrary toy units. This is not
                  measured MRI noise, a distribution, a seed or a patient result.
                </p>
              </>
            ) : (
              <>
                <b>Independent 2-D BM3D profile=np → restore range</b>
                <p>
                  Flatten leading dimensions; clip filtered values to [0,1]. Copy
                  size/spacing/origin/direction/metadata; floating input dtype preserved. No BM3D
                  output or quality measurement shown.
                </p>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual denoised artifact absent</h3>
          <code>denoised_nifti</code>
          <pre data-bcer-denoise-output-schema>
            artifacts/denoise/denoised_&lt;input_stem&gt;.nii.gz
          </pre>
          <p>Illustrative default path only; actual path/image/elapsed/quality remain null.</p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Validator boundary; no pristine/private image</h3>
          <button
            className={css.reveal}
            type="button"
            disabled={state.reference <= 0.5}
            aria-pressed={visible}
            onClick={() => setReaderRequested((value) => !value)}
          >
            {visible ? 'Cover validator rule' : 'Reveal public validator rule'}
          </button>
          {visible ? (
            <div className={css.socket} data-bcer-denoise-reference-revealed>
              <b>{reference.role}</b>
              <p>
                Stage/path/nonempty/geometry checks. Read failure may fall back to file size; size
                is exact; spacing, origin and direction tolerances are 1e-3.
              </p>
              <p>
                No PSNR/SSIM/clean target. Artifact validity cannot establish noise removal or
                detail preservation.
              </p>
            </div>
          ) : (
            <p data-bcer-denoise-reference-hidden>
              Public rule remains covered until requested. No clean/private image is bundled.
            </p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Noise basis and output quality unmeasured</h3>
          <p>{source.actual_data_gap}</p>
          <div className={css.socket}>
            <b>Suppressing noise may suppress detail</b>
            <p>
              No actual tool run, clean image, noise distribution/seed or quality denominator.
              Representative acquisition is not matched task evidence.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
export function BcerDenoiseOutput({ state }: { state: BcerDenoiseState }) {
  return (
    <aside data-bcer-denoise-output={state.scene} className={css.output}>
      <b>Geometry-consistent NIfTI contract</b>
      <p>Representative helper only. Actual denoised_nifti absent.</p>
      <p>σ is an estimate in normalized units. Geometry validity ≠ image quality.</p>
      <small>
        Public validator rule is reader-controlled in its later chapter. Reset, backward seek and
        exit cover it. No clean reference image.
      </small>
    </aside>
  );
}

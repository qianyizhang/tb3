import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  fixture,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  interpolationModes,
  type BcerSuperresState,
} from './bcer-short-superres';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './bcer-short-superres.module.css';
export function BcerSuperresScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: BcerSuperresState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [revealed, setRevealed] = useState(false);
  const [interpolation, setInterpolation] = useState<(typeof interpolationModes)[number]>('linear');
  const previous = useRef(state.frame);
  const previousBeat = useRef(state.beatId);
  useLayoutEffect(() => {
    if (state.frame < previous.current || state.beatId !== previousBeat.current) {
      setRevealed(false);
      setInterpolation('linear');
    }
    previous.current = state.frame;
    previousBeat.current = state.beatId;
  }, [state.frame, state.beatId]);
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-bcer-superres-scene={state.scene}
      data-bcer-superres-currentstep={i}
    >
      {state.scene === 'input' && (
        <>
          <h3>Representative MRI input; target/output absent</h3>
          <div className={css.two}>
            <figure>
              <img
                className={css.native}
                src={source.preview_data_uri}
                alt="Representative PI-CAI T2w source input; not resampled output"
              />
              <figcaption>
                Source 640² k10 → 320² JPEG display. Window 15–829, arbitrary MRI units. Bilinear
                preview resize is not participant resampling.
              </figcaption>
            </figure>
            <div>
              <b>640×640×21 · LPS · 0.300×0.300×3.600 mm</b>
              <p>
                PI-CAI 10001_1000001 T2w. Representative helper, not a matched BCER input/output
                pair.
              </p>
              <small>
                No chosen reference grid, high-resolution truth or new anatomical measurements.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Physical grid →identity interpolation →typed NIfTI</h3>
          <nav className={css.controls} aria-label="BCER superres contract steps">
            {steps.map((s, j) => (
              <button
                key={s}
                type="button"
                data-bcer-superres-step={j}
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
                <b>Source size×spacing describes grid coverage</b>
                <p>
                  Explicit target keeps input origin/direction. Reference NIfTI instead supplies
                  size/spacing/origin/direction; if both provided, reference wins.
                </p>
                <small>
                  Reference grid is a supplied geometry helper, not a clean/private target or
                  registration.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Explore BCER target grid">
                  {branches.map((s, j) => (
                    <button
                      key={s}
                      type="button"
                      data-bcer-superres-branch={j}
                      aria-pressed={m === j}
                      disabled={!onSeekFrame}
                      onClick={() => onSeekFrame?.(operationFrame(plan, 1, j))}
                    >
                      {s}
                    </button>
                  ))}
                </nav>
                <b>Illustrative target: {fixture.derived_size[m].join('×')} voxels</b>
                <p>
                  ceil(N×s/t), using exact native header.{' '}
                  {m === 0
                    ? 'Same grid, using exact spacing'
                    : m === 1
                      ? 'z-spacing halved; sample count 42'
                      : 'all spacing halved; sample count 1280×1280×42'}
                  . No resampled image computed.
                </p>
                <small>
                  Rounded [0.3,0.3,3.6] → 641×641×22: +437,782 grid slots (+5.09%), not measured
                  output.
                </small>
              </>
            ) : (
              <>
                <nav className={css.controls} aria-label="Inspect interpolation contract">
                  {interpolationModes.map((mode) => (
                    <button
                      key={mode}
                      type="button"
                      data-bcer-superres-interpolation={mode}
                      aria-pressed={interpolation === mode}
                      onClick={() => setInterpolation(mode)}
                    >
                      {mode}
                    </button>
                  ))}
                </nav>
                <b>
                  {interpolation === 'linear'
                    ? 'Linear is the source default'
                    : interpolation === 'nearest'
                      ? 'Nearest selects samples; does not create detail'
                      : 'B-spline interpolates; no quality result is implied'}
                </b>
                <p>
                  Identity physical transform; no alignment optimization or newly measured detail.
                  Outside FOV default 0; input pixel type retained, integers can quantize
                  interpolated values.
                </p>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual resampled artifact absent</h3>
          <code>resampled_nifti</code>
          <pre>artifacts/resample/resampled_&lt;input_stem&gt;.nii.gz</pre>
          <p>
            Illustrative default path only; actual image, target, elapsed time and quality are null.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Grader boundary; no high-resolution truth</h3>
          <button
            type="button"
            className={css.reveal}
            data-bcer-superres-reveal
            aria-pressed={referenceVisible(state, revealed)}
            onClick={() => setRevealed(!revealed)}
          >
            {referenceVisible(state, revealed) ? 'Cover grader rules' : 'Reveal grader rules'}
          </button>
          {referenceVisible(state, revealed) ? (
            <div className={css.socket} data-bcer-superres-reference-revealed>
              <b>Reader-only grader rules; no clean image</b>
              <p>
                Stage, path and nonempty checks only. No target-grid, affine or quality invariant is
                listed for short_superres; read failure can fall back to positive file size.
              </p>
              <p>
                Denser grid is not new detail; artifact success is not PSNR/SSIM, alignment or
                clinical quality.
              </p>
            </div>
          ) : (
            <p data-bcer-superres-reference-hidden>
              Reader grader rules covered; no high-resolution image reference exists.
            </p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Target grid and output fidelity unresolved</h3>
          <p>{source.actual_data_gap}</p>
          <div className={css.socket}>
            <b>Interpolation changes sampling, not acquisition</b>
            <p>
              Source input is representative. No actual resampling, tool or model run; independently
              verify target physical grid and quality before claims.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
export function BcerSuperresOutput({ state }: { state: BcerSuperresState }) {
  return (
    <aside
      data-bcer-superres-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Physical-grid resampling contract</b>
      <p>Actual resampled_nifti empty. No independently acquired high-resolution target.</p>
      <p>ceil(N×s/t); identity transform; no quality verdict.</p>
      <small>
        Late grader rules need explicit reader reveal; backward seek, exit and Reset cover them.
      </small>
    </aside>
  );
}

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
  type AutomedBratsT1cSrState,
} from './automedbench-full-brats-t1c-sr-task';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './automedbench-full-brats-t1c-sr-task.module.css';
function ReaderRules({ state }: { state: AutomedBratsT1cSrState }) {
  const [requested, setRequested] = useState(false);
  const previous = useRef({ frame: state.frame, beat: state.beatId });
  const backward = state.frame < previous.current.frame || state.beatId !== previous.current.beat;
  useLayoutEffect(() => {
    if (backward) setRequested(false);
    previous.current = { frame: state.frame, beat: state.beatId };
  }, [state.frame, state.beatId, backward]);
  const visible = referenceVisible(state, requested && !backward);
  return (
    <>
      <button
        type="button"
        disabled={state.reference <= 0.5}
        aria-pressed={visible}
        onClick={() => setRequested((v) => !v)}
      >
        {visible ? 'Hide public evaluator rules' : 'Reveal public evaluator rules'}
      </button>
      {visible ? (
        <div className={css.socket} data-automed-brats-t1c-sr-reference-revealed>
          <b>{reference.role}</b>
          <p>
            All evaluator-supplied case IDs; independent NaN exclusions and format versus metric
            validity. No BraTS-specific normalization/rating map or supplied bands.
          </p>
          <small>
            PSNR / SSIM / LPIPS assets missing; no private target or metric revealed. “Clinical”
            names a code composite, not clinical validation.
          </small>
        </div>
      ) : (
        <p>Public evaluator rules covered; private target and output absent.</p>
      )}
    </>
  );
}
function Grid() {
  return (
    <figure className={css.native}>
      <svg
        viewBox="0 0 330 100"
        role="img"
        aria-label="Authored two by two normalized low-resolution cells versus four by four unknown high-resolution sockets, not MRI or interpolated result"
      >
        {fixture.low_grid.flat().map((v, i) => (
          <g key={`low-${i}`}>
            <rect
              x={10 + (i % 2) * 40}
              y={8 + Math.floor(i / 2) * 40}
              width="38"
              height="38"
              fill={`rgb(20,${80 + Math.round(v * 120)},${110 + Math.round(v * 100)})`}
            />
            <text
              x={29 + (i % 2) * 40}
              y={32 + Math.floor(i / 2) * 40}
              fill="#fff"
              textAnchor="middle"
              fontSize="13"
            >
              {v}
            </text>
          </g>
        ))}
        <text x="130" y="53" fill="#e9f4f7" fontSize="18">
          2×
        </text>
        {Array.from({ length: 16 }, (_, i) => (
          <g key={`unknown-${i}`}>
            <rect
              x={210 + (i % 4) * 20}
              y={8 + Math.floor(i / 4) * 20}
              width="18"
              height="18"
              fill="none"
              stroke="#b1bccc"
            />
            <text
              x={219 + (i % 4) * 20}
              y={22 + Math.floor(i / 4) * 20}
              fill="#d8e4ee"
              textAnchor="middle"
              fontSize="12"
            >
              ?
            </text>
          </g>
        ))}
      </svg>
      <figcaption>
        Teal: authored 2 × 2 low-resolution values. Outline: 4 × 4 unknown values. Geometry
        illustration; no MRI, bicubic output or reference.
      </figcaption>
    </figure>
  );
}
export function AutomedBratsT1cSrScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedBratsT1cSrState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-automed-brats-t1c-sr-scene={state.scene}
      data-automed-brats-t1c-sr-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Matching Full MRI / private target unavailable</h3>
          <div className={css.two}>
            <Grid />
            <div>
              <b>Declared 128 × 128 input → 256 × 256 output</b>
              <p>
                2× length, 4× cells: 16,384 → 65,536. Harness has no native images or model weights;
                exact split unresolved.
              </p>
              <small>
                Voxel grid, bicubic implementation and normalization unspecified. No clinical image
                or enhancement result.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Keep geometry, assistance and validity distinct</h3>
          <nav className={css.controls} aria-label="BraTS SR steps">
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
                <b>Public input.npy; private reference.npy stays evaluator-only</b>
                <p>
                  Per-case normalized T1c slice declared; exact case / patient / slice mapping
                  unknown. Private target never acquired or displayed.
                </p>
                <small>
                  “Bicubic downsample, scale 2” does not fix kernel, antialias, alignment, border
                  mode or physical spacing. No degradation/model run.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Select assistance or format rule">
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
                  <>
                    <b>Full Lite: prescribed Swin2SR x2</b>
                    <p>
                      Public caidas/swin2SR-classical-sr-x2-64; document grayscale conversion,
                      validate one public case, inference only.
                    </p>
                    <small>
                      Checkpoint/runtime not bundled; no loading, training or preserved-anatomy
                      claim.
                    </small>
                  </>
                ) : m === 1 ? (
                  <>
                    <b>Full Standard: compare ≥ 3 methods, ≥ 2 neural</b>
                    <p>
                      Public pretrained candidates; bicubic / Lanczos may be one baseline. Select
                      and validate exact 2× geometry.
                    </p>
                    <small>
                      Related Lite / gallery listings have unverified equivalence. No private target
                      access or weight updates.
                    </small>
                  </>
                ) : (
                  <>
                    <b>Task requires float32, finite, normalized 256 × 256</b>
                    <p>
                      Checker accepts any floating dtype, finite 2D array with private-reference
                      shape. Range and constant-image checks absent.
                    </p>
                    <small>
                      Generic “same input shape” prompt conflicts task-specific 2× contract; plural
                      agents_outputs is declared output root. No checker/evaluator execution.
                    </small>
                  </>
                )}
              </>
            ) : (
              <>
                <Grid />
                <small>
                  Authored geometry only: unknown high-resolution values. More cells do not
                  establish recovered detail or clinical edge preservation.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual enhanced.npy absent</h3>
          <code>agents_outputs/&lt;case_id&gt;/enhanced.npy</code>
          <p>
            Intended float32, finite, normalized 256 × 256. No submitted array, patient output,
            target, metric or rating.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later evaluator rules; no private target reveal</h3>
          <ReaderRules state={state} key={state.beatId} />
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Resolve matching source and evaluator assets</h3>
          <p>{source.actual_data_gap}</p>
          <small>
            No patient MRI, high-resolution target, model result, clinical outcome or measured
            performance.
          </small>
        </>
      )}
    </section>
  );
}
export function AutomedBratsT1cSrOutput({ state }: { state: AutomedBratsT1cSrState }) {
  return (
    <aside
      data-automed-brats-t1c-sr-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Symbolic geometry; enhanced.npy empty</b>
      <p>Matching input / private target unavailable.</p>
      <small>Reader-controlled public rules; reset / exit covers. No private answer assets.</small>
    </aside>
  );
}

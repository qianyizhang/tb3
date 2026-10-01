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
  type AutomedDeeplesionDenoiseState,
} from './automedbench-full-deeplesion-denoising-task';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './automedbench-full-deeplesion-denoising-task.module.css';
function ReaderRules({ state }: { state: AutomedDeeplesionDenoiseState }) {
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
        {visible ? 'Cover public evaluator rules' : 'Reveal public evaluator rules'}
      </button>
      {visible ? (
        <div className={css.socket} data-automed-deeplesion-denoise-reference-revealed>
          <b>{reference.role}</b>
          <p>
            All evaluator-supplied case IDs; metric means omit NaNs independently. No task-specific
            normalization/rating map or supplied bands.
          </p>
          <small>
            Private clean targets and model/LPIPS assets absent. “Clinical” is a code composite, not
            clinical validation. No metric or reference pixels.
          </small>
        </div>
      ) : (
        <p>Public evaluator rules covered; private clean target and output absent.</p>
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
        aria-label="Authored normalized noisy two by two cells beside two by two unknown clean or denoised values; same geometry, not CT or a Gaussian realization"
      >
        {fixture.observed_grid.flat().map((v, i) => (
          <g key={`observed-${i}`}>
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
        <text x="120" y="53" fill="#e9f4f7" fontSize="13">
          unknown D
        </text>
        {Array.from({ length: 4 }, (_, i) => (
          <g key={`unknown-${i}`}>
            <rect
              x={230 + (i % 2) * 40}
              y={8 + Math.floor(i / 2) * 40}
              width="38"
              height="38"
              fill="none"
              stroke="#b1bccc"
            />
            <text
              x={249 + (i % 2) * 40}
              y={32 + Math.floor(i / 2) * 40}
              fill="#d8e4ee"
              textAnchor="middle"
              fontSize="14"
            >
              ?
            </text>
          </g>
        ))}
      </svg>
      <figcaption>
        Teal: authored noisy values; outline: unknown clean/output values. Same geometry. Not CT,
        random noise, private target or denoised result.
      </figcaption>
    </figure>
  );
}
export function AutomedDeeplesionDenoiseScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedDeeplesionDenoiseState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-automed-deeplesion-denoise-scene={state.scene}
      data-automed-deeplesion-denoise-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Matching Full noisy CT / private clean target absent</h3>
          <div className={css.two}>
            <Grid />
            <div>
              <b>Declared 512 × 512 normalized CT</b>
              <p>
                262,144 pixels in and out; no Full native cases or split mapping recovered. Symbolic
                values only.
              </p>
              <small>
                σ = 0.05 normalized intensity, not HU, photon noise, dose fraction or real low-dose
                acquisition.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Separate normalized noise from a denoising outcome</h3>
          <nav className={css.controls} aria-label="DeepLesion steps">
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
                <b>Declared additive Gaussian σ = 0.05; variance = 0.0025</b>
                <p>
                  Normalization, seed, clipping, spatial correlation and exact mean specification
                  unavailable. No native noise draw.
                </p>
                <small>
                  Authored 0.98 + 0.05 = 1.03 illustrates range ambiguity; [0,1] requirement does
                  not establish a clipping rule or calibrated CT noise.
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
                    <b>Full Lite: prescribed public pretrained DRUNet</b>
                    <p>
                      Document checkpoint, normalized preprocessing and σ = 0.05 mapping; validate
                      public input pilot, inference only.
                    </p>
                    <small>
                      No checkpoint loaded; exact model noise-conditioning convention and
                      lesion-detail preservation unverified.
                    </small>
                  </>
                ) : m === 1 ? (
                  <>
                    <b>Full Standard: ≥ 3 denoisers, ≥ 2 pretrained neural</b>
                    <p>
                      BM3D may be one classical baseline; DnCNN / Restormer / SwinIR candidates.
                      Choose from public evidence and pilot.
                    </p>
                    <small>
                      No private target access, training or benchmark performance. Related
                      Lite/gallery equivalence unresolved.
                    </small>
                  </>
                ) : (
                  <>
                    <b>Required float32, finite normalized 512 × 512</b>
                    <p>
                      Checker accepts any finite floating 2D private-reference shape, including
                      float64, copy, constant or out-of-range values.
                    </p>
                    <small>
                      Protocol validation is stricter; plural agents_outputs vs singular tier
                      wording retained. No checker or metric executed.
                    </small>
                  </>
                )}
              </>
            ) : (
              <>
                <Grid />
                <small>
                  Authored y = {fixture.toy_y} = 0.40 + 0.05 = 0.50 − 0.05. Clean value and D(y)
                  unknown; no denoised CT.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual enhanced.npy absent</h3>
          <code>agents_outputs/&lt;case_id&gt;/enhanced.npy · 512 × 512</code>
          <p>
            Intended normalized float32. No submitted array, clean CT, inferred lesion boundaries,
            metric or rating.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later evaluator rules; private clean target stays absent</h3>
          <ReaderRules state={state} key={state.beatId} />
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Resolve matching data, noise lineage and evaluator assets</h3>
          <p>{source.actual_data_gap}</p>
          <small>
            No noised native image, model denoising, preserved lesion detail, clinical outcome or
            measured metric.
          </small>
        </>
      )}
    </section>
  );
}
export function AutomedDeeplesionDenoiseOutput({
  state,
}: {
  state: AutomedDeeplesionDenoiseState;
}) {
  return (
    <aside
      data-automed-deeplesion-denoise-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Symbolic noise; enhanced.npy empty</b>
      <p>Matching noisy input / private clean target absent.</p>
      <small>Reader-controlled public rules; reset / exit covers. No private answer assets.</small>
    </aside>
  );
}

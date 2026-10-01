import { useLayoutEffect, useRef, useState } from 'react';
import {
  imagingDynamicMriPack as pack,
  dynamicSteps,
  dynamicMethods,
  operationIndex,
  methodIndex,
  operationFrame,
  type ImagingDynamicMriState,
} from './imaging-dynamic-mri';
import { nativeFrame, resetOnBackward, publicTruthVisible } from './imaging-dynamic-mri-controls';
import type { StoryPlan } from '../contracts.generated';
import css from './imaging-dynamic-mri.module.css';
const titles = {
  input: 'Native point masks · twenty synthetic frames',
  helper: 'Covered source series · already solver-visible',
  operation: 'Measured consistency and temporal neighbors',
  output: 'Unsubmitted magnitude sequence',
  limits: 'Acquisition and aggregation boundaries',
} as const;
function useReset(state: ImagingDynamicMriState, reset: () => void) {
  const prev = useRef(state.frame);
  useLayoutEffect(() => {
    if (resetOnBackward(prev.current, state.frame)) reset();
    prev.current = state.frame;
  }, [state.frame, reset]);
}
function Input({ state }: { state: ImagingDynamicMriState }) {
  const [index, setIndex] = useState(0);
  useReset(state, () => setIndex(0));
  const m = pack.measurement;
  return (
    <div className={css.columns} data-dynamic-mri-input>
      <figure className={css.figure}>
        <svg
          viewBox="0 0 128 128"
          aria-label="Native binary Cartesian point sampling mask; not an MRI image"
          shapeRendering="crispEdges"
        >
          <rect width="128" height="128" fill="#0b1d2a" />
          {m.mask_rows[index].flatMap((row, y) =>
            Array.from(row, (v, x) =>
              v === '1' ? (
                <rect key={`${y}-${x}`} x={x} y={y} width="1" height="1" fill="#73c7e6" />
              ) : null,
            ),
          )}
        </svg>
        <figcaption>128×128 k-space index grid · rows down, columns right</figcaption>
        <div className={css.legend}>
          <span style={{ color: '#73c7e6' }}>■ sampled point</span>
          <span style={{ color: '#c3d8e5' }}>□ unsampled/zero-filled</span>
        </div>
      </figure>
      <div className={css.card}>
        <label htmlFor="dynamic-mri-source-frame">Native source frame 0–19</label>
        <input
          id="dynamic-mri-source-frame"
          type="range"
          min="0"
          max="19"
          value={index}
          onChange={(e) => {
            const n = nativeFrame(Number(e.target.value));
            if (n !== null) setIndex(n);
          }}
        />
        <strong data-dynamic-mri-frame>
          Frame {index} · {m.time_seconds[index].toFixed(2)} synthetic seconds
        </strong>
        <dl className={css.values}>
          <dt>Sampled points</dt>
          <dd>{m.sample_counts[index]}/16384</dd>
          <dt>Center y[64,64]</dt>
          <dd>
            {m.native_kspace_center_64_64[index].map((v) => v.toPrecision(5)).join(' + i ')} a.u.
          </dd>
        </dl>
        <p>{pack.source.sampling}</p>
        <p>{pack.source.geometry}</p>
        <small>
          Mask slider selects native acquisition frame, not a reconstructed anatomy or participant
          result.
        </small>
      </div>
    </div>
  );
}
function Helper({ state }: { state: ImagingDynamicMriState }) {
  const [show, setShow] = useState(false);
  const [tier, setTier] = useState<'L1' | 'L2' | 'L3'>('L1');
  useReset(state, () => {
    setShow(false);
    setTier('L1');
  });
  return (
    <div className={css.columns} data-dynamic-mri-helper>
      <div className={css.card}>
        <b>Source truth stays covered initially</b>
        <p>
          Ground truth ships in visible data. This teaching reveal never makes the solver condition
          blind.
        </p>
        <button
          type="button"
          aria-expanded={show}
          aria-controls="dynamic-mri-source-series"
          onClick={() => setShow(!show)}
        >
          {show ? 'Hide synthetic source series' : 'Reveal synthetic source series'}
        </button>
        {publicTruthVisible(state.scene, show) && (
          <div id="dynamic-mri-source-series" className={css.reveal} data-dynamic-mri-source-series>
            <strong>{pack.helper.truth_role}</strong>
            <div className={css.tokens}>
              {pack.helper.source_pixel_series.map((v, i) => (
                <span key={i}>
                  t{i}: {v.toPrecision(4)} a.u.
                </span>
              ))}
            </div>
          </div>
        )}
        <small>
          Reference appears only after this action; exit/backwards replay resets before paint. No
          saved TV image is displayed.
        </small>
      </div>
      <div className={css.card}>
        <b>Assistance remains separate</b>
        <div className={css.buttons} role="group" aria-label="Dynamic MRI assistance">
          {(['L1', 'L2', 'L3'] as const).map((t) => (
            <button type="button" key={t} aria-pressed={tier === t} onClick={() => setTier(t)}>
              {t}
            </button>
          ))}
        </div>
        <p data-dynamic-mri-tier>{pack.helper.tiers[tier]}</p>
        <p>{pack.source.time}</p>
      </div>
    </div>
  );
}
function Operation({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingDynamicMriState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const step = operationIndex(state),
    method = methodIndex(state);
  return (
    <div data-dynamic-mri-operation>
      <div className={css.buttons} role="group" aria-label="Dynamic MRI canonical operation">
        {dynamicSteps.map((title, i) => (
          <button
            type="button"
            key={title}
            data-dynamic-mri-operation-step={i}
            aria-pressed={step === i}
            disabled={!onSeekFrame}
            onClick={() => onSeekFrame?.(operationFrame(plan, i, method))}
          >
            {title}
          </button>
        ))}
      </div>
      <div className={css.buttons} role="group" aria-label="Dynamic MRI source method">
        {dynamicMethods.map((name, i) => (
          <button
            type="button"
            key={name}
            aria-pressed={method === i}
            disabled={!onSeekFrame}
            onClick={() => onSeekFrame?.(operationFrame(plan, step, i))}
          >
            {name.replaceAll('_', ' ')}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b>{dynamicSteps[step]}</b>
          <p data-dynamic-mri-step>{pack.operation.steps[step]}</p>
          <div className={css.formula}>
            x₀ ↔ x₁ ↔ … ↔ x₁₉
            <br />
            <small>19 adjacent-index differences; no division by time</small>
          </div>
          <p>
            Authored unitless [1,3,2] gives [2,−1]. This illustrates neighboring differences, not
            concentration or a reconstruction.
          </p>
        </div>
        <div className={css.card}>
          <b data-dynamic-mri-method>{pack.operation.methods[dynamicMethods[method]]}</b>
          <p>Spatial axes only; no temporal Fourier transform or coils.</p>
          <strong className={css.caution}>Source PGD contract; no operator or solver runs</strong>
        </div>
      </div>
    </div>
  );
}
function Output({ state }: { state: ImagingDynamicMriState }) {
  const [show, setShow] = useState(false);
  useReset(state, () => setShow(false));
  return (
    <div className={css.columns} data-dynamic-mri-output-schema>
      <div className={css.card}>
        <b>{pack.output.path}</b>
        <div className={css.empty}>
          20×128×128 real magnitude sequence
          <br />
          <strong>UNSUBMITTED</strong>
        </div>
        <button type="button" aria-expanded={show} onClick={() => setShow(!show)}>
          Inspect artifact format
        </button>
        {show && <p data-dynamic-mri-format>{pack.output.format}</p>}
      </div>
      <div className={css.card}>
        <b>Intensity is not physiology</b>
        <p>{pack.source.time}</p>
        <p>
          Source TV archive is retained provenance only. Predicted sequence, score, runtime and
          convergence are absent.
        </p>
        <strong className={css.caution}>No acquired patient image or perfusion estimate</strong>
      </div>
    </div>
  );
}
function Limits({ state }: { state: ImagingDynamicMriState }) {
  const [rule, setRule] = useState<'metric' | 'task_metric' | 'threshold'>('metric');
  const [show, setShow] = useState(false);
  useReset(state, () => {
    setRule('metric');
    setShow(false);
  });
  return (
    <div data-dynamic-mri-limits>
      <div className={css.buttons} role="group" aria-label="Dynamic MRI evaluation boundary">
        {(['metric', 'task_metric', 'threshold'] as const).map((t) => (
          <button type="button" key={t} aria-pressed={rule === t} onClick={() => setRule(t)}>
            {t.replaceAll('_', ' ')}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-dynamic-mri-rule>{pack.output[rule]}</b>
          <button type="button" aria-expanded={show} onClick={() => setShow(!show)}>
            {show ? 'Hide acquisition mismatch' : 'Reveal acquisition mismatch'}
          </button>
          {show && <p data-dynamic-mri-acquisition>{pack.source.noise}</p>}
        </div>
        <div className={css.card}>
          <b>Reopen condition before scoring</b>
          <p>{pack.output.limits}</p>
          <p>
            No clinical time-activity interpretation, model performance or accuracy claim follows
            from synthetic source truth.
          </p>
          <strong className={css.caution}>
            Pixel entries, frames and patients are separate units.
          </strong>
        </div>
      </div>
    </div>
  );
}
export function ImagingDynamicMriScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingDynamicMriState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  return (
    <div className={css.scene} data-dynamic-mri-scene={state.scene}>
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' ? (
        <Input key={state.beatId} state={state} />
      ) : state.scene === 'helper' ? (
        <Helper key={state.beatId} state={state} />
      ) : state.scene === 'operation' ? (
        <Operation key={state.beatId} state={state} plan={plan} onSeekFrame={onSeekFrame} />
      ) : state.scene === 'output' ? (
        <Output key={state.beatId} state={state} />
      ) : (
        <Limits key={state.beatId} state={state} />
      )}
    </div>
  );
}
export function ImagingDynamicMriOutput({ state }: { state: ImagingDynamicMriState }) {
  return (
    <aside className={css.sidebar} data-dynamic-mri-output>
      <span className={css.eyebrow}>Magnitude sequence · unsubmitted</span>
      <h3>Twenty frames, no result</h3>
      <code>{pack.output.path}</code>
      <div className={css.sidebarFields}>
        <span>prediction</span>
        <strong>unset</strong>
        <span>shape</span>
        <strong>20×128×128</strong>
        <span>intensity</span>
        <strong>arbitrary units</strong>
        <span>score/verdict</span>
        <strong>not measured</strong>
      </div>
      <p>
        Native masks and complex measurements accompany a symbolic inverse. Source ground truth is
        solver-visible; teaching reveal is explicit.
      </p>
      <small>
        {state.scene === 'limits'
          ? 'Global 327680 entries versus 20 frame means.'
          : 'No coils, physical spacing or patient geometry.'}
      </small>
    </aside>
  );
}

import { useLayoutEffect, useRef, useState } from 'react';
import { imagingGrappaPack as pack, type ImagingGrappaState } from './imaging-grappa';
import {
  canonicalMethod,
  nativeCoil,
  resetOnBackward,
  canonicalStep,
  operationFrame,
  sourceTargetVisible,
  type GrappaMethod,
} from './imaging-grappa-controls';
import shared from './task-visual.module.css';
import css from './imaging-grappa.module.css';
const titles = {
  input: 'Native full eight-coil arrays · supplied row rule',
  helper: 'ACS training versus source full-data targets',
  operation: 'Cross-coil kernel · weights remain uncomputed',
  output: 'Unsubmitted magnitude image',
  limits: 'RSS reference and scorer semantics',
} as const;
function useReset(state: ImagingGrappaState, reset: () => void) {
  const prev = useRef(state.frame);
  useLayoutEffect(() => {
    if (resetOnBackward(prev.current, state.frame)) reset();
    prev.current = state.frame;
  }, [state.frame, reset]);
}
function pair(v: number[]) {
  return `${v[0].toPrecision(7)} + i(${v[1].toPrecision(7)})`;
}
function Input({ state }: { state: ImagingGrappaState }) {
  const [coil, setCoil] = useState(0);
  useReset(state, () => setCoil(0));
  const m = pack.measurement;
  return (
    <div className={css.columns} data-grappa-input>
      <figure className={css.figure}>
        <svg
          viewBox="0 0 128 128"
          aria-label="Supplied R2 ACS20 rule illustration; raw source is fully sampled"
          shapeRendering="crispEdges"
        >
          <rect width="128" height="128" fill="#0b1d2a" />
          {m.symbolic_rule_retained_rows.map((y) => (
            <rect
              key={y}
              x="0"
              y={y}
              width="128"
              height="1"
              fill={y >= 54 && y <= 73 ? '#eeb989' : '#73c7e6'}
            />
          ))}
          <rect x="0" y="51" width="128" height="1" fill="#92d9ae" />
        </svg>
        <figcaption>Illustrated rule · rows (dim 0) down · columns right</figcaption>
        <div className={css.legend}>
          <span style={{ color: '#73c7e6' }}>■ retained even row</span>
          <span style={{ color: '#eeb989' }}>■ ACS 54–73</span>
          <span style={{ color: '#92d9ae' }}>■ target row 51 · no estimate</span>
        </div>
      </figure>
      <div className={css.card}>
        <label htmlFor="grappa-native-coil">Native coil index 0–7</label>
        <input
          id="grappa-native-coil"
          type="range"
          min="0"
          max="7"
          value={coil}
          onChange={(e) => {
            const n = nativeCoil(Number(e.target.value));
            if (n !== null) setCoil(n);
          }}
        />
        <strong data-grappa-coil>Coil {coil} · native center [64,64]</strong>
        <dl className={css.values}>
          <dt>Full k-space</dt>
          <dd>{pair(m.native_center_kspace[coil])} a.u.</dd>
          <dt>Sensitivity</dt>
          <dd>{pair(m.native_center_sensitivity[coil])} a.u.</dd>
        </dl>
        <p>{pack.source.sampling}</p>
        <p>{pack.source.geometry}</p>
        <small>{m.symbolic_rule}</small>
      </div>
    </div>
  );
}
function Helper({ state }: { state: ImagingGrappaState }) {
  const [show, setShow] = useState(false);
  const [tier, setTier] = useState<'L1' | 'L2' | 'L3'>('L1');
  useReset(state, () => {
    setShow(false);
    setTier('L1');
  });
  return (
    <div className={css.columns} data-grappa-helper>
      <div className={css.card}>
        <b>Native full-data target covered in teaching</b>
        <p>
          Row 51 is missing under the illustrated rule but available in the actual raw full archive.
          Educational cover does not change solver access.
        </p>
        <button
          type="button"
          aria-expanded={show}
          aria-controls="grappa-native-full-target"
          onClick={() => setShow(!show)}
        >
          {show ? 'Hide source full-data target' : 'Reveal source full-data target'}
        </button>
        {sourceTargetVisible(state.scene, show) && (
          <div id="grappa-native-full-target" className={css.reveal} data-grappa-full-target>
            <strong>{pack.helper.target_role}</strong>
            <div className={css.tokens}>
              {pack.helper.native_full_target_pairs.map((v, c) => (
                <span key={c}>
                  coil {c}: {pair(v)}
                </span>
              ))}
            </div>
          </div>
        )}
        <small>
          Covered initially and reset before paint on exit/backward replay. No learned weights or
          estimates shown.
        </small>
      </div>
      <div className={css.card}>
        <b>ACS is calibration data</b>
        <p>{pack.helper.acs}</p>
        <div className={css.buttons} role="group" aria-label="GRAPPA assistance">
          {(['L1', 'L2', 'L3'] as const).map((t) => (
            <button type="button" key={t} aria-pressed={tier === t} onClick={() => setTier(t)}>
              {t}
            </button>
          ))}
        </div>
        <p data-grappa-tier>{pack.helper.tiers[tier]}</p>
        <p>{pack.source.visibility}</p>
      </div>
    </div>
  );
}
function Operation({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingGrappaState;
  plan?: { beats: { scene: string; frames: number }[] };
  onSeekFrame?: (frame: number) => void;
}) {
  const [method, setMethod] = useState<GrappaMethod>('calibration');
  useReset(state, () => setMethod('calibration'));
  return (
    <div data-grappa-operation data-grappa-current-step={canonicalStep(state.progress)}>
      <div className={css.buttons} role="group" aria-label="GRAPPA canonical stages">
        {['Row rule', 'ACS patches', 'Ridge fit', 'IFFT + RSS'].map((label, i) => (
          <button
            type="button"
            key={label}
            data-grappa-step={i}
            aria-pressed={canonicalStep(state.progress) === i}
            onClick={() => {
              const f = plan ? operationFrame(plan, i) : null;
              if (f !== null) onSeekFrame?.(f);
            }}
          >
            {label}
          </button>
        ))}
      </div>
      <div className={css.buttons} role="group" aria-label="GRAPPA source mechanism">
        {(['calibration', 'interpolation', 'combination'] as const).map((t) => (
          <button
            type="button"
            key={t}
            aria-pressed={method === t}
            onClick={() => {
              const v = canonicalMethod(t);
              if (v) setMethod(v);
            }}
          >
            {t}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b>5×5 spatial stencil across 8 coils</b>
          <div className={css.kernel} aria-label="Symbolic missing-row GRAPPA kernel">
            {Array.from({ length: 25 }, (_, i) => (
              <span
                key={i}
                data-kind={i === 12 ? 'target' : Math.floor(i / 5) % 2 === 1 ? 'source' : 'hole'}
              >
                {i === 12 ? 'T' : Math.floor(i / 5) % 2 === 1 ? 'S' : '·'}
              </span>
            ))}
          </div>
          <small>S: acquired neighbors · T: target · repeated across 8 coils</small>
          <ol className={css.steps}>
            {pack.operation.steps.map((s, i) => (
              <li key={s} data-active={canonicalStep(state.progress) === i}>
                {s}
              </li>
            ))}
          </ol>
        </div>
        <div className={css.card}>
          <b data-grappa-method>{pack.operation.methods[method]}</b>
          <p>{pack.operation.kernel}</p>
          <strong className={css.caution}>
            No calibration solve, missing samples or reconstructed image computed.
          </strong>
        </div>
      </div>
    </div>
  );
}
function Output({ state }: { state: ImagingGrappaState }) {
  const [show, setShow] = useState(false);
  useReset(state, () => setShow(false));
  return (
    <div className={css.columns} data-grappa-output-schema>
      <div className={css.card}>
        <b>{pack.output.path}</b>
        <div className={css.empty}>
          128×128 real magnitude image
          <br />
          <strong>UNSUBMITTED</strong>
        </div>
        <button type="button" aria-expanded={show} onClick={() => setShow(!show)}>
          Inspect artifact format
        </button>
        {show && <p data-grappa-format>{pack.output.format}</p>}
      </div>
      <div className={css.card}>
        <b>RSS is a coil-combination convention</b>
        <p>{pack.source.units}</p>
        <p>
          Saved source GRAPPA/zero-fill performance is not shown. Prediction, reconstructed image,
          metric and verdict remain absent.
        </p>
        <strong className={css.caution}>Synthetic phantom is not an acquired patient brain.</strong>
      </div>
    </div>
  );
}
function Limits({ state }: { state: ImagingGrappaState }) {
  const [rule, setRule] = useState<'metric' | 'reference_selection' | 'threshold'>(
    'reference_selection',
  );
  const [show, setShow] = useState(false);
  useReset(state, () => {
    setRule('reference_selection');
    setShow(false);
  });
  return (
    <div data-grappa-limits>
      <div className={css.buttons} role="group" aria-label="GRAPPA evaluation boundary">
        {(['metric', 'reference_selection', 'threshold'] as const).map((t) => (
          <button type="button" key={t} aria-pressed={rule === t} onClick={() => setRule(t)}>
            {t.replaceAll('_', ' ')}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-grappa-rule>{pack.output[rule]}</b>
          <button type="button" aria-expanded={show} onClick={() => setShow(!show)}>
            {show ? 'Hide SSIM implementation difference' : 'Reveal SSIM implementation difference'}
          </button>
          {show && <p data-grappa-ssim>{pack.output.task_metric}</p>}
        </div>
        <div className={css.card}>
          <b>Reopen reference and visibility condition</b>
          <p>{pack.output.limits}</p>
          <p>
            16384 pixel entries are the numerical error unit; 8 coils are encoding channels, not 8
            patients. Geometry and current data establish no clinical performance.
          </p>
          <strong className={css.caution}>
            Source metrics are provenance, not participant scores.
          </strong>
        </div>
      </div>
    </div>
  );
}
export function ImagingGrappaScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingGrappaState;
  plan?: { beats: { scene: string; frames: number }[] };
  onSeekFrame?: (frame: number) => void;
}) {
  return (
    <div className={css.scene} data-grappa-scene={state.scene}>
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
export function ImagingGrappaOutput({ state }: { state: ImagingGrappaState }) {
  return (
    <aside className={`${shared.storyOutput} ${css.sidebar}`} data-grappa-output>
      <span className={shared.storyEyebrow}>GRAPPA artifact · unsubmitted</span>
      <h3>One magnitude image, no result</h3>
      <code>{pack.output.path}</code>
      <div className={css.sidebarFields}>
        <span>prediction</span>
        <strong>unset</strong>
        <span>shape</span>
        <strong>128×128</strong>
        <span>reference</span>
        <strong>RSS versus phantom</strong>
        <span>metric/verdict</span>
        <strong>not measured</strong>
      </div>
      <p>
        Actual raw data are fully sampled across 8 coils. Illustrated R2/ACS20 mask is a supplied
        rule; full target reveal is educational.
      </p>
      <small>
        {state.scene === 'limits'
          ? 'Pixel denominator 16384; reference semantics matter.'
          : 'No patient geometry or calibrated intensity.'}
      </small>
    </aside>
  );
}

import { useLayoutEffect, useRef, useState } from 'react';
import {
  imagingUltrasoundSosPack as pack,
  type ImagingUltrasoundSosState as State,
} from './imaging-ultrasound-sos';
import {
  operationIndex,
  operationFrame,
  branchIndex,
  nativeAngle,
  signedSlowness,
  resetOnBackward,
} from './imaging-ultrasound-sos-controls';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging-ultrasound-sos.module.css';
const titles = {
  input: 'Native noisy detector trace · uncalibrated time',
  helper: 'Source phantom and clean sums · already solver-visible',
  operation: 'Signed slowness and source inverse conventions',
  output: 'Unsubmitted speed map',
  limits: 'Speed reference versus cropped slowness',
} as const;
function useReset(s: State, reset: () => void) {
  const prev = useRef({ frame: s.frame, beat: s.beatId });
  const stable = s.frame >= prev.current.frame && s.beatId === prev.current.beat;
  useLayoutEffect(() => {
    if (resetOnBackward(prev.current.frame, s.frame) || s.beatId !== prev.current.beat) reset();
    prev.current = { frame: s.frame, beat: s.beatId };
  }, [s.frame, s.beatId, reset]);
  return stable;
}
const number = (n: number) => n.toPrecision(7);
function Input({ state }: { state: State }) {
  const [index, setIndex] = useState(0);
  useReset(state, () => setIndex(0));
  const m = pack.measurement;
  const scale = Math.max(...m.native_detector_trace.map(Math.abs));
  const points = m.native_detector_trace
    .map((v, i) => `${15 + i * 4},${85 - (65 * v) / scale}`)
    .join(' ');
  return (
    <div className={css.columns} data-sos-input>
      <figure className={css.figure}>
        <svg
          viewBox="0 0 270 170"
          aria-label="Exact native noisy detector 64 trace; angle index increases right; projection units uncalibrated"
        >
          <rect width="270" height="170" fill="#0b1d2a" />
          <line x1="15" x2="252" y1="85" y2="85" stroke="#eeb989" strokeDasharray="4 4" />
          <polyline points={points} fill="none" stroke="#73c7e6" strokeWidth="2" />
          <circle
            cx={15 + index * 4}
            cy={85 - (65 * m.native_detector_trace[index]) / scale}
            r="4"
            fill="#92d9ae"
          />
        </svg>
        <figcaption>Native detector 64 · angle index 0–59 →</figcaption>
        <div className={css.legend}>
          <span style={{ color: '#73c7e6' }}>— noisy source trace</span>
          <span style={{ color: '#eeb989' }}>┄ zero baseline</span>
          <span style={{ color: '#92d9ae' }}>● selected native sample</span>
        </div>
        <small>
          Vertical display scale ±{number(scale)} source sums. No physical time calibration.
        </small>
      </figure>
      <div className={css.card}>
        <label htmlFor="sos-native-angle">Angle index 0–59</label>
        <input
          id="sos-native-angle"
          type="range"
          min="0"
          max="59"
          value={index}
          onChange={(e) => {
            const n = nativeAngle(Number(e.target.value));
            if (n !== null) setIndex(n);
          }}
        />
        <strong data-sos-sample>
          angle {m.angles[index]}° · {number(m.native_detector_trace[index])} source sum
        </strong>
        <p>{pack.source.geometry}</p>
        <p>{pack.source.units}</p>
        <small>{pack.source.sampling}</small>
      </div>
    </div>
  );
}
function Helper({ state }: { state: State }) {
  const [show, setShow] = useState(false);
  const [tier, setTier] = useState<'L1' | 'L2' | 'L3'>('L1');
  const stable = useReset(state, () => {
    setShow(false);
    setTier('L1');
  });
  return (
    <div className={css.columns} data-sos-helper>
      <div className={css.card}>
        <b>Educational source-truth cover</b>
        <p>
          Clean/full projections and phantom truth are already in supplied data. Covering this
          teaching view does not establish private evaluation.
        </p>
        <button
          type="button"
          aria-expanded={show && stable}
          aria-controls="sos-native-source-truth"
          onClick={() => setShow(!show)}
        >
          {show && stable ? 'Hide source truth' : 'Reveal source truth'}
        </button>
        {show && stable && (
          <div id="sos-native-source-truth" className={css.reveal} data-sos-source-truth>
            <strong>{pack.helper.target_role}</strong>
            <p>Center speed: {number(pack.helper.source_center_speed)} m/s</p>
            <p>Center Δs: {number(pack.helper.source_center_delta_slowness)} s/m</p>
            <p>
              Clean detector 64 angle 0: {number(pack.helper.native_clean_detector_trace[0])} source
              sum
            </p>
          </div>
        )}
        <small>Covered initially; backward replay and chapter exit reset before paint.</small>
      </div>
      <div className={css.card}>
        <b>Assistance changes supplied design</b>
        <div className={css.buttons} role="group" aria-label="Ultrasound assistance">
          {(['L1', 'L2', 'L3'] as const).map((t) => (
            <button key={t} type="button" aria-pressed={tier === t} onClick={() => setTier(t)}>
              {t}
            </button>
          ))}
        </div>
        <p data-sos-tier>{pack.helper.tiers[tier]}</p>
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
  state: State;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const step = operationIndex(state.progress);
  const method = (['fbp', 'sart', 'tv'] as const)[branchIndex(state.detail)];
  const [speed, setSpeed] = useState(1500);
  useReset(state, () => {
    setSpeed(1500);
  });
  return (
    <div data-sos-operation>
      <div className={css.buttons} role="group" aria-label="Canonical ultrasound operation steps">
        {['Signed slowness', 'Inverse conventions', 'Adjoint normalization'].map((label, i) => (
          <button
            key={label}
            type="button"
            aria-pressed={step === i}
            onClick={() => onSeekFrame?.(operationFrame(plan, i, branchIndex(state.detail)))}
          >
            {i + 1}. {label}
          </button>
        ))}
      </div>
      {step === 0 ? (
        <div className={css.card}>
          <b>Symbolic baseline algebra · not a native finding</b>
          <div className={css.buttons} role="group" aria-label="Symbolic sound speed">
            {[1450, 1500, 2500].map((c) => (
              <button key={c} type="button" aria-pressed={speed === c} onClick={() => setSpeed(c)}>
                {c} m/s
              </button>
            ))}
          </div>
          <strong data-sos-sign>
            Δs = {number(signedSlowness(speed)!)} s/m ·{' '}
            {speed < 1500 ? 'positive' : speed > 1500 ? 'negative' : 'zero'}
          </strong>
          <p>{pack.operation.formula}</p>
          <small>{pack.operation.sign}</small>
        </div>
      ) : step === 1 ? (
        <div className={css.card}>
          <b>Source inverse conventions · no reconstruction</b>
          <div className={css.buttons} role="group" aria-label="Source inverse convention">
            {(['fbp', 'sart', 'tv'] as const).map((t, i) => (
              <button
                key={t}
                type="button"
                aria-pressed={method === t}
                onClick={() => onSeekFrame?.(operationFrame(plan, 1, i))}
              >
                {t.toUpperCase()}
              </button>
            ))}
          </div>
          <strong data-sos-method>{pack.operation.methods[method]}</strong>
        </div>
      ) : (
        <div className={css.card}>
          <b>Adjoint scale and stopping assumptions</b>
          <p>{pack.operation.adjoint}</p>
          <strong className={css.caution}>
            No forward operator, inverse, reconstruction or convergence trial.
          </strong>
        </div>
      )}
    </div>
  );
}
function Output({ state }: { state: State }) {
  const [show, setShow] = useState(false);
  const stable = useReset(state, () => setShow(false));
  return (
    <div className={css.columns} data-sos-output-schema>
      <div className={css.card}>
        <b>{pack.output.path}</b>
        <div className={css.empty}>
          128×128 real speed map · m/s
          <br />
          <strong>UNSUBMITTED</strong>
        </div>
        <button type="button" aria-expanded={show && stable} onClick={() => setShow(!show)}>
          Inspect artifact format
        </button>
        {show && stable && <p data-sos-format>{pack.output.format}</p>}
      </div>
      <div className={css.card}>
        <b>Speed is distinct from signed perturbation</b>
        <p>
          Δs may be negative while absolute slowness remains positive. The source denominator floor
          1e−8 gives a mathematical ceiling 1e8 m/s, not a clinically validated range.
        </p>
        <strong className={css.caution}>
          Synthetic source phantom is not patient acquisition or tissue diagnosis.
        </strong>
      </div>
    </div>
  );
}
function Limits({ state }: { state: State }) {
  const [rule, setRule] = useState<'metric' | 'reference_selection' | 'threshold'>(
    'reference_selection',
  );
  const [show, setShow] = useState(false);
  const stable = useReset(state, () => {
    setRule('reference_selection');
    setShow(false);
  });
  return (
    <div data-sos-limits>
      <div className={css.buttons} role="group" aria-label="Ultrasound evaluation mechanics">
        {(['metric', 'reference_selection', 'threshold'] as const).map((r) => (
          <button key={r} type="button" aria-pressed={rule === r} onClick={() => setRule(r)}>
            {r.replaceAll('_', ' ')}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <strong data-sos-rule>{pack.output[rule]}</strong>
          <button type="button" aria-expanded={show && stable} onClick={() => setShow(!show)}>
            {show && stable ? 'Hide source metric boundary' : 'Reveal source metric boundary'}
          </button>
          {show && stable && <p data-sos-metric-boundary>{pack.output.task_metric}</p>}
        </div>
        <div className={css.card}>
          <b>Reopen calibration and reference condition</b>
          <p>{pack.output.limits}</p>
          <small>
            7680 projection samples and 16384 speed entries are computational units, not patients.
            No reconstruction accuracy, clinical accuracy or generic verdict is measured.
          </small>
        </div>
      </div>
    </div>
  );
}
export function ImagingUltrasoundSosScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: State;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  return (
    <div className={css.scene} data-sos-scene={state.scene}>
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
export function ImagingUltrasoundSosOutput({ state }: { state: State }) {
  return (
    <aside className={`${shared.storyOutput} ${css.sidebar}`} data-sos-output>
      <span className={shared.storyEyebrow}>Ultrasound artifact · unsubmitted</span>
      <h3>One speed map, no result</h3>
      <code>{pack.output.path}</code>
      <div className={css.sidebarFields}>
        <span>prediction</span>
        <strong>unset</strong>
        <span>shape / units</span>
        <strong>128×128 / m/s</strong>
        <span>source reference</span>
        <strong>solver-visible phantom</strong>
        <span>metric / verdict</span>
        <strong>not measured</strong>
      </div>
      <p>
        Native projection values omit physical pixel-length scaling. Source ring metadata does not
        establish ring ray paths.
      </p>
      <small>
        {state.scene === 'limits'
          ? 'Generic speed denominator 16384; cropped slowness differs.'
          : 'No acquired patient or calibrated travel time.'}
      </small>
    </aside>
  );
}

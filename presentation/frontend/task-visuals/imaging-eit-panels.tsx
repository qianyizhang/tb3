import { useLayoutEffect, useRef, useState } from 'react';
import {
  imagingEitPack as pack,
  eitSteps,
  eitMethods,
  operationIndex,
  methodIndex,
  operationFrame,
  type ImagingEitState,
} from './imaging-eit';
import type { StoryPlan } from '../contracts.generated';
import { measurementRow, resetOnBackward, publicTruthVisible } from './imaging-eit-controls';
import css from './imaging-eit.module.css';
const titles = {
  input: 'Native mesh · ordered boundary voltages',
  helper: 'Visible source truth · deliberate teaching reveal',
  operation: 'Difference inverse · separate domains and scales',
  output: 'Unsubmitted artifact · no conductivity map',
  limits: 'Reference meaning precedes numerical agreement',
} as const;
function useBackwardReset(state: ImagingEitState, reset: () => void) {
  const prev = useRef(state.frame);
  useLayoutEffect(() => {
    if (resetOnBackward(prev.current, state.frame)) reset();
    prev.current = state.frame;
  }, [state.frame, reset]);
}
function Input({ state }: { state: ImagingEitState }) {
  const [index, setIndex] = useState(0);
  useBackwardReset(state, () => setIndex(0));
  const m = pack.measurement;
  const row = m.meas_mat[index];
  const drive = m.ex_mat[row[2]];
  const p = (i: number) => `${160 + m.node[i][0] * 132},${154 - m.node[i][1] * 132}`;
  const role = (e: number) =>
    e === drive[0]
      ? 'inject'
      : e === drive[1]
        ? 'return'
        : e === row[0] || e === row[1]
          ? 'measure'
          : 'idle';
  return (
    <div className={css.columns} data-eit-input>
      <figure className={css.figure}>
        <svg
          viewBox="0 0 320 310"
          aria-label="Native synthetic EIT triangular mesh and selected electrode protocol"
        >
          {m.element.map((tri, i) => (
            <polygon
              key={i}
              points={tri.map(p).join(' ')}
              fill="none"
              stroke="#456477"
              strokeWidth="0.35"
            />
          ))}
          {m.el_pos.map((n, e) => (
            <g key={e} data-electrode={e} data-role={role(e)}>
              <circle
                cx={160 + m.node[n][0] * 132}
                cy={154 - m.node[n][1] * 132}
                r="5"
                fill={
                  role(e) === 'inject'
                    ? '#f5b75b'
                    : role(e) === 'return'
                      ? '#e087ac'
                      : role(e) === 'measure'
                        ? '#73c7e6'
                        : '#abbec7'
                }
              />
              <text
                x={160 + m.node[n][0] * 146}
                y={158 - m.node[n][1] * 146}
                textAnchor="middle"
                fill="#f2f5fa"
                fontSize="10"
              >
                {e}
              </text>
            </g>
          ))}
          <circle
            cx={160 + m.node[m.ref_node][0] * 132}
            cy={154 - m.node[m.ref_node][1] * 132}
            r="3"
            fill="#b6d591"
          />
        </svg>
        <figcaption>376 nodes · 686 triangles · 16 electrodes · x right/y up</figcaption>
        <div className={css.legend}>
          <span style={{ color: '#f5b75b' }}>● +1 injection</span>
          <span style={{ color: '#e087ac' }}>● −1 return</span>
          <span style={{ color: '#73c7e6' }}>● N−M pair</span>
          <span style={{ color: '#b6d591' }}>● ground node 16</span>
        </div>
      </figure>
      <div className={css.card}>
        <label htmlFor="eit-measurement-index">BP native measurement index 0–207</label>
        <input
          id="eit-measurement-index"
          type="range"
          min="0"
          max="207"
          value={index}
          onChange={(e) => {
            const n = measurementRow(Number(e.target.value), m.v0.length);
            if (n !== null) setIndex(n);
          }}
        />
        <strong data-eit-measurement>
          Row {index}: drive {drive.join('→')}; measure {row[0]}−{row[1]}
        </strong>
        <dl className={css.values}>
          <dt>v0 background</dt>
          <dd>{m.v0[index].toPrecision(7)} V*</dd>
          <dt>v1 source anomaly</dt>
          <dd>{m.v1[index].toPrecision(7)} V*</dd>
        </dl>
        <p>{pack.source.voltage}</p>
        <p>{pack.source.contact}</p>
        <small>
          *README units; synthetic model values, no patient calibration. Slider selects an ordered
          measurement, not a reconstructed pixel.
        </small>
      </div>
    </div>
  );
}
function Helper({ state }: { state: ImagingEitState }) {
  const [reveal, setReveal] = useState(false);
  const [tier, setTier] = useState<'L1' | 'L2' | 'L3'>('L1');
  useBackwardReset(state, () => {
    setReveal(false);
    setTier('L1');
  });
  return (
    <div className={css.columns} data-eit-helper>
      <div className={css.card}>
        <b>Data visibility is part of the condition</b>
        <p>
          Raw archive contains perm_anomaly. Entire data directory is visible to the solver; hidden
          teaching text does not establish a blind task.
        </p>
        <button
          type="button"
          aria-expanded={reveal}
          aria-controls="eit-source-truth"
          onClick={() => setReveal(!reveal)}
        >
          {reveal ? 'Hide source conductivity truth' : 'Reveal source conductivity truth'}
        </button>
        {publicTruthVisible(state.scene, reveal) && (
          <div id="eit-source-truth" className={css.reveal} data-eit-source-truth>
            <strong>{pack.helper.public_truth_role}</strong>
            <ul>
              {Object.entries(pack.helper.public_truth).map(([key, value]) => (
                <li key={key}>
                  {key}: {value}
                </li>
              ))}
            </ul>
          </div>
        )}
        <small>
          Explicit teaching reveal resets on exit or backward replay. No private reference exists in
          this pack.
        </small>
      </div>
      <div className={css.card}>
        <b>Assistance changes; measurement units do not</b>
        <div className={css.buttons} role="group" aria-label="EIT assistance level">
          {(['L1', 'L2', 'L3'] as const).map((t) => (
            <button type="button" key={t} aria-pressed={tier === t} onClick={() => setTier(t)}>
              {t}
            </button>
          ))}
        </div>
        <p data-eit-tier>{pack.helper.tiers[tier]}</p>
        <p>{pack.source.geometry}</p>
        <p>{pack.source.protocol}</p>
      </div>
    </div>
  );
}
function Operation({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingEitState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const step = operationIndex(state),
    method = eitMethods[methodIndex(state)],
    selected = pack.operation.methods[method];
  return (
    <div data-eit-operation>
      <div className={css.buttons} role="group" aria-label="EIT canonical operation steps">
        {eitSteps.map((title, i) => (
          <button
            key={title}
            type="button"
            data-eit-operation-step={i}
            aria-pressed={step === i}
            disabled={!onSeekFrame}
            onClick={() => onSeekFrame?.(operationFrame(plan, i, methodIndex(state)))}
          >
            {title}
          </button>
        ))}
      </div>
      <div className={css.buttons} role="group" aria-label="EIT inverse method">
        {eitMethods.map((title, i) => (
          <button
            key={title}
            type="button"
            data-eit-method-branch={i}
            aria-pressed={method === title}
            disabled={!onSeekFrame}
            onClick={() => onSeekFrame?.(operationFrame(plan, step, i))}
          >
            {title}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b>{eitSteps[step]}</b>
          <p>{pack.operation.steps[step]}</p>
          {step === 1 ? (
            <p>
              Authored unitless gauge toy: potentials 3−1 = 2; adding +10 gives 13−11 = 2. Neither
              values nor offset are native patient measurements.
            </p>
          ) : step === 2 ? (
            <>
              <strong className={css.formula}>δV ≈ J δσ</strong>
              <p>{pack.operation.linearization}</p>
            </>
          ) : (
            <p>
              Native voltage row, point-electrode protocol and spatial output index are distinct. No
              FEM or inverse calculation is performed.
            </p>
          )}
        </div>
        <div className={css.card}>
          <b data-eit-method>
            {method} · {selected.domain}
          </b>
          <code className={css.formula}>{selected.normalize}</code>
          <p>{selected.inverse}</p>
          <code>{selected.path}</code>
          <small>
            No inverse computed. Method output is not automatically calibrated absolute S/m.
          </small>
        </div>
      </div>
    </div>
  );
}
function Output({ state }: { state: ImagingEitState }) {
  const [show, setShow] = useState(false);
  useBackwardReset(state, () => setShow(false));
  return (
    <div className={css.columns} data-eit-output-schema>
      <div className={css.card}>
        <b>{pack.output.path}</b>
        <div className={css.empty}>
          Conductivity artifact
          <br />
          <strong>UNSUBMITTED</strong>
        </div>
        <button type="button" aria-expanded={show} onClick={() => setShow(!show)}>
          Inspect generic output contract
        </button>
        {show && <p data-eit-format>{pack.output.generic}</p>}
      </div>
      <div className={css.card}>
        <b>Keep spatial domains explicit</b>
        <dl className={css.values}>
          <dt>BP</dt>
          <dd>376 node values</dd>
          <dt>JAC</dt>
          <dd>686 element values</dd>
          <dt>GREIT</dt>
          <dd>32×32 grid + xg/yg</dd>
        </dl>
        <p>
          Source saved BP output is retained audit evidence only. It is not this participant’s
          reconstruction.
        </p>
        <strong className={css.caution}>Prediction, map, score and verdict absent</strong>
      </div>
    </div>
  );
}
function Limits({ state }: { state: ImagingEitState }) {
  const [rule, setRule] = useState<'metric' | 'reference_selection' | 'threshold'>('metric');
  const [show, setShow] = useState(false);
  useBackwardReset(state, () => {
    setRule('metric');
    setShow(false);
  });
  return (
    <div data-eit-limits>
      <div className={css.buttons} role="group" aria-label="EIT evaluator boundary">
        {(['metric', 'reference_selection', 'threshold'] as const).map((t) => (
          <button type="button" key={t} aria-pressed={rule === t} onClick={() => setRule(t)}>
            {t.replaceAll('_', ' ')}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-eit-rule>
            {rule === 'reference_selection' ? pack.output.reference_summary : pack.output[rule]}
          </b>
          <button type="button" aria-expanded={show} onClick={() => setShow(!show)}>
            {show ? 'Hide source method metric rule' : 'Reveal source method metric rule'}
          </button>
          {show && <p data-eit-task-metric>{pack.output.task_metric}</p>}
          <p>
            No evaluator has run. Error is over array entries; domain size is not a patient/sample
            denominator.
          </p>
        </div>
        <div className={css.card}>
          <b>Reopen the scientific contract</b>
          <p>{pack.output.limits}</p>
          <p>
            BP/GREIT 208 and JAC 192 refer to boundary measurement counts, distinct from output
            spatial entries.
          </p>
          <strong className={css.caution}>
            Synthetic phantom; no clinical or model performance claim
          </strong>
        </div>
      </div>
    </div>
  );
}
export function ImagingEitScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingEitState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  return (
    <div className={css.scene} data-eit-scene={state.scene}>
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
export function ImagingEitOutput({ state }: { state: ImagingEitState }) {
  return (
    <aside className={css.sidebar} data-eit-output>
      <span className={css.eyebrow}>Inverse artifact · unsubmitted</span>
      <h3>Conductivity domain undecided</h3>
      <code>{pack.output.path}</code>
      <div className={css.sidebarFields}>
        <span>prediction</span>
        <strong>unset</strong>
        <span>reference key</span>
        <strong>unresolved</strong>
        <span>scale / domain</span>
        <strong>unresolved</strong>
        <span>metric / verdict</span>
        <strong>not measured</strong>
      </div>
      <p>
        Source truth is already solver-visible. No participant reconstruction, physiological
        interpretation or independent reference.
      </p>
      <small>
        {state.scene === 'limits'
          ? 'Range RMSE and cosine over matched array entries.'
          : 'Native synthetic input; symbolic inverse contract.'}
      </small>
    </aside>
  );
}

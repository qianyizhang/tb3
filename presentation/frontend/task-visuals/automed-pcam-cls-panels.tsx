import { useState, useLayoutEffect, useRef } from 'react';
import {
  canonicalNamedClass,
  upstreamBinaryClass,
  submissionFields,
  shouldResetControls,
} from './automed-pcam-cls-controls';
import { automedPcamClsPack as pack, type AutomedPcamClsState } from './automed-pcam-cls';
import shared from './task-visual.module.css';
import css from './automed-pcam-cls.module.css';
function useReset(state: AutomedPcamClsState, reset: () => void) {
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (shouldResetControls(previous.current, state.frame)) reset();
    previous.current = state.frame;
  }, [state.frame, reset]);
}
const titles = {
  input: 'Inspect center-label geometry',
  helper: 'Reveal upstream teaching figure',
  operation: 'Verify method and mapping',
  output: 'Inspect submission alternatives',
  limits: 'Separate scoring denominators',
} as const;
function Socket({ title }: { title: string }) {
  return (
    <div className={css.socket}>
      <b>{title}</b>
      <span>Absent · no image, label or output synthesized</span>
    </div>
  );
}
function Input({ state }: { state: AutomedPcamClsState }) {
  const [window, setWindow] = useState<'center' | 'context'>('center');
  useReset(state, () => setWindow('center'));
  return (
    <div className={css.columns} data-pcam-cls-input>
      <div className={css.card}>
        <b>Symbolic input geometry · no tissue pixels</b>
        <svg
          viewBox="0 0 112 112"
          className={css.geometry}
          role="img"
          aria-label="Symbolic 96 pixel tile with central 32 pixel labeling window"
        >
          <rect x="8" y="8" width="96" height="96" fill="#182c38" stroke="#78909b" />
          <rect
            x="40"
            y="40"
            width="32"
            height="32"
            fill={window === 'center' ? '#185d68' : '#182c38'}
            stroke="#18c6d4"
            strokeDasharray="2 2"
          />
          <text x="56" y="59" textAnchor="middle" fill="#eaf1f4" fontSize="6">
            32 x 32
          </text>
          <text x="56" y="110" textAnchor="middle" fill="#b7cbd4" fontSize="6">
            96 x 96 px
          </text>
        </svg>
        <div className={css.buttons} role="group" aria-label="PCam label window">
          <button
            type="button"
            aria-pressed={window === 'center'}
            onClick={() => setWindow('center')}
          >
            Label center
          </button>
          <button
            type="button"
            aria-pressed={window === 'context'}
            onClick={() => setWindow('context')}
          >
            Outer context
          </button>
        </div>
        <p data-pcam-cls-window>
          {window === 'center'
            ? 'Positive iff at least one annotated tumor pixel lies in the center.'
            : 'Outer tumor alone does not set positive; context supplies model information.'}
        </p>
      </div>
      <div className={css.card}>
        <b>Native Full image absent</b>
        <p>
          Central half-open bounds: 32≤x&lt;64,32≤y&lt;64 in a 96 pixel grid. This frame is a rule
          diagram, not a tumor mask.
        </p>
        <p>No verified native row pair, physical calibration or WSI coordinates.</p>
        <p>
          A training gzip prefix was acquired, but chunk-index metadata lies outside the decoded
          prefix; no image offset guessed.
        </p>
      </div>
    </div>
  );
}
function Helper({ state }: { state: AutomedPcamClsState }) {
  const [revealed, setRevealed] = useState(false);
  useReset(state, () => setRevealed(false));
  return (
    <div data-pcam-cls-helper>
      <button
        type="button"
        className={css.reveal}
        aria-expanded={revealed}
        aria-controls="pcam-annotated-figure"
        onClick={() => setRevealed(!revealed)}
      >
        {revealed ? 'Hide annotated source figure' : 'Reveal annotated source figure'}
      </button>
      {revealed ? (
        <figure id="pcam-annotated-figure" className={css.figure} data-pcam-cls-figure-revealed>
          <img
            src={pack.figureUrl}
            alt="Official PCam README collage with source green positive-label boxes; row IDs and partition unknown, not Full cases"
          />
          <figcaption>
            1600 x 400 source collage · green boxes source positives · no row/Full IDs or partition
            match
          </figcaption>
        </figure>
      ) : (
        <div id="pcam-annotated-figure" className={css.socket} data-pcam-cls-figure-hidden>
          <b>Label-marked official figure covered</b>
          <span>Reader reveal; no private or exact training target</span>
        </div>
      )}
      <div className={css.columns}>
        <div className={css.card}>
          <b>Upstream numeric → Full canonical string</b>
          <div className={css.fields}>
            {Object.entries(pack.helper.source_mapping).map(([n]) => (
              <div key={n}>
                <code>
                  {n} → {upstreamBinaryClass(Number(n))}
                </code>
                <span>Source mapping</span>
              </div>
            ))}
          </div>
          <p>Positive is a center-pixel rule, not a patient diagnosis.</p>
        </div>
        <div className={css.card}>
          <b>Source split policy</b>
          <p>Train 262144 / validation 32768 / test 32768; WSI-disjoint.</p>
          <p>{pack.helper.split_boundary}</p>
          <p>
            Public train labels recovered; no verified image pair. No individual source label shown.
          </p>
        </div>
      </div>
    </div>
  );
}
function Operation({ state }: { state: AutomedPcamClsState }) {
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  const [token, setToken] = useState('');
  useReset(state, () => {
    setTier('lite');
    setToken('');
  });
  return (
    <div data-pcam-cls-operation>
      <div className={css.buttons} role="group" aria-label="PCam classification assistance">
        {(['lite', 'standard'] as const).map((t) => (
          <button key={t} type="button" aria-pressed={tier === t} onClick={() => setTier(t)}>
            {t}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b>{tier} guidance</b>
          <p>{pack.helper.tiers[tier]}</p>
          <ol className={css.steps}>
            {pack.operation.steps.map((s, i) => (
              <li key={s} data-active={state.progress > (i + 1) / 4}>
                {s}
              </li>
            ))}
          </ol>
        </div>
        <div className={css.card}>
          <label>
            Mapping exercise · hypothetical named checkpoint token
            <select
              value={token}
              onChange={(e) =>
                setToken(canonicalNamedClass(e.target.value, pack.helper.classes) ?? '')
              }
              aria-label="Hypothetical canonical token"
            >
              <option value="">Select a source token</option>
              {pack.helper.classes.map((c) => (
                <option key={c} value={c}>
                  {c.toUpperCase()}
                </option>
              ))}
            </select>
          </label>
          <p data-pcam-cls-map>
            {token ? `Canonical spelling: ${token}` : 'No checkpoint index supplied'}
          </p>
          <p>
            String mapping only; no logits, source label or prediction. Always inspect the actual
            checkpoint id2label before inference.
          </p>
        </div>
      </div>
    </div>
  );
}
function Output({ state }: { state: AutomedPcamClsState }) {
  const [format, setFormat] = useState<'csv' | 'json'>('csv');
  useReset(state, () => setFormat('csv'));
  return (
    <div data-pcam-cls-output-schema>
      <div className={css.buttons} role="group" aria-label="PCam classification submission format">
        {(['csv', 'json'] as const).map((f) => (
          <button key={f} type="button" aria-pressed={format === f} onClick={() => setFormat(f)}>
            {f}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-pcam-cls-format>{pack.output.formats[format]}</b>
          <div className={css.fields}>
            {submissionFields(format).map((c) => (
              <div key={c}>
                <code>{c}</code>
                <span>unset</span>
              </div>
            ))}
          </div>
          <p>{pack.output.format_boundary}</p>
        </div>
        <Socket title="Unsubmitted artifact" />
      </div>
    </div>
  );
}
function Limits({ state }: { state: AutomedPcamClsState }) {
  const [metric, setMetric] = useState<'accuracy' | 'balanced_accuracy'>('accuracy');
  useReset(state, () => setMetric('accuracy'));
  return (
    <div data-pcam-cls-limits>
      <div className={css.buttons} role="group" aria-label="Classification metric denominator">
        {(['accuracy', 'balanced_accuracy'] as const).map((m) => (
          <button key={m} type="button" aria-pressed={metric === m} onClick={() => setMetric(m)}>
            {m.replaceAll('_', ' ')}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-pcam-cls-metric>{pack.output[metric]}</b>
          <p>{pack.output.units}</p>
          <p>{pack.output.CSV_precedence}</p>
          <p>{pack.output.tiers}</p>
        </div>
        <div className={css.card}>
          <b>Aggregate is a separate field</b>
          <p>{pack.output.workflow}</p>
          <p>{pack.output.overall}</p>
          <p className={css.caution}>{pack.output.clinical_boundary}</p>
          <strong>No scores or ratings measured</strong>
        </div>
      </div>
    </div>
  );
}
export function AutomedPcamClsScene({ state }: { state: AutomedPcamClsState }) {
  return (
    <div className={css.scene} data-pcam-cls-scene={state.scene}>
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' ? (
        <Input key={state.beatId} state={state} />
      ) : state.scene === 'helper' ? (
        <Helper key={state.beatId} state={state} />
      ) : state.scene === 'operation' ? (
        <Operation key={state.beatId} state={state} />
      ) : state.scene === 'output' ? (
        <Output key={state.beatId} state={state} />
      ) : (
        <Limits key={state.beatId} state={state} />
      )}
    </div>
  );
}
export function AutomedPcamClsOutput({ state }: { state: AutomedPcamClsState }) {
  return (
    <aside className={`${shared.storyOutput} ${css.aside}`} data-pcam-cls-output>
      <span className={shared.storyEyebrow}>Required output · unsubmitted</span>
      <h3>One center label per Full tile</h3>
      <div className={css.fields}>
        <div>
          <code>patient_id</code>
          <span>unset</span>
        </div>
        <div>
          <code>label</code>
          <span>unset</span>
        </div>
      </div>
      <p>Private targets, checkpoint outputs and scores are absent.</p>
      <small>
        {state.scene === 'limits'
          ? 'Accuracy counts all supplied IDs, including missing predictions.'
          : 'Symbolic task workflow · no matched Full tile.'}
      </small>
    </aside>
  );
}

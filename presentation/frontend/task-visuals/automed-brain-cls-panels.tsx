import { useLayoutEffect, useRef, useState } from 'react';
import { automedBrainClsPack as pack, type AutomedBrainClsState } from './automed-brain-cls';
import {
  canonicalNamedClass,
  submissionFields,
  shouldResetControls,
} from './automed-brain-cls-controls';
import shared from './task-visual.module.css';
import css from './automed-brain-cls.module.css';
const titles = {
  input: 'Required MRI · source absent',
  helper: 'Choose a canonical taxonomy token',
  operation: 'Verify named mapping and method',
  output: 'Submission alternatives · formatter boundary',
  limits: 'Classification accuracy · grader boundaries',
} as const;
function useReset(frame: number, reset: () => void) {
  const previous = useRef(frame);
  useLayoutEffect(() => {
    if (shouldResetControls(previous.current, frame)) reset();
    previous.current = frame;
  }, [frame, reset]);
}
function Socket({ title }: { title: string }) {
  return (
    <div className={css.socket}>
      <b>{title}</b>
      <span>Absent · no image, case label or result synthesized</span>
    </div>
  );
}
function Input() {
  return (
    <div className={css.columns} data-brain-cls-input>
      <Socket title="Full case / image.jpg" />
      <div className={css.card}>
        <b>One source raster per case</b>
        <p>
          The harness declares dataset.included=false and no runtime assets. Native MRI and frozen
          Full IDs are absent.
        </p>
        <p>
          No sequence, orientation, physical geometry or tumor finding is inferred. patient_id is a
          schema identifier, not independent-patient provenance.
        </p>
      </div>
    </div>
  );
}
function Helper({ state }: { state: AutomedBrainClsState }) {
  const [selected, setSelected] = useState('');
  useReset(state.frame, () => setSelected(''));
  return (
    <div className={css.columns} data-brain-cls-helper>
      <div className={css.card}>
        <b>Four source tokens · public taxonomy</b>
        <div className={css.buttons} role="group" aria-label="Canonical brain classification token">
          {pack.helper.classes.map((c) => (
            <button
              key={c}
              type="button"
              aria-pressed={selected === c}
              onClick={() => setSelected(c)}
            >
              {c}
            </button>
          ))}
        </div>
        <p data-brain-cls-class-selection>
          {selected ? `Selected taxonomy token: ${selected}` : 'No taxonomy token selected'}
        </p>
        <p>{pack.helper.index_boundary}</p>
        <p>
          Selection is a public spelling exercise. It never populates label or establishes a case
          finding.
        </p>
      </div>
      <div className={css.card}>
        <b>Partition boundary</b>
        <p>{pack.helper.training_labels}</p>
        <p>
          Private label.json / ground_truth.csv is evaluator-only by declared path. No case label is
          retained; filesystem isolation is unaudited.
        </p>
      </div>
    </div>
  );
}
function Operation({ state }: { state: AutomedBrainClsState }) {
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  const [token, setToken] = useState('');
  useReset(state.frame, () => {
    setTier('lite');
    setToken('');
  });
  const canonical = canonicalNamedClass(token, pack.helper.classes);
  return (
    <div data-brain-cls-operation>
      <div className={css.buttons} role="group" aria-label="Brain classification assistance">
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
          <label htmlFor="brain-cls-named-token">Hypothetical named checkpoint token</label>
          <select
            id="brain-cls-named-token"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            aria-label="Hypothetical class token"
          >
            <option value="">Choose a named token</option>
            {pack.helper.classes.map((c) => (
              <option key={c} value={c.toUpperCase()}>
                {c.toUpperCase()}
              </option>
            ))}
          </select>
          <p data-brain-cls-map>
            {canonical ? `Canonical spelling: ${canonical}` : 'No named checkpoint token supplied'}
          </p>
          <p>
            Named mapping only. Config order is not a logit index map; actual checkpoint id2label
            and preprocessing remain absent.
          </p>
        </div>
      </div>
    </div>
  );
}
function Output({ state }: { state: AutomedBrainClsState }) {
  const [format, setFormat] = useState<'csv' | 'json'>('csv');
  const [detail, setDetail] = useState(false);
  useReset(state.frame, () => {
    setFormat('csv');
    setDetail(false);
  });
  return (
    <div data-brain-cls-output-schema>
      <div className={css.buttons} role="group" aria-label="Brain classification submission format">
        {(['csv', 'json'] as const).map((f) => (
          <button
            key={f}
            type="button"
            aria-pressed={format === f}
            onClick={() => {
              setFormat(f);
              setDetail(false);
            }}
          >
            {f}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-brain-cls-format>{pack.output.formats[format]}</b>
          <div className={css.fields}>
            {submissionFields(format).map((c) => (
              <div key={c}>
                <code>{c}</code>
                <span>unset</span>
              </div>
            ))}
          </div>
          <button
            type="button"
            className={css.reveal}
            aria-expanded={detail}
            aria-controls="brain-cls-formatter-rule"
            onClick={() => setDetail(!detail)}
          >
            {detail ? 'Hide formatter rules' : 'Inspect formatter rules'}
          </button>
          {detail && (
            <div id="brain-cls-formatter-rule" data-brain-cls-formatter>
              <p>{pack.output.format_boundary}</p>
              <p>{pack.output.CSV_precedence}</p>
              <p>Contract inspection only; no file is written or validated here.</p>
            </div>
          )}
        </div>
        <Socket title="Unsubmitted artifact" />
      </div>
    </div>
  );
}
function Limits({ state }: { state: AutomedBrainClsState }) {
  const [metric, setMetric] = useState<'accuracy' | 'balanced_accuracy'>('accuracy');
  const [detail, setDetail] = useState(false);
  useReset(state.frame, () => {
    setMetric('accuracy');
    setDetail(false);
  });
  return (
    <div data-brain-cls-limits>
      <div className={css.buttons} role="group" aria-label="Classification metric denominator">
        {(['accuracy', 'balanced_accuracy'] as const).map((m) => (
          <button
            key={m}
            type="button"
            aria-pressed={metric === m}
            onClick={() => {
              setMetric(m);
              setDetail(false);
            }}
          >
            {m.replaceAll('_', ' ')}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-brain-cls-metric>{pack.output[metric]}</b>
          <p>{pack.output.units}</p>
          <button
            type="button"
            className={css.reveal}
            aria-expanded={detail}
            aria-controls="brain-cls-grader-rules"
            onClick={() => setDetail(!detail)}
          >
            {detail ? 'Hide grader rules' : 'Inspect grader rules'}
          </button>
          {detail && (
            <div id="brain-cls-grader-rules" data-brain-cls-grader>
              <p>{pack.output.tiers}</p>
              <p>{pack.output.workflow}</p>
              <p>{pack.output.overall}</p>
            </div>
          )}
          <p>
            All declared test IDs stay in accuracy denominator, including missing predictions.
            Balanced recall averages only supported true classes.
          </p>
        </div>
        <div className={css.card}>
          <b>Dataset agreement has limits</b>
          <p className={css.caution}>{pack.output.clinical_boundary}</p>
          <p>
            No private targets, cohort coefficients or measured rating. Controls reset on scene exit
            or backward replay.
          </p>
          <strong>No model results or clinical validation</strong>
        </div>
      </div>
    </div>
  );
}
export function AutomedBrainClsScene({ state }: { state: AutomedBrainClsState }) {
  return (
    <div className={css.scene} data-brain-cls-scene={state.scene}>
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' ? (
        <Input />
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
export function AutomedBrainClsOutput({ state }: { state: AutomedBrainClsState }) {
  return (
    <aside className={`${shared.storyOutput} ${css.aside}`} data-brain-cls-output>
      <span className={shared.storyEyebrow}>Required output · unsubmitted</span>
      <h3>One label per Full case</h3>
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
      <p>Private targets, MRI, checkpoint output and scores are absent.</p>
      <small>
        {state.scene === 'limits'
          ? 'Accuracy counts all supplied IDs, including missing predictions.'
          : 'Symbolic workflow · no matching MRI.'}
      </small>
    </aside>
  );
}

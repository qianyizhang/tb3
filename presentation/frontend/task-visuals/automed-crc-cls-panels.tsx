import {
  canonicalNamedClass,
  submissionFields,
  shouldResetControls,
} from './automed-crc-cls-controls';
import { useLayoutEffect, useRef, useState } from 'react';
import { automedCrcClsPack as pack, type AutomedCrcClsState } from './automed-crc-cls';
import shared from './task-visual.module.css';
import css from './automed-crc-cls.module.css';
const titles = {
  input: 'Inspect official training patch',
  helper: 'Reveal training annotation',
  operation: 'Verify method and mapping',
  output: 'Inspect submission alternatives',
  limits: 'Separate scoring denominators',
} as const;
function useReset(state: AutomedCrcClsState, reset: () => void) {
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (shouldResetControls(previous.current, state.frame)) reset();
    previous.current = state.frame;
  }, [state.frame, reset]);
}
function Socket({ title }: { title: string }) {
  return (
    <div className={css.socket}>
      <b>{title}</b>
      <span>Absent · no image, label or output synthesized</span>
    </div>
  );
}
function Input() {
  return (
    <div className={css.columns} data-crc-cls-input>
      <figure className={css.image}>
        <img
          src={pack.imageUrl}
          alt="Official public CRC training patch, native RGB preview; source annotation covered until helper reveal"
        />
        <figcaption>224 x 224 RGB · 0.5 µm/pixel (source description)</figcaption>
      </figure>
      <div className={css.card}>
        <b>Upstream training patch, not a Full test case</b>
        <p>
          Macenko-normalized NCT-CRC-HE-100K source; decoded RGB preview adds no stain processing or
          resize.
        </p>
        <p>
          No Full ID or WSI coordinates retained. Patch labels do not establish patient diagnosis.
        </p>
        <p>
          NONORM archive regions can differ; it is not an exact before/after normalization pair.
        </p>
      </div>
    </div>
  );
}
function Helper({ state }: { state: AutomedCrcClsState }) {
  const [revealed, setRevealed] = useState(false);
  useReset(state, () => setRevealed(false));
  return (
    <div className={css.columns} data-crc-cls-helper>
      <div className={css.card}>
        <b>Nine source tissue categories</b>
        <div className={css.taxonomy}>
          {pack.helper.classes.map((c) => (
            <div key={c}>
              <code>
                {c.toUpperCase()} → {c}
              </code>
              <span>{pack.helper.class_descriptions[c]}</span>
            </div>
          ))}
        </div>
        <p>{pack.helper.index_boundary}</p>
      </div>
      <div className={css.card}>
        <b>Public training annotation · reader reveal</b>
        <button
          type="button"
          aria-expanded={revealed}
          aria-controls="crc-source-annotation"
          onClick={() => setRevealed(!revealed)}
        >
          {revealed ? 'Hide training annotation' : 'Reveal training annotation'}
        </button>
        {revealed ? (
          <div id="crc-source-annotation" data-crc-cls-training-revealed>
            <p>
              <code>{pack.helper.source_member}</code>
            </p>
            <p>
              Source folder ADI → <strong>{pack.helper.training_label}</strong> · adipose
            </p>
            <p>
              Public source annotation only; not Full truth, model output or independent diagnosis.
            </p>
          </div>
        ) : (
          <div className={css.socket} data-crc-cls-training-hidden>
            <b>Training annotation covered</b>
            <span>Reader-controlled helper; no private target</span>
          </div>
        )}
        <p>
          NCT-CRC-HE-100K train / CRC-VAL-HE-7K evaluation source. Frozen Full 100-case subset
          unresolved.
        </p>
      </div>
    </div>
  );
}
function Operation({ state }: { state: AutomedCrcClsState }) {
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  const [token, setToken] = useState('');
  useReset(state, () => {
    setTier('lite');
    setToken('');
  });
  return (
    <div data-crc-cls-operation>
      <div className={css.buttons} role="group" aria-label="CRC classification assistance">
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
              aria-label="Hypothetical tissue token"
            >
              <option value="">Select a source token</option>
              {pack.helper.classes.map((c) => (
                <option key={c} value={c}>
                  {c.toUpperCase()}
                </option>
              ))}
            </select>
          </label>
          <p data-crc-cls-map>
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
function Output({ state }: { state: AutomedCrcClsState }) {
  const [format, setFormat] = useState<'csv' | 'json'>('csv');
  useReset(state, () => setFormat('csv'));
  return (
    <div data-crc-cls-output-schema>
      <div className={css.buttons} role="group" aria-label="CRC classification submission format">
        {(['csv', 'json'] as const).map((f) => (
          <button key={f} type="button" aria-pressed={format === f} onClick={() => setFormat(f)}>
            {f}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-crc-cls-format>{pack.output.formats[format]}</b>
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
function Limits({ state }: { state: AutomedCrcClsState }) {
  const [metric, setMetric] = useState<'accuracy' | 'balanced_accuracy'>('accuracy');
  useReset(state, () => setMetric('accuracy'));
  return (
    <div data-crc-cls-limits>
      <div className={css.buttons} role="group" aria-label="Classification metric denominator">
        {(['accuracy', 'balanced_accuracy'] as const).map((m) => (
          <button key={m} type="button" aria-pressed={metric === m} onClick={() => setMetric(m)}>
            {m.replaceAll('_', ' ')}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-crc-cls-metric>{pack.output[metric]}</b>
          <p className={css.caution}>{pack.output.metric_discrepancy}</p>
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
export function AutomedCrcClsScene({ state }: { state: AutomedCrcClsState }) {
  return (
    <div className={css.scene} data-crc-cls-scene={state.scene}>
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
export function AutomedCrcClsOutput({ state }: { state: AutomedCrcClsState }) {
  return (
    <aside className={`${shared.storyOutput} ${css.aside}`} data-crc-cls-output>
      <span className={shared.storyEyebrow}>Required output · unsubmitted</span>
      <h3>One tissue label per Full case</h3>
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
          : 'Symbolic task workflow · no Full evaluation patch.'}
      </small>
    </aside>
  );
}

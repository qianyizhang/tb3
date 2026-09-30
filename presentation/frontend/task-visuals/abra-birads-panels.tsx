import { useState } from 'react';
import { abraBiradsPack as pack, type AbraBiradsState } from './abra-birads';
import shared from './task-visual.module.css';
import css from './abra-birads.module.css';

const titles = {
  input: 'Inspect series metadata',
  operation: 'Compare assistance conditions',
  output: 'Inspect report schema',
  reference: 'Reveal general target construction',
  limits: 'Inspect scorer limits',
} as const;
function EmptySocket({ label }: { label: string }) {
  return (
    <div className={css.socket}>
      <b>{label}</b>
      <span>Absent · no patient pixels or output synthesized</span>
    </div>
  );
}
function Input() {
  return (
    <div className={css.columns} data-birads-input>
      <div className={css.series} data-birads-series>
        <b>{pack.source.study.patient_id} · source-manifest rows</b>
        {pack.source.series.map((s) => (
          <div key={s.series_uid}>
            <span>{s.description || 'No description'}</span>
            <small>
              {s.modality} · {s.num_instances} instances
              {s.modality !== 'MR' ? ' · outside MR generator selection' : ''}
            </small>
          </div>
        ))}
        <p>{pack.source.ordering}.</p>
      </div>
      <div className={css.card}>
        <EmptySocket label="Matched breast MRI images" />
        <p>
          No pixel-derived lesion, laterality or enhancement claim follows from these series
          descriptions.
        </p>
        <p>
          The collection warns that dummy FrameOfReferenceUID values may be unreliable for
          alignment.
        </p>
      </div>
    </div>
  );
}
function Operation({ state }: { state: AbraBiradsState }) {
  const [override, setOverride] = useState<'visual' | 'oracle' | null>(null);
  const selected = override ?? (state.detail > 0.5 ? 'oracle' : 'visual');
  const condition = pack.operation.conditions.find((c) => c.id === selected)!;
  return (
    <div data-birads-operation data-birads-condition={selected}>
      <div className={css.buttons} role="group" aria-label="BI-RADS assistance condition">
        {pack.operation.conditions.map((c) => (
          <button
            key={c.id}
            type="button"
            aria-pressed={selected === c.id}
            onClick={() => setOverride(c.id)}
          >
            {c.label}
          </button>
        ))}
        <button type="button" onClick={() => setOverride(null)}>
          Follow story
        </button>
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b>{condition.label}</b>
          <p>
            Vision {condition.vision ? 'enabled' : 'disabled'} · {condition.max_turns} turns
          </p>
          <ol className={css.steps}>
            {condition.steps.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ol>
          <p>{condition.assistance}.</p>
        </div>
        <div className={css.card}>
          <EmptySocket
            label={selected === 'visual' ? 'Pre/post MRI comparison' : 'Prepared oracle response'}
          />
          <p>{condition.remaining}.</p>
          <p>
            {selected === 'visual'
              ? pack.operation.preprocessor
              : 'query_birads_model validates the requested series UID and returns the in-task overview. No learned CAD model runs in that source path.'}
          </p>
          <strong>No tool call occurs here</strong>
        </div>
      </div>
    </div>
  );
}
function Output() {
  return (
    <div className={css.columns} data-birads-output-schema>
      <div className={css.card}>
        <b>Required terminal report</b>
        <div className={css.fields}>
          {pack.output.fields.map((field) => (
            <div key={field}>
              <code>{field}</code>
              <span>unset</span>
            </div>
          ))}
        </div>
        <p>
          Optional quadrant: <code>{pack.output.optional_quadrant}</code>
        </p>
      </div>
      <div className={css.card}>
        <EmptySocket label="submit_birads_report arguments" />
        <p>No submitted report, actual oracle response or score is retained.</p>
        <p>
          Receipt by the terminal tool is distinct from reference agreement or clinical adequacy.
        </p>
      </div>
    </div>
  );
}
function Reference({ state }: { state: AbraBiradsState }) {
  const [override, setOverride] = useState<boolean | null>(null);
  const revealed = override ?? state.reference > 0.5;
  return (
    <div data-birads-derivation>
      <button
        type="button"
        className={css.reveal}
        aria-expanded={revealed}
        onClick={() => setOverride(!revealed)}
      >
        {revealed ? 'Hide construction rules' : 'Reveal construction rules'}
      </button>
      {!revealed ? (
        <div className={css.socket} data-birads-reference-hidden>
          <b>General code derivation covered</b>
          <span>No patient reference is available. Reveal source construction explicitly.</span>
        </div>
      ) : (
        <div data-birads-reference-revealed className={css.rules}>
          <p className={css.caution}>{pack.derivation.warning}</p>
          {Object.entries(pack.derivation.rules).map(([field, rule]) => (
            <div key={field} className={css.card}>
              <b>{field.replaceAll('_', ' ')}</b>
              <p>{rule}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
function Limits() {
  const [withQuadrant, setWithQuadrant] = useState(false);
  return (
    <div className={css.columns} data-birads-limits>
      <div className={css.card}>
        <b>Weights, not an observed score</b>
        <div className={css.fields}>
          {Object.entries(pack.output.weights).map(([field, weight]) => (
            <div key={field}>
              <span>{field.replaceAll('_', ' ')}</span>
              <strong>
                {weight.toFixed(2)}
                {field === 'lesion_quadrant' ? ' optional' : ''}
              </strong>
            </div>
          ))}
        </div>
        <label>
          <input
            type="checkbox"
            checked={withQuadrant}
            onChange={(e) => setWithQuadrant(e.target.checked)}
          />
          Illustrative reference includes quadrant
        </label>
        <p data-birads-denominator>
          Included weight denominator: <strong>{withQuadrant ? '1.00' : '0.90'}</strong>
        </p>
        <small>This selector shows a rule branch; it supplies no patient target.</small>
      </div>
      <div className={css.card}>
        <b>Agreement limits</b>
        <p>{pack.derivation.category_credit}</p>
        <p>{pack.derivation.count_credit}</p>
        <p>{pack.derivation.laterality_caveat}</p>
        <p>
          Morphology, size and recommendation are unscored. No independent diagnostic quality or
          measured result is established.
        </p>
        <strong>Report remains unsubmitted · no score</strong>
      </div>
    </div>
  );
}
export function AbraBiradsScene({ state }: { state: AbraBiradsState }) {
  return (
    <section className={css.scene} data-birads-scene={state.scene} data-birads-basis="mixed">
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' && <Input />}
      {state.scene === 'operation' && <Operation state={state} />}
      {state.scene === 'output' && <Output />}
      {state.scene === 'reference' && <Reference state={state} />}
      {state.scene === 'limits' && <Limits />}
    </section>
  );
}
export function AbraBiradsOutput({ state }: { state: AbraBiradsState }) {
  return (
    <aside className={`${shared.storyOutput} ${css.aside}`} data-birads-aside>
      <b>{state.scene === 'input' ? 'Source metadata boundary' : 'Report boundary'}</b>
      <p>
        {state.scene === 'input'
          ? 'Real series records; matched patient MRI absent.'
          : 'All patient fields unset; no report or score.'}
      </p>
      <small>Code-policy reveal is separate from a patient reference.</small>
    </aside>
  );
}

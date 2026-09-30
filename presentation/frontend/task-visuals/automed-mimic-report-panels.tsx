import { useLayoutEffect, useRef, useState } from 'react';
import {
  operationFrame,
  operationIndex,
  resetOnBackward,
  canonicalTier,
  canonicalMetric,
  automedMimicReportPack as pack,
  type AutomedMimicReportState,
} from './automed-mimic-report';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './automed-mimic-report.module.css';
const titles = {
  input: 'One or more views per study',
  helper: 'Public text-scoring schema',
  operation: 'Generate and submit every report',
  output: 'Inspect required text artifact',
  limits: 'Separate score and clinical claims',
} as const;
function useReset(state: AutomedMimicReportState, reset: () => void) {
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (resetOnBackward(previous.current, state.frame)) reset();
    previous.current = state.frame;
  }, [state.frame, reset]);
}
function Socket({ title }: { title: string }) {
  return (
    <div className={css.socket}>
      <b>{title}</b>
      <span>Absent · no patient image/report synthesized</span>
    </div>
  );
}
function Input() {
  return (
    <div className={css.columns} data-mimic-input>
      <Socket title="Required JPEG view sockets" />
      <div className={css.card}>
        <b>Study unit · patient join unknown</b>
        <p>{pack.source.partition}</p>
        <p>{pack.source.original_boundary}</p>
        <p>
          Use all views listed in the actual manifest. Grouping rule: first_three_underscore_fields.
          Unknown views/count and subject-study-image join; no independent-patient, geometry or
          temporal-order claim.
        </p>
      </div>
    </div>
  );
}
function Helper() {
  return (
    <div data-mimic-helper>
      <p className={css.caution}>{pack.helper.schema_boundary}</p>
      <div className={css.columns}>
        <div className={css.card}>
          <b>Twelve public scoring concepts</b>
          <div className={css.tags}>
            {pack.helper.classes.map((c) => (
              <code key={c}>{c}</code>
            ))}
          </div>
        </div>
        <div className={css.card}>
          <b>Language-rule boundary</b>
          <p>{pack.helper.rules}</p>
          <p>{pack.helper.training_labels}</p>
          <p>Private labels/report remain outside this illustration.</p>
        </div>
      </div>
    </div>
  );
}
function Operation({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedMimicReportState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  useReset(state, () => setTier('lite'));
  return (
    <div data-mimic-operation>
      <div className={css.buttons} role="group" aria-label="MIMIC method guidance">
        {(['lite', 'standard'] as const).map((t) => (
          <button
            type="button"
            key={t}
            aria-pressed={tier === t}
            onClick={() => {
              const v = canonicalTier(t);
              if (v) setTier(v);
            }}
          >
            {t}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b>{tier} guidance</b>
          <p data-mimic-tier>{pack.helper.tiers[tier]}</p>
          <div className={css.buttons} role="group" aria-label="Canonical MIMIC reporting stages">
            {pack.operation.steps.map((s, i) => (
              <button
                type="button"
                key={s}
                data-mimic-step={i}
                aria-pressed={operationIndex(state.progress) === i}
                onClick={() => onSeekFrame?.(operationFrame(plan, i))}
              >
                {i + 1}.{' '}
                {['Stage views', 'Select pipeline', 'Generate / validate', 'Submit all cases'][i]}
              </button>
            ))}
          </div>
          <p data-mimic-currentstage>{pack.operation.steps[operationIndex(state.progress)]}</p>
        </div>
        <Socket title="Generated report remains unset" />
      </div>
    </div>
  );
}
function Output({ state }: { state: AutomedMimicReportState }) {
  const [detail, setDetail] = useState(false);
  useReset(state, () => setDetail(false));
  return (
    <div data-mimic-output-schema>
      <div className={css.columns}>
        <div className={css.card}>
          <b>Required path</b>
          <code className={css.path}>{pack.output.path}</code>
          <div className={css.empty}>No report text</div>
          <button type="button" aria-expanded={detail} onClick={() => setDetail(!detail)}>
            Inspect format constraints
          </button>
          {detail && <p data-mimic-format>{pack.output.format}</p>}
          <p>{pack.output.completeness}</p>
        </div>
        <Socket title="Private reference report absent" />
      </div>
    </div>
  );
}
function Limits({ state }: { state: AutomedMimicReportState }) {
  const [metric, setMetric] = useState<'macro' | 'micro'>('macro');
  useReset(state, () => setMetric('macro'));
  return (
    <div data-mimic-limits>
      <div className={css.buttons} role="group" aria-label="Report metric aggregation">
        {(['macro', 'micro'] as const).map((m) => (
          <button
            type="button"
            key={m}
            aria-pressed={metric === m}
            onClick={() => {
              const v = canonicalMetric(m);
              if (v) setMetric(v);
            }}
          >
            {m}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-mimic-metric>{pack.output[metric]}</b>
          <p>{pack.output.selector}</p>
          <p>{pack.output.empty_positive}</p>
        </div>
        <div className={css.card}>
          <b>Aggregate and meaning</b>
          <p>{pack.output.workflow}</p>
          <p>{pack.output.overall}</p>
          <p className={css.caution}>{pack.output.boundary}</p>
          <strong>No scores, ratings or outcomes measured</strong>
        </div>
      </div>
    </div>
  );
}
export function AutomedMimicReportScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedMimicReportState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  return (
    <div className={css.scene} data-mimic-scene={state.scene}>
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' ? (
        <Input key={state.beatId} />
      ) : state.scene === 'helper' ? (
        <Helper key={state.beatId} />
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
export function AutomedMimicReportOutput({ state }: { state: AutomedMimicReportState }) {
  return (
    <aside className={`${shared.storyOutput} ${css.sidebar}`} data-mimic-output>
      <span className={shared.storyEyebrow}>Required output · unsubmitted</span>
      <h3>One report per study</h3>
      <code className={css.path}>agent_outputs/&lt;case_id&gt;/report.txt</code>
      <div className={css.empty}>Report text · unset</div>
      <p>
        Private references and measured scores absent. Text-proxy components and configured scores
        are fractions 0–1; no clinical accuracy is measured.
      </p>
      <small>
        {state.scene === 'limits'
          ? 'All discovered cases valid before aggregate credit.'
          : 'Symbolic findings contract · exact views absent.'}
      </small>
    </aside>
  );
}

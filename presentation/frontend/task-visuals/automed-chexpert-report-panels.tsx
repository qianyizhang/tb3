import { useState, useLayoutEffect, useRef } from 'react';
import type { StoryPlan } from '../contracts.generated';
import {
  operationIndex,
  operationFrame,
  shouldResetControls,
  reportSelector,
  stageQuestions,
} from './automed-chexpert-report-controls';
import {
  automedChexpertReportPack as pack,
  type AutomedChexpertReportState,
} from './automed-chexpert-report';
import shared from './task-visual.module.css';
import css from './automed-chexpert-report.module.css';
function useReset(state: AutomedChexpertReportState, reset: () => void) {
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (shouldResetControls(previous.current, state.frame)) reset();
    previous.current = state.frame;
  }, [state.frame, reset]);
}
const titles = {
  input: 'One frontal view per study',
  helper: 'Public text-scoring schema',
  operation: 'Generate and submit every report',
  output: 'Inspect required text artifact',
  limits: 'Separate score and clinical claims',
} as const;
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
    <div className={css.columns} data-chexpert-input>
      <Socket title="Required frontal JPEG" />
      <div className={css.card}>
        <b>Study unit · patient join unknown</b>
        <p>{pack.source.partition}</p>
        <p>{pack.source.original_boundary}</p>
        <p>
          One staged image per study does not establish independent patients. No orientation, scale
          or radiologic finding is inferred.
        </p>
      </div>
    </div>
  );
}
function Helper() {
  return (
    <div data-chexpert-helper>
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
  state: AutomedChexpertReportState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  useReset(state, () => setTier('lite'));
  const index = operationIndex(state.progress);
  return (
    <div data-chexpert-operation>
      <div className={css.buttons} role="group" aria-label="CheXpert method guidance">
        {(['lite', 'standard'] as const).map((t) => (
          <button type="button" key={t} aria-pressed={tier === t} onClick={() => setTier(t)}>
            {t}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b>{tier} guidance</b>
          <p data-chexpert-tier>{pack.helper.tiers[tier]}</p>
          {tier === 'standard' && (
            <p>
              Source candidates: CheXagent-2-3b, CheXagent-8b, MedVersa and MAIRA-2. Compare at
              least two; access and weights unverified.
            </p>
          )}
          <nav className={css.buttons} aria-label="CheXpert canonical operation steps">
            {pack.operation.steps.map((s, j) => (
              <button
                key={s}
                type="button"
                aria-pressed={index === j}
                aria-label={s}
                disabled={!onSeekFrame}
                onClick={() => onSeekFrame?.(operationFrame(plan, j))}
              >
                {j + 1}
              </button>
            ))}
          </nav>
          <p data-chexpert-stage-question>{stageQuestions[index]}</p>
          <ol className={css.steps} start={index + 1}>
            <li data-active>{pack.operation.steps[index]}</li>
          </ol>
        </div>
        <Socket title="Generated report remains unset" />
      </div>
    </div>
  );
}
function Output({ state }: { state: AutomedChexpertReportState }) {
  const [detail, setDetail] = useState(false);
  useReset(state, () => setDetail(false));
  return (
    <div data-chexpert-output-schema>
      <div className={css.columns}>
        <div className={css.card}>
          <b>Required path</b>
          <code className={css.path}>{pack.output.path}</code>
          <div className={css.empty}>No report text</div>
          <button
            type="button"
            aria-expanded={detail}
            aria-controls="chexpert-format-constraints"
            onClick={() => setDetail(!detail)}
          >
            Inspect format constraints
          </button>
          {detail && (
            <p id="chexpert-format-constraints" data-chexpert-format>
              {pack.output.format}
            </p>
          )}
          <p>{pack.output.completeness}</p>
        </div>
        <Socket title="Private reference report absent" />
      </div>
    </div>
  );
}
function Limits({ state }: { state: AutomedChexpertReportState }) {
  const [metric, setMetric] = useState<'macro' | 'micro'>('macro');
  const [section, setSection] = useState<'findings' | 'fallback'>('findings');
  useReset(state, () => {
    setMetric('macro');
    setSection('findings');
  });
  return (
    <div data-chexpert-limits>
      <div className={css.buttons} role="group" aria-label="Report metric aggregation">
        {(['macro', 'micro'] as const).map((m) => (
          <button type="button" key={m} aria-pressed={metric === m} onClick={() => setMetric(m)}>
            {m}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-chexpert-metric>{pack.output[metric]}</b>
          <div className={css.buttons} role="group" aria-label="Reference text selector mechanics">
            {(['findings', 'fallback'] as const).map((s) => (
              <button
                type="button"
                key={s}
                aria-pressed={section === s}
                onClick={() => setSection(s)}
              >
                {s === 'findings' ? 'Nonempty Findings' : 'Full-report fallback'}
              </button>
            ))}
          </div>
          <p data-chexpert-selector>{reportSelector(section)}</p>
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
export function AutomedChexpertReportScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedChexpertReportState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  return (
    <div className={css.scene} data-chexpert-scene={state.scene}>
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' ? (
        <Input />
      ) : state.scene === 'helper' ? (
        <Helper />
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
export function AutomedChexpertReportOutput({ state }: { state: AutomedChexpertReportState }) {
  return (
    <aside className={`${shared.storyOutput} ${css.aside}`} data-chexpert-output>
      <span className={shared.storyEyebrow}>Required output · unsubmitted</span>
      <h3>One report per study</h3>
      <code className={css.path}>agent_outputs/&lt;case_id&gt;/report.txt</code>
      <div className={css.empty}>Report text · unset</div>
      <p>Private references and measured scores absent.</p>
      <p>Text-proxy scores use fractions 0–1; no clinical accuracy is measured.</p>
      <small>
        {state.scene === 'limits'
          ? 'All discovered cases valid before aggregate credit.'
          : 'Symbolic contract · exact frontal JPEG absent.'}
      </small>
    </aside>
  );
}

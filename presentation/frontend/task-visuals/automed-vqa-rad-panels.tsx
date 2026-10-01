import { useLayoutEffect, useRef, useState } from 'react';
import {
  automedVqaRadPack as pack,
  type AutomedVqaRadState,
  operationSteps,
  operationIndex,
  operationFrame,
  publicAnnotationVisible,
} from './automed-vqa-rad';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './automed-vqa-rad.module.css';
const titles = {
  input: 'Native training pair · Full case absent',
  helper: 'Public annotation · deliberate reader reveal',
  operation: 'Preserve question, prompt and answer span',
  output: 'Empty six-field answer contract',
  limits: 'Question means · optional judge · validity gates',
} as const;
function Input() {
  return (
    <div className={css.columns} data-vqa-rad-input>
      <figure className={css.figure}>
        <img src={pack.image} alt="Native public VQA-RAD train row0 image; no diagnostic overlay" />
        <figcaption>566×555 / 23,661-byte viewer JPEG · train row0 · no Full join</figcaption>
      </figure>
      <div className={css.card}>
        <b>English public source question</b>
        <blockquote>{pack.source.question}</blockquote>
        <p>
          Public mirror row0 has no native question ID; exact Full ID absent. No source answer in
          this input view.
        </p>
        <p>{pack.source.geometry}</p>
        <strong className={css.caution}>{pack.source.question_unit}</strong>
      </div>
    </div>
  );
}
function Helper({ state }: { state: AutomedVqaRadState }) {
  const [revealed, setRevealed] = useState(false);
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (state.frame < previous.current) setRevealed(false);
    previous.current = state.frame;
  }, [state.frame]);
  return (
    <div className={css.columns} data-vqa-rad-helper>
      <div className={css.card}>
        <b>Educational public train annotation</b>
        <p>Source answer is initially hidden. This reveal establishes source annotation only.</p>
        <button
          type="button"
          aria-expanded={publicAnnotationVisible(state, revealed)}
          aria-controls="vqa-rad-public-annotation"
          onClick={() => setRevealed(!revealed)}
        >
          {revealed ? 'Hide public training annotation' : 'Reveal public training annotation'}
        </button>
        {publicAnnotationVisible(state, revealed) && (
          <div id="vqa-rad-public-annotation" className={css.reveal} data-vqa-rad-public-annotation>
            <strong>{pack.helper.public_answer}</strong>
            <p>{pack.helper.public_answer_role}</p>
          </div>
        )}
        <p>Reveal resets on scene exit or backward replay. Private Full gold is absent.</p>
      </div>
      <div className={css.card}>
        <b>Calibration is separate assistance</b>
        <p>{pack.helper.calibration}</p>
        <ul className={css.steps}>
          {pack.helper.tools.map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
function Operation({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedVqaRadState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  const [calibration, setCalibration] = useState(false);
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (state.frame < previous.current) {
      setTier('lite');
      setCalibration(false);
    }
    previous.current = state.frame;
  }, [state.frame]);
  return (
    <div data-vqa-rad-operation data-vqa-rad-currentstep={operationIndex(state)}>
      <nav className={css.buttons} aria-label="VQA-RAD canonical steps">
        {operationSteps.map((label, index) => (
          <button
            type="button"
            key={label}
            data-vqa-rad-step={index}
            aria-pressed={operationIndex(state) === index}
            disabled={!onSeekFrame}
            onClick={() => onSeekFrame?.(operationFrame(plan, index))}
          >
            {label}
          </button>
        ))}
      </nav>
      <div className={css.buttons} role="group" aria-label="VQA-RAD assistance">
        {(['lite', 'standard'] as const).map((t) => (
          <button type="button" key={t} aria-pressed={tier === t} onClick={() => setTier(t)}>
            {t}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b>{tier} instruction</b>
          <p data-vqa-rad-tier>{pack.helper.tiers[tier]}</p>
          <button
            type="button"
            aria-expanded={calibration}
            onClick={() => setCalibration(!calibration)}
          >
            Inspect calibration rule
          </button>
          {calibration && <p data-vqa-rad-calibration>{pack.helper.calibration}</p>}
          <ol className={css.steps}>
            {pack.operation.steps.map((s, i) => (
              <li key={s} data-active={operationIndex(state) === i}>
                {s}
              </li>
            ))}
          </ol>
        </div>
        <div className={css.card}>
          <b>Phrase / binary normalization</b>
          <p>{pack.operation.normalization}</p>
          <div className={css.tokens}>
            <span>Open phrase → normalized short span</span>
            <span>Binary question → exact yes / no</span>
            <span>No option tokens or A–E mapping</span>
          </div>
          <p>
            S4 warns against a five-word cap: some gold phrases have6–10 words. No schema word-count
            limit or actual decoded text shown.
          </p>
        </div>
      </div>
    </div>
  );
}
function Output({ state }: { state: AutomedVqaRadState }) {
  const [detail, setDetail] = useState(false);
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (state.frame < previous.current) setDetail(false);
    previous.current = state.frame;
  }, [state.frame]);
  return (
    <div className={css.columns} data-vqa-rad-output-schema>
      <div className={css.card}>
        <b>{pack.output.path}</b>
        <div className={css.fields}>
          {Object.entries(pack.output.fields).map(([key, type]) => (
            <div key={key}>
              <code>{key}</code>
              <span>{type}</span>
              <em>unset</em>
            </div>
          ))}
        </div>
        <button type="button" aria-expanded={detail} onClick={() => setDetail(!detail)}>
          Inspect format checks
        </button>
        {detail && <p data-vqa-rad-format>{pack.output.format}</p>}
      </div>
      <div className={css.card}>
        <b>No answer was generated</b>
        <p>{pack.output.checker_difference}</p>
        <p>Raw text, model identity and runtime require genuine execution evidence.</p>
        <strong className={css.caution}>
          Private reference, score and participant output absent
        </strong>
      </div>
    </div>
  );
}
function Limits({ state }: { state: AutomedVqaRadState }) {
  const [metric, setMetric] = useState<'accuracy' | 'judge' | 'format_gate'>('accuracy');
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (state.frame < previous.current) setMetric('accuracy');
    previous.current = state.frame;
  }, [state.frame]);
  return (
    <div data-vqa-rad-limits>
      <div className={css.buttons} role="group" aria-label="VQA-RAD scoring boundary">
        {(['accuracy', 'judge', 'format_gate'] as const).map((m) => (
          <button type="button" key={m} aria-pressed={metric === m} onClick={() => setMetric(m)}>
            {m.replaceAll('_', ' ')}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-vqa-rad-metric>{pack.output[metric]}</b>
          <p>{pack.output.completion}</p>
          <p>{pack.output.rating_rule}</p>
        </div>
        <div className={css.card}>
          <b>Evidence and denominator boundaries</b>
          <p>{pack.output.workflow}</p>
          <p>{pack.output.limits}</p>
          <strong className={css.caution}>
            No measured accuracy, judge verdict or clinical result
          </strong>
        </div>
      </div>
    </div>
  );
}
export function AutomedVqaRadScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedVqaRadState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  return (
    <div className={css.scene} data-vqa-rad-scene={state.scene}>
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' ? (
        <Input />
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
export function AutomedVqaRadOutput({ state }: { state: AutomedVqaRadState }) {
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-vqa-rad-output>
      <span className={shared.storyEyebrow}>Answer record · unsubmitted</span>
      <h3>One short answer per question</h3>
      <div className={css.sidebarFields}>
        {Object.keys(pack.output.fields).map((key) => (
          <div key={key}>
            <code>{key}</code>
            <span>unset</span>
          </div>
        ))}
      </div>
      <p>
        Open mode: label ignored. Public training annotation is a reader reveal; private gold and
        model output absent.
      </p>
      <small>
        {state.scene === 'limits'
          ? 'Main denominator: all question IDs.'
          : 'Native public train input · Full mapping absent.'}
      </small>
    </aside>
  );
}

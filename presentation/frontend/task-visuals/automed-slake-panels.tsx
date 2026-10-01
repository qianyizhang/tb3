import { useLayoutEffect, useRef, useState } from 'react';
import { automedSlakePack as pack, type AutomedSlakeState } from './automed-slake';
import type { StoryPlan } from '../contracts.generated';
import { operationIndex, operationFrame, readerVisible, resetOnBackward } from './automed-slake';
import css from './automed-slake.module.css';
const titles = {
  input: 'Native training pair · Full case absent',
  helper: 'Public annotation · deliberate reader reveal',
  operation: 'Preserve question, prompt and answer span',
  output: 'Empty six-field answer contract',
  limits: 'Question means · optional judge · validity gates',
} as const;
function Input() {
  return (
    <div className={css.columns} data-slake-input>
      <figure className={css.figure}>
        <img
          data-slake-native
          src={pack.image}
          alt="Native public SLAKE train qid0 image; no diagnostic overlay"
        />
        <figcaption>256×256 native JPEG · train qid0 · not a Full case</figcaption>
      </figure>
      <div className={css.card}>
        <b>English public source question</b>
        <blockquote>{pack.source.question}</blockquote>
        <p>
          Source xmlab1/source.jpg, img_id1; exact Full question ID absent. No source answer in this
          input view.
        </p>
        <p>{pack.source.geometry}</p>
        <strong className={css.caution}>{pack.source.question_unit}</strong>
      </div>
    </div>
  );
}
function Helper({ state }: { state: AutomedSlakeState }) {
  const [revealed, setRevealed] = useState(false);
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (resetOnBackward(previous.current, state.frame)) setRevealed(false);
    previous.current = state.frame;
  }, [state.frame]);
  return (
    <div className={css.columns} data-slake-helper>
      <div className={css.card}>
        <b>Educational public train annotation</b>
        <p>Source answer is initially hidden. This reveal establishes source annotation only.</p>
        <button
          type="button"
          aria-expanded={revealed}
          aria-controls="slake-public-annotation"
          disabled={state.reference <= 0}
          onClick={() => setRevealed(!revealed)}
        >
          {revealed ? 'Hide public training annotation' : 'Reveal public training annotation'}
        </button>
        {readerVisible(state, revealed) && (
          <div id="slake-public-annotation" className={css.reveal} data-slake-public-annotation>
            <strong>{pack.reference.public_answer}</strong>
            <p>{pack.reference.public_answer_role}</p>
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
  state: AutomedSlakeState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const current = operationIndex(state);
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (resetOnBackward(previous.current, state.frame)) setTier('lite');
    previous.current = state.frame;
  }, [state.frame]);
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  return (
    <div data-slake-operation>
      <div className={css.buttons} role="group" aria-label="SLAKE assistance">
        {(['lite', 'standard'] as const).map((t) => (
          <button type="button" key={t} aria-pressed={tier === t} onClick={() => setTier(t)}>
            {t}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b>{tier} instruction</b>
          <p data-slake-tier>{pack.helper.tiers[tier]}</p>
          <nav className={css.buttons} aria-label="SLAKE canonical steps">
            {pack.operation.steps.map((s, i) => (
              <button
                key={s}
                type="button"
                data-slake-operation-step={i}
                aria-pressed={current === i}
                disabled={!onSeekFrame}
                onClick={() => onSeekFrame?.(operationFrame(plan, i))}
              >
                {['Bind input', 'Prompt/raw text', 'Normalize span', 'Write record'][i]}
              </button>
            ))}
          </nav>
          <p data-slake-currentstage={current}>{pack.operation.steps[current]}</p>
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
            S4 warns against a five-word cap: some gold phrases have 6–10 words. No schema
            word-count limit or actual decoded text shown.
          </p>
        </div>
      </div>
    </div>
  );
}
function Output({ state }: { state: AutomedSlakeState }) {
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (resetOnBackward(previous.current, state.frame)) setDetail(false);
    previous.current = state.frame;
  }, [state.frame]);
  const [detail, setDetail] = useState(false);
  return (
    <div className={css.columns} data-slake-output-schema>
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
        {detail && <p data-slake-format>{pack.output.format}</p>}
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
function Limits({ state }: { state: AutomedSlakeState }) {
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (resetOnBackward(previous.current, state.frame)) setMetric('accuracy');
    previous.current = state.frame;
  }, [state.frame]);
  const [metric, setMetric] = useState<'accuracy' | 'judge' | 'format_gate'>('accuracy');
  return (
    <div data-slake-limits>
      <div className={css.buttons} role="group" aria-label="SLAKE scoring boundary">
        {(['accuracy', 'judge', 'format_gate'] as const).map((m) => (
          <button type="button" key={m} aria-pressed={metric === m} onClick={() => setMetric(m)}>
            {m.replaceAll('_', ' ')}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-slake-metric>{pack.output[metric]}</b>
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
export function AutomedSlakeScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedSlakeState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  return (
    <div className={css.scene} data-slake-scene={state.scene}>
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
export function AutomedSlakeOutput({ state }: { state: AutomedSlakeState }) {
  return (
    <aside className={css.output} data-slake-output>
      <span className={css.eyebrow}>Answer record · unsubmitted</span>
      <h3>One record per question</h3>
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
          ? 'Main denominator: evaluator-supplied IDs; default discovered split IDs.'
          : 'Native public train input · Full mapping absent.'}
      </small>
    </aside>
  );
}

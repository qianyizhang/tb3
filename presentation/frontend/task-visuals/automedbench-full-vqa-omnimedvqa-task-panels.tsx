import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  resetOnBackward,
  type AutomedOmniState,
} from './automedbench-full-vqa-omnimedvqa-task';
import type { StoryPlan } from '../contracts.generated';
import css from './automedbench-full-vqa-omnimedvqa-task.module.css';
export function AutomedOmniScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedOmniState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [show, setShow] = useState(false);
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  const [format, setFormat] = useState(false);
  const previous = useRef({ frame: state.frame, beat: state.beatId });
  useLayoutEffect(() => {
    if (
      previous.current.beat !== state.beatId ||
      resetOnBackward(previous.current.frame, state.frame)
    ) {
      setShow(false);
      setTier('lite');
      setFormat(false);
    }
    previous.current = { frame: state.frame, beat: state.beatId };
  }, [state.frame, state.beatId]);
  const i = operationIndex(state),
    m = branchIndex(state);
  const options = [
    source.source_question.option_A,
    source.source_question.option_B,
    source.source_question.option_C,
    source.source_question.option_D,
  ];
  return (
    <section className={css.scene} data-omni-scene={state.scene}>
      {state.scene === 'input' && (
        <>
          <h3>Source README QA; matching image missing</h3>
          <div className={css.two}>
            <div className={css.socket}>
              <b>Referenced CT image unavailable</b>
              <p>{source.source_question.image_path}</p>
              <small>
                Empty socket, no recovered patient pixels. Modality is source-declared;
                geometry/window unknown.
              </small>
            </div>
            <div>
              <b>{source.source_question.question}</b>
              <ul className={css.options}>
                {options.map((o, j) => (
                  <li key={o}>
                    <b>{'ABCD'[j]}</b> {o}
                  </li>
                ))}
              </ul>
              <small>
                Source item {source.source_question.question_id}; not verified Full ID. Answer
                covered.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Four options; inspect task/parser/schema boundary</h3>
          <nav className={css.controls} aria-label="OmniMedVQA contract steps">
            {steps.map((s, j) => (
              <button
                key={s}
                type="button"
                data-omni-operation-step={j}
                aria-pressed={i === j}
                disabled={!onSeekFrame}
                onClick={() => onSeekFrame?.(operationFrame(plan, j, m))}
              >
                {s}
              </button>
            ))}
          </nav>
          <div className={css.socket}>
            {i === 0 ? (
              <>
                <b>Authorized image + question + exact A–D options</b>
                <nav className={css.controls} aria-label="OmniMedVQA assistance">
                  {(['lite', 'standard'] as const).map((t) => (
                    <button
                      type="button"
                      key={t}
                      aria-pressed={tier === t}
                      onClick={() => setTier(t)}
                    >
                      {t}
                    </button>
                  ))}
                </nav>
                <p data-omni-tier>
                  {tier === 'lite'
                    ? 'Fixed LLaVA-Med 7B, llava_med_conv; actual loader/model/runtime absent.'
                    : 'Compare all six pinned model_info candidates for modality/access/memory/reproducibility; no observed comparison.'}
                </p>
                <p>
                  Real decode absent. Modalities differ by source; original source terms apply. Task
                  1–10 smoke without private gold, no completed calibration.
                </p>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Explore OmniMedVQA parser controls">
                  {branches.map((s, j) => (
                    <button
                      key={s}
                      type="button"
                      aria-pressed={m === j}
                      disabled={!onSeekFrame}
                      onClick={() => onSeekFrame?.(operationFrame(plan, 1, j))}
                    >
                      {s}
                    </button>
                  ))}
                </nav>
                <b>
                  Authored control: “{fixture.raw_examples[m]}” →{' '}
                  {fixture.parsed_examples[m] ?? 'reject'}
                </b>
                {m === 0 ? (
                  <p>
                    Standalone A → copy exact options[A]. This is a parser control, never a real
                    decode or solved medical question.
                  </p>
                ) : m === 1 ? (
                  <p>
                    E is outside task A–D; per-options extraction rejects. Generic schema/scorer A–E
                    can accept E: enforce per-question allowed set separately.
                  </p>
                ) : (
                  <p>
                    Parser miss → reject; do not guess or fill a fallback. Label normalization/prose
                    matching alone does not satisfy task parser policy.
                  </p>
                )}
              </>
            ) : (
              <>
                <b>&lt;question_id&gt;/answer.json · 6 required fields</b>
                <button type="button" aria-expanded={format} onClick={() => setFormat(!format)}>
                  Inspect task versus generic checks
                </button>
                {format && (
                  <p data-omni-format>
                    Task A–D and exact option text differ from generic A–E with conditional
                    nonempty-text comparison. Private gold is exact, unnormalized; no score
                    computed.
                  </p>
                )}
                <p>
                  Exact ID, task A–D, exact option text, real raw decode/model/runtime. Generic
                  checker permits empty answer and E; scorer can accept incomplete letter record.
                  Actual output stays empty.
                </p>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Participant answer empty</h3>
          <code data-omni-output-schema>&lt;question_id&gt;/answer.json</code>
          <pre>
            {
              'question_id / predicted_label / predicted_answer\nraw_model_output / model_name / runtime_s'
            }
          </pre>
          <p>No authored control or public source answer copied into participant output.</p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Public README annotation; no private gold</h3>
          <button
            type="button"
            aria-expanded={show}
            disabled={state.reference <= 0}
            onClick={() => setShow(!show)}
          >
            Reveal public README annotation
          </button>
          {referenceVisible(state, show) ? (
            <div className={css.socket} data-omni-reference-revealed>
              <b>
                Source answer: {reference.answer} ·option {reference.label}
              </b>
              <p>{reference.role}</p>
              <p>
                MCQ accuracy uses correct labels/all evaluator-supplied IDs (default discovered
                split IDs), including missing/invalid. No open-ended token-F1 or judge promotion.
              </p>
            </div>
          ) : (
            <p data-omni-reference-hidden>
              Public README answer covered until explicit reader reveal.
            </p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Per-source authorization and Full boundary unresolved</h3>
          <p>{source.actual_data_gap}</p>
          <div className={css.socket}>
            <b>Image missing; no independent clinical inference</b>
            <p>
              Card QA/coverage is not a recovered Full test set. Private label mapping, source split
              isolation and actual staging unverified.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
export function AutomedOmniOutput({ state }: { state: AutomedOmniState }) {
  return (
    <aside data-omni-output={state.scene} className={css.output}>
      <b>Four-option question + missing image</b>
      <p>1 public README QA; 0 matching images/Full cases.</p>
      <p>Actual answer empty. A–D task rule differs from generic A–E checks.</p>
      <small>
        Public README annotation requires an explicit later reader reveal; private gold remains
        absent.
      </small>
    </aside>
  );
}

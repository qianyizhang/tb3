import { useLayoutEffect, useRef, useState } from 'react';
import native from '../../task-explorer/automedbench-full-medxpertqa-mm-task/source-preview.jpeg';
import {
  source,
  reference,
  steps,
  letters,
  operationIndex,
  optionIndex,
  operationFrame,
  referenceVisible,
  resetOnBackward,
  type AutomedMedxpertState,
} from './automedbench-full-medxpertqa-mm-task';
import type { StoryPlan } from '../contracts.generated';
import css from './automedbench-full-medxpertqa-mm-task.module.css';
export function AutomedMedxpertScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedMedxpertState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const i = operationIndex(state),
    o = optionIndex(state),
    letter = letters[o];
  const [show, setShow] = useState(false);
  const [questionOpen, setQuestionOpen] = useState(false);
  const [format, setFormat] = useState(false);
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  const previous = useRef({ frame: state.frame, beat: state.beatId });
  useLayoutEffect(() => {
    if (
      previous.current.beat !== state.beatId ||
      resetOnBackward(previous.current.frame, state.frame)
    ) {
      setShow(false);
      setQuestionOpen(false);
      setFormat(false);
      setTier('lite');
    }
    previous.current = { frame: state.frame, beat: state.beatId };
  }, [state.frame, state.beatId]);
  return (
    <section className={css.scene} data-medxpert-scene={state.scene}>
      {state.scene === 'input' && (
        <>
          <h3>Public dev MM-2000; Full membership unverified</h3>
          <div className={css.two}>
            <figure>
              <img
                className={css.native}
                data-medxpert-native
                src={native}
                alt="Unchanged question-linked public dev source radiograph; no authored clinical overlay"
              />
              <figcaption>
                1 linked JPEG · 945×999 · 96,627 unchanged bytes. Original source markers retained;
                no interpretation overlay.
              </figcaption>
            </figure>
            <div>
              <b>One question + one image + A–E options</b>
              <p>
                Source asks the next imaging study in its stated scenario. No Full selected case,
                private gold or model answer.
              </p>
              <details
                open={questionOpen}
                onToggle={(event) => setQuestionOpen(event.currentTarget.open)}
              >
                <summary>Read public source question</summary>
                {questionOpen && <pre>{source.source_question.question}</pre>}
              </details>
              <small>Question/options are given inputs; correct source label stays covered.</small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Inspect binding, option association and schema</h3>
          <nav className={css.controls} aria-label="MedXpert contract steps">
            {steps.map((s, j) => (
              <button
                key={s}
                type="button"
                data-medxpert-operation-step={j}
                aria-pressed={i === j}
                disabled={!onSeekFrame}
                onClick={() => onSeekFrame?.(operationFrame(plan, j, o))}
              >
                {s}
              </button>
            ))}
          </nav>
          <div className={css.socket} data-medxpert-currentstage={i}>
            {i === 0 ? (
              <>
                <b>Upstream id/images ≠ proven Full question_id/image_paths</b>
                <nav className={css.controls} aria-label="MedXpert assistance">
                  {(['lite', 'standard'] as const).map((t) => (
                    <button
                      key={t}
                      type="button"
                      aria-pressed={tier === t}
                      onClick={() => setTier(t)}
                    >
                      {t}
                    </button>
                  ))}
                </nav>
                <p data-medxpert-tier>
                  {tier === 'lite'
                    ? 'Fixed LLaVA-Med 7B, mistral_instruct; no model swap. S3 first-image helper, general multi-image handling unverified.'
                    : 'Compare all five source-named candidates; gated/model availability and one-GPU runtime unverified.'}
                </p>
                <small>
                  Smoke 1–10; S3 15 public-gold samples, generic verifier ≥10 with optional gold. No
                  private tuning or actual calibration.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Explore source option text">
                  {letters.map((l, j) => (
                    <button
                      key={l}
                      type="button"
                      data-medxpert-option={l}
                      aria-pressed={o === j}
                      disabled={!onSeekFrame}
                      onClick={() => onSeekFrame?.(operationFrame(plan, 1, j))}
                    >
                      {l}
                    </button>
                  ))}
                </nav>
                <b>
                  {letter} → {source.source_question.options[letter]}
                </b>
                <p>
                  Reader association only. No inferred answer, model decode or patient
                  recommendation.
                </p>
              </>
            ) : (
              <>
                <b>Scorer letter-valid differs from full schema-valid</b>
                <button type="button" aria-expanded={format} onClick={() => setFormat(!format)}>
                  Inspect format/scorer boundary
                </button>
                {format ? (
                  <p data-medxpert-format>
                    Six keys, exact ID, option text when nonempty, raw/model strings, nonnegative
                    runtime. Empty-answer conditional gap remains; wrong text can fail format while
                    letter scores correctly.
                  </p>
                ) : (
                  <p>
                    Normalized predicted letter is compared to exact, unnormalized gold;
                    missing/placeholder stays wrong in all-supplied-ID denominator.
                  </p>
                )}
                <small>
                  All files for output_format_valid; ≥50% for submission_format_valid. No score
                  computed.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Participant output always empty</h3>
          <code data-medxpert-output-schema>&lt;question_id&gt;/answer.json</code>
          <div className={css.socket}>
            <p>
              question_id · predicted_label · predicted_answer
              <br />
              raw_model_output · model_name · runtime_s
            </p>
            <small>
              Six expected keys; actual values remain null. No source correct label is copied into
              an output record.
            </small>
          </div>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later reader-only public dev annotation</h3>
          <button type="button" aria-expanded={show} onClick={() => setShow(!show)}>
            Reveal public source label
          </button>
          {referenceVisible(state, show) ? (
            <div className={css.socket} data-medxpert-reference-revealed>
              <b>
                Source annotation: {reference.label} · {reference.option_text}
              </b>
              <p>{reference.role}</p>
              <small>
                Not private Full gold, model result, clinical recommendation or adjudicated finding.
                Backward seek, scene exit and reset cover it before paint.
              </small>
            </div>
          ) : (
            <p data-medxpert-reference-hidden>
              Public label covered until explicit reader reveal. Private gold stays absent.
            </p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Native source example is not performance evidence</h3>
          <p>{source.actual_data_gap}</p>
          <div className={css.socket}>
            <b>Recover Full membership and isolation</b>
            <p>
              Upstream dev ID and JPEG do not establish Full staging conversion, split overlap or
              calibration eligibility. No runtime/model/scorer execution.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
export function AutomedMedxpertOutput({ state }: { state: AutomedMedxpertState }) {
  return (
    <aside className={css.output} data-medxpert-output>
      <b>One question; bind its required images</b>
      <p>Public dev source only. Full selection/private gold absent.</p>
      <p>Participant label/answer always empty; option selection is teaching only.</p>
      <small>Current scene: {state.scene}. Actual model result and score: absent.</small>
    </aside>
  );
}

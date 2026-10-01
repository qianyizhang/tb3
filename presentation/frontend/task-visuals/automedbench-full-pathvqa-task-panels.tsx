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
  type AutomedPathvqaState,
} from './automedbench-full-pathvqa-task';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './automedbench-full-pathvqa-task.module.css';
export function AutomedPathvqaScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedPathvqaState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [revealed, setRevealed] = useState(false);
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  const [calibration, setCalibration] = useState(false);
  const [format, setFormat] = useState(false);
  const previous = useRef({ frame: state.frame, beat: state.beatId });
  useLayoutEffect(() => {
    if (
      previous.current.beat !== state.beatId ||
      resetOnBackward(previous.current.frame, state.frame)
    ) {
      setRevealed(false);
      setTier('lite');
      setCalibration(false);
      setFormat(false);
    }
    previous.current = { frame: state.frame, beat: state.beatId };
  }, [state.frame, state.beatId]);
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-pathvqa-scene={state.scene}
      data-pathvqa-currentstep={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>PathVQA public train row0; Full case unverified</h3>
          <div className={css.two}>
            <figure>
              <img
                className={css.native}
                src={source.preview_data_uri}
                alt="Unchanged public PathVQA source image with embedded source arrows; no new overlay"
              />
              <figcaption>
                309×272 native JPEG ·49,231bytes. Embedded arrows/letter marks belong to source; not
                our findings.
              </figcaption>
            </figure>
            <div>
              <b>{source.source_question.question}</b>
              <p>
                Source training question +image. Answer remains covered; no A–E option set or
                recovered Full question_id.
              </p>
              <small>
                Specimen, magnification and independent clinical interpretation unverified.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Open-ended answer; inspect actual scorer branches</h3>
          <nav className={css.controls} aria-label="PathVQA contract steps">
            {steps.map((s, j) => (
              <button
                key={s}
                type="button"
                data-pathvqa-step={j}
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
                <b>Question + image → raw decode → short-answer text</b>
                <div className={css.controls}>
                  {(['lite', 'standard'] as const).map((t) => (
                    <button key={t} aria-pressed={tier === t} onClick={() => setTier(t)}>
                      {t}
                    </button>
                  ))}
                </div>
                <p data-pathvqa-tier>
                  {tier === 'lite'
                    ? 'Fixed LLaVA-Med starting model and conversation helper. No weights or inference acquired.'
                    : 'S1: exactly six candidates, including LLaVA-Med. model_info lists five and says MCQ; config/S1 are open-ended. No current availability or performance verified.'}
                </p>
                <button
                  aria-expanded={calibration}
                  aria-controls="pathvqa-calibration-rule"
                  onClick={() => setCalibration(!calibration)}
                >
                  Inspect public calibration rule
                </button>
                {calibration && (
                  <p id="pathvqa-calibration-rule">
                    Task S3: first 15 public rows, drop missing gold, top up to ≥15 (example does
                    not implement top-up). Generic verifier: ≥10, gold optional; config smoke 1–10
                    is separate. Mapper collapses yes/no prefixes or first clause, without an
                    enforced eight-word cap. No private answer supplied.
                  </p>
                )}
                <p>
                  Actual decode absent. Lite helper selects the first image; actual Full image
                  assembly and calibration eligibility remain unresolved.
                </p>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Explore PathVQA scoring branches">
                  {branches.map((s, j) => (
                    <button
                      key={s}
                      type="button"
                      data-pathvqa-branch={j}
                      aria-pressed={m === j}
                      disabled={!onSeekFrame}
                      onClick={() => onSeekFrame?.(operationFrame(plan, 1, j))}
                    >
                      {s}
                    </button>
                  ))}
                </nav>
                {m === 0 ? (
                  <>
                    <b>Nonbinary: .5 exact match + .5 token F1</b>
                    <p>
                      Toy only: reference “red blue”, prediction “red” → EM0, F1⅔, score⅓. Normalize
                      “{fixture.normalization.raw}” → “{fixture.normalization.normalized}”. Articles
                      remain; no semantic adjudication.
                    </p>
                  </>
                ) : m === 1 ? (
                  <>
                    <b>Binary gold uses strict normalized equality</b>
                    <p>
                      Toy “yes because red” vs “yes” →0; “true” →“yes” matches. Prefix-collapsing
                      postprocess is a separate pipeline step, not scorer behavior.
                    </p>
                  </>
                ) : (
                  <>
                    <b>Enabled answer judge becomes primary</b>
                    <p>
                      Judge-score sum/allIDs replaces lexical primary; heuristic diagnostic
                      retained. Cache, judge backend and heuristic-fallback count must remain
                      visible. No judge/model run here.
                    </p>
                  </>
                )}
              </>
            ) : (
              <>
                <b>&lt;question_id&gt;/answer.json ·6 required fields</b>
                <p>
                  Nonempty answer, exact ID, raw/model strings, runtime≥0. predicted_label remains
                  required but unused for open-ended scoring. Scorer accepts less than full schema;
                  ≥50% valid graded submission separate.
                </p>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Participant answer empty</h3>
          <code>&lt;question_id&gt;/answer.json</code>
          <pre>
            {
              'question_id / predicted_label / predicted_answer\nraw_model_output / model_name / runtime_s'
            }
          </pre>
          <p>All actual fields null; no source train answer copied into a participant artifact.</p>
          <button
            aria-expanded={format}
            aria-controls="pathvqa-format-rule"
            onClick={() => setFormat(!format)}
          >
            Inspect format boundary
          </button>
          {format && (
            <p id="pathvqa-format-rule">
              Six required keys, extra keys accepted; nonempty answer string and model name, numeric
              runtime≥0. No finite-runtime/bool exclusion guard. Scorer-valid text can fail strict
              schema; ≥50% strict-valid graded gate differs from every-file output_format_valid.
              Missing files remain in all-ID denominator.
            </p>
          )}
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Public training annotation; no private gold</h3>
          <button
            aria-expanded={referenceVisible(state, revealed)}
            aria-controls="pathvqa-public-reference"
            disabled={state.reference <= 0.5}
            onClick={() => setRevealed(!revealed)}
          >
            Reveal public train annotation
          </button>
          {referenceVisible(state, revealed) ? (
            <div
              className={css.socket}
              id="pathvqa-public-reference"
              data-pathvqa-reference-revealed
            >
              <b>Source training answer: {reference.answer}</b>
              <p>{reference.role}</p>
              <p>
                Not model evidence, recovered Full answer or independent clinical finding. AllIDs
                includes missing/invalid answers; binary-subset denominator differs.
              </p>
            </div>
          ) : (
            <p data-pathvqa-reference-hidden>
              Public source answer covered until explicit reader reveal.
            </p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Heldout split and actual pipeline absent</h3>
          <p>{source.actual_data_gap}</p>
          <div className={css.socket}>
            <b>Source train answer cannot establish test performance</b>
            <p>
              Leakage/calibration isolation, original rights and judge reliability unresolved. No
              localization, pathology diagnosis or generated result.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
export function AutomedPathvqaOutput({ state }: { state: AutomedPathvqaState }) {
  return (
    <aside data-pathvqa-output={state.scene} className={`${shared.storyOutput} ${css.output}`}>
      <b>Image +open-ended question</b>
      <p>1 public train example; Full split/private answer absent.</p>
      <p>Actual answer empty. Lexical, binary and judge branches remain distinct.</p>
      <small>
        Public train annotation is reader-controlled in its dedicated scene; backward/exit reset
        covers it. Private Full gold remains absent.
      </small>
    </aside>
  );
}

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
  type AutomedKvasirState,
} from './automedbench-full-vqa-kvasir-task';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './automedbench-full-vqa-kvasir-task.module.css';
export function AutomedKvasirScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedKvasirState;
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
      data-kvasir-scene={state.scene}
      data-kvasir-currentstep={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Kvasir-VQA public raw row0; Full case unverified</h3>
          <div className={css.two}>
            <figure>
              <img
                className={css.native}
                src={source.preview_data_uri}
                alt="Unchanged public Kvasir-VQA source image with border and embedded acquisition text; no new overlay"
              />
              <figcaption>
                720×576 native JPEG · 35,381 bytes. Source border and embedded acquisition text
                remain unchanged; no new overlay or finding.
              </figcaption>
            </figure>
            <div>
              <b>{source.source_question.question}</b>
              <p>
                Source raw question + image. Answer remains covered; no A–E option set or recovered
                Full question_id.
              </p>
              <small>
                Full membership, frame/patient linkage and clinical adjudication unverified.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Open-ended answer; inspect actual scorer branches</h3>
          <nav className={css.controls} aria-label="Kvasir-VQA contract steps">
            {steps.map((s, j) => (
              <button
                key={s}
                type="button"
                data-kvasir-step={j}
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
                <p data-kvasir-tier>
                  {tier === 'lite'
                    ? 'Fixed LLaVA-Med starting model and conversation helper. No weights or inference acquired.'
                    : 'Standard S1 compares all six model_info candidates, including LLaVA-Med, for endoscopy-image and free-text handling. Availability and performance unverified.'}
                </p>
                <button
                  aria-expanded={calibration}
                  aria-controls="kvasir-calibration-rule"
                  onClick={() => setCalibration(!calibration)}
                >
                  Inspect staged validation rule
                </button>
                {calibration && (
                  <p id="kvasir-calibration-rule">
                    Task-specific S3: 1–10 staged questions, real decode and deterministic phrase
                    postprocessing; no private gold. Shared generic S3: ≥10 public records, 15
                    recommended, gold optional. Effective composite prompt unresolved; these are
                    different instructions. No task-specific 15-public-gold requirement.
                  </p>
                )}
                <p>
                  Actual decode absent. Task plan declares one endoscopy image; actual Full image
                  assembly and calibration eligibility remain unresolved.
                </p>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Explore Kvasir-VQA scoring branches">
                  {branches.map((s, j) => (
                    <button
                      key={s}
                      type="button"
                      data-kvasir-branch={j}
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
          <p>
            All actual fields null; no source raw annotation copied into a participant artifact.
          </p>
          <button
            aria-expanded={format}
            aria-controls="kvasir-format-rule"
            onClick={() => setFormat(!format)}
          >
            Inspect format boundary
          </button>
          {format && (
            <p id="kvasir-format-rule">
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
          <h3>Public raw annotation; no private gold</h3>
          <button
            aria-expanded={referenceVisible(state, revealed)}
            aria-controls="kvasir-public-reference"
            disabled={state.reference <= 0.5}
            onClick={() => setRevealed(!revealed)}
          >
            Reveal public raw annotation
          </button>
          {referenceVisible(state, revealed) ? (
            <div className={css.socket} id="kvasir-public-reference" data-kvasir-reference-revealed>
              <b>Source raw annotation answer: {reference.answer}</b>
              <p>{reference.role}</p>
              <p>Source category: {reference.category}</p>
              <p>
                Not model evidence, recovered Full answer or independent clinical finding. AllIDs
                includes missing/invalid answers; binary-subset denominator differs.
              </p>
            </div>
          ) : (
            <p data-kvasir-reference-hidden>
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
            <b>Source raw annotation cannot establish test performance</b>
            <p>
              Leakage/calibration isolation, benchmark permission and judge reliability unresolved.
              No localization, pathology diagnosis or generated result.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
export function AutomedKvasirOutput({ state }: { state: AutomedKvasirState }) {
  return (
    <aside data-kvasir-output={state.scene} className={`${shared.storyOutput} ${css.output}`}>
      <b>Image +open-ended question</b>
      <p>1 public raw example; Full split/private answer absent.</p>
      <p>Actual answer empty. Lexical, binary and judge branches remain distinct.</p>
      <small>
        Public raw annotation is reader-controlled in its dedicated scene; backward/exit reset
        covers it. Private Full gold remains absent.
      </small>
    </aside>
  );
}

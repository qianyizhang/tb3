import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  fixture,
  steps,
  operationIndex,
  operationFrame,
  referenceVisible,
  resetOnBackward,
  type AutomedPathology100State,
} from './automedbench-full-pathology-caption-100-task';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './automedbench-full-pathology-caption-100-task.module.css';
export function AutomedPathology100Scene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedPathology100State;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const i = operationIndex(state);
  const [show, setShow] = useState(false);
  const [format, setFormat] = useState(false);
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  const previous = useRef({ frame: state.frame, beat: state.beatId });
  useLayoutEffect(() => {
    if (
      previous.current.beat !== state.beatId ||
      resetOnBackward(previous.current.frame, state.frame)
    ) {
      setShow(false);
      setFormat(false);
      setTier('lite');
    }
    previous.current = { frame: state.frame, beat: state.beatId };
  }, [state.frame, state.beatId]);
  return (
    <section className={css.scene} data-pathology100-scene={state.scene}>
      {state.scene === 'input' && (
        <>
          <h3>PathCap100: one image, one caption</h3>
          <figure className={css.socket}>
            <div className={css.sockets}>
              <span>
                Histology image
                <br />
                empty source socket
              </span>
              <b>
                → 1 case
                <br />→ 1 report.txt
              </b>
            </div>
            <figcaption>
              Authored socket only: 0 actual images/captions. Tissue, stain, magnification and
              specimen remain unknown.
            </figcaption>
          </figure>
          <p>
            Expected 100 selected case IDs are unstaged. 500 is a different declared selection;
            subset relation is unknown. Public captions are not initial solver input.
          </p>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Inspect image unit, caption syntax and metric gap</h3>
          <nav className={css.controls} aria-label="PathCap100 contract steps">
            {steps.map((s, j) => (
              <button
                key={s}
                type="button"
                data-pathology100-step={j}
                aria-pressed={i === j}
                disabled={!onSeekFrame}
                onClick={() => onSeekFrame?.(operationFrame(plan, j))}
              >
                {s}
              </button>
            ))}
          </nav>
          <div className={css.socket} data-pathology100-currentstage={i}>
            {i === 0 ? (
              <>
                <b>Exactly one JPEG per case → one caption file</b>
                <nav className={css.controls} aria-label="PathCap inference guidance">
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
                <p data-pathology100-tier>
                  {tier === 'lite'
                    ? 'Release-owned BLIP inference-only baseline; no website checkpoint or availability claim.'
                    : 'Compare at least three source-prescribed public inference-only captioning candidates; benchmark training forbidden.'}
                </p>
                <p>
                  Lite BLIP inference-only; Standard compares ≥3 public inference-only candidates.
                  No training on benchmark cases. Selected 100 case IDs and train/test overlap
                  absent.
                </p>
              </>
            ) : i === 1 ? (
              <>
                <b>1–8000 raw chars · ≥1 letter · ASCII printable</b>
                <p>
                  One ASCII letter passes syntax only. No caption relevance, morphology or clinical
                  correctness is established. UTF-8 readable, nonempty. Plain caption with no
                  JSON/debug wrapper is a task instruction; the checker does not enforce wrapper
                  structure.
                </p>
              </>
            ) : (
              <>
                <b>Default CXR schema does not validate pathology</b>
                <p>{source.runtime_discrepancy}</p>
                <p>Fractions 0–1; no score or pathology quality measured.</p>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Participant caption empty; syntax fixture only</h3>
          <code data-pathology100-output-schema>agent_outputs/&lt;case_id&gt;/report.txt</code>
          <button type="button" aria-expanded={format} onClick={() => setFormat(!format)}>
            Inspect authored syntax fixture
          </button>
          {format && <pre data-pathology100-format>{fixture.text}</pre>}
          <p>
            Authored nonclinical text, unrelated to any image or patient. 0 saved caption/model
            results.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Private captions absent; evaluator mechanics</h3>
          <button
            type="button"
            aria-expanded={show}
            aria-controls="pathology100-grading-mechanics"
            onClick={() => setShow(!show)}
          >
            {show ? 'Hide grading mechanics' : 'Reveal grading mechanics'}
          </button>
          {referenceVisible(state, show) ? (
            <div
              id="pathology100-grading-mechanics"
              className={css.socket}
              data-pathology100-reference-revealed
            >
              <b>valid cases / all supplied IDs; 100 not enforced</b>
              <p>
                Any requested missing/invalid caption forces F and zero aggregate clinical
                components. Raw micro fields can remain retained.
              </p>
              <p>
                CXR regex empty-positive overlap returns F1=1 by convention. This is not evidence of
                pathology caption quality. No private/public caption is revealed.
              </p>
            </div>
          ) : (
            <p data-pathology100-reference-hidden>
              Evaluator mechanics covered until explicit reader reveal.
            </p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Source access and pathology evaluation unresolved</h3>
          <p>{source.actual_data_gap}</p>
          <div className={css.socket}>
            <b>No selection or clinical/model performance evidence</b>
            <p>
              Retained official metadata lists gated noncommercial-use and citation fields. No terms
              accepted. Metric pathology compatibility, train/test leakage and actual image-caption
              pairing unresolved.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
export function AutomedPathology100Output({ state }: { state: AutomedPathology100State }) {
  return (
    <aside data-pathology100-output className={`${shared.storyOutput} ${css.output}`}>
      <b>100 expected image cases</b>
      <p>Selected IDs unstaged; 1 image/1 caption per case. 500 membership relation unknown.</p>
      <p>1–8000 chars, ≥1 letter; syntax is not caption quality. Actual caption empty.</p>
      <small>
        Private caption absent; grading-rule reveal is educational and resets before paint.
      </small>
    </aside>
  );
}

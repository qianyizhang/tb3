import { useState, useRef, useLayoutEffect } from 'react';
import {
  source,
  fixture,
  steps,
  operationIndex,
  operationFrame,
  referenceVisible,
  type AutomedIuReportState,
} from './automedbench-full-iu-xray-report-task';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './automedbench-full-iu-xray-report-task.module.css';
export function AutomedIuReportScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedIuReportState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const i = operationIndex(state);
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  const [format, setFormat] = useState(false);
  const [binding, setBinding] = useState<'declared' | 'default'>('declared');
  const previous = useRef(state.frame),
    scene = useRef(state.scene);
  useLayoutEffect(() => {
    if (state.frame < previous.current || scene.current !== state.scene) {
      setTier('lite');
      setFormat(false);
      setBinding('declared');
    }
    previous.current = state.frame;
    scene.current = state.scene;
  }, [state.frame, state.scene]);
  return (
    <section className={css.scene} data-iu-report-scene={state.scene}>
      {state.scene === 'input' && (
        <>
          <h3>Symbolic study; matching images/report absent</h3>
          <figure className={css.socket}>
            <div className={css.sockets}>
              <span>
                Image A<br />
                empty source socket
              </span>
              <span>
                Image B<br />
                empty source socket
              </span>
              <b>
                → 1 study
                <br />→ 1 report.txt
              </b>
            </div>
            <figcaption>
              Two authored image sockets illustrate grouping only. Actual image/report/case count:
              0. View and Full manifest mapping unresolved.
            </figcaption>
          </figure>
          <p>
            Public images belong to the solver. Source reports, if later acquired, require separate
            reader reveal; no report is bundled.
          </p>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Inspect the actual report contract</h3>
          <nav className={css.controls} aria-label="IU method assistance">
            {(['lite', 'standard'] as const).map((t) => (
              <button type="button" key={t} aria-pressed={tier === t} onClick={() => setTier(t)}>
                {t}
              </button>
            ))}
          </nav>
          <p data-iu-assistance>
            {tier === 'lite'
              ? 'Lite: prescribed CheXagent-2-3b path; consume every JPEG in the study manifest.'
              : 'Standard: compare at least three source candidates; chosen pipeline and resources remain unprovisioned.'}
          </p>
          <nav className={css.controls} aria-label="IU report contract steps">
            {steps.map((s, j) => (
              <button
                key={s}
                type="button"
                aria-pressed={i === j}
                disabled={!onSeekFrame}
                onClick={() => onSeekFrame?.(operationFrame(plan, j))}
              >
                {s}
              </button>
            ))}
          </nav>
          <div className={css.socket}>
            {i === 0 ? (
              <>
                <b>One or more JPEGs per study → one text report</b>
                <p>
                  Consume every image in the public manifest. Evaluator denominator is its supplied
                  case list; image count does not multiply reports.
                </p>
              </>
            ) : i === 1 ? (
              <>
                <b>40–8000 raw chars · ≥20 letters · ASCII printable</b>
                <p>
                  UTF-8 readable and nonempty. Unicode letters may still fail string.printable.
                  Format success does not validate medical content.
                </p>
              </>
            ) : (
              <>
                <b>Seven equal components are declared intent</b>
                <nav className={css.controls} aria-label="IU declared versus executable metrics">
                  {(['declared', 'default'] as const).map((b) => (
                    <button
                      key={b}
                      type="button"
                      aria-pressed={binding === b}
                      onClick={() => setBinding(b)}
                    >
                      {b === 'declared' ? 'Declared seven' : 'Executable default'}
                    </button>
                  ))}
                </nav>
                <p data-iu-binding>
                  {binding === 'declared'
                    ? 'Config: equal BLEU, METEOR, ROUGE-L, F1RadGraph, micro precision, recall and F1; metric assets absent.'
                    : 'Missing clinical_score_backend/weights selects lightweight 0.7 observation F1 + 0.3 ROUGE-L. Fractions 0–1; not clinical accuracy.'}
                </p>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Plain text file; actual report empty</h3>
          <code data-iu-report-output-schema>agent_outputs/&lt;case_id&gt;/report.txt</code>
          <pre>{fixture.text}</pre>
          <button
            className={css.controls}
            type="button"
            aria-expanded={format}
            onClick={() => setFormat(!format)}
          >
            Inspect text format
          </button>
          {format && (
            <p data-iu-format>
              UTF-8 decode; 40–8000 raw characters, at least 20 letters, ASCII printable. No JSON
              wrapper. Format validity does not establish factual quality.
            </p>
          )}
          <p>
            Authored nonclinical format fixture only. No patient finding, JSON envelope, prediction
            or clinical score.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Private reports absent; evaluator mechanics</h3>
          {referenceVisible(state) ? (
            <div className={css.socket} data-iu-report-reference-revealed>
              <b>valid studies / all supplied studies</b>
              <p>
                Any requested missing/invalid report forces F and zeroes aggregate clinical
                components. Missing predictions remain empty entries in scoring.
              </p>
              <p>
                Local default: 0.7 observation F1 + 0.3 token-LCS similarity. Raw micro metrics may
                remain nonzero after aggregate invalidation; no actual score exists.
              </p>
            </div>
          ) : (
            <p data-iu-report-reference-hidden>
              Evaluator mechanics covered until explicit reader reveal.
            </p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Defined task; no qualified clinical result</h3>
          <p>{source.actual_data_gap}</p>
          <div className={css.socket}>
            <b>Metric assets and assembly unresolved</b>
            <p>
              External MLRG tokenization/checkpoints unverified. Baseline weights and effective tier
              prompt assembly absent. Study/image correspondence not recovered.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
export function AutomedIuReportOutput({ state }: { state: AutomedIuReportState }) {
  return (
    <aside data-iu-report-output className={`${shared.storyOutput} ${css.output}`}>
      <b>1 text file per study</b>
      <p>0 source images/reports; actual Full output empty.</p>
      <p>40–8000 chars,≥20 letters, ASCII printable. No clinical validity follows.</p>
      <small>
        Reference {referenceVisible(state) ? 'explicitly revealed' : 'covered'}; reset covers it.
      </small>
    </aside>
  );
}

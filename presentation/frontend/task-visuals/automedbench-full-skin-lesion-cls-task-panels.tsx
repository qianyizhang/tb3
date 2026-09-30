import { useState, useLayoutEffect, useRef } from 'react';
import {
  processorView,
  submissionFields,
  shouldResetControls,
} from './automed-skin-lesion-controls';
import {
  source,
  steps,
  abbreviations,
  canonicalForIndex,
  mappingIndex,
  operationIndex,
  operationFrame,
  referenceVisible,
  type AutomedSkinLesionState,
} from './automedbench-full-skin-lesion-cls-task';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './automedbench-full-skin-lesion-cls-task.module.css';
export function AutomedSkinLesionScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedSkinLesionState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const i = operationIndex(state),
    m = mappingIndex(state);
  const [view, setView] = useState<'native' | 'processor'>('processor');
  const [format, setFormat] = useState<'csv' | 'json'>('csv');
  const previous = useRef(state.frame),
    scene = useRef(state.scene);
  useLayoutEffect(() => {
    if (shouldResetControls(previous.current, state.frame) || scene.current !== state.scene) {
      setView('processor');
      setFormat('csv');
    }
    previous.current = state.frame;
    scene.current = state.scene;
  }, [state.frame, state.scene]);
  return (
    <section className={css.scene} data-skin-lesion-scene={state.scene}>
      {state.scene === 'input' && (
        <>
          <h3>HAM10000 source example; Full test socket empty</h3>
          <div className={css.two}>
            <figure>
              <img
                className={css.native}
                src={source.preview_data_uri}
                alt="Public HAM10000 dermoscopy source example, no diagnostic overlay or model interpretation"
              />
              <figcaption>
                ISIC_0024306 · 600×450 RGB · CC BY-NC4 · MILK study team. Source-delivered bytes
                unchanged.
              </figcaption>
            </figure>
            <div className={css.socket}>
              <b>/data/public/&lt;case_id&gt;/image.jpg</b>
              <p>
                Full split/private labels absent; public example has no frozen Full equivalence. API
                says22038 bytes, received25247. Public metadata is helper information, not a
                prediction or clinical finding here.
              </p>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Fixed Lite checkpoint; map to output vocabulary</h3>
          <nav className={css.controls} aria-label="Classification steps">
            {steps.map((step, j) => (
              <button
                key={step}
                type="button"
                aria-pressed={i === j}
                disabled={!onSeekFrame}
                onClick={() => onSeekFrame?.(operationFrame(plan, j, m))}
              >
                {step}
              </button>
            ))}
          </nav>
          {i === 0 ? (
            <div className={css.socket}>
              <nav className={css.controls} aria-label="Native display versus processor contract">
                {(['native', 'processor'] as const).map((v) => (
                  <button
                    key={v}
                    aria-pressed={view === v}
                    type="button"
                    onClick={() => setView(v)}
                  >
                    {v === 'native' ? 'Native display' : 'Processor settings'}
                  </button>
                ))}
              </nav>
              <b data-skin-lesion-preprocessing>{processorView(view, source.processor_config)}</b>
              <p>
                Pinned ViT processor settings only; displayed native image was not transformed for a
                model. Logits/tensor absent. Lite forbids substitution, training, fine-tuning or
                ensemble.
              </p>
            </div>
          ) : i === 1 ? (
            <div className={css.socket}>
              <nav className={css.controls} aria-label="Inspect seven checkpoint label mappings">
                {abbreviations.map((a, j) => (
                  <button
                    key={a}
                    type="button"
                    aria-pressed={m === j}
                    disabled={!onSeekFrame}
                    onClick={() => onSeekFrame?.(operationFrame(plan, 1, j))}
                  >
                    {j}:{a}
                  </button>
                ))}
              </nav>
              <b>
                index {m} → {abbreviations[m]} → {canonicalForIndex(m)}
              </b>
              <p>
                Source-defined mapping selection only. No argmax, logits or image prediction exists.
                Raw abbreviations fail canonical-label format.
              </p>
            </div>
          ) : (
            <div className={css.socket}>
              <b>All staged IDs → one canonical string per case</b>
              <p>
                predictions.csv patient_id,label or per-case prediction.json. CSV present label
                precedes JSON fallback; private labels never enter model input.
              </p>
            </div>
          )}
          <small>
            Seven source classes are benchmark vocabulary; no lesion location, uncertainty or
            clinical diagnosis is inferred.
          </small>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Artifact syntax; actual prediction empty</h3>
          <code>participant_prediction: —</code>
          <nav className={css.controls} aria-label="Skin classification submission format">
            {(['csv', 'json'] as const).map((f) => (
              <button
                key={f}
                type="button"
                aria-pressed={format === f}
                onClick={() => setFormat(f)}
              >
                {f}
              </button>
            ))}
          </nav>
          <code data-skin-lesion-fields>{submissionFields(format).join(',')}</code>
          <pre>
            {format === 'csv'
              ? 'patient_id,label\ntoy-case,melanocytic_nevi'
              : '{"label":"melanocytic_nevi"}'}
          </pre>
          <p>
            Authored toy formatting, unrelated to the source image. Alternatively prediction.json
            contains a canonical label. No saved model result or private reference.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Headline macro recall; private GT absent</h3>
          {referenceVisible(state) ? (
            <div data-skin-lesion-reference-revealed>
              <b>Balanced accuracy = mean recall over represented true classes</b>
              <p>
                Absent GT classes omitted; missing predictions wrong within their true class. Plain
                accuracy separately divides correct by allIDs. Partial may be format-valid; empty or
                raw nv fails format.
              </p>
              <p>
                No extra completion multiplier. Configured thresholds .80/.45 are gates, not
                performance estimates. Actual denominator/split/score absent.
              </p>
            </div>
          ) : (
            <p data-skin-lesion-reference-hidden>
              Source evaluator mechanics covered until reader reveal.
            </p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Source example does not establish performance</h3>
          <p>{source.actual_data_gap}</p>
          <div className={css.socket}>
            <b>Generic prompt conflict</b>
            <p>{source.prompt_conflict}</p>
          </div>
          <p>
            Checkpoint training overlap, patients/lesions, actual test isolation and clinical
            adjudication unresolved. No model weights or inference run.
          </p>
        </>
      )}
    </section>
  );
}
export function AutomedSkinLesionOutput({ state }: { state: AutomedSkinLesionState }) {
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-skin-lesion-output>
      <b>Seven classes; canonical strings</b>
      <p>1 native HAM10000 public example. Actual Full prediction/reference absent.</p>
      <p>
        Macro recall over represented true classes; class balancing differs from plain accuracy.
      </p>
      <p>Scores are fractions 0–1, rounded to four decimal places; no measured score.</p>
      <small>
        Reference {referenceVisible(state) ? 'explicitly revealed' : 'covered'}; reset covers it.
      </small>
    </aside>
  );
}

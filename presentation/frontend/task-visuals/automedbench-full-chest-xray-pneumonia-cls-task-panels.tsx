import {
  source,
  steps,
  operationIndex,
  operationFrame,
  referenceVisible,
  publicTrainingLabel,
  type AutomedPneumoniaState,
} from './automedbench-full-chest-xray-pneumonia-cls-task';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './automedbench-full-chest-xray-pneumonia-cls-task.module.css';
export function AutomedPneumoniaScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedPneumoniaState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const i = operationIndex(state);
  return (
    <section
      className={css.scene}
      data-pneumonia-scene={state.scene}
      data-pneumonia-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Training helper available; Full test input absent</h3>
          <div className={css.two}>
            <figure>
              <img
                data-pneumonia-native
                className={css.native}
                src={source.preview_data_uri}
                alt="Original public training chest radiograph; source-folder label is helper, no diagnostic interpretation"
              />
              <figcaption>
                1 upstream training JPEG · 2090×1858 · bytes unchanged. Public training annotation
                covered until later reader reveal.
              </figcaption>
            </figure>
            <div className={css.socket}>
              <b>Full /data/public/&lt;case_id&gt;/image.jpg</b>
              <p>
                Frozen100 IDs and staged test image absent. Private evaluator label remains absent.
                This training file is not a Full test case.
              </p>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Two-class pipeline without test-label leakage</h3>
          <nav className={css.controls} aria-label="Classification implementation steps">
            {steps.map((step, j) => (
              <button
                key={step}
                type="button"
                aria-pressed={i === j}
                disabled={!onSeekFrame}
                onClick={() => onSeekFrame?.(operationFrame(plan, j))}
              >
                {step}
              </button>
            ))}
          </nav>
          {i === 0 ? (
            <div className={css.socket}>
              <b>Public train → training-derived validation</b>
              <p>
                Record grayscale/channel conversion and normalization. Frozen evaluation IDs
                excluded from fitting, calibration and selection. Actual split and checkpoint
                absent.
              </p>
            </div>
          ) : i === 1 ? (
            <div className={css.socket}>
              <b>class index 0 → normal · 1 → pneumonia</b>
              <p>
                Lite DenseNet-121 head: 1×2 output. Store this source-prescribed order with
                checkpoint. Standard compares DenseNet-121 / ResNet-50 / EfficientNet-B0 on common
                training-derived validation balanced accuracy. No logits or trained model shown.
              </p>
            </div>
          ) : (
            <div className={css.socket}>
              <b>Each staged case → exactly one canonical class file</b>
              <p>
                Inference input never includes private test label. CSV takes precedence, JSON
                fallback. Actual case list and predictions absent.
              </p>
            </div>
          )}
          <p>
            Native training label is helper data. Neither class implies lesion localization,
            bacterial/viral subtype or clinical diagnosis.
          </p>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Output schema; actual prediction empty</h3>
          <code>participant_prediction: —</code>
          <div className={css.two} data-pneumonia-output-schema>
            <pre>{'patient_id,label\ntoy-case,normal'}</pre>
            <pre>{'{"label":"normal"}'}</pre>
          </div>
          <p>
            Authored toy syntax only. It is not the displayed native image, a saved response,
            private reference or score.
          </p>
          <p>
            CSV: agents_outputs/predictions.csv · JSON:
            agents_outputs/&lt;case_id&gt;/prediction.json.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Training helper and evaluator rules; no private reference</h3>
          {referenceVisible(state) ? (
            <div data-pneumonia-reference-revealed>
              <b data-pneumonia-training-label>
                Public training helper: {source.native_example.source_folder_label} →{' '}
                {publicTrainingLabel(state)}
              </b>
              <p>
                Training-folder annotation only; no diagnosis, model prediction or private Full test
                reference.
              </p>
              <b>Accuracy = n_correct / len(patient_ids)</b>
              <p>
                Missing prediction or reference cannot be correct; IDs stay in denominator. Partial
                output may be format-valid; empty output fails. Unknown classes fail format.
                Balanced accuracy averages recall over represented true classes. Values are 0–1
                fractions rounded to four decimals, not percentages.
              </p>
              <p>
                Config headline is accuracy; no extra completion multiplier. Declared100 is
                unresolved split target, not observed denominator. Thresholds .85/.50 are
                provisional generic defaults.
              </p>
            </div>
          ) : (
            <p data-pneumonia-reference-hidden>
              Scorer mechanics covered until explicit reader reveal.
            </p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Harness and sample boundaries</h3>
          <p>{source.actual_data_gap}</p>
          <div className={css.socket}>
            <b>Stage prompt conflict</b>
            <p>{source.prompt_conflict}</p>
          </div>
          <p>
            Actual reference isolation, final split, preprocessing and performance need a separately
            authorized staged evaluation. Source folder labels are not adjudicated clinical
            findings.
          </p>
        </>
      )}
    </section>
  );
}
export function AutomedPneumoniaOutput({ state }: { state: AutomedPneumoniaState }) {
  return (
    <aside data-pneumonia-output={state.scene} className={`${shared.storyOutput} ${css.output}`}>
      <b>normal / pneumonia</b>
      <p>1 native public training helper · actual Full test output absent.</p>
      <p>Class index map, one label per ID; no localization or subtype.</p>
      <small>
        Evaluator rules {referenceVisible(state) ? 'explicitly revealed' : 'covered'}; reset covers
        them.
      </small>
    </aside>
  );
}

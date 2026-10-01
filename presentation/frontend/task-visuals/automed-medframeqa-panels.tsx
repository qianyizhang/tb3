import { useLayoutEffect, useRef, useState } from 'react';
import type { StoryPlan } from '../contracts.generated';
import {
  automedMedframeqaPack as pack,
  operationFrame,
  operationIndex,
  resetOnBackward,
  type AutomedMedframeqaState,
} from './automed-medframeqa';
import css from './automed-medframeqa.module.css';
const titles = {
  input: 'Public upstream slots · Full join absent',
  helper: 'Six source options versus five Full tokens',
  operation: 'Keep question, frames and prompt aligned',
  output: 'Six required answer fields · unset',
  limits: 'Question accuracy and validity differ',
} as const;
const stepLabels = [
  'Audit question / frames',
  'Build aligned prompt',
  'Infer / parse A..E',
  'Map option / submit',
];
export function AutomedMedframeqaScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedMedframeqaState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const [slot, setSlot] = useState(0);
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  const [calibration, setCalibration] = useState(false);
  const [format, setFormat] = useState(false);
  const [metric, setMetric] = useState<'accuracy' | 'format_gate' | 'workflow'>('accuracy');
  const previous = useRef({ frame: state.frame, beat: state.beatId });
  useLayoutEffect(() => {
    if (
      previous.current.beat !== state.beatId ||
      resetOnBackward(previous.current.frame, state.frame)
    ) {
      setSlot(0);
      setTier('lite');
      setCalibration(false);
      setFormat(false);
      setMetric('accuracy');
    }
    previous.current = { frame: state.frame, beat: state.beatId };
  }, [state.frame, state.beatId]);
  const index = operationIndex(state.progress);
  return (
    <div
      className={css.scene}
      data-medframeqa-scene={state.scene}
      data-medframeqa-currentstep={state.scene === 'operation' ? index : undefined}
    >
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' ? (
        <div className={css.columns} data-medframeqa-input>
          <figure className={css.figure}>
            <div className={css.buttons} role="group" aria-label="Upstream frame slot">
              {pack.frames.map((_, i) => (
                <button type="button" key={i} aria-pressed={slot === i} onClick={() => setSlot(i)}>
                  Source slot {i + 1}
                </button>
              ))}
            </div>
            <img
              src={pack.frames[slot]}
              alt={`Native public upstream image_${slot + 1}; source slot only, no diagnostic overlay`}
            />
            <figcaption>Upstream public test row 0 · no Full question join</figcaption>
          </figure>
          <div className={css.card}>
            <b>Question is the scored unit</b>
            <p>
              Two native JPEG source slots, 1280×720 pixels. Full question, options and answer
              remain absent.
            </p>
            <p>{pack.source.order}</p>
            <p>{pack.source.geometry}</p>
            <strong className={css.caution}>
              Source test partition does not prove video-disjoint or patient-independent evaluation.
            </strong>
          </div>
        </div>
      ) : state.scene === 'helper' ? (
        <div className={css.columns} data-medframeqa-helper>
          <div className={css.card}>
            <b>Upstream option slots · texts withheld</b>
            <div className={css.slots}>
              {Array.from({ length: pack.helper.source_options }, (_, i) => (
                <span key={i} data-unmapped={i === 5}>
                  slot {i + 1}
                </span>
              ))}
            </div>
            <b>Full allowed tokens</b>
            <div className={css.slots}>
              {pack.helper.valid_labels.map((c) => (
                <code key={c}>{c}</code>
              ))}
            </div>
            <p>{pack.helper.mapping}</p>
          </div>
          <div className={css.card}>
            <b>Helpers and public calibration roles</b>
            <ul className={css.steps}>
              {pack.helper.tools.map((t) => (
                <li key={t}>{t}</li>
              ))}
            </ul>
            <button
              type="button"
              aria-expanded={calibration}
              aria-controls="medframeqa-calibration-rules"
              onClick={() => setCalibration(!calibration)}
            >
              Inspect calibration rule
            </button>
            {calibration && (
              <p id="medframeqa-calibration-rules" data-medframeqa-calibration>
                {pack.helper.calibration}
              </p>
            )}
            <p>No source question, options, gold or reasoning text is revealed.</p>
          </div>
        </div>
      ) : state.scene === 'operation' ? (
        <div data-medframeqa-operation>
          <div className={css.buttons} role="group" aria-label="Canonical question workflow">
            {stepLabels.map((s, i) => (
              <button
                type="button"
                key={s}
                data-medframeqa-step={i}
                aria-pressed={index === i}
                disabled={!onSeekFrame}
                onClick={() => onSeekFrame?.(operationFrame(plan, i))}
              >
                {i + 1}. {s}
              </button>
            ))}
          </div>
          <div className={css.columns}>
            <div className={css.card}>
              <b>{stepLabels[index]}</b>
              <p>{pack.operation.steps[index]}</p>
              <div className={css.buttons} role="group" aria-label="MedFrameQA assistance">
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
              </div>
              <p data-medframeqa-tier>{pack.helper.tiers[tier]}</p>
            </div>
            <div className={css.card}>
              <b>Prompt contract · no generated question</b>
              <div className={css.tokens}>
                <span>Frame 1 &lt;image&gt;</span>
                <span>… every supplied Full frame</span>
                <span>Question: unset</span>
                <span>A..E option text: unset</span>
              </div>
              <p>
                Image tokens follow actual Full image_paths. Source slots establish neither
                timestamps nor native CT slice ordering. No inference or submission has run.
              </p>
            </div>
          </div>
        </div>
      ) : state.scene === 'output' ? (
        <div className={css.columns} data-medframeqa-output-schema>
          <div className={css.card}>
            <b className={css.path}>{pack.output.path}</b>
            <div className={css.fields}>
              {Object.entries(pack.output.fields).map(([key, type]) => (
                <div key={key}>
                  <code>{key}</code>
                  <span>{type}</span>
                  <em>unset</em>
                </div>
              ))}
            </div>
            <button
              type="button"
              aria-expanded={format}
              aria-controls="medframeqa-format-rules"
              onClick={() => setFormat(!format)}
            >
              Inspect format checks
            </button>
            {format && (
              <p id="medframeqa-format-rules" data-medframeqa-format>
                {pack.output.format}
              </p>
            )}
          </div>
          <div className={css.card}>
            <b>Schema is separate from inference evidence</b>
            <p>
              Raw output, runtime and model identity require a genuine execution record. No
              submitted answer exists.
            </p>
            <p>{pack.output.checker_difference}</p>
            <strong className={css.caution}>
              Private reference and public source gold are absent.
            </strong>
          </div>
        </div>
      ) : (
        <div className={css.columns} data-medframeqa-limits>
          <div className={css.card}>
            <div className={css.buttons} role="group" aria-label="Scoring boundary">
              {(['accuracy', 'format_gate', 'workflow'] as const).map((m) => (
                <button
                  type="button"
                  key={m}
                  aria-pressed={metric === m}
                  onClick={() => setMetric(m)}
                >
                  {m.replaceAll('_', ' ')}
                </button>
              ))}
            </div>
            <p data-medframeqa-metric>{pack.output[metric]}</p>
            <p>{pack.output.completion}</p>
            <p>{pack.output.rating_rule}</p>
          </div>
          <div className={css.card}>
            <b>Agreement limits</b>
            <p>{pack.output.limits}</p>
            <p>
              The six-option upstream row is not a verified Full question. No patient, video or
              held-out performance follows from these images.
            </p>
            <strong className={css.caution}>Accuracy/rating/model result = unset</strong>
          </div>
        </div>
      )}
    </div>
  );
}
export function AutomedMedframeqaOutput({ state }: { state: AutomedMedframeqaState }) {
  return (
    <aside className={css.sidebar} data-medframeqa-output>
      <h3>Unsubmitted question record</h3>
      <div className={css.sidebarFields}>
        {Object.keys(pack.output.fields).map((key) => (
          <div key={key}>
            <code>{key}</code>
            <span>unset</span>
          </div>
        ))}
      </div>
      <p>Public source gold, private reference and model output absent.</p>
      <small>
        {state.scene === 'limits'
          ? '0–1 label agreement over all question IDs; no clinical accuracy.'
          : 'Native upstream slots · Full mapping absent.'}
      </small>
    </aside>
  );
}

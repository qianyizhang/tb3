import { useLayoutEffect, useRef, useState } from 'react';
import { rexLdctIqaPack as pack, type RexLdctIqaState } from './rex-ldct-iqa';
import shared from './task-visual.module.css';
import css from './rex-ldct-iqa.module.css';
const titles = {
  input: 'Inspect official training CT',
  helper: 'Inspect label and visibility',
  operation: 'Follow no-reference prediction',
  output: 'Inspect unfilled CSV',
  limits: 'Compare grader fields',
} as const;
function Input() {
  return (
    <div className={css.columns} data-ldct-input>
      <figure className={css.image}>
        <img
          src={pack.imageUrl}
          alt="Official public training CT 0559, normalized grayscale preview; no annotated diagnostic finding"
        />
        <figcaption>0559.tif · 512 × 512 pixels · training</figcaption>
      </figure>
      <div className={css.card}>
        <b>Native training raster, linear preview</b>
        <p>{pack.source.display_transform}</p>
        <p>
          Source row/column order is preserved. Physical spacing, anatomical orientation and HU
          calibration are unavailable.
        </p>
        <p>
          The source description mentions soft-tissue window 350/40. Those values are not applied to
          this normalized TIFF.
        </p>
        <strong>No held-out input is retained</strong>
      </div>
    </div>
  );
}
function Helper({ state }: { state: RexLdctIqaState }) {
  const [revealed, setRevealed] = useState(false);
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (state.frame < previous.current) setRevealed(false);
    previous.current = state.frame;
  }, [state.frame]);
  const [selected, setSelected] = useState<'training' | 'inference' | 'evaluator'>('training');
  return (
    <div data-ldct-helper>
      <div className={css.buttons} role="group" aria-label="LDCT data visibility">
        {(['training', 'inference', 'evaluator'] as const).map((p) => (
          <button
            key={p}
            type="button"
            aria-pressed={selected === p}
            onClick={() => {
              setSelected(p);
              setRevealed(false);
            }}
          >
            {p}
          </button>
        ))}
      </div>
      <div className={css.columns}>
        <div className={css.card} data-ldct-partition={selected}>
          <b>
            {selected === 'evaluator'
              ? 'Declared evaluator-only path'
              : 'Declared solver-visible paths'}
          </b>
          {pack.operation.partitions[selected].map((p) => (
            <p key={p}>
              <code>{p}</code>
            </p>
          ))}
          <p>Filesystem isolation is declared by paths, not verified by a runtime audit.</p>
        </div>
        <div className={css.card}>
          {selected === 'training' ? (
            <>
              <b>Public training helper · {pack.helper.image_id}</b>
              <button
                type="button"
                className={css.reveal}
                aria-expanded={revealed}
                aria-controls="ldct-public-training-label"
                onClick={() => setRevealed(!revealed)}
              >
                {revealed ? 'Hide public training label' : 'Reveal public training label'}
              </button>
              {revealed ? (
                <p id="ldct-public-training-label" className={css.label} data-ldct-training-score>
                  {pack.helper.training_reader_score}
                </p>
              ) : (
                <p data-ldct-training-hidden>Public label covered · reader reveal</p>
              )}
              <p>
                Reader score from exact train.json record; not a model prediction. Scale endpoints
                were not verified in the pinned adapter.
              </p>
            </>
          ) : (
            <div className={css.socket}>
              <b>
                {selected === 'inference'
                  ? 'Held-out images absent'
                  : 'Private reader targets absent'}
              </b>
              <span>No target or image synthesized</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
function Operation({ state }: { state: RexLdctIqaState }) {
  return (
    <div className={css.columns} data-ldct-operation>
      <div className={css.card}>
        <b>Develop → infer → submit</b>
        <ol className={css.steps}>
          {pack.operation.steps.map((s, i) => (
            <li key={s} data-active={state.progress > (i + 1) / 4}>
              {s}
            </li>
          ))}
        </ol>
      </div>
      <div className={css.card}>
        <b>One CT → one scalar quality estimate</b>
        <p>
          No pristine image is required at inference. This task does not request a denoised CT or a
          mask.
        </p>
        <p>{pack.operation.preparation_split}</p>
        <p>{pack.operation.sample_submission}</p>
        <strong>No preparation, model or inference executed</strong>
      </div>
    </div>
  );
}
function Output() {
  return (
    <div className={css.columns} data-ldct-output-schema>
      <div className={css.card}>
        <b>submission.csv · required schema</b>
        <div className={css.fields}>
          {pack.output.columns.map((c) => (
            <div key={c}>
              <code>{c}</code>
              <span>unset</span>
            </div>
          ))}
        </div>
        <p>{pack.output.image_id_rule}</p>
      </div>
      <div className={css.socket}>
        <b>Unsubmitted output</b>
        <span>No test ID, predicted quality or measured metric is fabricated.</span>
      </div>
    </div>
  );
}
function Limits() {
  const [field, setField] = useState<'score' | 'overall'>('score');
  return (
    <div data-ldct-limits>
      <div className={css.buttons} role="group" aria-label="LDCT grader field">
        <button type="button" aria-pressed={field === 'score'} onClick={() => setField('score')}>
          score
        </button>
        <button
          type="button"
          aria-pressed={field === 'overall'}
          onClick={() => setField('overall')}
        >
          overall
        </button>
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <b data-ldct-grader-field>{field}</b>
          <p>{field === 'score' ? pack.output.score_rule : pack.output.overall_rule}</p>
          <p>
            {field === 'score'
              ? 'Range 0..3 only for finite, nondegenerate coefficients; higher magnitudes indicate stronger association.'
              : 'Mean position is lower-is-better and leaderboard-dependent; fallback -abs(Pearson) has another scale.'}
          </p>
          <p className={css.caution}>|r| = |−r| · mathematical rule only</p>
          <p>No cohort coefficients can be derived from one illustrated training image.</p>
        </div>
        <div className={css.card}>
          <b>Limits of agreement</b>
          {pack.output.limits.map((s) => (
            <p key={s}>{s}</p>
          ))}
          <p>
            Agreement with reader scores does not establish clinical benefit or diagnostic accuracy.
          </p>
        </div>
      </div>
    </div>
  );
}
export function RexLdctIqaScene({ state }: { state: RexLdctIqaState }) {
  return (
    <div className={css.scene} data-ldct-scene={state.scene}>
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' ? (
        <Input />
      ) : state.scene === 'helper' ? (
        <Helper key={state.beatId} state={state} />
      ) : state.scene === 'operation' ? (
        <Operation state={state} />
      ) : state.scene === 'output' ? (
        <Output />
      ) : (
        <Limits />
      )}
    </div>
  );
}
export function RexLdctIqaOutput({ state }: { state: RexLdctIqaState }) {
  return (
    <aside className={shared.storyOutput} data-ldct-output>
      <span className={shared.storyEyebrow}>Required output · unsubmitted</span>
      <h3>Predict perceived quality</h3>
      <div className={css.fields}>
        <div>
          <code>image_id</code>
          <span>unset</span>
        </div>
        <div>
          <code>quality_score</code>
          <span>unset</span>
        </div>
      </div>
      <p>
        Training helper is public; reveal it in the helper chapter. Private targets, model
        predictions and score remain absent.
      </p>
      <small>
        {state.scene === 'limits'
          ? 'score and overall are distinct grader fields.'
          : 'One official training CT; symbolic workflow only.'}
      </small>
    </aside>
  );
}

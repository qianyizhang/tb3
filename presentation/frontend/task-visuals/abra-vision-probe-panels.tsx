import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import {
  conditions,
  conditionIndex,
  displayOptions,
  fixture,
  modalityOptions,
  probeReferenceVisible,
  source,
  previews,
  selectedIndexSlot,
  probeOperationFrame,
  type AbraVisionProbeState,
} from './abra-vision-probe';
import css from './abra-vision-probe.module.css';
function Grid({ cells, label }: { cells: number[][]; label: string }) {
  return (
    <figure>
      <figcaption>{label}</figcaption>
      <svg viewBox="0 0 80 80" role="img" aria-label={label} className={css.grid}>
        {cells.flatMap((row, y) =>
          row.map((value, x) => (
            <rect
              key={`${x}-${y}`}
              x={x * 10}
              y={y * 10}
              width="10"
              height="10"
              fill={`rgb(${value},${value},${value})`}
            >
              <title>
                Authored display cell {x},{y}: {value} / 255
              </title>
            </rect>
          )),
        )}
      </svg>
    </figure>
  );
}
function Transform({ condition, indexSlot }: { condition: number; indexSlot: number }) {
  const sample = previews.instances[indexSlot];
  if (condition === 0)
    return (
      <div className={css.socket}>
        <b>Exact normal-modality default PNG absent</b>
        <p>
          Default transfer unverified. Source CT examples are in Lung/Soft views; neither
          reconstructs this condition.
        </p>
      </div>
    );
  if (condition === 2 || condition === 3)
    return (
      <div>
        <p className={css.label}>
          Source CT · selected index {sample.index} · InstanceNumber {sample.instance_number} ·
          independent derivative.
        </p>
        <div className={css.two}>
          {(['lung', 'soft'] as const).map((window) => (
            <figure key={window}>
              <figcaption>
                {window === 'lung' ? 'Lung' : 'Soft tissue'}: C={sample[window].center_HU}, W=
                {sample[window].width_HU} HU
              </figcaption>
              <img
                className={css.native}
                src={sample[window].data_uri}
                alt={`Source-example CT index ${sample.index}, ${window} window; no annotation or diagnosis`}
                width={512}
                height={512}
              />
            </figure>
          ))}
        </div>
        <small>
          Native 512×512; source float32 clip/scale/truncate, no resampling. MRI/DX absent.
        </small>
      </div>
    );
  if (condition === 4)
    return (
      <div className={css.transform}>
        <b>Breast MRI: source percentile transfer</b>
        <p>
          Raw signal → optional non-default rescale → 1st / 99th percentiles → clipping and uint8
          PNG.
        </p>
        <div className={css.percentile}>
          <span>p01 → 0</span>
          <span>interior → grayscale</span>
          <span>p99 → 255</span>
        </div>
        <p>
          Flat-image fallback uses min/max, then width ≥ 1. Units are signal intensity, not HU. No
          MRI image or enhancement finding is fabricated.
        </p>
      </div>
    );
  const isNoise = condition === 1 || condition === 5;
  const window = condition === 2 ? fixture.lung_window : fixture.soft_tissue_window;
  return (
    <div className={css.two}>
      <div>
        <b>Authored CT intensity ramp</b>
        <p>8×8 cells, -1500 to +500 HU; no anatomy or patient image.</p>
        <Grid
          cells={fixture.input_ramp_HU.map((row) =>
            row.map((v) => Math.floor(((v + 1500) / 2000) * 255)),
          )}
          label="Illustrative raw display [-1500,+500] HU"
        />
      </div>
      <div>
        <b>
          {isNoise
            ? 'Replace values entirely'
            : `Window C=${window.center_HU}, W=${window.width_HU} HU`}
        </b>
        <p>
          {isNoise
            ? 'Ignore input; retain dimensions. Uniform uint8 [0,255], seed 42; source name noise_gaussian.'
            : `Rescale CT → clip [${window.low_HU}, ${window.high_HU}] HU → map/truncate uint8 [0,255].`}
        </p>
        <Grid
          cells={isNoise ? fixture.replacement_noise.cells : window.cells}
          label={
            isNoise
              ? 'Illustrative uniform integer replacement; not Gaussian or additive noise'
              : 'Illustrative source-formula window output'
          }
        />
      </div>
    </div>
  );
}
export function AbraVisionProbeScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AbraVisionProbeState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const index = conditionIndex(state);
  const options = index < 2 ? modalityOptions : displayOptions;
  const slot = selectedIndexSlot(state);
  const selectedIndex = [14, 42, 70, 98, 126][slot];
  return (
    <section className={css.scene} data-abra-vision-probe-scene={state.scene}>
      {/* Integration retains the shared SourceWarning above this scene; no hidden banner inside a scroll card. */}
      {(state.scene === 'input' || state.scene === 'operation') && (
        <>
          <h3>Supplied view → condition → one option letter</h3>
          <div className={css.controls} aria-label="Select probe condition">
            {conditions.map((item, i) => (
              <button
                type="button"
                key={item}
                aria-pressed={i === index}
                aria-label={item}
                onClick={() => onSeekFrame?.(probeOperationFrame(plan, i, slot))}
                disabled={!onSeekFrame}
              >
                {
                  ['Modality', 'Modality control', 'Lung', 'Soft tissue', 'MRI', 'Display control'][
                    i
                  ]
                }
              </button>
            ))}
          </div>
          <div
            className={css.controls}
            aria-label="Supplied source indices for illustrative 140-instance series"
          >
            {[14, 42, 70, 98, 126].map((n, i) => (
              <button
                type="button"
                key={n}
                aria-pressed={selectedIndex === n}
                onClick={() => onSeekFrame?.(probeOperationFrame(plan, index, i))}
                disabled={!onSeekFrame}
              >
                Index {n}
              </button>
            ))}
          </div>
          <small>
            0-based selection for 140 instances; stack-normal order (InstanceNumber fallback).
          </small>
          <Transform condition={index} indexSlot={slot} />
          <h4>
            {index < 2 ? 'What modality is this image?' : 'What windowing preset was applied?'}
          </h4>
          <div className={css.options}>
            {options.map((option, i) => (
              <span key={option}>
                {'ABCD'[i]}) {option}
              </span>
            ))}
          </div>
          <p>
            Only submit_answer · initial viewport may expose window/level; image-only isolation
            unproven.
          </p>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>One terminal letter; participant output empty</h3>
          <code data-abra-vision-probe-empty-output>submit_answer.arguments.answer: —</code>
          <p>
            Formatting illustration only:{' '}
            <code>{'{"name":"submit_answer","arguments":{"answer":"A"}}'}</code>. The letter
            demonstrates syntax and is not a case answer or model response.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Evaluator label rule; no generated case reference</h3>
          {!probeReferenceVisible(state) ? (
            <p data-abra-vision-probe-reference-hidden>
              Source label rules covered until reader reveal.
            </p>
          ) : (
            <div data-abra-vision-probe-reference-revealed>
              <p>
                <b>Source-defined evaluator mapping:</b> modality CT→A, MR/MRI→B, DX→C;
                lung_window→A, soft_tissue_window→B, breast_mri→C; replacement noise→D (N/A).
              </p>
              <p>
                These mappings define expected letters from metadata/pipeline, not an observed
                answer or clinical image adjudication.
              </p>
              <p>
                The source control name says Gaussian, but its algorithm is uniform integer
                replacement. No original values survive; repeated same-size calls use seed 42. No
                causal performance claim follows.
              </p>
            </div>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Original selected PNG and task result remain absent</h3>
          <p>{source.actual_data_gap}</p>
          <p>
            Three-turn limit, selected-slice assistance, no oracle tool. A scorer label match is not
            diagnosis, free viewer navigation or a measured noise effect. Initial window/level
            context can be informative.
          </p>
        </>
      )}
    </section>
  );
}
export function AbraVisionProbeOutput({ state }: { state: AbraVisionProbeState }) {
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-abra-vision-probe-output>
      <b>ABRA vision probe</b>
      <p>{conditions[conditionIndex(state)]}</p>
      <p>Source CT derivative · exact task PNG, participant response and score absent.</p>
      <small>
        Reference mapping {probeReferenceVisible(state) ? 'explicitly revealed' : 'covered'}; reset
        restores coverage.
      </small>
    </aside>
  );
}

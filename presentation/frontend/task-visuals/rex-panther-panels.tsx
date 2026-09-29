import { pantherRecords, pantherRevealed, pantherTask, type RexPantherState } from './rex-panther';
import shared from './task-visual.module.css';
import css from './rex-panther.module.css';

const ACQUIRE = 'https://zenodo.org/records/15192302';

function VoxelGrid({ progress, title }: { progress: number; title: string }) {
  const focus = Math.max(0, Math.min(4, Math.round(progress * 4)));
  return (
    <div className={css.gridCard} data-panther-symbolic-grid>
      <div className={css.gridHead}>
        <b>{title}</b>
        <span>abstract index grid · no anatomy</span>
      </div>
      <svg
        viewBox="0 0 270 202"
        role="img"
        aria-label="Unitless five by five schematic voxel grid, not MRI"
      >
        <rect
          x="37"
          y="14"
          width="160"
          height="160"
          fill="#e6f1f3"
          stroke="#4f7c89"
          strokeWidth="1.5"
        />
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <g key={i} stroke="#9bbac3" strokeWidth="1">
            <path d={`M${37 + i * 32} 14v160`} />
            <path d={`M37 ${14 + i * 32}h160`} />
          </g>
        ))}
        <rect
          x={37 + focus * 32}
          y={14 + (4 - focus) * 32}
          width="32"
          height="32"
          fill="#49b5c2"
          fillOpacity=".55"
          stroke="#14758a"
          strokeWidth="2"
        />
        <path d="M37 180h160" stroke="#236074" markerEnd="url(#arrowPanther)" />
        <path d="M31 174V14" stroke="#236074" markerEnd="url(#arrowPanther)" />
        <defs>
          <marker
            id="arrowPanther"
            markerWidth="7"
            markerHeight="7"
            refX="5"
            refY="3"
            orient="auto"
          >
            <path d="M0 0L6 3L0 6" fill="none" stroke="#236074" />
          </marker>
        </defs>
        <text x="205" y="183">
          i →
        </text>
        <text x="12" y="12">
          j ↑
        </text>
        <text x="54" y="198">
          selected (i={focus}, j={focus}, k=1)
        </text>
      </svg>
      <small>
        Cells and cursor are symbolic; native dimensions and physical spacing are unknown.
      </small>
    </div>
  );
}
function Input({ state }: { state: RexPantherState }) {
  const { source } = pantherRecords(state);
  const task = pantherTask(state);
  return (
    <div className={css.input} data-panther-input>
      <VoxelGrid progress={state.grid} title={source.variant.modality} />
      <div className={css.inputFlow}>
        <article>
          <b>Public training help</b>
          <span>{source.variant.helper}</span>
          <small>Training labels are visible learning aids, never the held-out answer.</small>
        </article>
        <article>
          <b>Held-out input</b>
          <span>
            MHA image pattern <code>{source.variant.image_pattern}</code>
          </span>
          <small>Test image only. No source patient pixels are available to this pack.</small>
        </article>
        <div className={css.split}>
          Pinned 80/20 split of matched cases. If all {source.variant.annotated_source_count}{' '}
          described cases match: {source.variant.conditional_train_count} train /{' '}
          {source.variant.conditional_test_count} test. Preparer not run.
        </div>
        {task === 2 && (
          <div className={css.domain}>
            Task 1 diagnostic T1 is a different domain, not a paired or registered treatment-session
            scan.
          </div>
        )}
      </div>
    </div>
  );
}
function Geometry({ state }: { state: RexPantherState }) {
  const { source } = pantherRecords(state);
  return (
    <div className={css.geometry} data-panther-geometry>
      <VoxelGrid progress={state.grid} title="Index-space operation" />
      <div className={css.geometryFlow}>
        <div className={css.step}>
          <b>1 · Read current MHA header</b>
          <span>
            Dimensions, spacing in mm, origin in mm and direction matrix are native per image.
            Values are unknown here.
          </span>
        </div>
        <div className={css.formula}>
          <b>2 · Map index to physical position</b>
          <code>world = origin + direction × diag(spacing) × [i,j,k]</code>
        </div>
        <div className={css.step}>
          <b>3 · Write same-grid mask</b>
          <span>
            Binary tumor output should carry the input grid and physical metadata;{' '}
            {source.variant.label_pattern} names source labels, not a produced prediction.
          </span>
        </div>
      </div>
    </div>
  );
}
function Output({ state }: { state: RexPantherState }) {
  const { output } = pantherRecords(state);
  return (
    <div className={css.schema} data-panther-output-schema>
      <div className={css.schemaTitle}>ReX answer-owned submission · empty</div>
      <div className={css.schemaRow}>
        <span>{output.csv}</span>
        <code>{output.csv_columns.join(',')}</code>
      </div>
      <div className={css.schemaRow}>
        <span>relative mask path</span>
        <code>{output.relative_prediction_pattern}</code>
      </div>
      <div className={css.schemaRow}>
        <span>MHA label values</span>
        <code>0 background · 1 tumor</code>
      </div>
      <div className={css.empty}>
        <b>Nothing was produced</b>
        <span>
          No saved mask, CSV submission, model execution or grader result. The path is a schema
          template, not a file.
        </span>
      </div>
      <div className={css.pipeline}>
        held-out MHA image <em>→</em> method to develop <em>→</em> binary same-grid MHA socket
      </div>
    </div>
  );
}
function Reference({ state, reveal }: { state: RexPantherState; reveal: boolean }) {
  const { source } = pantherRecords(state);
  if (!reveal)
    return (
      <div className={css.covered} data-panther-reference-hidden>
        <b>Private test label remains unseen</b>
        <span>Only its source-defined role and label vocabulary can be explained.</span>
      </div>
    );
  return (
    <div className={css.reference} data-panther-reference>
      <b>Private held-out reference · no pixels available</b>
      <p>
        The pinned preparer writes test labels to <code>private/test/labels</code> and{' '}
        <code>test_labels.csv</code>. These are evaluator inputs, not public solver inputs or
        answer-owned outputs.
      </p>
      <div className={css.labelKeys}>
        <span>
          <i className={css.keyZero} />0 · background
        </span>
        <span>
          <i className={css.keyOne} />1 · tumor target
        </span>
        <span>
          <i className={css.keyTwo} />2 · possible pancreas in source GT
        </span>
      </div>
      <p>
        The grader extracts <code>GT == 1</code>. This vocabulary is source-defined; no patient
        label geometry is depicted. {source.variant.domain_boundary}
      </p>
    </div>
  );
}
function Limits({ state }: { state: RexPantherState }) {
  const { output } = pantherRecords(state);
  const task = pantherTask(state);
  return (
    <div className={css.limits} data-panther-limits>
      <article>
        <b>Recovered</b>
        <span>
          Pinned ReX description, preparation, grade, config and metric bytes; official
          restricted-record metadata.
        </span>
      </article>
      <article>
        <b>Absent</b>
        <span>
          No matching native MRI, source label, private test mask, prediction, score or patient
          geometry. Diagram uses unitless indices.
        </span>
      </article>
      <article>
        <b>Scorer limit</b>
        <span>
          Shape mismatch triggers nearest-neighbor prediction resize. Physical metrics use
          prediction-file spacing; affine/origin/direction agreement is unchecked.
        </span>
      </article>
      <div className={css.limitFoot}>
        <b>Metrics defined, not observed:</b> {output.grader.metrics.join(' · ')}.{' '}
        {task === 2
          ? 'Inference time matters to the workflow but is not measured by the pinned grader.'
          : 'Optional other-sequence unlabeled scans do not supply test labels.'}
      </div>
    </div>
  );
}
const titles: Record<RexPantherState['scene'], string> = {
  input: 'Identify the input and training help',
  geometry: 'Carry native MHA geometry to the mask',
  output: 'Fill the ReX output contract',
  reference: 'Keep held-out labels private',
  limits: 'Bound the scorer and evidence',
};
export function RexPantherScene({ state }: { state: RexPantherState }) {
  const task = pantherTask(state);
  const reveal = pantherRevealed(state);
  return (
    <section
      className={css.scene}
      data-panther-scene={state.scene}
      data-panther-task={task}
      data-panther-reference-state={reveal ? 'revealed' : 'hidden'}
    >
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' && <Input state={state} />}
      {state.scene === 'geometry' && <Geometry state={state} />}
      {state.scene === 'output' && <Output state={state} />}
      {state.scene === 'reference' && <Reference state={state} reveal={reveal} />}
      {state.scene === 'limits' && <Limits state={state} />}
    </section>
  );
}
export function RexPantherOutput({ state }: { state: RexPantherState }) {
  const { source } = pantherRecords(state);
  const task = pantherTask(state);
  const detail =
    state.scene === 'input'
      ? source.variant.modality + '; no source image in this pack.'
      : state.scene === 'geometry'
        ? 'Read image-specific MHA geometry before writing the mask.'
        : state.scene === 'output'
          ? 'CSV and binary MHA remain unfilled answer-owned fields.'
          : state.scene === 'reference'
            ? 'Private test label role only; no label asset or patient pixels.'
            : 'Metrics are defined by code, with no observed result.';
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-panther-output>
      <b>
        Task {task}: {source.variant.name}
      </b>
      <p>{detail}</p>
      <b>Answer-owned output</b>
      <p>None retained. No prediction, submission or score.</p>
      <b>Source boundary</b>
      <p>
        Official scans restricted; license statements unresolved.{' '}
        <a href={ACQUIRE}>Official access route ↗</a>
      </p>
      <small>Symbolic contract diagram · no clinical case illustration</small>
    </aside>
  );
}

import {
  automedInputs as src,
  automedReference as ref,
  automedContract as data,
  automedSelection,
  type AutomedState,
} from './automed-multiorgan';
import css from './automed-multiorgan.module.css';
const steps = [
  [
    'S1 · Research',
    'Choose the supplied TotalSegmentator model; inspect its label names and input conventions.',
  ],
  [
    'S2 · Set up',
    'Prepare the environment, checkpoints and writable caches from the supplied guidance.',
  ],
  [
    'S3 · Validate',
    'Try one case; check native shape, affine, integer IDs and missing structures.',
  ],
  ['S4 · Infer', 'Process every CT and save each patient’s completed label map.'],
  ['S5 · Submit', 'Return agents_outputs/<patient_id>/dseg.nii.gz and retain the work log.'],
];
const names: Record<string, string> = {
  exact: 'Exact toy labels',
  empty: 'All background',
  swapped: 'Kidneys swapped',
  shifted: 'Origin +100 mm',
  probability: 'One value = 42.5',
  missing_one: 'One of two missing',
  missing_all: 'Both missing',
};
function Native({
  index = 1,
  reveal = false,
  selected = 0,
}: {
  index?: number;
  reveal?: boolean;
  selected?: number;
}) {
  const v = src.views[index];
  return (
    <figure className={css.native}>
      <svg
        viewBox="0 0 333 336"
        role="img"
        aria-label={`Native coronal CT at y=${v.y}; right rightward, superior upward${reveal ? ', partial reader reference' : ''}`}
      >
        <image href={v.png} width="333" height="336" />
        {reveal &&
          ref.structures.map((r, i) => (
            <image
              key={r.name}
              data-automed-reference={r.name}
              href={r.png}
              width="333"
              height="336"
              opacity={i === selected ? 1 : 0.35}
            />
          ))}
        <g fill="white" fontSize="11">
          <text x="5" y="172">
            L
          </text>
          <text x="319" y="172">
            R
          </text>
          <text x="164" y="13">
            S
          </text>
        </g>
      </svg>
      <figcaption>
        <b>Native coronal y={v.y}</b>
        <span>333 × 336 pixels · −160 to 240 HU</span>
      </figcaption>
    </figure>
  );
}
function Toy({ empty = false }: { empty?: boolean }) {
  return (
    <svg
      className={css.toy}
      viewBox="0 0 240 80"
      role="img"
      aria-label="Nonclinical schematic: two occupied classes and 115 empty classes"
    >
      <rect x="3" y="3" width="74" height="74" fill="#eff2e9" stroke="#8da393" />
      <rect
        x="14"
        y="14"
        width="16"
        height="16"
        fill={empty ? '#eff2e9' : '#267f72'}
        stroke="#267f72"
      />
      <rect
        x="50"
        y="50"
        width="16"
        height="16"
        fill={empty ? '#eff2e9' : '#326fbb'}
        stroke="#326fbb"
      />
      <g fill="#294b3b" fontSize="12">
        <text x="92" y="26">
          2 occupied GT classes
        </text>
        <text x="92" y="48">
          115 empty GT classes
        </text>
        <text x="92" y="69">
          Author toy · no CT
        </text>
      </g>
    </svg>
  );
}
export function AutomedScene({ state: s }: { state: AutomedState }) {
  const i = automedSelection(s),
    reveal = s.scene === 'reference' && s.reference > 0.5;
  let title = '',
    body;
  switch (s.scene) {
    case 'inputs':
      title = 'A whole CT volume enters the pipeline';
      body = (
        <div className={css.columns}>
          <Native index={i} />
          <article>
            <p className={css.kicker}>TSG_00000001 · SOURCE s1366</p>
            <h4>333 × 333 × 336 voxels</h4>
            <p>1.5 mm isotropic · RAS world geometry</p>
            <p>One example from the 40-case Lite segmentation track.</p>
            <p className={css.callout}>
              These teaching planes were selected post hoc. The solver receives the CT volume, not a
              target slice or organ boundary.
            </p>
            <p>No prediction is shown.</p>
          </article>
        </div>
      );
      break;
    case 'workflow':
      title = 'Five stages organize the required work';
      body = (
        <>
          <div className={css.steps}>
            {steps.map(([name], j) => (
              <div key={name} data-current={i === j}>
                {name}
              </div>
            ))}
          </div>
          <article className={css.selected}>
            <h4>{steps[i][0]}</h4>
            <p>{steps[i][1]}</p>
          </article>
          <p>
            Lite supplies model guidance and requirements. The configured budget is 3,600 seconds.
          </p>
          <p className={css.callout}>
            Static contract walkthrough. No environment setup, model download, inference or agent
            trace is replayed.
          </p>
        </>
      );
      break;
    case 'remap':
      title = 'Match class names before writing integer IDs';
      body = (
        <>
          <table data-automed-remap>
            <thead>
              <tr>
                <th>Structure</th>
                <th>Model 2.4.0</th>
                <th>Benchmark</th>
              </tr>
            </thead>
            <tbody>
              {data.remap.map((r, j) => (
                <tr key={r.name} data-current={i === j}>
                  <td>{r.name}</td>
                  <td>{r.model_id}</td>
                  <td>{r.benchmark_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className={css.mapping}>
            <b>{data.remap[i].model_id}</b>
            <span>→ {data.remap[i].name} →</span>
            <b>{data.remap[i].benchmark_id}</b>
          </div>
          <p>
            Illustrative pinned TotalSegmentator 2.4.0 map. Requirements allow later versions;
            inspect the actual checkpoint’s label table.
          </p>
          <p className={css.callout}>A valid integer can still name the wrong structure.</p>
        </>
      );
      break;
    case 'geometry':
      title = 'Output labels must keep the CT’s native grid';
      body = (
        <div className={css.columns}>
          <Native />
          <article>
            <p className={css.kicker}>SINGLE OUTPUT · dseg.nii.gz</p>
            <h4>Integer values 0–117</h4>
            <p>0 is background. No probabilities or independent binary output files.</p>
            <pre>{`shape = (333, 333, 336)\nRAS spacing = 1.5 mm\norigin = (-249.512, -54.512, -896) mm`}</pre>
            <div className={css.selected} data-automed-geometry>
              {i === 0 ? (
                <>
                  <b>Preserve native geometry</b>
                  <p>Match shape, affine and active qform/sform.</p>
                </>
              ) : (
                <>
                  <b>Same array, shifted origin</b>
                  <p>A +100 mm toy shift fails format and gets zero Dice.</p>
                </>
              )}
            </div>
            <p>
              Use nearest-neighbor labels if mapping from another grid. No resampling is performed
              here.
            </p>
          </article>
        </div>
      );
      break;
    case 'reference':
      title = reveal
        ? 'Reveal five released reference masks'
        : 'References are separate from solver inputs';
      body = (
        <div className={css.columns}>
          <Native reveal={reveal} selected={i} />
          <article>
            <p className={css.kicker}>READER-ONLY REFERENCE REVEAL</p>
            {reveal ? (
              <>
                <h4 style={{ color: ref.structures[i].color, background: '#162b23', padding: 8 }}>
                  {ref.structures[i].name}
                </h4>
                <p>
                  Benchmark ID {ref.structures[i].benchmark_id} ·{' '}
                  {ref.structures[i].plane_voxels.toLocaleString('en-US')} voxels on this plane
                </p>
                <p>Selected mask bright; other retained masks dim.</p>
              </>
            ) : (
              <>
                <h4>CT only at chapter start</h4>
                <p>Continue playback to reveal the separately stored masks.</p>
              </>
            )}
            <div className={css.coverage}>
              <b>5 retained</b>
              <span>78 present per release CSV</span>
              <span>117 configured classes</span>
            </div>
            <p className={css.callout}>
              Partial ground truth, not a prediction. No full-case score is computed from this
              collection.
            </p>
          </article>
        </div>
      );
      break;
    case 'scoring':
      title = 'Inspect the denominator in the pinned scorer';
      body = (
        <>
          <div className={css.columns}>
            <article>
              <p className={css.kicker}>CONFIG WORDING</p>
              <h4>Nonempty references only</h4>
              <p>The task description claims averaging only classes with nonempty ground truth.</p>
            </article>
            <article>
              <p className={css.kicker}>IMPLEMENTED LOOP</p>
              <h4>All 117 classes</h4>
              <p>Dice(empty, empty) = 1. Every configured class enters the mean.</p>
            </article>
          </div>
          <div className={css.score}>
            <Toy empty={i === 1} />
            <div>
              <b>{i === 0 ? 'Exact toy: 117 / 117 = 1' : 'Empty toy: 115 / 117 = 0.9829'}</b>
              <p>
                Two occupied classes, 115 empty classes. This toy result is not anatomical
                performance.
              </p>
            </div>
          </div>
          <p className={css.callout}>
            The pinned code and nonclinical replay support the displayed rule. The contradictory
            prose is retained as a source discrepancy.
          </p>
        </>
      );
      break;
    case 'coverage':
      title = 'Keep validity, coverage and overlap separate';
      body = (
        <>
          <table data-automed-fixtures>
            <thead>
              <tr>
                <th>Nonclinical fixture</th>
                <th>Format</th>
                <th>Counted / 2</th>
                <th>Task Dice</th>
              </tr>
            </thead>
            <tbody>
              {data.examples.map((e, j) => (
                <tr key={e.id} data-current={i === j}>
                  <td>{names[e.id]}</td>
                  <td>{e.format_valid ? 'valid' : 'invalid'}</td>
                  <td>{e.completed} / 2</td>
                  <td>{e.task_score.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className={css.selected}>
            {i === 5
              ? 'One exact output: raw Dice 1 × coverage 1/2 = task score 0.5.'
              : i === 6
                ? 'Missing files leave format=true; completeness and task score are zero.'
                : i === 3 || i === 4
                  ? 'Malformed present outputs count in completeness but receive zero Dice.'
                  : i === 1 || i === 2
                    ? 'Wrong occupied classes still receive 115 empty-pair credits in this toy.'
                    : 'Exact means identical synthetic labels, not a medical prediction.'}
          </p>
          <p className={css.small}>
            Medal is assigned before coverage scaling. S1–S3 remain unscored in this deterministic
            path.
          </p>
        </>
      );
      break;
    case 'limits':
      title = 'What this explanation establishes';
      body = (
        <div className={css.cards}>
          <article>
            <b>Native source</b>
            <p>One CT and five masks match published hashes and share a native grid.</p>
          </article>
          <article>
            <b>Operational contract</b>
            <p>117 IDs, name-based remapping, geometry checks and per-patient outputs.</p>
          </article>
          <article>
            <b>Evaluator mechanics</b>
            <p>Seven nonclinical fixtures; all-class averaging and coverage scaling inspected.</p>
          </article>
          <article>
            <b>Still absent</b>
            <p>
              Full reference coverage, patient prediction, model trial, judge and runtime isolation
              audit.
            </p>
          </article>
        </div>
      );
      break;
  }
  return (
    <section className={css.scene} data-automed-scene={s.scene}>
      <h3>{title}</h3>
      {body}
    </section>
  );
}
export function AutomedOutput({ state: s }: { state: AutomedState }) {
  const headings = {
    inputs: 'Volume → label map',
    workflow: 'Follow the supplied condition',
    remap: 'Names anchor the conversion',
    geometry: 'A NIfTI is more than its array',
    reference: 'Reference boundary',
    scoring: 'Implementation differs from prose',
    coverage: 'Read several fields together',
    limits: 'Scope of this review',
  };
  const copy = {
    inputs: 'Forty cases are required by the task. One native case is illustrated here.',
    workflow: 'Model/version, cache paths, validation and submission are agent responsibilities.',
    remap: 'The five-row mapping is an example from a pinned version, not the full 117-class map.',
    geometry: 'Preserve origin, spacing, orientation and active forms alongside integer IDs.',
    reference:
      'These public-release reference files remain evaluator-owned material. Their display does not prove solver isolation.',
    scoring:
      'An empty-pair convention changes the meaning of a macro average. Do not equate the toy number with useful segmentation.',
    coverage:
      'Format can remain valid when files are missing. The final task score also depends on completeness.',
    limits:
      'This is a source-backed task explanation with bounded evaluator replay, not a capability result.',
  };
  return (
    <aside className={css.aside} data-automed-aside>
      <b>{headings[s.scene]}</b>
      <p>{copy[s.scene]}</p>
      <small>
        Pinned AutoMedBench Lite · 8928073d
        <br />
        CT/labels: CC BY 4.0 · no model run
      </small>
    </aside>
  );
}

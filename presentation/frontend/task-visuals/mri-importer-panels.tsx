import {
  mriInputs,
  mriOutput,
  mriReference,
  mriSelection,
  mriSlot,
  mriPoint,
  mriCorners,
  mriGray,
  type MriImporterState,
  type MriCase,
  type MriFrame,
} from './mri-importer';
import styles from './task-visual.module.css';
const shuffled = mriInputs.cases[1];
const fmt = (v: number) => v.toFixed(3);
function Samples({
  pixels,
  label,
  numbers = false,
}: {
  pixels: number[][];
  label: string;
  numbers?: boolean;
}) {
  const rows = pixels.length,
    cols = pixels[0].length,
    cell = numbers ? 48 : 12;
  return (
    <svg
      viewBox={`0 0 ${cols * cell} ${rows * cell}`}
      role="img"
      aria-label={label}
      className={numbers ? styles.mriSamplesLarge : styles.mriSamples}
    >
      {pixels.flatMap((row, r) =>
        row.map((v, c) => {
          const g = mriGray(v);
          return (
            <g key={`${r}-${c}`}>
              <rect
                x={c * cell}
                y={r * cell}
                width={cell}
                height={cell}
                fill={`rgb(${g},${g},${g})`}
              />
              {numbers && (
                <text
                  x={(c + 0.5) * cell}
                  y={(r + 0.55) * cell}
                  textAnchor="middle"
                  fontSize="10"
                  fill={g < 125 ? 'white' : '#111'}
                >
                  {v}
                </text>
              )}
            </g>
          );
        }),
      )}
    </svg>
  );
}
function FrameGrid({
  info,
  canonical,
  selected,
}: {
  info: MriCase;
  canonical: boolean;
  selected?: number;
}) {
  const frames = canonical
    ? [...info.rows].sort((a, b) => mriSlot(a, info.shape) - mriSlot(b, info.shape))
    : info.rows;
  return (
    <div className={styles.mriGrid} data-mri-grid={canonical ? 'canonical' : 'storage'}>
      {frames.map((f) => (
        <article
          key={f.storage}
          data-selected={f.storage === selected}
          data-target={f.target.join(',')}
          data-storage={f.storage}
        >
          <b>{canonical ? `[${f.target.join(',')}]` : `frame ${f.storage}`}</b>
          <Samples
            pixels={f.pixels}
            label={`Storage ${f.storage}, destination ${f.target.join(',')}`}
          />
          <small>
            t {f.time} · e {f.echo_ms}
          </small>
        </article>
      ))}
    </div>
  );
}
function PairInfo({ f }: { f: MriFrame }) {
  return (
    <p className={styles.mriWitness} data-mri-witness>
      Frame <b>{f.storage}</b> → pixels<b>[{f.target.join(',')}, :, :]</b> · actual time {f.time} ·
      echo {f.echo_ms} ms · slice projection {fmt(f.projection_mm)} mm
    </p>
  );
}
function Cards({ rows }: { rows: [string, string][] }) {
  return (
    <div className={styles.mriCards}>
      {rows.map(([title, body]) => (
        <article key={title}>
          <b>{title}</b>
          <p>{body}</p>
        </article>
      ))}
    </div>
  );
}
function Geometry({ corner }: { corner: number }) {
  const info = mriInputs.cases[3],
    affine = mriOutput.cases[3].affine_lps,
    corners = mriCorners(info.shape);
  const origin = mriPoint(affine, [0, 0, 0]);
  const project = (point: number[]) => {
    const [l, p, s] = point.map((v, i) => v - origin[i]);
    return [l - 0.5 * p, -s + 0.3 * p];
  };
  const raw = corners.map((p) => project(mriPoint(affine, p)));
  const xs = raw.map((p) => p[0]),
    ys = raw.map((p) => p[1]);
  const minX = Math.min(...xs),
    minY = Math.min(...ys),
    dx = Math.max(...xs) - minX,
    dy = Math.max(...ys) - minY;
  const scale = Math.min(230 / dx, 170 / dy),
    screen = raw.map(([x, y]) => [40 + (x - minX) * scale, 30 + (y - minY) * scale]);
  const edges = corners
    .flatMap((p, i) =>
      corners.map((q, j) => ({ i, j, differing: p.filter((v, a) => v !== q[a]).length })),
    )
    .filter((e) => e.j > e.i && e.differing === 1);
  const point = mriPoint(affine, corners[corner]);
  return (
    <>
      <div className={styles.mriPair}>
        <div>
          <svg
            viewBox="0 0 320 250"
            className={styles.mriGeometry}
            role="img"
            aria-label="Oblique acquisition corner diagram in LPS, projected for teaching"
          >
            {edges.map(({ i, j }) => (
              <line
                key={`${i}-${j}`}
                x1={screen[i][0]}
                y1={screen[i][1]}
                x2={screen[j][0]}
                y2={screen[j][1]}
                stroke="#91aaa6"
                strokeWidth="2"
              />
            ))}
            {screen.map(([x, y], i) => (
              <circle
                key={i}
                cx={x}
                cy={y}
                r={i === corner ? 7 : 3}
                fill={i === corner ? '#c97b18' : '#267f72'}
              />
            ))}
            <text x="12" y="237" fontSize="11" fill="currentColor">
              Projected pixel-centre corners · not anatomy
            </text>
          </svg>
        </div>
        <div>
          <b>Affine maps [column, row, slice, 1]</b>
          <pre>{affine.map((row) => row.map(fmt).join('  ')).join('\n')}</pre>
          <p>
            Column step = first IOP vector × column spacing.
            <br />
            Row step = second IOP vector × row spacing.
          </p>
          <p>
            PixelSpacing [row, column]:
            <br />
            <b>{info.spacing_row_column_mm.map(fmt).join(', ')} mm</b>
          </p>
        </div>
      </div>
      <p className={styles.mriWitness} data-mri-corner={corner}>
        [{corners[corner].join(', ')}] → LPS [{point.map(fmt).join(', ')}] mm
      </p>
      <p>
        Amber marks the selected corner; green marks the other corners. All eight are graded within
        10⁻⁵ mm. Display values are rounded; the calculation uses full precision.
      </p>
    </>
  );
}
function Results() {
  return (
    <div data-mri-private>
      <table className={styles.mriTable}>
        <thead>
          <tr>
            <th>Retained answer</th>
            <th>
              Ordered/
              <wbr />
              shared
            </th>
            <th>
              Shuffled/
              <wbr />
              shared
            </th>
            <th>
              Shuffled/
              <wbr />
              per-frame
            </th>
          </tr>
        </thead>
        <tbody>
          {[
            ['model', 'Terra/high'],
            ['oracle', 'Oracle'],
            ['starter', 'Starter / no-op'],
          ].map(([key, label]) => (
            <tr key={key}>
              <th>{label}</th>
              {[0, 1, 2].map((e) => (
                <td key={e}>
                  {
                    mriReference.results[key].report.passed.filter((n) =>
                      n.endsWith(`encoding-${e}`),
                    ).length
                  }
                  /12
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <p>
        <b>12 acquisitions × 3 correlated encodings = 36 fixtures.</b> One completed model attempt;
        reward 1 requires the complete batch to pass.
      </p>
      <p>
        The starter passes ordered data. On shuffled/shared inputs, eight shape checks and four
        sample-value checks fail. All twelve per-frame variants fail at geometry lookup.
      </p>
    </div>
  );
}
export function MriImporterScene({ state }: { state: MriImporterState }) {
  const sel = mriSelection(state),
    frame = shuffled.rows[sel.frame];
  let title = '',
    body;
  switch (state.scene) {
    case 'inputs':
      title = 'The pixels and their metadata move together';
      body = (
        <>
          <FrameGrid info={shuffled} canonical={false} />
          <p>
            Actual public-00 shuffled encoding: twelve 3 × 4 signed sample tiles. Each tile stays
            paired with its functional-group record. Grayscale window −3000…3000; these are
            synthetic numbers, not anatomy.
          </p>
        </>
      );
      break;
    case 'ordinals':
      title = 'Descriptor ordinals are not actual labels';
      body = (
        <>
          <table className={styles.mriTable}>
            <thead>
              <tr>
                <th>Descriptor order</th>
                <th>Logical ordinal → actual value</th>
              </tr>
            </thead>
            <tbody>
              {shuffled.descriptors.map((d, i) => (
                <tr key={d.keyword}>
                  <th>
                    {i + 1}. {d.keyword}
                  </th>
                  <td>
                    {Object.entries(d.ordinal_to_actual)
                      .map(([o, v]) => `${o} → ${v}`)
                      .join(' · ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <Cards
            rows={[
              [
                `Frame ${frame.storage}: ordinals [${frame.ordinals.join(',')}]`,
                `Actual time ${frame.time}; actual echo ${frame.echo_ms} ms; physical slice projection ${fmt(frame.projection_mm)} mm.`,
              ],
              [
                'Required sort',
                'Time and echo by actual values; slices by position dotted with the orientation normal. Storage order has no canonical meaning.',
              ],
            ]}
          />
        </>
      );
      break;
    case 'association':
      title = 'Route each intact sample tile to its canonical slot';
      body = (
        <>
          <div className={styles.mriPair}>
            <div>
              <b>Storage order · selected frame in amber</b>
              <FrameGrid info={shuffled} canonical={false} selected={sel.frame} />
            </div>
            <div>
              <b>Canonical [time, echo, slice] · green slot</b>
              <FrameGrid info={shuffled} canonical selected={sel.frame} />
            </div>
          </div>
          <PairInfo f={frame} />
          <p>
            Teaching traversal of all twelve original frames; no interpolation, averaging or
            simulated solver iterations.
          </p>
        </>
      );
      break;
    case 'geometry':
      title = 'Keep the sample coordinate and its LPS point together';
      body = <Geometry corner={sel.corner} />;
      break;
    case 'placement':
      title = 'The same geometry macro can live in either location';
      body = (
        <>
          <Cards
            rows={[
              [
                'Shared placement',
                'One PlaneOrientationSequence and PixelMeasuresSequence in SharedFunctionalGroupsSequence.',
              ],
              [
                'Per-frame placement',
                'The same constant geometry is repeated in each PerFrameFunctionalGroupsSequence item.',
              ],
            ]}
          />
          <p>
            The contract forbids a macro appearing in both locations. The saved repair looks in both
            permitted locations and associates each pixel tile with its own time, echo and position.
          </p>
          <p className={styles.mriWitness}>
            Input-legal public relocation: samples and labels unchanged; maximum corner error{' '}
            {mriOutput.relocation.max_landmark_error_mm.toExponential(2)} mm.
          </p>
          <p>
            This is a replay of the trace’s public-data check, separate from the private evaluation.
          </p>
        </>
      );
      break;
    case 'outputs':
      title = 'Return the canonical array and its coordinate map';
      body = sel.output ? (
        <>
          <div className={styles.mriPair}>
            <div>
              <Samples
                pixels={mriOutput.cases[1].pixels[0][0][0]}
                label="Replayed canonical first frame exact signed samples"
                numbers
              />
              <small>Replay of saved code · public-00 · pixels[0,0,0,:,:]</small>
            </div>
            <div>
              <pre>
                {
                  'pixels: [2, 2, 3, 3, 4]\ntemporal_indices: [11, 20]\necho_ms: [17.5, 21.25]\naffine_lps: [4, 4]'
                }
              </pre>
              <p>
                Singleton time/echo axes must stay present. A sorted list of labels alone does not
                repair the sample associations.
              </p>
            </div>
          </div>
          <p>
            All displayed sample values come from the retained public fixture and match its supplied
            expected array exactly.
          </p>
        </>
      ) : (
        <p>Awaiting the saved-code output reveal.</p>
      );
      break;
    case 'reference':
      title = sel.reference
        ? 'The saved repair passes every retained encoding'
        : 'The private batch remains separate from public examples';
      body = sel.reference ? (
        <Results />
      ) : (
        <Cards
          rows={[
            [
              'Solver-visible',
              'Four public inputs and expected outputs, the adapter, starter and exact metadata profile.',
            ],
            [
              'Private evaluator',
              'Twelve separate acquisitions in three encodings each. The original canonical arrays precede serialization.',
            ],
          ]}
        />
      );
      break;
    case 'controls':
      title = 'Different mistakes fail different invariants';
      body = (
        <>
          <table className={styles.mriTable} data-mri-controls>
            <thead>
              <tr>
                <th>Offline diagnostic</th>
                <th>Pass</th>
                <th>What it isolates</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Swap row/column spacing</td>
                <td>3/36</td>
                <td>Only three encodings of the isotropic control survive.</td>
              </tr>
              <tr>
                <td>Return logical echo ordinals</td>
                <td>0/36</td>
                <td>Actual echo times differ from ordinal labels.</td>
              </tr>
              <tr>
                <td>Keep storage reshape</td>
                <td>12/36</td>
                <td>Only ordered/shared encodings pass.</td>
              </tr>
            </tbody>
          </table>
          <p>
            These are saved-code or modified-output diagnostics, not additional model attempts.
            Exact samples, labels and physical corners test complementary obligations.
          </p>
        </>
      );
      break;
    case 'trace':
      title = 'A strict equality failure was numerical, not lost association';
      body = (
        <>
          <Cards
            rows={[
              [
                'Step 16: exact dictionary equality',
                'The relocated public example fails Python’s exact comparison; the four standard public examples still pass.',
              ],
              [
                'Step 17: inspect each output',
                'Samples and labels differ by zero. The maximum affine entry difference is 2.95 × 10⁻¹³.',
              ],
            ]}
          />
          <p className={styles.mriWitness}>
            Replayed maximum physical corner error: 2.98 × 10⁻¹³ mm; frozen bound: 10⁻⁵ mm.
          </p>
          <p>
            The retained private verifier later reports 36/36. This explanation preserves the
            intermediate assertion failure and the final pass.
          </p>
        </>
      );
      break;
    case 'limits':
      title = 'A successful bounded importer repair';
      body = (
        <>
          <Cards
            rows={[
              [
                'Observed',
                'One completed Terra/high repair passes all 36 private fixtures from 12 acquisitions.',
              ],
              [
                'Scope',
                'Synthetic signed samples, one stack, complete acquisition, constant geometry, uncompressed pixels.',
              ],
              [
                'Unresolved beyond this task',
                'Full clinical DICOM conformance, missing or duplicate planes, multiple stacks and real-world robustness.',
              ],
            ]}
          />
          <p>
            The proposed failure hypothesis is not supported by this trial. The user parked the
            study; this explainer launches no new attempt.
          </p>
        </>
      );
      break;
  }
  return (
    <section
      className={styles.mriScene}
      data-mri-scene={state.scene}
      data-mri-reference={sel.reference ? 'visible' : 'hidden'}
    >
      <h4>{title}</h4>
      {body}
    </section>
  );
}
export function MriImporterOutput({ state }: { state: MriImporterState }) {
  const sel = mriSelection(state),
    f = shuffled.rows[sel.frame];
  return (
    <aside className={styles.mriAside}>
      <b>Canonical reconstruction contract</b>
      <p>pixels[time, echo, slice, row, column]</p>
      <p>affine_lps × [column,row,slice,1] → LPS mm</p>
      <p>Actual time/echo labels sorted numerically. Slice order follows the orientation normal.</p>
      {state.scene === 'geometry' ? (
        <>
          <b>Public oblique fixture</b>
          <p>
            public-01 · shape [1,2,3,5,5]
            <br />
            Selected corner [{mriCorners(mriInputs.cases[3].shape)[sel.corner].join(',')}]
          </p>
        </>
      ) : (
        <>
          <b>Public fixture witness</b>
          <p>
            Frame {f.storage} → [{f.target.join(',')}]<br />
            Time {f.time} · echo {f.echo_ms} ms
          </p>
        </>
      )}
      <p>Supplied public expected outputs are available to the solver.</p>
      {sel.output && (
        <p data-mri-output>
          Saved-code replay preserves all sample values. Local replay is not a new model run.
        </p>
      )}
      {sel.reference && (
        <p data-mri-private>
          <b>Private retained result</b>
          <br />
          Terra/high 36/36 · oracle 36/36
          <br />
          Starter 12/36
          <br />
          12 acquisitions; one model attempt.
        </p>
      )}
      <small>
        Synthetic fixture data · no patient images
        <br />
        Amber = selected frame/corner; green = canonical slot/corner.
      </small>
    </aside>
  );
}

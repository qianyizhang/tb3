import {
  materialColors as color,
  materialFrame,
  materialMethod,
  materialOutput,
  materialReference,
  materialReveal,
  materialSource,
  type CardiacMaterialState,
  type MaterialMethod,
  type Point3,
} from './cardiac-material';
import sharedStyles from './task-visual.module.css';
import styles from './cardiac-material.module.css';

const sub = (a: Point3, b: Point3): Point3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const project = (p: Point3): [number, number] => [
  150 + 2.1 * (p[0] - 145 + 0.38 * (p[1] + 48)),
  145 - 2.1 * (p[2] - 160 - 0.2 * (p[1] + 48)),
];
const fmt = (v: number | null, n = 2) => (v == null ? 'unavailable' : v.toFixed(n));

function ImagePanel({
  frame,
  view,
  seeds,
}: {
  frame: number;
  view: number;
  seeds?: [number, number][];
}) {
  const plane = materialSource.views[view];
  return (
    <figure
      className={styles.card}
      data-material-source-image
      data-material-frame={frame + 1}
      data-material-view={view}
    >
      <figcaption>
        {plane.name} · native frame {frame + 1}/30
      </figcaption>
      <svg
        className={styles.image}
        viewBox="0 0 192 192"
        role="img"
        aria-label={`${plane.name} synthetic ultrasound, frame ${frame + 1}`}
      >
        <image href={plane.images[frame]} x="0" y="0" width="192" height="192" />
        {seeds?.map(([x, y], i) => (
          <circle
            key={i}
            cx={x}
            cy={y}
            r="1.5"
            fill={color.affine}
            stroke="#091c25"
            strokeWidth=".4"
            data-material-tracked-seed
          />
        ))}
      </svg>
    </figure>
  );
}

function MeshPanel({
  points,
  title,
  colorValue,
  initial = false,
  selected,
  referencePoints,
}: {
  points: Point3[];
  title: string;
  colorValue: string;
  initial?: boolean;
  selected?: Point3[];
  referencePoints?: Point3[];
}) {
  const edges = [
    [0, 1],
    [0, 2],
    [0, 3],
    [1, 2],
    [1, 3],
    [2, 3],
  ];
  return (
    <figure
      className={styles.card}
      data-material-input-mesh={initial ? 'initial' : undefined}
      data-material-output={initial ? undefined : 'saved'}
    >
      <figcaption>{title}</figcaption>
      <svg
        className={styles.mesh}
        viewBox="0 0 300 290"
        role="img"
        aria-label="Fixed millimetre projection of sampled material vertices"
      >
        <text x="8" y="17">
          Fixed camera · native mm
        </text>
        <path d="M18 263h34m-34 0v-34" stroke="#738e9c" strokeWidth="1" />
        <text x="55" y="266">
          ~16 mm
        </text>
        <path
          d={points
            .map((p) => {
              const [x, y] = project(p);
              return `M${(x - 1.6).toFixed(3)} ${(y - 1.6).toFixed(3)}h3.2v3.2h-3.2Z`;
            })
            .join('')}
          fill={colorValue}
          shapeRendering="crispEdges"
        />
        {referencePoints && (
          <path
            d={referencePoints
              .map((p) => {
                const [x, y] = project(p);
                return `M${(x - 1.2).toFixed(3)} ${(y - 1.2).toFixed(3)}h2.4v2.4h-2.4Z`;
              })
              .join('')}
            fill={color.reference}
            shapeRendering="crispEdges"
            data-material-reference
          />
        )}
        {selected &&
          edges.map(([a, b], i) => {
            const [x1, y1] = project(selected[a]);
            const [x2, y2] = project(selected[b]);
            return (
              <line
                key={i}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke="#f1f8fb"
                strokeWidth="1.8"
                data-material-tetra
              />
            );
          })}
        {selected?.map((p, i) => {
          const [x, y] = project(p);
          return <circle key={i} cx={x} cy={y} r="3" fill="#f1f8fb" />;
        })}
      </svg>
    </figure>
  );
}

const tetraFrames = [
  materialSource.tetra.initial_vertices_mm,
  ...materialOutput.methods.video_affine.tetra_vertices_mm,
  ...materialOutput.methods.tissue_fit.tetra_vertices_mm,
];
const edgeProjection = (p: Point3): [number, number] => [p[0] + 0.38 * p[1], -(p[2] - 0.2 * p[1])];
const tetraScale =
  78 /
  Math.max(
    ...tetraFrames.flatMap((points) =>
      points.flatMap((p) => edgeProjection(sub(p, points[0])).map(Math.abs)),
    ),
  );
function TetraComparison({ frame, method }: { frame: number; method: MaterialMethod }) {
  const initial = materialSource.tetra.initial_vertices_mm;
  const current = materialOutput.methods[method].tetra_vertices_mm[frame];
  const position = (p: Point3, origin: Point3) =>
    edgeProjection(sub(p, origin)).map((v, i) => (i === 0 ? 140 : 115) + tetraScale * v);
  return (
    <figure className={styles.card} data-material-tetra>
      <figcaption>Cell {materialSource.tetra.id}: same four material IDs</figcaption>
      <svg
        className={styles.tetraFigure}
        viewBox="0 0 300 230"
        role="img"
        aria-label="Magnified retained tetrahedron, reference dashed and saved current solid; translation removed, fixed millimeter scale"
      >
        {[initial, current].map((points, kind) => (
          <g
            key={kind}
            fill="none"
            stroke={kind ? color.tissue : color.input}
            strokeWidth={kind ? 2.3 : 1.6}
            strokeDasharray={kind ? undefined : '5 3'}
          >
            {[
              [0, 1],
              [0, 2],
              [0, 3],
              [1, 2],
              [1, 3],
              [2, 3],
            ].map(([a, b], i) => {
              const x = position(points[a], points[0]),
                y = position(points[b], points[0]);
              return <line key={i} x1={x[0]} y1={x[1]} x2={y[0]} y2={y[1]} />;
            })}
            {points.map((p, i) => {
              const v = position(p, points[0]);
              return <circle key={i} cx={v[0]} cy={v[1]} r={kind ? 3 : 4} />;
            })}
          </g>
        ))}
        {current.map((p, i) => {
          const v = position(p, current[0]);
          return (
            <text key={i} x={v[0] + 5} y={v[1] - 5}>
              {i}
            </text>
          );
        })}
        <text x="10" y="16">
          Gray dashed: supplied · cyan solid: saved
        </text>
        <text x="10" y="210">
          Vertex 0 aligned; translation removed.
        </text>
        <text x="10" y="224">
          Common scale: {tetraScale.toFixed(1)} display units/mm.
        </text>
      </svg>
    </figure>
  );
}

function TetraFields({ frame, method }: { frame: number; method: MaterialMethod }) {
  const fields = materialOutput.methods[method];
  const matrix = (a: number[][]) =>
    a.map((row) => row.map((v) => v.toFixed(2).padStart(6)).join(' ')).join('\n');
  const values = fields.engineering_strain[frame];
  return (
    <div className={styles.tensor} data-material-strain data-material-method={method}>
      <div>
        <strong>F · edge deformation</strong>
        <code>{matrix(fields.F[frame])}</code>
      </div>
      <div>
        <strong>E · Green–Lagrange, fraction</strong>
        <code>{matrix(fields.E_green_lagrange[frame])}</code>
      </div>
      <div>
        <strong>Engineering strain · longitudinal / circumferential / radial</strong>
        <code>{values.map((v) => (v == null ? '—' : `${(v * 100).toFixed(1)}%`)).join(' / ')}</code>
      </div>
      <div>
        <strong>J = det F</strong>
        <code>{fields.J[frame].toFixed(3)} · dimensionless</code>
      </div>
    </div>
  );
}

function Curve({
  frame,
  method,
  reveal,
}: {
  frame: number;
  method: MaterialMethod;
  reveal: boolean;
}) {
  const selected = materialOutput.methods[method].global_engineering_percent.map((row) => row[2]);
  const other = materialOutput.methods[
    method === 'video_affine' ? 'tissue_fit' : 'video_affine'
  ].global_engineering_percent.map((row) => row[2]);
  const reference = materialReference.global_engineering_percent.map((row) => row[2]);
  const x = (i: number) => 40 + i * (312 / 29);
  const y = (v: number) => 145 - (v + 25) * (120 / 55); // Fixed -25..+30% scale.
  const line = (a: number[]) =>
    a.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ');
  return (
    <svg
      className={styles.curve}
      viewBox="0 0 370 180"
      role="img"
      aria-label="Mean radial engineering strain over cells with usable anatomical axes, fixed percentage scale over 30 frames"
    >
      <path d="M40 19V145H352" fill="none" stroke="#597580" />
      {[-20, -10, 0, 10, 20, 30].map((v) => (
        <g key={v}>
          <path d={`M40 ${y(v)}H352`} stroke="#dce6e8" />
          <text x="35" y={y(v) + 3} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      <text x="4" y="12">
        %
      </text>
      <text x="40" y="163">
        1
      </text>
      <text x="352" y="163" textAnchor="end">
        30
      </text>
      <path
        d={line(other)}
        fill="none"
        stroke={method === 'video_affine' ? color.tissue : color.affine}
        strokeWidth="1.6"
        opacity=".7"
      />
      <path
        d={line(selected)}
        fill="none"
        stroke={method === 'video_affine' ? color.affine : color.tissue}
        strokeWidth="2.6"
      />
      {reveal && (
        <path
          d={line(reference)}
          fill="none"
          stroke={color.reference}
          strokeWidth="2.2"
          strokeDasharray="5 3"
          data-material-reference
        />
      )}
      <path d={`M${x(frame)} 19V145`} stroke="#566e77" strokeWidth="1" />
      <circle
        cx={x(frame)}
        cy={y(selected[frame])}
        r="3.5"
        fill={method === 'video_affine' ? color.affine : color.tissue}
      />
    </svg>
  );
}

export function CardiacMaterialScene({ state }: { state: CardiacMaterialState }) {
  const frame = materialFrame(state.phase);
  const reveal = materialReveal(state);
  const method = materialMethod(state.scene);
  const output = state.output > 0.5 && state.scene !== 'inputs' && state.scene !== 'initial';
  const showBody = ['tetra', 'comparison', 'controls', 'limits'].includes(state.scene);
  const samples = materialOutput.methods[method];
  const imageView = state.scene === 'tracking' ? 1 : state.scene === 'strain' ? 3 : 0;
  const title =
    state.scene === 'inputs'
      ? 'Four fixed ultrasound planes are observed'
      : state.scene === 'initial'
        ? 'The material IDs and tetrahedra start supplied'
        : state.scene === 'tracking'
          ? 'Near-plane seeds constrain one video-affine motion'
          : state.scene === 'tetra'
            ? 'One fixed tetrahedron changes its edges'
            : state.scene === 'strain'
              ? 'Saved deformation yields tensor and directional fields'
              : state.scene === 'comparison'
                ? 'Two saved methods, one hidden material reference'
                : state.scene === 'controls'
                  ? 'Volume agreement does not establish tracking'
                  : 'One simulated heart; no clinical strain claim';
  return (
    <div
      className={styles.scene}
      data-material-scene={state.scene}
      data-material-frame={frame + 1}
      data-material-view={imageView}
      data-material-method={method}
      data-material-reference-state={reveal ? 'revealed' : 'hidden'}
    >
      <div className={styles.head}>
        <strong>{title}</strong>
        <span>BR-029 · healthy simulator · frame {frame + 1}/30</span>
      </div>
      {state.scene === 'inputs' && (
        <div className={styles.grid}>
          {[0, 1, 2, 3].map((view) => (
            <ImagePanel key={view} frame={frame} view={view} />
          ))}
        </div>
      )}
      {state.scene === 'initial' && (
        <div className={styles.grid}>
          <ImagePanel frame={0} view={0} />
          <MeshPanel
            points={materialSource.initial_points_mm}
            title="Supplied frame-1 material mesh · fixed IDs"
            colorValue={color.input}
            initial
            selected={materialSource.tetra.initial_vertices_mm}
          />
        </div>
      )}
      {state.scene === 'tracking' && (
        <div className={styles.grid}>
          <ImagePanel
            frame={frame}
            view={1}
            seeds={output ? samples.tracked_seed_projected_pixels[1][frame] : undefined}
          />
          {output && (
            <MeshPanel
              points={samples.sample_points_mm[frame]}
              title="Saved video-affine position · same material IDs"
              colorValue={color.affine}
            />
          )}
        </div>
      )}
      {showBody && (
        <div className={styles.grid}>
          {state.scene === 'tetra' ? (
            <TetraComparison frame={frame} method={method} />
          ) : (
            <MeshPanel
              points={materialSource.initial_points_mm}
              title={
                state.scene === 'controls'
                  ? 'Static control: supplied frame-1 body'
                  : 'Supplied initial body · frame 1'
              }
              colorValue={color.input}
              initial
              selected={materialSource.tetra.initial_vertices_mm}
            />
          )}
          {output && (
            <MeshPanel
              points={samples.sample_points_mm[frame]}
              title={`Saved ${method === 'tissue_fit' ? 'tissue fit' : 'video affine'} · frame ${frame + 1}`}
              colorValue={method === 'tissue_fit' ? color.tissue : color.affine}
              selected={samples.tetra_vertices_mm[frame]}
              referencePoints={reveal ? materialReference.sample_points_mm[frame] : undefined}
            />
          )}
        </div>
      )}
      <div className={styles.key}>
        <span>
          <i style={{ background: color.input }} />
          supplied mesh
        </span>
        {output && (
          <span>
            <i style={{ background: method === 'tissue_fit' ? color.tissue : color.affine }} />
            saved motion
          </span>
        )}
        {reveal && (
          <span>
            <i style={{ background: color.reference }} />
            simulator reference · reader only
          </span>
        )}
      </div>
      {state.scene === 'inputs' && (
        <p className={styles.note}>
          120 source-derived grayscale frames at 0.75 mm/pixel. Later source meshes and strain are
          hidden from the solver. Four views are not a full 3D motion field.
        </p>
      )}
      {state.scene === 'initial' && (
        <p className={styles.note}>
          The input already includes 11,370 named material points and 47,186 tetrahedra in
          millimetres. This task estimates their later positions; it does not construct a mesh from
          scratch.
        </p>
      )}
      {state.scene === 'tracking' && (
        <p className={styles.step}>
          Saved video-affine fit: initial seeds lie within 1.5 mm of the four planes. Cyan dots are
          projected positions from the retained global affine result, not measured optical-flow
          truth. The remaining 3D body follows one 12-parameter map.
        </p>
      )}
      {state.scene === 'tetra' && output && (
        <div className={styles.step} data-material-tetra>
          For tetrahedron {materialSource.tetra.id}, Dm uses its frame-1 edge columns and Ds uses
          the same four vertex IDs at frame {frame + 1}. F = Ds Dm⁻¹. The fixed display projection
          uses the same millimetre scale at every frame.
        </div>
      )}
      {state.scene === 'strain' && output && (
        <>
          <div className={styles.grid}>
            <TetraComparison frame={frame} method="tissue_fit" />
            <TetraFields frame={frame} method="tissue_fit" />
          </div>
          <p className={styles.note}>
            Directional engineering strain is ||F e||−1; the displayed E is the full Green–Lagrange
            tensor. This saved kinematic fit is not force-balanced mechanics.
          </p>
          <div className={styles.warn} data-material-missing-axis>
            Cell {materialSource.missing_axis_cell.id} has AHA{' '}
            {materialSource.missing_axis_cell.aha} and J={samples.missing_axis.J[frame].toFixed(3)},
            but its three directions are unavailable—never zero strain.
          </div>
        </>
      )}
      {state.scene === 'comparison' && (
        <p className={styles.step}>
          The video-affine and development-informed tissue fits use the same four images, but
          different model assumptions. The gold simulator trajectory appears only after reader
          reference reveal. This endpoint contrast is not a controlled causal ablation.
        </p>
      )}
      {state.scene === 'controls' && (
        <p className={styles.step}>
          Static geometry changes no material point; its tissue-volume error is only 1.87%, while
          material displacement RMSE is 6.19 mm. A plausible volume curve can miss true motion.
        </p>
      )}
      {state.scene === 'limits' && (
        <p className={styles.note}>
          One healthy simulation, 30 correlated frames. Three positive-AHA cells lack usable axes.
          Tissue volume is not cavity EF. Physical frame duration, measured patient strain, force
          balance, blood flow and diagnosis are unavailable.
        </p>
      )}
    </div>
  );
}

export function CardiacMaterialOutput({ state }: { state: CardiacMaterialState }) {
  const frame = materialFrame(state.phase);
  const reveal = materialReveal(state);
  const method = materialMethod(state.scene);
  const visible = state.output > 0.5 && !['inputs', 'initial'].includes(state.scene);
  if (!visible)
    return (
      <aside
        className={`${sharedStyles.storyOutput} ${styles.output}`}
        data-material-output-panel="hidden"
      >
        <h3>Output withheld</h3>
        <p>The first read contains only supplied images and initial material anatomy.</p>
      </aside>
    );
  const selected = materialOutput.methods[method];
  const radial = selected.global_engineering_percent[frame][2];
  const showScores = reveal && ['controls', 'limits'].includes(state.scene);
  return (
    <aside
      className={`${sharedStyles.storyOutput} ${styles.output}`}
      data-material-output-panel="visible"
    >
      <h3>
        {method === 'video_affine' ? 'Video-affine motion' : 'Coupled tissue fit'} · saved output
      </h3>
      <p>
        Frame {frame + 1}: global radial engineering strain {radial.toFixed(1)}% · tissue volume{' '}
        {selected.tissue_volume_ml[frame].toFixed(1)} mL.
      </p>
      {!showScores && <Curve frame={frame} method={method} reveal={reveal} />}
      <p>
        {showScores
          ? 'Metrics: 30 frames × 11,370 material points; directional errors use 31,241 cells with usable anatomical axes.'
          : `Blue: video affine · cyan: tissue fit ${reveal ? '· dashed gold: simulator reference' : '· reference hidden'}.`}
      </p>
      {showScores && (
        <table className={styles.metrics} data-material-reference>
          <thead>
            <tr>
              <th>Retained method</th>
              <th>Material RMSE</th>
              <th>Radial MAE</th>
              <th>Tissue-volume error</th>
            </tr>
          </thead>
          <tbody>
            {(['static', 'video_affine', 'tissue_fit'] as const).map((key) => {
              const m = materialReference.metrics[key];
              return (
                <tr key={key}>
                  <td>{key.replace('_', ' ')}</td>
                  <td>{fmt(m.rmse_mm)} mm</td>
                  <td>{m.directional_mae_pp ? `${fmt(m.directional_mae_pp[2])} pp` : '—'}</td>
                  <td>{fmt(m.tissue_volume_error_percent)}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
      {state.scene === 'limits' && (
        <p className={styles.warn}>
          No saved method passes all provisional targets; reference scores are from one simulator
          case and do not validate clinical strain.
        </p>
      )}
    </aside>
  );
}

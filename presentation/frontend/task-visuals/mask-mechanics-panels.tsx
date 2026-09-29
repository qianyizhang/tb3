import {
  mmColors as color,
  mmCondition,
  mmFrame,
  mmOutput as answer,
  mmReference as reference,
  mmReveal,
  mmSource as input,
  type MaskMechanicsState,
} from './mask-mechanics';
import css from './mask-mechanics.module.css';
import shared from './task-visual.module.css';

const shape = [
  [85, 81],
  [85, 86],
  [81, 86],
];
const clinicalShape = [
  [63, 55],
  [63, 90],
  [55, 90],
];
const centre = [143.4, -47.8, 158.6];

function Slice({
  index,
  frame,
  image = false,
  output = false,
  clinical = false,
  condition,
}: {
  index: number;
  frame: number;
  image?: boolean;
  output?: boolean;
  clinical?: boolean;
  condition?: 'masks' | 'masks-images';
}) {
  const [w, h] = (clinical ? clinicalShape : shape)[index];
  const mask = clinical
    ? input.clinical.mask_png[index][frame]
    : input.input_masks_png[index][frame];
  const background = !clinical && image ? input.input_images_png[index][frame] : undefined;
  const contour = !clinical ? input.input_contours_px[index][frame] : undefined;
  const section =
    output && condition ? answer.conditions[condition].saved_sections_px[index][frame] : undefined;
  const axis = index === 0 ? 'X ↔ / Y ↕' : index === 1 ? 'X ↔ / Z ↕' : 'Y ↔ / Z ↕';
  const label = clinical
    ? ['Axial cavity', 'Coronal cavity', 'Sagittal cavity'][index]
    : input.views[index];
  return (
    <figure
      className={css.slice}
      data-mask-mechanics-clinical-cavity={clinical ? 'input' : undefined}
    >
      <svg
        viewBox={`0 0 ${w} ${h}`}
        role="img"
        aria-label={`${label}, native 1.5 mm voxel grid${output ? ', saved mesh section and supplied mask' : ''}`}
      >
        {background && (
          <image data-mask-mechanics-input-image href={background} width={w} height={h} />
        )}
        <image data-mask-mechanics-input-mask href={mask} width={w} height={h} />
        {output && contour && (
          <path
            d={contour}
            stroke={color.input}
            strokeDasharray="2 1.5"
            strokeWidth=".7"
            fill="none"
          />
        )}
        {section && (
          <path
            data-mask-mechanics-saved-occupancy
            d={section}
            stroke={color.output}
            strokeWidth=".8"
            fill="none"
          />
        )}
      </svg>
      <figcaption>
        {label}
        <small>{axis} · 1.5 mm/voxel</small>
      </figcaption>
    </figure>
  );
}

const project = (point: number[]) => {
  const x = point[0] - centre[0],
    y = point[1] - centre[1],
    z = point[2] - centre[2];
  return [150 + 1.75 * (x + 0.35 * z), 112 - 1.75 * (y - 0.2 * z)];
};

function MeshCloud({ frame, condition }: { frame: number; condition: 'masks' | 'masks-images' }) {
  const data = answer.conditions[condition];
  const tetra = data.selected_vertices_mm[frame];
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
      className={css.mesh}
      data-mask-mechanics-initial-mesh={frame === 0 ? 'answer-owned' : undefined}
    >
      <svg
        viewBox="0 0 300 225"
        role="img"
        aria-label={`Fixed millimetre projection of sampled saved answer vertices, phase ${frame}, selected tetrahedron highlighted`}
      >
        <path
          data-mask-mechanics-saved-output
          d={data.sampled_points_mm[frame]
            .map((p) => {
              const [x, y] = project(p);
              return `M${(x - 0.7).toFixed(3)} ${(y - 0.7).toFixed(3)}h1.4v1.4h-1.4Z`;
            })
            .join('')}
          fill={color.output}
          shapeRendering="crispEdges"
        />
        {edges.map(([a, b], i) => {
          const [x1, y1] = project(tetra[a]);
          const [x2, y2] = project(tetra[b]);
          return (
            <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#ffdfa4" strokeWidth="1.2" />
          );
        })}
        <path d="M14 202H49M14 202V167" className={css.axis} />
        <text x="54" y="205">
          20 mm
        </text>
      </svg>
      <figcaption>
        Saved answer vertices · sampled 1 in 96
        <small>Fixed oblique task-mm projection; selected tetra {data.selected_cell_index}</small>
      </figcaption>
    </figure>
  );
}

// One fixed display scale across both answers and every phase; align vertex 0 only.
const tetraLocal = (pts: number[][]) =>
  pts.map((p) => {
    const q = p.map((v, i) => v - pts[0][i]);
    return [q[0] + 0.35 * q[2], -q[1] + 0.25 * q[2]];
  });
const allTetra = Object.values(answer.conditions).flatMap((c) =>
  c.selected_vertices_mm.flatMap(tetraLocal),
);
const tetraX = allTetra.map((p) => p[0]),
  tetraY = allTetra.map((p) => p[1]);
const tetraBounds = [
  Math.min(...tetraX),
  Math.max(...tetraX),
  Math.min(...tetraY),
  Math.max(...tetraY),
];
const tetraScale = Math.min(
  135 / (tetraBounds[1] - tetraBounds[0]),
  125 / (tetraBounds[3] - tetraBounds[2]),
);

function TetraPair({ frame, condition }: { frame: number; condition: 'masks' | 'masks-images' }) {
  const d = answer.conditions[condition],
    p0 = d.selected_vertices_mm[0],
    pt = d.selected_vertices_mm[frame];
  const edges = [
    [0, 1],
    [0, 2],
    [0, 3],
    [1, 2],
    [1, 3],
    [2, 3],
  ];
  const draw = (pts: number[][], dx: number) =>
    tetraLocal(pts).map(([x, y]) => [
      dx + tetraScale * (x - (tetraBounds[0] + tetraBounds[1]) / 2),
      105 + tetraScale * (y - (tetraBounds[2] + tetraBounds[3]) / 2),
    ]);
  const first = draw(p0, 85),
    current = draw(pt, 265);
  return (
    <figure className={css.tetra} data-mask-mechanics-tetra={d.selected_cell_index}>
      <svg
        viewBox="0 0 360 210"
        role="img"
        aria-label={`Actual selected tetra ${d.selected_cell_index}, phase zero and ${frame}, fixed local ${tetraScale.toFixed(1)} display units per millimetre`}
      >
        {[
          { points: first, stroke: '#9daec2' },
          { points: current, stroke: color.output },
        ].map((s, group) => (
          <g key={group}>
            {edges.map(([a, b], i) => (
              <line
                key={i}
                x1={s.points[a][0]}
                y1={s.points[a][1]}
                x2={s.points[b][0]}
                y2={s.points[b][1]}
                stroke={s.stroke}
                strokeWidth="2"
              />
            ))}
            {s.points.map(([x, y], i) => (
              <circle key={i} cx={x} cy={y} r="3" fill={s.stroke} />
            ))}
          </g>
        ))}
        <text x="35" y="26">
          initial answer Dm
        </text>
        <text x="215" y="26">
          phase {frame} Ds
        </text>
        <text x="24" y="185">
          Same zoom: {tetraScale.toFixed(1)} display units/mm · vertex 0 aligned
        </text>
      </svg>
      <figcaption>
        Gray: initial answer edges; cyan: current edges. The same four saved IDs define Dm and Ds.
      </figcaption>
    </figure>
  );
}

function Matrix({ frame, condition }: { frame: number; condition: 'masks' | 'masks-images' }) {
  const d = answer.conditions[condition];
  const grid = (matrix: number[][]) => (
    <div className={css.matrix}>
      {matrix.map((row, i) => row.map((v, j) => <span key={`${i}-${j}`}>{v.toFixed(3)}</span>))}
    </div>
  );
  return (
    <div className={css.tensor} data-mask-mechanics-tensor>
      <strong>
        Saved fields · tetra {d.selected_cell_index} · phase {frame}
      </strong>
      <div className={css.tensorCols}>
        <div>
          <b>F = Ds Dm⁻¹</b>
          {grid(d.selected_F[frame])}
          <small>dimensionless</small>
        </div>
        <div>
          <b>E = (FᵀF − I)/2</b>
          {grid(d.selected_E_fraction[frame])}
          <small>fractional Green–Lagrange</small>
        </div>
      </div>
      <p>
        J = det F = <b>{d.selected_J[frame].toFixed(3)}</b> · dimensionless. J &gt; 0 checks
        orientation here, not global injectivity.
      </p>
    </div>
  );
}

function Cylinder() {
  return (
    <div
      className={css.ambiguity}
      role="img"
      aria-label="Analytic cylinder with unchanged occupied shape but alternate untwisted and twisted material paths"
    >
      <svg viewBox="0 0 480 200">
        <defs>
          <linearGradient id="mm-cylinder" x2="1" y2="1">
            <stop stopColor="#153440" />
            <stop offset="1" stopColor="#2b6b76" />
          </linearGradient>
        </defs>
        {[80, 320].map((cx, i) => (
          <g key={i}>
            <path
              d={`M${cx - 48} 40V151Q${cx} 175 ${cx + 48} 151V40`}
              fill="url(#mm-cylinder)"
              stroke="#8eb6c0"
            />
            <ellipse cx={cx} cy="40" rx="48" ry="14" fill="#20505b" stroke="#8eb6c0" />
            <ellipse cx={cx} cy="151" rx="48" ry="14" fill="none" stroke="#8eb6c0" />
            {[0, 1, 2].map((j) => (
              <path
                key={j}
                d={
                  i
                    ? `M${cx - 25 + j * 25} 45C${cx + 25 - j * 25} 85 ${cx - 25 + j * 25} 115 ${cx + 25 - j * 25} 150`
                    : `M${cx - 25 + j * 25} 45V150`
                }
                fill="none"
                stroke={i ? '#f5e8db' : color.output}
                strokeWidth="2"
              />
            ))}
          </g>
        ))}
        <text x="32" y="190">
          Untwisted material map
        </text>
        <text x="270" y="190">
          Twisted material map
        </text>
      </svg>
      <p>
        Cyan straight: untwisted; white curved: twisted. Equal occupancy at every phase, but
        different tangential motion and strain. Analytic control, not patient or STRAUS pixels.
      </p>
    </div>
  );
}

function LineChart({
  frame,
  values,
  referenceValues,
  domain,
  unit,
  label,
}: {
  frame: number;
  values: number[];
  referenceValues?: number[];
  domain: [number, number];
  unit: string;
  label: string;
}) {
  const x = (i: number) => 43 + i * (289 / (values.length - 1));
  const y = (v: number) => 142 - (v - domain[0]) * (114 / (domain[1] - domain[0]));
  const path = (v: number[]) =>
    v.map((n, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)} ${y(n).toFixed(1)}`).join(' ');
  const mid = (domain[0] + domain[1]) / 2;
  return (
    <svg
      className={css.chart}
      viewBox="0 0 355 175"
      role="img"
      aria-label={`${label}, fixed ${domain[0]} to ${domain[1]} ${unit} axis`}
    >
      {[domain[0], mid, domain[1]].map((v) => (
        <g key={v}>
          <path d={`M43 ${y(v)}H332`} className={css.gridline} />
          <text x="37" y={y(v) + 3} textAnchor="end">
            {Number.isInteger(v) ? v : v.toFixed(1)}
          </text>
        </g>
      ))}
      <text x="5" y="16">
        {unit}
      </text>
      <path d={path(values)} stroke={color.output} strokeWidth="2.6" fill="none" />
      {referenceValues && (
        <path
          d={path(referenceValues)}
          data-mask-mechanics-reference
          stroke={color.reference}
          strokeDasharray="5 3"
          strokeWidth="2.3"
          fill="none"
        />
      )}
      <path d={`M${x(frame)} 27V142`} stroke="#d6e6e7" strokeWidth="1" />
      <text x="43" y="165">
        0
      </text>
      <text x="332" y="165" textAnchor="end">
        {values.length - 1}
      </text>
    </svg>
  );
}

export function MaskMechanicsScene({ state }: { state: MaskMechanicsState }) {
  const frame = mmFrame(state),
    mode = mmCondition(state),
    d = answer.conditions[mode],
    reveal = mmReveal(state);
  const common = {
    'data-mask-mechanics-scene': state.scene,
    'data-mask-mechanics-phase': frame,
    'data-mask-mechanics-condition': state.scene === 'clinical-transfer' ? 'clinical' : mode,
    'data-mask-mechanics-reference-state': reveal ? 'revealed' : 'hidden',
  };
  if (state.scene === 'clinical-transfer')
    return (
      <div className={css.root} {...common}>
        <p className={css.tag}>
          Clinical LV cavity · supplied all-phase masks · frame {frame + 1}/18 ·{' '}
          {input.clinical.times_seconds[frame].toFixed(3)} s
        </p>
        <div className={css.grid}>
          {[0, 1].map((i) => (
            <Slice key={i} index={i} frame={frame} clinical />
          ))}
          <LineChart
            frame={frame}
            values={answer.clinical['clinical-masks'].volume_ml}
            domain={[0, 140]}
            unit="mL"
            label="Saved clinical cavity volume"
          />
        </div>
        <p className={css.note}>
          Different grid: origin [−47, −39, −70] mm. Cavity volume/EF only; no epicardium or
          myocardial material truth.
        </p>
      </div>
    );
  if (state.scene === 'material-ambiguity')
    return (
      <div className={css.root} {...common}>
        <p className={css.tag}>Same segmented domain ≠ one material map</p>
        <Cylinder />
      </div>
    );
  if (state.scene === 'reference-probes' || state.scene === 'limits')
    return (
      <div className={css.root} {...common}>
        <p className={css.tag}>
          Private fixed source-cell material probe · {reveal ? 'reader reveal' : 'hidden'}
        </p>
        {reveal ? (
          <div
            className={css.reference}
            data-mask-mechanics-reference
            data-mask-mechanics-material-probe
          >
            <LineChart
              frame={frame}
              values={reference.conditions[mode].predicted_engineering_strain_pp[2]}
              referenceValues={reference.source_engineering_strain_pp[2]}
              domain={[-10, 50]}
              unit="%"
              label="Selected AHA 8 source-cell radial engineering strain, predicted versus simulator"
            />
            <div className={css.referenceText}>
              <b>One AHA {reference.source_AHA_label} cell</b>
              <p>
                Dashed purple: simulator material path. Solid cyan: saved answer at the same
                barycentric source-centroid probe, with no per-frame realignment.
              </p>
              <p>
                Aggregate reference-volume coverage:{' '}
                {reference.conditions[mode].material_coverage_pct.toFixed(2)}%. Aggregate radial
                MAE: {reference.conditions[mode].radial_mae_pp.toFixed(2)} pp; diagnostic target ≤5
                pp.
              </p>
              <small data-mask-mechanics-missing-direction>{reference.missing_direction}</small>
            </div>
          </div>
        ) : (
          <div className={css.hidden}>
            Private simulator trajectories and anatomical directions are withheld until reader
            reveal.
          </div>
        )}
      </div>
    );
  if (state.scene === 'deformation-gradient')
    return (
      <div className={css.root} {...common}>
        <p className={css.tag}>Answer-owned tetrahedron · fixed connectivity · phase {frame}/29</p>
        <div className={css.tensorStage}>
          <TetraPair frame={frame} condition={mode} />
          <Matrix frame={frame} condition={mode} />
        </div>
      </div>
    );
  if (state.scene === 'mesh-construction' || state.scene === 'fixed-connectivity')
    return (
      <div className={css.root} {...common}>
        <p className={css.tag}>
          {state.scene === 'mesh-construction'
            ? 'Frame-0 mask → answer-owned tetrahedralization'
            : `Fixed vertex indices through phase ${frame}/29`}
        </p>
        <div className={css.meshStage}>
          <Slice
            index={0}
            frame={state.scene === 'mesh-construction' ? 0 : frame}
            image={mode === 'masks-images'}
          />
          <Slice
            index={1}
            frame={state.scene === 'mesh-construction' ? 0 : frame}
            image={mode === 'masks-images'}
          />
          <MeshCloud frame={state.scene === 'mesh-construction' ? 0 : frame} condition={mode} />
        </div>
        <p className={css.note}>
          {d.vertices.toLocaleString()} saved vertices, {d.tetrahedra.toLocaleString()} fixed
          tetrahedra. Sampled dots are display geometry; IDs encode hypothesized correspondence, not
          observed tissue tracks.
        </p>
      </div>
    );
  return (
    <div className={css.root} {...common}>
      <p className={css.tag}>
        Synthetic myocardial wall · phase {frame}/29 ·{' '}
        {mode === 'masks-images' ? 'mask + registered ultrasound' : 'masks alone'}
      </p>
      <div className={css.grid}>
        {[0, 1, 2].map((i) => (
          <Slice
            key={i}
            index={i}
            frame={frame}
            image={mode === 'masks-images'}
            output={state.scene === 'occupancy' && state.output > 0.5}
            condition={mode}
          />
        ))}
      </div>
      <p className={css.note}>
        {state.scene === 'occupancy'
          ? 'Orange dashed: supplied wall mask boundary. Cyan solid: saved tetra-mesh section. Same native slices and scale.'
          : mode === 'masks-images'
            ? 'Grayscale is registered appearance; the orange mask remains the supplied wall geometry.'
            : 'Orange shows the independently rasterized mask. No vertex identity or initial tetrahedral mesh is supplied.'}
      </p>
    </div>
  );
}

export function MaskMechanicsOutput({ state }: { state: MaskMechanicsState }) {
  const frame = mmFrame(state),
    mode = mmCondition(state),
    d = answer.conditions[mode],
    reveal = mmReveal(state);
  const title: Record<MaskMechanicsState['scene'], string> = {
    'input-masks': 'Input: 30 wall masks, no material IDs',
    'input-images': 'Second condition: masks plus ultrasound',
    'mesh-construction': 'Answer-owned initial tetra mesh',
    'fixed-connectivity': 'A proposed material correspondence',
    'deformation-gradient': 'Saved local F, E and J',
    occupancy: 'Domain fit is separate from tissue motion',
    'material-ambiguity': 'Identical occupancy can hide different strain',
    'reference-probes': 'Fixed simulator probes revealed',
    'clinical-transfer': 'Clinical cavity transfer only',
    limits: 'Construction passes; radial diagnostic misses',
  };
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-mask-mechanics-output>
      <strong>{title[state.scene]}</strong>
      {state.scene === 'input-masks' && (
        <p>
          30 independently rasterized STRAUS phases on a 1.5 mm grid, origin [81, −108, 95] mm.
          Synthetic time has phase index only; no seconds-based rate.
        </p>
      )}
      {state.scene === 'input-images' && (
        <p>
          Registered ultrasound is extra appearance input only in this condition. It is not
          velocity, displacement or strain truth.
        </p>
      )}
      {state.scene === 'mesh-construction' && (
        <p>
          {mode === 'masks' ? 'Five' : 'Six'} tetrahedra per occupied voxel create the answer's
          frame-0 topology. The source masks contain no initial mesh.
        </p>
      )}
      {state.scene === 'fixed-connectivity' && (
        <p>
          One connectivity persists across phases. The moving cell is inferred by the answer;
          equal-looking masks cannot prove its material identity.
        </p>
      )}
      {state.scene === 'deformation-gradient' && (
        <p>
          F maps saved reference edges to saved current edges; full E is Green–Lagrange strain. J
          checks local orientation. These fields are mathematically consistent with this chosen
          mesh.
        </p>
      )}
      {state.scene === 'occupancy' && (
        <p>
          Saved mean voxel-centre Dice across all 30 phases is{' '}
          {mode === 'masks' ? '0.9461' : '0.9328'}. Local contour differences remain, and geometric
          fit does not validate correspondence.
        </p>
      )}
      {state.scene === 'material-ambiguity' && (
        <p>
          An analytic cylinder can twist without changing any phase's occupied region. Its twisted J
          is {input.analytic_ambiguity.twisted_J.toFixed(1)}, yet strain differs.
        </p>
      )}
      {state.scene === 'reference-probes' && (
        <p>
          {reveal
            ? 'Private simulator material trajectories and anatomical axes are now revealed. The chart is one selected source cell; aggregate diagnostics use reference-volume weights.'
            : 'Private material trajectories remain hidden until this explicit reference chapter.'}
        </p>
      )}
      {state.scene === 'clinical-transfer' && (
        <p>
          18 supplied LV cavity masks already encode a{' '}
          {answer.clinical['clinical-masks'].ef_pct.toFixed(2)}% geometric EF. Saved cavity mesh
          reproduces volume; myocardial_strain_supported=false.
        </p>
      )}
      {state.scene === 'limits' && (
        <p>
          {reveal
            ? 'Both original answers have construction reward 1. Their aggregate radial errors are 7.37 and 5.45 pp, above the 5 pp diagnostic target.'
            : 'The private material diagnostic remains hidden.'}{' '}
          One synthetic case cannot establish clinical strain.
        </p>
      )}
      <div className={css.legend}>
        <span>
          <i style={{ background: color.input }} />
          Supplied mask
        </span>
        {state.output > 0.5 &&
          !['input-masks', 'input-images', 'material-ambiguity', 'clinical-transfer'].includes(
            state.scene,
          ) && (
            <span>
              <i style={{ background: color.output }} />
              Saved answer
            </span>
          )}
        {reveal && (
          <span data-mask-mechanics-reference>
            <i className={css.dashed} style={{ borderColor: color.reference }} />
            Private simulator
          </span>
        )}
      </div>
      {state.scene === 'clinical-transfer' && (
        <small>
          The cavity input has no epicardium, wall trajectories or myocardial-strain truth.
          Timestamps run 0–0.751282 s; no strain rate is inferred.
        </small>
      )}
      {state.scene === 'limits' && (
        <small>
          Oracle uses privileged exact-source material. Static control fails construction. The two
          original methods and tetrahedralizations differ, so their errors do not isolate a causal
          image benefit.
        </small>
      )}
    </aside>
  );
}

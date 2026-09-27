import {
  resectCase as g,
  resectReference as refs,
  resectHelpers,
  resectColors as c,
  resectProjection,
  resectSweepIndex,
  resectReveal,
  resectTeachingOutput,
  type ResectState,
  type ResectPlane,
} from './resect';
import styles from './task-visual.module.css';
const n = (v: number) => v.toFixed(3),
  triplet = (v: number[]) => v.map(n).join(', ');
function Section({
  plane,
  x,
  y,
  size,
  label,
  query,
  reference = false,
  helper,
  opacity = 0,
}: {
  plane: ResectPlane;
  x: number;
  y: number;
  size: number;
  label: string;
  query: 'mri' | 'us';
  reference?: boolean;
  helper?: ResectPlane;
  opacity?: number;
}) {
  const w = (size * plane.width) / Math.max(plane.width, plane.height),
    h = (size * plane.height) / Math.max(plane.width, plane.height);
  const projected = resectProjection(plane, g.query_world_mm);
  const target = reference ? resectProjection(plane, refs[1].target_world_mm) : null;
  const screen = (p: { u: number; v: number }) => [
    x + ((p.u + 0.5) * w) / plane.width,
    y + ((p.v + 0.5) * h) / plane.height,
  ];
  const q = screen(projected),
    t = target ? screen(target) : null;
  return (
    <g>
      <text x={x} y={y - 10} fontSize="15">
        {label}
      </text>
      <rect x={x} y={y} width={w} height={h} fill="#202825" />
      <image href={plane.png} x={x} y={y} width={w} height={h} />
      {helper && (
        <image
          data-resect-helper={query}
          href={helper.png}
          x={x}
          y={y}
          width={w}
          height={h}
          opacity={opacity}
        />
      )}
      <circle
        cx={q[0]}
        cy={q[1]}
        r="5"
        fill="none"
        stroke={query === 'mri' ? c.query : c.initial}
        strokeWidth="2.5"
      />
      {t && (
        <g data-resect-target="projected">
          <line
            x1={q[0]}
            y1={q[1]}
            x2={t[0]}
            y2={t[1]}
            stroke={c.reference}
            strokeWidth="1.5"
            strokeDasharray="4 3"
          />
          <path
            d={`M${t[0] - 6} ${t[1]}h12M${t[0]} ${t[1] - 6}v12`}
            stroke={c.reference}
            strokeWidth="2.5"
          />
        </g>
      )}
    </g>
  );
}
function Pair({ state }: { state: ResectState }) {
  const inspect = state.scene === 'inspect',
    frame = resectSweepIndex(state.scan);
  const views = (key: 'mri' | 'us') =>
    inspect ? g.modalities[key].sweep[frame] : g.modalities[key].ras[0];
  const helpers = state.scene === 'helpers';
  return (
    <>
      <text x="25" y="30">
        {inspect
          ? 'Inspect co-oriented axial sections'
          : helpers
            ? 'Optional paired tumor-mask condition'
            : 'One shared physical position, two image grids'}
      </text>
      {(['mri', 'us'] as const).map((key, i) => (
        <Section
          key={key}
          plane={views(key)}
          x={35 + i * 280}
          y={95}
          size={230}
          label={key === 'mri' ? 'FLAIR · MRI query' : '3D US · initial candidate'}
          query={key}
          helper={helpers ? resectHelpers[key] : undefined}
          opacity={state.helper}
        />
      ))}
      {helpers ? (
        <>
          <g>
            <rect
              data-resect-mask-legend="mri"
              x="35"
              y="341"
              width="12"
              height="12"
              fill="#e65b9f"
            />
            <text x="55" y="353" fontSize="16">
              Pink · MRI tumor
            </text>
            <rect
              data-resect-mask-legend="us"
              x="315"
              y="341"
              width="12"
              height="12"
              fill="#37cdcd"
            />
            <text x="335" y="353" fontSize="16">
              Cyan · US tumor
            </text>
          </g>
          <text x="25" y="382" fontSize="15">
            Masks narrow region search; they do not identify the paired point.
          </text>
          <text x="25" y="406" fontSize="14">
            Both masks withheld in base · helper reveal {Math.round(state.helper * 100)}%
          </text>
        </>
      ) : (
        <>
          <text x="25" y="353" fontSize="16">
            48 mm field · 0.5 mm pixels · +R right / +A down
          </text>
          <text x="25" y="382" fontSize="15">
            {inspect
              ? `Plane z = ${n(g.query_world_mm[2] + frame - 6)} mm · query is ${6 - frame} mm out of plane`
              : 'NIfTI affines locate the candidate; no registration is estimated.'}
          </text>
          <text x="25" y="406" fontSize="14">
            {inspect
              ? 'Rings are projections; only the middle section contains the query.'
              : 'Same RAS+ world point ≠ same native voxel index'}
          </text>
        </>
      )}
    </>
  );
}
export function ResectScene({ state }: { state: ResectState }) {
  const reveal = resectReveal(state);
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="RESECT query-centred sections and explicitly revealed manual reference"
    >
      {state.scene === 'inputs' ? (
        <>
          <text x="25" y="26">
            Complete native sections through the supplied world query
          </text>
          {(['mri', 'us'] as const).map((key, row) =>
            g.modalities[key].native.map((p, col) => (
              <Section
                key={key + col}
                plane={p}
                x={25 + col * 195}
                y={row ? 238 : 65}
                size={125}
                label={`${key === 'mri' ? 'MRI' : 'US'} ${p.name.replace('native ', '')}`}
                query={key}
              />
            )),
          )}
          <text x="25" y="409" fontSize="14">
            Case 2 · native axes differ across modalities · full volumes proposed
          </text>
        </>
      ) : ['frame', 'inspect', 'helpers', 'output'].includes(state.scene) ? (
        <Pair state={state} />
      ) : state.scene === 'reference' ? (
        <>
          <text x="25" y="30">
            Manual reference reveal · same-centre US sections
          </text>
          {g.modalities.us.ras.map((p, i) => {
            const d = reveal ? resectProjection(p, refs[1].target_world_mm).normal_mm : null;
            return (
              <g key={p.name}>
                <Section
                  plane={p}
                  x={25 + 195 * i}
                  y={100}
                  size={160}
                  label={p.name}
                  query="us"
                  reference={reveal}
                />
                <text x={25 + 195 * i} y="282" fontSize="14">
                  {d === null ? 'Hidden' : 'Off-plane:'}
                </text>
                <text x={25 + 195 * i} y="305" fontSize="14">
                  {d === null ? '' : `${d.toFixed(2)} mm`}
                </text>
              </g>
            );
          })}
          <text x="25" y="338" fontSize="16">
            {reveal
              ? `Full 3D separation: ${n(refs[1].initial_error_mm)} mm`
              : 'The initial candidate remains at the public query position.'}
          </text>
          <text x="25" y="366" fontSize="15">
            Dashed segments and crosses are projected, not same-slice matches.
          </text>
          <text x="25" y="390" fontSize="14">
            XY: +R/+A · XZ: +R/+S · YZ: +A/+S (right/down)
          </text>
          <text x="25" y="410" fontSize="14">
            All three planes fixed at the initial candidate; no GT recentering.
          </text>
        </>
      ) : state.scene === 'cases' ? (
        <>
          <text x="25" y="30">
            Copy the MRI world point unchanged · all 45 pairs
          </text>
          {refs.map((r, i) => (
            <g key={r.id}>
              <text x="25" y={77 + i * 95} fontSize="17">
                {r.id} · n=15
              </text>
              <line x1="150" y1={90 + i * 95} x2="550" y2={90 + i * 95} stroke="#aaa" />
              {reveal &&
                r.all_noop_errors_mm.map((e, k) => (
                  <circle
                    key={k}
                    cx={150 + (e / 12) * 400}
                    cy={82 + i * 95 + (k % 3) * 8}
                    r="4"
                    fill={c.reference}
                  >
                    <title>{n(e)} mm</title>
                  </circle>
                ))}
            </g>
          ))}
          <g>
            {[0, 3, 6, 9, 12].map((v) => (
              <text key={v} x={150 + (v / 12) * 400} y="325" textAnchor="middle" fontSize="15">
                {v}
              </text>
            ))}
            <text x="195" y="350" fontSize="16">
              Initial physical error (mm)
            </text>
          </g>
          <text x="25" y="382" fontSize="15">
            Source characterization · no model outcome or pass threshold
          </text>
          <text x="25" y="410" fontSize="14">
            Each dot is one published pair; vertical jitter only separates points.
          </text>
        </>
      ) : (
        <>
          <text x="25" y="35">
            Three proposed conditions · one unchanged coordinate control
          </text>
          {[
            ['Base', 'FLAIR + US + public query', 'Inspect homologous anatomy'],
            ['Mask assisted', 'Base + paired tumor masks', 'Narrow region; still match the point'],
            ['Coordinate only', 'Coordinates; no voxels', 'Measure the shared-frame shortcut'],
          ].map((row, i) => (
            <g key={row[0]}>
              <rect x="25" y={65 + i * 103} width="550" height="88" rx="8" fill="#e9ede5" />
              <text x="40" y={88 + i * 103} fontSize="18">
                {row[0]}
              </text>
              <text x="40" y={113 + i * 103} fontSize="16">
                {row[1]}
              </text>
              <text x="40" y={136 + i * 103} fontSize="14">
                {row[2]}
              </text>
            </g>
          ))}
          <text x="25" y="405" fontSize="14">
            Proposed voxel-output task ≠ executed two-query world-output pilot
          </text>
        </>
      )}
    </svg>
  );
}
export function ResectOutput({ state }: { state: ResectState }) {
  const reveal = resectReveal(state),
    output = resectTeachingOutput(state);
  return (
    <aside className={styles.storyOutput} data-resect-output={state.scene}>
      {state.scene === 'inputs' ? (
        <>
          <h4>Proposed single-query task</h4>
          <p>
            Complete native FLAIR MRI and pre-resection 3D ultrasound, one MRI world query, and the
            same-world US candidate.
          </p>
          <table>
            <thead>
              <tr>
                <th>Case 2</th>
                <th>Native shape</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>MRI</td>
                <td>176 × 224 × 256</td>
              </tr>
              <tr>
                <td>US</td>
                <td>306 × 385 × 254</td>
              </tr>
            </tbody>
          </table>
          <p>MRI ≈ 1 mm; US ≈ 0.208 mm. No masks or paired US targets in the base input.</p>
          <small>
            Selected after inspecting references; these teaching previews are not a frozen solver
            interface.
          </small>
        </>
      ) : state.scene === 'frame' ? (
        <>
          <h4>World → native US voxel</h4>
          <p>
            <b>RAS+ millimetres</b>: +x right, +y anterior, +z superior.
          </p>
          <p>world = affine × [i,j,k,1]. Invert the US affine to place the initial candidate.</p>
          <table>
            <tbody>
              <tr>
                <th>MRI voxel</th>
                <td>{triplet(g.modalities.mri.initial_voxel)}</td>
              </tr>
              <tr>
                <th>World mm</th>
                <td>{triplet(g.query_world_mm)}</td>
              </tr>
              <tr>
                <th>US voxel</th>
                <td>{triplet(g.modalities.us.initial_voxel)}</td>
              </tr>
            </tbody>
          </table>
          <small>
            The shared navigation frame supplies a useful initial guess, not proof of anatomical
            alignment.
          </small>
        </>
      ) : state.scene === 'inspect' ? (
        <>
          <h4>Inspect before moving a point</h4>
          <p>
            Thirteen source-derived axial sections sweep from −6 to +6 mm relative to the query.
          </p>
          <p>
            Compare shape across modalities and adjacent slices. MRI intensities and US speckle are
            not interchangeable.
          </p>
          <p>
            The plane moves; the world query remains fixed. The rings are projected when off-plane.
          </p>
          <small>
            Positive-intensity 1st–99th percentile windows stay fixed per volume. Dark exposed
            background denotes missing source coverage.
          </small>
        </>
      ) : state.scene === 'helpers' ? (
        <>
          <h4>Optional help has a separate contract</h4>
          <p>
            <b>Pink fill:</b> MRI tumor mask. <b>Cyan fill:</b> US tumor mask. The animation reveals
            the optional overlay.
          </p>
          <p>
            These masks indicate regions, not a point correspondence. Base inputs withhold both
            masks.
          </p>
          <p>
            Mask geometry is verified against the native image; nearest-neighbor sampling preserves
            discrete labels.
          </p>
          <small>
            Images/landmarks: CC BY 4.0. Masks and combined overlay exports: CC BY-NC-SA 4.0.
          </small>
        </>
      ) : state.scene === 'output' ? (
        <>
          <h4>Return a continuous US voxel point</h4>
          <p>
            Proposed fields: <code>us_voxel_ijk</code>, confidence and concise image evidence.
          </p>
          {output ? (
            <>
              <pre data-resect-teaching-output>
                {JSON.stringify(
                  { ...output, us_voxel_ijk: output.us_voxel_ijk.map((v) => +v.toFixed(3)) },
                  null,
                  2,
                )}
              </pre>
              <small>
                Unchanged teaching control, not a model answer. The evaluator converts this native
                voxel back to world mm.
              </small>
            </>
          ) : (
            <p>
              Teaching control is withheld until its reveal; no anatomical correction has been made.
            </p>
          )}
        </>
      ) : state.scene === 'reference' ? (
        <>
          <h4>Measure 3D physical error</h4>
          <span data-resect-reference>{reveal ? 'revealed' : 'hidden'}</span>
          {reveal ? (
            <>
              <p>Published Case 2 pair 13 (index 12).</p>
              <table>
                <tbody>
                  <tr>
                    <th>Initial world</th>
                    <td>{triplet(g.query_world_mm)}</td>
                  </tr>
                  <tr>
                    <th>Manual US</th>
                    <td>{triplet(refs[1].target_world_mm)}</td>
                  </tr>
                  <tr>
                    <th>3D TRE</th>
                    <td>
                      <b>{n(refs[1].initial_error_mm)} mm</b>
                    </td>
                  </tr>
                </tbody>
              </table>
            </>
          ) : (
            <p>Manual US destination and error are hidden.</p>
          )}
          <p>
            Score final error and improvement over no-op; report movement and worse corrections
            separately.
          </p>
          <small>
            No acceptance threshold or ambiguous-point policy is frozen. Manual landmarks are sparse
            references, not a dense deformation field.
          </small>
        </>
      ) : state.scene === 'cases' ? (
        <>
          <h4>Preserve easy points; test correction</h4>
          <table>
            <thead>
              <tr>
                <th>15 pairs/case</th>
                <th>Mean</th>
                <th>Max mm</th>
              </tr>
            </thead>
            <tbody>
              {refs.map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{reveal ? r.baseline.mean_mm.toFixed(2) : 'hidden'}</td>
                  <td>{reveal ? r.baseline.max_mm.toFixed(2) : 'hidden'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            Case 1 has a stronger no-op than Cases 2–3. A useful hypothesis is to correct
            misalignment without degrading already-close points.
          </p>
          <small>
            Three selected public cases characterize these inputs only. No inference about model
            success or population performance follows.
          </small>
        </>
      ) : (
        <>
          <h4>Define the study before testing it</h4>
          <p>
            <b>Unfrozen:</b> three-case sampling, viewer, thresholds, ambiguous-point handling and
            aggregation.
          </p>
          <p>
            <b>Exposure:</b> public challenge training data; not an unseen test claim.
          </p>
          <p>
            <b>Selection:</b> teaching points used masks and tags; older static views were
            independently GT-centred.
          </p>
          <p>
            <b>Separate pilot:</b> two selected queries already executed with{' '}
            <code>us_world_mm</code>. Its results belong to the next entry.
          </p>
          <small>This explanation launches no trial and makes no clinical safety claim.</small>
        </>
      )}
    </aside>
  );
}

import {
  respiratory,
  respiratoryOutput,
  respiratoryReference,
  respiratoryRows,
  respiratoryColors as colors,
  focusQuery,
  q06Error,
  planePixels,
  isRespiratoryCloseup,
  type CTPlane,
  type RespiratoryState,
} from './respiratory';
import styles from './task-visual.module.css';
const xyz = (point: number[]) => point.map((v) => v.toFixed(2)).join(', ');
function Slice({
  plane,
  x,
  y,
  width,
  height,
  points = [],
}: {
  plane: CTPlane;
  x: number;
  y: number;
  width: number;
  height: number;
  points?: { p: number[]; color: string }[];
}) {
  const sx = width / plane.width,
    sy = height / plane.height;
  return (
    <g>
      <image
        href={plane.png}
        x={x}
        y={y}
        width={width}
        height={height}
        preserveAspectRatio="none"
      />
      {points.map(({ p, color }, i) => {
        const [u, v] = planePixels(plane, p);
        return (
          <circle
            key={i}
            cx={x + (u + 0.5) * sx}
            cy={y + (v + 0.5) * sy}
            r="4"
            stroke={color}
            fill="none"
            strokeWidth="2"
          />
        );
      })}
    </g>
  );
}
export function RespiratoryScene({ state }: { state: RespiratoryState }) {
  const close = isRespiratoryCloseup(state.scene),
    reveal = state.reference > 0.5;
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Calibrated source CT slices; projected points retain their full three-dimensional errors in the table"
    >
      {close ? (
        <>
          {respiratory.target_returned_patch.map((plane, i) => {
            const gt = respiratoryReference.truth.points_world_mm[focusQuery],
              returned = respiratoryOutput.points_world_mm[focusQuery],
              off = gt[i === 0 ? 2 : i === 1 ? 1 : 0] - returned[i === 0 ? 2 : i === 1 ? 1 : 0];
            return (
              <g key={plane.name}>
                <text x={12 + i * 198} y="70">
                  Target {plane.name}
                </text>
                <Slice
                  plane={plane}
                  x={12 + i * 198}
                  y={100}
                  width={180}
                  height={180}
                  points={[
                    { p: returned, color: colors.returned },
                    ...(reveal ? [{ p: gt, color: colors.reference }] : []),
                  ]}
                />
                <text x={12 + i * 198} y="308" fontSize="13">
                  {reveal ? `GT off-plane: ${off.toFixed(2)} mm` : 'Manual target hidden'}
                </text>
              </g>
            );
          })}
          <text x="12" y="360">
            64 mm patches · centred on returned q06
          </text>
          <text x="12" y="383" fontSize="13">
            Markers are projections; the table uses the full 3D distance.
          </text>
        </>
      ) : state.scene === 'conditions' ? (
        <>
          {[respiratory.views.patient1, respiratory.views.patient3].map((view, i) => (
            <g key={i}>
              <text x={20 + i * 295} y="60">
                Case {i === 0 ? '1' : '3'} · supplied slice
              </text>
              <Slice
                plane={view.plane}
                x={20 + i * 295}
                y={100}
                width={265}
                height={(265 * view.plane.height) / view.plane.width}
                points={view.source_world_mm.map((p) => ({ p, color: colors.query }))}
              />
            </g>
          ))}
          <text x="20" y="355">
            Different patients · separate source poses
          </text>
        </>
      ) : (
        <>
          <text x="20" y="40">
            Case 3 · exhale source
          </text>
          <text x="315" y="40">
            Inhale target · XY section
          </text>
          <Slice
            plane={respiratory.views.patient3.plane}
            x={20}
            y={70}
            width={265}
            height={170}
            points={respiratory.views.patient3.source_world_mm.map((p) => ({
              p,
              color: colors.query,
            }))}
          />
          <Slice
            plane={respiratory.target_sections[0]}
            x={315}
            y={70}
            width={265}
            height={189}
            points={respiratoryRows(state)
              .filter((r) => r.point)
              .map((r) => ({ p: r.point!, color: colors.returned }))}
          />
          {state.depth > 0 && (
            <g opacity={state.depth}>
              {respiratory.source_sections.map((plane, i) => (
                <g key={plane.name}>
                  <Slice plane={plane} x={20 + i * 89} y={282} width={80} height={80} />
                  <text x={20 + i * 89} y="380" fontSize="13">
                    {plane.name}
                  </text>
                </g>
              ))}
            </g>
          )}
          <text x="315" y="295" fontSize="13">
            Complete target CT supplied.
          </text>
          <text x="315" y="318" fontSize="13">
            Output marks project onto XY;
          </text>
          <text x="315" y="341" fontSize="13">
            their Z coordinates stay in the table.
          </text>
          <text x="20" y="410" fontSize="13">
            Display windows only · no estimated deformation field
          </text>
        </>
      )}
    </svg>
  );
}
const titles = {
  inputs: 'Eight source queries → target points',
  frame: 'Known source pose is not a correspondence',
  depth: 'Add source depth; retain the same query',
  output: 'Retained BR-028 output · eight ordered points',
  reference: 'Reveal the manual target and frozen gates',
  judgment: 'Frozen score and practical judgment coexist',
  conditions: 'Keep the four frozen contracts separate',
  limits: 'Sparse feasibility, not a general difficulty claim',
};
export function RespiratoryOutput({ state }: { state: RespiratoryState }) {
  const reveal = state.reference > 0.5,
    grade = respiratoryReference.conditions[1].grade;
  return (
    <aside className={styles.storyOutput} data-respiratory-output>
      <strong>{titles[state.scene]}</strong>
      {state.scene === 'inputs' ? (
        <>
          <p>
            <b>Left:</b> complete 189 × 121 exhale slice and eight fractional-pixel queries.{' '}
            <b>Right:</b> sections of the supplied inhale CT.
          </p>
          <p>
            The target volume is <b>192 × 192 × 208</b>, with <b>1.75 × 1.25 × 1.75 mm</b> sampling.
          </p>
          <p>
            Learn2Reg LungCT case 3 was cropped, resampled and affine prealigned. Expiration
            coverage is incomplete.
          </p>
          <p>
            <b>Hidden:</b> manual target coordinates. Ordinary libraries and network access were
            allowed.
          </p>
          <small>
            Dataset-world mm; native patient LPS/RAS is not asserted. Source and target are
            separated for display.
          </small>
        </>
      ) : state.scene === 'frame' ? (
        <>
          <p>
            <b>q06</b> is the posthoc teaching example. Its source pixel is <b>(125.714, 85.879)</b>
            , using 1.25 mm in-plane spacing.
          </p>
          <p>
            <code>source = slice_to_world × [u·sx, v·sy, 0, 1]</code>
          </p>
          <p>
            Public source location: <b>[220.50, 170.00, 140.00] mm</b>.
          </p>
          <p>
            The affine places the slice inside the source scan. Respiration still changes anatomical
            positions in the target.
          </p>
          <small>
            No rigid pose or dense field is the required output; return eight corresponding target
            coordinates.
          </small>
        </>
      ) : state.scene === 'depth' ? (
        <>
          <p>
            <b>BR-028 adds the full source CT.</b> The left view reveals three source sections
            around the public q06 location.
          </p>
          <table className={styles.screenTable}>
            <tbody>
              <tr>
                <th>Added</th>
                <td>reference_volume.npz</td>
              </tr>
              <tr>
                <th>Unchanged</th>
                <td>Slice, queries, target, truth, grader</td>
              </tr>
              <tr>
                <th>Gates</th>
                <td>RMS ≤ 3 mm AND max ≤ 5 mm</td>
              </tr>
            </tbody>
          </table>
          <p>
            The original fractional pixels and slice pose remain. Exact manual source points are not
            substituted.
          </p>
          <small>
            These are calibrated sections, not a volume rendering or an animated registration
            result.
          </small>
        </>
      ) : state.scene === 'output' ? (
        <>
          <p>
            Retained Sol/xhigh answer in <code>/app/answer/points.json</code>. Rows appear in query
            order; no search trajectory is simulated.
          </p>
          <table className={styles.screenTable}>
            <thead>
              <tr>
                <th>query_ids</th>
                <th>points_world_mm [X, Y, Z]</th>
              </tr>
            </thead>
            <tbody>
              {respiratoryRows(state).map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td data-respiratory-point>{r.point ? xyz(r.point) : 'pending reveal'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <small>
            Historical submitted coordinates; no new prediction or fresh model execution.
          </small>
        </>
      ) : state.scene === 'reference' ? (
        <>
          <p>
            Target close-up is centred on the <b>returned</b> q06. Teal and pink retain their true
            offset.
          </p>
          <table className={styles.screenTable}>
            <tbody>
              <tr>
                <th>Returned</th>
                <td>{xyz(respiratoryOutput.points_world_mm[focusQuery])}</td>
              </tr>
              <tr>
                <th>Manual target</th>
                <td data-respiratory-reference>
                  {reveal ? xyz(respiratoryReference.truth.points_world_mm[focusQuery]) : 'hidden'}
                </td>
              </tr>
              <tr>
                <th>q06 3D error</th>
                <td>{reveal ? `${q06Error.toFixed(3)} mm` : 'hidden'}</td>
              </tr>
              <tr>
                <th>8-point RMS ≤ 3</th>
                <td>{reveal ? `${grade.rms_mm.toFixed(3)} mm · pass` : 'hidden'}</td>
              </tr>
              <tr>
                <th>Maximum ≤ 5</th>
                <td>{reveal ? `${grade.max_mm.toFixed(3)} mm · fail` : 'hidden'}</td>
              </tr>
            </tbody>
          </table>
          <p>
            {reveal
              ? 'Pink dashed circles mark a 5 mm radius around the manual target in 3D. q06 is outside it. The other seven errors are ≤ 2.181 mm.'
              : 'The manual coordinates enter only with the reader reference reveal.'}
          </p>
          <small>
            Frozen reward remains 0. Sparse manual landmarks are not clinical equivalence criteria.
          </small>
        </>
      ) : state.scene === 'judgment' ? (
        <>
          <p>
            <b>Frozen result:</b> RMS 2.604 mm passes; maximum 6.412 mm fails. Original reward:{' '}
            <b>0</b>.
          </p>
          <p>
            <b>User visual judgment:</b> q06 was good enough for the intended example. The
            full-source case was retired as a hard-task candidate and the idea parked.
          </p>
          <p>
            No reference correction, new tolerance, independent clinical adjudication or regrading
            followed.
          </p>
          <small>
            Three target sections share one physical frame. A visually plausible match can still
            miss a predeclared numerical gate.
          </small>
        </>
      ) : state.scene === 'conditions' ? (
        <>
          <table className={styles.screenTable}>
            <thead>
              <tr>
                <th>Contract</th>
                <th>Solver observation</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>BR-021 case 1 · 2D</td>
                <td>118 × 171 slice, pixels + pose</td>
              </tr>
              <tr>
                <td>BR-021 case 1 · 3D</td>
                <td>Full source, exact manual source queries</td>
              </tr>
              <tr>
                <td>BR-024 case 3 · 2D</td>
                <td>121 × 189 slice, pixels + pose</td>
              </tr>
              <tr>
                <td>BR-028 case 3 · 3D</td>
                <td>Add full source; keep projected queries</td>
              </tr>
            </tbody>
          </table>
          <p>
            <b>BR-023:</b> reused case 1’s frozen 2D task. Four later author interventions are not
            four additional model trials.
          </p>
          <small>
            Both case 1 contracts use the same eight target references, with source locations
            differing by up to 0.313 mm. Case 2 was not admitted or trialled.
          </small>
        </>
      ) : (
        <>
          <table className={styles.screenTable}>
            <thead>
              <tr>
                <th>Case 3 Sol/xhigh</th>
                <th>RMS / max (mm)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>BR-024 · slice</td>
                <td>12.731 / 32.203</td>
              </tr>
              <tr>
                <td>BR-028 · source depth</td>
                <td>2.604 / 6.412</td>
              </tr>
            </tbody>
          </table>
          <p>
            <b>One fresh attempt per condition.</b> Source context, solver strategy and run variance
            differ; this is not a causal depth estimate.
          </p>
          <p>
            A public-input author method passed case 3’s 2D feasibility gate:{' '}
            <b>2.133 / 3.416 mm</b>.
          </p>
          <p>
            Eight landmarks do not validate dense deformation, topology or unqueried regions. Public
            external annotations also limit contamination control.
          </p>
          <small>
            Case 1 was retired after repeat passes; the full-source case was parked after visual
            acceptance.
          </small>
        </>
      )}
    </aside>
  );
}

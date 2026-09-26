import { useId } from 'react';
import type { StoryPlan } from '../types';
import type { StoryState } from './story-timeline';
import {
  graph,
  rigid,
  multiscale as m,
  traceEdges,
  transformedPoint,
  residualM,
  level0Point,
} from './operation-fixtures';
import styles from './task-visual.module.css';
import { InverseScene, InverseOutput } from './inverse-panels';
import { FamilyScene, FamilyOutput } from './family-panels';
const COLORS = ['#357f75', '#b4743c', '#72639a', '#497a9a', '#9b5863', '#77833d'];
const xy = (p: number[]) => `${300 + p[0] * 3300},${235 - p[1] * 3300}`;
function NavigationScene({ state }: { state: Extract<StoryState, { recipe: 'multiscale-v1' }> }) {
  const clip = useId();
  const scale = 1 + 3 * state.viewport;
  const origin = m.tile_origin_level0.map((v) => v * state.viewport);
  const sx = 520 / m.width_level0,
    sy = 300 / m.height_level0;
  const screen = (p: number[]) => [
    (p[0] - origin[0]) * sx * scale,
    (p[1] - origin[1]) * sy * scale,
  ];
  const tile = screen(m.tile_origin_level0),
    point = screen(level0Point(m.example_local_point));
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Viewport zoom with a later selected point and an affine-derived slide coordinate"
    >
      <defs>
        <clipPath id={clip}>
          <rect width="520" height="300" />
        </clipPath>
      </defs>
      <text x="35" y="30">
        {state.viewport === 0
          ? 'Overview · no candidate selected'
          : 'Zoom retains the level-0 origin'}
      </text>
      <g transform="translate(35 55)">
        <rect width="520" height="300" fill="#eeeee5" stroke="#bdbdaf" />
        <g clipPath={`url(#${clip})`}>
          {Array.from({ length: 13 }, (_, i) => (
            <path key={'x' + i} d={`M${screen([i * 1000, 0])[0]} 0V300`} stroke="#d5d7ce" />
          ))}
          {Array.from({ length: 9 }, (_, i) => (
            <path key={'y' + i} d={`M0 ${screen([0, i * 1000])[1]}H520`} stroke="#d5d7ce" />
          ))}
          <rect
            x={tile[0]}
            y={tile[1]}
            width={130 * scale}
            height={75 * scale}
            fill="#dae5e6"
            fillOpacity="0.7"
            stroke="#557e93"
            strokeWidth="2"
          />
          <g opacity={state.selections}>
            <path
              d={`M${point[0] - 9} ${point[1]}h18M${point[0]} ${point[1] - 9}v18`}
              stroke="#b77128"
              strokeWidth="3"
            />
            <text x={point[0] + 14} y={point[1] + 24} fontSize="16">
              local ({m.example_local_point.join(', ')})
            </text>
          </g>
        </g>
      </g>
      <text x="35" y="390" fontSize="16">
        {state.outputs > 0
          ? `level-0 (${level0Point(m.example_local_point).join(', ')}) px`
          : `Tile origin (${m.tile_origin_level0.join(', ')}) · downsample ${m.tile_downsample}`}
      </text>
    </svg>
  );
}
/** Fallbacks are data-derived views of the current canonical frame, not separate stories. */
export function OperationScene({ plan, state }: { plan: StoryPlan; state: StoryState }) {
  if (state.recipe === 'topology-v1')
    return (
      <svg
        className={styles.operationCanvas}
        viewBox="0 0 600 420"
        role="img"
        aria-label="Projected graph with the same edge IDs and path samples"
      >
        {graph.edges.map((e, i) => (
          <polyline
            key={e.id}
            points={e.points.map(xy).join(' ')}
            fill="none"
            stroke={i < Math.floor(state.inventory * 7 + 1e-8) ? '#307f74' : '#bdbdb0'}
            strokeWidth="5"
          />
        ))}
        {traceEdges(state.trace).map(({ edge, points }) => (
          <polyline
            key={edge.id}
            points={points.map(xy).join(' ')}
            fill="none"
            stroke="#b77128"
            strokeWidth="5"
          />
        ))}
        {Object.entries(graph.nodes).map(([id, p]) => (
          <text key={id} x={300 + p[0] * 3300 + 8} y={235 - p[1] * 3300} fontSize="16">
            {id}
          </text>
        ))}
      </svg>
    );
  if (state.recipe === 'correspondence-v1')
    return (
      <svg
        className={styles.operationCanvas}
        viewBox="0 0 600 420"
        role="img"
        aria-label="Fixed and moving point coordinates; endpoint transform shown in table"
      >
        <text x="24" y="35">
          Projected fixture coordinates · endpoint witness
        </text>
        {rigid.point_ids.map((id, i) => {
          const a = rigid.moving_points[i],
            b = transformedPoint(a);
          return (
            <g key={id}>
              <line
                x1={300 + a[0] * 3300}
                y1={235 - a[1] * 3300}
                x2={300 + b[0] * 3300}
                y2={235 - b[1] * 3300}
                stroke="#a9b5b2"
                strokeDasharray="5 5"
              />
              <circle cx={300 + a[0] * 3300} cy={235 - a[1] * 3300} r="7" fill="#b77128" />
              <circle cx={300 + b[0] * 3300} cy={235 - b[1] * 3300} r="7" fill="#307f74" />
              <text x={310 + b[0] * 3300} y={235 - b[1] * 3300} fontSize="16">
                {id}
              </text>
            </g>
          );
        })}
        <text x="24" y="390">
          Dashed: source → transformed endpoint · not a motion path
        </text>
      </svg>
    );
  if (state.recipe === 'inverse-v1') return <InverseScene plan={plan} state={state} />;
  if (state.recipe !== 'multiscale-v1') return <FamilyScene state={state} />;
  if (plan.id === 'wsi-search') return <NavigationScene state={state} />;
  const patches = plan.id === 'wsi-patches',
    coverage = plan.id === 'wsi-coverage';
  const sx = 520 / m.width_level0,
    sy = 300 / m.height_level0;
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label={
        patches
          ? 'Twelve supplied abstract patch slots, no diagnoses'
          : coverage
            ? 'Six teaching symbols and explicitly bounded annotation coverage'
            : 'Local to level-0 coordinate mapping'
      }
    >
      <defs>
        <pattern id="unknown-region" width="10" height="10" patternUnits="userSpaceOnUse">
          <path d="M0 10L10 0" stroke="#d3d3c7" strokeWidth="1" />
        </pattern>
      </defs>
      <text x="35" y="30">
        {patches
          ? '12 supplied slots · fixed locations'
          : coverage
            ? 'Coverage is separate from a class label'
            : 'Local coordinates → level-0 pixels'}
      </text>
      <g transform="translate(35 55)">
        <rect
          width="520"
          height="300"
          fill={coverage ? 'url(#unknown-region)' : '#eeeee5'}
          stroke="#bdbdaf"
        />
        {coverage &&
          m.regions.map((r) => (
            <g key={r.id} opacity={0.3 + 0.7 * state.coverage}>
              <rect
                x={r.bounds_level0[0] * sx}
                y={r.bounds_level0[1] * sy}
                width={r.bounds_level0[2] * sx}
                height={r.bounds_level0[3] * sy}
                fill="#d5e5dc"
                stroke="#307f74"
                strokeWidth="2"
              />
              <text x={r.bounds_level0[0] * sx + 5} y={r.bounds_level0[1] * sy + 18} fontSize="14">
                {r.id}
              </text>
            </g>
          ))}
        {patches ? (
          m.patches.map((p, i) => (
            <g key={p.id}>
              <rect
                x={p.origin_level0[0] * sx}
                y={p.origin_level0[1] * sy}
                width={p.size_level0[0] * sx}
                height={p.size_level0[1] * sy}
                fill="#eedec8"
                stroke="#b77128"
                strokeWidth="2"
              />
              <text x={p.origin_level0[0] * sx - 5} y={p.origin_level0[1] * sy + 40} fontSize="14">
                slot {i + 1}
              </text>
            </g>
          ))
        ) : coverage ? (
          m.objects.map((o) => (
            <g key={o.id} opacity={state.selections}>
              <circle
                cx={o.center_level0[0] * sx}
                cy={o.center_level0[1] * sy}
                r={o.radius_level0 * sx}
                fill={COLORS[m.teaching_classes.indexOf(o.teaching_class)]}
              />
              <text x={o.center_level0[0] * sx + 14} y={o.center_level0[1] * sy + 5} fontSize="14">
                {o.teaching_class}
              </text>
            </g>
          ))
        ) : (
          <g>
            <rect
              x={m.tile_origin_level0[0] * sx}
              y={m.tile_origin_level0[1] * sy}
              width="170"
              height="120"
              fill="#dae5e6"
              stroke="#557e93"
            />
            <circle
              cx={m.example_level0_point[0] * sx}
              cy={m.example_level0_point[1] * sy}
              r="6"
              fill="#b77128"
            />
            <text x="125" y="145" fontSize="16">
              local (70,110)
            </text>
          </g>
        )}
        {patches && state.viewport > 0 && (
          <g>
            <path d="M82 40L425 5" stroke="#557e93" strokeWidth="2" />
            <rect x="405" y="0" width="108" height="90" fill="#e0e8e9" stroke="#557e93" />
            <rect x="444" y="30" width="30" height="30" fill="#eedec8" stroke="#b77128" />
            <text x="415" y="80" fontSize="13">
              slot 1 context
            </text>
          </g>
        )}
      </g>
      <text x="35" y="390" fontSize="16">
        {patches
          ? 'Abstract positions and sizes; source crops remain above.'
          : coverage
            ? 'Hatched area: outside annotated coverage ≠ normal'
            : '(2400,1600) + 4 × (70,110) = (2680,2040)'}
      </text>
    </svg>
  );
}
export function OperationOutput({ plan, state }: { plan: StoryPlan; state: StoryState }) {
  if (state.recipe === 'topology-v1') {
    const inventory = plan.id === 'topology-inventory',
      edges = inventory
        ? graph.edges
        : graph.selected_edges.map((id) => graph.edges.find((e) => e.id === id)!);
    const count = inventory
      ? Math.floor(state.inventory * edges.length + 1e-8)
      : edges.filter(
          (e) => traceEdges(state.trace).find((x) => x.edge.id === e.id)!.points.length > 1,
        ).length;
    return (
      <aside className={styles.storyOutput}>
        <strong>{inventory ? 'Edge inventory' : 'Ordered path'}</strong>
        <p>Teaching graph is not supplied CTA input. Anatomical names remain unresolved.</p>
        <table>
          <thead>
            <tr>
              <th>Edge</th>
              <th>Connection</th>
              <th>Length (m)</th>
            </tr>
          </thead>
          <tbody>
            {edges.map((e, i) => (
              <tr key={e.id} style={{ opacity: i < count ? 1 : 0.35 }}>
                <td>{e.id}</td>
                <td>
                  {e.source} → {e.target}
                </td>
                <td>{e.length_m.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p>
          {count} / {edges.length}{' '}
          {inventory ? 'edges enumerated once' : 'connected edges traversed'}
        </p>
        <p>
          {inventory
            ? 'Output schema: branch ID, anatomical name or unknown, centerline points.'
            : 'Output schema: ordered centerline in patient coordinates. Toy coordinates here are metres.'}
        </p>
      </aside>
    );
  }
  if (state.recipe === 'correspondence-v1')
    return (
      <aside className={styles.storyOutput}>
        <strong>One fixed-from-moving transform</strong>
        <p>Constructed from P1–P3; P4–P5 are independent checks.</p>
        <pre className={styles.matrix}>
          {rigid.fixed_from_moving.map((row) => row.map((x) => x.toFixed(3)).join('  ')).join('\n')}
        </pre>
        <p>
          P2 → (
          {transformedPoint(rigid.moving_points[1])
            .map((v) => v.toFixed(4))
            .join(', ')}
          ) m
        </p>
        <table>
          <tbody>
            {rigid.held_out_ids.map((id) => {
              const i = rigid.point_ids.indexOf(id);
              return (
                <tr key={id}>
                  <td>{id} · held out</td>
                  <td>
                    {state.residual > 0 ? residualM(i).toExponential(2) + ' m' : 'check pending'}
                  </td>
                </tr>
              );
            })}
            <tr>
              <td>P6</td>
              <td>Target absent · no coordinate</td>
            </tr>
          </tbody>
        </table>
        {state.beatId === 'scope' && (
          <p>
            Deformed-target rigid residual:{' '}
            {Math.max(
              ...rigid.deformed_points.map((p, i) =>
                Math.hypot(...p.map((v, j) => v - rigid.fixed_points[i][j])),
              ),
            ).toFixed(4)}{' '}
            m (fixture).
          </p>
        )}
        <p>
          Oblique CT input is one section plus a volume. This fiducial fixture only teaches rigid
          transfer; deformation needs a different model.
        </p>
      </aside>
    );
  if (state.recipe === 'multiscale-v1')
    return (
      <aside className={styles.storyOutput}>
        <strong>
          {plan.id === 'wsi-patches'
            ? 'One unfilled output per supplied ID'
            : plan.id === 'wsi-coverage'
              ? 'Six nonclinical teaching codes'
              : 'Coordinates retain origin and scale'}
        </strong>
        {plan.id === 'wsi-patches' ? (
          <>
            <p>Real task: 256² target + 1024² context; codes 0–6, with 0 = abstention.</p>
            <div className={styles.patchSlots}>
              {m.patches.map((p, i) => (
                <div key={p.id}>
                  patch_{String(i + 1).padStart(2, '0')} <b>—</b>
                </div>
              ))}
            </div>
            <p>No labels assigned. Twelve selected locations from one slide.</p>
            <code>{'{"labels":[{"id":"patch_ID","class":…}]}'}</code>
          </>
        ) : plan.id === 'wsi-coverage' ? (
          <>
            <div className={styles.patchSlots}>
              {m.teaching_classes.map((c, i) => (
                <div key={c}>
                  <i
                    style={{
                      background: COLORS[i],
                      display: 'inline-block',
                      width: 14,
                      height: 14,
                      marginRight: 8,
                    }}
                  />
                  {c}
                </div>
              ))}
            </div>
            <p>C1–C6 are not official histotypes.</p>
            <p>Output: strip_id, class regions, polygon_level0_px, confidence, unknown regions.</p>
            <p>
              Evaluate only where the real reference provides coverage. The two rectangles here are
              synthetic.
            </p>
          </>
        ) : (
          <>
            <p>level0 = tile origin + downsample × local</p>
            <pre>
              ({m.tile_origin_level0.join(', ')}) + {m.tile_downsample} × (
              {m.example_local_point.join(', ')})
              <br />={' '}
              {state.outputs > 0
                ? `(${level0Point(m.example_local_point).join(', ')}) px`
                : 'return coordinate at the final step'}
            </pre>
            <p>
              This equation explains navigation. It does not find tumour tissue or provide evaluator
              contours.
            </p>
          </>
        )}
      </aside>
    );
  if (state.recipe === 'inverse-v1') return <InverseOutput plan={plan} state={state} />;
  return <FamilyOutput state={state} />;
}

import {
  airwayCases as cases,
  airwayMasks as masks,
  airwayOutput as outputs,
  airwayReference as refs,
  airwayColors as colors,
  airwayCaseIndex,
  airwayReveal,
  airwayReturned,
  airwaySliceIndex,
  airwayAngleIndex,
  airwayRouteIndex,
  airwayCPRRowEdges,
  airwayProject,
  type AirwayState,
} from './airway-repair';
import type { IndexedMesh } from './operation-fixtures';
import styles from './task-visual.module.css';
const path = (points: number[][]) =>
  points.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(' ');
function surface(mesh: IndexedMesh, index: number) {
  const vertices = mesh.vertices.map((p) => airwayProject(p, index));
  // A closed mesh has opposite front/back winding. Normalize in the projected
  // plane so SVG's compound nonzero fill produces their union instead of cancellation.
  return mesh.faces
    .map((face) => {
      const p = face.map((i) => vertices[i]);
      const cross =
        (p[1][0] - p[0][0]) * (p[2][1] - p[0][1]) - (p[1][1] - p[0][1]) * (p[2][0] - p[0][0]);
      return Math.abs(cross) < 1e-10 ? '' : path(cross < 0 ? p.reverse() : p) + 'Z';
    })
    .join(' ');
}
const projections = cases.map((c, i) => ({
  mask: surface(masks[c.mesh_key], i),
  added: surface(outputs[i].added_mesh, i),
  core: surface(refs[i].core_mesh, i),
}));
export function AirwayRepairScene({ state }: { state: AirwayState }) {
  const i = airwayCaseIndex(state),
    c = cases[i],
    out = outputs[i],
    projection = projections[i];
  const project = (p: number[]) => airwayProject(p, i);
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Actual airway masks and saved routes projected in native physical coordinates"
    >
      <text x="22" y="28">
        {c.id} · source patient {c.patient} · mask projection
      </text>
      <path d={projection.mask} fill={colors.input} opacity="0.7" />
      {airwayReturned(state) && (
        <g data-airway-result>
          <path d={projection.added} fill={colors.output} />
          {!['repair', 'inspect'].includes(state.scene) && (
            <path
              d={path(out.route.map(project))}
              fill="none"
              stroke={colors.output}
              strokeWidth="2.5"
            />
          )}
          {state.scene === 'route' && (
            <circle
              cx={project(out.route[airwayRouteIndex(state)])[0]}
              cy={project(out.route[airwayRouteIndex(state)])[1]}
              r="5"
              fill={colors.output}
            />
          )}
          {state.scene === 'cpr' &&
            [0, 1].map((side) => (
              <path
                key={side}
                d={path(
                  out.cpr[airwayAngleIndex(state)].sampling_edges.map((e) => project(e[side])),
                )}
                fill="none"
                stroke={colors.output}
                strokeWidth="1"
              />
            ))}
        </g>
      )}
      {airwayReveal(state) && (
        <g data-airway-reference-geometry>
          <path d={projection.core} fill={colors.reference} opacity="0.6" />
          <path
            d={path(refs[i].reference_path.map(project))}
            fill="none"
            stroke={colors.reference}
            strokeWidth="2"
            strokeDasharray="6 4"
          />
        </g>
      )}
      {c.anchors.map((p, j) => {
        const v = project(p);
        return (
          <g key={j}>
            <circle cx={v[0]} cy={v[1]} r="5" fill={colors.anchor} />
            <text x={v[0] + 9} y={v[1] - 6}>
              {j ? 'B' : 'A'}
            </text>
          </g>
        );
      })}
      <text x="22" y="410" fontSize="18">
        Fixed physical projection · overlaps do not establish connectivity
      </text>
    </svg>
  );
}
function NativeSections({ state }: { state: AirwayState }) {
  const i = airwayCaseIndex(state),
    k = airwaySliceIndex(state),
    section = cases[i].sections[k];
  const ratio =
    (section.height * Math.hypot(...section.dy_world_mm)) /
    (section.width * Math.hypot(...section.dx_world_mm));
  const width = Math.min(188, 180 / ratio),
    height = width * ratio;
  return (
    <svg
      viewBox="0 0 440 230"
      role="img"
      aria-label="Same native CT section with a separate overlay panel"
      style={{ width: '100%', maxHeight: 190 }}
    >
      {[0, 1].map((side) => (
        <g key={side}>
          <text x={15 + side * 220} y="18" fontSize="16" fill="#37473e">
            {side
              ? airwayReveal(state)
                ? 'Private core · reveal'
                : airwayReturned(state)
                  ? 'Input + saved addition'
                  : 'Public mask + edit region'
              : `CT · index ${section.index}`}
          </text>
          <image
            x={15 + side * 220}
            y="29"
            width={width}
            height={height}
            href={section.png}
            preserveAspectRatio="none"
          />
          {side === 1 && (
            <>
              <image
                x="235"
                y="29"
                width={width}
                height={height}
                href={section.proposed}
                preserveAspectRatio="none"
              />
              {!airwayReturned(state) && (
                <image
                  x="235"
                  y="29"
                  width={width}
                  height={height}
                  href={section.editable}
                  preserveAspectRatio="none"
                />
              )}
              {airwayReturned(state) && (
                <image
                  data-airway-added-slice
                  x="235"
                  y="29"
                  width={width}
                  height={height}
                  href={outputs[i].slice_added[k]}
                  preserveAspectRatio="none"
                />
              )}
              {airwayReveal(state) && (
                <image
                  data-airway-reference-image
                  x="235"
                  y="29"
                  width={width}
                  height={height}
                  href={refs[i].slice_core[k]}
                  preserveAspectRatio="none"
                />
              )}
            </>
          )}
        </g>
      ))}
      <text x="15" y="227" fontSize="13" fill="#37473e">
        HU −1000 to 200 · calibrated pixel aspect · no resampling
      </text>
    </svg>
  );
}
function CPR({ state }: { state: AirwayState }) {
  const cpr = outputs[airwayCaseIndex(state)].cpr[airwayAngleIndex(state)],
    length = cpr.arc_mm.at(-1)!;
  const width = 140,
    edges = airwayCPRRowEdges(cpr.display_arc_mm),
    scale = width / 16.25,
    height = scale * (edges.at(-1)! - edges[0]),
    y = (arc: number) => 18 + scale * (arc - edges[0]);
  return (
    <svg
      data-airway-cpr
      viewBox="0 0 440 300"
      role="img"
      aria-label="Submitted curved planar reconstruction with physical offset and arc axes"
      style={{ width: '100%', maxHeight: 240 }}
    >
      <image
        data-airway-cpr-image
        href={cpr.arc_png}
        x="50"
        y="18"
        width={width}
        height={height}
        preserveAspectRatio="none"
      />
      <line
        x1="120"
        x2="120"
        y1="18"
        y2={18 + height}
        stroke={colors.output}
        strokeDasharray="4 4"
      />
      <text x="18" y={y(0) + 5} fontSize="13">
        0
      </text>
      <text x="8" y={y(length) + 4} fontSize="13">
        {length.toFixed(1)}
      </text>
      <text x="45" y={39 + height} fontSize="13">
        −8
      </text>
      <text x="114" y={39 + height} fontSize="13">
        0
      </text>
      <text x="175" y={39 + height} fontSize="13">
        +8
      </text>
      <text x="218" y="48" fontSize="19">
        Angle {cpr.angle_deg}°
      </text>
      <text x="218" y="88" fontSize="18">
        Arc (mm) ↓
      </text>
      <text x="218" y="117" fontSize="18">
        Offset (mm) →
      </text>
      <text x="218" y="160" fontSize="18">
        8 rotations × 65 offsets
      </text>
      <text x="218" y="189" fontSize="18">
        Green centre: route
      </text>
      <text x="218" y="231" fontSize="16">
        Saved HU · arc display
      </text>
      <text x="218" y="256" fontSize="16">
        Raw samples retained
      </text>
    </svg>
  );
}
const titles = {
  inputs: 'Three supplied routes · two source patients',
  inspect: 'Inspect the actual CT and editable region',
  repair: 'Reveal the saved A01 repair',
  route: 'Trace the returned route in RAS+ mm',
  cpr: 'Rotate the saved CPR sampling plane',
  reference: 'Reveal private core and route checks',
  controls: 'Connected between anchors; detached from parent',
  comparison: 'Controls constrain what the pass means',
  limits: 'A local-route pass, with retained limitations',
};
export function AirwayRepairOutput({ state }: { state: AirwayState }) {
  const i = airwayCaseIndex(state),
    c = cases[i],
    out = outputs[i],
    ref = refs[i],
    visible = airwayReturned(state),
    reveal = airwayReveal(state);
  return (
    <aside className={styles.storyOutput} data-airway-output={state.scene} data-airway-case={c.id}>
      <strong>{titles[state.scene]}</strong>
      {['inputs', 'inspect', 'repair', 'reference'].includes(state.scene) && (
        <NativeSections state={state} />
      )}
      {state.scene === 'inputs' && (
        <>
          <p>
            <b>Supplied:</b> CT, released-model mask, editable region and ordered anchors A → B. The
            author chose the crops with reference assistance.
          </p>
          <p>
            <b>Return:</b> corrected mask, ordered centerline and 8 CPRs per request. No deletions
            or edits outside the region.
          </p>
          <small>A01/A03 share one crop. Private core and reference path start hidden.</small>
        </>
      )}
      {state.scene === 'inspect' && (
        <>
          <p>
            <b>Nine native sections</b> around the public review centre. Orange is the supplied edit
            region; blue is the predicted mask.
          </p>
          <p>
            The trace inspected CT montages and tested local intensity thresholds. No
            private-reference command was found in the retained audit.
          </p>
          <small>Reader slice sweep; not an animation of the agent's reasoning.</small>
        </>
      )}
      {state.scene === 'repair' && (
        <>
          <p data-airway-answer>
            {visible ? (
              <>
                <b>578 voxels added · 0 removed.</b> One CT &lt; −700 HU component within the
                editable region touches both anchor components.
              </>
            ) : (
              'Saved edit hidden until the reveal.'
            )}
          </p>
          <p>
            Other fragments remain. A01's whole crop changes from 7 to 6 components; this is one
            local reconnection.
          </p>
          <small>Saved final edit, not an interpolated or newly solved repair.</small>
        </>
      )}
      {state.scene === 'route' && (
        <>
          <p>
            <b>{out.route.length} ordered RAS+ points</b> follow the returned mask. The cursor is
            point {airwayRouteIndex(state) + 1}.
          </p>
          <p>
            The saved method uses a distance-to-boundary path cost, then resamples at about 0.25 mm.
          </p>
          <p>
            Required spacing is <b>0.05–0.75 mm</b>; endpoints must be within <b>1 mm</b>. Optional
            PLY meshes were author derived after the trial.
          </p>
          <small>Animation inspects saved geometry; it does not replay optimizer iterations.</small>
        </>
      )}
      {state.scene === 'cpr' && (
        <>
          <CPR state={state} />
          <p>
            The left ribbon uses saved source coordinates. HU is trilinearly sampled from the CT,
            with −1024 outside its crop.
          </p>
          <small>
            Parallel-transport normals; 45° steps. Display interpolates saved HU along arc
            positions; no new CT samples.
          </small>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <p data-airway-reference>
            {reveal ? (
              <>
                <b>433/495 core voxels = 87.47%</b> (gate ≥80%). Route p95: <b>0.449 mm</b> (gate
                ≤1.2 mm). HU error p99: <b>0.00570</b> (gate ≤0.2).
              </>
            ) : (
              'Private core, path and numerical score hidden until the reveal.'
            )}
          </p>
          <small>
            The core is GT intersected with a 1.5 mm route tube and edit region. Coverage is not
            whole-airway Dice. Original reward remains 1.
          </small>
        </>
      )}
      {state.scene === 'controls' && (
        <>
          <p>
            <b>
              {c.id} · patient {c.patient} · zero changed voxels.
            </b>{' '}
            Both anchors are inside the same {ref.connectivity.after.anchor_component_voxels[0]}
            -voxel fragment.
          </p>
          <table>
            <thead>
              <tr>
                <th>Whole crop</th>
                <th>Before</th>
                <th>After</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Components (26-neighbour)</td>
                <td>{ref.connectivity.before.components}</td>
                <td>{ref.connectivity.after.components}</td>
              </tr>
              <tr>
                <td>Anchors in largest?</td>
                <td>No</td>
                <td>No</td>
              </tr>
            </tbody>
          </table>
          <p>
            Instructions explicitly preserve already connected requested routes. The parent gap is
            outside that narrow request.
          </p>
          <p>
            <b>Control-selection limitation:</b> these are not intact parent-tree or true-absence
            controls.
          </p>
          <small>A03 shares A01's source crop and is not an independent patient.</small>
        </>
      )}
      {state.scene === 'comparison' && (
        <>
          <table>
            <thead>
              <tr>
                <th>Retained condition</th>
                <th>Outcome</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Oracle geometry + repair</td>
                <td>Pass</td>
              </tr>
              <tr>
                <td>Unchanged mask + oracle route</td>
                <td>Fail A01</td>
              </tr>
              <tr>
                <td>Image baseline v2 · tuned</td>
                <td>Pass</td>
              </tr>
              <tr>
                <td>Terra/high · one attempt</td>
                <td>Pass</td>
              </tr>
              <tr>
                <td>Postfreeze geometric shortcuts</td>
                <td>Fail A01</td>
              </tr>
            </tbody>
          </table>
          <p>
            The tuned image baseline is author development, not a blind comparison. Shortcut
            failures do not prove all geometry-only methods fail.
          </p>
          <small>
            Wrong-edit, route, arc and fabricated-HU controls also fail their retained checks.
          </small>
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <p>
            <b>Supported:</b> one saved Terra/high attempt repaired A01 and preserved two instructed
            local routes. Replayed scoring still passes.
          </p>
          <p>
            <b>Not established:</b> parent-tree completeness, named-branch identity, diagnostic
            utility or broad task difficulty.
          </p>
          <p>
            Public-source exposure, reference completeness and clinical interpretation remain
            unresolved. A revised task needs genuinely intact, absent-branch and false-connection
            controls.
          </p>
          <small>
            36 frozen files and 9 source members verified. Original scores and source bytes
            retained; no new trial or clinical adjudication.
          </small>
        </>
      )}
      <small data-airway-boundary>
        Output: {visible ? 'shown' : 'hidden'} · Private reference:{' '}
        <span data-airway-reference-state>{reveal ? 'shown' : 'hidden'}</span>
      </small>
    </aside>
  );
}

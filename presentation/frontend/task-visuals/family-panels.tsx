import { AnatomyAssets } from './anatomy';
import type { StoryState } from './story-timeline';
import { longitudinal as l, material, materialPosition } from './operation-fixtures';
import styles from './task-visual.module.css';
import supplied from '../../assets/teaching-fixtures/local-edit-v1/supplied-mask.png?inline';
import corrected from '../../assets/teaching-fixtures/local-edit-v1/corrected-mask.png?inline';
import control from '../../assets/teaching-fixtures/local-edit-v1/unchanged-control.png?inline';
export function FamilyScene({ state }: { state: StoryState }) {
  if (state.recipe === 'local-edit-v1')
    return (
      <svg
        className={styles.operationCanvas}
        viewBox="0 0 600 420"
        role="img"
        aria-label="Supplied binary grid, bounded correction, unchanged control"
      >
        <text x="25" y="32">
          {state.control > 0
            ? 'Intact control · unchanged is valid'
            : 'Constructed edit · source support not established'}
        </text>
        <image
          href={state.control > 0 ? control : supplied}
          x="25"
          y="85"
          width="250"
          height="188"
          style={{ imageRendering: 'pixelated' }}
        />
        <image
          href={state.control > 0 ? control : supplied}
          x="320"
          y="85"
          width="250"
          height="188"
          style={{ imageRendering: 'pixelated' }}
        />
        {state.control === 0 && (
          <image
            href={corrected}
            opacity={state.correction}
            x="320"
            y="85"
            width="250"
            height="188"
            style={{ imageRendering: 'pixelated' }}
          />
        )}
        {[25, 320].map((x) => (
          <rect
            key={x}
            x={x + (22 / 64) * 250}
            y={85 + (18 / 48) * 188}
            width={(8 / 64) * 250}
            height={(12 / 48) * 188}
            stroke="#b77128"
            fill="none"
            strokeWidth="3"
            opacity={state.domain}
          />
        ))}
        <text x="25" y="305">
          Input
        </text>
        <text x="320" y="305">
          {state.control > 0 ? 'Identical output' : 'Conditional fixture correction'}
        </text>
        <text x="25" y="355">
          Exterior: 0 changed cells
        </text>
        <text x="25" y="390">
          {state.control > 0
            ? 'Control: 0 changed cells'
            : 'Inside editable region: 20 constructed changes'}
        </text>
      </svg>
    );
  if (state.recipe === 'longitudinal-v1')
    return (
      <svg
        className={styles.operationCanvas}
        viewBox="0 0 600 420"
        role="img"
        aria-label="Visit-local candidates and declared identity links, including unobserved coverage"
      >
        <defs>
          <pattern id="unobserved" width="10" height="10" patternUnits="userSpaceOnUse">
            <path d="M0 10L10 0" stroke="#bcbcac" />
          </pattern>
        </defs>
        {l.visits.map((v, i) => (
          <g
            key={v.id}
            transform={`translate(${25 + i * 300} 65)`}
            opacity={i ? 0.35 + 0.65 * state.visits : 1}
          >
            <text y="-25">{v.id} · visit-local IDs</text>
            <rect width="250" height="275" fill="#eceee5" stroke="#c0c4b6" />
            {v.coverage && (
              <>
                <rect
                  x={v.coverage[2] * 250}
                  width={(1 - v.coverage[2]) * 250}
                  height="275"
                  fill="url(#unobserved)"
                />
                <text x="158" y="296" fontSize="14">
                  Not observed
                </text>
              </>
            )}
            {v.objects.map((o) => (
              <g key={o.id}>
                <circle
                  cx={o.position[0] * 250}
                  cy={o.position[1] * 275}
                  r={o.radius * 250}
                  fill={
                    state.links > 0 && o.id[0] !== 'c' && o.id[0] !== 'd' ? '#307f74' : '#a2a99c'
                  }
                />
                <text
                  x={o.position[0] * 250 + o.radius * 250 + 4}
                  y={o.position[1] * 275 + 5}
                  fontSize="16"
                >
                  {o.id}
                </text>
              </g>
            ))}
          </g>
        ))}
        {l.links
          .filter((link) => link.source && link.target)
          .map((link) => {
            const a = l.visits[0].objects.find((o) => o.id === link.source)!,
              b = l.visits[1].objects.find((o) => o.id === link.target)!;
            return (
              <line
                key={link.source}
                x1={25 + a.position[0] * 250}
                y1={65 + a.position[1] * 275}
                x2={325 + b.position[0] * 250}
                y2={65 + b.position[1] * 275}
                stroke="#557e93"
                strokeWidth="2"
                opacity={state.links}
              />
            );
          })}
        <text x="25" y="405" fontSize="16">
          Toy candidates only · no detections supplied in the actual CT task
        </text>
      </svg>
    );
  if (state.recipe === 'shape-material-v1')
    return (
      <svg
        className={styles.operationCanvas}
        viewBox="0 0 600 420"
        role="img"
        aria-label="Projected analytic shell with two material maps"
      >
        {[0, 1].map((side) => (
          <g key={side} transform={`translate(${160 + side * 280} 200)`}>
            <text x="-75" y="-145">
              Map {side ? 'B' : 'A'}
            </text>
            {Array.from({ length: 10 }, (_, j) => (
              <polyline
                key={j}
                points={Array.from({ length: 65 }, (_, i) => {
                  const p = materialPosition(i / 64, j / 10, state.phase, 0);
                  return `${p[0] * 2400},${-p[1] * 2400}`;
                }).join(' ')}
                fill="none"
                stroke="#c1c2b5"
              />
            ))}
            {Array.from({ length: 12 }, (_, j) => (
              <polyline
                key={'meridian-' + j}
                points={Array.from({ length: 65 }, (_, i) => {
                  const p = materialPosition(j / 12, i / 64, state.phase, 0);
                  return `${p[0] * 2400},${-p[1] * 2400}`;
                }).join(' ')}
                fill="none"
                stroke="#999d8e"
              />
            ))}
            {material.marker_uv.map((uv, i) => {
              const p = materialPosition(uv[0], uv[1], state.phase, side ? state.alternative : 0);
              return (
                <g key={i} opacity={state.markers}>
                  <circle
                    cx={p[0] * 2400}
                    cy={-p[1] * 2400}
                    r="6"
                    fill={['#307f74', '#b77128', '#557e93'][i]}
                  />
                  <text x={p[0] * 2400 + 8} y={-p[1] * 2400}>
                    {material.material_ids[i]}
                  </text>
                </g>
              );
            })}
          </g>
        ))}
        <text x="25" y="395">
          Same continuous surface set · different constructed trajectories
        </text>
      </svg>
    );
  if (state.recipe === 'anatomy-audit-v1')
    return (
      <svg
        className={styles.operationCanvas}
        viewBox="0 0 600 420"
        role="img"
        aria-label="Fixed projection of retained source-derived abdominal assembly"
      >
        {AnatomyAssets.get('abdomen')!.map((part) => (
          <g
            key={part.id}
            fill={part.id === 'kidney_left' && state.focus > 0 ? '#307f74' : '#bebeb0'}
            opacity={part.id === 'kidney_left' ? 1 : 0.3}
          >
            {part.faces.map((f, i) => (
              <polygon
                key={i}
                points={f
                  .map((index) => {
                    const p = part.vertices[index];
                    return `${300 + p[0] * 150},${205 - p[1] * 150}`;
                  })
                  .join(' ')}
              />
            ))}
          </g>
        ))}
        <text x="25" y="395">
          Retained s1233 assembly · same scale for all seven parts
        </text>
      </svg>
    );
  return null;
}
export function FamilyOutput({ state }: { state: StoryState }) {
  if (state.recipe === 'local-edit-v1')
    return (
      <aside className={styles.storyOutput}>
        <strong>Source support comes before an edit</strong>
        <p>Actual task: native MRA + supplied vessel mask + broad review region.</p>
        <p>This grid contains no MRA evidence. The repair remains a constructed editing example.</p>
        <table>
          <tbody>
            <tr>
              <td>Changed cells</td>
              <td>{state.control > 0 ? 0 : state.correction === 1 ? 20 : 'pending'}</td>
            </tr>
            <tr>
              <td>Outside domain</td>
              <td>0</td>
            </tr>
            <tr>
              <td>Intact control</td>
              <td>0</td>
            </tr>
          </tbody>
        </table>
        <p>
          Return a repaired mask only when source evidence supports it. A clean control returns
          unchanged.
        </p>
      </aside>
    );
  if (state.recipe === 'longitudinal-v1')
    return (
      <aside className={styles.storyOutput}>
        <strong>Identity and observation are separate</strong>
        <p>
          Two full CT volumes; no candidate locations supplied. Discovery and instance masks remain
          task work.
        </p>
        <table>
          <tbody>
            {l.links.map((link, i) => (
              <tr key={i} style={{ opacity: state.links > 0 ? 1 : 0.35 }}>
                <td>
                  {link.source ?? '—'} → {link.target ?? '—'}
                </td>
                <td>
                  {link.relation === 'same-identity'
                    ? 'Matched identity'
                    : link.relation === 'outside-followup-coverage'
                      ? 'Not observed · unknown'
                      : 'New in observed field'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <p>
          Comprehensive contract: masks, links/events, report, probability/reason row for each
          candidate.
        </p>
        <p>Toy sizes are not clinical measurements or treatment response.</p>
      </aside>
    );
  if (state.recipe === 'shape-material-v1')
    return (
      <aside className={styles.storyOutput}>
        <strong>Equal shapes ≠ identified material motion</strong>
        <p>
          Map A holds longitude. Map B shifts longitude by 0.32 t sin(πv). Both span the same
          periodic shell.
        </p>
        <table>
          <tbody>
            <tr>
              <td>Stage 0</td>
              <td>Reference motion supplied → calculations</td>
            </tr>
            <tr>
              <td>Stage 1</td>
              <td>Sparse calibrated views → motion inference</td>
            </tr>
            <tr>
              <td>Stage 1V</td>
              <td>Full volumes → motion inference</td>
            </tr>
          </tbody>
        </table>
        <p>Initial mesh and axes are assistance. Do not treat calculation as recovered motion.</p>
        <p>
          Output schema: geometry, material trajectories, deformation fields. No strain or
          physiological result is asserted here.
        </p>
      </aside>
    );
  if (state.recipe === 'anatomy-audit-v1')
    return (
      <aside className={styles.storyOutput}>
        <strong>Label + witness schema</strong>
        <p>
          Actual inputs: DICOM / CT and named spatial labels. Clean and altered cases remain
          separate.
        </p>
        <table>
          <tbody>
            <tr>
              <td>Object</td>
              <td>supplied label_id</td>
            </tr>
            <tr>
              <td>Evidence</td>
              <td>source image / spatial witness</td>
            </tr>
            <tr>
              <td>Unreviewed</td>
              <td>no conclusion yet</td>
            </tr>
            <tr>
              <td>Reviewed clean</td>
              <td>findings: [] allowed</td>
            </tr>
          </tbody>
        </table>
        <p>
          Shared anatomy: TotalSegmentator v2.0.1, Wasserthal and contributors, University Hospital
          Basel. CC BY 4.0; retained notices apply.
        </p>
        <p>The highlighted source object is not a defect finding or a scored case answer.</p>
      </aside>
    );
  return null;
}

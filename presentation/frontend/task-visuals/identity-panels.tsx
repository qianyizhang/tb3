import { identityObjects, identityRows, type IdentityState } from './identity';
import styles from './task-visual.module.css';

export function IdentityScene({ state }: { state: IdentityState }) {
  const rows = identityRows(state);
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Source-derived anonymous objects in their shared anatomical arrangement"
    >
      {identityObjects().map(({ part, objectId }, index) => (
        <g
          key={objectId}
          fill={rows[index].selected ? '#307f74' : '#b8b5a6'}
          opacity={rows[index].selected ? 1 : 0.3}
        >
          {part.faces.map((face, i) => (
            <polygon
              key={i}
              points={face
                .map((j) => {
                  const p = part.vertices[j];
                  return `${300 + p[0] * 150},${205 - p[1] * 150}`;
                })
                .join(' ')}
            />
          ))}
        </g>
      ))}
      <text x="25" y="32">
        2D projection · inspect {rows.find((row) => row.selected)!.objectId} in context
      </text>
      <text x="25" y="395">
        Seven retained objects · shared scale · no CT in this view
      </text>
    </svg>
  );
}

export function IdentityOutput({ state }: { state: IdentityState }) {
  const rows = identityRows(state);
  return (
    <aside className={styles.storyOutput} data-identity-output>
      <strong>
        {state.reveal > 0
          ? 'Source-name reveal · teaching only'
          : 'Assign one identity to every object'}
      </strong>
      <p>Supplied geometry → object-to-label mapping.</p>
      <table>
        <thead>
          <tr>
            <th>Teaching ID</th>
            <th>{state.reveal > 0 ? 'Source name' : 'Assignment'}</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.objectId} data-selected={row.selected}>
              <td style={{ color: row.selected ? '#307f74' : undefined }}>
                {row.selected ? '● ' : ''}
                {row.objectId}
              </td>
              <td data-identity-label>{row.label ?? 'unassigned'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p>
        {state.inventory > 0
          ? 'A01/A02: labels used at most once; unused labels allowed. F01: repeated labels for fragments.'
          : 'No contour reconstruction or diagnosis. Names stay hidden until the reveal chapter.'}
      </p>
      <p>Names are source metadata, not a solver result. CT assistance is condition-specific.</p>
      <small>TotalSegmentator v2.0.1 · Wasserthal et al. · CC BY 4.0.</small>
    </aside>
  );
}

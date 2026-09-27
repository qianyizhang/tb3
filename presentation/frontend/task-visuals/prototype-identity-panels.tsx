import {
  prototypeProjection,
  prototypeRows,
  type PrototypeIdentityState,
} from './prototype-identity';
import styles from './task-visual.module.css';

export function PrototypeIdentityScene({ state }: { state: PrototypeIdentityState }) {
  const rows = prototypeRows(state);
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Projected source surface points in their shared anatomical arrangement; no CT or mesh connectivity"
    >
      {rows
        .filter((row) => !row.selected)
        .map((row) => {
          const index = rows.indexOf(row);
          return (
            <path
              key={row.objectId}
              d={prototypeProjection[index]}
              fill="none"
              stroke="#8c9589"
              strokeWidth="1"
              strokeLinecap="round"
              opacity="0.27"
            />
          );
        })}
      {rows
        .filter((row) => row.selected)
        .map((row) => {
          const index = rows.indexOf(row);
          return (
            <path
              key={row.objectId}
              d={prototypeProjection[index]}
              fill="none"
              stroke="#307f74"
              strokeWidth="1.8"
              strokeLinecap="round"
            />
          );
        })}
      <text x="24" y="28">
        Shared-frame projection · inspect {rows.find((r) => r.selected)!.objectId}
      </text>
      <text x="24" y="395">
        Sampled boundary points · 17 objects · no faces or CT
      </text>
    </svg>
  );
}

export function PrototypeIdentityOutput({ state }: { state: PrototypeIdentityState }) {
  const rows = prototypeRows(state);
  return (
    <aside className={styles.storyOutput} data-prototype-output>
      <strong>
        {state.reveal > 0
          ? 'Private source-key reveal · reader only'
          : '17 objects → 17 assignments'}
      </strong>
      <p>
        {state.inventory > 0
          ? '117 allowed names; no proposed labels or CT. I2 asks only for identity.'
          : 'Shared position, orientation and scale; the highlight adds no identity.'}
      </p>
      <div className={styles.prototypeAssignments}>
        {rows.map((row) => (
          <div key={row.objectId} data-prototype-selected={row.selected}>
            <b style={{ color: row.selected ? '#307f74' : undefined }}>{row.objectId}</b>
            <span data-prototype-label>{row.label ?? 'unassigned'}</span>
          </div>
        ))}
      </div>
      <p>
        {state.reveal > 0
          ? 'These are retained source labels, not agent predictions or clinical adjudication.'
          : 'assignments.json: one object_id + label per ID. Names hidden until reveal.'}
      </p>
      <small>BR-011 I2 · case 32 · no trials. TotalSegmentator · CC BY 4.0 / Apache 2.0.</small>
    </aside>
  );
}

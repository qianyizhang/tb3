import {
  screenKey,
  screenRows,
  screenPaths,
  screenProject,
  screenColor,
  screenReference,
  type MaskScreenState,
} from './mask-screen';
import styles from './task-visual.module.css';
const short = (label: string | null) => label?.replace('rib_left_', 'L rib ') ?? '—';

export function MaskScreenScene({ state }: { state: MaskScreenState }) {
  const key = screenKey(state),
    rows = screenRows(state),
    selected = rows.find((r) => r.selected)!;
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Source-derived point projection and occupancy centroids; connecting centroids is an ordering aid, not an anatomical attachment"
    >
      {rows.map((row) => (
        <path
          key={row.id}
          d={screenPaths[key][row.id]}
          fill="none"
          stroke={screenColor(row)}
          strokeWidth={row.selected || row.wrong ? 1.8 : 1}
          strokeLinecap="round"
          opacity={row.selected || row.wrong ? 1 : 0.4}
        />
      ))}
      {state.measure > 0 && key !== 'organs-32' && (
        <g opacity={state.measure}>
          <polyline
            points={rows.map((r) => screenProject(key, r.centroid_lps_mm).join(',')).join(' ')}
            stroke="#b77128"
            strokeWidth="2"
            fill="none"
            strokeDasharray="5 4"
          />
          {rows.map((row) => {
            const [x, y] = screenProject(key, row.centroid_lps_mm);
            return (
              <g key={row.id}>
                <circle cx={x} cy={y} r="4" fill="#b77128" />
                <text x={x + 9} y={y + 5} fontSize="13">
                  {row.rank}
                </text>
              </g>
            );
          })}
        </g>
      )}
      <text x="24" y="28">
        {key} · shared-frame source projection
      </text>
      <text x="24" y="385">
        {selected.id.split('-').at(-1)}
        {selected.predicted ? ` → ${short(selected.predicted)}` : ' · no prediction yet'}
      </text>
      <text x="24" y="407" fontSize="13">
        Sampled source points · no faces · separate scenes are not registered
      </text>
    </svg>
  );
}

export function MaskScreenOutput({ state }: { state: MaskScreenState }) {
  const key = screenKey(state),
    rows = screenRows(state);
  const organ = screenReference.organ_baseline;
  const example = screenReference.feature_example;
  return (
    <aside className={styles.storyOutput} data-mask-screen-output>
      {state.scene === 'context' ? (
        <>
          <strong>Check the reasoning claim first</strong>
          <p>
            BR-010 reviewed seven historical tool trajectories. They already contain quantitative
            and relational checks.
          </p>
          <ul className={styles.screenNotes}>
            <li>
              <b>Counterexample:</b> Terra repaired exchanged ribs using fragment distances and
              opposite-side matching.
            </li>
            <li>
              <b>Unresolved:</b> Sol found a numeric signal in a planted kidney extension, then
              returned an empty report. Clinical significance was unvalidated.
            </li>
            <li>
              <b>Next author step:</b> screen cheap geometric baselines before proposing a difficult
              mask-only task.
            </li>
          </ul>
          <p>
            No new model trials. The rib view is case-32 source context, not Terra's case-28
            evidence.
          </p>
        </>
      ) : state.scene === 'admission' ? (
        <>
          <strong>Output: a bounded author assessment</strong>
          <ul className={styles.screenNotes}>
            <li>
              <b>I1 · proposed labels:</b> 23/24 groups admit simple ordering. Screen these out as
              difficulty leads.
            </li>
            <li>
              <b>I2 · anonymous objects:</b> 109/131 identities; 0/8 complete scenes. A residual
              error does not establish a fair hard task.
            </li>
            <li>
              <b>I3 · identity + quality:</b> needs verified unusual anatomy and independent review
              from solver inputs.
            </li>
          </ul>
          <p>
            Short or unusual shape alone cannot distinguish real anatomy from an annotation
            omission.
          </p>
          <p>
            Require a unique answer, clean controls and alternative-assignment checks before
            freezing a trial.
          </p>
        </>
      ) : key === 'organs-32' ? (
        <>
          <strong>Author baseline · leave one patient out</strong>
          <p>Seven geometric features → median templates from seven training patients.</p>
          {state.reference === 0 ? (
            <>
              <p>
                <b>Case 32 · object o1</b> · features from full occupancy
              </p>
              <table className={styles.screenTable} data-screen-features>
                <tbody>
                  <tr>
                    <th>Centroid / scan extents</th>
                    <td>
                      {example.features
                        .slice(0, 3)
                        .map((v) => v.toFixed(3))
                        .join(', ')}
                    </td>
                  </tr>
                  <tr>
                    <th>ln volume (mm³)</th>
                    <td>{example.features[3].toFixed(3)}</td>
                  </tr>
                  <tr>
                    <th>ln box extents (mm)</th>
                    <td>
                      {example.features
                        .slice(4)
                        .map((v) => v.toFixed(3))
                        .join(', ')}
                    </td>
                  </tr>
                </tbody>
              </table>
              <p>Nearest templates · standardized squared distance</p>
              <table className={styles.screenTable}>
                <tbody>
                  {example.nearest_templates.map((r, i) => (
                    <tr key={r.label}>
                      <th>{state.prediction > 0 ? r.label : 'pending'}</th>
                      <td>
                        {state.prediction > 0 ? r.squared_distance.toFixed(3) : '—'}
                        {state.prediction > 0 && i === 0 ? ' · minimum' : ''}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p>Choose the minimum distance; no one-to-one assignment or parameter search.</p>
            </>
          ) : (
            <>
              <div
                className={styles.screenBars}
                aria-label="Correct identities by held-out patient"
              >
                {organ.rows.map((r) => (
                  <div key={r.case_id}>
                    <span>Case {r.case_id}</span>
                    <div>
                      <i style={{ width: `${(100 * r.correct) / r.total}%` }} />
                    </div>
                    <b>
                      {r.correct}/{r.total}
                    </b>
                  </div>
                ))}
              </div>
              <p>
                <b>
                  {organ.correct}/{organ.total}
                </b>{' '}
                identities · <b>0/8</b> complete scenes.
              </p>
              <p data-mask-screen-reference>
                {state.reference > 0
                  ? 'Case 32: spleen → stomach. Source disagreement.'
                  : 'Case 32 predictions appear in the selected-object callout. Source comparison is hidden.'}
              </p>
            </>
          )}
          <small>Training labels were unavailable to I2 solvers; eight clustered patients.</small>
        </>
      ) : (
        <>
          <strong>Order left ribs by superior centroid</strong>
          <p>
            Family and label multiset are given. Compute centroids from full occupancy; assign names
            in descending S order.
          </p>
          <table className={styles.screenTable}>
            <thead>
              <tr>
                <th>Object</th>
                <th>S (mm)</th>
                <th>Sort label</th>
                <th>Source key</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} data-screen-wrong={row.wrong} data-screen-selected={row.selected}>
                  <td>{row.id.split('-').at(-1)}</td>
                  <td>{state.measure > 0 ? row.centroid_lps_mm[2].toFixed(1) : '—'}</td>
                  <td data-screen-prediction>{short(row.predicted)}</td>
                  <td data-screen-reference>{short(row.source)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            <b>23/24 groups</b> correct across eight source patients.
          </p>
          <p>
            {key === 'ribs-74'
              ? 'Case 74: ribs 8/9 reverse order. Limited coverage needs review; no hard task is admitted.'
              : 'Case 32: all six agree. Simple ordering undoes a label permutation.'}
          </p>
        </>
      )}
      <small className={styles.screenCredit}>
        Retained BR-010/011 author study · no new trials. TotalSegmentator · CC BY 4.0 / Apache 2.0.
      </small>
    </aside>
  );
}

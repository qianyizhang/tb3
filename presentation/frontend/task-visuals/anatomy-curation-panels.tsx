import {
  curationRows,
  curationScanName,
  curationPaths,
  curationProject,
  curationColor,
  curationReference,
  curationGeometry,
  curationKeys,
  type CurationState,
} from './anatomy-curation';
import styles from './task-visual.module.css';

export function CurationScene({ state }: { state: CurationState }) {
  const rows = curationRows(state),
    selected = rows.find((r) => r.selected)!;
  const [x, y] = curationProject(selected.centroid);
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Source vertebral boundary points; separate scans independently fitted, not registered"
    >
      {rows.map((r) => (
        <path
          key={r.key + r.id}
          d={curationPaths[state.scene][r.key + r.id]}
          fill="none"
          stroke={curationColor(r)}
          strokeWidth={r.selected ? 2 : 1.2}
          opacity={r.selected ? 1 : 0.6}
          strokeLinecap="round"
        />
      ))}
      <text x="20" y="24">
        {curationKeys[state.scene].map(curationScanName).join(' / ')} · source masks
      </text>
      <circle cx={x} cy={y} r="5" fill="none" stroke="#a34555" strokeWidth="2" />
      <text x="20" y="395">
        {selected.id}
        {selected.source ? ` · source ${selected.source}` : ' · source name hidden'}
      </text>
      <text x="20" y="414" fontSize="12">
        Sampled points · no faces · each scan fitted independently
      </text>
    </svg>
  );
}

const names = {
  pair: 'C01 · equal counts, different source partitions',
  preservation: 'C02 · preserve an unusual source structure',
  overlap: 'C02 · separate grids and an unresolved anchor',
  calibration: 'C03 · typical numbering is calibration',
  reserve: 'C04 · keep the cropped scan in reserve',
  ambiguity: 'C05 · reject an exact mask-only key',
  admission: 'Five candidate cards · zero hard tasks admitted',
};
export function CurationOutput({ state }: { state: CurationState }) {
  const reveal = state.reference > 0.5,
    keys = curationKeys[state.scene];
  return (
    <aside className={styles.storyOutput} data-curation-output>
      <strong>{names[state.scene]}</strong>
      {state.scene === 'pair' ? (
        <>
          <p>
            547 and 585 each contain <b>25</b> vertebral objects. The source masks contain no ribs
            or sacrum.
          </p>
          <table className={styles.screenTable}>
            <thead>
              <tr>
                <th>Source scan</th>
                <th>547</th>
                <th>585</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th>Source C / T / L</th>
                {keys.map((k) => (
                  <td key={k} data-curation-reference>
                    {reveal
                      ? curationReference[k].curation.source_segmented_counts.join(' / ')
                      : 'hidden'}
                  </td>
                ))}
              </tr>
              <tr>
                <th>Supplied-multiset sort</th>
                {keys.map((k) => (
                  <td key={k}>{reveal ? `${curationReference[k].multiset_correct}/25` : '—'}</td>
                ))}
              </tr>
              <tr>
                <th>Fixed 12T + true top anchor</th>
                {keys.map((k) => (
                  <td key={k}>{reveal ? `${curationReference[k].fixed_correct}/25` : '—'}</td>
                ))}
              </tr>
              <tr>
                <th>Voxel spacing (mm)</th>
                {keys.map((k) => (
                  <td key={k}>
                    {curationGeometry[k].spacing_mm.map((v) => v.toFixed(2)).join(' × ')}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
          <p>
            {reveal
              ? 'The multiset gives away the regional counts. A true top anchor alone does not resolve 547’s additional thoracic level.'
              : 'Two different patients, independently displayed. Their equal count does not identify the thoracic/lumbar boundary.'}
          </p>
          <p>
            <b>Pending:</b> anonymous rib context or blind evidence that supplied facet geometry
            uniquely supports the source convention.
          </p>
          <small>
            Cross-patient comparison; unequal sampling. No matched intervention or model trial.
          </small>
        </>
      ) : state.scene === 'preservation' ? (
        <>
          <p>
            406 lower scan · focused T9–T11 source geometry. Original positions and shapes are
            retained.
          </p>
          <table className={styles.screenTable}>
            <thead>
              <tr>
                <th>Source level</th>
                <th>Full-mask volume</th>
              </tr>
            </thead>
            <tbody>
              {curationRows(state).map((r) => (
                <tr key={r.id}>
                  <td data-curation-reference>{r.source}</td>
                  <td>{r.volume_ml.toFixed(2)} mL</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            <b>T10 is 0.334×</b> the mean volume of T9 and T11. This size check was made after
            inspection.
          </p>
          <p>
            Small size already flags the region. It cannot decide whether the anatomy is faithful or
            the annotation is wrong.
          </p>
          <small>
            No injected error; no frozen disease/error key or independent clinical adjudication.
          </small>
        </>
      ) : state.scene === 'overlap' ? (
        <>
          <p>
            406 upper scan: <b>9</b> identities. Lower scan: <b>19</b>. C7, T1 and T2 overlap.
          </p>
          <p>
            Each scan has its own image grid. These views do not establish alignment or support
            fusion.
          </p>
          <p>
            <b>Unresolved source discrepancy:</b> the upper mask contains C1, but its centroid JSON
            has no C1 entry.
          </p>
          <p>
            The source’s assumed segment structure <b>7 / 11.5 / 6 / 5</b> differs from the
            segmented C / T / L counts <b>7 / 12 / 6</b>.
          </p>
          <small>Do not use the upper scan as an unquestioned anchor key.</small>
        </>
      ) : state.scene === 'calibration' ? (
        <>
          <p>
            823: <b>24</b> identities, source partition <b>7C / 12T / 5L</b>.
          </p>
          <p>
            Both supplied-multiset sorting and fixed-12T sorting with a true top anchor recover{' '}
            <b>24/24</b>.
          </p>
          <p>
            This is a useful typical-numbering control. It does not certify absence of pathology.
          </p>
          <p>
            <b>Decision:</b> calibration only; not a difficult recognition candidate.
          </p>
        </>
      ) : state.scene === 'reserve' ? (
        <>
          <p>
            642: <b>20</b> objects, <b>C5–C7 + 11T + 6L</b>. Upper cervical coverage is cropped.
          </p>
          <table className={styles.screenTable}>
            <tbody>
              <tr>
                <th>Supplied-multiset sort</th>
                <td>20/20</td>
              </tr>
              <tr>
                <th>Fixed 12T + true top anchor</th>
                <td>14/20</td>
              </tr>
            </tbody>
          </table>
          <p>
            Approximately <b>3 mm left–right sampling</b>; no ribs or sacrum in the supplied masks.
          </p>
          <p>
            <b>Pending:</b> anchor, morphology and nomenclature checks. A baseline error alone does
            not qualify a task.
          </p>
        </>
      ) : state.scene === 'ambiguity' ? (
        <>
          <p>
            581 is explicitly ambiguous in the source paper. Its reported Castellvi category is 3b.
          </p>
          <p>
            The source assumes six lumbar levels but segments only five lumbar instances. Partly
            sacral-fused vertebrae may intentionally be unsegmented.
          </p>
          <p>
            <b>Decision:</b> reject an exact mask-only answer key. Do not label this as a discovered
            missing-object defect.
          </p>
          <p>
            A future uncertainty task needs a defensible set of acceptable answers and independent
            review.
          </p>
        </>
      ) : (
        <>
          <table className={styles.screenTable}>
            <tbody>
              <tr>
                <th>C01 · 547 / 585</th>
                <td>Needs context</td>
              </tr>
              <tr>
                <th>C02 · 406</th>
                <td>Preservation candidate</td>
              </tr>
              <tr>
                <th>C03 · 823</th>
                <td>Calibration only</td>
              </tr>
              <tr>
                <th>C04 · 642</th>
                <td>Reserve</td>
              </tr>
              <tr>
                <th>C05 · 581</th>
                <td>Reject exact key</td>
              </tr>
            </tbody>
          </table>
          <p>
            <b>6 patients · 7 volumes · 145 mask instances</b>, including three repeated identities
            in 406. Author screens: multiset <b>145/145</b>; fixed-12T <b>128/145</b>.
          </p>
          <p>
            <b>0 admitted hard tasks · 0 model trials.</b> No injected-error controls or clinical
            disease gold added.
          </p>
          <small>
            Reopen with missing context, independent input-only review, acceptable-answer rules and
            verified controls.
          </small>
        </>
      )}
      <small className={styles.screenCredit}>
        VerSe · Sekuboyina / Liebl / Schinz et al. · source-derived view, CC BY-SA 4.0. Retained
        BR-012 author screen.
      </small>
    </aside>
  );
}

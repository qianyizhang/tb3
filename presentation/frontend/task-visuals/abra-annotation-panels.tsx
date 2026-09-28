import {
  abraInputs as src,
  abraReference as ref,
  abraSelection,
  abraPixel,
  abraLps,
  type AbraState,
} from './abra-annotation';
import styles from './task-visual.module.css';

function Native({
  k = 66,
  crop = false,
  reference = false,
  output = false,
  oracle = false,
  witness = false,
}: {
  k?: number;
  crop?: boolean;
  reference?: boolean;
  output?: boolean;
  oracle?: boolean;
  witness?: boolean;
}) {
  const v = (crop ? ref.crops : src.full).find((v) => v.k === k)!;
  const frame = ref.frames.find((v) => v.k === k),
    width = crop ? 111 : 512;
  const path = frame?.polygon.map((p) => abraPixel(p, crop).join(',')).join(' ');
  return (
    <figure className={styles.abraImage} data-abra-native={`${crop ? 'crop' : 'full'}-${k}`}>
      <svg
        viewBox={`0 0 ${width} ${width}`}
        role="img"
        aria-label={`Native axial CT, slice ${k}${crop ? ', reader-selected crop' : ', full field'}`}
      >
        <image href={v.png} width={width} height={width} />
        {reference && (
          <polyline
            data-abra-reference
            points={path}
            fill="none"
            stroke="#37c9bc"
            strokeWidth={crop ? 0.75 : 1.8}
          />
        )}
        {oracle && (
          <polyline
            data-abra-oracle
            points={path}
            fill="none"
            stroke="#78afff"
            strokeWidth={crop ? 0.9 : 2.2}
            strokeDasharray={crop ? '1.3 1.3' : '3 3'}
          />
        )}
        {output && (
          <polyline
            data-abra-output
            points={path}
            fill="none"
            stroke="#ffc35b"
            strokeWidth={crop ? 0.9 : 2.2}
            strokeDasharray={crop ? '3 2' : '7 5'}
          />
        )}
        {witness && (
          <g data-abra-witness stroke="white" strokeWidth="1.6">
            <path d="M119.5 256.5h18 M128.5 247.5v18" fill="none" />
          </g>
        )}
        {!crop && (
          <g fill="white" fontSize="14">
            <text x="7" y="262">
              R
            </text>
            <text x="493" y="262">
              L
            </text>
          </g>
        )}
      </svg>
      <figcaption>
        <b>
          Slice {k} · {crop ? 'reader crop' : '512 × 512 native pixels'}
        </b>
        <span>
          {crop ? 'Origin (313,292) · 111 × 111 pixels' : 'Lung window · WW 1500 / WC −600 HU'}
        </span>
      </figcaption>
    </figure>
  );
}

export function AbraScene({ state: s }: { state: AbraState }) {
  const sel = abraSelection(s),
    f = ref.frames[sel.frame],
    score = ref.scorer_arithmetic[sel.field];
  let title = '',
    body;
  switch (s.scene) {
    case 'inputs':
      title = 'One native examination, a specified slice';
      body = (
        <div className={styles.abraColumns}>
          <Native k={0} />
          <div>
            <p className={styles.abraKicker}>ORDINARY CONDITION</p>
            <h4>LIDC-IDRI-0003 · Nodule 1</h4>
            <p>140 acquired axial slices. Initial viewer slice: 0.</p>
            <p>
              Prompt: navigate to <strong>slice 66</strong>, set the lung window, then outline the
              nodule using a circle or polygon.
            </p>
            <p className={styles.abraCallout}>
              The slice and window are supplied. The boundary, mask and target coordinates are not.
            </p>
            <p>15-turn limit · visual boundary judgment required.</p>
          </div>
        </div>
      );
      break;
    case 'navigate':
      title = 'Navigation does not determine the boundary';
      body = (
        <div className={styles.abraColumns}>
          <Native k={sel.k} />
          <div>
            <p className={styles.abraKicker}>TEACHING NAVIGATION · NOT AN AGENT TRACE</p>
            <div className={styles.abraSteps}>
              {[0, 64, 66].map((k) => (
                <span key={k} data-current={sel.k === k}>
                  slice {k}
                </span>
              ))}
            </div>
            <p>
              Open the CT series, select the requested zero-based slice and apply the lung window.
            </p>
            <code>
              set_viewport_slice(66)
              <br />
              set_window_level(1500, −600)
              <br />
              get_dicom_image(..., 66)
            </code>
            <p>
              These are illustrative tool intents. No OHIF session or model attempt is being
              replayed.
            </p>
            <p className={styles.abraCallout}>
              A successful navigation call is separate from a correct outline.
            </p>
          </div>
        </div>
      );
      break;
    case 'coordinates':
      title = 'Keep the image, slice and pixel coordinates together';
      body = (
        <div className={styles.abraColumns}>
          <Native witness />
          <div>
            <p className={styles.abraKicker}>COORDINATE WITNESS · NOT A LESION HINT</p>
            <h4>(x, y) = (128, 256)</h4>
            <p>x is column; y is row. Both are zero-based image-pixel centers.</p>
            <p>Source spacing: 0.820312 mm in both image axes. Slice step: 2.5 mm.</p>
            <code>
              LPS mm:{' '}
              {abraLps([128, 256], 66)
                .map((v) => v.toFixed(3))
                .join(', ')}
            </code>
            <p>
              Annotations attach to a slice in the active image series. Crop-local coordinates must
              be translated back to native pixels.
            </p>
          </div>
        </div>
      );
      break;
    case 'reference':
      title = sel.reference
        ? 'The private reference has a recoverable source'
        : 'The ordinary solver does not receive this reference';
      body = sel.reference ? (
        <>
          <div className={styles.abraColumns}>
            <Native reference />
            <Native k={f.k} crop reference />
          </div>
          <p className={styles.abraCallout} data-abra-reference-info>
            Reader reference · Nodule 1 / Annotation 12 · Slice {f.k}: {f.pixels} pixels. One
            annotator; the 50% rule reproduces its mask.
          </p>
          <p>
            Left: task slice 66. Right: source slices 62–69. UID and geometry aligned; crop selected
            from reference.
          </p>
        </>
      ) : (
        <>
          <div className={styles.abraColumns}>
            <Native />
            <div className={styles.abraHidden}>
              <h4>Reference hidden</h4>
              <p>
                CT and slice hint remain visible. Source masks, contour coordinates and the
                reader-selected crop appear only after this reveal.
              </p>
            </div>
          </div>
          <p>Private evaluation geometry is separate from ordinary solver assistance.</p>
        </>
      );
      break;
    case 'ordinary':
      title = 'An annotation carries geometry and an attachment';
      body = (
        <div className={styles.abraColumns}>
          <Native crop reference={sel.reference} output={sel.output} />
          <div>
            <p className={styles.abraKicker}>AUTHOR REFERENCE-COPY EXAMPLE</p>
            <code>
              add_polygon_segmentation
              <br />
              {'{'} label: "Nodule 1",
              <br /> slice_index: 66,
              <br /> points: [[x, y], …] {'}'}
            </code>
            <p>
              The yellow dashed polygon copies the reference to explain the output contract. It is
              not an ordinary agent answer.
            </p>
            <p className={styles.abraCallout}>
              In the actual ordinary task, the agent must determine its own boundary from the image.
            </p>
            <p>
              The tool declares a segmentation ID, segment index, slice index and filled-pixel
              count.
            </p>
          </div>
        </div>
      );
      break;
    case 'oracle':
      title = 'Oracle assistance supplies the boundary';
      body = (
        <div className={styles.abraColumns}>
          <Native crop oracle={sel.helper} output={sel.output} />
          <div>
            <p className={styles.abraKicker}>SEPARATE ORACLE CONDITION · 10 TURNS</p>
            <ol className={styles.abraOracleSteps}>
              <li>Query overview: Nodule 1, slices 62–69, representative slice 66.</li>
              <li data-abra-helper-info={sel.helper ? 'visible' : 'hidden'}>
                {sel.helper
                  ? 'Query slice 66: return source-derived polygon points.'
                  : 'Contour query has not been revealed.'}
              </li>
              <li>
                {sel.output
                  ? 'Transfer those native points to a slice-66 annotation.'
                  : 'Annotation transfer follows the contour query.'}
              </li>
            </ol>
            <p>
              The “pathology model” is simulated from the prepared reference. Its 0.95 overview
              confidence is hardcoded, not measured calibration.
            </p>
            <p className={styles.abraCallout}>
              Boundary judgment and supplied-contour transfer are different conditions.
            </p>
          </div>
        </div>
      );
      break;
    case 'scoring':
      title = 'Outcome scoring is not a strict attachment check';
      body = (
        <>
          <div className={styles.abraScoreColumns}>
            <div>
              <p className={styles.abraKicker}>SAME REFERENCE POLYGON · ANALYTICAL IoU = 1</p>
              <table data-abra-score>
                <thead>
                  <tr>
                    <th>Slice offset</th>
                    <th>Penalty</th>
                    <th>Outcome</th>
                    <th>≥ 0.5</th>
                  </tr>
                </thead>
                <tbody>
                  {ref.scorer_arithmetic.map((r, i) => (
                    <tr key={i} data-current={i === sel.field}>
                      <td>
                        {r.delta === null
                          ? 'Missing index*'
                          : r.delta === 0
                            ? 'Correct slice'
                            : `+${r.delta} slice${r.delta === 1 ? '' : 's'}`}
                      </td>
                      <td>{r.penalty.toFixed(1)}</td>
                      <td>{r.reference_copy_polygon_score.toFixed(1)}</td>
                      <td>{r.reference_copy_polygon_score >= 0.5 ? 'hit' : 'miss'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div>
              <h4 data-abra-score-value>{score.reference_copy_polygon_score.toFixed(1)} outcome</h4>
              <p>
                For polygons: max(IoU − slice penalty, 0). Circle and rectangle scores are divided
                by a reference-derived shape heuristic, capped at 1.
              </p>
              <p>
                Adjacent-slice copies can meet the hit threshold. *A missing index has zero scorer
                penalty, although the annotation tool requires that field.
              </p>
              <p>
                Shown values combine exact polygon identity with the pinned penalty function. Full
                Shapely scoring and viewer execution were not run.
              </p>
            </div>
          </div>
          <p className={styles.abraCallout}>
            Overall benchmark score = 0.20 planning + 0.30 execution + 0.50 outcome. No overall or
            model score is shown.
          </p>
        </>
      );
      break;
    case 'limits':
      title = 'What this source-backed explanation establishes';
      body = (
        <div className={styles.abraLimits}>
          <article>
            <b>Actual source</b>
            <p>
              One CT series, one source annotator, eight aligned mask frames. Selected native views
              preserve pixels and physical scale.
            </p>
          </article>
          <article>
            <b>Recovered condition</b>
            <p>
              Ordinary s066 and oracle Nodule 1 definitions regenerated from pinned pure functions.
              Other nodules and task families remain separate.
            </p>
          </article>
          <article>
            <b>Teaching examples</b>
            <p>
              Navigation, reference-copy output and scorer arithmetic illustrate the contract. They
              are not a retained agent trace or model result.
            </p>
          </article>
          <article>
            <b>Remaining evidence limits</b>
            <p>
              No live OHIF run, full benchmark replay, diagnostic adjudication or population
              performance claim. Source contour agreement is not clinical truth.
            </p>
          </article>
        </div>
      );
  }
  return (
    <section
      className={styles.abraScene}
      data-abra-scene={s.scene}
      data-abra-reference-visible={sel.reference}
    >
      <h3>{title}</h3>
      {body}
    </section>
  );
}

export function AbraOutput({ state: s }: { state: AbraState }) {
  return (
    <aside className={styles.abraAside}>
      <b>Annotation operation</b>
      <p>Image + slice hint → boundary → attached annotation</p>
      <b>{s.scene === 'oracle' ? 'Oracle condition' : 'Ordinary condition'}</b>
      <p>
        {s.scene === 'oracle'
          ? 'Reference contour returned through a tool.'
          : 'Slice 66 and lung window; reference stays private.'}
      </p>
      <b>Source scope</b>
      <p>
        One CT and Nodule 1.
        <br />
        No model or OHIF run.
      </p>
      <small>
        Teal solid: reader reference. Yellow dashed: reference-copy example. Blue dotted: supplied
        oracle contour. White cross: coordinate witness.
      </small>
    </aside>
  );
}

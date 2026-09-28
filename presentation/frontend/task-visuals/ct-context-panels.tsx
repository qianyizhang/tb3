import {
  contextInputs as src,
  contextOutput as out,
  contextReference as ref,
  contextFields,
  contextSelection,
  contextPixel,
  type CtContextState,
} from './ct-context';
import styles from './task-visual.module.css';
function Pair({ region, mark = false }: { region: string; mark?: boolean }) {
  return (
    <div className={styles.contextPair}>
      {src.images
        .filter((v) => v.region === region)
        .map((v) => (
          <figure key={v.id} data-context-image={v.id}>
            <svg
              viewBox={`0 0 ${v.width} ${v.height}`}
              role="img"
              aria-label={`${v.visit} CT, native k=${v.k}; i right, j down`}
            >
              <image href={v.png} width={v.width} height={v.height} />
              {mark &&
                v.point &&
                (() => {
                  const [x, y] = contextPixel(v, v.point!);
                  return (
                    <path
                      data-context-point
                      d={`M${x - 7} ${y}h14 M${x} ${y - 7}v14`}
                      stroke="#ffc35b"
                      strokeWidth="1.4"
                    />
                  );
                })()}
              {mark && v.roi && (
                <rect
                  data-context-region
                  x={v.roi[0] - v.bounds[0]}
                  y={v.roi[2] - v.bounds[2]}
                  width={v.roi[1] - v.roi[0]}
                  height={v.roi[3] - v.roi[2]}
                  fill="none"
                  stroke="#ffc35b"
                  strokeWidth="1.4"
                  strokeDasharray="5 3"
                />
              )}
            </svg>
            <figcaption>
              <b>
                {v.visit === 'baseline' ? 'Baseline' : 'Follow-up'} · k={v.k}
              </b>
              <span>
                {mark
                  ? v.point
                    ? `Cited point (${v.point.join(', ')}, ${v.k})`
                    : 'Cited groin region · dashed box'
                  : `Selected native crop · ${v.width} × ${v.height} pixels`}
              </span>
            </figcaption>
          </figure>
        ))}
    </div>
  );
}
export function CtContextScene({ state }: { state: CtContextState }) {
  const sel = contextSelection(state),
    f = contextFields[sel.field],
    record = out.fields[f[0]];
  let title = '',
    body;
  switch (state.scene) {
    case 'inputs':
      title = 'Two CT volumes, no clinical record';
      body = (
        <>
          <Pair region="liver" />
          <p>
            Earlier and later scans of one patient. The agent received full volumes and headers;
            these are reader crops at its subsequently cited planes.
          </p>
          <p className={styles.contextCallout}>
            No diagnosis, dates, demographics, evidence points, masks or prior output were supplied.
          </p>
        </>
      );
      break;
    case 'headers':
      title = 'Geometry is available; clinical history is absent';
      body = (
        <>
          <div className={styles.contextCards}>
            {src.geometry.map((g) => (
              <article key={g.visit}>
                <b>{g.visit}.nii.gz</b>
                <p>{g.shape.join(' × ')} voxels</p>
                <p>{g.spacing_mm.join(' × ')} mm</p>
                <p>L / P / S increasing native axes</p>
                <code>
                  descrip = empty
                  <br />
                  aux_file = empty
                  <br />
                  intent_name = empty
                  <br />
                  extensions = {g.extensions}
                </code>
              </article>
            ))}
          </div>
          <p className={styles.contextCallout}>
            RAS affine origins describe spatial millimeters. They do not encode elapsed time or
            register anatomy between scans.
          </p>
          <p>
            These cleaned files contain no acquisition dates, age or recorded sex. File modification
            time is not a scan date.
          </p>
        </>
      );
      break;
    case 'liver':
      title = 'Connect an image observation to a bounded claim';
      body = (
        <>
          <Pair region="liver" mark />
          <div className={styles.contextChain}>
            <article>
              <b>Observed appearance</b>
              <p>Low-attenuation liver abnormalities; larger visible later burden.</p>
            </article>
            <span>→</span>
            <article>
              <b>Retained inference · 0.91</b>
              <p>Suspected metastatic malignancy.</p>
            </article>
          </div>
          <p className={styles.contextCallout}>
            Primary diagnosis remains unknown. Melanoma is an alternative, not an identified
            histology. No formal response measurement was performed.
          </p>
        </>
      );
      break;
    case 'surgery':
      title = 'A scar-like appearance is not an operative record';
      body = (
        <>
          <Pair region="groin" mark />
          <div className={styles.contextChain}>
            <article>
              <b>Retained inference · 0.76</b>
              <p>Probable prior right inguinal/local intervention.</p>
            </article>
            <span>?</span>
            <article>
              <b>Still unresolved</b>
              <p>Procedure, indication, timing and nonsurgical alternatives.</p>
            </article>
          </div>
          <p className={styles.contextCallout}>
            The agent cited tethering and linear stranding. No individual surgical record is
            available to adjudicate its suggestion.
          </p>
        </>
      );
      break;
    case 'fields':
      title = 'Write an evidence status for every requested field';
      body = (
        <>
          <div className={styles.contextFields}>
            {contextFields.map((r, i) => (
              <div key={r[0]} data-context-field={r[0]} data-selected={sel.field === i}>
                <b>{r[1]}</b>
                <small>{out.fields[r[0]].status}</small>
              </div>
            ))}
          </div>
          <article className={styles.contextClaim} data-context-selected={f[0]}>
            <b>
              {f[1]} · {record.status}
            </b>
            <h5>{f[2]}</h5>
            <p>{f[3]}</p>
            <p>
              Submitted confidence: <b>{record.confidence.toFixed(2)}</b> — confidence in this
              assessment, including an unknown.
            </p>
          </article>
          <p>
            Exact output: status · value (null when unknown) · confidence · basis · alternatives. A
            companion report supplies method and native image citations.
          </p>
        </>
      );
      break;
    case 'reference':
      title = sel.reference
        ? 'Reveal the source level behind each comparison'
        : 'Keep source metadata outside the image-only input';
      body = sel.reference ? (
        <div data-context-private>
          <div className={styles.contextCards}>
            <article>
              <b>Patient CSV</b>
              <p>
                Age {ref.metadata.age_years.value} · recorded sex {ref.metadata.recorded_sex.value}
                <br />
                Interval {ref.metadata.interval_days.value} days
              </p>
              <small>Age reference date unspecified.</small>
            </article>
            <article>
              <b>Cohort descriptions</b>
              <p>
                Metastatic malignant melanoma
                <br />
                Systemic therapy
                <br />
                Staging / response assessment
              </p>
              <small>Not an individual clinical report.</small>
            </article>
            <article>
              <b>Unavailable</b>
              <p>Individual regimen, operative record and treatment dates.</p>
              <small>Surgical suggestion remains unadjudicated.</small>
            </article>
          </div>
          <p className={styles.contextCallout}>
            Seven unknowns and two inferences are not a 2/9 accuracy score. Agreement with metadata
            does not prove CT-only identifiability.
          </p>
          <p>
            Broad malignancy is compatible with the source. Naming melanoma among alternatives is
            not exact identification.
          </p>
        </div>
      ) : (
        <div className={styles.contextLock}>
          <b>Private reader comparison</b>
          <p>
            Patient metadata and cohort facts appear halfway through this chapter. They were not
            available to the inference session.
          </p>
          <p>Look for the source level of each fact, not a single “correct diagnosis” label.</p>
        </div>
      );
      break;
    case 'validator':
      title = 'A valid file can still contain unsupported claims';
      body = (
        <div data-context-private>
          <table className={styles.contextTable}>
            <thead>
              <tr>
                <th>Saved-output check</th>
                <th>Structure valid?</th>
                <th>Meaning</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Original agent answer</td>
                <td>Yes</td>
                <td>Exact saved-validator replay</td>
              </tr>
              <tr>
                <td>Author: all nine unknown</td>
                <td>Yes</td>
                <td>Abstention is permitted</td>
              </tr>
              <tr>
                <td>Author: invented observed claims</td>
                <td>Yes</td>
                <td>Evidence is not graded</td>
              </tr>
              <tr>
                <td>Author: unknown + non-null value</td>
                <td>No</td>
                <td>Inconsistent field rejected</td>
              </tr>
              <tr>
                <td>Author: missing report</td>
                <td>No</td>
                <td>Required file absent</td>
              </tr>
            </tbody>
          </table>
          <p className={styles.contextCallout}>
            The unchanged validator returns scientific_score = null. Original model/oracle rewards =
            1; no-op = 0.
          </p>
          <p>
            Four author diagnostics exercise the mechanical boundary. They are temporary
            saved-output checks, not fresh model attempts.
          </p>
        </div>
      );
      break;
    case 'limits':
      title = 'Preserve useful inference and justified unknowns';
      body = (
        <>
          <div className={styles.contextCards}>
            <article>
              <b>Retained result</b>
              <p>
                One Astra / medium session.
                <br />3 min 27 s; 14 image observation blocks.
              </p>
              <p>Montages count as blocks, not native slices.</p>
            </article>
            <article>
              <b>Supported explanation</b>
              <p>
                Link image evidence to qualified claims; distinguish observations, inferences and
                missing history.
              </p>
            </article>
            <article>
              <b>Unresolved</b>
              <p>
                Exact primary, patient history, surgical adjudication and statistical confidence
                calibration.
              </p>
            </article>
          </div>
          <p className={styles.contextCallout}>
            A schema pass establishes neither diagnostic correctness nor exhaustive image review.
            One patient does not establish population performance.
          </p>
          <p>
            The independent context-supplied lesion trial is a separate condition. This output was
            not supplied to it.
          </p>
        </>
      );
      break;
  }
  return (
    <section
      className={styles.contextScene}
      data-context-scene={state.scene}
      data-context-reference={sel.reference ? 'visible' : 'hidden'}
    >
      <h4>{title}</h4>
      {body}
    </section>
  );
}
export function CtContextOutput({ state }: { state: CtContextState }) {
  const s = contextSelection(state);
  return (
    <aside className={styles.contextAside}>
      <b>Context-assessment operation</b>
      <p>Images + headers → evidence → qualified claims and unknowns.</p>
      <b>Requested outputs</b>
      <p>
        context.json + report.md
        <br />
        Nine fields with confidence, basis and alternatives.
      </p>
      {s.output && (
        <div data-context-output>
          <b>Retained answer</b>
          <p>
            2 inferred · 7 unknown · 0 observed.
            <br />
            Status counts, not accuracy.
          </p>
        </div>
      )}
      {s.reference && (
        <div data-context-private>
          <b>Reference boundary</b>
          <p>Patient CSV ≠ cohort context ≠ individual history.</p>
          <p>Schema validity supplies no diagnostic score.</p>
        </div>
      )}
      {['inputs', 'liver', 'surgery'].includes(state.scene) && (
        <small>
          Native CT, HU −40 to 140. Amber cross: agent evidence point. Dashed box: agent evidence
          region. Neither is supplied assistance or GT.
        </small>
      )}
    </aside>
  );
}

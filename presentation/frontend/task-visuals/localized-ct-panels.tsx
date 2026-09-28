import { useId } from 'react';
import {
  localizedVisits as visits,
  localizedReference as reference,
  localizedOutput as output,
  localizedSelection,
  localizedPixel,
  localizedPath,
  type LocalizedCtState,
  type LocalizedVisit,
} from './localized-ct';
import styles from './task-visual.module.css';
const visitNames: LocalizedVisit[] = ['baseline', 'followup'];
const axes = ['i', 'j', 'k'];
function Plane({ visit, name, reveal }: { visit: LocalizedVisit; name: string; reveal: boolean }) {
  const info = visits[visit],
    p = info.views[name],
    pos = localizedPixel(p, info.native_ijk, info.spacing_mm),
    clip = useId();
  const scale = Math.min(250 / p.extent_mm[0], 225 / p.extent_mm[1]);
  const w = p.extent_mm[0] * scale,
    h = p.extent_mm[1] * scale,
    x = (256 - w) / 2,
    y = (231 - h) / 2;
  const marker = Math.max(2.4, p.width * 0.022),
    bar = name === 'input' ? 50 : 20;
  return (
    <article data-localized-plane={`${visit}/${name}`} data-native-index={p.index}>
      <b>
        {info.candidate} · {visit} · {axes[p.axis]} = {p.index}
      </b>
      <svg
        className={styles.localizedImage}
        viewBox="0 0 256 252"
        role="img"
        aria-label={`${visit}: ${p.selection}`}
      >
        <defs>
          <clipPath id={clip}>
            <rect x={x} y={y} width={w} height={h} />
          </clipPath>
        </defs>
        <image href={p.png} x={x} y={y} width={w} height={h} preserveAspectRatio="none" />
        <g clipPath={`url(#${clip})`}>
          <svg
            x={x}
            y={y}
            width={w}
            height={h}
            viewBox={`0 0 ${p.width} ${p.height}`}
            preserveAspectRatio="none"
          >
            {reveal && (
              <path
                data-localized-private
                d={localizedPath(reference.views[`${visit}/${name}`].paths)}
                fill="none"
                stroke="#36dcdd"
                strokeWidth="1.5"
                vectorEffect="non-scaling-stroke"
              />
            )}
            <path
              data-localized-point
              data-depth-offset={pos.offset}
              d={`M${pos.x - marker},${pos.y}H${pos.x + marker}M${pos.x},${pos.y - marker}V${pos.y + marker}`}
              fill="none"
              stroke="#ff626b"
              strokeWidth="1.5"
              vectorEffect="non-scaling-stroke"
            />
          </svg>
        </g>
        <path d={`M8,239h${bar * scale}`} stroke="white" strokeWidth="2" />
        <text x={10 + bar * scale} y="243" fill="white" fontSize="10">
          {bar} mm
        </text>
        <text x="180" y="243" fill="white" fontSize="10">
          {info.axes[p.u_axis]} → · {info.axes[p.v_axis]} {p.flip_v ? '↑' : '↓'}
        </text>
      </svg>
      <small>
        Plane − point: {pos.offset > 0 ? '+' : ''}
        {pos.offset.toFixed(2)} mm · window −150 to 250
      </small>
      <small>Native i/j/k: {p.bounds.map((v, n) => (n % 2 ? `${v})` : `[${v},`)).join(' ')}</small>
    </article>
  );
}
function Pair({ name, reveal = false }: { name: string; reveal?: boolean }) {
  return (
    <div className={styles.localizedPair}>
      {visitNames.map((v) => (
        <Plane key={v} visit={v} name={name} reveal={reveal} />
      ))}
    </div>
  );
}
function Flow({ rows }: { rows: [string, string][] }) {
  return (
    <div className={styles.localizedFlow}>
      {rows.map(([title, body]) => (
        <article key={title}>
          <b>{title}</b>
          <p>{body}</p>
        </article>
      ))}
    </div>
  );
}
export function LocalizedCtScene({ state: s }: { state: LocalizedCtState }) {
  const v = localizedSelection(s);
  return (
    <section
      className={styles.localizedScene}
      data-localized-scene={s.scene}
      data-localized-reference={v.reference ? 'visible' : 'hidden'}
    >
      {s.scene === 'inputs' && (
        <>
          <h4>Two full CT volumes, with exact locations to review</h4>
          <Pair name="input" />
          <p>
            Native center planes shown. The entire 512 × 512 × 261 / 274 CT pair was supplied; red
            crosses are input assistance.
          </p>
        </>
      )}
      {s.scene === 'rules' && (
        <>
          <h4>Decide first; segment only accepted tumor candidates</h4>
          <Flow
            rows={[
              ['Tumor', 'More likely tumor → include the full visible extent on the native grid.'],
              [
                'Normal or benign',
                'More likely normal/benign → explain the exclusion; no tumor mask.',
              ],
              ['Indeterminate', 'Record an image-based reason; no tumor mask.'],
            ]}
          />
          <p>
            Review only R01/R02. No source mask, disease label or guaranteed-positive statement was
            supplied.
          </p>
          <p>
            Uncertainty alone is not the generic exclusion rule. IDs are local to each visit; equal
            IDs do not establish identity.
          </p>
        </>
      )}
      {s.scene === 'axial' && (
        <>
          <h4>Inspect the saved four-slice close-up</h4>
          <Pair name={`axial-${v.axial}`} />
          <p>
            Step 14 displayed both saved montages. Native plane {v.axial + 1} / 4; the point stays
            at its supplied 3D location.
          </p>
        </>
      )}
      {s.scene === 'orthogonal' && (
        <>
          <h4>Check the candidate from two other directions</h4>
          <Pair name={v.orthogonal} />
          <p>
            Step 11: i/j center ±5 voxels. Physical aspect preserves 3 mm through-plane spacing;
            adjacent-plane crosses are projections.
          </p>
        </>
      )}
      {s.scene === 'serial' && (
        <>
          <h4>Follow the changing appearance through native slices</h4>
          <Pair name={`serial-${v.serial}`} />
          <p>
            Saved step-10 crops · section {v.serial + 1} / 12 · every second native slice. Reader
            replay of selected views, not simulated search.
          </p>
        </>
      )}
      {s.scene === 'judgments' && (
        <>
          <h4>The saved decision is explicit rejection</h4>
          <Pair name="axial-2" />
          {v.output && (
            <p data-localized-output>
              <b>R01 + R02: normal_or_benign.</b> The agent favors normal scalene-region soft
              tissue, citing smooth continuity and uncertain tissue attribution. This is its
              interpretation.
            </p>
          )}
        </>
      )}
      {s.scene === 'outputs' && (
        <>
          <h4>Negative judgments produce an empty tumor inventory</h4>
          {v.output && (
            <div data-localized-output>
              <Flow
                rows={[
                  ['baseline_instances.nii.gz', 'uint16 · 512 × 512 × 261 · zero positive voxels'],
                  ['followup_instances.nii.gz', 'uint16 · 512 × 512 × 274 · zero positive voxels'],
                  ['events.json', 'schema_version: 1; groups: []'],
                ]}
              />
              <p>
                Exact input affines and qform/sform retained. candidate_judgments.json gives two
                reasons; report.md cites the reviewed images.
              </p>
              <p>
                <b>Empty events do not mean disappearance.</b> Other findings were outside the task.
              </p>
            </div>
          )}
        </>
      )}
      {s.scene === 'reference' && (
        <>
          <h4>
            {v.reference
              ? 'Private reference disagrees at both indicated locations'
              : 'Keep the same candidate views; reveal the reference next'}
          </h4>
          <Pair name="axial-2" reveal={v.reference} />
          {v.reference ? (
            <p data-localized-private>
              Cyan: selected source label 3. Two visit instances, one persistent focus. Both
              supplied points lie inside it; both saved masks are empty.
            </p>
          ) : (
            <p>
              Red crosses remain solver-supplied points. Source masks and source-derived
              measurements stay hidden until reveal.
            </p>
          )}
        </>
      )}
      {s.scene === 'scoring' && v.reference && (
        <div data-localized-private>
          <h4>Separate the denominators and the validation gap</h4>
          <table className={styles.localizedTable}>
            <thead>
              <tr>
                <th>Measure</th>
                <th>Saved result</th>
                <th>Meaning</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Accepted / source-positive</td>
                <td>0 / 2</td>
                <td>One selected focus at two visits</td>
              </tr>
              <tr>
                <td>Localized / instances</td>
                <td>0 / 2</td>
                <td>No positive masks</td>
              </tr>
              <tr>
                <td>End-to-end links / events</td>
                <td>0 / 1 each</td>
                <td>Persistent identity not recovered</td>
              </tr>
              <tr>
                <td>Conditional links / events</td>
                <td>0 eligible</td>
                <td>Undefined, not a separate linking failure</td>
              </tr>
              <tr>
                <td>Specificity</td>
                <td>Undefined</td>
                <td>No negative controls</td>
              </tr>
            </tbody>
          </table>
          <p>
            <b>Offline diagnostic:</b> rejected judgments + oracle masks still validate and detect
            2/2. The verifier does not couple judgment to mask eligibility.
          </p>
          <p>
            The original answer is consistent. Its valid status and original scores remain
            unchanged.
          </p>
        </div>
      )}
      {s.scene === 'context' && (
        <>
          <h4>Source reference and solver did not have equal context</h4>
          <Flow
            rows={[
              [
                'Source annotators',
                'CT + clinical examination reports; manual axial masks and cross-visit matching.',
              ],
              [
                'Localized solver',
                'CT + exact points; no clinical reports, diagnosis, source identity or prior trace.',
              ],
              [
                'Unresolved',
                'Clinical correctness and whether this focus is decidable from CT alone.',
              ],
            ]}
          />
          <p>
            Coordinate fidelity and exact replay establish evidence identity. They do not resolve
            the clinical disagreement.
          </p>
        </>
      )}
      {s.scene === 'limits' && (
        <>
          <h4>What this selected probe establishes</h4>
          <Flow
            rows={[
              ['Observed', 'The indicated structures were displayed, then explicitly excluded.'],
              [
                'Supported',
                'A recognition/inclusion disagreement remains after location assistance.',
              ],
              ['Still untested', 'Contour construction and linking after positive acceptance.'],
            ]}
          />
          <p>
            One fresh Astra/medium attempt; one outcome-selected focus, two visits. No population
            sensitivity, specificity or isolated causal effect.
          </p>
          <p>
            Clinical/reference review stays open. No new model trial is part of this explanation.
          </p>
        </>
      )}
    </section>
  );
}
export function LocalizedCtOutput({ state: s }: { state: LocalizedCtState }) {
  const v = localizedSelection(s);
  return (
    <aside className={styles.localizedAside}>
      <b>Native input assistance</b>
      <p>
        R01 baseline: <code>[304,263,213]</code>
        <br />
        R02 follow-up: <code>[302,221,216]</code>
      </p>
      <p>
        Zero-based voxel indices. Same patient; separately calibrated grids, no registration
        implied.
      </p>
      {v.output && (
        <div data-localized-output>
          <b>Saved output</b>
          <pre>
            {output.judgments.candidates.map((r) => `${r.candidate_id}: ${r.judgment}`).join('\n')}
          </pre>
          <p>0 mask instances · {output.events.groups.length} event groups.</p>
        </div>
      )}
      {v.reference && (
        <div data-localized-private>
          <b>Private source reference</b>
          <p>
            B3: {reference.geometry[0].reference_voxels} voxels ·{' '}
            {reference.geometry[0].volume_ml.toFixed(2)} mL
            <br />
            F3: {reference.geometry[1].reference_voxels} voxels ·{' '}
            {reference.geometry[1].volume_ml.toFixed(2)} mL
          </p>
          <p>Persistent means identity, not unchanged size.</p>
        </div>
      )}
      <p>
        Red cross = supplied point.
        <br />
        Cyan solid outline = private reference.
      </p>
    </aside>
  );
}

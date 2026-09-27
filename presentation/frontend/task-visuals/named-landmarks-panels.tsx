import { useId } from 'react';
import {
  landmarkSource as src,
  landmarkOutputs as outputs,
  landmarkReference as refs,
  landmarkColors as colors,
  landmarkWorld,
  landmarkProjection,
  landmarkSelection,
  landmarkRevealed,
  landmarkReturned,
  type LandmarkCase,
  type LandmarkState,
  type LandmarkPlane,
} from './named-landmarks';
import styles from './task-visual.module.css';
const f = (v: number) => v.toFixed(2);
const triple = (v: number[]) => v.map(f).join(', ');
const names = {
  full: 'VerSe full CT',
  partial: 'VerSe partial CT',
  pddca: 'PDDCA head/neck CT',
  mri: 'AFIDs T1 MRI',
};
const axisNames = ['i', 'j', 'k'];
function Plane({
  plane: p,
  caseId,
  x,
  y,
  w,
  h,
  marks = [],
}: {
  plane: LandmarkPlane;
  caseId: LandmarkCase;
  x: number;
  y: number;
  w: number;
  h: number;
  marks?: { point: number[]; type: keyof typeof colors; label: string }[];
}) {
  const clip = useId();
  const scale = Math.min(w / p.extent_mm[0], h / p.extent_mm[1]);
  const width = p.extent_mm[0] * scale,
    height = p.extent_mm[1] * scale;
  const left = x + (w - width) / 2,
    top = y + (h - height) / 2;
  return (
    <g data-landmark-plane={p.axis} data-native-index={p.index}>
      <defs>
        <clipPath id={clip}>
          <rect x={left} y={top} width={width} height={height} />
        </clipPath>
      </defs>
      <text x={x} y={y - 9} fontSize="14">
        {axisNames[p.axis]} = {p.index} · {src.cases[caseId].positive_axes[p.u_axis]} → /{' '}
        {src.cases[caseId].positive_axes[p.v_axis]} ↑
      </text>
      <rect x={left} y={top} width={width} height={height} fill="#111" />
      <image
        data-landmark-image={caseId}
        href={p.png}
        x={left}
        y={0}
        width={width}
        height={height}
        preserveAspectRatio="none"
        transform={`translate(0 ${top + height}) scale(1 -1)`}
      />
      <g clipPath={`url(#${clip})`}>
        {marks.map((m) => {
          const q = landmarkProjection(p, caseId, m.point);
          const px = left + (q.u / p.width) * width,
            py = top + (q.v / p.height) * height;
          return (
            <g
              key={m.type + m.label}
              transform={`translate(${px} ${py})`}
              data-landmark-mark={m.type}
              stroke={colors[m.type]}
              strokeWidth="2.5"
              fill="none"
            >
              {m.type === 'sol' ? (
                <circle r="6" />
              ) : (
                <path d={m.type === 'terra' ? 'M-5 -5L5 5M-5 5L5 -5' : 'M-7 0H7M0 -7V7'} />
              )}
            </g>
          );
        })}
      </g>
      {marks.map((m, i) => (
        <text
          key={m.type + m.label}
          x={x}
          y={y + h + 18 + i * 18}
          fontSize="13"
          fill={colors[m.type]}
          data-landmark-offset={m.type}
        >
          {m.label} Δ{axisNames[p.axis]} {f(landmarkProjection(p, caseId, m.point).offset)} mm
        </text>
      ))}
    </g>
  );
}
function InputViews({ conditions = false }: { conditions?: boolean }) {
  const keys: LandmarkCase[] = conditions ? ['full', 'partial'] : ['pddca', 'mri', 'full'];
  return (
    <>
      <h4>
        {conditions
          ? 'Acquisition extent changes the question'
          : 'Named targets; their locations are not supplied'}
      </h4>
      <div className={styles.landmarkCards} data-columns={keys.length}>
        {keys.map((key) => {
          const ratio = conditions ? src.cases[key].shape[2] / 1214 : 1;
          return (
            <article key={key}>
              <b>{names[key]}</b>
              <svg
                className={styles.landmarkNative}
                viewBox="0 0 185 260"
                role="img"
                aria-label={`${names[key]} native centre section`}
              >
                <Plane
                  plane={src.views[key + '-input'][0]}
                  caseId={key}
                  x={4}
                  y={25 + 200 * (1 - ratio)}
                  w={176}
                  h={200 * ratio}
                />
                {conditions && key === 'full' && (
                  <g>
                    <path
                      d={`M30 ${25 + 200 * (1 - 920 / 1214)}h122`}
                      stroke="#628ca5"
                      strokeDasharray="5 3"
                      strokeWidth="2"
                    />
                    <rect
                      x="102"
                      y={7 + 200 * (1 - 920 / 1214)}
                      width="73"
                      height="17"
                      fill="#f4f5ed"
                    />
                    <text x="105" y={19 + 200 * (1 - 920 / 1214)} fontSize="12">
                      k &lt; 920
                    </text>
                  </g>
                )}
              </svg>
              <span>{src.cases[key].shape.join(' × ')}</span>
              <span>
                {conditions
                  ? key === 'full'
                    ? '24 visible · 2 absent'
                    : '13 visible · 11 outside · 2 absent'
                  : key === 'pddca'
                    ? 'chin · condyles · dens'
                    : key === 'mri'
                      ? '32 named AFIDs'
                      : 'C1–C7 · T1–T13 · L1–L6'}
              </span>
            </article>
          );
        })}
      </div>
      <p>
        {conditions
          ? 'Same physical scale and inferior origin · native k=0:920 crop'
          : 'Actual native centre sections · independently fitted · no reference points'}
      </p>
    </>
  );
}
function PointViews({ state }: { state: LandmarkState }) {
  const row = landmarkSelection(state),
    models = outputs[row.caseId];
  const marks: { point: number[]; type: keyof typeof colors; label: string }[] = [];
  if (row.output)
    for (const type of ['terra', 'sol'] as const) {
      const point = models[type]?.[row.key]?.ijk;
      if (point)
        marks.push({ point, type, label: (type === 'terra' ? 'Terra ' : 'Sol ') + row.key });
    }
  if (row.reveal) {
    const point = refs.points[row.caseId][row.referenceKey].ijk;
    if (point) marks.push({ point, type: 'reference', label: 'Ref ' + row.referenceKey });
  }
  const search = state.scene === 'search';
  const heading =
    state.scene === 'condyle'
      ? 'Right condyle: inspect all three dimensions'
      : state.scene === 'mri'
        ? 'AFID 20 · source-assisted saved MRI output'
        : state.scene === 'counterexample'
          ? 'AFID 1 · anterior commissure counterexample'
          : search
            ? 'Step through actual source sections'
            : row.key === 'T5'
              ? 'Visible T5: abstention can miss real anatomy'
              : 'Submitted T4: point and name are separate claims';
  return (
    <>
      <h4>{heading}</h4>
      <p>
        Reader-selected region ·{' '}
        {row.reveal ? 'private reference revealed' : 'private reference hidden'}
      </p>
      <div className={styles.landmarkCards} data-columns={row.planes.length}>
        {row.planes.map((p, i) => (
          <svg
            key={i}
            className={styles.landmarkNative}
            viewBox="0 0 200 300"
            role="img"
            aria-label={`Native ${axisNames[p.axis]} section ${p.index}, projected points with depth offsets`}
          >
            <Plane plane={p} caseId={row.caseId} x={8} y={25} w={184} h={205} marks={marks} />
          </svg>
        ))}
      </div>
      <p>
        {row.reveal && row.key === 'T4'
          ? 'Terra T4 is 2.14 mm from source T5 · wrong level on real bone'
          : search
            ? '16 actual sections · teaching navigation, not an agent trace'
            : 'Projected markers · signed depth offsets below each plane'}
      </p>
      <p>
        {row.reveal && row.key === 'T5'
          ? 'Sol: out_of_fov for visible T5 · no Sol point to draw'
          : 'Native axes and physical aspect preserved · full 3D distance scores'}
      </p>
    </>
  );
}
function Comparison({ state }: { state: LandmarkState }) {
  const index = Math.min(2, Math.floor(state.view * 3));
  const ctThreshold = ['5', '10', '20'][index],
    mrThreshold = ['3', '5', '10'][index];
  return (
    <div data-landmark-threshold={ctThreshold}>
      <h4>The denominator includes visible misses</h4>
      <p>One attempt per condition · model, effort and MRI assistance differ</p>
      <table className={styles.landmarkCounts}>
        <thead>
          <tr>
            <th>Visible targets</th>
            <th>Terra/high</th>
            <th>Sol/xhigh</th>
          </tr>
        </thead>
        <tbody>
          {(['full', 'partial', 'mri'] as const).map((key) => {
            const threshold = key === 'mri' ? mrThreshold : ctThreshold,
              denominator = { full: 24, partial: 13, mri: 32 }[key];
            return (
              <tr key={key}>
                <td>
                  {names[key]} ≤{threshold} mm
                </td>
                {(['terra', 'sol'] as const).map((m) => (
                  <td key={m}>
                    {refs.grades[key][m]!.success_counts![threshold]}/{denominator}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
      <p>Partial CT Sol: 7.44 mm mean over 12 returned points</p>
      <p>Outside false detections: Terra 1/11 · Sol 0/11</p>
      <p>At 5 mm, full CT Sol has 1/24; a lower mean is not every endpoint.</p>
    </div>
  );
}
function Limits() {
  return (
    <>
      <h4>What this evidence can support</h4>
      <dl className={styles.landmarkLimits}>
        {[
          ['11 model attempts', 'Three subjects · correlated full/crop conditions'],
          ['Separate endpoints', 'Location · level name · visible miss · unavailable response'],
          [
            'Reference uncertainty',
            'AFIDs 22: 3.59 mm · 27: 3.14 mm maximum rater distance from consensus',
          ],
          ['Atlas assistance', 'Generic atlas used; original runtime image not retained'],
          ['Preserved outcomes', 'Saved-output replay · no new model or clinical trial'],
        ].map(([title, detail]) => (
          <div key={title}>
            <dt>{title}</dt>
            <dd>{detail}</dd>
          </div>
        ))}
      </dl>
    </>
  );
}
export function NamedLandmarksScene({ state }: { state: LandmarkState }) {
  return (
    <div className={styles.landmarkScene} data-landmark-scene={state.scene}>
      {state.scene === 'inputs' ? (
        <InputViews />
      ) : state.scene === 'conditions' ? (
        <InputViews conditions />
      ) : state.scene === 'comparison' ? (
        landmarkRevealed(state) ? (
          <Comparison state={state} />
        ) : (
          <p>Evaluation hidden until the reference reveal.</p>
        )
      ) : state.scene === 'limits' ? (
        <Limits />
      ) : (
        <PointViews state={state} />
      )}
    </div>
  );
}

export function NamedLandmarksOutput({ state }: { state: LandmarkState }) {
  const row = landmarkSelection(state),
    reveal = landmarkRevealed(state),
    returned = landmarkReturned(state);
  const coordinate = state.scene === 'coordinates';
  const pts = outputs[row.caseId];
  const terra = pts.terra?.[row.key];
  return (
    <aside
      className={styles.storyOutput}
      data-landmark-output={returned ? 'visible' : 'hidden'}
      data-landmark-reference={reveal ? 'visible' : 'hidden'}
    >
      <strong>
        {state.scene === 'inputs'
          ? 'Find → locate → report availability'
          : coordinate
            ? 'A saved point in two coordinate systems'
            : state.scene === 'conditions'
              ? 'Contracts stay condition-specific'
              : state.scene === 'comparison'
                ? 'Evaluate the whole requested set'
                : state.scene === 'limits'
                  ? 'Limits and provenance'
                  : `${names[row.caseId]} · ${row.key}`}
      </strong>
      {state.scene === 'inputs' ? (
        <>
          <p>
            Target names and definitions are supplied. The scan contains no provided point
            detections.
          </p>
          <p>
            BR-038/039/040 add native arrays, geometry and inspection tools. References remain
            private.
          </p>
          <p>BR-036 instead requests RAS millimetres.</p>
        </>
      ) : coordinate && terra?.ijk ? (
        <>
          <p>Terra/high T4, saved voxel output:</p>
          <code>[{triple(terra.ijk)}]</code>
          <p>Apply the native NIfTI affine:</p>
          <code>RAS mm [{triple(landmarkWorld('partial', terra.ijk))}]</code>
          <p>
            Native +i goes left, +j anterior, +k superior. The scan origin is not an anatomical
            landmark.
          </p>
          <p>This conversion says where the point is; it does not establish its name.</p>
        </>
      ) : state.scene === 'conditions' ? (
        <>
          <p>
            BR-036: RAS coordinates; cropped CT accepts 2/4 responses because both outside targets
            receive null.
          </p>
          <p>BR-038: voxel output and helper; all 32 MRI targets visible.</p>
          <p>
            BR-039/040: observed / out_of_fov / absent / uncertain. Source-confirmed T13 and L6 are
            absent.
          </p>
          <p>Counting anchors are removed in the partial scan.</p>
        </>
      ) : state.scene === 'comparison' ? (
        <>
          <p>Success counts include every visible target, even an omitted point.</p>
          <p>A mean over returned points cannot recover missed T5.</p>
          <p>Full CT improves at 10/20 mm but falls from 2/24 to 1/24 at 5 mm.</p>
          <p>MRI: atlas-assisted Sol; unavailable-target behavior untested.</p>
        </>
      ) : state.scene === 'limits' ? (
        <>
          <p>Preserve native coordinates and original scores.</p>
          <p>
            AFIDs uncertainty is context, not rescoring. Rater maxima are distances from the
            released consensus.
          </p>
          <p>
            One selected condition cannot establish population performance or a causal atlas
            benefit.
          </p>
          <p>Retained references are for reader review, never extra solver input.</p>
        </>
      ) : (
        <>
          {returned ? (
            <table>
              <thead>
                <tr>
                  <th>Saved output</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {(['terra', 'sol'] as const)
                  .filter((m) => pts[m])
                  .map((m) => (
                    <tr key={m}>
                      <td>{m === 'terra' ? 'Terra/high' : 'Sol/xhigh'}</td>
                      <td>{pts[m]![row.key].status}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          ) : (
            <p>No saved output shown. Actual native slices are available for inspection.</p>
          )}
          {reveal ? (
            <div data-landmark-private>
              <p>
                <b>Private source:</b> {row.referenceKey} is{' '}
                {refs.points[row.caseId][row.referenceKey].status}.
              </p>
              {row.key === 'T4' ? (
                <p>T4 is outside this crop. Terra's T4 point lies 2.14 mm from reference T5.</p>
              ) : (
                <p>
                  {(['terra', 'sol'] as const)
                    .filter((m) => refs.grades[row.caseId][m])
                    .map(
                      (m) =>
                        `${m === 'terra' ? 'Terra' : 'Sol'}: ${refs.grades[row.caseId][m]!.score.errors_mm[row.key] === undefined ? 'visible miss' : f(refs.grades[row.caseId][m]!.score.errors_mm[row.key]) + ' mm'}`,
                    )
                    .join(' · ')}
                </p>
              )}
            </div>
          ) : (
            <p>Private source point and score hidden.</p>
          )}
          {row.caseId === 'mri' && (
            <p>
              Sol used permitted generic atlas assistance plus manual review. The exact runtime
              atlas image is unavailable.
            </p>
          )}
          <p>
            Cross/circle/plus mark projected points. Signed plane offsets expose depth differences.
          </p>
        </>
      )}
    </aside>
  );
}

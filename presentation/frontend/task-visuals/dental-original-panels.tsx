import {
  dentalSource as src,
  dentalOutputs as out,
  dentalReference as refs,
  dentalColors as color,
  dentalGates,
  dentalDisplayedItems,
  dentalSelection,
  dentalPath,
  type DentalState,
  type DentalPlane,
  type DentalPaths,
  type DentalItem,
} from './dental-original';
import styles from './task-visual.module.css';

const f = (value: number) => value.toFixed(4);
const gateNames: Record<string, string> = {
  envelope: 'Tooth envelope',
  distance: 'Interior >1.6 vox',
  intensity: 'Intensity <1180',
  slice: 'Native k <66',
  final: 'Saved final pulp',
};
function Plane({
  plane: p,
  items = [],
  tone = color.output,
  reference = false,
  focus = false,
  gate,
  referencePaths,
}: {
  plane: DentalPlane;
  items?: DentalItem[];
  tone?: string;
  reference?: boolean;
  focus?: boolean;
  gate?: DentalPaths;
  referencePaths?: DentalPaths;
}) {
  const font = p.width / (focus ? 22 : 27);
  return (
    <>
      <svg
        className={styles.dentalNative}
        viewBox={`0 0 ${p.width} ${p.height}`}
        role="img"
        aria-label={`${p.case} native ${p.axis}=${p.index}`}
        data-dental-plane={`${p.case}:${p.axis}:${p.index}`}
      >
        <image href={p.png} width={p.width} height={p.height} />
        {items.map((item) => (
          <g key={item.id} data-dental-layer={reference ? 'reference' : 'output'}>
            <path
              d={dentalPath(item.paths)}
              fill="none"
              stroke={tone}
              strokeWidth="1.8"
              vectorEffect="non-scaling-stroke"
              strokeDasharray={reference ? '4 3' : undefined}
            />
            {typeof item.id === 'number' && (!focus || [11, 21].includes(item.id)) && (
              <g>
                <rect
                  x={item.center[0] - font * 0.85}
                  y={item.center[1] - font * 0.62}
                  width={font * 1.7}
                  height={font * 1.25}
                  fill="#07151d"
                  opacity="0.92"
                />
                <text
                  x={item.center[0]}
                  y={item.center[1]}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fill={tone}
                  fontSize={font}
                  fontWeight="700"
                  data-dental-id={item.id}
                >
                  {item.id}
                </text>
              </g>
            )}
          </g>
        ))}
        {gate && (
          <path
            data-dental-layer="gate"
            d={dentalPath(gate)}
            stroke={color.gate}
            fill="none"
            strokeWidth="2"
            vectorEffect="non-scaling-stroke"
          />
        )}
        {referencePaths && (
          <path
            data-dental-layer="reference"
            d={dentalPath(referencePaths)}
            stroke={color.reference}
            fill="none"
            strokeWidth="2"
            strokeDasharray="4 3"
            vectorEffect="non-scaling-stroke"
          />
        )}
      </svg>
      <small className={styles.dentalAxes}>
        {p.case} · {p.axis}={p.index} · {p.plane_axes[0]} {p.bounds_uv[0][0]}–
        {p.bounds_uv[0][1] - 1} → · {p.plane_axes[1]} {p.bounds_uv[1][0]}–{p.bounds_uv[1][1] - 1} ↑
      </small>
    </>
  );
}
function Anatomy({ state }: { state: DentalState }) {
  const v = dentalSelection(state);
  const keys =
    v.key === 'identity' ? (state.scene === 'output' ? ['medium', 'xhigh'] : ['xhigh']) : ['f002'];
  return (
    <>
      <div
        className={styles.dentalCards}
        data-columns={state.scene === 'diagnostic' && v.reveal ? 3 : 2}
      >
        {keys.map((key) => (
          <article key={key} data-dental-panel={key}>
            <b>
              {key === 'medium'
                ? 'Astra / medium'
                : key === 'xhigh'
                  ? 'Astra / xhigh'
                  : 'F002 · Astra / medium'}
            </b>
            <Plane
              plane={v.plane}
              items={v.output ? out.views[v.key][key] : []}
              tone={key === 'medium' ? color.medium : color.output}
              focus={state.scene === 'diagnostic'}
            />
          </article>
        ))}
        {state.scene === 'diagnostic' && (
          <article data-dental-panel="diagnostic">
            <b>{v.diagnostic ? 'Fixed side-ID swap · diagnostic' : 'Same output · original IDs'}</b>
            <Plane
              plane={v.plane}
              items={v.output ? dentalDisplayedItems(out.views.identity.xhigh, v.diagnostic) : []}
              focus
            />
          </article>
        )}
        {v.reveal && (
          <article data-dental-private data-dental-panel="reference">
            <b>Private research reference</b>
            <Plane
              plane={v.plane}
              items={refs.views[v.key]}
              tone={color.reference}
              reference
              focus={state.scene === 'diagnostic'}
            />
          </article>
        )}
      </div>
      <p>
        {state.scene === 'diagnostic'
          ? 'Only displayed IDs change; the two output contours have identical coordinates. Labels 11 and 21 highlighted.'
          : 'Saved IDs remain unchanged. Reader-selected section and crop; scores cover whole volumes.'}
      </p>
    </>
  );
}
export function DentalOriginalScene({ state }: { state: DentalState }) {
  const v = dentalSelection(state);
  return (
    <div
      className={styles.dentalScene}
      data-dental-scene={state.scene}
      data-dental-reference={v.reveal ? 'visible' : 'hidden'}
      data-dental-gate={v.gate}
    >
      {['inputs', 'contract', 'method'].includes(state.scene) ? (
        <>
          <h4>
            {state.scene === 'inputs'
              ? 'A full CBCT and a finite dictionary'
              : state.scene === 'contract'
                ? 'One exclusive integer label map'
                : 'Image-guided programming · retained method'}
          </h4>
          <div className={styles.dentalInput}>
            <article>
              <Plane plane={v.plane} />
            </article>
            {state.scene === 'method' ? (
              <ol className={styles.dentalFlow}>
                <li>Inspect native CT; choose regions and landmarks</li>
                <li>Thresholds + morphology; tooth envelopes</li>
                <li>Xhigh: 3D watershed; internal pulp filtering</li>
                <li>Canal paths or explicit omission</li>
                <li>Compose labels; inspect; save NIfTI</li>
              </ol>
            ) : (
              <div className={styles.dentalFacts}>
                <p>
                  <strong>77</strong> foreground classes + background 0
                </p>
                <p>Sparse IDs through 148</p>
                <p>32 tooth IDs + 32 pulp IDs</p>
                <p>13 jaw, air-space, canal and restoration classes</p>
                <p>
                  {state.scene === 'contract'
                    ? 'segmentation.nii.gz + method.md'
                    : 'No example masks, target counts or feedback'}
                </p>
              </div>
            )}
          </div>
          <p>F018 · 410 × 410 × 264 · 0.3 mm native voxels · full volume supplied</p>
          <p>
            {state.scene === 'contract'
              ? 'Preserve shape and affine. Header direction is not adjudicated patient laterality.'
              : state.scene === 'method'
                ? 'Reconstruction from saved scripts and observable actions; no new model execution.'
                : 'Unannotated reader section. The complete taxonomy does not specify this case’s inventory.'}
          </p>
        </>
      ) : ['output', 'reference', 'diagnostic', 'restorations'].includes(state.scene) ? (
        <>
          <h4>
            {state.scene === 'output'
              ? 'Saved masks and original tooth IDs'
              : state.scene === 'reference'
                ? 'Same positions, opposing semantic IDs'
                : state.scene === 'diagnostic'
                  ? 'Change names, keep every position fixed'
                  : 'F002 · restoration and tooth disagreement'}
          </h4>
          <Anatomy state={state} />
        </>
      ) : state.scene === 'metrics' ? (
        <>
          <h4>Whole-volume overlap · three completed attempts</h4>
          {v.reveal && (
            <table className={styles.dentalTable} data-dental-private>
              <thead>
                <tr>
                  <th>Attempt</th>
                  <th>
                    Original macro
                    <br />
                    <small>active classes</small>
                  </th>
                  <th>
                    Side diagnostic
                    <br />
                    <small>active classes</small>
                  </th>
                  <th>Foreground</th>
                </tr>
              </thead>
              <tbody>
                {refs.diagnostics.map((r) => (
                  <tr key={r.name}>
                    <td>{r.name}</td>
                    <td>
                      {f(r.original_macro)}
                      <small>n={r.active_labels_original}</small>
                    </td>
                    <td>
                      {f(r.fixed_lr_diagnostic_macro)}
                      <small>n={r.active_labels_lr_diagnostic}</small>
                    </td>
                    <td>{f(r.foreground_dice)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <p>
            Both-empty classes excluded; one-empty classes score zero. Active classes carry equal
            weight.
          </p>
          <p>
            Foreground pools all nonzero IDs. The diagnostic changes the denominator and never
            replaces the original score.
          </p>
        </>
      ) : state.scene === 'canals' ? (
        <>
          <h4>Pool both main-canal IDs; spatial disagreement remains</h4>
          <div className={styles.dentalCards}>
            {['medium', 'xhigh'].map((key) => (
              <article key={key}>
                <b>F018 · {key}</b>
                <Plane
                  plane={v.plane}
                  items={v.output ? out.views[v.key][key] : []}
                  tone={key === 'medium' ? color.medium : color.output}
                  referencePaths={v.reveal ? refs.views[v.key].flatMap((r) => r.paths) : undefined}
                />
              </article>
            ))}
          </div>
          <p>Native j={v.plane.index} · discrete acquired plane, not an interpolated contour</p>
          <p>
            IDs 3 and 4 pooled. These selected views illustrate residual geometry, without resolving
            clinical side or boundary conventions.
          </p>
        </>
      ) : state.scene === 'pulp' ? (
        <>
          <h4>Pulp loss after the tooth envelope · {gateNames[v.gate]}</h4>
          <div className={styles.dentalPulp}>
            <article>
              <Plane
                plane={v.plane}
                gate={out.views['pulp-gates'][v.gate]}
                referencePaths={v.reveal ? refs.views['pulp-gates'] : undefined}
              />
            </article>
            <div>
              <ol className={styles.dentalGateList}>
                {dentalGates.map((g) => (
                  <li key={g} data-active={g === v.gate}>
                    <span>{gateNames[g]}</span>
                    {v.reveal && (
                      <strong data-dental-private>
                        {out.gate_description.overlap_counts[g]} / 858
                      </strong>
                    )}
                  </li>
                ))}
              </ol>
              <p>Saved tooth 26 paired with reference tooth 16 for this diagnostic.</p>
              <p>
                Native i=289. Reader selects the tooth with the largest reference loss at the
                intensity gate.
              </p>
            </div>
          </div>
          <p>
            Reference overlap across the full tooth ROI, not this section alone. Final cleanup is
            not a strictly nested gate.
          </p>
        </>
      ) : state.scene === 'omissions' ? (
        <>
          <h4>F002 · all five canal labels omitted</h4>
          <div className={styles.dentalInput}>
            <article>
              <Plane
                plane={v.plane}
                referencePaths={v.reveal ? refs.views[v.key].flatMap((r) => r.paths) : undefined}
              />
            </article>
            {v.reveal && (
              <table className={styles.dentalTable} data-dental-private>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Reference voxels</th>
                    <th>Saved voxels</th>
                  </tr>
                </thead>
                <tbody>
                  {refs.diagnostics[2].per_label
                    .filter((r) => [3, 4, 103, 104, 105].includes(r.id))
                    .map((r) => (
                      <tr key={r.id}>
                        <td>{r.id}</td>
                        <td>{r.gt_voxels.toLocaleString('en')}</td>
                        <td>{r.pred_voxels}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            )}
          </div>
          <p>
            Whole-volume counts establish omission. This native section crosses the two main canals;
            it cannot show all five structures.
          </p>
        </>
      ) : (
        <>
          <h4>Retained observations, bounded interpretation</h4>
          <dl className={styles.ctLimits}>
            <div>
              <dt>2 cases · 3 completed model attempts</dt>
              <dd>Single attempts do not establish population ability or an effort benefit.</dd>
            </div>
            <div>
              <dt>1 authentication-only invocation · 4 oracle/no-op controls</dt>
              <dd>Infrastructure and controls are distinct from model segmentation.</dd>
            </div>
            <div>
              <dt>Orientation and annotation conventions remain under review</dt>
              <dd>Original outputs, source arrays and scores are unchanged.</dd>
            </div>
            <div>
              <dt>8 native teaching views · post-submission selection</dt>
              <dd>
                Not an exhaustive clinical contour review. V2/v3 and example-assisted tasks are
                separate.
              </dd>
            </div>
          </dl>
        </>
      )}
    </div>
  );
}
const outputCopy: Record<DentalState['scene'], string[]> = {
  inputs: [
    'CT + full label dictionary.',
    'No masks, example case, source identity, target inventory or scores.',
    'Two-hour CPU-only ceiling; no pretrained segmentation weights.',
  ],
  contract: [
    'One integer ID per voxel; allowed sparse IDs, input shape and affine preserved.',
    'Original instructions omit the source-specific direction convention.',
    'The publisher warns that NIfTI directions are not physically accurate.',
  ],
  method: [
    'All three attempts choose classical image processing.',
    'Xhigh adds 3D watershed; other choices and single-run variability also differ.',
    'Observable code explains operations, not hidden reasoning.',
  ],
  output: [
    'F018 medium and xhigh share exact task bytes.',
    'These are original saved IDs and contours.',
    'Private reference and scores remain hidden.',
  ],
  reference: [
    'The reference and agents assign opposing tooth-side IDs at essentially the same locations.',
    'No array mirroring is performed.',
    'Clinical laterality remains unadjudicated.',
  ],
  diagnostic: [
    'Fixed side-ID permutation, applied after completion.',
    '11↔21 and corresponding tooth/pulp, sinus and canal pairs.',
    'Only displayed names change. This is not a corrected submission.',
  ],
  metrics: [
    'Original custom macro: every active semantic ID has equal weight.',
    'Diagnostic relabeling also changes which classes are active.',
    'Foreground ignores identity and is dominated by large structures.',
  ],
  canals: [
    'Private reference: green dashed. Saved medium: orange; xhigh: cyan.',
    'Pooling both canal sides removes ID disagreement from this view.',
    'Location and extent differences remain.',
  ],
  restorations: [
    '8 = bridge; 9 = crown; 10 = implant.',
    'F002 predicts bridge voxels where reference has no bridge label.',
    'Bare names do not settle mixed-restoration conventions; no clinical subtype adjudication.',
  ],
  pulp: [
    'Purple: reconstructed saved gate; green dashed: private reference pulp.',
    'Distance >1.6 vox → smoothed intensity <1180 → native k<66.',
    'Reference retention is not precision. Raising a threshold is not a validated repair.',
  ],
  omissions: [
    'All five submitted canal labels are empty throughout F002.',
    'The agent explicitly abstained; reference contains all five IDs.',
    'A label permutation cannot recover absent geometry.',
  ],
  limits: [
    'No new medical/model execution.',
    'Public-data training overlap remains unknown.',
    'Later protocols and annotated examples require their own explanations.',
  ],
};
export function DentalOriginalOutput({ state }: { state: DentalState }) {
  const v = dentalSelection(state);
  return (
    <div className={styles.dentalOutput} data-dental-output={state.scene}>
      <strong>
        {['inputs', 'contract', 'method'].includes(state.scene)
          ? 'Solver packet and operation'
          : 'How to read this evidence'}
      </strong>
      {outputCopy[state.scene].map((s) => (
        <p key={s}>{s}</p>
      ))}
      {state.scene === 'pulp' && v.reveal && (
        <p data-dental-private>
          All paired pulp: <b>10,433 → 4,074</b> reference voxels survive the intensity gate, from
          12,242 total.
        </p>
      )}
    </div>
  );
}

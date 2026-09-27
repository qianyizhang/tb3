import {
  dentalV2Source as src,
  dentalV2Outputs as outputs,
  dentalV2Reference as refs,
  dentalV2Colors as colors,
  dentalV2Selection,
  dentalV2Path,
  dentalV2Stages,
  type DentalV2State,
  type V2Item,
} from './dental-v2';
import styles from './task-visual.module.css';

type Layer = keyof typeof colors;
const f = (n: number) => n.toFixed(3);
const pct = (n: number) => (100 * n).toFixed(1) + '%';
const conditionNames = ['No example', '+ F008 example'];
const stageNames = {
  before: 'Saved pulp before exclusion',
  prior: 'Shifted prior + 1.05 mm allowance',
  removed: 'Pulp deleted by the rule',
  after: 'Saved pulp after exclusion',
};
function Plane({
  name,
  panel,
  layers = [],
  reference = false,
  focus = false,
  warp,
}: {
  name: string;
  panel: string;
  layers?: Layer[];
  reference?: boolean;
  focus?: boolean;
  warp?: number;
}) {
  const p = src.views[name];
  const all: [Layer, V2Item[]][] = layers.map((key) => [
    key,
    key === 'example' ? src.example_annotations[name] : outputs.views[name][key],
  ]);
  if (reference) all.push(['reference', refs.views[name]]);
  const font = focus ? 9 : p.width / 24;
  return (
    <>
      <svg
        className={styles.dentalNative}
        viewBox={focus ? '0 0 78 86' : `0 0 ${p.width} ${p.height}`}
        role="img"
        aria-label={`${p.case} native ${p.axis}=${p.index}`}
        data-dental-v2-plane={name}
      >
        <image href={p.png} width={p.width} height={p.height} />
        {warp !== undefined && (
          <>
            <defs>
              <clipPath id={`v2-warp-${panel}`}>
                <rect width={p.width * warp} height={p.height} />
              </clipPath>
            </defs>
            <image
              data-v2-warp={warp.toFixed(4)}
              href={outputs.registration.warped_example_png}
              width={p.width}
              height={p.height}
              clipPath={`url(#v2-warp-${panel})`}
            />
            <line
              x1={p.width * warp}
              x2={p.width * warp}
              y1={0}
              y2={p.height}
              stroke="white"
              strokeWidth="1.5"
              vectorEffect="non-scaling-stroke"
            />
          </>
        )}
        {all.map(([key, items]) => (
          <g key={key} data-dental-v2-layer={key}>
            <path
              d={dentalV2Path(items)}
              fill="none"
              stroke="#071219"
              strokeWidth="4"
              strokeOpacity=".85"
              vectorEffect="non-scaling-stroke"
            />
            <path
              d={dentalV2Path(items)}
              fill="none"
              stroke={colors[key]}
              strokeWidth="1.8"
              strokeDasharray={key === 'reference' ? '4 3' : key === 'allowed' ? '1 3' : undefined}
              vectorEffect="non-scaling-stroke"
            />
            {name === 'identity' &&
              items
                .filter(
                  (i) => i.center && i.pixels && (!focus || [26, 27, 28].includes(Number(i.id))),
                )
                .map((item) => (
                  <g key={item.id}>
                    <rect
                      x={item.center![0] - font * 0.85}
                      y={item.center![1] - font * 0.63}
                      width={font * 1.7}
                      height={font * 1.25}
                      fill="#071219"
                    />
                    <text
                      x={item.center![0]}
                      y={item.center![1]}
                      textAnchor="middle"
                      dominantBaseline="central"
                      fill={colors[key]}
                      fontSize={font}
                      fontWeight="700"
                      data-dental-v2-id={item.id}
                    >
                      {item.id}
                    </text>
                  </g>
                ))}
          </g>
        ))}
      </svg>
      <small className={styles.dentalAxes}>
        {p.case} · {p.axis}={p.index} · {p.plane_axes.join('/')} native axes
        {focus ? ' · posterior crop' : ''}
      </small>
    </>
  );
}
function Card({ title, ...props }: Parameters<typeof Plane>[0] & { title: string }) {
  return (
    <article data-dental-v2-panel={props.panel}>
      <b>{title}</b>
      <Plane {...props} />
    </article>
  );
}
function Paired({ name, reveal, output }: { name: string; reveal: boolean; output: boolean }) {
  return (
    <div className={styles.dentalCards}>
      {(['baseline', 'assisted'] as const).map((key, i) => (
        <Card
          key={key}
          name={name}
          panel={key}
          title={conditionNames[i]}
          layers={output ? [key] : []}
          reference={reveal}
        />
      ))}
    </div>
  );
}
function Metrics() {
  const rows: [string, string, string][] = [
    [
      'Original macro · active IDs',
      ...refs.conditions.map((c) => `${f(c.original_macro_dice)} · n=${c.active_labels}`),
    ] as [string, string, string],
    [
      'Common 61-ID diagnostic',
      ...refs.conditions.map((c) => f(c.posthoc_common_label_macro_dice)),
    ] as [string, string, string],
    [
      'Whole-tooth geometry',
      ...refs.metrics.map((m) =>
        f(m.score.whole_tooth_geometry_and_identity.geometry_mean_dice_with_unmatched_zero),
      ),
    ] as [string, string, string],
    ['Pulp · pooled Dice', ...refs.conditions.map((c) => f(c.pulp_pooled.dice))] as [
      string,
      string,
      string,
    ],
    [
      'Main canals · macro Dice',
      ...refs.metrics.map((m) => f(m.score.groups.inferior_alveolar_canals.macro_dice)),
    ] as [string, string, string],
    [
      'Small canals · macro Dice',
      ...refs.metrics.map((m) => f(m.score.groups.small_canals.macro_dice)),
    ] as [string, string, string],
  ];
  return (
    <table className={`${styles.dentalTable} ${styles.dentalV2Table}`} data-dental-v2-private>
      <thead>
        <tr>
          <th>Whole-volume measure</th>
          <th>No example</th>
          <th>+ F008</th>
        </tr>
      </thead>
      <tbody>
        {rows.map(([label, a, b]) => (
          <tr key={label}>
            <td>{label}</td>
            <td>{a}</td>
            <td>{b}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
export function DentalV2Scene({ state: s }: { state: DentalV2State }) {
  const v = dentalV2Selection(s);
  const fine = refs.fine_diagnostics['diagnostics.json'];
  return (
    <div
      className={`${styles.dentalScene} ${styles.dentalV2Scene}`}
      data-dental-v2-scene={s.scene}
      data-dental-v2-reference={v.reveal ? 'visible' : 'hidden'}
      data-dental-v2-stage={v.stage}
    >
      {['inputs', 'contract'].includes(s.scene) ? (
        <>
          <h4>
            {s.scene === 'inputs'
              ? 'Same target and common contract'
              : 'Explicit native naming; unchanged grid'}
          </h4>
          <div className={styles.dentalInput}>
            <article>
              <Plane name="target-input" panel="input" />
            </article>
            <div className={styles.dentalFacts}>
              <p>
                <strong>410 × 410 × 274</strong>
                <br />
                0.3 mm native voxels · F002
              </p>
              <p>77 foreground IDs + background 0</p>
              {s.scene === 'contract' ? (
                <>
                  <p>
                    <b>i → Right · j → Posterior · k → Inferior</b>
                  </p>
                  <p>
                    One integer ID per voxel.
                    <br />
                    Tooth tissue + paired pulp = whole tooth.
                  </p>
                  <p>Keep shape, affine, qform and sform.</p>
                </>
              ) : (
                <>
                  <p>Full dictionary ≠ target inventory</p>
                  <p>Two independent Astra/medium attempts</p>
                  <p>Two-hour CPU ceiling; no pretrained weights</p>
                </>
              )}
            </div>
          </div>
          <p>
            {s.scene === 'contract'
              ? 'RPI governs semantic names. The retained legacy header does not adjudicate acquisition laterality.'
              : 'Unannotated reader section. Target reference, prior outputs and feedback are withheld.'}
          </p>
        </>
      ) : s.scene === 'example' ? (
        <>
          <h4>One condition receives an independent annotated case</h4>
          <div className={styles.dentalCards}>
            <Card title="F002 target · both conditions" name="target-input" panel="target" />
            <Card
              title="F008 example · assisted condition only"
              name="example-input"
              panel="example"
              layers={v.helper ? ['example'] : []}
            />
          </div>
          <p>
            F008: 32 tooth/pulp pairs and five canals; no restoration labels. Sampled views do not
            certify clinical normality.
          </p>
          <p>
            Same section index is context, not anatomical correspondence. Full volumes are supplied.
          </p>
        </>
      ) : s.scene === 'transfer' ? (
        <>
          <h4>Sample F008 through the saved target-to-example map</h4>
          <div className={styles.dentalInput}>
            <article>
              <Plane
                name="identity"
                panel="transfer"
                layers={v.output ? ['atlas'] : []}
                warp={v.transfer}
              />
            </article>
            <ol className={styles.dentalFlow}>
              <li>Inspect target and annotated example</li>
              <li>Estimate affine and smooth displacement</li>
              <li>Transfer labels with nearest-neighbour sampling</li>
              <li>Adapt tooth, jaw, pulp and canal priors</li>
              <li>Compose a target-grid answer</li>
            </ol>
          </div>
          <p>
            Wipe: actual target CT ↔ F008 CT sampled with the saved field. Purple: saved transferred
            labels.
          </p>
          <p>
            Reader comparison of a retained result, not optimizer playback or a new registration.
          </p>
        </>
      ) : s.scene === 'outputs' ? (
        <>
          <h4>Two original answers · same native section</h4>
          <Paired name="identity" output={v.output} reveal={false} />
          <p>
            Whole-tooth contours union tissue and paired pulp. IDs are unchanged; no relabeling.
          </p>
          <p>
            Target reference and scores remain hidden. The source dictionary does not imply every
            tooth is present.
          </p>
        </>
      ) : s.scene === 'identity' ? (
        <>
          <h4>Posterior identity improves in this pair</h4>
          <div className={styles.dentalCards} data-columns="3">
            <Card
              name="identity"
              panel="baseline"
              title="No example"
              layers={v.output ? ['baseline'] : []}
              focus
            />
            <Card
              name="identity"
              panel="assisted"
              title="+ F008"
              layers={v.output ? ['assisted'] : []}
              focus
            />
            {v.reveal && (
              <Card
                name="identity"
                panel="reference"
                title="Private target reference"
                reference
                focus
              />
            )}
          </div>
          {v.reveal && (
            <div data-dental-v2-private>
              <p>
                <b>Reference 26/27 → output 27/28 without example, 26/27 with F008.</b>
              </p>
              <p>
                Whole volume: correct identity{' '}
                {refs.conditions
                  .map(
                    (c) =>
                      `${c.identity_counts.correct_among_detected}/${c.identity_counts.detected} detected (${c.identity_counts.correct_among_detected}/${c.identity_counts.gt} GT)`,
                  )
                  .join(' → ')}
                .
              </p>
              <p>
                Reference tooth 37 still matches output 38; the baseline match is below Dice 0.5.
              </p>
            </div>
          )}
        </>
      ) : s.scene === 'metrics' ? (
        <>
          <h4>Keep geometry, identity and fine structures separate</h4>
          {v.reveal && <Metrics />}
          <p>
            Original macro excludes both-empty IDs. The common-union diagnostic assigns them zero
            across the same 61 IDs.
          </p>
          <p>
            Original scores are unchanged. Whole-tooth assignment counts unmatched objects as zero;
            Dice ≥0.5 defines detection.
          </p>
        </>
      ) : s.scene === 'pulp-rule' ? (
        <>
          <h4>A fixed intensity rule does not transfer reliably</h4>
          <p>Smoothed CT &lt;1250 and individual-tooth interior &gt;2 voxels (0.6 mm)</p>
          {v.reveal && (
            <div className={styles.dentalV2Bars} data-dental-v2-private>
              {[
                [
                  'F008 · true teeth · matching 22 IDs',
                  fine.pulp.example_true_teeth_target22_ids.score.dice,
                ],
                ['F002 · true teeth · author-only oracle', fine.pulp.target_true_teeth.score.dice],
                ['F002 · predicted teeth', fine.pulp.target_predicted_teeth.score.dice],
              ].map(([label, n]) => (
                <div key={label}>
                  <span>{label}</span>
                  <div>
                    <i style={{ width: pct(Number(n)) }} />
                    <b>{f(Number(n))}</b>
                  </div>
                </div>
              ))}
              <small>Pooled pulp Dice · common 0–1 scale</small>
            </div>
          )}
          <p>
            True target masks were unavailable to the solver. Example calibration is not held-out
            validation.
          </p>
          <p>This initial rule precedes component filters, prior corrections and final assembly.</p>
        </>
      ) : s.scene === 'pulp-contents' ? (
        <>
          <h4>Different appearance; occupied-pulp convention unresolved</h4>
          <div className={styles.dentalCards}>
            <Card
              name={`detail-F008-${v.pulpId}`}
              panel="example-pulp"
              title={`F008 · supplied pulp ${v.pulpId}`}
              layers={v.helper ? ['example'] : []}
            />
            <Card
              name={`detail-F002-${v.pulpId}`}
              panel="target-pulp"
              title={`F002 · pulp ${v.pulpId}`}
              layers={v.output ? ['assisted'] : []}
              reference={v.reveal}
            />
          </div>
          {v.reveal && (
            <p data-dental-v2-private>
              {refs.fine_diagnostics['supplement.json'].saturated_pulp
                .filter((r) => r.label === v.pulpId)
                .map(
                  (r) =>
                    `${r.raw_CT_above3000}/${r.gt_voxels} reference voxels exceed raw intensity 3000.`,
                )}{' '}
              Most are at the scan maximum.
            </p>
          )}
          <p>
            Same intensity window; independently zoomed native sections. Bright contents are not a
            material diagnosis or a verdict that GT is wrong.
          </p>
        </>
      ) : s.scene === 'pulp-clip' ? (
        <>
          <h4>Tooth 14 · {stageNames[v.stage]}</h4>
          <div className={styles.dentalPulp}>
            <article>
              <Plane
                name="prior-clipping"
                panel="clip"
                layers={
                  v.output ? (v.stage === 'prior' ? ['before', 'prior', 'allowed'] : [v.stage]) : []
                }
                reference={v.reveal}
              />
            </article>
            <div>
              <ol className={styles.dentalGateList}>
                {dentalV2Stages.map((stage) => (
                  <li key={stage} data-active={stage === v.stage}>
                    {stageNames[stage]}
                  </li>
                ))}
              </ol>
              {v.stage === 'prior' && (
                <p>Purple dotted: allowed distance from the shifted prior.</p>
              )}
              {v.reveal && (
                <div data-dental-v2-private>
                  <p>
                    <b>
                      {refs.clipping.before_true_overlap} correct voxels →{' '}
                      {refs.clipping.after_true_overlap} remain
                    </b>
                  </p>
                  <p>
                    {refs.clipping.removed_true_pulp_voxels}/{refs.clipping.before_true_overlap}{' '}
                    correctly placed voxels removed;{' '}
                    {refs.clipping.removed_pulp_voxels.toLocaleString('en')} total voxels removed.
                  </p>
                </div>
              )}
            </div>
          </div>
          <p>
            Exact saved exclusion, not a proposed repair. Reference overlap is not precision; false
            positives are also removed.
          </p>
        </>
      ) : s.scene === 'canals' ? (
        <>
          <h4>Canal paths improve, but remain misplaced or incomplete</h4>
          <Paired name={v.canalView} output={v.output} reveal={v.reveal} />
          {v.reveal && (
            <p data-dental-v2-private>
              Main-canal reference recall:{' '}
              {refs.conditions.map((c) => pct(c.main_canals_pooled.recall)).join(' → ')}. Assisted
              path samples inside GT:{' '}
              {fine.canals
                .filter((c) => [3, 4].includes(c.label))
                .map((c) => pct(c.path_samples_inside_gt_fraction))
                .join(' / ')}
              .
            </p>
          )}
          <p>
            Two discrete native sections; measurements use the full volume. Missing contours are
            section-specific.
          </p>
        </>
      ) : s.scene === 'small-canals' ? (
        <>
          <h4>Small canal {v.canalId} · placement and coverage differ</h4>
          <Paired name={`detail-F002-${v.canalId}`} output={v.output} reveal={v.reveal} />
          {v.reveal && (
            <p data-dental-v2-private>
              Assisted whole-volume Dice:{' '}
              {f(fine.canals.find((c) => c.label === v.canalId)!.final.dice)}. All small canals
              pooled recall: {pct(refs.conditions[1].small_canals_pooled.recall)}.
            </p>
          )}
          <p>
            {v.canalId === 103
              ? 'Useful placement with low coverage. A diagnostic radius expansion is not a validated repair.'
              : 'Zero overlap for this saved label; expanding a misplaced tube does not establish correct localization.'}
          </p>
        </>
      ) : (
        <>
          <h4>One informative pair; qualified conclusions</h4>
          <dl className={styles.ctLimits}>
            <div>
              <dt>Same F002 target · one attempt per condition</dt>
              <dd>22m55s versus 49m04s; different self-chosen methods and realized compute.</dd>
            </div>
            <div>
              <dt>Assistance helped some measures and harmed pulp overlap</dt>
              <dd>No population-level or isolated causal effect follows from this pair.</dd>
            </div>
            <div>
              <dt>Source conventions remain partly unresolved</dt>
              <dd>
                Clinical laterality, restoration subtypes and occupied-pulp labels require
                adjudication.
              </dd>
            </div>
            <div>
              <dt>Original arrays and scores retained</dt>
              <dd>
                Six saved evaluations replay exactly. Reader diagnostics and selected views are not
                new medical attempts.
              </dd>
            </div>
          </dl>
        </>
      )}
    </div>
  );
}
const notes: Record<DentalV2State['scene'], string[]> = {
  inputs: [
    'Same CT, label dictionary, common instruction and private evaluator.',
    'No first-condition feedback reaches the assisted solver.',
  ],
  contract: [
    'One exclusive segmentation.nii.gz + method.md.',
    'Uncertainty notes do not create ignored regions or an abstention exemption.',
  ],
  example: [
    'F008 annotation is authorized assistance in one condition.',
    'Its complete inventory does not reveal which labels occur in F002.',
  ],
  transfer: [
    'Purple labels are an intermediate prior, not target GT.',
    'The saved field reproduces the 168,100-voxel atlas plane exactly. Extra candidate teeth still require adaptation.',
  ],
  outputs: [
    'Orange: no-example answer. Cyan: assisted answer.',
    'Both passed native-grid validity. Validity does not establish anatomical accuracy.',
  ],
  identity: [
    'Assignment uses whole-tooth tissue+pulp geometry.',
    'Detection and correct naming are separate. Same object count does not imply same identity.',
  ],
  metrics: [
    'Pulp pooled Dice declines even when IDs are ignored.',
    'The active-ID denominator changes, so the diagnostic is reported separately.',
  ],
  'pulp-rule': [
    'Author-only intervention: replace predicted teeth with true target teeth.',
    'Low pulp agreement persists; tooth-envelope quality alone does not explain it.',
  ],
  'pulp-contents': [
    'The example lacks these sampled saturated pulp-labeled contents.',
    'The task does not fully settle occupied/treated/calcified chambers. This does not establish clinically wrong reference labels.',
  ],
  'pulp-clip': [
    'Saved prior exclusion at 3.5 voxels = 1.05 mm.',
    'Discrete saved/reconstructed stages; no invented intermediate masks. Counts cover the full tooth ROI.',
  ],
  canals: [
    '98.6% of missed main-canal GT lies outside the uncut tubes.',
    'Localization and width are different errors; final assembly does not explain most misses.',
  ],
  'small-canals': [
    'Selected views illustrate distinct failures; all five labels are measured.',
    'An improvement can coexist with very low reference coverage.',
  ],
  limits: [
    'Public-data pretraining exposure is unknown.',
    'These are reference-agreement measurements, not a clinical pass or official challenge score.',
  ],
};
export function DentalV2Output({ state }: { state: DentalV2State }) {
  const v = dentalV2Selection(state);
  const sensitive = [
    'identity',
    'metrics',
    'pulp-rule',
    'pulp-contents',
    'pulp-clip',
    'canals',
    'small-canals',
  ].includes(state.scene);
  return (
    <div className={styles.dentalOutput} data-dental-v2-output>
      {(!sensitive || v.reveal
        ? notes[state.scene]
        : ['Target reference and diagnostic measurements remain hidden.']
      ).map((text) => (
        <p key={text}>{text}</p>
      ))}
    </div>
  );
}

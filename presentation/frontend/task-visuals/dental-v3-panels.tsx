import {
  dentalV3Source as src,
  dentalV3Outputs as outputs,
  dentalV3Reference as refs,
  dentalV3Colors as colors,
  dentalV3Selection,
  dentalV3Path,
  type DentalV3State,
  type V3Item,
} from './dental-v3';
import styles from './task-visual.module.css';

type Layer = keyof typeof colors;
const f = (n: number | null) => (n === null ? 'not active' : n.toFixed(3));
const conditionNames = ['No example', '+ F008 example'];
const stages = {
  atlas: '1 · Transferred prior',
  before: '2 · Saved initial pulp',
  eligible: '3 · Retained or geometrically eligible',
  extra: '4 · Added region after intensity rule',
  after: '5 · Saved final pulp',
};
function Plane({
  name,
  panel,
  layers = [],
  reference = false,
  projection = false,
  warp,
}: {
  name: string;
  panel: string;
  layers?: Layer[];
  reference?: boolean;
  projection?: boolean;
  warp?: number;
}) {
  const p = projection ? src.projections[name] : src.views[name];
  const all: [Layer, V3Item[]][] = layers.map((key) => [
    key,
    key === 'example'
      ? src.example_annotations[name]
      : (projection ? outputs.projections : outputs.views)[name][key],
  ]);
  if (reference) all.push(['reference', (projection ? refs.projections : refs.views)[name]]);
  return (
    <>
      <svg
        className={styles.dentalNative}
        viewBox={`0 0 ${p.width} ${p.height}`}
        role="img"
        aria-label={
          projection
            ? `${p.case} complete projection along ${src.projections[name].collapsed_axis}`
            : `${p.case} native ${src.views[name].axis}=${src.views[name].index}`
        }
        data-dental-v3-plane={name}
        data-dental-v3-projection={projection}
      >
        {!projection && <image href={src.views[name].png} width={p.width} height={p.height} />}
        {warp !== undefined && (
          <>
            <defs>
              <clipPath id={`v3-warp-${panel}`}>
                <rect width={p.width * warp} height={p.height} />
              </clipPath>
            </defs>
            <image
              data-v3-warp={warp.toFixed(4)}
              href={outputs.registration.warped_example_png}
              width={p.width}
              height={p.height}
              clipPath={`url(#v3-warp-${panel})`}
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
          <g key={key} data-dental-v3-layer={key}>
            <path
              d={dentalV3Path(items)}
              fill="none"
              stroke="#071219"
              strokeWidth="4"
              strokeOpacity=".85"
              vectorEffect="non-scaling-stroke"
            />
            <path
              d={dentalV3Path(items)}
              fill={key === 'eligible' ? colors[key] : 'none'}
              fillOpacity=".2"
              fillRule="evenodd"
              stroke={colors[key]}
              strokeWidth="1.8"
              strokeDasharray={
                key === 'reference'
                  ? '4 3'
                  : ['eligible', 'search_box'].includes(key)
                    ? '1 3'
                    : undefined
              }
              vectorEffect="non-scaling-stroke"
            />
          </g>
        ))}
      </svg>
      <small className={styles.dentalAxes}>
        {p.case} ·{' '}
        {projection
          ? `all-depth silhouette along ${src.projections[name].collapsed_axis}`
          : `${src.views[name].axis}=${src.views[name].index}`}
        {' · '}
        {p.plane_axes.join('/')} native axes
        <br />
        {p.plane_axes.map((a, i) => `${a}=[${p.bounds_uv[i].join(',')})`).join(' · ')}
      </small>
    </>
  );
}
function Card({ title, ...props }: Parameters<typeof Plane>[0] & { title: string }) {
  return (
    <article data-dental-v3-panel={props.panel}>
      <b>{title}</b>
      <Plane {...props} />
    </article>
  );
}
function Paired({
  name,
  reveal,
  output,
  projection = false,
}: {
  name: string;
  reveal: boolean;
  output: boolean;
  projection?: boolean;
}) {
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
          projection={projection}
        />
      ))}
    </div>
  );
}
function Metrics() {
  const rows = [
    ['Original macro · 68 active IDs', ...refs.conditions.map((c) => f(c.original_macro_dice))],
    [
      'Whole-tooth geometry · 29 objects',
      ...refs.metrics.map((m) =>
        f(m.score.whole_tooth_geometry_and_identity.geometry_mean_dice_with_unmatched_zero),
      ),
    ],
    ['Pulp macro · 29 IDs', ...refs.metrics.map((m) => f(m.score.groups.pulp.macro_dice))],
    ['Pulp pooled Dice', ...refs.pooled.map((c) => f(c.pulp.dice))],
    [
      'Main-canal macro · 2 IDs',
      ...refs.metrics.map((m) => f(m.score.groups.inferior_alveolar_canals.macro_dice)),
    ],
    [
      'Small-canal macro · 3 IDs',
      ...refs.metrics.map((m) => f(m.score.groups.small_canals.macro_dice)),
    ],
  ];
  return (
    <table className={`${styles.dentalTable} ${styles.dentalV3Table}`} data-dental-v3-private>
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
function PulpCount({ stage }: { stage: ReturnType<typeof dentalV3Selection>['stage'] }) {
  const p = refs.pulp_stages.find((r) => r.label === 127)!;
  const prior = refs.diagnostic_details.find((r) => r.label === 127)!.transferred_prior;
  const measure = {
    atlas: prior,
    before: p.before,
    eligible: p.retained_or_geometry_eligible,
    extra: p.extra_after_intensity,
    after: p.after_component_filter,
  }[stage];
  return (
    <p data-dental-v3-private>
      <strong>
        {measure.intersection}/{p.gt_voxels_full_volume} GT voxels
      </strong>
      {' · '}
      {measure.prediction_voxels.toLocaleString('en-US')} voxels in this stage’s region.
      {stage === 'eligible'
        ? ' Gold fill preserves holes; this is a reach bound before intensity filtering.'
        : stage === 'extra'
          ? ' Added region only; the initial mask is retained separately.'
          : ' Selected sections; counts cover the full volume.'}
    </p>
  );
}
export function DentalV3Scene({ state: s }: { state: DentalV3State }) {
  const v = dentalV3Selection(s);
  const label = s.scene === 'pulp-gain' ? 122 : 127;
  const detail = refs.diagnostic_details.find((d) => d.label === label)!;
  const canal = refs.canal_stages.find((d) => d.label === 104)!;
  return (
    <div
      className={`${styles.dentalScene} ${styles.dentalV3Scene}`}
      data-dental-v3-scene={s.scene}
      data-dental-v3-reference={v.reveal ? 'visible' : 'hidden'}
      data-dental-v3-stage={v.stage}
    >
      {['inputs', 'contract'].includes(s.scene) ? (
        <>
          <h4>
            {s.scene === 'inputs'
              ? 'Same complete target and common contract'
              : 'Explicit compartments; preserve native metadata'}
          </h4>
          <div className={styles.dentalInput}>
            <article>
              <Plane name="target-input" panel="input" />
            </article>
            <div className={styles.dentalFacts}>
              <p>
                <strong>410 × 410 × 264</strong>
                <br />
                F018 · 0.3 mm isotropic
              </p>
              {s.scene === 'inputs' ? (
                <>
                  <p>77 possible foreground IDs + background</p>
                  <p>
                    Astra / medium · 4 CPUs · no GPU
                    <br />
                    7,200-second maximum each
                  </p>
                  <p>Target labels and evaluation feedback withheld.</p>
                </>
              ) : (
                <>
                  <p>
                    Tooth tissue + separate pulp compartment
                    <br />
                    Supported occupied pulp remains pulp.
                  </p>
                  <p>Jaw marrow, canal lumen and cavity boundaries follow explicit rules.</p>
                  <p>
                    Semantic i/j/k → Right/Posterior/Inferior.
                    <br />
                    Stored target header: LPI; preserve it.
                  </p>
                </>
              )}
            </div>
          </div>
        </>
      ) : s.scene === 'example' ? (
        <>
          <h4>F008 annotation is supplied only to the assisted condition</h4>
          <div className={styles.dentalCards}>
            <Card name="target-input" panel="target" title="Target F018 · unannotated input" />
            <Card
              name="example-input"
              panel="example"
              title="Separate F008 · permitted example"
              layers={v.helper ? ['example'] : []}
            />
          </div>
          <p>
            Same dictionary; a different anatomy and native depth. The example does not disclose the
            target’s label inventory.
          </p>
        </>
      ) : s.scene === 'transfer' ? (
        <>
          <h4>Compare target CT with F008 sampled by the saved pull map</h4>
          <div className={styles.dentalInput}>
            <article>
              <Plane
                name="shape"
                panel="warp"
                layers={v.helper ? ['atlas'] : []}
                warp={v.transfer}
              />
            </article>
            <ol className={styles.dentalFlow}>
              <li>Fit affine and regional deformation.</li>
              <li>Transfer labels into target coordinates.</li>
              <li>Correct tooth correspondence and orientation.</li>
              <li>Refine transferred boundaries against target CT.</li>
            </ol>
          </div>
          <p>
            White line: CT comparison wipe. Purple: saved transferred prior. Exact saved-field
            replay; no optimizer iterations are depicted.
          </p>
        </>
      ) : ['outputs', 'shape'].includes(s.scene) ? (
        <>
          <h4>
            {s.scene === 'outputs'
              ? 'Two unchanged saved answers on the same target'
              : 'Separate whole-tooth shape from FDI identity'}
          </h4>
          <Paired
            name={s.scene === 'outputs' ? 'outputs' : 'shape'}
            reveal={v.reveal}
            output={v.output}
          />
          {v.reveal ? (
            <p data-dental-v3-private>
              Whole-volume shape Dice{' '}
              <strong>
                {refs.metrics
                  .map((m) =>
                    f(
                      m.score.whole_tooth_geometry_and_identity
                        .geometry_mean_dice_with_unmatched_zero,
                    ),
                  )
                  .join(' → ')}
              </strong>
              . Correct detected identities:{' '}
              <strong>
                {refs.conditions
                  .map((c) => `${c.identity_counts.correct_among_detected}/${c.identity_counts.gt}`)
                  .join(' → ')}
              </strong>
              .
            </p>
          ) : (
            <p>
              Both files passed native-grid validity.{' '}
              {s.scene === 'shape'
                ? 'Tooth tissue and its pulp are unioned for shape comparison. '
                : ''}
              Target reference remains hidden.
            </p>
          )}
        </>
      ) : s.scene === 'metrics' ? (
        <>
          <h4>Same active-label denominator; different anatomical measures</h4>
          {v.reveal ? (
            <>
              <Metrics />
              <p data-dental-v3-private>
                All 68 active IDs contribute in each arm. Nine both-empty classes do not inflate the
                mean; restoration performance is untested.
              </p>
            </>
          ) : (
            <p>Private measurements remain hidden.</p>
          )}
        </>
      ) : ['pulp-gain', 'pulp-loss'].includes(s.scene) ? (
        <>
          <h4>
            {s.scene === 'pulp-gain'
              ? 'A selected success · pulp 122'
              : 'A counterexample · pulp 127'}
          </h4>
          <Paired
            name={s.scene === 'pulp-gain' ? v.gainView : v.lossView}
            reveal={v.reveal}
            output={v.output}
          />
          {v.reveal && (
            <p data-dental-v3-private>
              Full-volume Dice{' '}
              <strong>{detail.conditions.map((d) => f(d.dice)).join(' → ')}</strong>.
              {s.scene === 'pulp-gain'
                ? ' Largest pulp gain; 20/29 pulp labels improve overall.'
                : ` Transferred prior overlaps ${detail.transferred_prior.intersection}/${detail.transferred_prior.gt_voxels} GT voxels; final mask overlaps ${detail.conditions[1].intersection}.`}
            </p>
          )}
        </>
      ) : s.scene === 'pulp-reach' ? (
        <>
          <h4>Pulp 127 · {stages[v.stage]}</h4>
          <div className={styles.dentalCards}>
            {['pulp-eligibility-j156', 'pulp-eligibility-j160'].map((name) => (
              <Card
                key={name}
                name={name}
                panel={name}
                title={name.endsWith('156') ? 'Native j=156' : 'Native j=160'}
                layers={v.output ? [v.stage] : []}
                reference={v.reveal}
              />
            ))}
          </div>
          {v.reveal && <PulpCount stage={v.stage} />}
        </>
      ) : s.scene === 'canal-crop' ? (
        <>
          <h4>Canal 104 · refinement is confined to a fixed prior crop</h4>
          <div className={styles.dentalCards}>
            <Card
              name={v.canalView}
              panel="canal-ct"
              title="Native CT section · saved prior and final mask"
              layers={v.output ? ['search_box', 'atlas', 'assisted'] : []}
              reference={v.reveal}
            />
            <Card
              name="canal-104-along-k"
              panel="canal-projection"
              title="Complete silhouette · all k depths, not CT"
              layers={v.output ? ['search_box', 'atlas', 'assisted'] : []}
              reference={v.reveal}
              projection
            />
          </div>
          {v.reveal && (
            <p data-dental-v3-private>
              Search crop contains{' '}
              <strong>
                {canal.gt_voxels_in_search_crop}/{canal.gt_voxels_full_volume} GT voxels
              </strong>
              . Prior {canal.prior.prediction_voxels} → final {canal.final.prediction_voxels}{' '}
              voxels; both submitted answers have zero overlap for this label.
            </p>
          )}
        </>
      ) : s.scene === 'canal-extent' ? (
        <>
          <h4>Canal 4 · complete extent across three native projections</h4>
          <Paired name={v.projection} reveal={v.reveal} output={v.output} projection />
          {v.reveal && (
            <p data-dental-v3-private>
              Dice{' '}
              <strong>
                {refs.metrics
                  .map((m) => f(m.score.per_label.find((r) => r.id === 4)!.dice))
                  .join(' → ')}
              </strong>
              ; HD95{' '}
              <strong>
                {refs.metrics
                  .map((m) => m.score.canal_surface_metrics['4'].hd95_mm.toFixed(2))
                  .join(' → ')}{' '}
                mm
              </strong>{' '}
              (lower is better). Projected overlap can come from different depths.
            </p>
          )}
        </>
      ) : (
        <>
          <h4>One development case · one attempt per condition</h4>
          <ul className={styles.ctLimits}>
            <li>
              <strong>Matched contract:</strong> target, private reference, scorer and maximum
              budget are identical.
            </li>
            <li>
              <strong>Different execution:</strong> chosen methods and realized time differ —{' '}
              {refs.metrics
                .map(
                  (m) =>
                    `${Math.floor(Math.round(m.seconds) / 60)}m${(Math.round(m.seconds) % 60)
                      .toString()
                      .padStart(2, '0')}s`,
                )
                .join(' vs ')}
              .
            </li>
            <li>
              <strong>Untested definitions:</strong> no reference/output restoration classes;
              occupied treated pulp was not confidently identified.
            </li>
            <li>
              <strong>Open reference questions:</strong> source annotation intent and physical
              laterality remain under review.
            </li>
            <li>
              <strong>Retained evidence:</strong> exact saved evaluations and refinement replay; no
              new medical run.
            </li>
          </ul>
        </>
      )}
    </div>
  );
}
const notes: Record<DentalV3State['scene'], string[]> = {
  inputs: [
    'Complete native volume is the solver input. These sections are selected reader views.',
    'The dictionary lists possible anatomy; it does not assert target presence.',
  ],
  contract: [
    'Return one exclusive integer label volume and a method/uncertainty note.',
    'Preserve shape, affine and qform/sform. Semantic axis names do not adjudicate acquisition laterality.',
  ],
  example: [
    'F008 CT and annotation are permitted in the assisted arm.',
    'Target reference, earlier target answers and scores are withheld from both solvers.',
  ],
  transfer: [
    'The prior is an intermediate method output, separate from target GT.',
    '168,100 atlas and warped-CT voxels reproduce exactly from the saved final mapping.',
  ],
  outputs: [
    'Orange: no-example answer. Cyan: assisted answer.',
    'Native-grid validity and anatomical agreement are separate judgments.',
  ],
  shape: [
    'Matching maximizes whole-tooth tissue+pulp Dice independently of FDI names.',
    'Both arms detect and correctly name all 29 reference teeth. Shape agreement distinguishes them.',
  ],
  metrics: [
    'Macro Dice weights active IDs equally. Pooled Dice weights voxels.',
    'These custom research measures are not a clinical pass or an official challenge score.',
  ],
  'pulp-gain': [
    'Post-hoc success selection; selected sections illustrate full-volume measurements.',
    'A stronger aggregate does not mean every structure improves.',
  ],
  'pulp-loss': [
    'Reference overlap falls despite better aggregate pulp agreement.',
    'A displaced prior constrains later operations; this does not isolate a unique registration cause.',
  ],
  'pulp-reach': [
    'Expansion: inside whole tooth, depth ≥2.5 voxels, distance to prior ≤6 voxels; then intensity and component filters.',
    'Before filtering, initial mask plus eligible expansion reaches only 128/827 GT voxels. The constraints overlap; their losses are not additive.',
  ],
  'canal-crop': [
    'Actual crop: i=[274,291), j=[109,128), k=[193,209). Prior bounding box +4 voxels.',
    'The historical six-voxel proximity diagnostic is not the canal search radius. A crop outside all GT cannot recover that region.',
  ],
  'canal-extent': [
    'Complete-axis binary silhouettes are not CT sections or 3D voxel-overlap maps.',
    'Better Dice coexists with worse tail surface distance. Neither measure alone settles clinical correctness.',
  ],
  limits: [
    'Unequal realized compute and self-chosen methods limit attribution.',
    'Repeated development data, not untouched validation. License metadata conflict remains unresolved; this is a local review.',
  ],
};
export function DentalV3Output({ state }: { state: DentalV3State }) {
  const v = dentalV3Selection(state);
  const sensitive = [
    'shape',
    'metrics',
    'pulp-gain',
    'pulp-loss',
    'pulp-reach',
    'canal-crop',
    'canal-extent',
  ].includes(state.scene);
  return (
    <div className={styles.dentalOutput} data-dental-v3-output>
      {(!sensitive || v.reveal
        ? notes[state.scene]
        : ['Target reference and diagnostic measurements remain hidden.']
      ).map((text) => (
        <p key={text}>{text}</p>
      ))}
    </div>
  );
}

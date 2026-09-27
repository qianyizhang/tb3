import { CtText as T, NativeCtScan as Scan, CtRows as Rows } from './native-ct-panels';
import {
  revisedSource as source,
  revisedViews as views,
  revisedRef as ref,
  revisedIndex,
  revisedReference,
  revisedOutput,
  ctNativePoint,
  type RevisedCtState,
  type RevisedCtView,
  type CtCondition,
} from './longitudinal-ct-revised';
import styles from './task-visual.module.css';
const fmt = (n: number) => n.toFixed(3);
function Hidden() {
  return (
    <>
      <T y={176}>Reader reference hidden</T>
      <T y={212} size={17}>
        Reveal source masks and evaluation context separately.
      </T>
    </>
  );
}
function Panel({
  v,
  condition,
  x,
  r,
  o,
  point = false,
}: {
  v: RevisedCtView;
  condition: CtCondition;
  x: number;
  r: boolean;
  o: boolean;
  point?: boolean;
}) {
  const marker = v.reported_point_ijk ? ctNativePoint(v.reported_point_ijk, v) : null;
  return (
    <g>
      <Scan
        image={v.image}
        x={x}
        y={83}
        fov={v.fov_mm}
        reference={r ? v.reference.image : undefined}
        output={o ? v.outputs[condition].image : undefined}
      >
        {o && point && marker && (
          <g data-revised-point>
            <path
              d={`M${marker[0] - 7} ${marker[1]}h14M${marker[0]} ${marker[1] - 7}v14`}
              stroke="#ffb636"
              strokeWidth="1.5"
            />
          </g>
        )}
        {o &&
          !point &&
          v.outputs[condition].labels
            .filter((label) =>
              label.pixel_ij.every(
                (p) => (p / v.width_pixels) * 256 >= 12 && (p / v.width_pixels) * 256 <= 244,
              ),
            )
            .map((label) => (
              <g
                key={label.id}
                data-revised-local-id
                transform={`translate(${(label.pixel_ij[0] / v.width_pixels) * 256} ${(label.pixel_ij[1] / v.width_pixels) * 256})`}
              >
                <rect x="-9" y="-10" width="18" height="17" fill="black" opacity="0.7" />
                <text
                  textAnchor="middle"
                  y="3"
                  style={{ fill: source.colors[condition], fontSize: 12 }}
                >
                  {label.id}
                </text>
              </g>
            ))}
      </Scan>
      <T x={x} y={345} size={15}>
        native k{v.k} · {v.fov_mm.toFixed(1)} mm crop
      </T>
    </g>
  );
}
export function RevisedCtScene({ state }: { state: RevisedCtState }) {
  const r = revisedReference(state),
    o = revisedOutput(state),
    n = revisedIndex(state.view);
  const first = views[0].partition![n],
    second = views[3].new_focus![n];
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Revised CT rules, native saved masks, context and separate reference endpoints"
      data-revised-scene={state.scene}
    >
      <g>
        {state.scene === 'inputs' ? (
          <>
            <T y={28}>Three revised conditions · two full native CT pairs</T>
            {source.overview.map((v, i) => (
              <g key={i}>
                <T x={24 + Math.floor(i / 2) * 288} y={64 + (i % 2) * 142} size={15}>
                  {v.case === 'case1' ? 'Case 1' : 'Case 2'} · {v.visit} · k{v.k}
                </T>
                <Scan
                  image={v.image}
                  x={24 + Math.floor(i / 2) * 288}
                  y={72 + (i % 2) * 142}
                  size={118}
                  fov={v.shape[0] * v.spacing_mm[0]}
                />
                <T x={152 + Math.floor(i / 2) * 288} y={114 + (i % 2) * 142} size={14}>
                  {v.shape[2]} slices
                </T>
                <T x={152 + Math.floor(i / 2) * 288} y={145 + (i % 2) * 142} size={14}>
                  {v.spacing_mm[2]} mm spacing
                </T>
              </g>
            ))}
            <T y={365} size={16}>
              Image only: case 1 and case 2 · same revised prompt.
            </T>
            <T y={394} size={16}>
              Context supplied: case 2 CTs again · no target locations.
            </T>
          </>
        ) : state.scene === 'rules' ? (
          <>
            <T y={28}>Clarify generic decisions without revealing targets</T>
            <Rows
              values={[
                'More likely tumor → include, even without certainty',
                'More likely normal or benign → exclude, explain why',
                'Uncertain candidate → native location + decision + reason',
                'Distinguishable touching lesions → separate local IDs',
                'One instance only if components cannot be distinguished',
              ]}
            />
            <T y={392} size={16}>
              No lesion counts, anatomy hints, points or prior feedback.
            </T>
          </>
        ) : state.scene === 'partition' ? (
          <>
            <T y={28}>Case 1 · finer partition, incomplete reference recovery</T>
            {r ? (
              <g data-revised-reference>
                <T y={65} size={17}>
                  Original · amber · local IDs
                </T>
                <T x={312} y={65} size={17}>
                  Revised · purple · local IDs
                </T>
                <Panel v={first} condition="case1-original" x={24} r o={o} />
                <Panel v={first} condition="case1-revised" x={312} r o={o} />
                <T y={373} size={17}>
                  {o
                    ? 'Localized 2/6 → 3/6; links 1/4 → 2/4; events 0/2.'
                    : 'Cyan: private source masks; reference-selected planes.'}
                </T>
              </g>
            ) : (
              <Hidden />
            )}
            <T y={402} size={16}>
              Fine-instance review stays open; one rerun is not prompt causality.
            </T>
          </>
        ) : state.scene === 'inventory' ? (
          <>
            <T y={28}>Case 2 · one identity dominates foreground volume</T>
            {r ? (
              <g data-revised-reference>
                {[2, 3].map((i, j) => (
                  <g key={i}>
                    <T x={24 + j * 288} y={65} size={17}>
                      {j ? 'Follow-up' : 'Baseline'} · source ID 4
                    </T>
                    <Panel
                      v={views[i].dominant!}
                      condition="case2-image"
                      x={24 + j * 288}
                      r
                      o={o}
                    />
                    <T x={24 + j * 288} y={373} size={17}>
                      {(ref.measurements[i].dominant_share * 100).toFixed(1)}% of reference volume
                    </T>
                  </g>
                ))}
              </g>
            ) : (
              <Hidden />
            )}
            <T y={402} size={16}>
              Foreground Dice weights voxels; each instance needs its own check.
            </T>
          </>
        ) : state.scene === 'size' ? (
          <>
            <T y={28}>Keep every small instance in the denominator</T>
            {r ? (
              <g data-revised-reference>
                <T y={70} size={16}>
                  Case 2 · both conditions recover the same reference IDs
                </T>
                {['baseline', 'followup'].map((visit, i) => (
                  <g key={visit}>
                    <T y={109 + i * 94} size={16}>
                      {visit}
                    </T>
                    {ref.instances
                      .filter((row) => row.case === 'case2' && row.visit === visit)
                      .map((row, j) => (
                        <g key={row.id}>
                          <circle
                            cx={40 + j * 36}
                            cy={136 + i * 94}
                            r="14"
                            fill={
                              o && row.outputs['case2-image'].matched_id !== null
                                ? '#347569'
                                : '#e3e9e2'
                            }
                            stroke="#4f6464"
                          />
                          <T
                            x={row.id < 10 ? 35 + j * 36 : 30 + j * 36}
                            y={141 + i * 94}
                            size={13}
                            color={
                              o && row.outputs['case2-image'].matched_id !== null
                                ? 'white'
                                : undefined
                            }
                          >
                            {row.id}
                          </T>
                        </g>
                      ))}
                  </g>
                ))}
                {ref.strata['case2-image'].map((row, i) => (
                  <g key={row.stratum}>
                    <T x={24 + i * 191} y={299} size={17}>
                      {row.stratum}
                    </T>
                    <T x={24 + i * 191} y={336} size={24}>
                      {o ? `${row.localized}/${row.count}` : `${row.count} reference`}
                    </T>
                  </g>
                ))}
                <T y={375} size={17}>
                  {o
                    ? 'Filled = localized; outline = missed. Visit-level counts.'
                    : 'Reader reference IDs; saved detection status hidden.'}
                </T>
              </g>
            ) : (
              <Hidden />
            )}
            <T y={403} size={16}>
              The two large instances are one lesion at two visits.
            </T>
          </>
        ) : state.scene === 'context' ? (
          <>
            <T y={28}>What the context-supplied solver actually received</T>
            <Rows
              values={[
                'Patient metadata: age 44; recorded sex female; 121 days',
                'Age field reference date: unspecified',
                'Cohort: metastatic melanoma; systemic therapy',
                'Cohort purpose: staging and therapy-response assessment',
                'No individual report, regimen, surgery dates or target hints',
              ]}
            />
            <T y={394} size={16}>
              Separate context-inference answers were never passed in.
            </T>
          </>
        ) : state.scene === 'decisions' ? (
          <>
            <T y={28}>A recorded exclusion can disagree with the reference</T>
            {[2, 3].map((i, j) => (
              <g key={i}>
                <T x={24 + j * 288} y={65} size={16}>
                  {j ? 'Follow-up' : 'Baseline'} · reported excluded point
                </T>
                <Panel
                  v={views[i].excluded!}
                  condition="case2-context"
                  x={24 + j * 288}
                  r={r}
                  o={o}
                  point
                />
              </g>
            ))}
            {r ? (
              <g data-revised-reference>
                <T y={376} size={17}>
                  Both points lie inside GT2; context masks cover neither.
                </T>
              </g>
            ) : (
              <T y={376} size={17}>
                Saved report: benign cyst-like or vascular focus favored.
              </T>
            )}
            <T y={404} size={16}>
              Report-selected crops; source agreement is not clinical adjudication.
            </T>
          </>
        ) : state.scene === 'newfocus' ? (
          <>
            <T y={28}>Accept uncertainty, then inspect the actual boundary</T>
            {r ? (
              <g data-revised-reference>
                <T y={65} size={17}>
                  Case 2 image only · purple
                </T>
                <T x={312} y={65} size={17}>
                  Context supplied · amber
                </T>
                <Panel v={second} condition="case2-image" x={24} r o={o} />
                <Panel v={second} condition="case2-context" x={312} r o={o} />
                <T y={375} size={17}>
                  Accepted new focus: local ID 2 → source F13.
                </T>
              </g>
            ) : (
              <Hidden />
            )}
            <T y={403} size={16}>
              Both reports allow benign alternatives while favoring inclusion.
            </T>
          </>
        ) : state.scene === 'events' ? (
          <>
            <T y={28}>Local event IDs must map to complete reference groups</T>
            <Rows
              values={[
                'Both case 2 outputs: B local 1 → F local 1 · persistent',
                'F local 2 · newly_appearing; no baseline output ID',
                'Every positive mask ID appears in exactly one group',
                'Unresolved groups assert no links',
                'Different scan coverage does not prove disappearance',
              ]}
            />
            {r ? (
              <g data-revised-reference>
                <T y={394} size={16}>
                  Correct: 1/7 links, 2/15 events · conditional 1/1 and 2/2.
                </T>
              </g>
            ) : (
              <T y={394} size={16}>
                Private eligible/total event denominators remain hidden.
              </T>
            )}
          </>
        ) : state.scene === 'comparison' ? (
          <>
            <T y={28}>Contours differ; detected identities stay the same</T>
            {r && o ? (
              <g data-revised-reference data-revised-output>
                <T x={290} y={76} size={17}>
                  Image only
                </T>
                <T x={451} y={76} size={17}>
                  Context
                </T>
                {[
                  ['Localized instances', '3/22', '3/22'],
                  [
                    'Foreground Dice B',
                    fmt(
                      ref.results['case2-image'].metrics.visits.baseline.segmentation
                        .foreground_dice,
                    ),
                    fmt(
                      ref.results['case2-context'].metrics.visits.baseline.segmentation
                        .foreground_dice,
                    ),
                  ],
                  [
                    'Foreground Dice F',
                    fmt(
                      ref.results['case2-image'].metrics.visits.followup.segmentation
                        .foreground_dice,
                    ),
                    fmt(
                      ref.results['case2-context'].metrics.visits.followup.segmentation
                        .foreground_dice,
                    ),
                  ],
                  [
                    'GT-macro instance Dice',
                    fmt(ref.results['case2-image'].metrics.segmentation_gt_macro_dice),
                    fmt(ref.results['case2-context'].metrics.segmentation_gt_macro_dice),
                  ],
                  ['Correct links / events', '1/7 · 2/15', '1/7 · 2/15'],
                ].map(([label, a, b], i) => (
                  <g key={label}>
                    <T y={121 + i * 49} size={17}>
                      {label}
                    </T>
                    <T x={295} y={121 + i * 49} size={17}>
                      {a}
                    </T>
                    <T x={457} y={121 + i * 49} size={17}>
                      {b}
                    </T>
                  </g>
                ))}
                <T y={379} size={16}>
                  Same B4, F4 and F13; no detected identity gained or lost.
                </T>
              </g>
            ) : (
              <Hidden />
            )}
            <T y={405} size={16}>
              One run each cannot exclude a benefit from detailed clinical reports.
            </T>
          </>
        ) : state.scene === 'output' ? (
          <>
            <T y={28}>Keep uncertain decisions inspectable in the report</T>
            <Rows
              values={[
                'Two integer instance masks on exact native grids',
                'events.json: local IDs, event types and complete groups',
                'report.md: native point, included/excluded, short reason',
                'Evidence: input filename and zero-based native slice',
                'No probability sidecar is required in this revision',
              ]}
            />
            <T y={395} size={17}>
              Valid files are not a scientific pass; zero lesions remains allowed.
            </T>
          </>
        ) : (
          <>
            <T y={28}>Preserve what each condition can establish</T>
            <Rows
              values={[
                'Case 1: instance/confluence adjudication remains open',
                'Case 2: purposive selection; persistence and new events',
                'Broad context changes priors; target locations stay hidden',
                'One fresh attempt each; context and run variation differ',
                'Source agreement is not a clinical response assessment',
              ]}
            />
            <T y={395} size={17}>
              Saved-score replay verified · no new trial or corrected score.
            </T>
          </>
        )}
      </g>
    </svg>
  );
}
export function RevisedCtOutput({ state }: { state: RevisedCtState }) {
  const r = revisedReference(state);
  const copy: Record<RevisedCtState['scene'], [string, string]> = {
    inputs: [
      'Same task, explicit conditions',
      'All three attempts used Astra medium, native CTs and the same scorer. The first pair has 3 mm slice spacing; the second uses 2.0 and 2.5 mm. Case 2 is purposively selected, not a random validation patient.',
    ],
    rules: [
      'Uncertainty is not an exclusion rule',
      'Include a finding judged more likely tumor; exclude a finding judged more likely normal/benign. Record uncertain candidates with a native coordinate, decision and reason. Touching alone does not determine instance identity.',
    ],
    partition: [
      'Separate subdivision from omission',
      'The revised first-case output has two baseline IDs and a merging group. It still omits the separate B3/F3 focus and does not recover the complete source merger. Two wording changes plus a fresh run do not isolate prompt causality.',
    ],
    inventory: [
      'Useful masks can hide incomplete discovery',
      'One reference identity supplies 84.6% of baseline and 94.9% of follow-up tumor volume. Its selected native crops show useful overlap, while equal-instance metrics retain the many smaller targets.',
    ],
    size: [
      'No small reference is dropped',
      'All 22 case-2 visit instances remain: 11 at or below 1 mL, nine above 1 to 10 mL, two above 10 mL. Both conditions localize 0/11, 1/9 and 2/2 respectively. Counts do not represent independent patients.',
    ],
    context: [
      'Availability is not demonstrated use',
      'Patient demographic metadata and cohort background are distinct. No individual clinical report, regimen or surgical timeline was available. Diagnosis intentionally changes priors. The prompt verifies delivery; the trace does not establish use of each field.',
    ],
    decisions: [
      'Observed rejection; unresolved clinical interpretation',
      'The context-supplied report excludes baseline (190,199,406) and follow-up (182,165,524), favoring a benign cyst-like or vascular explanation. The amber cross is its saved coordinate; cyan is the separately revealed source boundary.',
    ],
    newfocus: [
      'Acceptance and contour quality differ',
      'Both reports include this follow-up focus despite a possible benign cyst. Source F13 is mapped from local ID 2. Dice improves from 0.579 to 0.735 with context, but no new reference identity is recovered. The original one-voxel satellite is preserved.',
    ],
    events: [
      'Conditional scores require their scope',
      'The two predicted groups match two of fifteen source groups. Conditional 2/2 examines only eligible groups; thirteen other groups lack detected endpoints. This case has no merging or disappearing reference event.',
    ],
    comparison: [
      'One diagnostic comparison',
      'The same 3/22 instances, 1/7 links and 2/15 events are recovered. Foreground and equal-instance overlap change differently. Zero instance false positives does not mean zero extra segmented tissue. No general model or context-effect claim follows.',
    ],
    output: [
      'Complete native outputs, explicit candidate reasoning',
      'Return baseline_instances.nii.gz, followup_instances.nii.gz, events.json and report.md. Background 0; local IDs 1–65535, at most 4096 per visit. Preserve useful scripts/views. The later probability-sidecar task is a separate definition.',
    ],
    limits: [
      'Evidence remains qualified',
      'All three saved score sets replay exactly. Fine-instance reference review, clinical-context limits and public-source exposure remain visible. No localized recognition or context-inference task is silently counted as this entry, and no new medical run occurs.',
    ],
  };
  const hidden =
    ['partition', 'inventory', 'size', 'newfocus', 'events', 'comparison'].includes(state.scene) &&
    !r;
  return (
    <div className={styles.storyOutput} data-revised-output-panel>
      <strong>{copy[state.scene][0]}</strong>
      <p>
        {hidden
          ? 'Reader-only source reference and evaluation details are hidden until reveal.'
          : copy[state.scene][1]}
      </p>
      <small>Actual native CT · separate solver/reference roles · CC BY-NC 4.0</small>
    </div>
  );
}

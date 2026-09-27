import type { ReactNode } from 'react';
import {
  ctSource as source,
  ctVisits as visits,
  ctReference as ref,
  ctFrameIndex,
  ctShowReference,
  ctShowOutput,
  ctEdges,
  type CtOriginalState,
  type CtView,
} from './longitudinal-ct-original';
import styles from './task-visual.module.css';
const amber = source.output_color;
const T = ({
  x = 24,
  y,
  children,
  size = 18,
  color,
}: {
  x?: number;
  y: number;
  children: ReactNode;
  size?: number;
  color?: string;
}) => (
  <text x={x} y={y} style={{ fontSize: size, ...(color ? { fill: color } : {}) }}>
    {children}
  </text>
);
function Scan({
  image,
  x,
  y,
  size = 240,
  fov,
  reference,
  output,
}: {
  image: string;
  x: number;
  y: number;
  size?: number;
  fov: number;
  reference?: string;
  output?: string;
}) {
  return (
    <svg x={x} y={y} width={size} height={size} viewBox="0 0 256 256">
      <image href={image} width="256" height="256" data-ct-input />
      {reference && <image href={reference} width="256" height="256" data-ct-reference />}
      {output && <image href={output} width="256" height="256" data-ct-output />}
      <g data-ct-scale>
        <rect x="8" y="222" width="80" height="30" fill="black" opacity="0.75" />
        <path d={`M14 245h${(20 / fov) * 256}`} stroke="white" strokeWidth="2" />
        <text x="14" y="238" style={{ fill: 'white', fontSize: 11 }}>
          20 mm
        </text>
      </g>
      <text x="6" y="126" style={{ fill: 'white', fontSize: 13 }}>
        R
      </text>
      <text x="239" y="126" style={{ fill: 'white', fontSize: 13 }}>
        L
      </text>
      <text x="124" y="15" style={{ fill: 'white', fontSize: 13 }}>
        A
      </text>
    </svg>
  );
}
function Pair({ frames, r, o }: { frames: CtView[]; r: boolean; o: boolean }) {
  return (
    <>
      {frames.map((v, i) => (
        <g key={v.visit}>
          <T x={24 + i * 288} y={65} size={17}>
            {v.visit === 'baseline' ? 'Baseline' : 'Follow-up'} · native k{v.k}
          </T>
          <Scan
            image={v.image}
            x={24 + i * 288}
            y={82}
            fov={v.fov_mm}
            reference={r ? v.reference : undefined}
            output={o ? v.astra : undefined}
          />
          <T x={24 + i * 288} y={346} size={15}>
            RAS z {v.z_ras_mm.toFixed(1)} mm
          </T>
        </g>
      ))}
    </>
  );
}
function Rows({ values }: { values: string[] }) {
  return (
    <>
      {values.map((v, i) => (
        <g key={v}>
          <rect x="24" y={59 + i * 61} width="552" height="49" rx="5" fill="#e5ebe2" />
          <T x={36} y={90 + i * 61} size={16}>
            {v}
          </T>
        </g>
      ))}
    </>
  );
}
function Hidden() {
  return (
    <>
      <T y={170}>Reader reference hidden</T>
      <T y={208} size={17}>
        Reveal the reference to see selected crops and labels.
      </T>
    </>
  );
}
export function CtOriginalScene({ state }: { state: CtOriginalState }) {
  const r = ctShowReference(state),
    o = ctShowOutput(state);
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Original CT inputs, native saved instances and separately revealed reference masks and events"
      data-ct-scene={state.scene}
    >
      <g>
        {state.scene === 'inputs' ? (
          <>
            <T y={29}>Two full native CT volumes · no supplied targets</T>
            {source.overview.map((v, i) => (
              <g key={v.visit}>
                <T x={24 + i * 288} y={65} size={17}>
                  {v.visit} · middle slice k{v.k}
                </T>
                <Scan image={v.image} x={24 + i * 288} y={82} fov={v.shape[0] * v.spacing_mm[0]} />
                <T x={24 + i * 288} y={345} size={16}>
                  {v.shape.join(' × ')} voxels
                </T>
              </g>
            ))}
            <T y={380} size={17}>
              CPU tools; no pretrained weights or dataset lookup.
            </T>
            <T y={405} size={16}>
              These previews are a small part of the full search space.
            </T>
          </>
        ) : state.scene === 'instances' ? (
          <>
            <T y={29}>Return separate native instance maps</T>
            <Pair frames={visits.map((v) => v.saved_output_view)} r={false} o={o} />
            <T y={376} size={17}>
              {o
                ? 'Saved Astra: local ID 1 at each visit · amber solid'
                : 'Saved output hidden · output-selected native crops'}
            </T>
            <T y={404} size={16}>
              Keep shape and affine; matching numbers do not prove identity.
            </T>
          </>
        ) : state.scene === 'partition' ? (
          <>
            <T y={29}>Foreground overlap does not resolve instance partition</T>
            {r ? (
              <g data-ct-reference>
                <T y={63} size={17}>
                  Reference-selected baseline · k
                  {visits[0].boundary_frames[ctFrameIndex(state.view)].k}
                </T>
                <Scan
                  image={visits[0].boundary_frames[ctFrameIndex(state.view)].image}
                  reference={visits[0].boundary_frames[ctFrameIndex(state.view)].reference}
                  output={o ? visits[0].boundary_frames[ctFrameIndex(state.view)].astra : undefined}
                  x={24}
                  y={80}
                  size={265}
                  fov={visits[0].boundary_frames[0].fov_mm}
                />
                <rect
                  x="308"
                  y="100"
                  width="13"
                  height="13"
                  fill={source.reference_colors['1']}
                  stroke="#425d60"
                  strokeWidth="0.5"
                />
                <T x={330} y={113}>
                  B1 · cyan solid
                </T>
                <rect
                  x="308"
                  y="140"
                  width="13"
                  height="13"
                  fill={source.reference_colors['2']}
                  stroke="#425d60"
                  strokeWidth="0.5"
                />
                <T x={330} y={153}>
                  B2 · pink solid
                </T>
                <rect
                  x="308"
                  y="180"
                  width="13"
                  height="13"
                  fill={source.reference_colors['4']}
                  stroke="#425d60"
                  strokeWidth="0.5"
                />
                <T x={330} y={193}>
                  B4 · blue solid
                </T>
                <T x={309} y={240} size={16}>
                  One 6-connected union
                </T>
                <T x={309} y={271} size={16}>
                  Three reference instances
                </T>
                <T x={309} y={315} size={16}>
                  {o ? 'Astra: one saved instance' : 'Astra overlay hidden'}
                </T>
              </g>
            ) : (
              <Hidden />
            )}
            <T y={376} size={17}>
              Instruction: “A confluent region is one instance.”
            </T>
            <T y={404} size={16}>
              Convention under review; contact alone is not clinical confluence.
            </T>
          </>
        ) : state.scene === 'focus' ? (
          <>
            <T y={29}>Inspect the separate reference focus at both visits</T>
            {r ? (
              <g data-ct-reference>
                <Pair frames={visits.map((v) => v.focus)} r o={o} />
              </g>
            ) : (
              <Hidden />
            )}
            <T y={376} size={17}>
              {r
                ? 'Green B3/F3 · reference-selected crops remove search.'
                : 'Reader-selected crops and identities are hidden.'}
            </T>
            <T y={404} size={16}>
              {r && o
                ? 'No saved Astra coverage here; visits are not registered.'
                : 'Native slice numbers are not registered across visits.'}
            </T>
          </>
        ) : state.scene === 'matching' ? (
          <>
            <T y={29}>Map local output IDs before scoring links</T>
            <Rows
              values={[
                'Predicted centroid → reference voxel centers in RAS mm',
                'Inside reference OR within 3 mm → eligible pair',
                'One-to-one assignment → maximize valid matches',
                'Foreground Dice → all tumor voxels, ignoring local IDs',
                'Instance Dice → best one-to-one; missed references = 0',
              ]}
            />
            {r && o ? (
              <g data-ct-reference data-ct-output>
                <T y={393} size={17}>
                  Astra local 1 → reference 4 at each visit · 2/6 localized
                </T>
              </g>
            ) : (
              <T y={393} size={17}>
                Saved/reference mapping is hidden.
              </T>
            )}
          </>
        ) : state.scene === 'links' ? (
          <>
            <T y={29}>
              {r
                ? 'Four reference edges; one eligible after detection'
                : 'Score links after mapping local instance IDs'}
            </T>
            {r ? (
              <g data-ct-reference>
                <T x={94} y={66}>
                  Baseline IDs
                </T>
                <T x={395} y={66}>
                  Follow-up IDs
                </T>
                {ctEdges(ref.groups).map(([b, f]) => (
                  <path
                    key={`${b}-${f}`}
                    d={`M175 ${95 + b * 54}L425 ${f === 3 ? 203 : 284}`}
                    stroke={source.reference_colors[String(b)]}
                    strokeWidth="3"
                    fill="none"
                  />
                ))}
                {o && (
                  <path
                    data-ct-output
                    d="M175 311L425 284"
                    stroke={amber}
                    strokeWidth="7"
                    fill="none"
                  />
                )}
                {[1, 2, 3, 4].map((id) => (
                  <g key={id}>
                    <circle
                      cx="157"
                      cy={95 + id * 54}
                      r="20"
                      fill={source.reference_colors[String(id)]}
                    />
                    <T x={144} y={101 + id * 54} color="#12252b" size={17}>
                      B{id}
                    </T>
                  </g>
                ))}
                {[3, 4].map((id) => (
                  <g key={id}>
                    <circle
                      cx="444"
                      cy={id === 3 ? 203 : 284}
                      r="20"
                      fill={source.reference_colors[String(id)]}
                    />
                    <T x={433} y={id === 3 ? 209 : 290} color="#12252b" size={17}>
                      F{id}
                    </T>
                  </g>
                ))}
                <T y={369} size={17}>
                  {o
                    ? 'Amber mapped output: B4 → F4 · one of four GT edges'
                    : 'Reference graph · node positions are schematic'}
                </T>
              </g>
            ) : (
              <Hidden />
            )}
            <T y={401} size={16}>
              {r && o
                ? 'Conditional 1/1 uses only 1/4 eligible reference edges.'
                : 'Eligibility must stay beside every conditional score.'}
            </T>
          </>
        ) : state.scene === 'events' ? (
          <>
            <T y={29}>An event requires the whole typed group</T>
            <Rows
              values={[
                'persistent: 1 → 1 · identity persists, size may change',
                'merging: two or more → 1',
                'disappearing: 1 → 0 · check follow-up field of view',
                'newly_appearing: 0 → 1',
                'unresolved: any nonempty group · no asserted link',
              ]}
            />
            {r ? (
              <g data-ct-reference>
                <T y={393} size={16}>
                  Reference: B1+B2+B4 → F4 merging; B3 → F3 persistent.
                </T>
              </g>
            ) : (
              <T y={393} size={16}>
                Every positive mask ID must appear in exactly one group.
              </T>
            )}
          </>
        ) : state.scene === 'results' ? (
          <>
            <T y={29}>Keep four scientific endpoints separate</T>
            {r && o ? (
              <g data-ct-reference data-ct-output>
                <T x={296} y={72}>
                  Astra medium
                </T>
                <T x={468} y={72}>
                  Sol xhigh
                </T>
                {[
                  ['Localized instances', '2/6', '0/6'],
                  ['Foreground Dice B / F', '0.685 / 0.779', '0 / 0'],
                  ['GT macro instance Dice', '0.234', '0'],
                  ['Correct links', '1/4', '0/4'],
                  ['Exact event groups', '0/2', '0/2'],
                ].map(([label, a, b], i) => (
                  <g key={label}>
                    <T y={118 + i * 48} size={17}>
                      {label}
                    </T>
                    <T x={296} y={118 + i * 48} size={17}>
                      {a}
                    </T>
                    <T x={475} y={118 + i * 48} size={17}>
                      {b}
                    </T>
                  </g>
                ))}
                <T y={365} size={17}>
                  Both completed normally; both artifact contracts valid.
                </T>
              </g>
            ) : (
              <Hidden />
            )}
            <T y={402} size={16}>
              {r && o
                ? '0/2 complete groups eligible: merging ability is not isolated.'
                : 'Detection, masks, links and complete events measure different work.'}
            </T>
          </>
        ) : state.scene === 'output' ? (
          <>
            <T y={29}>Submit masks, a complete event ledger and a report</T>
            <Rows
              values={[
                'baseline_instances.nii.gz · exact baseline native grid',
                'followup_instances.nii.gz · exact follow-up native grid',
                'events.json · schema_version 1; each ID once',
                'report.md · method, uncertainty, file + zero-based slice',
                '0 = background; IDs 1–65535; at most 4096 per visit',
              ]}
            />
            <T y={393} size={17}>
              An empty mask pair with groups: [] can pass artifact checks.
            </T>
          </>
        ) : (
          <>
            <T y={29}>The explanation does not close the scientific review</T>
            <Rows
              values={[
                'One selected public pair; one attempt per model',
                'Source annotators had clinical reports; solver had CT only',
                'Instance/confluence convention remains under review',
                'No new or disappearing reference events in this pair',
                'No clinical pass, population estimate or causal model ranking',
              ]}
            />
            <T y={393} size={17}>
              Original outputs and scores retained · no new medical run.
            </T>
          </>
        )}
      </g>
    </svg>
  );
}
export function CtOriginalOutput({ state }: { state: CtOriginalState }) {
  const r = ctShowReference(state),
    o = ctShowOutput(state);
  const a = ref.conditions[0].metrics.association;
  const copy: Record<CtOriginalState['scene'], [string, string]> = {
    inputs: [
      'Search is part of the task',
      'baseline.nii.gz and followup.nii.gz contain full CT volumes. No locations, counts, source identity, masks, links or clinical history were supplied.',
    ],
    instances: [
      'Local IDs, native geometry',
      'Saved-output-selected crops. Amber is the submitted Astra mask, one local ID per visit. A shared integer does not itself establish correspondence. Sol submitted zero positive IDs.',
    ],
    partition: [
      'An unresolved convention',
      'The three baseline reference labels touch. This supports an instruction/reference review, not a claim that the expert partition is wrong. The six native slices show the retained geometry.',
    ],
    focus: [
      'Separate omission',
      'The saved Astra masks cover none of reference B3/F3. These source-selected crops remove localization search and do not establish what the model attended to. Native slice numbers and RAS z differ across unregistered visits.',
    ],
    matching: [
      'Detection differs from segmentation',
      'The 3 mm rule measures from the predicted centroid to labeled reference voxel centers, not reference centroid to centroid. Matching is one-to-one. Foreground overlap does not establish the instance count.',
    ],
    links: [
      'Keep eligibility beside the score',
      `Astra: ${a.links_end_to_end.tp}/4 correct end-to-end links; conditional ${a.links_conditional_on_detection.tp}/${a.links_conditional_on_detection.eligible_gt_edges}, with only ${a.links_conditional_on_detection.eligible_gt_edges}/${a.links_conditional_on_detection.total_gt_edges} reference edges eligible. The graph is schematic, not anatomy.`,
    ],
    events: [
      'Whole groups, not isolated edges',
      'The saved persistent local 1 → 1 maps to B4 → F4. It is not the complete reference merging group. No complete reference event group is eligible after detection, so conditional merging competence is unassessed.',
    ],
    results: [
      'One diagnostic comparison',
      'Astra gpt-6 medium and gpt-5.6-sol xhigh used the same frozen task. Sol’s empty final masks are valid outputs. The convention issue was known before Sol dispatch; no correction or reference feedback was supplied.',
    ],
    output: [
      'Artifact validity is not medical correctness',
      'Two integer native masks, events.json and report.md are required. Include representative evidence and uncertainty; retain analysis scripts and views. Empty valid output does not become a scientific pass.',
    ],
    limits: [
      'Review stays open',
      'Both saved scores replay exactly. The source has four baseline and two follow-up instances, but only merging and persistent events. Public-case exposure and the CT-only clinical-context gap limit interpretation.',
    ],
  };
  const referenceScenes = ['partition', 'focus', 'links', 'events', 'results', 'limits'];
  const gated = referenceScenes.includes(state.scene) && !r;
  return (
    <div className={styles.storyOutput} data-ct-output-panel>
      <strong>{copy[state.scene][0]}</strong>
      <p>
        {gated
          ? 'Reader-only source reference is hidden. Reveal it to inspect the selected views and private evaluation context.'
          : copy[state.scene][1]}
      </p>
      {state.scene === 'results' && (!r || !o) ? (
        <small>Reveal both saved output and reference to inspect the result comparison.</small>
      ) : (
        <small>Native reader explanation · CC BY-NC 4.0 · frozen evidence unchanged</small>
      )}
    </div>
  );
}

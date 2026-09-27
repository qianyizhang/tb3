import type { ReactNode } from 'react';
import {
  mriSource as source,
  mriP02 as p02,
  mriP03 as p03,
  mriRef as ref,
  mriPhaseIndex,
  mriShowOutput,
  mriShowReference,
  projectedMethodBox,
  type MriState,
  type MriMethodView,
} from './longitudinal-mri';
import styles from './task-visual.module.css';
const amber = '#cb8523',
  teal = '#187d74';
const fmt = (n: number, d = 1) => n.toFixed(d);
function Text({
  x = 24,
  y,
  size = 18,
  color,
  children,
}: {
  x?: number;
  y: number;
  size?: number;
  color?: string;
  children: ReactNode;
}) {
  return (
    <text x={x} y={y} style={{ fontSize: size, ...(color ? { fill: color } : {}) }}>
      {children}
    </text>
  );
}
function Scan({
  image,
  x,
  y,
  size = 240,
  fovMm,
  children,
}: {
  image: string;
  x: number;
  y: number;
  size?: number;
  fovMm?: number;
  children?: ReactNode;
}) {
  return (
    <svg x={x} y={y} width={size} height={size} viewBox="0 0 512 512">
      <image data-mri-input href={image} width="512" height="512" />
      {children}
      {fovMm && (
        <g data-mri-scale>
          <rect x="25" y="433" width="175" height="65" fill="black" opacity="0.75" />
          <path d={`M40 479h${(20 / fovMm) * 512}`} stroke="white" strokeWidth="4" />
          <text x="40" y="460" style={{ fill: 'white', fontSize: 24 }}>
            20 mm
          </text>
        </g>
      )}
      <text x="14" y="270" style={{ fill: 'white', fontSize: 28 }}>
        R
      </text>
      <text x="474" y="270" style={{ fill: 'white', fontSize: 28 }}>
        L
      </text>
      <text x="248" y="30" style={{ fill: 'white', fontSize: 28 }}>
        A
      </text>
    </svg>
  );
}
function Lines({ items }: { items: string[] }) {
  return (
    <>
      {items.map((s, i) => (
        <g key={s}>
          <rect x="24" y={58 + i * 71} width="552" height="59" rx="6" fill="#e5ebe2" />
          <Text x={38} y={94 + i * 71} size={17}>
            {s}
          </Text>
        </g>
      ))}
    </>
  );
}
function Method({ v, x, show }: { v: MriMethodView; x: number; show: boolean }) {
  const box = projectedMethodBox(v);
  return (
    <g>
      <Text x={x} y={63} size={17}>
        {v.visit} · {v.series} · file phase 0
      </Text>
      <svg x={x} y="83" width="244" height="244" viewBox="0 0 120 120">
        <image href={v.image} width="120" height="120" data-mri-input />
        <g data-mri-scale>
          <rect x="3" y="98" width="48" height="21" fill="black" opacity="0.75" />
          <path d={`M8 114h${20 / v.spacing_mm[0]}`} stroke="white" strokeWidth="1" />
          <text x="8" y="108" style={{ fill: 'white', fontSize: 6 }}>
            20 mm
          </text>
        </g>
        {show && <rect data-mri-output {...box} fill="none" stroke={amber} strokeWidth="1.2" />}
      </svg>
      {show && (
        <g data-mri-output>
          <Text x={x} y={353} color={amber}>
            {fmt(v.diameter_mm, 3)} mm
          </Text>
          <Text x={x} y={378} size={15}>
            {v.bbox_mm.map((n) => fmt(n, 1)).join(' × ')} mm box
          </Text>
        </g>
      )}
    </g>
  );
}
export function MriScene({ state }: { state: MriState }) {
  const r = mriShowReference(state),
    o = mriShowOutput(state),
    phase = mriPhaseIndex(state.view),
    cite = p02.citation;
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Native longitudinal MRI inputs, saved measurements and separately revealed source references"
      data-mri-scene={state.scene}
    >
      <g>
        {state.scene === 'inputs' ? (
          <>
            <Text y={28}>Three cases · first two available MRI exams</Text>
            {source.overview.map((c, i) => (
              <g key={c.case}>
                {c.visits.map((v, j) => (
                  <g key={v.id}>
                    <Scan image={v.image} x={22 + i * 193} y={55 + j * 145} size={128} />
                    <Text x={22 + i * 193} y={194 + j * 145} size={14}>
                      {c.case} {v.visit} · day {v.day} · k{v.k}
                    </Text>
                  </g>
                ))}
              </g>
            ))}
            <Text y={372} size={17}>
              Full volumes supplied; these are middle-slice previews.
            </Text>
            <Text y={400} size={16}>
              Labels, later visits and pathology withheld from solver.
            </Text>
          </>
        ) : state.scene === 'locate' ? (
          <>
            <Text y={29}>A finding needs a native image citation</Text>
            <Scan
              image={o ? cite.image : source.overview[1].visits[0].image}
              x={24}
              y={60}
              size={280}
              fovMm={360}
            >
              {o && (
                <path
                  data-mri-output
                  d={`M${cite.voxel[0] - 12} ${cite.voxel[1]}h24M${cite.voxel[0]} ${cite.voxel[1] - 12}v24`}
                  stroke={amber}
                  strokeWidth="3"
                />
              )}
            </Scan>
            {o ? (
              <g data-mri-output>
                <Text x={325} y={85} color={amber}>
                  Saved P02 citation
                </Text>
                <Text x={325} y={125} size={17}>
                  V1 · S20 · phase 1
                </Text>
                <Text x={325} y={165} size={17}>
                  voxel [386, 155, 84]
                </Text>
                <Text x={325} y={205} size={17}>
                  native affine → RAS mm
                </Text>
                <Text x={325} y={244} size={16}>
                  [{cite.ras_mm.map((n) => fmt(n, 2)).join(', ')}]
                </Text>
                <Text x={325} y={291} size={16}>
                  Patient left is screen right.
                </Text>
              </g>
            ) : (
              <Text x={325} y={135}>
                Saved citation hidden
              </Text>
            )}
            <Text y={375} size={17}>
              A citation locates a statement; it is not a lesion boundary.
            </Text>
            <Text y={402} size={16}>
              Cross-visit voxel coordinates are not registered.
            </Text>
          </>
        ) : state.scene === 'phases' || state.scene === 'sequences' ? (
          <>
            <Text y={29}>
              {state.scene === 'phases'
                ? 'Keep the window fixed while changing phase'
                : 'Check another sequence in its own native frame'}
            </Text>
            {r ? (
              <g data-mri-reference>
                {p02.visits.map((v, j) => (
                  <g key={v.visit}>
                    <Text x={24 + j * 288} y={60} size={17}>
                      {v.visit} ·{' '}
                      {state.scene === 'phases'
                        ? `${v.series} phase ${v.phases[phase].phase}`
                        : `${v.t2.series} T2 fat-sat`}
                    </Text>
                    <Scan
                      image={state.scene === 'phases' ? v.phases[phase].image : v.t2.image}
                      x={24 + j * 288}
                      y={79}
                      size={240}
                      fovMm={110 * v.spacing_mm[0]}
                    />
                    <Text x={24 + j * 288} y={344} size={15}>
                      {state.scene === 'phases'
                        ? `${v.phases[phase].offset_s} s from first frame · k${v.center[2]}`
                        : `center [${v.t2.center.join(', ')}]`}
                    </Text>
                  </g>
                ))}
                <Text y={376} size={16} color={teal}>
                  Reader reference: source-VOI selected 110 × 110 crops.
                </Text>
                <Text y={402} size={16}>
                  {state.scene === 'phases'
                    ? 'Windows fixed per visit; intensities not calibrated across visits.'
                    : 'Native affine maps source center; this is not image registration.'}
                </Text>
              </g>
            ) : (
              <Lines
                items={[
                  'Source-selected crops withheld until reference reveal.',
                  'The original task required localization in full volumes.',
                  'A selected crop does not test autonomous search.',
                ]}
              />
            )}
          </>
        ) : state.scene === 'measure' ? (
          <>
            <Text y={29}>P03 neutral · reproduce the saved component method</Text>
            {p03.methods[0].visits.map((v, i) => (
              <Method v={v} x={24 + i * 288} show={o} key={v.visit} />
            ))}
            <Text y={407} size={15}>
              Amber: projection of 3-D method box · not clinical lesion GT
            </Text>
          </>
        ) : state.scene === 'change' ? (
          <>
            <Text y={29}>The paired cue run changed several method choices</Text>
            {o ? (
              <g data-mri-output>
                {p03.methods.map((m, i) => (
                  <g key={m.condition}>
                    <Text x={30 + i * 290} y={79} color={amber}>
                      {i ? 'Misleading-cue run' : 'Neutral run'}
                    </Text>
                    <Text x={30 + i * 290} y={124} size={24}>
                      {fmt(m.visits[0].diameter_mm, 3)} → {fmt(m.visits[1].diameter_mm, 3)}
                    </Text>
                    <Text x={30 + i * 290} y={161} size={16}>
                      millimetres · recomputed box span
                    </Text>
                    <Text x={30 + i * 290} y={218} size={32}>
                      {fmt(m.change_percent)}%
                    </Text>
                    <Text x={30 + i * 290} y={268} size={16}>
                      {i ? 'post 3 → 1 · threshold 0.50' : 'post 1 → 1 · threshold 0.30'}
                    </Text>
                    <Text x={30 + i * 290} y={303} size={16}>
                      {i ? 'no smoothing · voxel centers' : 'sigma 1 voxel · voxel edges'}
                    </Text>
                  </g>
                ))}
                <Text y={360} size={17}>
                  Same input images · one pair · diagnostic comparison
                </Text>
                <Text y={392} size={16}>
                  Method changes confound causal attribution to the cue.
                </Text>
              </g>
            ) : (
              <Text y={130}>Saved-method results hidden</Text>
            )}
          </>
        ) : state.scene === 'reference' ? (
          <>
            <Text y={29}>Diameter, functional volume and pathology differ</Text>
            {r ? (
              <g data-mri-reference>
                <Text x={30} y={77} size={16}>
                  Case
                </Text>
                <Text x={135} y={77} size={16}>
                  Source diameter Δ
                </Text>
                <Text x={365} y={77} size={16}>
                  Source FTV Δ
                </Text>
                {ref.cases.map((c, i) => (
                  <g key={c.case}>
                    <Text x={30} y={130 + i * 68}>
                      {c.case}
                    </Text>
                    <Text x={135} y={130 + i * 68} size={26} color={teal}>
                      {fmt(c.diameter_change_percent)}%
                    </Text>
                    <Text x={365} y={130 + i * 68} size={26} color={teal}>
                      {c.ftv_change_percent > 0 ? '+' : ''}
                      {fmt(c.ftv_change_percent)}%
                    </Text>
                  </g>
                ))}
                <Text y={323} size={17}>
                  V1 → V2 · diameter unit unresolved in workbook
                </Text>
                <Text y={358} size={17}>
                  FTV uses enhancement criteria and a source VOI.
                </Text>
                <Text y={393} size={16}>
                  Neither endpoint directly establishes viable tumor or pCR.
                </Text>
              </g>
            ) : (
              <Lines
                items={[
                  'Source measurements withheld until reader reveal.',
                  'Use unit-invariant diameter change, not assumed mm.',
                  'Functional volume and pathology are distinct endpoints.',
                ]}
              />
            )}
          </>
        ) : state.scene === 'output' ? (
          <>
            <Text y={29}>Return a qualified, inspectable assessment</Text>
            <Lines
              items={[
                'assessment.json: native citations for both visits',
                'Comparison: number or null + explicit method',
                'Impression: alternatives, confidence, limitations',
                'Forecast: direction, confidence, assumptions',
              ]}
            />
            <Text y={379} size={17}>
              report.md + analysis code + key figures
            </Text>
            <Text y={405} size={16}>
              Saved P02 V2 diameter is null; that is schema-valid.
            </Text>
          </>
        ) : state.scene === 'forecast' ? (
          <>
            <Text y={29}>A correct direction still needs a baseline</Text>
            {r ? (
              <g data-mri-reference>
                <Lines
                  items={[
                    'Three neutral forecasts: smaller in all three',
                    'Always-smaller baseline: also matches 3 / 3',
                    'P03 cue is the same patient, not a fourth case',
                  ]}
                />
                <Text y={307} size={20} color={teal}>
                  Next-visit source diameter: smaller in 3 / 3
                </Text>
                <Text y={355} size={17}>
                  No individualized forecast advantage established.
                </Text>
                <Text y={391} size={16}>
                  Future visits were withheld from the original solver.
                </Text>
              </g>
            ) : (
              <Text y={140}>Future source measurements withheld until reveal</Text>
            )}
          </>
        ) : (
          <>
            <Text y={29}>Four completed attempts; clinical success unassessed</Text>
            <Lines
              items={[
                '4 / 4 mechanical passes: structure and citation bounds',
                'No adjudicated clinical pass rate or measurement GT',
                'Three selected public cases; no population estimate',
                'One cue pair; no established causal prompt effect',
              ]}
            />
            <Text y={384} size={17}>
              Reproduction preserves original scores and uncertainty.
            </Text>
          </>
        )}
      </g>
    </svg>
  );
}
const copy: Record<MriState['scene'], [string, string, string]> = {
  inputs: [
    'Solver packet',
    'Full reconstructed MRI volumes, sequence metadata, native affines and relative days for two visits.',
    'P01/P02/P03: 22 / 40 / 122 volumes, including split scouts. No prior reports, pathology, treatment labels or future visits.',
  ],
  locate: [
    'Image-cited observation',
    'Visit + series + zero-based phase + zero-based voxel + description.',
    'The amber cross is a saved answer point, not adjudicated target truth. Use the affine; laterality is anatomical.',
  ],
  phases: [
    'Sequence and phase choice',
    'Compare phases 0, 1, 2 and 6 at the same native slice with a fixed display window.',
    'These source-VOI selected reader crops remove the search step. Phase-dependent appearance does not validate a diameter.',
  ],
  sequences: [
    'Corroborate and qualify',
    'Review T2 alongside the dynamic series; report sequence-specific observations.',
    'Each sequence uses its own affine. An approximate source-center mapping does not register the breasts across visits.',
  ],
  measure: [
    'Define the measured object',
    'Saved neutral P03: post-minus-pre, Gaussian sigma 1 voxel, 30% threshold, connected component, voxel-edge box.',
    'The displayed rectangle projects a 3-D component box. Its longest axis is reproducible but not an adjudicated clinical diameter.',
  ],
  change: [
    'Diagnostic comparison',
    'Recompute both saved methods on identical input images. Both outputs reject the disappearance cue.',
    'Phase, threshold, smoothing and box convention differ. One paired run cannot isolate the cue or ordinary run variability.',
  ],
  reference: [
    'Reader-only source endpoints',
    'Reveal source FTV and unit-invariant diameter changes separately from saved enhancing-component spans.',
    'Source workbook diameter units remain unresolved. Regional VOIs are not exhaustive tumor boundaries; pCR is a separate endpoint.',
  ],
  output: [
    'Deliverable and uncertainty',
    'P02 reported 31.0 mm at V1 and null at V2, with a method and limitations.',
    'Null is permitted. The schema checker cannot determine whether a residual boundary is clinically unmeasurable.',
  ],
  forecast: [
    'Future prediction',
    'Specify next_exam_extent, confidence, basis and assumptions without seeing future MRI.',
    'All three source next-visit diameters decreased. The always-smaller baseline ties these neutral forecasts; no calibration claim follows.',
  ],
  limits: [
    'What the study establishes',
    'Four normal completions and four mechanical passes; fixture/no-op controls were healthy in each condition.',
    'No clinical pass rate, independently adjudicated failure, causal cue effect or held-out generalization is established.',
  ],
};
export function MriOutput({ state }: { state: MriState }) {
  const [heading, body, limit] = copy[state.scene];
  return (
    <div className={styles.storyOutput} data-mri-output-panel>
      <strong>{heading}</strong>
      <p>{body}</p>
      <small>{limit}</small>
      <small>
        {mriShowReference(state)
          ? 'Source reference revealed for the reader.'
          : mriShowOutput(state)
            ? 'Saved output / post-hoc method display.'
            : 'Input and contract view; references hidden.'}
      </small>
    </div>
  );
}

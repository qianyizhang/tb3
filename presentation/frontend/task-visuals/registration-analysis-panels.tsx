import {
  analysisGeometry as g,
  analysisReference as r,
  analysisColors as c,
  originalVariant,
  supportRows,
  objectiveSamples,
  analysisRevealed,
  type AnalysisState,
  type Patch,
} from './registration-analysis';
import styles from './task-visual.module.css';
const n = (v: number) => v.toFixed(3);
function Source({ context = false }: { context?: boolean }) {
  const width = 440,
    height = (width * g.source_view.height) / g.source_view.width,
    s = width / g.source_view.width;
  const [u, v] = g.queries.pixels_uv[4];
  return (
    <>
      <image href={g.source_view.png} x="80" y="45" width={width} height={height} />
      {g.queries.pixels_uv.map(([x, y], i) => (
        <circle
          key={i}
          cx={80 + (x + 0.5) * s}
          cy={45 + (y + 0.5) * s}
          r="4"
          fill={c.query}
          stroke="white"
          strokeWidth="1"
        />
      ))}
      {context &&
        [25, 16, 10, 8].map((half, i) => (
          <rect
            key={half}
            x={80 + (u + 0.5 - half / 1.25) * s}
            y={45 + (v + 0.5 - half / 1.25) * s}
            width={(half / 1.25) * s * 2}
            height={(half / 1.25) * s * 2}
            stroke={i === 3 ? c.query : c.neutral}
            fill="none"
            strokeWidth="2"
            strokeDasharray={i === 3 ? '4 3' : undefined}
          />
        ))}
      <text x="25" y="380">
        {context
          ? 'q05: blue 25 → 16 → 10 mm; orange dashed 8 mm'
          : 'Complete 171 × 118 source slice · eight public queries'}
      </text>
      <text x="25" y="405" fontSize="13">
        {context
          ? 'Posthoc size illustration; the source location is not a solver intervention.'
          : 'Actual case 1 CT · HU −1000 to 200 · no full source volume supplied'}
      </text>
    </>
  );
}
function PatchImage({
  patch,
  x,
  y,
  label,
}: {
  patch?: Patch;
  x: number;
  y: number;
  label: string;
}) {
  return (
    <g>
      <text x={x} y={y - 7} fontSize="14">
        {label}
      </text>
      {patch ? (
        <image
          href={patch.png}
          x={x}
          y={y}
          width="120"
          height="120"
          style={{ imageRendering: 'pixelated' }}
        />
      ) : (
        <rect x={x} y={y} width="120" height="120" fill="#e8e9e2" />
      )}
    </g>
  );
}
export function RegistrationAnalysisScene({ state }: { state: AnalysisState }) {
  const visible = analysisRevealed(state),
    data = r.analysis;
  let content;
  if (state.scene === 'input' || state.scene === 'context')
    content = <Source context={state.scene === 'context'} />;
  else if (state.scene === 'replay') {
    const labels: { key: string; name: string }[] = [
      { key: 'nominal', name: 'Nominal' },
      { key: 'rigid', name: 'Rigid' },
      { key: 'affine_only', name: 'Affine only' },
      { key: 'direct_bspline', name: 'B only' },
      { key: 'original_composition', name: 'A(B)' },
      { key: 'final', name: 'Patch search' },
    ];
    content = (
      <>
        <text x="25" y="35">
          Reconstructed stages · RMS over eight points (mm)
        </text>
        {labels.map(({ key, name }, i) => (
          <g key={key}>
            <text x="20" y={79 + i * 45} fontSize="15">
              {name}
            </text>
            <rect
              x="175"
              y={60 + i * 45}
              width={visible ? data.replay.stages[key].rms_mm * 13 : 0}
              height="25"
              fill={c.output}
            />
            <text
              x={185 + (visible ? data.replay.stages[key].rms_mm * 13 : 0)}
              y={79 + i * 45}
              fontSize="14"
            >
              {visible ? n(data.replay.stages[key].rms_mm) : 'hidden'}
            </text>
          </g>
        ))}
        <text x="25" y="374">
          Replay drift: {visible ? '6.30 × 10⁻⁹ mm' : 'hidden'}
        </text>
        <text x="25" y="404" fontSize="13">
          Saved stages from a replacement image; no new execution here.
        </text>
      </>
    );
  } else if (state.scene === 'composition') {
    content = (
      <>
        <text x="25" y="40">
          Which moving image was B fitted against?
        </text>
        {['Original code', 'Minimal repair', 'Secondary structural repair'].map((label, i) => (
          <g key={label}>
            <text x="25" y={92 + i * 108} fontSize="15">
              {label}
            </text>
            <rect
              x="260"
              y={64 + i * 108}
              width="310"
              height="72"
              rx="4"
              fill="#eef0e9"
              stroke={i === 0 ? c.reference : c.output}
            />
            <text x="277" y={91 + i * 108} fontSize="16">
              {i === 0
                ? 'Fit B against original moving'
                : i === 1
                  ? 'Use the same fitted B'
                  : 'Refit B against A-resampled image'}
            </text>
            <text x="277" y={116 + i * 108} fontSize="17">
              {i === 1 ? 'x → B(x)' : 'x → B(x) → A(B(x))'}
            </text>
          </g>
        ))}
        <text x="25" y="402" fontSize="13">
          The defect concerns B’s fitting image; simply swapping A and B is not the repair.
        </text>
      </>
    );
  } else if (state.scene === 'support') {
    const row = supportRows(state.bounds)[3],
      half = row.halfWidth;
    content = (
      <>
        <text x="25" y="30">
          q04 · saved orthonormal search axes (mm)
        </text>
        <text x="25" y="50" fontSize="12">
          Orange: search box · Pink: manual target · Dashed: nearest-box residual
        </text>
        {[1, 2].map((axis, i) => {
          const cx = 150 + i * 295,
            cy = 190,
            s = 3.2,
            x = (v: number) => cx + v * s,
            y = (v: number) => cy - v * s;
          return (
            <g key={axis}>
              <path d={`M${x(-40)},${cy}H${x(40)}M${cx},${y(-40)}V${y(40)}`} stroke="#aab3a7" />
              {[-40, -20, 20, 40].map((t) => (
                <g key={t}>
                  <text x={x(t) - 9} y={cy + 17} fontSize="11">
                    {t}
                  </text>
                  <text x={cx + 4} y={y(t)} fontSize="11">
                    {t}
                  </text>
                </g>
              ))}
              <rect
                x={x(-half)}
                y={y(half)}
                width={half * s * 2}
                height={half * s * 2}
                fill={c.query}
                fillOpacity=".08"
                stroke={c.query}
                strokeWidth="2"
              />
              {visible && (
                <>
                  <line
                    x1={x(row.nearest[0])}
                    y1={y(row.nearest[axis])}
                    x2={x(row.true_offset_local_mm[0])}
                    y2={y(row.true_offset_local_mm[axis])}
                    stroke={c.reference}
                    strokeWidth="2"
                    strokeDasharray="4 3"
                  />
                  <circle
                    cx={x(row.true_offset_local_mm[0])}
                    cy={y(row.true_offset_local_mm[axis])}
                    r="5"
                    fill={c.reference}
                  />
                  <rect
                    x={x(row.nearest[0]) - 3}
                    y={y(row.nearest[axis]) - 3}
                    width="6"
                    height="6"
                    fill={c.query}
                  />
                </>
              )}
              <text x={cx - 60} y="355">
                e1 / e{axis + 1} projection
              </text>
            </g>
          );
        })}
        <text x="25" y="388">
          Half-width ±{half.toFixed(1)} mm · full 3D lower bound:{' '}
          {visible ? `${row.distance.toFixed(2)} mm` : 'hidden'}
        </text>
        <text x="25" y="410" fontSize="12">
          Extent animation is illustrative. Only ±9 and ±30 mm searches were executed.
        </text>
      </>
    );
  } else if (state.scene === 'objective') {
    content = (
      <>
        {['q01', 'q06'].map((id, i) => (
          <g key={id}>
            <text x="12" y={44 + i * 158}>
              {id}
            </text>
            <PatchImage patch={g.patches[id].source} x={62} y={35 + i * 158} label="Source" />
            <PatchImage
              patch={visible ? r.manual_patches[id] : undefined}
              x={204}
              y={35 + i * 158}
              label="Manual"
            />
            <PatchImage
              patch={g.patches[id].submitted}
              x={346}
              y={35 + i * 158}
              label="Submitted"
            />
          </g>
        ))}
        <text x="25" y="355" fontSize="14">
          21 × 21 samples · 0.8 mm grid · 8 mm half-span
        </text>
        <text x="25" y="380" fontSize="13">
          Patches are independently centred for appearance comparison.
        </text>
        <text x="25" y="403" fontSize="13">
          Saved target axes are fixed. These panels do not depict displacement.
        </text>
      </>
    );
  } else if (state.scene === 'repeats' || state.scene === 'limits') {
    content = (
      <>
        <text x="25" y="30">
          Each point error (mm) · same eight-query task
        </text>
        {r.attempts.map((attempt, i) => (
          <g key={attempt.phase}>
            <text x="25" y={60 + i * 111} fontSize="15">
              {['Original', 'Fresh 2', 'Fresh 3'][i]}
            </text>
            <line
              x1="185"
              x2="565"
              y1={125 + i * 111 - 5 * 1.8}
              y2={125 + i * 111 - 5 * 1.8}
              stroke={c.reference}
              strokeDasharray="4 3"
            />
            {[0, 20, 40].map((tick) => (
              <text key={tick} x="166" y={129 + i * 111 - tick * 1.8} fontSize="10">
                {tick}
              </text>
            ))}
            {attempt.grade.per_point_mm.map((v, j) => (
              <g key={j}>
                <rect
                  x={195 + j * 45}
                  y={125 + i * 111 - v * 1.8}
                  width="18"
                  height={v * 1.8}
                  fill={c.output}
                />
                <text x={190 + j * 45} y={144 + i * 111} fontSize="11">
                  q0{j + 1}
                </text>
              </g>
            ))}
          </g>
        ))}
        <text x="25" y="404" fontSize="13">
          Dashed = 5 mm maximum gate · selected miss is not a random first sample.
        </text>
      </>
    );
  }
  return (
    <svg
      className={`${styles.operationCanvas} ${styles.analysisCanvas}`}
      data-analysis-scene={state.scene}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Retained registration postmortem with actual CT patches, calibrated search bounds and separate diagnostic scores"
    >
      {content}
    </svg>
  );
}
function Curves({ state }: { state: AnalysisState }) {
  return (
    <svg
      viewBox="0 0 430 105"
      role="img"
      aria-label="Diagnostic objective along the straight segment from manual target to submitted point, not a search trajectory"
      style={{ width: '100%', height: 105 }}
    >
      <path d="M30 5V75H415" fill="none" stroke="#9ba69d" />
      {[0, 1].map((v) => (
        <text key={v} x="5" y={79 - v * 65} fontSize="11">
          {v}
        </text>
      ))}
      {['q01', 'q06'].map((id, i) => (
        <g key={id}>
          <polyline
            points={objectiveSamples(id, state.curve)
              .map((p) => `${30 + p.t * 385},${75 - p.score * 65}`)
              .join(' ')}
            fill="none"
            stroke={i ? c.neutral : c.output}
            strokeWidth="2"
          />
          <circle
            cx={30 + objectiveSamples(id, state.curve).at(-1)!.t * 385}
            cy={75 - objectiveSamples(id, state.curve).at(-1)!.score * 65}
            r="2.5"
            fill={i ? c.neutral : c.output}
          />
          <text x={210 + i * 85} y="15" fill={i ? c.neutral : c.output} fontSize="12">
            {id}
          </text>
        </g>
      ))}
      <text x="30" y="99" fontSize="11">
        Manual target
      </text>
      <text x="325" y="99" fontSize="11">
        Submitted point
      </text>
    </svg>
  );
}
export function RegistrationAnalysisOutput({ state }: { state: AnalysisState }) {
  const a = r.analysis,
    visible = analysisRevealed(state),
    rows = supportRows(state.bounds);
  const titles = {
    input: 'A postmortem of one selected failure',
    replay: 'Replay fidelity before attribution',
    composition: 'A real bug, without a rescue',
    support: 'Search support and optimization are separate',
    objective: 'Similarity can favor a reference-disagreeing match',
    context: 'Context helps inside this author pipeline',
    repeats: 'Two predeclared fresh attempts split',
    limits: 'Different queries support different explanations',
  };
  return (
    <aside className={styles.storyOutput} data-registration-analysis-output>
      <strong>{titles[state.scene]}</strong>
      {state.scene === 'input' ? (
        <>
          <p>
            <b>Solver:</b> one exhale section, a complete inhale CT, eight fractional-pixel queries
            and the known source pose.
          </p>
          <p>
            Return eight target XYZ points in dataset-world mm. Both <b>RMS ≤ 3 mm</b> and{' '}
            <b>maximum ≤ 5 mm</b> must pass.
          </p>
          <p>
            <b>Postmortem author:</b> saved code, outputs, reconstructed transforms and privileged
            manual targets.
          </p>
          <p>
            The original Terra/high miss was selected after its outcome. BR-022 separately fixed
            interventions and two fresh repeats.
          </p>
          <small>This is an author analysis, not another autonomous task or a new model run.</small>
        </>
      ) : state.scene === 'replay' ? (
        <>
          <p>
            Recovered trace steps <b>12–19</b> reproduce all eight submitted coordinates to{' '}
            <b>6.30 × 10⁻⁹ mm</b>.
          </p>
          <p>
            The original trial image was removed. Historical replay used a retained image built from
            the identical Dockerfile, with matching public files and pinned packages.
          </p>
          <p>
            Original final error:{' '}
            <b data-analysis-reference>{visible ? '12.641 RMS / 23.796 max mm' : 'hidden'}</b>.
          </p>
          <p>
            Nominal → rigid improves the fit. Direct B-spline worsens it; the extra affine barely
            changes aggregate RMS.
          </p>
          <small>
            Saved intermediate states are reconstructed artifacts. Numerical equivalence does not
            turn replay into fresh execution.
          </small>
        </>
      ) : state.scene === 'composition' ? (
        <>
          <p>
            B was fitted against the original moving image, then evaluated as <code>A(B(x))</code>.
            The minimal consistent mapping is <code>B(x)</code>.
          </p>
          <table className={styles.screenTable}>
            <thead>
              <tr>
                <th>Seed 17 mapping</th>
                <th>±9 mm RMS / max</th>
                <th>±30 mm RMS / max</th>
              </tr>
            </thead>
            <tbody>
              {[
                ['original', 'A(B)'],
                ['direct_bspline', 'B'],
                ['residual_on_affine', 'Refit, then A(B)'],
              ].map(([key, label]) => (
                <tr key={key}>
                  <td>{label}</td>
                  {[9, 30].map((bound) => {
                    const v = a.counterfactuals.find(
                      (v) => v.composition === key && v.bound_mm === bound && v.seed === 17,
                    )!;
                    return (
                      <td key={bound}>
                        {n(v.grade.rms_mm)} / {n(v.grade.max_mm)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            <b>All 12 primary variants failed:</b> two mappings × two bounds × seeds 17/41/73. Both
            secondary refits also failed.
          </p>
          <small>
            Author interventions; no hidden-score selection for a subsequent agent. Wider bounds
            used the same finite optimizer settings.
          </small>
        </>
      ) : state.scene === 'support' ? (
        <>
          <p>
            <b>q04</b> requires local offset <b>[−9.12, −27.27, +14.19] mm</b>. The two plots
            preserve all three axes.
          </p>
          <table className={styles.screenTable}>
            <thead>
              <tr>
                <th>Query</th>
                <th>Distance to current box</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td>{row.id}</td>
                  <td data-analysis-bound>{row.distance.toFixed(3)} mm</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            At ±9 mm, q04 is <b>18.994 mm</b> outside the box; even perfect box optimization cannot
            pass. The eight-point RMS lower bound is <b>6.78 mm</b>.
          </p>
          <small>
            At ±30 mm all references enter the box, yet all fixed-seed original/minimal searches
            still fail. Including every reference does not guarantee a passing search.
          </small>
        </>
      ) : state.scene === 'objective' ? (
        <>
          <table className={styles.screenTable}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Manual</th>
                <th>Output</th>
                <th>Best ≤3 mm</th>
              </tr>
            </thead>
            <tbody>
              {[0, 5].map((i) => {
                const d = a.objective_diagnostics[i];
                return (
                  <tr key={d.id}>
                    <td>{d.id}</td>
                    <td>{n(d.score_at_manual_target)}</td>
                    <td>{n(d.score_at_submitted_point)}</td>
                    <td>{n(d.best_found_score_within_3mm_of_manual)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <p>
            Original mixed NCC objective: <b>higher is better</b>. Both references are inside their
            original boxes, yet the submitted errors are <b>16.334</b> and <b>8.638 mm</b>.
          </p>
          <Curves state={state} />
          <p>
            The curves interpolate from manual to submitted locations; they are{' '}
            <b>not search trajectories</b>.
          </p>
          <small>
            Privileged, finite near-reference search is not a global optimum. No NCC cutoff is
            validated. q02 has a different pattern: a better near-reference score was found.
          </small>
        </>
      ) : state.scene === 'context' ? (
        <>
          <table className={styles.screenTable}>
            <thead>
              <tr>
                <th>Author model</th>
                <th>8/8/8 mm</th>
                <th>25/16/10 mm</th>
              </tr>
            </thead>
            <tbody>
              {['translation', 'affine'].map((model) => (
                <tr key={model}>
                  <td>{model}</td>
                  {['small', 'multiscale'].map((context) => {
                    const v = a.author_baseline_ablations.find(
                      (v) => v.name === `${model}-${context}`,
                    )!;
                    return (
                      <td key={context}>
                        {n(v.grade.rms_mm)} / {n(v.grade.max_mm)}
                        <br />
                        {v.grade.reward ? 'pass' : 'fail'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            Cells show eight-point <b>RMS / maximum mm</b>. Blue windows: 25 → 16 → 10 mm; orange
            dashed: 8 mm. Sizes are half-widths.
          </p>
          <p>
            Broad nominal search, blur and candidate selection stayed fixed. Larger context rescues
            both local models here; affine freedom does not.
          </p>
          <small>
            This is a different author pipeline, not a one-line repair of the agent. Independent
            point translations are globally nonrigid.
          </small>
        </>
      ) : state.scene === 'repeats' ? (
        <>
          <table className={styles.screenTable}>
            <thead>
              <tr>
                <th>Terra/high</th>
                <th>RMS / max mm</th>
                <th>Gate</th>
              </tr>
            </thead>
            <tbody>
              {r.attempts.map((v, i) => (
                <tr key={v.phase}>
                  <td>{['Selected original', 'Fresh 2', 'Fresh 3'][i]}</td>
                  <td>
                    {n(v.grade.rms_mm)} / {n(v.grade.max_mm)}
                  </td>
                  <td>{v.grade.reward ? 'pass' : 'fail'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            Same frozen task and runtime request; fresh independent sessions, zero retries, no prior
            code, answers or diagnostic hints. Both completed normally.
          </p>
          <p>
            Matched oracle/nop controls scored <b>1/0</b>. Fresh 3 passed with final <b>15 × 15</b>{' '}
            patches, broad candidate search and additional verification.
          </p>
          <small>
            Small patches can succeed in another strategy. No ablation isolates its visual choice or
            orientation refinement; no population success rate is estimated.
          </small>
        </>
      ) : (
        <>
          <p>
            <b>Observed defect:</b> inconsistent composition. Minimal correction preserves the
            failure.
          </p>
          <p>
            <b>q04 support:</b> the original box excludes any target within tolerance.
          </p>
          <p>
            <b>q01/q06 objective:</b> local similarity prefers submitted points over tested
            reference neighborhoods.
          </p>
          <p>
            <b>Limits:</b> q02 differs; finite search does not establish global optimality. Manual
            references and eight sparse points do not certify dense or clinical accuracy.
          </p>
          <small>
            Retire this exact case as reliably difficult after the fresh pass. Keep all original
            scores; any multi-patient study requires separate authorization.
          </small>
        </>
      )}
    </aside>
  );
}

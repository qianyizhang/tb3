import {
  dtiInput as input,
  dtiData as data,
  dtiReference as ref,
  dtiIndex,
  dtiReveal,
  dtiScalar,
  type DtiState,
  type DtiImage,
  type DtiTensor,
} from './imaging101-dti';
import css from './imaging101-dti.module.css';
const green = '#264b43',
  orange = '#b9521e',
  purple = '#8052a1',
  gray = '#788c84';
const n = (v: number, d = 3) => v.toFixed(d);
const axes = ['x', 'y', 'z'];
const titles = {
  inputs: 'A gradient changes the measured signal',
  gradients: '31 measurements constrain seven parameters',
  fit: 'One fixed pixel links measurements to a tensor',
  tensor: 'Inspect the saved tensor in three source planes',
  output: 'Compare saved OLS and WLS scalar maps',
  reference: 'Reveal simulated truth and saved-map error',
  scoring: 'A score can check only part of the output',
  limits: 'Keep source and evaluator boundaries explicit',
};
function Plane({
  image,
  label,
  pixel,
  reference = false,
  small = false,
}: {
  image: DtiImage;
  label: string;
  pixel?: [number, number];
  reference?: boolean;
  small?: boolean;
}) {
  return (
    <figure
      className={`${css.plane} ${small ? css.small : ''}`}
      data-dti-panel={reference ? 'reference' : 'source'}
    >
      <figcaption>{label}</figcaption>
      <svg viewBox="0 0 220 210" role="img" aria-label={label}>
        <rect x="20" y="8" width="180" height="180" fill="#e9eee6" />
        <image href={image.data} x="20" y="8" width="180" height="180" preserveAspectRatio="none" />
        <rect
          x="20"
          y="8"
          width="180"
          height="180"
          fill="none"
          stroke={reference ? purple : green}
          strokeDasharray={reference ? '5 3' : undefined}
        />
        {pixel && (
          <g stroke={orange} strokeWidth="2" fill="none">
            <circle
              cx={20 + ((pixel[1] + 0.5) / 128) * 180}
              cy={8 + ((pixel[0] + 0.5) / 128) * 180}
              r="7"
            />
          </g>
        )}
        <text x="110" y="205" textAnchor="middle">
          128 × 128 · rows down / columns right
        </text>
      </svg>
      <div className={css.scale}>
        <span>0</span>
        <i />
        <span>{n(image.range[1], image.range[1] === 1 ? 0 : 2)}</span>
      </div>
      <p className={css.unit}>
        {image.unit}
        {image.masked ? ' · supplied mask' : ''}
      </p>
    </figure>
  );
}
function Gradients({ index }: { index: number }) {
  const g = input.gradients.bvecs[index];
  const project = (v: number[]) => [180 + v[0] * 95 - v[1] * 44, 150 - v[2] * 95 + v[1] * 30];
  const end = project(g);
  return (
    <div className={css.two}>
      <div>
        <svg
          className={css.gradient}
          viewBox="0 0 360 290"
          role="img"
          aria-label={`Source gradient ${index}`}
        >
          {axes.map((name, i) => {
            const a = [0, 0, 0];
            a[i] = 1.25;
            const p = project(a);
            return (
              <g key={name}>
                <path d={`M180 150L${p[0]} ${p[1]}`} stroke={gray} />
                <text x={p[0] + 5} y={p[1] + 4}>
                  {name}
                </text>
              </g>
            );
          })}
          {input.gradients.bvecs.slice(1).map((v, i) => {
            const p = project(v);
            return <rect key={i} x={p[0] - 2} y={p[1] - 2} width="4" height="4" fill={green} />;
          })}
          <path d={`M180 150L${end[0]} ${end[1]}`} stroke={orange} strokeWidth="3" />
          <circle key={index} cx={end[0]} cy={end[1]} r="6" fill={orange} />
          <text x="180" y="274" textAnchor="middle">
            Source axes · fixed oblique projection
          </text>
        </svg>
        <p className={css.formula}>S = S₀ exp(−b gᵀDg)</p>
      </div>
      <div className={css.card} data-dti-gradient-row={index}>
        <h4>
          Volume {index} · b = {input.gradients.bvals[index]} s/mm²
        </h4>
        <p>g = [{g.map((v) => n(v)).join(', ')}]</p>
        <div className={css.coefficients}>
          {['ln S₀', 'Dxx', 'Dxy', 'Dxz', 'Dyy', 'Dyz', 'Dzz'].map((label, i) => (
            <div key={label}>
              <span>{label}</span>
              <strong>{n(input.gradients.design_matrix[index][i], i ? 2 : 0)}</strong>
            </div>
          ))}
        </div>
        <p>One row of B · 31 rows × 7 columns · rank 7</p>
        <p className={css.note}>
          Cross terms double gx·gy, gx·gz and gy·gz. Opposite gradients have the same quadratic
          form.
        </p>
      </div>
    </div>
  );
}
function SignalFit({ index }: { index: number }) {
  const values = input.probes[index].signal,
    x = (i: number) => 44 + (i / 30) * 328,
    y = (v: number) => 236 - (v / 1.15) * 202;
  const path = (v: number[]) => v.map((a, i) => `${i ? 'L' : 'M'}${x(i)},${y(a)}`).join(' ');
  return (
    <svg
      className={css.curve}
      viewBox="0 0 400 300"
      role="img"
      aria-label="Retained observations and fixed pixel OLS/WLS predictions"
    >
      {[0, 0.5, 1].map((v) => (
        <g key={v}>
          <path d={`M40 ${y(v)}H376`} stroke="#d9e1d5" />
          <text x="34" y={y(v) + 4} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      <path
        d={path(data.fixed_pixel_fits.ols.predicted_signal[index])}
        stroke={gray}
        fill="none"
        strokeWidth="2"
        strokeDasharray="5 3"
      />
      <path
        d={path(data.fixed_pixel_fits.wls.predicted_signal[index])}
        stroke={green}
        fill="none"
        strokeWidth="2"
      />
      {values.map((v, i) => (
        <rect key={i} x={x(i) - 2.5} y={y(v) - 2.5} width="5" height="5" fill="#182b26" />
      ))}
      {[0, 15, 30].map((i) => (
        <text key={i} x={x(i)} y="254" textAnchor="middle">
          {i}
        </text>
      ))}
      <text x="42" y="18">
        Signal (a.u.)
      </text>
      <text x="206" y="277" textAnchor="middle">
        Gradient volume index · 0 is b0
      </text>
    </svg>
  );
}
function Weights({ index }: { index: number }) {
  const values = data.wls_weights[index];
  return (
    <svg
      className={css.weights}
      viewBox="0 0 380 88"
      role="img"
      aria-label="Actual squared OLS-predicted signal weights"
    >
      <text x="1" y="16">
        WLS weights = ŜOLS²
      </text>
      <text x="365" y="16" textAnchor="end">
        0–1.1 a.u.²
      </text>
      {values.map((v, i) => (
        <rect
          key={i}
          x={14 + i * 11}
          y={70 - (v / 1.1) * 44}
          width="7"
          height={(v / 1.1) * 44}
          fill={green}
        />
      ))}
      <text x="12" y="85">
        0
      </text>
      <text x="344" y="85">
        30
      </text>
    </svg>
  );
}
function TensorGlyph({ tensor }: { tensor: DtiTensor }) {
  const bound = Math.ceil(tensor.eigenvalues[0] * 1000 * 2) / 2,
    scale = 45 / bound;
  return (
    <div>
      <svg
        className={css.glyph}
        viewBox="0 0 420 175"
        role="img"
        aria-label="Three orthographic eigenvalue-scaled tensor projections"
      >
        {tensor.projections.map((p, i) => {
          const cx = 70 + i * 140,
            cy = 82;
          return (
            <g key={i}>
              <path
                d={`M${cx - 52} ${cy}H${cx + 52}M${cx} ${cy - 52}V${cy + 52}`}
                stroke="#c2d0c5"
              />
              <path
                d={
                  p.points
                    .map(([x, y], j) => `${j ? 'L' : 'M'}${cx + x * scale},${cy - y * scale}`)
                    .join(' ') + 'Z'
                }
                stroke={green}
                fill="#d7e6df"
                strokeWidth="2"
              />
              <text x={cx + 54} y={cy + 5}>
                {axes[p.axes[0]]}
              </text>
              <text x={cx + 4} y={cy - 54}>
                {axes[p.axes[1]]}
              </text>
              <text x={cx} y="155" textAnchor="middle">
                {axes[p.axes[0]]}–{axes[p.axes[1]]}
              </text>
            </g>
          );
        })}
      </svg>
      <p className={css.unit}>Equal axes within all three views: ±{n(bound, 1)} ×10⁻³ mm²/s</p>
    </div>
  );
}
function Tensor({ index }: { index: number }) {
  const t = data.tensor_probes.wls[index],
    p = input.probes[index];
  return (
    <div className={css.two} data-dti-tensor={index}>
      <div className={css.card}>
        <h4>
          Saved WLS · pixel [{p.row}, {p.column}]
        </h4>
        <p>Symmetric D · values ×10⁻³ mm²/s</p>
        <div className={css.matrix}>
          {t.matrix.flat().map((v, i) => (
            <span key={i}>{n(v * 1000, 4)}</span>
          ))}
        </div>
        <p className={css.formula}>λ = [{t.eigenvalues.map((v) => n(v * 1000, 3)).join(', ')}]</p>
        <dl>
          <dt>FA · dimensionless</dt>
          <dd>{n(t.fa, 4)}</dd>
          <dt>MD · ×10⁻³ mm²/s</dt>
          <dd>{n(t.md * 1000, 4)}</dd>
        </dl>
      </div>
      <div>
        <TensorGlyph tensor={t} />
        <p className={css.formula}>MD = (λ₁ + λ₂ + λ₃) / 3</p>
        <p>FA measures the spread of eigenvalues relative to their magnitude.</p>
        <p className={css.note}>
          Axis lengths are proportional to eigenvalues. These glyphs are not tissue surfaces or
          fiber tracks.
        </p>
      </div>
    </div>
  );
}
const scoreRows = [
  { label: 'Saved OLS FA', scope: 'custom · 7,186 pixels', score: data.custom_scoring.ols },
  { label: 'Saved WLS FA', scope: 'custom · 7,186 pixels', score: data.custom_scoring.wls },
  { label: 'Saved WLS FA', scope: 'generic · 16,384 pixels', score: data.generic_scoring.wls_fa },
  {
    label: 'Truth FA; zero MD/tensor',
    scope: 'custom · FA only',
    score: data.custom_scoring.oracle_fa_with_zero_md_and_tensor,
  },
  {
    label: 'Correct MD oracle',
    scope: 'generic · compared with FA',
    score: data.generic_scoring.oracle_md,
  },
  {
    label: 'Correct tensor oracle',
    scope: 'generic · tensor reference',
    score: data.generic_scoring.oracle_tensor,
  },
];
function Scoring({ index }: { index: number }) {
  return (
    <div data-dti-score={index}>
      <table className={css.table}>
        <thead>
          <tr>
            <th>Retained output / control</th>
            <th>Comparison</th>
            <th>NCC</th>
            <th>NRMSE</th>
          </tr>
        </thead>
        <tbody>
          {scoreRows.map((r, i) => (
            <tr key={i} className={i === index ? css.active : ''}>
              <td>{r.label}</td>
              <td>{r.scope}</td>
              <td>{n(r.score.ncc, 6)}</td>
              <td>{n(r.score.nrmse, 6)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className={css.note}>
        The custom helper selects OLS first if both files exist. No published thresholds file: these
        values do not establish a current pass.
      </p>
      <p>Oracle and deliberately incomplete outputs are evaluator controls, not model runs.</p>
    </div>
  );
}
function Limits({ index }: { index: number }) {
  return (
    <div data-dti-limit={index}>
      {index === 0 && (
        <>
          <h4>Every assistance level exposes truth and the mask</h4>
          <div className={css.three}>
            {Object.entries(data.staging).map(([level, files]) => (
              <div className={css.card} key={level}>
                <h4>{level}</h4>
                <p>README + requirements</p>
                <p>
                  <strong>raw data + metadata + full truth</strong>
                </p>
                <p>
                  {files.includes('plan/design.md')
                    ? 'Approach and design supplied'
                    : files.includes('plan/approach.md')
                      ? 'Approach supplied'
                      : 'No plan supplied'}
                </p>
              </div>
            ))}
          </div>
          <p className={css.note}>
            Source and evaluation folders are absent from the seeded workspace. The truth mask
            removes a background-selection step.
          </p>
        </>
      )}
      {index === 1 && (
        <>
          <h4>Stored tensor axes disagree with declared directions</h4>
          <table className={css.table}>
            <thead>
              <tr>
                <th>Source region label</th>
                <th>Declared axis</th>
                <th>Stored principal axis</th>
                <th>Pixels</th>
              </tr>
            </thead>
            <tbody>
              {data.orientation_controls.map((r) => (
                <tr key={r.source_label}>
                  <td>{r.source_label}</td>
                  <td>{axes[r.declared_direction.indexOf(1)]}</td>
                  <td>
                    {r.principal_axis_unique && r.actual_principal_axis_absolute
                      ? axes[r.actual_principal_axis_absolute.indexOf(1)]
                      : 'not unique'}
                  </td>
                  <td>{r.matching_voxels}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className={css.note}>
            The rotation maps z to the declared axis; the largest eigenvalue uses its first column.
            The views retain the stored tensor values.
          </p>
        </>
      )}
      {index === 2 && (
        <>
          <h4>Check a notebook label against its actual pixel</h4>
          <table className={css.table}>
            <thead>
              <tr>
                <th>Notebook label</th>
                <th>[row, column]</th>
                <th>In mask?</th>
                <th>Truth FA</th>
              </tr>
            </thead>
            <tbody>
              {data.notebook_probe_check.map((p) => (
                <tr key={p.source_label}>
                  <td>{p.source_label}</td>
                  <td>
                    [{p.row}, {p.column}]
                  </td>
                  <td>{p.in_tissue_mask ? 'yes' : 'no'}</td>
                  <td>{n(p.fa, 6)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className={css.note}>
            The first two points contain the same tensor. The third point is background. Our five
            probes are selected from verified arrays.
          </p>
        </>
      )}
      {index === 3 && (
        <div className={css.card}>
          <h4>A missing file blocks the fallback scorer</h4>
          <p>
            Without a local filesystem workspace, the source branch requires NPY truth. This release
            supplies NPZ truth.
          </p>
          <p className={css.formula}>
            <code>{data.fallback.result.error}</code>
          </p>
          <p>
            Branch control: {data.fallback.runner_commands_executed} runner commands executed. No
            container launched.
          </p>
          <p className={css.note}>
            No fresh full-image fit, agent result or clinical validation. Notebook thresholds remain
            historical.
          </p>
        </div>
      )}
    </div>
  );
}
export function DtiScene({ state }: { state: DtiState }) {
  const index = dtiIndex(state, 5),
    p = input.probes[index],
    scalar = dtiScalar(state);
  return (
    <section className={css.scene} data-dti-scene={state.scene}>
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'inputs' && (
        <div className={css.two}>
          <Plane
            image={input.signals[dtiIndex(state, 4)].image}
            label={`Source volume ${input.signals[dtiIndex(state, 4)].volume} · b=${input.signals[dtiIndex(state, 4)].bvalue}`}
          />
          <div className={css.card}>
            <h4>Supplied truth mask</h4>
            <div className={css.maskSummary}>
              <Plane image={input.mask} label="Included pixels" small />
              <div>
                <p>
                  <strong>7,186 / 16,384</strong> pixels
                </p>
                <p>31 volumes per pixel</p>
                <p>1.71875 mm pixels</p>
                <p>220 mm field of view</p>
              </div>
            </div>
            <p className={css.note}>
              Synthetic phantom. All L1–L3 receive this mask and full truth. No patient anatomy is
              inferred.
            </p>
          </div>
        </div>
      )}
      {state.scene === 'gradients' && <Gradients index={dtiIndex(state, 31)} />}
      {state.scene === 'fit' && (
        <div className={css.two} data-dti-probe={index}>
          <div>
            <SignalFit index={index} />
            <p className={css.lineLegend}>
              <span>■ observed</span>
              <span>┄ OLS</span>
              <strong>━ WLS</strong>
            </p>
            <p>Fixed controls; lines connect gradient indices, not time.</p>
          </div>
          <div className={css.card}>
            <div className={css.maskSummary}>
              <Plane
                image={input.signals[0].image}
                label="b0 location"
                pixel={[p.row, p.column]}
                small
              />
              <div>
                <h4>
                  Pixel [{p.row}, {p.column}]
                </h4>
                <p>Control {index + 1} of 5</p>
                <p>31 retained signals</p>
                <p>S₀ fitted: {n(data.fixed_pixel_fits.wls.fitted_s0[index], 4)}</p>
              </div>
            </div>
            <Weights index={index} />
            <p className={css.note}>
              Post-hoc selection, one per truth tensor type. No new full-image fitting.
            </p>
          </div>
        </div>
      )}
      {state.scene === 'tensor' && <Tensor index={index} />}
      {state.scene === 'output' && (
        <>
          <div className={css.two}>
            {(['ols', 'wls'] as const).map((m) => (
              <Plane
                key={m}
                image={data.maps[scalar][m]}
                label={`Saved ${m.toUpperCase()} · ${scalar.toUpperCase()}`}
              />
            ))}
          </div>
          <p className={css.note}>
            Saved outputs, shared scales. Pale background is excluded by the supplied truth mask.
          </p>
        </>
      )}
      {state.scene === 'reference' &&
        (dtiReveal(state) ? (
          <div data-dti-reference="maps">
            <div className={css.three}>
              <Plane image={ref.maps[scalar]} label={`Truth ${scalar.toUpperCase()}`} reference />
              <Plane image={data.maps[scalar].wls} label={`Saved WLS ${scalar.toUpperCase()}`} />
              <Plane image={ref.errors[scalar].wls} label="Absolute error · full range" reference />
            </div>
            <p className={css.note}>
              Simulated reference · 7,186 tissue pixels. Truth and mask are solver-visible at all
              levels.
            </p>
          </div>
        ) : (
          <div className={css.hidden}>
            <h4>Reference remains hidden</h4>
            <p>Play this chapter to reveal truth and error halfway through.</p>
            <p>This is a reading boundary. The solver already receives the truth archive.</p>
          </div>
        ))}
      {state.scene === 'scoring' && <Scoring index={dtiIndex(state, 6)} />}
      {state.scene === 'limits' && <Limits index={dtiIndex(state, 4)} />}
    </section>
  );
}
export function DtiOutput({ state }: { state: DtiState }) {
  const text: Record<DtiState['scene'], string> = {
    inputs:
      'Native signal arrays, gradients and a supplied truth mask define this synthetic condition.',
    gradients:
      'Each row links direction and b-value to six symmetric tensor components plus baseline intensity.',
    fit: 'Fixed pixel controls closely reproduce saved values. The complete image is not refit here.',
    tensor:
      'Three projections describe one saved tensor. Source axes do not imply anatomical orientation.',
    output:
      'FA summarizes anisotropy; MD summarizes magnitude. Both discard some tensor information.',
    reference: dtiReveal(state)
      ? 'Truth and full-range errors are now visible. Actual task staging also exposes truth.'
      : 'The reader reference opens after the chapter midpoint and resets to hidden.',
    scoring:
      'Native masked FA scoring and generic full-grid scoring have different scope and reference selection.',
    limits:
      'One synthetic phantom, original labels and retained numerical controls. No agent or clinical result.',
  };
  return (
    <aside className={css.aside} data-dti-output>
      <b>READOUT</b>
      <h4>{titles[state.scene]}</h4>
      <p>{text[state.scene]}</p>
      <small>Pinned Imaging101 DTI source</small>
    </aside>
  );
}

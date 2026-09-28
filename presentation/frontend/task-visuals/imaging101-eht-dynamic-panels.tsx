import {
  dynamicInput as input,
  dynamicData as data,
  dynamicReference as ref,
  dynamicIndex,
  dynamicReveal,
  dynamicReferenceIndex,
  dynamicControlNames,
  type DynamicImage,
  type EhtDynamicState,
} from './imaging101-eht-dynamic';
import css from './imaging101-eht-dynamic.module.css';
const green = '#264b43',
  orange = '#b9521e',
  purple = '#8052a1';
const n = (v: number, d = 3) => v.toFixed(d);
const titles = {
  inputs: 'Changing coverage gives a different snapshot',
  operator: 'Each complex sample mixes 900 brightness values',
  temporal: 'A temporal model shares information between frames',
  output: 'Compare the two retained reconstruction videos',
  reference: 'Reveal the supplied synthetic reference',
  diagnostics: 'Image similarity and recovered motion can differ',
  scoring: 'Oracle controls expose what image scores miss',
  limits: 'Keep source, access and evidence limits explicit',
};
function Plane({
  image,
  label,
  reference = false,
}: {
  image: DynamicImage;
  label: string;
  reference?: boolean;
}) {
  return (
    <figure className={css.plane} data-dynamic-panel={reference ? 'reference' : 'source'}>
      <figcaption>{label}</figcaption>
      <svg viewBox="0 0 245 238" role="img" aria-label={label}>
        <image
          href={image.data}
          x="38"
          y="8"
          width="185"
          height="185"
          preserveAspectRatio="none"
          style={{ imageRendering: 'pixelated' }}
        />
        <rect
          x="38"
          y="8"
          width="185"
          height="185"
          fill="none"
          stroke={reference ? purple : green}
          strokeDasharray={reference ? '5 3' : undefined}
        />
        {[0, 15, 29].map((v) => (
          <g key={v}>
            <text x={38 + ((v + 0.5) / 30) * 185} y="210" textAnchor="middle">
              {v}
            </text>
            <text x="31" y={12 + ((29.5 - v) / 30) * 185} textAnchor="end">
              {v}
            </text>
          </g>
        ))}
        <text x="133" y="232" textAnchor="middle">
          Array column →
        </text>
        <text transform="translate(11 100) rotate(-90)" textAnchor="middle">
          Array row ↑
        </text>
      </svg>
      <div className={css.scale}>
        <span>{n(image.range[0], image.range[0] === -1 ? 0 : 3)}</span>
        <i className={css[image.palette]} />
        <span>{n(image.range[1], image.range[1] === 1 ? 0 : 3)}</span>
      </div>
      <p className={css.unit}>{image.unit} · native 30×30 grid</p>
    </figure>
  );
}
function Coverage({ time }: { time: number }) {
  const points = input.frames[time].uv_Glambda;
  return (
    <svg
      className={css.chart}
      viewBox="0 0 300 280"
      role="img"
      aria-label="28 native Fourier points at the selected epoch"
    >
      {[-10, 0, 10].map((v) => (
        <g key={v}>
          <path d={`M43 ${132 - v * 10}H263M${153 + v * 10} 32V232`} stroke="#dbe0d4" />
          <text x={153 + v * 10} y="251" textAnchor="middle">
            {v}
          </text>
          <text x="35" y={136 - v * 10} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      {points.map(([u, v], i) => (
        <circle key={i} cx={153 + u * 10} cy={132 - v * 10} r="3.5" fill={green}>
          <title>Baseline {i}</title>
        </circle>
      ))}
      <text x="152" y="273" textAnchor="middle">
        u (G wavelengths)
      </text>
      <text transform="translate(12 133) rotate(-90)" textAnchor="middle">
        v (G wavelengths)
      </text>
    </svg>
  );
}
function Visibilities({ time }: { time: number }) {
  const f = input.frames[time],
    x = (i: number) => 45 + (i / 27) * 265,
    y = (v: number) => 225 - ((v + 0.7) / 3) * 190;
  return (
    <svg
      className={css.chart}
      viewBox="0 0 340 280"
      role="img"
      aria-label="Complex visibility components, with generator component-noise bars"
    >
      {[-0.5, 0, 1, 2].map((v) => (
        <g key={v}>
          <path d={`M45 ${y(v)}H310`} stroke="#dbe0d4" />
          <text x="37" y={y(v) + 4} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      {[0, 9, 18, 27].map((v) => (
        <text key={v} x={x(v)} y="251" textAnchor="middle">
          {v}
        </text>
      ))}
      {[f.vis_real_Jy, f.vis_imaginary_Jy].map((values, k) =>
        values.map((v, i) => {
          const xx = x(i) + (k ? 1.6 : -1.6),
            e = f.sigma_complex_RMS_Jy[i] / Math.SQRT2,
            col = k ? orange : green;
          return (
            <g key={`${k}-${i}`}>
              <path d={`M${xx} ${y(v - e)}V${y(v + e)}`} stroke={col} />
              {k ? (
                <rect x={xx - 2} y={y(v) - 2} width="4" height="4" fill={col} />
              ) : (
                <circle cx={xx} cy={y(v)} r="2.2" fill={col} />
              )}
            </g>
          );
        }),
      )}
      <text x="179" y="273" textAnchor="middle">
        Stored baseline index
      </text>
      <text transform="translate(11 131) rotate(-90)" textAnchor="middle">
        Visibility (Jy)
      </text>
    </svg>
  );
}
function Epoch({ time }: { time: number }) {
  return (
    <div
      className={css.epochs}
      aria-label={`Native epoch ${time + 1} of 12`}
      data-dynamic-epoch={time}
    >
      {input.times_hours.map((t, i) => (
        <span key={i} className={i === time ? css.selected : undefined}>
          {n(t, 1)}
        </span>
      ))}
      <small>Native time (hours)</small>
    </div>
  );
}
function Temporal({ progress }: { progress: number }) {
  const phase = Math.min(7, Math.floor(progress * 8)),
    back = phase >= 4,
    k = back ? 7 - phase : phase;
  return (
    <div className={css.temporal}>
      <h4>{back ? 'Backward information pass' : 'Forward information pass'} · schematic</h4>
      <svg
        className={css.network}
        viewBox="0 0 480 185"
        role="img"
        aria-label="Conceptual forward and backward messages between five illustrated time nodes"
      >
        {[0, 1, 2, 3].map((i) => (
          <g key={i}>
            <path
              d={`M${64 + i * 91} 49H${100 + i * 91}l-6 -4m6 4l-6 4`}
              fill="none"
              stroke={i === k && !back ? orange : '#9bad9f'}
              strokeWidth={i === k && !back ? 4 : 2}
            />
            <path
              d={`M${100 + i * 91} 104H${64 + i * 91}l6 -4m-6 4l6 4`}
              fill="none"
              stroke={i === k && back ? orange : '#9bad9f'}
              strokeWidth={i === k && back ? 4 : 2}
            />
          </g>
        ))}
        {[0, 1, 2, 3, 4].map((i) => (
          <g key={i}>
            <rect
              x={21 + i * 91}
              y="57"
              width="61"
              height="37"
              rx="4"
              fill="#e6eee3"
              stroke={green}
            />
            <text x={51 + i * 91} y="81" textAnchor="middle">
              {['x₀', 'x₁', '…', 'x₁₀', 'x₁₁'][i]}
            </text>
            <path d={`M${51 + i * 91} 144V99l-4 6m4 -6l4 6`} fill="none" stroke={green} />
            <text x={51 + i * 91} y="163" textAnchor="middle">
              y{['₀', '₁', '…', '₁₀', '₁₁'][i]}
            </text>
          </g>
        ))}
      </svg>
      <div className={css.formula}>
        xₜ = W(θ)xₜ₋₁ + wₜ
        <br />
        yₜ = Fₜxₜ + nₜ
      </div>
      <p>
        Each image uses neighboring observations. EM alternates image statistics and warp updates.
      </p>
      <p className={css.unit}>
        Highlight motion explains message direction; no EM states are replayed.
      </p>
    </div>
  );
}
function Curve({ kind, time }: { kind: 'angle' | 'flux'; time: number }) {
  const series = [data.diagnostics.starwarps, data.diagnostics.static_per_frame, ref.diagnostics];
  const bounds = kind === 'angle' ? [210, 320] : [1.9, 3.1],
    ticks = kind === 'angle' ? [220, 260, 300] : [2, 2.5, 3];
  const x = (i: number) => 48 + (i / 11) * 260,
    y = (v: number) => 222 - ((v - bounds[0]) / (bounds[1] - bounds[0])) * 195;
  return (
    <svg
      className={css.chart}
      viewBox="0 0 340 280"
      role="img"
      aria-label={
        kind === 'angle'
          ? 'Descriptive array brightness direction at all twelve epochs'
          : 'Per-frame brightness sum in Jy'
      }
    >
      {ticks.map((v) => (
        <g key={v}>
          <path d={`M48 ${y(v)}H308`} stroke="#dbe0d4" />
          <text x="41" y={y(v) + 4} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      <path d={`M${x(time)} 27V222`} stroke="#b4bfb3" strokeDasharray="2 3" />
      {series.map((d, k) => {
        const values = kind === 'angle' ? d.array_polar_moment_angle_deg : d.flux_Jy,
          col = [green, orange, purple][k];
        return (
          <g key={k}>
            <path
              d={values.map((v, i) => `${i ? 'L' : 'M'}${x(i)} ${y(v)}`).join('')}
              fill="none"
              stroke={col}
              strokeWidth="2"
              strokeDasharray={k === 2 ? '5 3' : undefined}
            />
            {values.map((v, i) => (
              <circle key={i} cx={x(i)} cy={y(v)} r={i === time ? 4 : 2} fill={col} />
            ))}
          </g>
        );
      })}
      {[0, 5, 11].map((i) => (
        <text key={i} x={x(i)} y="250" textAnchor="middle">
          {n(input.times_hours[i], 1)}
        </text>
      ))}
      <text x="178" y="273" textAnchor="middle">
        Native time (hours)
      </text>
      <text transform="translate(12 132) rotate(-90)" textAnchor="middle">
        {kind === 'angle' ? 'Array brightness direction (°)' : 'Flux (Jy)'}
      </text>
    </svg>
  );
}
const limits = [
  [
    'Source reproducibility',
    'Pinned main.py has a merged-import syntax error. Saved arrays remain historical outputs; no fresh EM execution is established.',
  ],
  [
    'Reference access',
    'All L1–L3 copy ground_truth.npz. L2 adds approach; L3 adds design. Reader reveals are not private evaluation boundaries.',
  ],
  [
    'Noise and warp conventions',
    'The helper uses twice the generator’s nominal real/imaginary noise variance. Current source defaults to four affine parameters, without translation.',
  ],
  [
    'Scope of the example',
    'One synthetic crescent; all station pairs are retained. No real black-hole movie, general superiority or calibrated motion estimate is established.',
  ],
];
export function EhtDynamicScene({ state }: { state: EhtDynamicState }) {
  const i = dynamicIndex(state),
    time = input.times_hours[i],
    reveal = dynamicReveal(state),
    j = dynamicReferenceIndex(state),
    kernel = input.kernels[dynamicIndex(state, 4)],
    control = ref.controls[dynamicIndex(state, 4)];
  return (
    <section
      className={css.scene}
      data-dynamic-scene={state.scene}
      data-dynamic-selection={state.scene === 'reference' ? j : i}
    >
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'inputs' && (
        <>
          <div className={css.two}>
            <div>
              <h4>28 native baselines · t={n(time, 2)} h</h4>
              <Coverage time={i} />
            </div>
            <div>
              <h4>Real ● green · imaginary ■ orange</h4>
              <Visibilities time={i} />
            </div>
          </div>
          <Epoch time={i} />
          <p className={css.unit}>
            8 stations · 336 complex samples total · bars: generator σ/√2 · overlapping points are
            retained.
          </p>
        </>
      )}
      {state.scene === 'operator' && (
        <>
          <div className={css.three}>
            <Plane image={kernel.real} label="Real Fourier weights" />
            <Plane image={kernel.imaginary} label="Imaginary Fourier weights" />
            <div className={css.card}>
              <h4>Epoch 0 · baseline {kernel.baseline}</h4>
              <p>{kernel.station_pair.map((k) => input.station_names[k]).join(' ↔ ')}</p>
              <p>
                u={n(kernel.uv_Glambda[0])}, v={n(kernel.uv_Glambda[1])} Gλ
              </p>
              <div className={css.formula}>Vⱼ = Σₚ xₚ exp[−2πi(uⱼlₚ + vⱼmₚ)]</div>
              <p>
                <strong>
                  56 real constraints
                  <br />
                  900 image values
                </strong>
              </p>
              <p>These are measurement weights, not reconstructed images.</p>
            </div>
          </div>
          <p className={css.unit}>
            Fixed rows 0, 8, 16, 27 · dimensionless signed scale · each sample sums over the full
            native grid.
          </p>
        </>
      )}
      {state.scene === 'temporal' && (
        <div className={css.two}>
          <div>
            <Plane image={input.prior} label="Source-formula prior · 2 Jy" />
            <p className={css.unit}>50 μas FWHM · power 6 · 5% floor</p>
          </div>
          <Temporal progress={state.view} />
        </div>
      )}
      {state.scene === 'output' && (
        <>
          <div className={css.three}>
            <Plane image={data.videos.static[i]} label={`Saved static · t=${n(time, 2)} h`} />
            <Plane image={data.videos.starwarps[i]} label={`Saved StarWarps · t=${n(time, 2)} h`} />
            <div className={css.card}>
              <h4>Original frame {i + 1}/12</h4>
              <p>Common brightness scale: 0–0.075 Jy/pixel.</p>
              <table className={css.table}>
                <thead>
                  <tr>
                    <th>Frame</th>
                    <th>Static</th>
                    <th>SW</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Flux (Jy)</td>
                    <td>{n(data.diagnostics.static_per_frame.flux_Jy[i])}</td>
                    <td>{n(data.diagnostics.starwarps.flux_Jy[i])}</td>
                  </tr>
                  <tr>
                    <td>NCC</td>
                    <td>{n(data.metrics.static_per_frame.per_frame[i].ncc)}</td>
                    <td>{n(data.metrics.starwarps.per_frame[i].ncc)}</td>
                  </tr>
                  <tr>
                    <td>NRMSE</td>
                    <td>{n(data.metrics.static_per_frame.per_frame[i].nrmse)}</td>
                    <td>{n(data.metrics.starwarps.per_frame[i].nrmse)}</td>
                  </tr>
                </tbody>
              </table>
              <p className={css.unit}>
                Native metrics replay against supplied truth. No optimizer runs here.
              </p>
            </div>
          </div>
          <Epoch time={i} />
        </>
      )}
      {state.scene === 'reference' && !reveal && (
        <div className={css.hidden}>
          <h4>Reference remains hidden</h4>
          <p>
            At this chapter’s midpoint, reveal the synthetic truth and saved StarWarps error for all
            twelve epochs.
          </p>
          <p>Actual L1–L3 expose the truth file. This controls reading order only.</p>
        </div>
      )}
      {state.scene === 'reference' && reveal && (
        <div data-dynamic-reference="true">
          <div className={css.three}>
            <Plane image={ref.truth[j]} label="Supplied synthetic truth" reference />
            <Plane image={data.videos.starwarps[j]} label="Saved StarWarps" />
            <Plane image={ref.error[j]} label="Absolute error vs truth" reference />
          </div>
          <Epoch time={j} />
          <p className={css.unit}>
            t={n(input.times_hours[j], 2)} h · brightness shares one scale; error uses 0–0.031
            Jy/pixel · no crops.
          </p>
        </div>
      )}
      {state.scene === 'diagnostics' && reveal && (
        <div data-dynamic-reference="true">
          <div className={css.two}>
            <div>
              <h4>Brightness direction · array coordinates</h4>
              <Curve kind="angle" time={i} />
            </div>
            <div>
              <h4>Flux · reference is 2 Jy per frame</h4>
              <Curve kind="flux" time={i} />
            </div>
          </div>
          <p className={css.unit}>
            Green: StarWarps · orange: static · purple dashed: truth. Dots are native epochs;
            joining lines guide reading.
          </p>
          <p className={css.note}>
            Net direction change: SW 57.88° · static 88.61° · truth 90°. This diagnostic is not a
            fitted warp or sky position angle.
          </p>
        </div>
      )}
      {state.scene === 'scoring' && reveal && (
        <div data-dynamic-reference="true">
          <div className={css.three}>
            <Plane
              image={control.first}
              label={`${dynamicControlNames[dynamicIndex(state, 4)]} · first`}
              reference
            />
            <Plane image={control.last} label="Same control · last epoch" reference />
            <div>
              <h4>All 12 frames scored</h4>
              <table className={css.table}>
                <thead>
                  <tr>
                    <th>Control</th>
                    <th>NCC ↑</th>
                    <th>NRMSE ↓</th>
                  </tr>
                </thead>
                <tbody>
                  {ref.controls.map((c, k) => (
                    <tr key={c.id} className={control.id === c.id ? css.active : undefined}>
                      <td>{dynamicControlNames[k]}</td>
                      <td>{n(c.native.ncc, 4)}</td>
                      <td>{n(c.native.nrmse, 4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className={css.unit}>Native mean framewise metrics. Oracle rows use the answer.</p>
            </div>
          </div>
          <p className={css.note}>
            Selected direction change: {n(control.direction_change_deg, 2)}°. High similarity alone
            does not establish correct temporal change.
          </p>
        </div>
      )}
      {state.scene === 'limits' && (
        <div className={css.two}>
          {limits.map(([title, body], k) => (
            <div
              key={title}
              className={`${css.card} ${dynamicIndex(state, 4) === k ? css.active : ''}`}
            >
              <h4>{title}</h4>
              <p>{body}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
export function EhtDynamicOutput({ state }: { state: EhtDynamicState }) {
  const copy = {
    inputs: [
      'Input, not a photograph',
      '12 epochs over 6 hours. Each telescope pair samples one Fourier coordinate. Both coverage and brightness change.',
      'Time here is the source’s epoch, not animation time.',
    ],
    operator: [
      'An underdetermined image',
      'Even with 28 complex samples, one frame has 900 unknown brightness values. Priors supply additional assumptions.',
      'Kernel colors encode signed weights; no reference is required.',
    ],
    temporal: [
      'State-space assumption',
      'A four-parameter affine warp couples neighboring frames. Process covariance is 10⁻⁷ times identity; the source adds interior priors.',
      'The diagram illustrates the source procedure, not retained inference states.',
    ],
    output: [
      'Saved output comparison',
      'Native mean NCC: static 0.8507; StarWarps 0.8817. Mean NRMSE: 0.0710 versus 0.0638.',
      'A better image score on this sequence is not general superiority.',
    ],
    reference: [
      'Reference and error',
      dynamicReveal(state)
        ? 'Truth is a synthetic rotating crescent, 2 Jy in every frame. Error is the absolute difference from the saved StarWarps image.'
        : 'The reference appears halfway through this chapter. It is separate from the image prior and recorded outputs.',
      'Purple dashed borders identify reference-derived views.',
    ],
    diagnostics: [
      'Smoothness is not full motion recovery',
      'Adjacent-difference error ratio: StarWarps 0.819; static 2.681. Lower is better for this supplemental diagnostic.',
      'Denominator: norm of the truth’s 11 frame differences. No official temporal score is supplied.',
    ],
    scoring: [
      'Three scoring definitions',
      'StarWarps: native mean 0.881699 / 0.063803; flattened recipe 0.880961 / 0.063114; local generic 0.882934 / 0.063114.',
      'NCC / NRMSE. Generic NCC is cosine; native NCC is centered. No pass thresholds.',
    ],
    limits: [
      'What this review establishes',
      'Pinned arrays, fixed numerical checks and saved-score replay. The older runner fallback requires 2D; no Docker equivalence is proven.',
      'No simulation, fresh EM reconstruction or agent trial.',
    ],
  }[state.scene];
  return (
    <aside className={css.aside} data-dynamic-output={state.scene}>
      <b>{copy[0]}</b>
      <h4>Read the condition</h4>
      <p>{copy[1]}</p>
      <small>{copy[2]}</small>
    </aside>
  );
}

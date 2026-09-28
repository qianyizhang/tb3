import {
  featuresInput as input,
  featuresData as data,
  featuresReference as ref,
  featuresIndex,
  featuresReveal,
  featuresReferenceIndex,
  type FeaturesImage,
  type EhtFeaturesState,
} from './imaging101-eht-features-dynamic';
import css from './imaging101-eht-features-dynamic.module.css';
const green = '#264b43',
  orange = '#b9521e',
  purple = '#8052a1';
const n = (v: number, d = 2) => v.toFixed(d);
const titles = {
  inputs: 'Ten snapshots, each with sparse Fourier measurements',
  closures: 'Station gains cancel in closure quantities',
  model: 'Four parameters describe an entire crescent',
  posterior: 'Inspect weighted distributions, not just sample counts',
  reference: 'Reveal the supplied synthetic truth',
  diagnostics: 'Weighted spread and actual error can disagree',
  scoring: 'Image scores do not certify parameter uncertainty',
  limits: 'Keep the source and evaluation limits visible',
};
function Plane({
  image,
  label,
  reference = false,
}: {
  image: FeaturesImage;
  label: string;
  reference?: boolean;
}) {
  return (
    <figure className={css.plane} data-features-panel={reference ? 'reference' : 'source'}>
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
        {[0, 32, 63].map((v) => (
          <g key={v}>
            <text x={38 + ((v + 0.5) / 64) * 185} y="210" textAnchor="middle">
              {v}
            </text>
            <text x="31" y={12 + ((v + 0.5) / 64) * 185} textAnchor="end">
              {v}
            </text>
          </g>
        ))}
        <text x="133" y="232" textAnchor="middle">
          Array column →
        </text>
        <text transform="translate(11 100) rotate(-90)" textAnchor="middle">
          Array row ↓
        </text>
      </svg>
      <div className={css.scale}>
        <span>0</span>
        <i className={css[image.palette]} />
        <span>{n(image.range[1], 5)}</span>
      </div>
      <p className={css.unit}>Fraction of total flux / pixel · 64×64</p>
    </figure>
  );
}
function Epoch({ time }: { time: number }) {
  return (
    <div
      className={css.epochs}
      data-features-epoch={time}
      aria-label={`Native epoch ${time + 1} of 10`}
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
function Coverage({ time }: { time: number }) {
  return (
    <svg
      className={css.chart}
      viewBox="0 0 300 280"
      role="img"
      aria-label="28 stored Fourier coordinates"
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
      {input.frames[time].uv_Glambda.map(([u, v], i) => (
        <circle key={i} cx={153 + u * 10} cy={132 - v * 10} r="3.5" fill={green}>
          <title>Stored baseline {i}</title>
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
    y = (v: number) => 225 - (v + 0.25) * 200;
  return (
    <svg
      className={css.chart}
      viewBox="0 0 340 280"
      role="img"
      aria-label="Measured real and imaginary components in Jy"
    >
      {[-0.2, 0, 0.3, 0.6].map((v) => (
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
        values.map((v, i) =>
          k ? (
            <rect key={`${k}-${i}`} x={x(i) - 2} y={y(v) - 2} width="4" height="4" fill={orange} />
          ) : (
            <circle key={`${k}-${i}`} cx={x(i)} cy={y(v)} r="2.5" fill={green} />
          ),
        ),
      )}
      <text x="179" y="273" textAnchor="middle">
        Stored baseline index
      </text>
      <text transform="translate(11 131) rotate(-90)" textAnchor="middle">
        Complex visibility (Jy)
      </text>
    </svg>
  );
}
function Closure({ choice }: { choice: number }) {
  const c = input.closure_controls[choice],
    phase = c.kind === 'phase';
  const points = phase
    ? [
        [60, 210],
        [180, 45],
        [300, 210],
      ]
    : [
        [60, 60],
        [300, 60],
        [60, 215],
        [300, 215],
      ];
  const nodeIndex = (station: number) => c.stations.indexOf(station);
  return (
    <div data-features-choice={choice}>
      <div className={css.two}>
        <div>
          <h4>
            {phase ? 'Triangle phase sum' : 'Four-station log ratio'} · t=
            {n(input.times_hours[c.epoch], 1)} h
          </h4>
          <svg
            className={css.chart}
            viewBox="0 0 360 280"
            role="img"
            aria-label="Selected station relationships; schematic positions"
          >
            {c.pairs.map(([a, b], i) => {
              const p = points[nodeIndex(a)],
                q = points[nodeIndex(b)];
              return (
                <g key={i}>
                  <path
                    d={`M${p[0]} ${p[1]}L${q[0]} ${q[1]}`}
                    stroke={c.signs[i] > 0 ? green : orange}
                    strokeWidth="3"
                  />
                  <rect
                    x={(p[0] + q[0]) / 2 - 28}
                    y={(p[1] + q[1]) / 2 - 13}
                    width="56"
                    height="24"
                    fill="#f6f7ef"
                  />
                  <text x={(p[0] + q[0]) / 2} y={(p[1] + q[1]) / 2 + 4} textAnchor="middle">
                    {c.signs[i] > 0 ? '+' : '−'} V{a}
                    {b}
                  </text>
                </g>
              );
            })}
            {points.map(([x, y], i) => (
              <g key={i}>
                <circle cx={x} cy={y} r="8" fill={green} />
                <text x={x} y={y + (phase && i === 1 ? -20 : 28)} textAnchor="middle">
                  {input.station_names[c.stations[i]]}
                </text>
              </g>
            ))}
          </svg>
          <p className={css.unit}>Station positions are schematic. Green adds; orange subtracts.</p>
        </div>
        <div className={css.card}>
          <h4>Fixed gain-cancellation control</h4>
          <table className={css.table}>
            <thead>
              <tr>
                <th>{phase ? 'Phase (°)' : 'Amplitude (Jy)'}</th>
                <th>Stored</th>
                <th>With gains</th>
              </tr>
            </thead>
            <tbody>
              {c.pairs.map(([a, b], i) => (
                <tr key={i}>
                  <td>
                    V{a}
                    {b}
                  </td>
                  <td>{n(c.before[i], phase ? 1 : 3)}</td>
                  <td>{n(c.after[i], phase ? 1 : 3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className={css.formula}>
            {phase ? 'Wrap(φₐᵦ + φᵦ𝚌 − φₐ𝚌)' : 'ln|Vₐᵦ| + ln|V𝚌𝚍| − ln|Vₐ𝚌| − ln|Vᵦ𝚍|'}
          </p>
          <p>
            <strong>
              {n(c.combined_before, 3)} → {n(c.combined_after, 3)}
            </strong>{' '}
            {phase ? 'degrees' : 'log amplitude'}
          </p>
          <p className={css.unit}>Only station gains change; no new observations or noise draws.</p>
        </div>
      </div>
    </div>
  );
}
function Model({ choice }: { choice: number }) {
  const c = input.model_controls[choice];
  return (
    <div data-features-choice={choice}>
      <div className={css.three}>
        {c.images.map((image, i) => (
          <Plane key={i} image={image} label={`${c.label}: ${c.values[i]} ${c.unit}`} />
        ))}
        <div className={css.card}>
          <h4>One independent fit per time</h4>
          <p className={css.formula}>
            Flow → 4 parameters
            <br />→ crescent → closures
          </p>
          <p>Compare predicted and observed closures; then importance-weight saved samples.</p>
          <p>No neighboring-frame prior.</p>
          <p className={css.unit}>
            Ranges: diameter 20–80 μas; width 1–40 μas; asymmetry 0–1; angle −181–181°.
          </p>
        </div>
      </div>
      <p className={css.note}>
        Fixed formula examples, not inferred images. Only the named parameter changes; both panels
        use 0–0.0045.
      </p>
    </div>
  );
}
function Ridge({ parameter, truth = false }: { parameter: number; truth?: boolean }) {
  const h = data.histograms[parameter],
    x = (v: number) => 52 + ((v - h.range[0]) / (h.range[1] - h.range[0])) * 320,
    y = (i: number) => 274 - i * 24;
  return (
    <svg
      className={css.chart}
      viewBox="0 0 410 315"
      role="img"
      aria-label={`All ten weighted histograms of ${data.parameter_labels[parameter]}`}
    >
      {h.mass.map((mass, i) => {
        const peak = Math.max(...mass),
          p = mass.map((v, j) => `${x(h.centers[j])},${y(i) - (v / peak) * 18}`).join(' ');
        return (
          <g key={i}>
            <path d={`M52 ${y(i)}H372`} stroke="#dbe0d4" />
            <polygon
              points={`52,${y(i)} ${p} 372,${y(i)}`}
              fill="#b1c9bc"
              stroke={green}
              strokeWidth="1"
            />
            <text x="43" y={y(i) + 4} textAnchor="end">
              {n(input.times_hours[i], 1)}
            </text>
            {truth && (
              <path
                d={`M${x(ref.parameters[i][parameter])} ${y(i) + 1}V${y(i) - 20}`}
                stroke={purple}
                strokeDasharray="4 2"
                strokeWidth="2"
              />
            )}
          </g>
        );
      })}
      {[h.range[0], (h.range[0] + h.range[1]) / 2, h.range[1]].map((v) => (
        <text key={v} x={x(v)} y="294" textAnchor="middle">
          {n(v, parameter === 2 ? 2 : 1)}
        </text>
      ))}
      <text x="213" y="313" textAnchor="middle">
        {data.parameter_labels[parameter]} ({data.parameter_units[parameter]})
      </text>
      <text transform="translate(12 165) rotate(-90)" textAnchor="middle">
        Observation time (hours)
      </text>
    </svg>
  );
}
function EffectiveSamples() {
  return (
    <svg
      className={css.chart}
      viewBox="0 0 350 315"
      role="img"
      aria-label="Effective sample size for all ten snapshots"
    >
      {data.ess.map((ess, i) => {
        const y = 274 - i * 24;
        return (
          <g key={i}>
            <rect x="45" y={y - 15} width={(ess / 120) * 225} height="15" fill={green} />
            <text x="36" y={y - 2} textAnchor="end">
              {n(input.times_hours[i], 1)}
            </text>
            <text x={51 + (ess / 120) * 225} y={y - 2}>
              {n(ess, 1)}
            </text>
          </g>
        );
      })}
      {[0, 50, 100].map((v) => (
        <text key={v} x={45 + (v / 120) * 225} y="294" textAnchor="middle">
          {v}
        </text>
      ))}
      <text x="174" y="313" textAnchor="middle">
        ESS = 1 / Σw²
      </text>
    </svg>
  );
}
function Summary({ parameter }: { parameter: number }) {
  const values = data.means
    .map((m, i) => [
      m[parameter] - data.stds[i][parameter],
      m[parameter] + data.stds[i][parameter],
      ref.parameters[i][parameter],
    ])
    .flat();
  const low = Math.min(...values),
    high = Math.max(...values),
    pad = (high - low) * 0.1,
    lo = low - pad,
    hi = high + pad;
  const x = (i: number) => 55 + (i / 9) * 330,
    y = (v: number) => 238 - ((v - lo) / (hi - lo)) * 205;
  return (
    <svg
      className={css.chart}
      viewBox="0 0 420 285"
      role="img"
      aria-label="Saved weighted mean and one standard deviation with supplied truth"
    >
      {[0, 0.5, 1].map((t) => {
        const v = lo + t * (hi - lo);
        return (
          <g key={t}>
            <path d={`M55 ${y(v)}H385`} stroke="#dbe0d4" />
            <text x="46" y={y(v) + 4} textAnchor="end">
              {n(v, parameter === 2 ? 2 : 1)}
            </text>
          </g>
        );
      })}
      <polyline
        points={data.means.map((m, i) => `${x(i)},${y(m[parameter])}`).join(' ')}
        fill="none"
        stroke={green}
      />
      <polyline
        points={ref.parameters.map((m, i) => `${x(i)},${y(m[parameter])}`).join(' ')}
        fill="none"
        stroke={purple}
        strokeDasharray="5 3"
        strokeWidth="2"
      />
      {data.means.map((m, i) => (
        <g key={i}>
          <path
            d={`M${x(i)} ${y(m[parameter] - data.stds[i][parameter])}V${y(m[parameter] + data.stds[i][parameter])}`}
            stroke={green}
            strokeWidth="2"
          />
          <circle
            cx={x(i)}
            cy={y(m[parameter])}
            r={i === 4 ? 5 : 3}
            fill={i === 4 ? orange : green}
          />
        </g>
      ))}
      {[0, 3, 6, 9].map((i) => (
        <text key={i} x={x(i)} y="258" textAnchor="middle">
          {n(input.times_hours[i], 1)}
        </text>
      ))}
      <text x="219" y="280" textAnchor="middle">
        Observation time (hours)
      </text>
      <text transform="translate(13 135) rotate(-90)" textAnchor="middle">
        {data.parameter_units[parameter]}
      </text>
    </svg>
  );
}
function Scoring({ choice }: { choice: number }) {
  const titles = [
    'Native parameter error',
    'Generic image score',
    'Oracle collapsed posterior',
    'Angle-wrap counterexample',
  ];
  return (
    <div className={css.two} data-features-choice={choice}>
      <div>
        <table className={css.table}>
          <thead>
            <tr>
              <th>Readout</th>
              <th>Value / control</th>
            </tr>
          </thead>
          <tbody>
            {[
              [titles[0], '6.08° angle MAE'],
              [titles[1], 'NCC 0.996218'],
              [titles[2], '0 error; 0 spread'],
              [titles[3], 'Linear 0°; circular 180°'],
            ].map(([title, value], i) => (
              <tr key={title} className={choice === i ? css.active : undefined}>
                <td>{title}</td>
                <td>{value}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className={css.note}>
          The oracle uses supplied answers. It is a scoring counterexample, not a blind solution.
        </p>
      </div>
      <div className={css.card}>
        <h4>{titles[choice]}</h4>
        {choice === 0 && (
          <>
            <p>
              Mean absolute error compares one weighted angle estimate with truth at each epoch.
            </p>
            <p className={css.formula}>
              {n(ref.native.avg_abs_bias[3], 5)} degrees over 10 snapshots
            </p>
            <p>It does not test distribution calibration, tails or missing modes.</p>
          </>
        )}
        {choice === 1 && (
          <>
            <p>Generic dispatch compares the 10×64×64 mean-image stack with unit-flux truth.</p>
            <p className={css.formula}>
              NCC {n(ref.generic.ncc, 6)}
              <br />
              NRMSE {n(ref.generic.nrmse, 6)}
            </p>
            <p>Posterior sample arrays are rejected. No published pass thresholds.</p>
          </>
        )}
        {choice === 2 && (
          <>
            <p>A point placed exactly at each truth parameter has zero error and no uncertainty.</p>
            <svg
              className={css.network}
              viewBox="0 0 320 150"
              role="img"
              aria-label="Oracle point distribution at supplied truth"
            >
              <path d="M35 110H285" stroke={green} />
              <path d="M160 110V30" stroke={purple} strokeWidth="3" strokeDasharray="5 3" />
              <circle cx="160" cy="30" r="5" fill={purple} />
              <text x="160" y="135" textAnchor="middle">
                All weight at truth · schematic
              </text>
              <text x="170" y="55">
                Spread = 0
              </text>
            </svg>
            <p>Perfect point accuracy does not validate a posterior.</p>
          </>
        )}
        {choice === 3 && (
          <>
            <p>Fixed equal-weight angles: −179° and +179°. They are adjacent on a circle.</p>
            <p className={css.formula}>
              Source linear mean: 0°
              <br />
              Circular mean: 180°
            </p>
            <p>
              This seam is absent from the released samples; it does not explain their observed
              bias.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
const limits = [
  [
    'Answer access',
    'All L1–L3 expose ground_truth.npz and the extra meta_data file containing all 40 truth parameters.',
  ],
  [
    'Likelihood mismatch',
    'Source training weights likelihood 70× more than importance reweighting, relative to the same log-density term.',
  ],
  [
    'Output and units',
    'Saved images have unit flux; simulated observations use 0.6 Jy. Generic image scoring differs from native parameter scoring.',
  ],
  [
    'Evidence scope',
    'No checkpoints or latent densities for corrected weights. No new training, blind pass or uncertainty calibration claim.',
  ],
];
export function EhtFeaturesScene({ state }: { state: EhtFeaturesState }) {
  const i = featuresIndex(state),
    j = featuresReferenceIndex(state),
    choice = featuresIndex(state, 4),
    reveal = featuresReveal(state);
  return (
    <section className={css.scene} data-features-scene={state.scene}>
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'inputs' && (
        <>
          <div className={css.two}>
            <div>
              <h4>28 native u/v samples</h4>
              <Coverage time={i} />
            </div>
            <div>
              <h4>Green: real · orange: imaginary</h4>
              <Visibilities time={i} />
            </div>
          </div>
          <Epoch time={i} />
          <p className={css.unit}>
            Eight stations · complex Jy measurements · overlapping baselines remain separate rows.
          </p>
        </>
      )}
      {state.scene === 'closures' && <Closure choice={featuresIndex(state, 6)} />}
      {state.scene === 'model' && <Model choice={choice} />}
      {state.scene === 'posterior' && (
        <div data-features-choice={choice}>
          <div className={css.two}>
            <div>
              <h4>{data.parameter_labels[choice]} · original weights</h4>
              <Ridge parameter={choice} />
            </div>
            <div>
              <h4>10,000 samples per epoch</h4>
              <EffectiveSamples />
            </div>
          </div>
          <p className={css.unit}>
            60 bins · width {n(data.histograms[choice].bin_width, 3)} {data.parameter_units[choice]}{' '}
            · each ridge height normalized · no KDE.
          </p>
          <p className={css.note}>
            One frame-9 sample carries 45.9% of its weight. Sample count is not effective sample
            size.
          </p>
        </div>
      )}
      {state.scene === 'reference' && !reveal && (
        <div className={css.hidden}>
          <h4>Supplied truth remains hidden</h4>
          <p>The second half reveals all ten truth, saved-image and error panels.</p>
          <p>Actual assistance levels expose truth. This controls reading order only.</p>
        </div>
      )}
      {state.scene === 'reference' && reveal && (
        <div data-features-reference="true">
          <div className={css.three}>
            <Plane image={ref.truth[j]} label="Supplied synthetic truth" reference />
            <Plane image={data.images[j]} label="Saved posterior mean" />
            <Plane image={ref.error[j]} label="Absolute error" reference />
          </div>
          <Epoch time={j} />
          <p className={css.unit}>
            Truth and mean share 0–0.0022; error uses 0–0.00038. Original array axes; no crop.
          </p>
        </div>
      )}
      {state.scene === 'diagnostics' && reveal && (
        <div data-features-reference="true" data-features-choice={choice}>
          <div className={css.two}>
            <div>
              <h4>{data.parameter_labels[choice]} · mean ± 1 SD</h4>
              <Summary parameter={choice} />
            </div>
            <div className={css.card}>
              <h4>Frame 4 · 3.2 hours</h4>
              <p>
                Weighted mean: <strong>{n(data.means[4][choice], 3)}</strong>
              </p>
              <p>
                Supplied truth: <strong>{n(ref.parameters[4][choice], 3)}</strong>
              </p>
              <p>
                Bias:{' '}
                <strong>
                  {n(ref.biases[4][choice], 3)} {data.parameter_units[choice]}
                </strong>
              </p>
              <p>
                Weighted SD: {n(data.stds[4][choice], 3)} {data.parameter_units[choice]}
              </p>
              <p className={css.note}>Weighted spread is not a guaranteed coverage interval.</p>
            </div>
          </div>
          <p className={css.unit}>
            Green: saved mean ± SD · purple dashed: truth · orange: frame 4. Joining lines guide
            reading; fits are independent.
          </p>
        </div>
      )}
      {state.scene === 'scoring' && reveal && (
        <div data-features-reference="true">
          <Scoring choice={choice} />
        </div>
      )}
      {state.scene === 'limits' && (
        <div className={css.two} data-features-choice={choice}>
          {limits.map(([title, body], k) => (
            <div key={title} className={`${css.card} ${choice === k ? css.active : ''}`}>
              <h4>{title}</h4>
              <p>{body}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
export function EhtFeaturesOutput({ state }: { state: EhtFeaturesState }) {
  const copy = {
    inputs: [
      'Synthetic source',
      'Ten snapshots run from 0 to 7.2 hours. Each baseline samples one spatial frequency; this is not a photograph.',
      'Native time and playback time are different.',
    ],
    closures: [
      'Gain-invariant combinations',
      '56 phase combinations have linear rank 21; 70 log-amplitude combinations have rank 19. They are correlated.',
      'A fixed station-gain control verifies algebra, not inference.',
    ],
    model: [
      'A constrained image family',
      'Diameter, width, asymmetry and angle define the source formula. Each snapshot trains an independent flow.',
      'Changing highlights and examples are conceptual, not optimizer states.',
    ],
    posterior: [
      'Concentrated weights',
      'Effective sample sizes range from 4.3 to 110.9 among 10,000 stored samples. All original weights enter the histograms.',
      'No new samples, posterior fit or density smoothing.',
    ],
    reference: [
      'Reader reference reveal',
      featuresReveal(state)
        ? 'Stored images sum to approximately one. Their scale differs from the 0.6 Jy used to generate observations.'
        : 'Truth appears at this chapter’s midpoint, separately from saved posterior summaries.',
      'Purple dashed borders identify reference-derived views.',
    ],
    diagnostics: [
      'One sequence is not calibration',
      'The angle mean at frame 4 is 26.24° below truth, while its weighted SD is 7.30°. A narrow-looking result can be displaced.',
      'Ten snapshots of one synthetic sequence are not ten independent studies.',
    ],
    scoring: [
      'Separate evaluation contracts',
      'Native angle error measures a point estimate; generic scoring measures mean-image similarity. Neither directly assesses posterior calibration.',
      'Original values retained. Oracle controls use answers.',
    ],
    limits: [
      'What is verified',
      'Pinned sources, fixed arithmetic, saved arrays and staging. The older no-filesystem scorer fails to find the NPZ reference.',
      'No new training, NUFFT execution or agent trial.',
    ],
  }[state.scene];
  return (
    <aside className={css.aside} data-features-output={state.scene}>
      <b>{copy[0]}</b>
      <h4>Read the condition</h4>
      <p>{copy[1]}</p>
      <small>{copy[2]}</small>
    </aside>
  );
}

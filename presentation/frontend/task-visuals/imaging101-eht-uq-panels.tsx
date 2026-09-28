import {
  ehtInput as input,
  ehtData as data,
  ehtReference as ref,
  ehtIndex,
  ehtReveal,
  ehtReferenceIndex,
  ehtGainControl,
  type EhtState,
  type EhtImage,
} from './imaging101-eht-uq';
import css from './imaging101-eht-uq.module.css';
const green = '#264b43',
  orange = '#b9521e',
  purple = '#8052a1',
  gray = '#84988e';
const n = (v: number, d = 3) => v.toFixed(d);
const titles = {
  inputs: 'Sparse Fourier measurements constrain the image',
  closures: 'Station gains change edges, but cancel in closures',
  prior: 'The retained prior and current source disagree',
  samples: 'Read stored samples from an approximate posterior',
  output: 'Separate the average image from sample spread',
  reference: 'Reveal reference; compare error and sample spread',
  scoring: 'An image score does not test uncertainty',
  limits: 'Preserve source, access and scientific limits',
};
function Plane({
  image,
  label,
  reference = false,
  pixel = false,
}: {
  image: EhtImage;
  label: string;
  reference?: boolean;
  pixel?: boolean;
}) {
  return (
    <figure className={css.plane} data-eht-panel={reference ? 'reference' : 'source'}>
      <figcaption>{label}</figcaption>
      <svg viewBox="0 0 245 238" role="img" aria-label={label}>
        <image
          href={image.data}
          x="36"
          y="9"
          width="185"
          height="185"
          preserveAspectRatio="none"
          style={{ imageRendering: 'pixelated' }}
        />
        <rect
          x="36"
          y="9"
          width="185"
          height="185"
          fill="none"
          stroke={reference ? purple : green}
          strokeDasharray={reference ? '5 3' : undefined}
        />
        {[80, 0, -80].map((v, i) => (
          <g key={v}>
            <text x={36 + i * 92.5} y="211" textAnchor="middle">
              {v}
            </text>
            <text x="30" y={13 + i * 92.5} textAnchor="end">
              {v}
            </text>
          </g>
        ))}
        <text x="127" y="231" textAnchor="middle">
          Relative RA (μas) →
        </text>
        <text transform="translate(11 110) rotate(-90)" textAnchor="middle">
          Relative Dec (μas)
        </text>
        {pixel && (
          <circle
            cx={36 + ((data.pixel.column + 0.5) / 32) * 185}
            cy={9 + ((31.5 - data.pixel.row) / 32) * 185}
            r="5"
            fill="none"
            stroke={orange}
            strokeWidth="2"
          />
        )}
      </svg>
      <div className={css.scale}>
        <span>0</span>
        <i className={css[image.palette]} />
        <span>{n(image.range[1], image.range[1] === 1 ? 0 : 3)}</span>
      </div>
      <p className={css.unit}>
        {image.unit}
        {pixel ? ' · marked pixel [15,20]' : ''}
      </p>
    </figure>
  );
}
function Coverage({ time }: { time: number }) {
  const xy = ([u, v]: number[]) => [135 + (u / 10) * 104, 131 - (v / 10) * 104];
  return (
    <svg
      className={css.chart}
      viewBox="0 0 270 280"
      role="img"
      aria-label="Native Fourier coverage in G wavelengths"
    >
      {[-8, 0, 8].map((v) => (
        <g key={v}>
          <path
            d={`M31 ${131 - (v / 10) * 104}H239M${135 + (v / 10) * 104} 27V235`}
            stroke="#dbe0d4"
          />
          <text x={135 + (v / 10) * 104} y="251" textAnchor="middle">
            {v}
          </text>
          <text x="23" y={135 - (v / 10) * 104} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      {input.uv_Glambda.map((p, i) => {
        const [x, y] = xy(p),
          [cx, cy] = xy(p.map((a) => -a));
        return (
          <g key={i}>
            <circle cx={cx} cy={cy} r="1.1" fill={orange} opacity=".6" />
            <circle
              cx={x}
              cy={y}
              r={input.time_ids[i] === time ? 3 : 1.25}
              fill={input.time_ids[i] === time ? green : gray}
            />
          </g>
        );
      })}
      <text x="137" y="273" textAnchor="middle">
        u (G wavelengths)
      </text>
      <text transform="translate(11 132) rotate(-90)" textAnchor="middle">
        v (G wavelengths)
      </text>
    </svg>
  );
}
function Measurements({ kind }: { kind: 'phase' | 'amplitude' }) {
  const values = kind === 'phase' ? input.phase_deg : input.log_amplitude,
    limit = kind === 'phase' ? 180 : 9;
  const x = (i: number) => 39 + (i / (values.length - 1)) * 210,
    y = (v: number) => 130 - (v / limit) * 101;
  return (
    <svg
      className={css.chart}
      viewBox="0 0 270 280"
      role="img"
      aria-label={
        kind === 'phase'
          ? '465 measured closure phases in degrees'
          : '485 measured log closure amplitudes'
      }
    >
      {[-limit, 0, limit].map((v) => (
        <g key={v}>
          <path d={`M39 ${y(v)}H249`} stroke="#dbe0d4" />
          <text x="34" y={y(v) + 4} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      {values.map((v, i) => (
        <circle key={i} cx={x(i)} cy={y(v)} r="1.5" fill={green} />
      ))}
      {[0, Math.floor(values.length / 2), values.length - 1].map((i) => (
        <text key={i} x={x(i)} y="251" textAnchor="middle">
          {i}
        </text>
      ))}
      <text x="144" y="273" textAnchor="middle">
        Source closure row
      </text>
    </svg>
  );
}
function Closure({ kind, progress }: { kind: 'phase' | 'amplitude'; progress: number }) {
  const w = input.witnesses[kind],
    c = ehtGainControl(w, progress, kind),
    points =
      kind === 'phase'
        ? [
            [45, 35],
            [310, 35],
            [178, 128],
          ]
        : [
            [45, 35],
            [310, 35],
            [310, 125],
            [45, 125],
          ];
  return (
    <div data-eht-closure={kind} data-eht-closure-value={c.value}>
      <h4>{kind === 'phase' ? 'Triangle · phase sum' : 'Quadrangle · amplitude ratio'}</h4>
      <svg
        className={css.network}
        viewBox="0 0 355 162"
        role="img"
        aria-label={`${kind} closure station diagram, schematic positions`}
      >
        {c.edges.map((e, i) => {
          const [x, y] = points[e.from],
            [a, b] = points[e.to];
          return (
            <g key={i}>
              <path
                d={`M${x} ${y}L${a} ${b}`}
                stroke={orange}
                strokeWidth="2"
                strokeDasharray={e.weight < 0 ? '5 3' : undefined}
              />
            </g>
          );
        })}
        {points.map(([x, y], i) => (
          <g key={i}>
            <circle cx={x} cy={y} r={11 + 6 * c.gains[i].amplitude} fill="#e6ede3" stroke={green} />
            <text x={x} y={y + 4} textAnchor="middle">
              {i + 1}
            </text>
            <text x={x} y={y < 60 ? y - 23 : y + 29} textAnchor="middle">
              {w.stations[i]}
            </text>
          </g>
        ))}
      </svg>
      <div className={css.edgeTable}>
        {c.edges.map((e, i) => (
          <span key={i}>
            {e.from + 1}→{e.to + 1}:{' '}
            {kind === 'phase' ? `${n(e.phase, 1)}°` : `${n(e.amplitude)} Jy`}
          </span>
        ))}
      </div>
      <div className={css.measure}>
        {kind === 'phase' ? 'Σ phase' : 'ln(|V12·V34| / |V14·V23|)'} = {n(c.value, 3)}
        {kind === 'phase' ? '°' : ''}
      </div>
      <p className={css.unit}>
        Stored closure row 0: {n(w.observed, 3)}
        {kind === 'phase' ? '°' : ''}
      </p>
    </div>
  );
}
function PixelTrace({ index }: { index: number }) {
  const p = data.pixel,
    upper = Math.ceil(Math.max(...p.values) * 100) / 100,
    x = (i: number) => 45 + (i / 1023) * 295,
    y = (v: number) => 221 - (v / upper) * 186;
  const path = p.values.map((v, i) => `${i ? 'L' : 'M'}${x(i)},${y(v)}`).join(' ');
  return (
    <svg
      className={css.chart}
      viewBox="0 0 365 280"
      role="img"
      aria-label="All 1024 saved pixel values; mean and population standard deviation"
    >
      <rect
        x="45"
        y={y(p.mean + p.std)}
        width="295"
        height={((2 * p.std) / upper) * 186}
        fill="#e1ece4"
      />
      <path d={`M45 ${y(p.mean)}H340`} stroke={green} strokeWidth="2" strokeDasharray="5 3" />
      <path d={path} fill="none" stroke={gray} strokeWidth=".7" />
      <circle cx={x(index)} cy={y(p.values[index])} r="4" fill={orange} />
      <text x="45" y="24">
        Jy/pixel
      </text>
      {[0, upper / 2, upper].map((v) => (
        <g key={v}>
          <text x="40" y={y(v) + 4} textAnchor="end">
            {n(v, 3)}
          </text>
        </g>
      ))}
      {[0, 512, 1023].map((i) => (
        <text key={i} x={x(i)} y="245" textAnchor="middle">
          {i}
        </text>
      ))}
      <text x="180" y="271" textAnchor="middle">
        Saved sample index (not time)
      </text>
    </svg>
  );
}
const scoreRows = [
  ['Native mean helper', 'Peak normalized', data.native_metrics],
  ['Generic mean', 'Absolute intensity', data.generic_metrics.saved_mean],
  ['Generic + zero std', 'Same mean', data.generic_metrics.zero_std],
  ['Generic + 1 Jy/pixel std', 'Same mean', data.generic_metrics.one_Jy_std],
  ['Reference-copy control', 'Truth visible in L1–L3', data.generic_metrics.oracle_truth],
] as const;
function Scoring({ index }: { index: number }) {
  const row = scoreRows[index];
  return (
    <>
      <table className={css.table} data-eht-score-row={index}>
        <thead>
          <tr>
            <th>Saved-array control</th>
            <th>NCC</th>
            <th>NRMSE</th>
          </tr>
        </thead>
        <tbody>
          {scoreRows.map(([label, , m], i) => (
            <tr key={label} className={i === index ? css.active : undefined}>
              <td>{label}</td>
              <td>{n(m.ncc, 6)}</td>
              <td>{n(m.nrmse, 6)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className={css.formula}>
        <strong>{row[0]}</strong> · {row[1]}
      </div>
      <p className={css.note}>
        Generic scoring ignores std and rejects a sample stack. Current pass thresholds are absent.
      </p>
    </>
  );
}
const limits = [
  {
    title: 'Truth is seeded at every assistance level',
    body: 'L1, L2 and L3 include ground_truth.npz and gt.fits in data/. Saved outputs and fixtures are not seeded.',
    detail: 'L2 adds an approach; L3 adds design. This reader reveal is not private evaluation.',
  },
  {
    title: 'Pinned source is not a reproducible saved run',
    body: 'main.py has a syntax error. The current loader returns arrays, while the solver expects an obsolete obs object.',
    detail:
      'Current prior flux also differs from retained fixtures. No source patch, model run or installation occurred.',
  },
  {
    title: 'Similar filenames contain different samples',
    body: 'posterior_samples.npy gives the saved mean/std exactly. posterior_samples_1024.npy is a different 1024-image set.',
    detail:
      'Largest mean-map difference: 0.012809 Jy/pixel. Preserve both files and their separate identities.',
  },
  {
    title: 'Real-observation provenance remains unresolved',
    body: 'Both FITS files match the original DPI example. Header labels alone do not verify the README’s real-2015 claim.',
    detail:
      'Call this the bundled DPI example. No calibrated astrophysical posterior, blind task pass or agent result is established.',
  },
];
export function EhtScene({ state }: { state: EhtState }) {
  const sample = ehtIndex(state, data.samples.length),
    pixelSample = ehtIndex(state, data.pixel.values.length),
    time = ehtIndex(state, input.times.length),
    revealed = ehtReveal(state);
  return (
    <section className={css.scene} data-eht-scene={state.scene} data-eht-view={state.view}>
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'inputs' && (
        <>
          <div className={css.three}>
            <div>
              <h4>938 visibilities</h4>
              <Coverage time={time} />
              <p className={css.unit}>Teal = stored · orange = conjugates</p>
            </div>
            <div>
              <h4>465 closure phases</h4>
              <Measurements kind="phase" />
              <p className={css.unit}>degrees · noise retained</p>
            </div>
            <div>
              <h4>485 log amplitude ratios</h4>
              <Measurements kind="amplitude" />
              <p className={css.unit}>dimensionless natural logarithm</p>
            </div>
          </div>
          <p className={css.note} data-eht-time={time}>
            9 stations · highlighted timestamp {time + 1}/100. Sparse frequencies leave image
            ambiguity.
          </p>
        </>
      )}
      {state.scene === 'closures' && (
        <>
          <div className={css.two}>
            <Closure kind="phase" progress={state.view} />
            <Closure kind="amplitude" progress={state.view} />
          </div>
          <p className={css.note}>
            Schematic layout · gain {n(state.view * 100, 0)}%. Orange: solid numerator, dashed
            denominator. Closures stay fixed.
          </p>
        </>
      )}
      {state.scene === 'prior' && (
        <>
          <div className={css.two} data-eht-prior={ehtIndex(state, 2)}>
            <div className={ehtIndex(state, 2) === 0 ? css.active : undefined}>
              <Plane image={input.retained_prior} label="Retained Gaussian prior" />
              <p>
                APEX–ALMA: <strong>{n(input.retained_flux, 6)} Jy</strong>
              </p>
            </div>
            <div className={ehtIndex(state, 2) === 1 ? css.active : undefined}>
              <Plane image={input.current_prior} label="Current source Gaussian prior" />
              <p>
                All visibilities: <strong>{n(input.current_flux, 6)} Jy</strong>
              </p>
            </div>
          </div>
          <p className={css.note}>
            Both use 50 μas FWHM. Different flux targets are different inference conditions.
          </p>
        </>
      )}
      {state.scene === 'samples' && (
        <div className={css.two} data-eht-sample={sample}>
          <div>
            <Plane image={data.samples[sample].image} label={`Saved sample row ${sample} / 1023`} />
            <p>Flux: {n(data.samples[sample].flux, 4)} Jy · common brightness scale</p>
          </div>
          <div>
            <div className={css.flow}>
              <div>
                Gaussian latent z <strong>→</strong> Real-NVP flow
              </div>
              <div>
                Softplus + learned scale <strong>→</strong> positive image
              </div>
              <div>Closure fit + priors − entropy bonus</div>
            </div>
            <p className={css.unit}>Source procedure, schematic. No latent values are replayed.</p>
            <div className={css.sampleGrid}>
              {data.samples.map((s, i) => (
                <div
                  key={i}
                  aria-label={`Saved sample thumbnail ${i}`}
                  className={i === sample ? css.selected : undefined}
                >
                  <img src={s.image.data} alt="" />
                  row {s.source_row}
                </div>
              ))}
            </div>
            <p className={css.unit}>First eight stored rows · no ranking or temporal order</p>
          </div>
        </div>
      )}
      {state.scene === 'output' && (
        <>
          <div className={css.three} data-eht-pixel-sample={pixelSample}>
            <Plane image={data.mean} label="Mean of 1,024 stored images" pixel />
            <Plane image={data.std} label="Population standard deviation" pixel />
            <div>
              <h4>Fixed pixel [15,20]</h4>
              <PixelTrace index={pixelSample} />
              <p className={css.unit}>
                Row {pixelSample}: {n(data.pixel.values[pixelSample], 4)} Jy/pixel
              </p>
              <p className={css.unit}>Teal dashed mean · pale band ±1 std</p>
            </div>
          </div>
          <p className={css.note}>
            Sample spread depends on the fitted model, likelihood and priors. It is not a pixel
            error map.
          </p>
        </>
      )}
      {state.scene === 'reference' &&
        (revealed ? (
          <>
            <div className={css.three} data-eht-reference="true">
              <Plane image={ref.image} label="Supplied reference · solver visible" reference />
              <Plane image={data.mean} label="Saved posterior mean" />
              <Plane
                image={ehtReferenceIndex(state) === 0 ? ref.error : ref.containment}
                label={
                  ehtReferenceIndex(state) === 0
                    ? 'Absolute mean error'
                    : 'Reference within mean ±1 std'
                }
                reference
              />
            </div>
            <p className={css.note}>
              180 / 1,024 pixels lie within ±1 std. One-image containment is not proof of
              calibration.
            </p>
          </>
        ) : (
          <div className={css.hidden}>
            <h4>Reference and error remain hidden</h4>
            <p>
              Continue this chapter to reveal the supplied reference. It was visible to the solver
              in all L1–L3 conditions.
            </p>
          </div>
        ))}
      {state.scene === 'scoring' && <Scoring index={ehtIndex(state, scoreRows.length)} />}
      {state.scene === 'limits' && (
        <div className={css.card} data-eht-limit={ehtIndex(state, limits.length)}>
          <h4>{limits[ehtIndex(state, limits.length)].title}</h4>
          <p>{limits[ehtIndex(state, limits.length)].body}</p>
          <p className={css.note}>{limits[ehtIndex(state, limits.length)].detail}</p>
          <p className={css.formula}>
            Source arrays + bounded arithmetic controls + saved-output replay
          </p>
          <p>
            Original bytes and historical scores remain retained. No new training, sampling, NUFFT
            inference or model trial.
          </p>
        </div>
      )}
    </section>
  );
}
export function EhtOutput({ state }: { state: EhtState }) {
  const notes: Record<EhtState['scene'], [string, string]> = {
    inputs: [
      'Measure frequencies, not pixels',
      'A telescope pair measures a Fourier component. Orange conjugates are derived symmetry, not extra data. Closure rows share baselines and noise.',
    ],
    closures: [
      'Gain cancellation is an identity',
      'Vab′ = ga · conj(gb) · Vab. Each station phase cancels around the triangle; gain amplitudes cancel in the quadrangle ratio. Thermal noise remains.',
    ],
    prior: [
      'Closures need additional assumptions',
      'Closure data do not determine absolute flux or position. The source supplies flux, centering, maximum-entropy, sparsity and smoothness penalties.',
    ],
    samples: [
      'Approximate posterior, conditional on choices',
      'The entropy term discourages collapse to one image. A varied sample set does not prove all plausible solutions or their probabilities were recovered.',
    ],
    output: [
      'Use all 1,024 stored rows',
      'Mean = ΣI / 1024. Variance = Σ(I − mean)² / 1024. This sample file exactly reproduces the saved maps. No Gaussian coverage assumption is made.',
    ],
    reference: ehtReveal(state)
      ? [
          'Compare error with spread',
          'Purple dashed borders identify reference-derived views. The observed containment fraction is descriptive for this supplied image, not a universal calibration target.',
        ]
      : [
          'A reader boundary',
          'Reference values and error maps appear after the midpoint. Actual solver staging already exposed the reference; reading order does not alter that condition.',
        ],
    scoring: [
      'Separate metric definitions',
      'Task-native scoring peak-normalizes and centers correlation. The local generic scorer uses raw intensity and cosine similarity. Neither scores sample diversity or std.',
    ],
    limits: [
      'Scope of this explanation',
      'One bundled DPI example, retained arrays and fixed controls. The source audit records versions, staging, contradictory source code and unresolved observation provenance.',
    ],
  };
  return (
    <aside className={css.aside} data-eht-output={state.scene}>
      <b>READING THE EVIDENCE</b>
      <h4>{notes[state.scene][0]}</h4>
      <p>{notes[state.scene][1]}</p>
      <small>32 × 32 · 160 μas field of view · no new model execution</small>
    </aside>
  );
}

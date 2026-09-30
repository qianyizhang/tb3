import {
  originalInput as input,
  originalData as data,
  originalReference as ref,
  originalIndex,
  originalReferenceIndex,
  originalReveal,
  originalPairs,
  originalStationOrder,
  type OriginalImage,
  type EhtOriginalState,
} from './imaging101-eht-original';
import css from './imaging101-eht-original.module.css';
const green = '#264b43',
  orange = '#b9521e',
  purple = '#8052a1';
const n = (v: number, digits = 3) => v.toFixed(digits);
const titles = {
  inputs: 'Sparse Fourier coverage, two supplied observations',
  closures: 'Combine simultaneous baselines to cancel station gains',
  observables: 'Gain cancellation does not remove measurement noise',
  imaging: 'Use an image prior to constrain the missing information',
  outputs: 'Inspect all six retained reconstruction conditions',
  reference: 'Reveal the supplied synthetic reference',
  scoring: 'Image scaling changes the meaning of the score',
  limits: 'Keep reference access and source limitations visible',
};
function Plane({
  image,
  label,
  reference = false,
}: {
  image: OriginalImage;
  label: string;
  reference?: boolean;
}) {
  return (
    <figure className={css.plane} data-original-panel={reference ? 'reference' : 'saved'}>
      <figcaption>{label}</figcaption>
      <svg viewBox="0 0 240 226" role="img" aria-label={label}>
        <image
          href={image.data}
          x="34"
          y="8"
          width="183"
          height="183"
          preserveAspectRatio="none"
          style={{ imageRendering: 'pixelated' }}
        />
        <rect
          x="34"
          y="8"
          width="183"
          height="183"
          fill="none"
          stroke={reference ? purple : green}
          strokeDasharray={reference ? '5 3' : undefined}
        />
        {[0, 32, 63].map((v) => (
          <g key={v}>
            <text x={34 + ((v + 0.5) / 64) * 183} y="207" textAnchor="middle">
              {v}
            </text>
            <text x="29" y={12 + ((v + 0.5) / 64) * 183} textAnchor="end">
              {v}
            </text>
          </g>
        ))}
        <text x="126" y="224" textAnchor="middle">
          Array column →
        </text>
        <text transform="translate(10 100) rotate(-90)" textAnchor="middle">
          Array row ↓
        </text>
      </svg>
      <div className={css.scale}>
        <span>10⁻⁶</span>
        <i />
        <span>0.34</span>
      </div>
      <p className={css.unit}>Unit-flux / pixel · logarithmic</p>
      <p className={css.unit}>
        Stored pixel sum: <strong>{n(image.stored_sum, 6)}</strong>
      </p>
    </figure>
  );
}
function Coverage({ pair }: { pair: number }) {
  const selected = originalPairs[pair];
  return (
    <svg
      className={css.chart}
      viewBox="0 0 330 285"
      role="img"
      aria-label="All 421 stored Fourier samples"
    >
      {[-8, 0, 8].map((v) => (
        <g key={v}>
          <path d={`M50 ${139 - v * 12}H304M${177 + v * 12} 31V247`} stroke="#dbe0d4" />
          <text x={177 + v * 12} y="262" textAnchor="middle">
            {v}
          </text>
          <text x="43" y={143 - v * 12} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      {input.uv_Glambda.map(([u, v], i) => {
        const active = [...input.station_pairs[i]].sort((a, b) => a - b).join('-') === selected;
        return (
          <circle
            key={i}
            cx={177 + u * 12}
            cy={139 - v * 12}
            r={active ? 3.6 : 1.8}
            fill={active ? orange : green}
            opacity={active ? 1 : 0.48}
          >
            <title>Native sample {i}</title>
          </circle>
        );
      })}
      <text x="177" y="283" textAnchor="middle">
        u (billion wavelengths)
      </text>
      <text transform="translate(13 138) rotate(-90)" textAnchor="middle">
        v (billion wavelengths)
      </text>
    </svg>
  );
}
function Amplitudes() {
  const x = (i: number) => 47 + Math.hypot(...input.uv_Glambda[i]) * 27,
    y = (v: number) => 244 - v * 220;
  return (
    <svg
      className={css.chart}
      viewBox="0 0 330 285"
      role="img"
      aria-label="All calibrated and corrupted visibility amplitudes in Jy"
    >
      {[0, 0.3, 0.6, 0.9].map((v) => (
        <g key={v}>
          <path d={`M47 ${y(v)}H306`} stroke="#dbe0d4" />
          <text x="39" y={y(v) + 4} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      {[0, 4, 8].map((v) => (
        <text key={v} x={47 + v * 27} y="261" textAnchor="middle">
          {v}
        </text>
      ))}
      {[input.vis_cal_abs_Jy, input.vis_corrupt_abs_Jy].map((a, k) =>
        a.map((v, i) =>
          k ? (
            <rect
              key={`${k}-${i}`}
              x={x(i) - 1.5}
              y={y(v) - 1.5}
              width="3"
              height="3"
              fill={orange}
            />
          ) : (
            <circle key={`${k}-${i}`} cx={x(i)} cy={y(v)} r="2" fill={green} />
          ),
        ),
      )}
      <text x="172" y="283" textAnchor="middle">
        Baseline length (billion wavelengths)
      </text>
      <text transform="translate(13 138) rotate(-90)" textAnchor="middle">
        Visibility amplitude (Jy)
      </text>
    </svg>
  );
}
function Closure({ choice }: { choice: number }) {
  const c = input.closure_controls[choice],
    phase = c.kind === 'phase';
  const stations = originalStationOrder(c);
  const points = phase
    ? [
        [56, 202],
        [172, 40],
        [290, 202],
      ]
    : [
        [56, 48],
        [290, 48],
        [56, 207],
        [290, 207],
      ];
  return (
    <div className={css.two} data-original-choice={choice}>
      <div>
        <h4>
          {phase ? 'Triangle phase' : 'Four-station log ratio'} · source row {c.source_row}
        </h4>
        <svg
          className={css.chart}
          viewBox="0 0 345 278"
          role="img"
          aria-label="Matched native station relationships; schematic positions"
        >
          {c.pairs.map(([a, b], i) => {
            const p = points[stations.indexOf(a)],
              q = points[stations.indexOf(b)];
            return (
              <g key={i}>
                <path
                  d={`M${p[0]} ${p[1]}L${q[0]} ${q[1]}`}
                  stroke={c.signs[i] > 0 ? green : orange}
                  strokeWidth="3"
                  strokeDasharray={c.signs[i] < 0 ? '6 4' : undefined}
                />
                <rect
                  x={(p[0] + q[0]) / 2 - 25}
                  y={(p[1] + q[1]) / 2 - 12}
                  width="50"
                  height="24"
                  fill="#f6f7ef"
                />
                <text x={(p[0] + q[0]) / 2} y={(p[1] + q[1]) / 2 + 5} textAnchor="middle">
                  {c.signs[i] > 0 ? '+' : '−'} {a}→{b}
                </text>
              </g>
            );
          })}
          {points.map(([x, y], i) => (
            <g key={i}>
              <circle cx={x} cy={y} r="6" fill={green} />
              <text x={x} y={y + (phase && i === 1 ? -18 : 28)} textAnchor="middle">
                {input.station_names[stations[i]]}
              </text>
            </g>
          ))}
        </svg>
        <p className={css.unit}>Schematic station positions. Solid adds; dashed subtracts.</p>
      </div>
      <div className={css.card}>
        <h4>Fixed gains, same recorded samples</h4>
        <table className={css.table}>
          <thead>
            <tr>
              <th>Term</th>
              <th>Before</th>
              <th>After</th>
            </tr>
          </thead>
          <tbody>
            {c.before.map((v, i) => (
              <tr key={i}>
                <td>
                  {c.signs[i] > 0 ? '+' : '−'} {c.pairs[i].join('→')}
                </td>
                <td>{n(v, 2)}</td>
                <td>{n(c.after[i], 2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className={css.formula}>
          {phase ? 'Wrapped phase sum' : 'Signed log sum'}
          <br />
          <strong>
            {n(c.combined_before, 6)} → {n(c.combined_after, 6)}
          </strong>
        </p>
        <p className={css.unit}>
          {phase
            ? 'Terms and result in degrees.'
            : 'Natural logs of amplitudes; signed result dimensionless.'}
        </p>
        <p className={css.unit}>UV-matched rows preserve scan geometry. No noise was redrawn.</p>
      </div>
    </div>
  );
}
function Scatter({ phase }: { phase: boolean }) {
  const a = phase ? input.observed.cp_values_deg : input.observed.lca_values,
    b = phase ? input.observed.cp_corrupt_values_deg : input.observed.lca_corrupt_values;
  const lo = phase ? -180 : -18,
    hi = phase ? 180 : 3,
    x = (v: number) => 49 + ((v - lo) / (hi - lo)) * 235,
    y = (v: number) => 241 - ((v - lo) / (hi - lo)) * 205;
  const ticks = phase ? [-180, 0, 180] : [-18, -9, 0, 3];
  return (
    <svg
      className={css.chart}
      viewBox="0 0 330 285"
      role="img"
      aria-label={phase ? 'All 269 supplied phase pairs' : 'All 233 supplied log-amplitude pairs'}
    >
      {ticks.map((v) => (
        <g key={v}>
          <path d={`M49 ${y(v)}H284M${x(v)} 36V241`} stroke="#dbe0d4" />
          <text x={x(v)} y="259" textAnchor="middle">
            {v}
          </text>
          <text x="42" y={y(v) + 4} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      <path d={`M${x(lo)} ${y(lo)}L${x(hi)} ${y(hi)}`} stroke={orange} strokeDasharray="6 4" />
      {a.map((v, i) => (
        <circle key={i} cx={x(v)} cy={y(b[i])} r="2.2" fill={green}>
          <title>Source row {i}</title>
        </circle>
      ))}
      <text x="165" y="283" textAnchor="middle">
        Calibrated {phase ? 'phase (degrees)' : 'log amplitude'}
      </text>
      <text transform="translate(13 138) rotate(-90)" textAnchor="middle">
        Corrupted {phase ? 'phase (degrees)' : 'log amplitude'}
      </text>
    </svg>
  );
}
function Imaging({ choice }: { choice: number }) {
  const labels = [
    '1 · Choose a positive image',
    '2 · Predict complex visibilities',
    '3 · Form predicted closures',
    '4 · Balance data fit and prior',
  ];
  const text = [
    'The retained Gaussian is a workflow prior, not a seeded image file.',
    'Use the released +2πi Fourier operator and triangle pixel response.',
    'Use simultaneous triangle phases and four-station amplitude ratios.',
    'Entropy penalties constrain missing information. This diagram is conceptual.',
  ];
  return (
    <div className={css.two} data-original-choice={choice}>
      <div>
        <Plane image={data.prior} label="Retained workflow prior" />
        <p className={css.unit}>Display rescaled to unit flux; original sum shown.</p>
      </div>
      <div className={css.flow}>
        {labels.map((label, i) => (
          <div key={label} className={`${css.card} ${choice === i ? css.active : ''}`}>
            <h4>{label}</h4>
            <p>{text[i]}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
function Results({ choice, reveal = false }: { choice: number; reveal?: boolean }) {
  return (
    <div data-original-choice={choice} data-original-reference={reveal ? 'true' : undefined}>
      <h4>{data.method_labels[choice]} · retained outputs</h4>
      <div className={reveal ? css.three : css.two}>
        {reveal && <Plane image={ref.truth} label="Supplied truth" reference />}
        <Plane image={data.images[choice * 2]} label="Calibrated observation" />
        <Plane image={data.images[choice * 2 + 1]} label="Corrupted observation" />
      </div>
      <p className={css.note}>
        Every image is rescaled to unit flux for display. Shared log scale; values below 10⁻⁶ are
        black. Full 64×64 grids, no crop.
      </p>
    </div>
  );
}
function Scores({ choice }: { choice: number }) {
  const rows = choice < 3 ? [choice * 2, choice * 2 + 1] : [4, 5];
  return (
    <div data-original-choice={choice} data-original-reference="true">
      <table className={css.table}>
        <thead>
          <tr>
            <th>Retained condition</th>
            <th>Cosine NCC</th>
            <th>Published NRMSE¹</th>
            <th>Live NRMSE²</th>
          </tr>
        </thead>
        <tbody>
          {data.names.map((name, i) => (
            <tr key={name} className={rows.includes(i) ? css.active : undefined}>
              <td>
                {data.method_labels[Math.floor(i / 2)]} · {i % 2 ? 'corrupt' : 'cal'}
              </td>
              <td>{n(ref.generic[i].ncc, 4)}</td>
              <td>{n(ref.native[i].nrmse, 4)}</td>
              <td>{n(ref.generic[i].nrmse, 6)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className={css.unit}>
        ¹ Flux-match, then divide RMSE by reference range. ² Same range, without flux-match.
      </p>
      {choice === 3 ? (
        <div className={css.note}>
          <strong>Controls expose the scoring boundary.</strong> Physical 0.6 Jy truth: NCC 1, live
          error {n(ref.physical_truth.nrmse, 6)}. Zero image: error {n(ref.zero.nrmse, 6)}. The
          scorer expects the unit-sum reference.
        </div>
      ) : (
        <div className={css.note}>
          No pass thresholds. The older fallback also flux-matches, but divides by reference RMS:
          closure-corrupt error {n(ref.fallback.nrmse, 4)}. These denominators are not
          interchangeable.
        </div>
      )}
    </div>
  );
}
function Limits({ choice }: { choice: number }) {
  const rows = [
    [
      'Answers are supplied',
      'All L1–L3 copy ground_truth.npz. Calibrated observations and native closures are also given.',
    ],
    [
      'Preserve scan identity',
      'The small first-match helper mixes scans. The main path uses supplied per-scan UV arrays.',
    ],
    [
      'Retain source discrepancies',
      'A malformed fixture, a 2× loss convention and a TV-gradient sign defect remain documented.',
    ],
    [
      'Keep claims bounded',
      'One synthetic source and saved outputs. No new optimization, agent pass, runtime recovery or sky-data result.',
    ],
  ];
  return (
    <div className={css.two} data-original-choice={choice}>
      {rows.map(([title, body], i) => (
        <div key={title} className={`${css.card} ${i === choice ? css.active : ''}`}>
          <h4>{title}</h4>
          <p>{body}</p>
        </div>
      ))}
      <p className={css.note}>
        The six saved comparisons use entropy penalties. The TV defect alone does not explain their
        outcomes.
      </p>
    </div>
  );
}
export function EhtOriginalScene({ state: s }: { state: EhtOriginalState }) {
  const pair = originalIndex(s, 21);
  return (
    <section className={css.scene} data-original-scene={s.scene}>
      <h3>{titles[s.scene]}</h3>
      {s.scene === 'inputs' && (
        <>
          <div className={css.two}>
            <div>
              <Coverage pair={pair} />
              <p className={css.unit}>
                Orange:{' '}
                {originalPairs[pair]
                  .split('-')
                  .map((i) => input.station_names[Number(i)])
                  .join('–')}{' '}
                · pair {pair + 1}/21
              </p>
            </div>
            <div>
              <Amplitudes />
              <p className={css.unit}>Green circles: calibrated · orange squares: corrupted</p>
            </div>
          </div>
          <p className={css.note}>
            421 stored samples from seven stations; no added conjugates. This synthetic source is
            static.
          </p>
        </>
      )}
      {s.scene === 'closures' && <Closure choice={originalIndex(s, 6)} />}
      {s.scene === 'observables' && (
        <>
          <div className={css.two}>
            <div className={originalIndex(s, 2) === 0 ? css.selected : undefined}>
              <h4>269 supplied closure phases</h4>
              <Scatter phase />
            </div>
            <div className={originalIndex(s, 2) === 1 ? css.selected : undefined}>
              <h4>233 supplied log amplitude ratios</h4>
              <Scatter phase={false} />
            </div>
          </div>
          <p className={css.note}>
            Orange dashed: equality. Noisy-condition differences remain; algebraic gain cancellation
            is not noise immunity.
          </p>
        </>
      )}
      {s.scene === 'imaging' && <Imaging choice={originalIndex(s, 4)} />}
      {s.scene === 'outputs' && <Results choice={originalIndex(s, 3)} />}
      {s.scene === 'reference' &&
        (originalReveal(s) ? (
          <Results choice={originalReferenceIndex(s)} reveal />
        ) : (
          <div className={css.hidden}>
            <h4>Reference not yet revealed</h4>
            <p>
              Continue through this chapter to inspect all three saved methods beside the synthetic
              truth.
            </p>
            <p>Actual L1–L3 expose this answer; the reveal controls reading order.</p>
          </div>
        ))}
      {s.scene === 'scoring' && originalReveal(s) && <Scores choice={originalIndex(s, 4)} />}
      {s.scene === 'limits' && <Limits choice={originalIndex(s, 4)} />}
    </section>
  );
}
export function EhtOriginalOutput({ state: s }: { state: EhtOriginalState }) {
  const body: Record<EhtOriginalState['scene'], [string, string]> = {
    inputs: [
      'What is supplied?',
      'Both calibrated and corrupted complex observations, geometry, uncertainties and precomputed per-scan closures.',
    ],
    closures: [
      'What cancels?',
      'Station factors cancel from phase loops and amplitude ratios. Fixed multipliers on matched native rows demonstrate the algebra.',
    ],
    observables: [
      'What remains?',
      'Noise and correlated combinations remain. The complete phase and amplitude arrays are shown, including outliers.',
    ],
    imaging: [
      'What must be implemented?',
      'A nonnegative image, the correct Fourier convention, closure losses and regularization. No optimizer runs in this view.',
    ],
    outputs: [
      'What is retained?',
      'Three methods × two observation conditions. This is saved-output inspection, not newly executed reconstruction.',
    ],
    reference: [
      'What is the reference?',
      'The unit-sum synthetic image. It is accessible in every solver assistance level despite this reader reveal.',
    ],
    scoring: [
      'What do scores establish?',
      'Array similarity under an explicit scaling rule. No task pass thresholds or general robustness conclusion.',
    ],
    limits: [
      'What comes out?',
      'A single output/reconstruction.npy with shape (64,64). The live scorer expects the unit-sum convention.',
    ],
  };
  return (
    <aside className={css.aside} data-original-output>
      <b>STATIC CLOSURE IMAGING</b>
      <h4>{body[s.scene][0]}</h4>
      <p>{body[s.scene][1]}</p>
      <small>64×64 · 2 μas pixels · 128 μas field</small>
      <p className={css.note}>
        One synthetic M87-like source. No observed sky image or fresh agent trial.
      </p>
    </aside>
  );
}

import {
  nlosInputs as input,
  nlosContract as data,
  nlosReference as ref,
  nlosIndex,
  nlosReveal,
  type NlosState,
  type NlosImage,
} from './imaging101-nlos';
import css from './imaging101-nlos.module.css';

const titles = {
  inputs: 'Record when indirect light returns',
  alignment: 'Align time zero, then crop 512 bins',
  stolt: 'Sample temporal frequencies on the Stolt curve',
  output: 'Inspect the released 3D reconstruction',
  reference: 'Reveal a baseline with identical values',
  staging: 'The released input packet includes the baseline',
  scoring: 'Perfect agreement is a saved-output check',
  limits: 'Retain the useful operation and its limits',
};
function Histogram({ values, cropped = false }: { values: number[]; cropped?: boolean }) {
  const path = values
    .map(
      (v, i) =>
        `${i ? 'L' : 'M'}${(40 + (i / (values.length - 1)) * 425).toFixed(2)},${(130 - (v / 42) * 100).toFixed(2)}`,
    )
    .join(' ');
  const end = (values.length - 1) * 0.032;
  return (
    <svg
      className={css.histogram}
      viewBox="0 0 490 165"
      role="img"
      aria-label={cropped ? 'Aligned and cropped native photon counts' : 'Raw native photon counts'}
    >
      <text x="40" y="15">
        {cropped ? 'Aligned · first 512 bins' : 'Raw · all 2048 bins'} · photon counts
      </text>
      {[0, 21, 42].map((v) => (
        <g key={v}>
          <line
            x1="40"
            x2="465"
            y1={130 - (v / 42) * 100}
            y2={130 - (v / 42) * 100}
            stroke="#d8e0d7"
          />
          <text x="32" y={134 - (v / 42) * 100} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      <path
        data-nlos-histogram={cropped ? 'aligned' : 'raw'}
        d={path}
        fill="none"
        stroke={cropped ? '#b9521e' : '#264b43'}
        strokeWidth="1.4"
      />
      <text x="40" y="148">
        0
      </text>
      <text x="465" y="148" textAnchor="end">
        {end.toFixed(3)}
      </text>
      <text x="250" y="161" textAnchor="middle">
        {cropped ? 'Time after alignment' : 'Recorded time'} / ns
      </text>
    </svg>
  );
}
function Plane({
  image,
  label,
  xLabel = 'x / m',
  yLabel = 'y / m',
  yMin = -1,
  yMax = 1,
  baseline = false,
  point,
}: {
  image: NlosImage;
  label: string;
  xLabel?: string;
  yLabel?: string;
  yMin?: number;
  yMax?: number;
  baseline?: boolean;
  point?: { x: number; y: number };
}) {
  const height = (225 * (yMax - yMin)) / 2;
  // Source axes specify first/last pixel centres. Extend each image by half a
  // pixel so the centre coordinates, labels and selected sample agree exactly.
  const dx = 225 / (image.shape[1] - 1);
  const dy = height / (image.shape[0] - 1);
  return (
    <figure className={css.plane} data-nlos-plane={baseline ? 'baseline' : 'source'}>
      <svg viewBox="0 0 310 330" role="img" aria-label={label}>
        <image
          href={image.data}
          x={55 - dx / 2}
          y={20 - dy / 2}
          width={225 + dx}
          height={height + dy}
          preserveAspectRatio="none"
        />
        <rect
          x={55 - dx / 2}
          y={20 - dy / 2}
          width={225 + dx}
          height={height + dy}
          fill="none"
          stroke={baseline ? '#8052a1' : '#264b43'}
          strokeWidth="2"
          strokeDasharray={baseline ? '6 4' : undefined}
        />
        <text x="55" y={height + 38}>
          −1
        </text>
        <text x="280" y={height + 38} textAnchor="end">
          1
        </text>
        <text x="167" y={height + 53} textAnchor="middle">
          {xLabel}
        </text>
        <text x="47" y="28" textAnchor="end">
          {yMin}
        </text>
        <text x="47" y={height + 20} textAnchor="end">
          {yMax}
        </text>
        <text transform={`translate(15 ${height / 2 + 20}) rotate(-90)`} textAnchor="middle">
          {yLabel}
        </text>
        {point && (
          <circle
            data-nlos-point
            cx={55 + (point.x / 127) * 225}
            cy={20 + (point.y / 127) * height}
            r="6"
            stroke="#fff"
            strokeWidth="2"
            fill="#b9521e"
          />
        )}
      </svg>
      <figcaption>{label}</figcaption>
    </figure>
  );
}
function Stolt({ index }: { index: number }) {
  const p = data.stolt.probes[index];
  const path = Array.from({ length: 101 }, (_, i) => {
    const z = i / 100;
    const f = Math.sqrt(data.stolt.scale ** 2 * 0.25 + z * z);
    return `${i ? 'L' : 'M'}${45 + z * 360},${255 - f * 215}`;
  }).join(' ');
  return (
    <div className={css.two}>
      <svg
        className={css.stolt}
        viewBox="0 0 455 310"
        role="img"
        aria-label="Stolt mapping from target depth frequency to sampled temporal frequency"
      >
        <rect x="45" y="20" width="360" height="235" fill="#fff" />
        {[0, 0.5, 1].map((v) => (
          <g key={v}>
            <line x1="45" x2="405" y1={255 - v * 215} y2={255 - v * 215} stroke="#d8e0d7" />
            <text x="37" y={259 - v * 215} textAnchor="end">
              {v}
            </text>
            <text x={45 + v * 360} y="275" textAnchor="middle">
              {v}
            </text>
          </g>
        ))}
        <path d={path} stroke="#264b43" fill="none" strokeWidth="2.5" />
        <line
          x1={45 + p.kz * 360}
          x2={45 + p.kz * 360}
          y1="255"
          y2={255 - p.sample_kf * 215}
          stroke="#b9521e"
          strokeDasharray="4 3"
        />
        <circle
          data-nlos-stolt-probe={index}
          cx={45 + p.kz * 360}
          cy={255 - p.sample_kf * 215}
          r="6"
          fill="#b9521e"
        />
        <text x="45" y="14">
          Sampled temporal frequency k_f
        </text>
        <text x="225" y="299" textAnchor="middle">
          Target depth frequency k_z · normalized
        </text>
      </svg>
      <div className={css.card}>
        <small>ONE OPERATOR SAMPLE · NOT A SOLVE</small>
        <h4>k_f = √(s²(k_x² + k_y²) + k_z²)</h4>
        <p>s = 0.3072 · k_x = 0.5 · k_y = 0</p>
        <dl>
          <dt>Target k_z</dt>
          <dd>{p.kz.toFixed(2)}</dd>
          <dt>Sample k_f</dt>
          <dd>{p.sample_kf.toFixed(6)}</dd>
          <dt>Array index</dt>
          <dd>{p.sample_index.toFixed(3)}</dd>
          <dt>Jacobian k_z/k_f</dt>
          <dd>{p.weight.toFixed(6)}</dd>
        </dl>
        <p className={css.note}>
          Linear interpolation of real and imaginary FFT values; zero outside the grid. Keep k_z
          &gt; 0.
        </p>
      </div>
    </div>
  );
}
export function NlosScene({ state: s }: { state: NlosState }) {
  const index = nlosIndex(s),
    h = input.histograms[index],
    reveal = nlosReveal(s),
    v = data.views[index];
  let body;
  switch (s.scene) {
    case 'inputs':
      body = (
        <div className={css.two}>
          <div>
            <Plane image={input.wall} label="Relay-wall map · sum over all time bins" point={h} />
            <p className={css.scale}>
              0 <span /> {input.wall.maximum} counts · sqrt display
            </p>
          </div>
          <div className={css.card}>
            <small>PUBLISHED OUTDOOR MEASUREMENTS</small>
            <h4>128 × 128 scan points × 2048 times</h4>
            <p>2 m × 2 m relay wall · 32 ps bins</p>
            <p>
              Confocal path: wall → hidden scene → same wall point. Arrival time constrains
              round-trip distance.
            </p>
            <Histogram values={h.raw} />
            <p>
              Selected (y,x) = ({h.y},{h.x}) · orange marker
            </p>
            <p className={css.note}>
              The wall map is measured counts, not a photograph of the hidden object.
              Source-attributed 10 minute exposure.
            </p>
          </div>
        </div>
      );
      break;
    case 'alignment':
      body = (
        <>
          <div className={css.two}>
            <div>
              <Histogram values={h.raw} />
              <Histogram values={h.aligned} cropped />
            </div>
            <div className={css.card}>
              <small>
                EXACT SELECTED HISTOGRAM · ({h.y},{h.x})
              </small>
              <h4>Shift {h.shift_bins} bins</h4>
              <p>
                −floor({h.tof_ps} ps / 32 ps) = {h.shift_bins}
              </p>
              <p>Circular roll → keep bins 0–511 → move time to the first axis.</p>
              <pre>
                (128,128,2048)
                <br />→ (512,128,128)
              </pre>
              <p>512 bins span 16.384 ns. Source displayed depth axis: 0–2.4576 m.</p>
            </div>
          </div>
          <p className={css.key}>
            <i />
            Raw counts · dark green <i className={css.orange} />
            Aligned counts · orange
          </p>
        </>
      );
      break;
    case 'stolt':
      body = (
        <>
          <p className={css.flow}>
            √(|counts|·normalized time²) → pad 2× → FFT → Stolt map → inverse FFT → |·|²
          </p>
          <Stolt index={index} />
          <p>
            Full padded shape: 1024 × 256 × 256. Only the published 16 × 8 × 8 operator fixture was
            executed.
          </p>
        </>
      );
      break;
    case 'output':
      body = (
        <div className={css.two}>
          <Plane
            image={v.image}
            label={v.label}
            xLabel={v.axes[0]}
            yLabel={v.axes[1]}
            yMin={v.ranges[1][0]}
            yMax={v.ranges[1][1]}
          />
          <div className={css.card}>
            <small>SAVED SOURCE OUTPUT · NO FRESH RECONSTRUCTION</small>
            <h4>512 × 128 × 128 float32</h4>
            <p>Axis order: depth, y, x. Each panel collapses one stated axis by a maximum.</p>
            <p>
              Display: square root of intensity divided by the global maximum, then 8-bit color.
              Native pixels retained.
            </p>
            <p className={css.scale}>
              0 <span /> 2.394456 · relative intensity
            </p>
            <p className={css.note}>
              The largest value is at depth index 511, the last plane. This does not establish
              object-depth accuracy.
            </p>
          </div>
        </div>
      );
      break;
    case 'reference':
      body = (
        <div className={css.two}>
          <Plane image={data.views[0].image} label="Saved output · front maximum" />
          {reveal ? (
            <div data-nlos-reference>
              <Plane
                image={ref.front}
                label="Baseline reference · identical front maximum"
                baseline
              />
              <p>
                All 8,388,608 values equal the saved output. This is not independent scene ground
                truth.
              </p>
            </div>
          ) : (
            <div className={css.card}>
              <small>READER REFERENCE HIDDEN</small>
              <h4>Compare after the reveal</h4>
              <p>Playback reveals the baseline halfway through this chapter.</p>
              <p className={css.note}>
                The released L1–L3 data packet already includes this baseline file.
              </p>
            </div>
          )}
        </div>
      );
      break;
    case 'staging':
      body = (
        <>
          <div className={css.three}>
            {['L1', 'L2', 'L3'].map((level, i) => (
              <div
                key={level}
                className={`${css.card} ${i === index ? css.active : ''}`}
                data-nlos-level={i === index ? level : undefined}
              >
                <h4>{level}</h4>
                <p>README + requirements + data/</p>
                <p>{i > 0 ? '+ approach.md' : 'Choose an approach'}</p>
                <p>{i > 1 ? '+ design.md' : 'Implementation still required'}</p>
                <p className={css.note}>baseline_reference.npz copied</p>
              </div>
            ))}
          </div>
          <p className={css.flow}>
            Selected LocalRunner.start reproduced file copies; all installation commands
            intercepted.
          </p>
          <p>
            src/ and evaluation/ are not seeded. Docker source mounts the whole task read-only;
            read-only access does not make references private.
          </p>
        </>
      );
      break;
    case 'scoring':
      body = (
        <>
          <table className={css.table}>
            <thead>
              <tr>
                <th>Generic local scorer</th>
                <th>NCC</th>
                <th>NRMSE</th>
                <th>Meaning</th>
              </tr>
            </thead>
            <tbody>
              {[
                ['Saved volume', '1.000000', '0.000000', 'Identical stored arrays'],
                ['Baseline-copy control', '1.000000', '0.000000', 'Visible reference copied'],
                ['Half-amplitude control', '1.000000', '0.020574', 'Scale affects NRMSE'],
              ].map((row, i) => (
                <tr key={row[0]} className={i === index ? css.active : ''}>
                  {row.map((c) => (
                    <td key={c}>{c}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          <div className={css.two}>
            <div className={css.card}>
              <h4>A volume is required</h4>
              <p>output/reconstruction.npy · (512,128,128)</p>
              <p>A 128 × 128 maximum projection fails shape matching.</p>
            </div>
            <div className={css.card}>
              <h4>Pass status: unavailable</h4>
              <p>
                Shipped metrics contain no boundary keys. Source main.py would write 0.9 / 0.1
                thresholds; it was not executed.
              </p>
            </div>
          </div>
          <p className={css.note}>
            Native main.py max-normalizes each volume: half amplitude then has NCC 1 and NRMSE 0.
            Active generic scoring retains amplitude.
          </p>
        </>
      );
      break;
    case 'limits':
      body = (
        <>
          <div className={css.two}>
            <div className={css.card}>
              <h4>Established by this review</h4>
              <p>
                Exact measurements, three calibration examples, bounded operator fixture, saved
                volume and scorer behavior.
              </p>
              <p>Original array bytes and historical metrics retained.</p>
            </div>
            <div className={css.card}>
              <h4>Still unestablished</h4>
              <p>
                Fresh agent reconstruction, independent ground truth, hidden-reference evaluation,
                benchmark pass or general scene accuracy.
              </p>
              <p>Original MAT-to-NPZ conversion lineage is not supplied.</p>
            </div>
          </div>
          <p className={css.note}>
            Original MATLAB swaps lateral axes and removes its last 11 depth planes. The Python
            adaptation retains the last plane. Original-author byte equivalence is unverified.
          </p>
          <p>
            Data and derived views retain Stanford academic/non-commercial terms. No full-size
            inversion, model run or runtime installation.
          </p>
        </>
      );
      break;
  }
  return (
    <section className={css.scene} data-nlos-scene={s.scene} data-nlos-reveal={reveal}>
      <h3>{titles[s.scene]}</h3>
      {body}
    </section>
  );
}
export function NlosOutput({ state: s }: { state: NlosState }) {
  return (
    <aside className={css.aside} data-nlos-aside>
      <b>{s.scene === 'scoring' ? 'SCORING CONTRACT' : 'SOURCE-BACKED WALKTHROUGH'}</b>
      <p>
        Published confocal measurements and a saved f-k volume. Reader reference appears only after
        reveal.
      </p>
      <p>One source case. Small operator fixture only; no fresh full-size inverse.</p>
      <small>
        Imaging101 dc2f668…
        <br />
        Stanford academic/non-commercial data
        <br />m · ns · photon counts
      </small>
    </aside>
  );
}

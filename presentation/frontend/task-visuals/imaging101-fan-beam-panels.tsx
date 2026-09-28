import {
  fanBeamInput as input,
  fanBeamData as data,
  fanBeamReference as ref,
  fanBeamIndex,
  fanBeamReveal,
  type FanBeamState,
  type FanBeamImage,
} from './imaging101-fan-beam';
import css from './imaging101-fan-beam.module.css';
const green = '#264b43',
  orange = '#b9521e',
  purple = '#8052a1';
const titles = {
  inputs: 'Two scans sample the same synthetic phantom',
  geometry: 'Magnification moves a pixel between detector bins',
  weights: 'Inspect the released short-scan weights',
  output: 'Three saved images, one display scale',
  reference: 'Reveal truth, then inspect the native scoring crop',
  scoring: 'Normalization changes which errors the score sees',
  staging: 'Every assistance packet contains the phantom',
  limits: 'A saved result does not prove the solver guarantees',
};
function Scale({ low = '0', high, unit }: { low?: string; high: string; unit: string }) {
  return (
    <div className={css.scale}>
      <span>{low}</span>
      <i />
      <span>
        {high} {unit}
      </span>
      <span>linear · 8-bit display</span>
    </div>
  );
}
function Plane({
  image,
  label,
  truth = false,
  row,
  column,
  crop = false,
  normalized = false,
}: {
  image: FanBeamImage;
  label: string;
  truth?: boolean;
  row?: number;
  column?: number;
  crop?: boolean;
  normalized?: boolean;
}) {
  const sino = image.shape[1] === 192,
    x = sino ? 48 : 70,
    width = sino ? 252 : 180;
  return (
    <figure
      className={css.plane}
      data-fan-beam-plane={truth ? 'truth' : 'saved-or-input'}
      data-fan-beam-reference={truth ? 'truth' : undefined}
    >
      <svg viewBox="0 0 325 260" role="img" aria-label={label}>
        <image
          href={image.data}
          x={x}
          y="20"
          width={width}
          height="180"
          preserveAspectRatio="none"
        />
        <rect
          x={x}
          y="20"
          width={width}
          height="180"
          fill="none"
          stroke={truth ? purple : green}
          strokeWidth="2"
          strokeDasharray={truth ? '6 4' : undefined}
        />
        {row !== undefined && (
          <line
            data-fan-beam-row
            x1={x}
            x2={x + width}
            y1={20 + ((row + 0.5) / image.shape[0]) * 180}
            y2={20 + ((row + 0.5) / image.shape[0]) * 180}
            stroke={orange}
            strokeWidth="2"
          />
        )}
        {column !== undefined && (
          <line
            data-fan-beam-column
            x1={x + ((column + 0.5) / image.shape[1]) * width}
            x2={x + ((column + 0.5) / image.shape[1]) * width}
            y1="20"
            y2="200"
            stroke={orange}
            strokeWidth="2"
          />
        )}
        {crop && (
          <rect
            data-fan-beam-crop
            x={x + (12 / 128) * width}
            y={20 + (12 / 128) * 180}
            width={(104 / 128) * width}
            height={(104 / 128) * 180}
            fill="none"
            stroke={orange}
            strokeWidth="2"
            strokeDasharray="3 3"
          />
        )}
        <text x={x} y="218">
          {normalized ? 12 : 0}
        </text>
        <text x={x + width} y="218" textAnchor="end">
          {normalized ? 115 : image.shape[1] - 1}
        </text>
        <text x={x + width / 2} y="236" textAnchor="middle">
          {sino ? 'detector bin' : 'column / pixel center'}
        </text>
        <text x={x - 8} y="25" textAnchor="end">
          {normalized ? 12 : 0}
        </text>
        <text x={x - 8} y="200" textAnchor="end">
          {normalized ? 115 : image.shape[0] - 1}
        </text>
        <text transform={`translate(${x - 35} 110) rotate(-90)`} textAnchor="middle">
          {sino ? 'source angle index' : 'row / pixel center'}
        </text>
        <text x={x + width / 2} y="254" textAnchor="middle">
          {sino
            ? `${image.shape[0]} angle rows × 192 bins`
            : normalized
              ? '104 × 104 native crop pixels'
              : '128 × 128 pixels · no mm calibration'}
        </text>
      </svg>
      <figcaption>{label}</figcaption>
    </figure>
  );
}
function Geometry({ index }: { index: number }) {
  const c = data.pixel_controls[index],
    beta = (c.angle_degrees * Math.PI) / 180;
  const source = [-256 * Math.sin(beta), 256 * Math.cos(beta)],
    center = [-source[0], -source[1]],
    axis = [Math.cos(beta), Math.sin(beta)];
  const detector = (t: number) => [center[0] + t * axis[0], center[1] + t * axis[1]];
  const xy = (p: number[]) => [200 + p[0] * 0.47, 152 + p[1] * 0.47];
  const s = xy(source),
    a = xy(detector(-128)),
    b = xy(detector(128)),
    point = xy([c.column - 63.5, c.row - 63.5]),
    hit = xy(detector(c.detector_coordinate));
  return (
    <svg
      className={css.geometry}
      viewBox="0 0 400 306"
      role="img"
      aria-label={`Pixel diagnostic at source angle ${c.angle_degrees} degrees; row coordinates increase down`}
    >
      <circle cx="200" cy="152" r={256 * 0.47} stroke="#c6d1c6" strokeDasharray="3 3" fill="none" />
      <rect
        x={200 - 64 * 0.47}
        y={152 - 64 * 0.47}
        width={128 * 0.47}
        height={128 * 0.47}
        fill="#e1e8df"
        stroke={green}
      />
      <line x1="168" x2="232" y1="152" y2="152" stroke="#abbcaf" />
      <line x1="200" x2="200" y1="120" y2="184" stroke="#abbcaf" />
      {[-128, 0, 128].map((t) => {
        const d = xy(detector(t));
        return (
          <line
            key={t}
            x1={s[0]}
            y1={s[1]}
            x2={d[0]}
            y2={d[1]}
            stroke="#9baea1"
            strokeWidth="1.2"
          />
        );
      })}
      <line
        data-fan-beam-detector
        x1={a[0]}
        y1={a[1]}
        x2={b[0]}
        y2={b[1]}
        stroke={green}
        strokeWidth="5"
      />
      <line
        data-fan-beam-ray
        x1={s[0]}
        y1={s[1]}
        x2={hit[0]}
        y2={hit[1]}
        stroke={orange}
        strokeWidth="2"
      />
      <circle data-fan-beam-source cx={s[0]} cy={s[1]} r="6" fill={orange} />
      <circle cx={point[0]} cy={point[1]} r="4" fill="#fff" stroke={orange} strokeWidth="2" />
      <circle cx={hit[0]} cy={hit[1]} r="4" fill={orange} />
      <text x="8" y="14">
        Source angle β = {c.angle_degrees}°
      </text>
      <text x="8" y="298">
        x / column → · y / row ↓ · geometry diagram
      </text>
      <text x="8" y="32">
        Field: 128 px
      </text>
      <text x="8" y="48">
        Center: (0, 0)
      </text>
    </svg>
  );
}
function WeightPlot({ index }: { index: number }) {
  const curves = data.weight_curves.selected_curves,
    colors = [green, orange, '#627788'],
    dash = [undefined, '6 4', '2 3'];
  return (
    <div>
      <svg
        className={css.plot}
        viewBox="0 0 370 255"
        role="img"
        aria-label="Released Parker weight versus source angle for three detector bins"
      >
        <text x="50" y="17">
          released weight
        </text>
        {[0, 0.5, 1].map((v) => (
          <g key={v}>
            <line x1="50" x2="345" y1={205 - v * 175} y2={205 - v * 175} stroke="#d5ddd4" />
            <text x="42" y={209 - v * 175} textAnchor="end">
              {v}
            </text>
          </g>
        ))}
        {curves.map((c, j) => (
          <path
            key={j}
            data-fan-beam-weight-curve={j}
            d={c
              .map(
                (v, i) =>
                  `${i ? 'L' : 'M'}${50 + (data.weight_curves.angles_degrees[i] / 233) * 295},${205 - v * 175}`,
              )
              .join(' ')}
            stroke={colors[j]}
            strokeWidth={index === j ? 3 : 1.5}
            strokeDasharray={dash[j]}
            fill="none"
          />
        ))}
        {[0, 90, 180, 233].map((v) => (
          <text key={v} x={50 + (v / 233) * 295} y="224" textAnchor="middle">
            {v}
          </text>
        ))}
        <text x="198" y="245" textAnchor="middle">
          source angle / degrees
        </text>
      </svg>
      <div className={css.curveLegend}>
        {data.weight_curves.selected_detector_bins.map((bin, j) => (
          <span key={bin} style={{ color: colors[j] }}>
            {['━', '┄', '┈'][j]} bin {bin}
          </span>
        ))}
      </div>
    </div>
  );
}
function LossPlot({ progress }: { progress: number }) {
  const index = Math.min(149, Math.floor(progress * 149)),
    x = (i: number) => 58 + (i / 149) * 285,
    y = (v: number) => 210 - (v / 2_000_000) * 170;
  return (
    <svg
      className={css.plot}
      viewBox="0 0 370 260"
      role="img"
      aria-label="All 150 saved data-fidelity values, including increases; no new solver run"
    >
      <text x="58" y="17">
        saved data fidelity · linear
      </text>
      {[0, 1_000_000, 2_000_000].map((v) => (
        <g key={v}>
          <line x1="58" x2="343" y1={y(v)} y2={y(v)} stroke="#d5ddd4" />
          <text x="50" y={y(v) + 4} textAnchor="end">
            {v ? `${v / 1e6}M` : 0}
          </text>
        </g>
      ))}
      <path
        d={data.loss.values.map((v, i) => `${i ? 'L' : 'M'}${x(i)},${y(v)}`).join(' ')}
        fill="none"
        stroke={green}
        strokeWidth="2"
      />
      <circle
        cx={x(index)}
        cy={y(data.loss.values[index])}
        r="4"
        fill={orange}
        data-fan-beam-loss-cursor
      />
      {[1, 50, 100, 150].map((v) => (
        <text key={v} x={x(v - 1)} y="230" textAnchor="middle">
          {v}
        </text>
      ))}
      <text x="200" y="251" textAnchor="middle">
        recorded iteration · excludes TV penalty
      </text>
    </svg>
  );
}
export function FanBeamScene({ state: s }: { state: FanBeamState }) {
  const index = fanBeamIndex(s),
    reveal = fanBeamReveal(s);
  let body;
  switch (s.scene) {
    case 'inputs':
      body = (
        <>
          <div className={css.two}>
            {input.sinograms.map((im, j) => {
              const angles = input.angles_degrees[j],
                row = Math.round([0, 90, 180][index] / angles[1]);
              return (
                <Plane
                  key={j}
                  image={im}
                  row={row}
                  label={`${j ? 'Short' : 'Full'} scan · selected row ${row}, β = ${angles[row].toFixed(2)}°`}
                />
              );
            })}
          </div>
          <Scale low="−5" high="55" unit="saved projection units" />
          <p className={css.flow}>
            <b>360° / 180 views</b> and <b>232.891° / 116 views</b>. Different angle spacing; both
            exclude the final angle.
          </p>
          <p>
            Gaussian noise can give negative values. One simulated phantom; values are not photon
            counts or HU.
          </p>
        </>
      );
      break;
    case 'geometry': {
      const c = data.pixel_controls[index];
      body = (
        <>
          <div className={css.two}>
            <Geometry index={index} />
            <div className={css.card}>
              <small>FIXED UNIT-PIXEL CONTROL {index + 1} / 3</small>
              <h4>
                Row {c.row}, column {c.column}
              </h4>
              <p>
                Source: orange dot · detector: green bar.
                <br />
                Orange ray passes through the selected pixel.
              </p>
              <dl>
                <dt>U = 256 − s</dt>
                <dd>{c.U.toFixed(1)} px</dd>
                <dt>Magnification = 512 / U</dt>
                <dd>{c.magnification.toFixed(4)}</dd>
                <dt>Detector coordinate</dt>
                <dd>{c.detector_coordinate.toFixed(3)} px</dd>
                <dt>Neighbor bins</dt>
                <dd>{c.bins.join(' / ')}</dd>
                <dt>Contributions</dt>
                <dd>{c.weights.map((v) => v.toFixed(4)).join(' / ')}</dd>
              </dl>
            </div>
          </div>
          <p className={css.flow}>
            Rotate coordinates → divide by source distance → distribute to two detector bins.
          </p>
          <p>
            No anatomical image is implied by the square. Pixel coordinates have no mm calibration
            or patient orientation.
          </p>
        </>
      );
      break;
    }
    case 'weights':
      body = (
        <>
          <div className={css.two}>
            <Plane
              image={data.weights}
              column={data.weight_curves.selected_detector_bins[index]}
              label="Released Parker weights · short scan"
            />
            <WeightPlot index={index} />
          </div>
          <Scale high="1" unit="weight · dimensionless" />
          <p className={css.note}>
            Source uses half-fan <b>26.446°</b> from detector position / 256. The 512 px
            source–detector geometry gives <b>13.966°</b>.
          </p>
          <p>
            Original sweep and weights are preserved. They are followed by preweighting, filtering
            and distance-weighted backprojection.
          </p>
        </>
      );
      break;
    case 'output':
      body = (
        <>
          <div className={css.two}>
            <Plane image={data.maps[index]} label={`Saved ${data.names[index]}`} />
            <div className={css.card}>
              <small>SAVED IMAGE {index + 1} / 3</small>
              <h4>{data.names[index]}</h4>
              <p>
                {index < 2
                  ? 'Saved noisy measurements → source Hann filter (cutoff 0.3) → backprojection → nonnegative clipping.'
                  : 'Released final image from the TV-labelled routine. Its 150 recorded losses do not supply intermediate images.'}
              </p>
              <p className={css.flow}>
                {index < 2
                  ? 'Both FBP outputs replay exactly after float32 conversion.'
                  : 'Saved image only. No iterative solver or agent was run.'}
              </p>
              <p>
                The full and short FBP scans use different angle sampling. This is one synthetic
                case.
              </p>
            </div>
          </div>
          <Scale high="1.6" unit="relative attenuation · all three saved maps" />
          <p>
            Switches select actual saved arrays; they do not animate an invented reconstruction
            trajectory.
          </p>
        </>
      );
      break;
    case 'reference': {
      const normalized = reveal && s.view > 0.8;
      body = (
        <>
          <div className={css.two}>
            <Plane
              image={normalized ? data.normalized_maps[2] : data.maps[2]}
              label={
                normalized
                  ? 'Saved TV-labelled crop · independently normalized'
                  : 'Saved TV-labelled map · orange metric crop'
              }
              crop={!normalized}
              normalized={normalized}
            />
            {reveal ? (
              <Plane
                image={normalized ? ref.normalized_map : ref.map}
                label={
                  normalized
                    ? 'Synthetic truth crop · independently normalized'
                    : 'Synthetic truth · orange metric crop'
                }
                truth
                crop={!normalized}
                normalized={normalized}
              />
            ) : (
              <div className={css.card}>
                <small>REFERENCE HIDDEN</small>
                <h4>Reveal at the chapter midpoint</h4>
                <p>
                  Dashed orange square: 12 pixels removed from each edge. This marks a metric crop,
                  not segmentation.
                </p>
                <p>
                  After revealing truth, switch both panels to their actual 104 × 104 normalized
                  crops.
                </p>
              </div>
            )}
          </div>
          <Scale
            high={normalized ? '1' : '1.6'}
            unit={
              normalized ? 'per-image normalized crop' : 'relative attenuation · matched raw scale'
            }
          />
          <p className={css.note}>
            Native score: <b>10,816 / 16,384 pixels</b>, each crop separately normalized. Dashed
            purple: synthetic truth.
          </p>
          <p>Reader reveal is not solver privacy: L1–L3 already include the phantom.</p>
        </>
      );
      break;
    }
    case 'scoring': {
      const key = ['half-truth', 'truth-plus-one', 'outside-crop-plus-ten'][index],
        label = ['Half-strength truth', 'Truth plus one', 'Add 10 outside crop'][index];
      body = (
        <>
          <table className={css.table}>
            <thead>
              <tr>
                <th>Saved result</th>
                <th>Native NCC / NRMSE</th>
                <th>Generic NCC / NRMSE</th>
              </tr>
            </thead>
            <tbody>
              {data.keys.map((k, j) => (
                <tr key={k}>
                  <td>{data.names[j]}</td>
                  <td>
                    {data.native[k].ncc.toFixed(4)} / {data.native[k].nrmse.toFixed(4)}
                  </td>
                  <td>
                    {data.generic[k].ncc?.toFixed(4)} / {data.generic[k].nrmse?.toFixed(4)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className={css.two}>
            <div className={css.card}>
              <small>NATIVE</small>
              <h4>Crop, then normalize each image</h4>
              <p>104 × 104 center; cosine NCC and range-NRMSE.</p>
              <p>Notebook values reproduce to four decimals.</p>
            </div>
            <div className={css.card}>
              <small>CONSTRUCTED CONTROL</small>
              <h4>{label}</h4>
              <p>
                Native: NCC <b>{data.native[key].ncc.toFixed(4)}</b> · NRMSE{' '}
                <b>{data.native[key].nrmse.toFixed(4)}</b>
              </p>
              <p>
                Generic full image: NRMSE <b>{data.generic[key].nrmse?.toFixed(4)}</b>
              </p>
            </div>
          </div>
          <p className={css.note}>
            Historical notebook boundaries are printed, but no metrics.json is shipped. Current
            generic scoring supplies no pass/fail.
          </p>
        </>
      );
      break;
    }
    case 'staging':
      body = (
        <>
          <div className={css.three}>
            {['L1', 'L2', 'L3'].map((level, j) => (
              <div key={level} className={`${css.card} ${index === j ? css.active : ''}`}>
                <small>{level}</small>
                <h4>{['README', '+ approach', '+ design'][j]}</h4>
                <p>Measurements + metadata</p>
                <p className={css.note}>
                  <b>ground_truth.npz</b>
                  <br />
                  Complete synthetic phantom
                </p>
                <p>
                  {j ? 'plan/approach.md' : 'Choose the method'}
                  {j === 2 && (
                    <>
                      <br />
                      plan/design.md
                    </>
                  )}
                </p>
              </div>
            ))}
          </div>
          <p className={css.flow}>
            Actual file seeding replayed with every installation command intercepted. Source and
            evaluation directories are not seeded.
          </p>
          <p>
            Generic submission: <code>output/reconstruction.npy</code>, one 128 × 128 image. Native
            NPZ, stacked images and loss-only vectors fail the active contract.
          </p>
          <p>Truth copying can score perfectly; it does not demonstrate reconstruction.</p>
        </>
      );
      break;
    case 'limits':
      body = (
        <>
          <div className={css.two}>
            <LossPlot progress={s.view} />
            <div className={css.card}>
              <small>FIXED OPERATOR CONTROLS</small>
              <h4>Descriptions have limits</h4>
              <p>
                Euclidean adjoint check:{' '}
                <b>
                  {data.adjoint.inner_Ax_y.toFixed(2)} ≠ {data.adjoint.inner_x_By.toFixed(2)}
                </b>
                .
              </p>
              <p>
                Declared radius 0.005 projection returns vector (3, 4), norm <b>5</b>.
              </p>
              <p>These controls qualify source claims; saved images and scores remain unchanged.</p>
            </div>
          </div>
          <p className={css.note}>
            Saved losses include <b>66 / 149 increases</b>. No fresh TV solve, agent capability,
            hidden-reference validity, current pass or patient accuracy.
          </p>
          <p>
            Benchmark MIT and cited upstream GPL text remain separate; the other cited upstream tree
            has no license file.
          </p>
        </>
      );
      break;
  }
  return (
    <section className={css.scene} data-fan-beam-scene={s.scene}>
      <h3>{titles[s.scene]}</h3>
      {body}
    </section>
  );
}
export function FanBeamOutput({ state: s }: { state: FanBeamState }) {
  return (
    <aside className={css.aside} data-fan-beam-aside>
      <b>{s.scene === 'scoring' ? 'SCORE SCOPE MATTERS' : 'SOURCE-BACKED WALKTHROUGH'}</b>
      <p>One synthetic phantom, two scans and three saved images.</p>
      <p>Truth appears after reader reveal. Released solver packets already include it.</p>
      <small>
        Imaging101 dc2f668…
        <br />
        Pixel coordinates · no HU
        <br />
        No new iterative reconstruction
      </small>
    </aside>
  );
}

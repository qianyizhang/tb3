import {
  dualEnergyInput as input,
  dualEnergyData as data,
  dualEnergyReference as ref,
  dualEnergyIndex,
  dualEnergyReveal,
  dualEnergyRayPixel,
  type DualEnergyState,
  type DualEnergyImage,
} from './imaging101-dual-energy';
import css from './imaging101-dual-energy.module.css';
const green = '#264b43',
  orange = '#b9521e';
const titles = {
  inputs: 'Two spectra measure the same synthetic phantom',
  calibration: 'Keep spectra and material attenuation separate',
  forward: 'Predict counts from a saved pair of material integrals',
  output: 'Backproject each saved material sinogram',
  reference: 'Reveal both synthetic truth maps on matched scales',
  staging: 'Every assistance level receives the truth archive',
  scoring: 'Array shape changes what the generic scorer evaluates',
  limits: 'A saved two-material result with explicit limits',
};
function Scale({ high, unit }: { high: string; unit: string }) {
  return (
    <div className={css.scale}>
      <span>0</span>
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
  ray,
}: {
  image: DualEnergyImage;
  label: string;
  truth?: boolean;
  ray?: number;
}) {
  const sino = image.shape[1] === 180,
    x = sino ? 48 : 70,
    width = sino ? 252 : 180;
  const point =
    ray === undefined
      ? null
      : dualEnergyRayPixel(data.rays[ray].detector_bin, data.rays[ray].angle_degrees);
  return (
    <figure
      className={css.plane}
      data-dual-energy-plane={truth ? 'truth' : 'saved-or-input'}
      data-dual-energy-reference={truth ? 'truth' : undefined}
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
          stroke={truth ? '#8052a1' : green}
          strokeWidth="2"
          strokeDasharray={truth ? '6 4' : undefined}
        />
        {point && (
          <circle
            data-dual-energy-ray
            cx={point.x}
            cy={point.y}
            r="6"
            stroke={orange}
            strokeWidth="2.5"
            fill="none"
          />
        )}
        <text x={x + width / image.shape[1] / 2} y="218">
          0
        </text>
        <text x={x + width - width / image.shape[1] / 2} y="218" textAnchor="end">
          {image.shape[1] - 1}
        </text>
        <text x={x + width / 2} y="236" textAnchor="middle">
          {sino ? 'projection angle / degrees' : 'column / pixel center'}
        </text>
        <text x={x - 8} y="25" textAnchor="end">
          0
        </text>
        <text x={x - 8} y="200" textAnchor="end">
          127
        </text>
        <text transform={`translate(${x - 35} 110) rotate(-90)`} textAnchor="middle">
          {sino ? 'detector bin' : 'row / pixel center'}
        </text>
        <text x={x + width / 2} y="254" textAnchor="middle">
          {sino ? '128 bins × 180 angles' : '1 mm pixels · 128 mm field'}
        </text>
      </svg>
      <figcaption>{label}</figcaption>
    </figure>
  );
}
function Plot({
  curves,
  labels,
  max,
  ticks,
  unit,
  index,
}: {
  curves: number[][];
  labels: string[];
  max: number;
  ticks: number[];
  unit: string;
  index?: number;
}) {
  const x = (i: number) => 55 + (i / 130) * 290,
    y = (v: number) => 205 - (v / max) * 170;
  return (
    <svg
      className={css.plot}
      viewBox="0 0 370 265"
      role="img"
      aria-label={unit + ': ' + labels.join(', ')}
    >
      <text x="55" y="17">
        {unit}
      </text>
      {ticks.map((v) => (
        <g key={v}>
          <line x1="55" x2="345" y1={y(v)} y2={y(v)} stroke="#d5ddd4" />
          <text x="47" y={y(v) + 4} textAnchor="end">
            {v >= 1000 ? `${v / 1000}k` : v}
          </text>
        </g>
      ))}
      {curves.map((c, j) => (
        <path
          key={j}
          data-dual-energy-curve={labels[j]}
          d={c.map((v, i) => `${i ? 'L' : 'M'}${x(i)},${y(v)}`).join(' ')}
          fill="none"
          stroke={j ? orange : green}
          strokeWidth="2"
        />
      ))}
      {index !== undefined && (
        <line x1={x(index)} x2={x(index)} y1="35" y2="205" stroke="#6e8294" strokeDasharray="3 3" />
      )}
      {[20, 60, 100, 150].map((e) => (
        <text key={e} x={x(e - 20)} y="223" textAnchor="middle">
          {e}
        </text>
      ))}
      <text x="200" y="240" textAnchor="middle">
        energy / keV · 1 keV bins
      </text>
      {labels.map((l, j) => (
        <text key={l} x={55 + j * 158} y="260" style={{ fill: j ? orange : green }}>
          {j ? '━ ' : '━ '}
          {l}
        </text>
      ))}
    </svg>
  );
}
export function DualEnergyScene({ state: s }: { state: DualEnergyState }) {
  const index = dualEnergyIndex(s),
    ray = data.rays[index],
    reveal = dualEnergyReveal(s);
  let body;
  switch (s.scene) {
    case 'inputs':
      body = (
        <>
          <div className={css.two}>
            {input.counts.map((im, j) => (
              <Plane
                key={j}
                image={im}
                label={j ? 'High-energy photon counts' : 'Low-energy photon counts'}
                ray={index}
              />
            ))}
          </div>
          <Scale high="1,600,000" unit="photons / ray" />
          <p className={css.flow}>
            Orange ring: detector {ray.detector_bin}, angle {ray.angle_degrees}°. Observed low /
            high: <b>{ray.observed_counts.map((v) => v.toLocaleString('en-US')).join(' / ')}</b>.
          </p>
          <p>
            One synthetic parallel-beam case. Each spectrum supplies 23,040 count measurements;
            these are not HU.
          </p>
        </>
      );
      break;
    case 'calibration': {
      const ei = [0, 40, 100][index];
      body = (
        <>
          <div className={css.two}>
            <Plot
              curves={input.spectra}
              labels={['low energy', 'high energy']}
              max={40000}
              ticks={[0, 10000, 20000, 30000, 40000]}
              unit="incident photons / bin"
              index={ei}
            />
            <Plot
              curves={input.mus}
              labels={['tissue', 'bone']}
              max={3.5}
              ticks={[0, 1, 2, 3]}
              unit="mass attenuation / cm² g⁻¹"
              index={ei}
            />
          </div>
          <p className={css.flow}>
            At {input.energies[ei]} keV: tissue μ/ρ = <b>{input.mus[0][ei].toFixed(3)}</b>; bone ={' '}
            <b>{input.mus[1][ei].toFixed(3)}</b> cm²/g.
          </p>
          <p className={css.note}>
            Released coefficients are approximate. At 20 keV NIST lists 0.823 / 4.001; this task
            uses 0.770 / 3.200. Calibration is retained unchanged.
          </p>
        </>
      );
      break;
    }
    case 'forward':
      body = (
        <>
          <div className={css.flow}>
            νₛ = Σₑ Sₛ(E) exp[−aₜ μₜ(E) − aᵦ μᵦ(E)] · ΔE, with ΔE = 1 keV
          </div>
          <div className={css.two}>
            <Plot
              curves={ray.count_contributions_by_energy}
              labels={['low contribution', 'high contribution']}
              max={20000}
              ticks={[0, 5000, 10000, 15000, 20000]}
              unit="transmitted photons / bin"
            />
            <div className={css.card}>
              <small>
                SAVED RAY · DETECTOR {ray.detector_bin} · {ray.angle_degrees}°
              </small>
              <h4>Two integrals, two predicted counts</h4>
              <dl>
                <dt>Tissue aₜ / g cm⁻²</dt>
                <dd>{ray.saved_material_integrals_g_cm2[0].toFixed(4)}</dd>
                <dt>Bone aᵦ / g cm⁻²</dt>
                <dd>{ray.saved_material_integrals_g_cm2[1].toFixed(4)}</dd>
              </dl>
              <table className={css.table}>
                <thead>
                  <tr>
                    <th>Counts</th>
                    <th>Low</th>
                    <th>High</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Observed</td>
                    {ray.observed_counts.map((v, j) => (
                      <td key={j}>{v.toFixed(0)}</td>
                    ))}
                  </tr>
                  <tr>
                    <td>Predicted</td>
                    {ray.saved_predicted_counts.map((v, j) => (
                      <td key={j}>{v.toFixed(1)}</td>
                    ))}
                  </tr>
                </tbody>
              </table>
              <p>
                The inverse adjusts both nonnegative material integrals to fit the spectra jointly.
              </p>
              <p className={css.note}>
                This is a forward check at a saved estimate. No optimization step was run.
              </p>
            </div>
          </div>
        </>
      );
      break;
    case 'output': {
      const maps = dualEnergyIndex(s, 2) === 1;
      body = (
        <>
          <div className={css.two}>
            {(maps ? data.maps : data.sinograms).map((im, j) => (
              <Plane
                key={j}
                image={im}
                label={`Saved ${j ? 'bone' : 'tissue'} ${maps ? 'density map' : 'material sinogram'}`}
              />
            ))}
          </div>
          <Scale high={maps ? '1.6' : '11'} unit={maps ? 'g/cm³' : 'g/cm²'} />
          <p className={css.flow}>
            Material sinogram ÷ 0.1 cm → ramp-filtered backprojection → clip negative density to
            zero
          </p>
          <p>
            Both saved maps reproduce exactly from stored sinograms. This replay does not repeat
            material decomposition.
          </p>
        </>
      );
      break;
    }
    case 'reference': {
      const material = s.view > 0.75 ? 1 : 0;
      body = (
        <>
          <div className={css.two}>
            <Plane
              image={data.maps[material]}
              label={`Saved ${material ? 'bone' : 'tissue'} density`}
            />
            {reveal ? (
              <Plane
                image={ref.maps[material]}
                label={`Synthetic ${material ? 'bone' : 'tissue'} truth`}
                truth
              />
            ) : (
              <div className={css.card}>
                <small>REFERENCE HIDDEN</small>
                <h4>First tissue, then bone</h4>
                <p>
                  Playback reveals the truth halfway through this chapter, then switches material.
                </p>
                <p>Both comparisons use the same density scale and native pixel geometry.</p>
              </div>
            )}
          </div>
          <Scale high="1.6" unit="g/cm³ · both panels" />
          <p className={css.note}>
            Dashed purple: synthetic truth. The released L1–L3 packet already includes both truth
            maps.
          </p>
          {reveal && (
            <p data-dual-energy-reference-detail>
              Native {material ? 'bone' : 'tissue'} NCC / NRMSE:{' '}
              {material ? '0.9886 / 0.0404' : '0.9980 / 0.0620'} · 8,797 / 16,384 truth-body pixels.
            </p>
          )}
        </>
      );
      break;
    }
    case 'staging':
      body = (
        <>
          <div className={css.three}>
            {['L1', 'L2', 'L3'].map((level, j) => (
              <div
                key={level}
                className={`${css.card} ${j === index ? css.active : ''}`}
                data-dual-energy-level={level}
              >
                <h4>{level}</h4>
                <p>README + requirements + data/</p>
                <p>{j > 0 ? '+ approach.md' : 'Choose an approach'}</p>
                <p>{j > 1 ? '+ design.md' : 'Implementation still required'}</p>
                <p className={css.note}>
                  <b>ground_truth.npz is copied</b>
                  <br />
                  Tissue and bone maps
                  <br />
                  Tissue and bone sinograms
                </p>
              </div>
            ))}
          </div>
          <p className={css.flow}>
            Actual local file seeding replayed; all installation commands intercepted.
          </p>
          <p>
            Source and evaluation directories are not seeded. Reader-facing reveals do not imply
            solver-private truth.
          </p>
        </>
      );
      break;
    case 'scoring': {
      const rows = [
        ['truth-tissue-only', 'Tissue truth only', '128 × 128', 'tissue_map'],
        ['truth-bone-sinogram', 'Bone sinogram truth', '128 × 180', 'bone_sinogram'],
        ['two-truth-maps', 'Both truth maps', '2 × 128 × 128', 'No shape match'],
      ];
      const controls = [
        ['half-density', 'Half both true densities'],
        ['erased-bone', 'Erase the bone map'],
        ['outside-body-added', 'Add 10 outside truth body'],
      ];
      const [id, label] = controls[index],
        m = data.native[id];
      body = (
        <>
          <table className={css.table}>
            <thead>
              <tr>
                <th>Generic submission</th>
                <th>Shape</th>
                <th>Reference key</th>
                <th>NCC / MSE</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(([id, label, shape, key], j) => (
                <tr key={id} className={j === index ? css.active : ''} data-dual-energy-score={id}>
                  <td>{label}</td>
                  <td>{shape}</td>
                  <td>{key}</td>
                  <td>
                    {data.generic[id].error
                      ? 'Error'
                      : `${data.generic[id].ncc} / ${data.generic[id].mse}`}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className={css.two}>
            <div className={css.card}>
              <h4>Neither perfect row is the requested pair</h4>
              <p>
                Generic output: reconstruction.npy. Native reconstructed_maps.npz alone fails its
                filename check.
              </p>
              <p>No shipped metrics.json or pass thresholds.</p>
            </div>
            <div className={css.card}>
              <h4>Native control: {label}</h4>
              <p>
                Mean cosine NCC: <b>{m.mean_ncc.toFixed(4)}</b> · mean NRMSE:{' '}
                <b>{m.mean_nrmse.toFixed(4)}</b>.
              </p>
              <p>
                {index === 0
                  ? 'Cosine similarity ignores positive density scaling.'
                  : index === 1
                    ? 'Native metrics evaluate both named materials.'
                    : 'Outside-body changes are excluded by the native mask.'}
              </p>
            </div>
          </div>
        </>
      );
      break;
    }
    case 'limits':
      body = (
        <>
          <div className={css.two}>
            <div className={css.card}>
              <h4>Established</h4>
              <p>
                Exact measurements, calibration, both saved material maps, forward fixtures and
                actual scoring routes.
              </p>
              <p>
                Saved FBP replay: maximum error <b>0</b> for both maps. Native mean NCC{' '}
                <b>0.9933</b>; NRMSE <b>0.0512</b>.
              </p>
            </div>
            <div className={css.card}>
              <h4>Unestablished</h4>
              <p>
                Fresh material decomposition, agent capability, hidden-reference validity, benchmark
                pass or patient accuracy.
              </p>
              <p>
                The tiny inverse fixture could not be downloaded. No optimizer or runtime
                installation ran.
              </p>
            </div>
          </div>
          <p className={css.note}>
            One synthetic phantom with approximate calibration. Native body-masked two-material
            metrics and generic whole-array metrics answer different questions.
          </p>
          <p>
            Original benchmark and Giavanna Jadick MIT notices retained separately. The cited
            fan-beam simulator is not this parallel-beam implementation.
          </p>
        </>
      );
      break;
  }
  return (
    <section className={css.scene} data-dual-energy-scene={s.scene}>
      <h3>{titles[s.scene]}</h3>
      {body}
    </section>
  );
}
export function DualEnergyOutput({ state: s }: { state: DualEnergyState }) {
  return (
    <aside className={css.aside} data-dual-energy-aside>
      <b>{s.scene === 'scoring' ? 'TWO-MATERIAL CONTRACT' : 'SOURCE-BACKED WALKTHROUGH'}</b>
      <p>One synthetic dual-energy dataset and two saved density maps.</p>
      <p>Truth appears only after reader reveal. Released solver packets already include it.</p>
      <small>
        Imaging101 dc2f668…
        <br />
        counts · keV · g/cm² · g/cm³
        <br />
        No fresh material optimization
      </small>
    </aside>
  );
}

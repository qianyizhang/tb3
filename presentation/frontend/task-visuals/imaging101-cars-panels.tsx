import {
  carsInput as input,
  carsReference as ref,
  carsContract as data,
  carsReveal,
  carsIndex,
  carsResidual,
  type CarsState,
} from './imaging101-cars';
import css from './imaging101-cars.module.css';
const px = (i: number) => 55 + (i / 199) * 450;
const py = (y: number) => 243 - y * 205;
function curve(a: number[]) {
  return a.map((v, i) => `${i ? 'L' : 'M'}${px(i).toFixed(3)},${py(v).toFixed(3)}`).join(' ');
}
function Spectrum({
  fit = false,
  reference = false,
  proposal,
  cursor,
}: {
  fit?: boolean;
  reference?: boolean;
  proposal?: number;
  cursor?: number;
}) {
  return (
    <figure className={css.plot}>
      <svg
        viewBox="0 0 530 288"
        role="img"
        aria-label="CARS intensity versus wavenumber, all 200 native samples"
      >
        <rect x="55" y="28" width="450" height="215" fill="#fff" />
        {[0, 0.5, 1].map((v) => (
          <g key={v}>
            <line x1="55" x2="505" y1={py(v)} y2={py(v)} stroke="#d8e0d7" />
            <text x="45" y={py(v) + 4} textAnchor="end">
              {v.toFixed(1)}
            </text>
          </g>
        ))}
        {[2280, 2290, 2300, 2310, 2320, 2330].map((v) => (
          <text key={v} x={55 + (v - 2280) * 9} y="261" textAnchor="middle">
            {v}
          </text>
        ))}
        <text x="280" y="281" textAnchor="middle">
          Wavenumber / cm⁻¹
        </text>
        <text x="55" y="16">
          Normalized intensity · dimensionless
        </text>
        {input.measured.map((v, i) => (
          <circle key={i} cx={px(i)} cy={py(v)} r="1.65" fill="#264b43" />
        ))}
        {proposal !== undefined && (
          <path
            data-cars-proposal={proposal}
            d={curve(data.proposals[proposal].curve)}
            fill="none"
            stroke="#286caa"
            strokeWidth="2"
          />
        )}
        {fit && (
          <path data-cars-fit d={curve(data.fit)} fill="none" stroke="#b9521e" strokeWidth="2" />
        )}
        {reference && (
          <path
            data-cars-reference
            d={curve(ref.clean)}
            fill="none"
            stroke="#8052a1"
            strokeWidth="2"
            strokeDasharray="6 4"
          />
        )}
        {cursor !== undefined && (
          <g>
            <line
              x1={px(cursor)}
              x2={px(cursor)}
              y1="28"
              y2="243"
              stroke="#777"
              strokeDasharray="2 3"
            />
            <line
              data-cars-residual
              x1={px(cursor)}
              x2={px(cursor)}
              y1={py(input.measured[cursor])}
              y2={py(data.fit[cursor])}
              stroke="#a1264e"
              strokeWidth="4"
            />
            <circle cx={px(cursor)} cy={py(input.measured[cursor])} r="4" fill="#264b43" />
          </g>
        )}
      </svg>
      <figcaption>
        <span>
          <i style={{ background: '#264b43', borderRadius: '50%' }} />
          Measured points
        </span>
        {fit && (
          <span>
            <i style={{ background: '#b9521e' }} />
            Saved fit · solid
          </span>
        )}
        {reference && (
          <span>
            <i className={css.dashed} />
            Clean reference · dashed
          </span>
        )}
        {cursor !== undefined && (
          <span>
            <i style={{ background: '#a1264e' }} />
            Residual · vertical segment
          </span>
        )}
        {proposal !== undefined && (
          <span>
            <i style={{ background: '#286caa' }} />
            Forward diagnostic · {data.proposals[proposal].temperature_K} K
          </span>
        )}
      </figcaption>
    </figure>
  );
}
const titles = {
  inputs: 'Start with 200 spectral measurements',
  staging: 'The released staging exposes the reference',
  forward: 'Change temperature, then predict a spectrum',
  fit: 'Inspect the published fit and its residual',
  reference: 'Reveal the clean source spectrum',
  scoring: 'Two scorer paths ask different questions',
  shape: 'Preserve the batch axis in the output',
  limits: 'A saved fit is useful; a benchmark pass is unresolved',
};
export function CarsScene({ state: s }: { state: CarsState }) {
  const i = carsIndex(s, 3),
    reveal = carsReveal(s),
    index = [50, 113, 182][i];
  let body;
  switch (s.scene) {
    case 'inputs':
      body = (
        <div className={css.columns}>
          <Spectrum />
          <article>
            <p className={css.kicker}>PUBLISHED SYNTHETIC N₂ CASE</p>
            <h4>One spectrum · shape (1, 200)</h4>
            <p>200 paired wavenumbers and intensities. The first axis is the one-case batch.</p>
            <dl>
              <dt>Axis</dt>
              <dd>2280–2330 cm⁻¹</dd>
              <dt>Pressure</dt>
              <dd>10 bar</dd>
              <dt>Pump linewidth</dt>
              <dd>1 cm⁻¹</dd>
              <dt>Slit width</dt>
              <dd>0.5 cm⁻¹</dd>
            </dl>
            <p className={css.callout}>
              These are source-generated data, not a measured gas experiment or a patient scan.
            </p>
          </article>
        </div>
      );
      break;
    case 'staging':
      body = (
        <>
          <div className={css.levels}>
            {['L1 · README', 'L2 · + approach', 'L3 · + design'].map((label, j) => (
              <article key={label} data-current={i === j}>
                <h4>{label}</h4>
                <p>README + requirements + all data/</p>
                {j > 0 && <p>Approach names true 2400 K</p>}
                {j === 2 && <p>Design adds function signatures</p>}
              </article>
            ))}
          </div>
          <div className={css.file}>
            data/raw_data.npz → observations
            <br />
            data/meta_data.json → physical constants
            <br />
            <b data-cars-staging-reference>data/ground_truth.npz → copied too</b>
          </div>
          <p className={css.callout}>
            Verified file seeding for all three levels. Reader reveal controls the illustration; the
            released staging does not hide ground truth.
          </p>
        </>
      );
      break;
    case 'forward':
      body = (
        <div className={css.columns}>
          <Spectrum proposal={carsIndex(s, 2)} />
          <article>
            <p className={css.kicker}>BOUNDED FORWARD DIAGNOSTIC</p>
            <h4>{data.proposals[carsIndex(s, 2)].temperature_K} K → predicted intensity</h4>
            <p>Temperature changes molecular populations and the relaxation matrix.</p>
            <ol>
              <li>Combine Q, O and S branch amplitudes</li>
              <li>Add nonresonant background</li>
              <li>Apply pump and slit operations</li>
              <li>Downsample; normalize by maximum</li>
            </ol>
            <p className={css.callout}>
              Two fixed proposals, not optimizer steps. Pressure, mole fraction and widths stay
              fixed.
            </p>
          </article>
        </div>
      );
      break;
    case 'fit':
      body = (
        <div className={css.columns}>
          <Spectrum fit cursor={index} />
          <article>
            <p className={css.kicker}>UPSTREAM SAVED FIT · REPLAY</p>
            <h4>{data.temperature_K.toFixed(2)} K</h4>
            <p>
              The source optimizer fits temperature, mole fraction, shift and slit width with
              bounded least squares.
            </p>
            <div className={css.number} data-cars-index={index}>
              <b>Sample {index}</b>
              <span>{input.nu[index].toFixed(3)} cm⁻¹</span>
              <span>Measured {input.measured[index].toFixed(5)}</span>
              <span>Fit {data.fit[index].toFixed(5)}</span>
              <strong>Fit − measured = {carsResidual(index).toFixed(5)}</strong>
            </div>
            <p>No new fitting was performed. No convergence trajectory is available here.</p>
          </article>
        </div>
      );
      break;
    case 'reference':
      body = (
        <div className={css.columns}>
          <Spectrum fit reference={reveal} />
          <article>
            <p className={css.kicker}>
              {reveal ? 'READER REFERENCE REVEALED' : 'REFERENCE DISPLAY HIDDEN'}
            </p>
            <h4>{reveal ? '2400 K source truth' : 'Compare after the reveal'}</h4>
            {reveal ? (
              <>
                <p data-cars-reference-temperature>
                  Saved fit: 2391.56 K<br />
                  Absolute error: <b>8.44 K</b>
                </p>
                <p>
                  Clean spectrum is dashed purple. Noise and preprocessing separate measured points
                  from this clean curve.
                </p>
              </>
            ) : (
              <p>
                Playback adds the clean source curve and its true parameter halfway through this
                chapter.
              </p>
            )}
            <p className={css.callout}>
              This is a display reveal. The audited L1–L3 staging already copies the reference file.
            </p>
          </article>
        </div>
      );
      break;
    case 'scoring':
      body = (
        <>
          <table>
            <thead>
              <tr>
                <th>Path</th>
                <th>Compare saved fit to</th>
                <th>NCC</th>
                <th>NRMSE</th>
                <th>T error</th>
              </tr>
            </thead>
            <tbody>
              <tr data-current={i === 0}>
                <td>Active local generic</td>
                <td>Clean spectrum</td>
                <td>0.999979</td>
                <td>0.002403</td>
                <td>Not emitted</td>
              </tr>
              <tr data-current={i === 1}>
                <td>Separate CARS adapter</td>
                <td>Measured spectrum</td>
                <td>0.998361</td>
                <td>0.018240</td>
                <td>8.44 K</td>
              </tr>
              <tr data-current={i === 2}>
                <td>Generic raw no-op</td>
                <td>Clean spectrum</td>
                <td>0.998346</td>
                <td>0.018418</td>
                <td>Not emitted</td>
              </tr>
            </tbody>
          </table>
          <div className={css.cards}>
            <article>
              <h4>Same curve, wrong temperature</h4>
              <p>
                CARS adapter: substituting 300 K leaves NCC unchanged and makes temperature error
                2100 K.
              </p>
            </article>
            <article>
              <h4>Pass status unavailable</h4>
              <p>
                No CARS metrics.json in the pinned Git tree or asset manifest. Thresholds were not
                invented or regenerated.
              </p>
            </article>
          </div>
          <p>
            Cosine NCC measures spectral agreement. It does not by itself establish temperature
            recovery.
          </p>
        </>
      );
      break;
    case 'shape':
      body = (
        <>
          <div className={css.levels}>
            {[
              ['(1, 200)', 'Spectral array accepted', 'Preserve batch axis.'],
              ['(200,)', 'Reference shape lookup fails', '1D flattening changes selection.'],
              ['(1,)', 'Scalar reference selected', 'NRMSE is infinite; no Kelvin-error metric.'],
            ].map((r, j) => (
              <article key={r[0]} data-current={i === j}>
                <h4>{r[0]}</h4>
                <b>{r[1]}</b>
                <p>{r[2]}</p>
              </article>
            ))}
          </div>
          <div className={css.file}>
            Active local contract:
            <br />
            <b>output/reconstruction.npy</b>
            <br />
            one numeric spectral array · retain shape (1, 200)
          </div>
          <p className={css.callout}>
            Separate native adapter: reconstruction.npz with y_pred and temperature_pred. These
            output contracts are not interchangeable.
          </p>
        </>
      );
      break;
    case 'limits':
      body = (
        <>
          <div className={css.cards}>
            <article>
              <h4>What is established</h4>
              <p>
                Exact published samples, saved fit, reproduced scoring, staged reference visibility
                and array conventions.
              </p>
              <p>
                Saved temperature error: <b>8.44 K on one synthetic case.</b>
              </p>
            </article>
            <article>
              <h4>What remains unestablished</h4>
              <p>
                No fresh agent result, hidden-reference evaluation, benchmark pass, confidence
                interval or general performance estimate.
              </p>
              <p>Docker fallback was inspected in source only.</p>
            </article>
          </div>
          <p className={css.callout}>
            Implementation limit: max normalization cancels mole-fraction amplitude. At fixed
            temperature, x = 0.79 and 0.20 gave curves equal within 2.23 × 10⁻¹⁶. A fitted mole
            fraction is not established by this normalized curve.
          </p>
          <p>
            Forward diagnostics retained numerical warnings; all output samples were finite.
            Original source arrays and outcomes remain unchanged.
          </p>
        </>
      );
      break;
  }
  return (
    <section className={css.scene} data-cars-scene={s.scene} data-cars-reveal={reveal}>
      <h3>{titles[s.scene]}</h3>
      {body}
    </section>
  );
}
export function CarsOutput({ state: s }: { state: CarsState }) {
  return (
    <aside className={css.aside} data-cars-aside>
      <b>
        {s.scene === 'staging'
          ? 'REFERENCE BOUNDARY'
          : s.scene === 'scoring'
            ? 'SCORING CONTRACT'
            : 'SOURCE-BACKED WALKTHROUGH'}
      </b>
      <p>
        {s.scene === 'staging'
          ? 'All L1–L3 levels copy the data directory, including ground truth.'
          : s.scene === 'scoring'
            ? 'The active local path scores spectral arrays. The distinct CARS adapter also reports temperature error.'
            : 'Published synthetic N₂ measurements and an upstream saved fit. Original arrays are retained.'}
      </p>
      <p>One source case. No agent run or fresh inverse solve.</p>
      <small>
        Imaging101 dc2f668… · MIT
        <br />
        200 source samples · cm⁻¹ and K
      </small>
    </aside>
  );
}

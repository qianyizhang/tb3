import {
  ptychographyInput as input,
  ptychographyData as data,
  ptychographyReference as ref,
  ptychographyIndex,
  ptychographyReveal,
  type PtychographyState,
  type PtychographyImage,
} from './imaging101-ptychography';
import css from './imaging101-ptychography.module.css';

const titles = {
  inputs: 'Measure intensity at overlapping scan positions',
  overlap: 'Place each probe window in one object grid',
  projection: 'Replace detector amplitude in one diagnostic step',
  output: 'Inspect the saved complex object and error history',
  reference: 'Reveal the synthetic phase object',
  staging: 'All three assistance levels include the truth',
  scoring: 'Magnitude scores cannot distinguish these phases',
  limits: 'Keep the phase result and evaluation limits separate',
};
function Plane({
  image,
  label,
  reference = false,
  detector = false,
}: {
  image: PtychographyImage;
  label: string;
  reference?: boolean;
  detector?: boolean;
}) {
  const n = image.shape[0],
    step = 220 / n;
  return (
    <figure
      className={css.plane}
      data-ptychography-plane={reference ? 'reference' : 'source'}
      data-ptychography-reference={reference ? 'truth' : undefined}
    >
      <svg viewBox="0 0 300 290" role="img" aria-label={label}>
        <image
          href={image.data}
          x="55"
          y="15"
          width="220"
          height="220"
          preserveAspectRatio="none"
        />
        <rect
          x="55"
          y="15"
          width="220"
          height="220"
          fill="none"
          stroke={reference ? '#8052a1' : '#264b43'}
          strokeWidth="2"
          strokeDasharray={reference ? '6 4' : undefined}
        />
        <text x={55 + step / 2} y="251">
          0
        </text>
        <text x={275 - step / 2} y="251" textAnchor="end">
          {n - 1}
        </text>
        <text x="165" y="267" textAnchor="middle">
          column / pixel center
        </text>
        <text x="47" y={20 + step / 2} textAnchor="end">
          0
        </text>
        <text x="47" y={235 - step / 2} textAnchor="end">
          {n - 1}
        </text>
        <text transform="translate(17 125) rotate(-90)" textAnchor="middle">
          row / pixel center
        </text>
        <text x="165" y="285" textAnchor="middle">
          {detector ? '72 µm / detector pixel' : '3.43316 µm / object pixel'}
        </text>
      </svg>
      <figcaption>{label}</figcaption>
    </figure>
  );
}
function Scale({
  low,
  high,
  logarithmic = false,
}: {
  low: string;
  high: string;
  logarithmic?: boolean;
}) {
  return (
    <div className={css.scale}>
      <span>{low}</span>
      <i />
      <span>{high}</span>
      <span>{logarithmic ? 'log1p · counts' : 'linear · 8-bit display'}</span>
    </div>
  );
}
function Overlap({ index }: { index: number }) {
  const sample = input.samples[index],
    [row, col] = sample.position_rc;
  const map = (p: number) => 45 + ((p + 0.5) / 542) * 250;
  return (
    <div className={css.two}>
      <svg
        className={css.map}
        viewBox="0 0 330 325"
        role="img"
        aria-label="All 100 rounded scan origins and a selected 128 pixel extraction window"
      >
        <rect x="45" y="45" width="250" height="250" fill="#fff" stroke="#7d9289" />
        {input.positions.map(([r, c], j) => (
          <circle key={j} cx={map(c + 64)} cy={map(r + 64)} r="2.5" fill="#264b43" />
        ))}
        <rect
          data-ptychography-window={sample.scan}
          x={map(col - 0.5)}
          y={map(row - 0.5)}
          width={(128 / 542) * 250}
          height={(128 / 542) * 250}
          fill="#b9521e"
          fillOpacity="0.08"
          stroke="#b9521e"
          strokeWidth="2"
        />
        <circle cx={map(col + 64)} cy={map(row + 64)} r="5" fill="#b9521e" stroke="#fff" />
        <text x="45" y="30">
          100 scan origins · no truth image
        </text>
        <text x={map(0)} y="310">
          0
        </text>
        <text x={map(541)} y="310" textAnchor="end">
          541
        </text>
        <text x="170" y="324" textAnchor="middle">
          column / pixel center
        </text>
        <text x="36" y={map(0) + 4} textAnchor="end">
          0
        </text>
        <text x="36" y={map(541)} textAnchor="end">
          541
        </text>
        <text transform="translate(15 168) rotate(-90)" textAnchor="middle">
          row / pixel center
        </text>
      </svg>
      <div className={css.card}>
        <small>ACTUAL SCAN {sample.scan} · ZERO-BASED</small>
        <h4>round(encoder / dx) + 207</h4>
        <dl>
          <dt>Encoder row / µm</dt>
          <dd>{(sample.encoder_m[0] * 1e6).toFixed(3)}</dd>
          <dt>Encoder column / µm</dt>
          <dd>{(sample.encoder_m[1] * 1e6).toFixed(3)}</dd>
          <dt>Patch upper-left / px</dt>
          <dd>
            ({row}, {col})
          </dd>
          <dt>Inclusive row indices</dt>
          <dd>
            {row}–{row + 127}
          </dd>
          <dt>Inclusive column indices</dt>
          <dd>
            {col}–{col + 127}
          </dd>
        </dl>
        <p>
          dx = 3.4331597 µm. Orange point: rounded scan origin. Orange outline: extraction window.
        </p>
        <p className={css.note}>
          Windows cover 144,986 / 293,764 pixels. This is rectangular patch coverage, not beam
          support or accuracy.
        </p>
      </div>
    </div>
  );
}
function History() {
  const values = data.errors,
    lo = 1,
    hi = 500;
  const y = (v: number) =>
    260 - ((Math.log10(v) - Math.log10(lo)) / (Math.log10(hi) - Math.log10(lo))) * 220;
  const path = values
    .map((v, i) => `${i ? 'L' : 'M'}${55 + (i / (values.length - 1)) * 360},${y(v)}`)
    .join(' ');
  return (
    <svg
      className={css.history}
      viewBox="0 0 460 305"
      role="img"
      aria-label="All 350 stored error values, logarithmic vertical axis"
    >
      <text x="55" y="18">
        Stored error · log scale
      </text>
      {[1, 10, 100, 500].map((v) => (
        <g key={v}>
          <line x1="55" x2="415" y1={y(v)} y2={y(v)} stroke="#d4ddd3" />
          <text x="47" y={y(v) + 4} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      <path data-ptychography-history d={path} fill="none" stroke="#264b43" strokeWidth="2" />
      <circle cx="415" cy={y(values[349])} r="4" fill="#b9521e" />
      <text x="55" y="280">
        1
      </text>
      <text x="415" y="280" textAnchor="end">
        350
      </text>
      <text x="240" y="299" textAnchor="middle">
        Stored outer iteration
      </text>
    </svg>
  );
}
export function PtychographyScene({ state: s }: { state: PtychographyState }) {
  const index = ptychographyIndex(s),
    sample = input.samples[index],
    reveal = ptychographyReveal(s);
  let body;
  switch (s.scene) {
    case 'inputs':
      body = (
        <>
          <div className={css.two}>
            <div>
              <Plane
                image={sample.measured}
                label={`Simulated diffraction · scan ${sample.scan}`}
                detector
              />
              <Scale low="0" high="32,966" logarithmic />
            </div>
            <div className={css.card}>
              <small>INTENSITY ONLY · SYNTHETIC CASE</small>
              <h4>100 scans × 128 × 128 pixels</h4>
              <p>632.8 nm wavelength · 50 mm propagation</p>
              <p>Detector: 72 µm / pixel. Object: 3.43316 µm / pixel.</p>
              <p className={css.flow}>object patch × probe → centered FFT → |field|²</p>
              <p>
                The detector stores intensity. Object phase must be inferred from agreement across
                overlapping scans.
              </p>
              <p className={css.note}>
                Source generation adds a Poisson draw to its expectation. The 14-bit scale is not a
                count cap.
              </p>
            </div>
          </div>
        </>
      );
      break;
    case 'overlap':
      body = <Overlap index={index} />;
      break;
    case 'projection':
      body = (
        <>
          <div className={css.flow}>
            One source initialization · scan {sample.scan} · Ψ′ = Ψ √(I / (|Ψ|² + 10⁻¹⁰))
          </div>
          <div className={css.three}>
            <Plane image={sample.estimated} label="Before: initialized wave intensity" detector />
            <Plane image={sample.measured} label="Target: source measured intensity" detector />
            <Plane image={sample.projected} label="After: projected wave intensity" detector />
          </div>
          <Scale low="0" high="32,966" logarithmic />
          <p>
            Relative intensity L1: <b>{sample.before_relative_l1.toFixed(6)}</b> →{' '}
            <b>{sample.after_relative_l1.toExponential(2)}</b>.
          </p>
          <p className={css.note}>
            The wave amplitude changes; no object or probe update was run. This is not a recovered
            object.
          </p>
        </>
      );
      break;
    case 'output':
      body = (
        <div className={css.two}>
          <div>
            {index === 2 ? (
              <History />
            ) : (
              <>
                <Plane
                  image={index === 0 ? data.amplitude : data.phase}
                  label={index === 0 ? 'Saved object amplitude' : 'Saved object raw phase'}
                />
                <Scale
                  low={index === 0 ? '0' : '−π rad'}
                  high={index === 0 ? '1.24527' : 'π rad'}
                />
              </>
            )}
          </div>
          <div className={css.card}>
            <small>SAVED RELEASE · NO FRESH INVERSE</small>
            <h4>{index === 2 ? '350 recorded error samples' : '542 × 542 complex64 object'}</h4>
            {index === 2 ? (
              <>
                <p>
                  Last stored value: <b>1.8429171</b>.
                </p>
                <p>
                  The code sums per-scan relative intensity L1 residuals before sequential updates,
                  then applies constraints.
                </p>
                <p className={css.note}>
                  The approach describes a different amplitude metric. These values are not
                  interchangeable.
                </p>
              </>
            ) : (
              <>
                <p>
                  Native pixel geometry and the original complex array are retained. Images only
                  apply the labeled display scale.
                </p>
                <p>
                  Native phase replay: <b>NCC 0.9757</b>, <b>NRMSE 0.0434</b>.
                </p>
                <p className={css.note}>
                  The native metric subtracts each phase image’s mean. Display shows raw phase; no
                  registration or phase unwrapping.
                </p>
              </>
            )}
            <p>
              Stored object and probe are a joint result. The projection diagnostic did not generate
              this result.
            </p>
          </div>
        </div>
      );
      break;
    case 'reference':
      body = (
        <>
          <div className={css.two}>
            <Plane image={data.phase} label="Saved object · raw phase" />
            {reveal ? (
              <Plane image={ref.phase} label="Synthetic truth · raw phase" reference />
            ) : (
              <div className={css.card}>
                <small>READER REFERENCE HIDDEN</small>
                <h4>Compare phase after the reveal</h4>
                <p>Playback reveals the truth halfway through this chapter.</p>
                <p className={css.note}>
                  The released L1–L3 data packet already includes both truth files.
                </p>
              </div>
            )}
          </div>
          <Scale low="−π rad" high="π rad" />
          {reveal && (
            <p data-ptychography-reference-detail>
              Truth has unit amplitude everywhere; 11,970 / 293,764 pixels encode bars at phase π/2.
              This is synthetic truth, not a specimen annotation.
            </p>
          )}
        </>
      );
      break;
    case 'staging':
      body = (
        <>
          <div className={css.three}>
            {['L1', 'L2', 'L3'].map((level, i) => (
              <div
                key={level}
                className={`${css.card} ${index === i ? css.active : ''}`}
                data-ptychography-level={level}
              >
                <h4>{level}</h4>
                <p>README + requirements + data/</p>
                <p>{i > 0 ? '+ approach.md' : 'Choose an approach'}</p>
                <p>{i > 1 ? '+ design.md' : 'Implementation still required'}</p>
                <p className={css.note}>
                  ground_truth.npy
                  <br />
                  ground_truth.npz
                  <br />
                  <b>Both copied</b>
                </p>
              </div>
            ))}
          </div>
          <p className={css.flow}>
            Selected LocalRunner.start reproduced file copies; all installation commands were
            intercepted.
          </p>
          <p>
            Source and evaluation directories are not seeded. A read-only Docker source mount does
            not make the truth private; no Docker execution was performed.
          </p>
        </>
      );
      break;
    case 'scoring': {
      const rows = [
        ['truth-copy', 'Correct truth'],
        ['phase-erased-unit', 'Erased phase'],
        ['conjugated-truth', 'Reversed phase'],
      ];
      body = (
        <>
          <table className={css.table}>
            <thead>
              <tr>
                <th>Control</th>
                <th>Generic NCC</th>
                <th>Generic MSE</th>
                <th>Phase NCC</th>
                <th>Phase NRMSE</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(([id, label], i) => (
                <tr key={id} className={i === index ? css.active : ''} data-ptychography-score={id}>
                  <td>{label}</td>
                  <td>{data.generic[id].ncc.toFixed(4)}</td>
                  <td>{data.generic[id].mse.toFixed(4)}</td>
                  <td>{data.native_phase[id].ncc.toFixed(4)}</td>
                  <td>{data.native_phase[id].nrmse.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className={css.two}>
            <div className={css.card}>
              <h4>Phase is discarded</h4>
              <p>
                Generic scoring converts complex arrays to magnitude. All three controls become the
                same unit array.
              </p>
            </div>
            <div className={css.card}>
              <h4>NRMSE: infinity for all three</h4>
              <p>
                Reference magnitude range is zero. Even exact truth returns infinity. No pass
                thresholds are shipped.
              </p>
            </div>
          </div>
          <p className={css.note}>
            Phase columns use native full-frame, mean-centered angles. Saved result: phase NCC
            0.9757; generic magnitude NCC 0.728639.
          </p>
        </>
      );
      break;
    }
    case 'limits':
      body = (
        <>
          <div className={css.two}>
            <div className={css.card}>
              <h4>Established by this audit</h4>
              <p>
                Exact simulated measurements, native geometry, operator fixture, saved result and
                scoring controls.
              </p>
              <p>
                32-pixel source fixture agreement within 1.25 × 10⁻¹⁴. Original arrays and metrics
                retained.
              </p>
            </div>
            <div className={css.card}>
              <h4>Still unestablished</h4>
              <p>
                Fresh reconstruction, agent capability, private-reference validity, benchmark pass
                or general specimen accuracy.
              </p>
              <p>No inverse iteration, runtime installation or dataset regeneration.</p>
            </div>
          </div>
          <p className={css.note}>
            Source code uses a 5% random momentum trigger and intensity L1 history; the approach
            describes periodic momentum and amplitude error.
          </p>
          <p>
            Benchmark MIT attribution and original PtyLab academic/non-commercial terms are retained
            separately.
          </p>
        </>
      );
      break;
  }
  return (
    <section className={css.scene} data-ptychography-scene={s.scene}>
      <h3>{titles[s.scene]}</h3>
      {body}
    </section>
  );
}
export function PtychographyOutput({ state: s }: { state: PtychographyState }) {
  return (
    <aside className={css.aside} data-ptychography-aside>
      <b>{s.scene === 'scoring' ? 'SCORING CONTRACT' : 'SOURCE-BACKED WALKTHROUGH'}</b>
      <p>
        One simulated diffraction dataset and saved complex reconstruction. Synthetic truth appears
        only after reveal.
      </p>
      <p>Selected forward diagnostics; no fresh inverse or agent run.</p>
      <small>
        Imaging101 dc2f668…
        <br />
        PtyLab source attribution retained
        <br />
        µm · pixels · radians · counts
      </small>
    </aside>
  );
}

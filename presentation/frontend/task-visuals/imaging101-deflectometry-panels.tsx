import {
  deflectometryInput as input,
  deflectometryData as data,
  deflectometryReference as ref,
  deflectometryIndex,
  deflectometryReveal,
  type DeflectometryState,
  type DeflectometryImage,
  type LensProfile,
  type PhaseProbe,
} from './imaging101-deflectometry';
import css from './imaging101-deflectometry.module.css';
const green = '#264b43',
  orange = '#b9521e',
  purple = '#8052a1';
const titles = {
  inputs: 'Two camera views retain the measured stripe pattern',
  calibration: 'Calibration fixes coordinates and the supplied crop',
  phase: 'Four shifted images encode one phase',
  geometry: 'Curvature and thickness define two refracting surfaces',
  output: 'Inspect saved views and all eight parameters',
  reference: 'Reveal the manufacturer specification',
  scoring: 'A three-number score leaves pose unchecked',
  limits: 'Read the saved loss with its actual scope',
};
const n = (v: number, digits = 3) => v.toFixed(digits);
function Plane({
  image,
  label,
  role = 'source',
  pixel,
}: {
  image: DeflectometryImage;
  label: string;
  role?: string;
  pixel?: [number, number];
}) {
  return (
    <figure className={css.plane} data-deflectometry-panel={role}>
      <svg viewBox="0 0 220 200" role="img" aria-label={label}>
        <image
          href={image.data}
          x="25"
          y="4"
          width="170"
          height="170"
          preserveAspectRatio="xMidYMid meet"
        />
        <rect x="25" y="4" width="170" height="170" fill="none" stroke={green} />
        {pixel && (
          <g stroke={orange} strokeWidth="2">
            <circle
              cx={25 + ((pixel[1] + 0.5) / 32) * 170}
              cy={4 + ((pixel[0] + 0.5) / 32) * 170}
              r="8"
              fill="none"
            />
            <line
              x1={25 + ((pixel[1] + 0.5) / 32) * 170 - 11}
              x2={25 + ((pixel[1] + 0.5) / 32) * 170 + 11}
              y1={4 + ((pixel[0] + 0.5) / 32) * 170}
              y2={4 + ((pixel[0] + 0.5) / 32) * 170}
            />
          </g>
        )}
        <text x="110" y="191" textAnchor="middle">
          {pixel ? '32 × 32 synthetic fixture' : 'Rendered 768 × 768 source view'}
        </text>
      </svg>
      <figcaption>{label}</figcaption>
    </figure>
  );
}
function Profile({ profile, reference = false }: { profile: LensProfile; reference?: boolean }) {
  const x = (z: number) => 160 + 8.5 * z,
    y = (r: number) => 145 - 8.5 * r;
  const line = (p: LensProfile, key: 'front' | 'back') =>
    p.r.map((r, i) => `${i ? 'L' : 'M'}${x(p[key][i])},${y(r)}`).join(' ');
  const outline =
    line(profile, 'front') +
    profile.r
      .map((_, j) => {
        const i = profile.r.length - 1 - j;
        return `L${x(profile.back[i])},${y(profile.r[i])}`;
      })
      .join(' ') +
    'Z';
  return (
    <svg
      className={css.profile}
      viewBox="0 0 360 285"
      role="img"
      aria-label={
        reference
          ? 'Saved lens section and manufacturer specification'
          : 'Lens-local section from source parameters'
      }
    >
      <path d={outline} fill="#dce9e5" stroke={green} strokeWidth="2" />
      {reference && (
        <g
          data-deflectometry-reference="profile"
          fill="none"
          stroke={purple}
          strokeWidth="2"
          strokeDasharray="5 3"
        >
          <path d={line(ref.profile, 'front')} />
          <path d={line(ref.profile, 'back')} />
        </g>
      )}
      <path d="M106 145H235M125 34V257" stroke="#8b9d95" strokeWidth="1" />
      {[-12, 0, 12].map((v) => (
        <g key={v}>
          <line x1="121" x2="129" y1={y(v)} y2={y(v)} stroke={green} />
          <text x="116" y={y(v) + 4} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      {[-2, 0, 2, 4, 6].map((v) => (
        <g key={v}>
          <line x1={x(v)} x2={x(v)} y1="142" y2="148" stroke={green} />
          <text x={x(v)} y="163" textAnchor="middle">
            {v}
          </text>
        </g>
      ))}
      <text x="25" y="28">
        radial r (mm)
      </text>
      <text x="244" y="146">
        axial z (mm)
      </text>
      <text x="180" y="277" textAnchor="middle">
        Equal mm scale · lens-local section
      </text>
      <line x1={x(0)} x2={x(profile.thickness)} y1="131" y2="131" stroke={orange} strokeWidth="3" />
      <text x="242" y="111" fill={orange}>
        d = {n(profile.thickness)} mm
      </text>
      <text x="15" y="225">
        Front surface
      </text>
      <path d={`M100 222L${x(profile.front[14])} ${y(profile.r[14])}`} stroke={green} fill="none" />
      <text x="246" y="224">
        Back surface
      </text>
      <path d={`M240 220L${x(profile.back[14])} ${y(profile.r[14])}`} stroke={green} fill="none" />
    </svg>
  );
}
function Phase({ probe }: { probe: PhaseProbe }) {
  return (
    <div className={css.two}>
      <div className={css.phaseGrid}>
        {probe.frames.map((image, i) => (
          <div key={i}>
            <Plane
              image={image}
              label={`Shift ${i}: I${i} = ${n(probe.values[i], 2)}`}
              role="synthetic"
              pixel={[probe.row, probe.column]}
            />
          </div>
        ))}
      </div>
      <div className={css.card}>
        <h4>
          {probe.axis}-direction · camera {probe.camera}
        </h4>
        <p>
          Fixed pixel [row {probe.row}, column {probe.column}]
        </p>
        <svg
          className={css.phaseVector}
          viewBox="0 0 270 160"
          role="img"
          aria-label="Four-step phase vector"
        >
          <path d="M35 80H235M135 8V150" stroke="#9eada4" />
          <circle cx="135" cy="80" r="57" fill="none" stroke="#c3d1c7" />
          <line
            x1="135"
            y1="80"
            x2={135 + probe.delta[0] * 0.57}
            y2={80 - probe.delta[1] * 0.57}
            stroke={orange}
            strokeWidth="3"
          />
          <circle
            cx={135 + probe.delta[0] * 0.57}
            cy={80 - probe.delta[1] * 0.57}
            r="5"
            fill={orange}
          />
          <text x="185" y="151">
            I₀ − I₂
          </text>
          <text x="10" y="16">
            I₃ − I₁
          </text>
        </svg>
        <p className={css.formula}>
          φ = atan2({n(probe.delta[1], 1)}, {n(probe.delta[0], 1)})
        </p>
        <p>
          <strong>{n(probe.phase, 4)} rad</strong> · mean {n(probe.mean, 0)} · b²{' '}
          {n(probe.squared_modulation, 0)}
        </p>
        <p className={css.note}>
          Synthetic helper fixture. This is not recovered native-camera phase.
        </p>
      </div>
    </div>
  );
}
function Loss({ index }: { index: number }) {
  const values = data.loss.values,
    x = (i: number) => 48 + (i / (values.length - 1)) * 328,
    y = (v: number) => 225 - ((Math.log10(v) + 3) / 3.4) * 195;
  return (
    <svg
      className={css.loss}
      viewBox="0 0 420 275"
      role="img"
      aria-label="All 21 saved pre-update loss samples, logarithmic scale"
    >
      {[1, 0.1, 0.01, 0.001].map((v) => (
        <g key={v}>
          <line x1="48" x2="380" y1={y(v)} y2={y(v)} stroke="#d4ded3" />
          <text x="39" y={y(v) + 4} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      <path
        d={values.map((v, i) => `${i ? 'L' : 'M'}${x(i)} ${y(v)}`).join(' ')}
        fill="none"
        stroke={green}
        strokeWidth="2"
      />
      {values.map((v, i) => (
        <rect key={i} x={x(i) - 1.5} y={y(v) - 1.5} width="3" height="3" fill={green} />
      ))}
      <circle key={`cursor-${index}`} cx={x(index)} cy={y(values[index])} r="5" fill={orange} />
      {[0, 5, 10, 15, 20].map((i) => (
        <text key={i} x={x(i)} y="246" textAnchor="middle">
          {i}
        </text>
      ))}
      <text x="210" y="268" textAnchor="middle">
        Saved loss index · no new optimizer
      </text>
      <text x="48" y="16">
        Masked component MSE · mm² · log axis
      </text>
    </svg>
  );
}
function SavedParameters() {
  const p = data.saved_parameters;
  return (
    <div className={css.card}>
      <h4>optimized_params.json</h4>
      <dl>
        <dt>c₀ (mm⁻¹)</dt>
        <dd>{n(p.surface_0_c, 6)}</dd>
        <dt>c₁ (mm⁻¹)</dt>
        <dd>{n(p.surface_1_c, 6)}</dd>
        <dt>Thickness (mm)</dt>
        <dd>{n(p.surface_1_d, 4)}</dd>
        <dt>Origin x / y / z (mm)</dt>
        <dd>{p.origin.map((v) => n(v, 2)).join(' / ')}</dd>
        <dt>Tilt x / y (degrees)</dt>
        <dd>
          {n(p.theta_x, 3)} / {n(p.theta_y, 3)}
        </dd>
      </dl>
      <p>
        R₀ = 1/c₀ = {n(1 / p.surface_0_c, 3)} mm
        <br />
        R₁ = 1/c₁ = {n(1 / p.surface_1_c, 3)} mm
      </p>
      <p className={css.note}>Eight values describe the fit; the custom score uses only three.</p>
    </div>
  );
}
export function DeflectometryScene({ state: s }: { state: DeflectometryState }) {
  const camera = deflectometryIndex(s, 2),
    revealed = deflectometryReveal(s),
    index = deflectometryIndex(s, 21),
    p = data.saved_parameters;
  return (
    <div className={css.scene} data-deflectometry-scene={s.scene}>
      <h3>{titles[s.scene]}</h3>
      {s.scene === 'inputs' && (
        <>
          <div className={css.two}>
            <div className={css.twoImages}>
              {input.measurements.map((image, i) => (
                <div key={i} className={i === camera ? css.active : undefined}>
                  <Plane image={image} label={`Camera ${i + 1} · measurement`} role="measurement" />
                </div>
              ))}
            </div>
            <div className={css.card}>
              <h4>Known stripes pass through a lens</h4>
              <p>Two calibrated cameras observe the display through two refracting surfaces.</p>
              <p>
                Declared raw stack: <code>3 periods × 8 shifts × 2 cameras</code>, with lens-present
                and lens-absent images.
              </p>
              <p className={css.note}>
                These are normalized, masked notebook panels. Raw intensity stacks are unavailable.
              </p>
              <p>One lens example · two cameras · no extra cases in the repeated source figure.</p>
            </div>
          </div>
          <p className={css.flow}>Input → phase measurements → lens geometry and pose</p>
        </>
      )}
      {s.scene === 'calibration' && (
        <div className={css.two}>
          <svg
            className={css.crop}
            viewBox="0 0 360 290"
            role="img"
            aria-label="Centered 768 pixel crop inside a 2048 pixel sensor"
          >
            <rect x="55" y="12" width="230" height="230" fill="#e9eee6" stroke={green} />
            <rect
              x={55 + (230 * 640) / 2048}
              y={12 + (230 * 640) / 2048}
              width={(230 * 768) / 2048}
              height={(230 * 768) / 2048}
              fill="#f2dfc8"
              stroke={orange}
              strokeWidth="3"
            />
            <text x="171" y="128" textAnchor="middle">
              768 × 768
            </text>
            <text x="171" y="259" textAnchor="middle">
              2048 × 2048 source sensor
            </text>
            <text x="171" y="281" textAnchor="middle">
              Start [640, 640] · index geometry only
            </text>
          </svg>
          <div className={css.card}>
            <h4>Supplied calibration</h4>
            <dl>
              <dt>Fringe periods</dt>
              <dd>70 / 100 / 110 px</dd>
              <dt>Display pitch</dt>
              <dd>0.115 mm / px</dd>
              <dt>Cameras</dt>
              <dd>2</dd>
              <dt>Lens prescription</dt>
              <dd>LE1234-A</dd>
            </dl>
            <p>
              Four shifts for x, four for y, at each period. Intrinsics and camera/display
              transforms accompany the data.
            </p>
            <p className={css.note}>
              Crop coordinates are camera pixels; display displacement uses a separate calibrated mm
              frame.
            </p>
          </div>
        </div>
      )}
      {s.scene === 'phase' && <Phase probe={input.fixture_probes[deflectometryIndex(s, 4)]} />}
      {s.scene === 'geometry' && (
        <div className={css.two}>
          <div>
            <h4>{camera === 0 ? 'Initial near-flat section' : 'Saved fitted section'}</h4>
            <Profile profile={camera === 0 ? data.initial_profile : data.saved_profile} />
          </div>
          <div className={css.card}>
            <h4>Two surfaces, one local lens frame</h4>
            <p>
              Each curvature controls spherical sag. Vertex separation is center thickness d; the
              supplied diameter is 25.4 mm.
            </p>
            <p className={css.formula}>z(r) = cr² / (1 + √(1 − c²r²))</p>
            <p>Initial: c₀ = c₁ = 0.001 mm⁻¹, d = 3 mm.</p>
            <p>
              Saved: c₀ = {n(p.surface_0_c, 6)}, c₁ = {n(p.surface_1_c, 6)} mm⁻¹.
            </p>
            <p className={css.note}>
              Discrete source states; analytical sections only. No ray tracing or invented
              optimization steps.
            </p>
          </div>
        </div>
      )}
      {s.scene === 'output' && (
        <div className={css.two}>
          <div>
            <h4>Camera {camera + 1} · saved source comparison</h4>
            <div className={css.twoImages}>
              <Plane
                image={data.modeled.initial[camera]}
                label="Initial modeled"
                role="modeled-initial"
              />
              <Plane
                image={data.modeled.saved[camera]}
                label="Optimized modeled"
                role="modeled-saved"
              />
            </div>
            <p className={css.note}>
              Rendered source panels, normalized to 0–1. Visual agreement is not a fresh fit.
            </p>
          </div>
          <SavedParameters />
        </div>
      )}
      {s.scene === 'reference' &&
        (!revealed ? (
          <div className={css.hidden}>
            <h4>Manufacturer reference not yet revealed</h4>
            <p>Continue playback to compare radii and thickness.</p>
            <p>
              Reader reveal only: the benchmark actually supplies this truth and prescription at
              every assistance level.
            </p>
          </div>
        ) : (
          <div className={css.two} data-deflectometry-reference="comparison">
            <Profile profile={data.saved_profile} reference />
            <div>
              <table className={css.table}>
                <thead>
                  <tr>
                    <th>mm</th>
                    <th>Saved</th>
                    <th>Maker</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {[1 / p.surface_0_c, 1 / p.surface_1_c, p.surface_1_d].map((v, i) => (
                    <tr
                      key={i}
                      className={
                        i === Math.min(2, Math.floor((s.view - 0.5) * 6)) ? css.active : undefined
                      }
                    >
                      <th>{['R₀', 'R₁', 'd'][i]}</th>
                      <td>{n(v, 2)}</td>
                      <td>{n(ref.manufacturer_parameters_mm[i], 2)}</td>
                      <td>{n(ref.relative_errors[i] * 100, 2)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p>
                Green solid: saved section.
                <br />
                <span className={css.purple}>Purple dashed: manufacturer section.</span>
                <br />
                Orange line: saved center thickness.
              </p>
              <p className={css.note}>
                Manufacturer specification is not an independent measurement of this sample. No pose
                truth is supplied.
              </p>
            </div>
          </div>
        ))}
      {s.scene === 'scoring' && (
        <div className={css.two}>
          <div className={css.card}>
            <h4>Custom helper: only R₀, R₁, d</h4>
            <table className={css.table}>
              <thead>
                <tr>
                  <th>File control</th>
                  <th>NCC</th>
                  <th>NRMSE</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Saved output</td>
                  <td>{n(data.custom_score.ncc, 6)}</td>
                  <td>{n(data.custom_score.nrmse, 6)}</td>
                </tr>
                <tr>
                  <td>Pose replaced</td>
                  <td>{n(data.pose_control.score.ncc, 6)}</td>
                  <td>{n(data.pose_control.score.nrmse, 6)}</td>
                </tr>
              </tbody>
            </table>
            <p>
              Changed origin to [1000, 1000, 1000] mm and both tilts to 90°. The score is unchanged.
            </p>
            <p className={css.note}>A scoring control, not an optically equivalent lens.</p>
          </div>
          <div className={css.card}>
            <h4>Generic end-to-end contract fails</h4>
            <p>
              <code>output/reconstruction.npy</code> with all three correct truth values is
              rejected: the reference NPZ holds three separate one-value arrays.
            </p>
            <p>
              A one-radius oracle matches a scalar key but has zero reference range:{' '}
              <strong>NRMSE = ∞</strong>.
            </p>
            <p className={css.note}>
              No NCC/NRMSE thresholds are supplied. Neither route establishes a current benchmark
              pass.
            </p>
          </div>
        </div>
      )}
      {s.scene === 'limits' && (
        <div className={css.two}>
          <div>
            <Loss index={index} />
            <p className={css.flow}>
              Sample {index} / 20 · {data.loss.values[index].toExponential(4)} mm²
            </p>
          </div>
          <div className={css.card}>
            <h4>Keep the evidence boundaries</h4>
            <p>21 saved pre-update losses average masked residual components over the full grid.</p>
            <p>
              Reported valid-pixel displacement: <strong>43.0513 µm</strong>. It cannot be replayed
              from rendered figures.
            </p>
            <p>
              L1 / L2 / L3 all expose manufacturer truth and the lens prescription. Plans add help;
              they do not hide answers.
            </p>
            <p className={css.note}>
              Raw archive unavailable · no new optical fit or agent run. These views explain the
              released task and its limits.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
export function DeflectometryOutput({ state: s }: { state: DeflectometryState }) {
  const text: Record<DeflectometryState['scene'], [string, string]> = {
    inputs: [
      'Two-camera measurement view',
      'Rendered notebook pixels; full raw stacks remain unavailable.',
    ],
    calibration: [
      'Known setup and crop',
      'Camera pixel coordinates and display millimeters remain distinct.',
    ],
    phase: [
      'Fixed four-step control',
      'Synthetic intensities recover phase by atan2; no native phase reconstruction.',
    ],
    geometry: [
      'Lens-local geometry',
      'Saved and initial sections use exact source parameters, with equal mm scales.',
    ],
    output: [
      'Eight saved parameters',
      'Curvatures, thickness, origin and tilt; a retained output, not a fresh prediction.',
    ],
    reference: deflectometryReveal(s)
      ? [
          'Manufacturer comparison',
          'Radii and thickness only; no independent sample metrology or pose truth.',
        ]
      : [
          'Reference hidden',
          'Playback reveals the source specification; this is not solver privacy.',
        ],
    scoring: [
      'Two evaluator limits',
      'Custom scoring ignores pose; generic scoring rejects the full parameter vector.',
    ],
    limits: [
      'Source explanation only',
      'Saved evidence and fixed controls do not establish raw replay or agent capability.',
    ],
  };
  return (
    <div className={css.aside} data-deflectometry-aside>
      <b>READOUT</b>
      <h3>{text[s.scene][0]}</h3>
      <p>{text[s.scene][1]}</p>
      <small>Pinned Imaging101 refractive-deflectometry source</small>
    </div>
  );
}

import {
  cavityColors as colors,
  cavityCaseLabel,
  cavitySelection,
  cavityFrameLabel,
  cavitySectionPath,
  type CavityState,
} from './clinical-cavity';
import styles from './task-visual.module.css';

function CavitySlices({ state }: { state: CavityState }) {
  const s = cavitySelection(state);
  return (
    <svg
      className={styles.cavitySlices}
      viewBox="0 0 360 186"
      role="img"
      aria-label={`Three calibrated ultrasound sections. ${cavityFrameLabel(state)}. ${s.reveal ? 'Saved output solid cyan and private reference dashed gold.' : state.output > 0.5 ? 'Saved output solid cyan; private reference hidden.' : 'Private reference hidden.'}`}
      data-cavity-images
    >
      {s.data.planes.map((plane, j) => {
        const scale = Math.min(110 / plane.width, 150 / plane.height);
        const x = j * 120 + (120 - plane.width * scale) / 2;
        return (
          <g key={plane.name}>
            <text x={j * 120 + 5} y="14">
              Local {plane.name}
            </text>
            <svg
              x={x}
              y="22"
              width={plane.width * scale}
              height={plane.height * scale}
              viewBox={`0 0 ${plane.width} ${plane.height}`}
            >
              <image
                href={plane.frames[s.imageFrame].png}
                width={plane.width}
                height={plane.height}
              />
              {state.helper > 0.5 && (
                <path
                  d={cavitySectionPath(s.data.initial.sections[j][0])}
                  stroke={colors.helper}
                  strokeWidth={1.2}
                  fill="none"
                />
              )}
              {state.output > 0.5 && (
                <path
                  data-cavity-output-section
                  d={cavitySectionPath(s.output.sections[j][s.frame])}
                  stroke={colors.output}
                  strokeWidth={1.2}
                  fill="none"
                />
              )}
              {s.reveal && (
                <path
                  data-cavity-reference-section
                  d={cavitySectionPath(s.reference.sections[j][s.refFrame])}
                  stroke={colors.reference}
                  strokeWidth={1.2}
                  strokeDasharray="3 2"
                  fill="none"
                />
              )}
            </svg>
          </g>
        );
      })}
      <text x="5" y="184">
        1 mm pixels · local axes, not anatomical planes
      </text>
    </svg>
  );
}
function VolumeCurve({ state }: { state: CavityState }) {
  const s = cavitySelection(state),
    n = s.data.frames;
  const max = Math.ceil((s.data.initial.volume_ml[0] * 1.2) / 20) * 20;
  const x = (i: number) => 38 + (306 * i) / (n - 1),
    y = (v: number) => 128 - (104 * v) / max;
  const indices = Array.from({ length: n }, (_, i) =>
    state.scene === 'shift' ? (i - 5 + n) % n : i,
  );
  const path = (values: number[], order: number[]) =>
    order.map((i, j) => `${j ? 'L' : 'M'}${x(j)},${y(values[i])}`).join('');
  return (
    <svg
      className={styles.cavityCurve}
      viewBox="0 0 360 158"
      role="img"
      aria-label="Cavity volume in mL at every retained frame; vertical cursor matches images and surfaces"
      data-cavity-curve
    >
      {[0, max / 2, max].map((v) => (
        <g key={v}>
          <path d={`M38 ${y(v)}H344`} stroke="#d6ddd8" />
          <text x="31" y={y(v) + 4} textAnchor="end">
            {v}
          </text>
        </g>
      ))}
      <text x="4" y="14">
        mL
      </text>
      <path
        d={path(
          s.output.volume_ml,
          Array.from({ length: n }, (_, i) => i),
        )}
        stroke={colors.output}
        strokeWidth="2.5"
        fill="none"
      />
      {s.reveal && (
        <path
          data-cavity-reference-curve
          d={path(s.reference.volume_ml, indices)}
          stroke={colors.reference}
          strokeWidth="2.5"
          strokeDasharray="5 3"
          fill="none"
        />
      )}
      <path d={`M${x(s.frame)} 20V128`} stroke="#55636b" strokeWidth="1" />
      <circle cx={x(s.frame)} cy={y(s.output.volume_ml[s.frame])} r="3.5" fill={colors.output} />
      {s.reveal && (
        <circle
          cx={x(s.frame)}
          cy={y(s.reference.volume_ml[s.refFrame])}
          r="3.5"
          fill={colors.reference}
        />
      )}
      <text x="38" y="146">
        0
      </text>
      <text x="344" y="146" textAnchor="end">
        {n - 1}
      </text>
      <text x="185" y="154" textAnchor="middle">
        {state.scene === 'shift' || state.scene === 'static'
          ? 'Counterfactual frame index'
          : 'Consecutive acquired frame index'}
      </text>
    </svg>
  );
}
export function ClinicalCavityScene({ state }: { state: CavityState }) {
  return (
    <div className={styles.cavityFallback} data-cavity-projection>
      <strong>{cavityCaseLabel(state)}</strong>
      <p>{cavityFrameLabel(state)}</p>
      <CavitySlices state={state} />
      <small>Live slice fallback · same native frames and fixed 1 mm scale · slowed playback</small>
    </div>
  );
}
const titles = {
  inputs: 'Current images are the tracking input',
  initial: 'Initialization is supplied assistance',
  tracking: 'Track the pixels; integrate the closed surface',
  reference: 'Reveal contraction error',
  patient: 'Transfer the unchanged executable',
  preserved: 'A supplementary preserved case',
  static: 'Repeated images → stationary output',
  shift: 'Five-frame shift → exact permutation',
  judgment: 'A close surface can miss contraction',
  output: 'Keep artifacts, outcomes and limits separate',
};
export function ClinicalCavityOutput({ state }: { state: CavityState }) {
  const s = cavitySelection(state),
    g = s.grade;
  return (
    <aside
      className={`${styles.storyOutput} ${styles.cavityOutput}`}
      data-cavity-output
      data-cavity-case={s.key}
      data-cavity-frame={s.frame}
      data-cavity-image-frame={s.imageFrame}
      data-cavity-reference={s.reveal ? 'revealed' : 'hidden'}
    >
      <strong>{titles[state.scene]}</strong>
      <small>
        {cavityCaseLabel(state)}
        <br />
        {cavityFrameLabel(state)}
      </small>
      <CavitySlices state={state} />
      <div className={styles.cavityReadout} data-with-curve={state.output > 0.5}>
        {state.output > 0.5 && (
          <div>
            <VolumeCurve state={state} />
            {state.scene === 'output' && (
              <small>
                Pre-model: uncertain mild-to-moderate. Final: severe from its own EF. No causal
                inference, strain, etiology or calibrated interval. Source annotations lack
                independent adjudication.
              </small>
            )}
            {state.scene === 'judgment' && (
              <small>
                Static initial surface against moving images. Category also fails. Distance samples
                surface points; it is not continuous Hausdorff distance.
              </small>
            )}
          </div>
        )}
        <div>
          {state.scene === 'inputs' && (
            <>
              <p>
                <b>18 frames · 134 × 82 × 93 voxels/frame.</b> Complete 3D B-mode data with 1 mm
                sampling; these panels show three center sections.
              </p>
              <p>
                Native frames 3–20, about 22.6 volumes/s. The story slows playback and holds
                discrete frames; it does not invent intermediate motion.
              </p>
              <p>
                <code>volumes.npy</code> + <code>geometry.json</code> +{' '}
                <code>initial_mesh.npz</code>. Later references are private.
              </p>
            </>
          )}
          {state.scene === 'initial' && (
            <>
              <p>
                <b>Frame 0: 1,946 vertices, 3,888 triangles.</b> The supplied endocardial cavity
                includes a basal closure. Segmentation at this frame is already given.
              </p>
              <p>
                Initial-surface PCA sets the local mm axes and crop. No later reference sets the
                coordinate frame. Later tracking remains the task.
              </p>
              <p>
                Blue-grey sections show only the public initialization. Dense vertex IDs are
                geometric indices, not measured material points.
              </p>
            </>
          )}
          {state.scene === 'tracking' && (
            <>
              <p>
                <b>Saved output: {s.output.volume_ml[s.frame].toFixed(1)} mL.</b> Sequential 3D
                TV-L1 displacement advects vertices; loop drift is corrected while preserving
                initialization.
              </p>
              <p>
                EF = 100 × (max − min) / max = <b>22.01%</b>. The saved extrema occur at frames 2
                and 10; the initial frame is not the predicted maximum.
              </p>
              <small>
                No flow vectors were retained for this illustration. Only actual saved surfaces are
                animated.
              </small>
            </>
          )}
          {['reference', 'patient', 'preserved'].includes(state.scene) && (
            <>
              {s.reveal ? (
                <>
                  <p>
                    <b>
                      EF {g.ef_pct.toFixed(2)}% vs {g.reference_ef_pct.toFixed(2)}%
                    </b>{' '}
                    reference: <b>{g.ef_error_pp.toFixed(2)} pp error</b> (gate ≤8 pp).
                  </p>
                  <p>
                    Mean distance <b>{g.surface_mean_mm.toFixed(2)} mm</b> passes ≤3 mm; ESV error{' '}
                    <b>{g.esv_error_pct.toFixed(2)}%</b> fails ≤15%. All curves use original float64
                    volumes.
                  </p>
                </>
              ) : (
                <p>
                  The gold source annotation and its volume curve remain hidden until the reader
                  reveal.
                </p>
              )}
              {state.scene !== 'reference' && (
                <small>
                  {s.data.frames} frames · a separate source case with its own supplied
                  initialization.{' '}
                  {state.scene === 'preserved'
                    ? 'Supplementary case added after dispatch, before output inspection.'
                    : 'No model feedback or additional model attempt.'}
                </small>
              )}
            </>
          )}
          {state.scene === 'static' && (
            <>
              <p>
                <b>Saved RMS motion 0 mm · EF 0%.</b> The retained executable received frame-0
                pixels repeated 18 times and kept every vertex stationary.
              </p>
              <p>
                Passes the predeclared ≤0.25 mm motion and ≤1 pp EF response checks. This artificial
                input is not a biological diagnosis.
              </p>
            </>
          )}
          {state.scene === 'shift' && (
            <>
              <p>
                <b>New frame t = old (t − 5) mod 18.</b> The declared initial mesh moves to index 5.
                The image, output and volume curve all follow that permutation.
              </p>
              <p>
                Undoing the shift gives <b>exactly identical points and 0 mL volume MAE</b>. This
                input response does not establish correct contraction.
              </p>
            </>
          )}
          {state.scene === 'judgment' && (
            <>
              <table>
                <thead>
                  <tr>
                    <th>Gate</th>
                    <th>Value / limit</th>
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ['Mean distance', g.surface_mean_mm, 3, 'mm', g.gates.surface_mean],
                    ['Max frame p95', g.surface_p95_mm, 6, 'mm', g.gates.surface_p95],
                    ['EF error', g.ef_error_pp, 8, 'pp', g.gates.ef],
                    ['EDV error', g.edv_error_pct, 15, '%', g.gates.edv],
                    ['ESV error', g.esv_error_pct, 15, '%', g.gates.esv],
                  ].map(([label, value, limit, unit, pass]) => (
                    <tr key={String(label)}>
                      <th>{label}</th>
                      <td>
                        {Number(value).toFixed(2)} / {limit} {unit}
                      </td>
                      <td>{pass ? 'Pass' : 'Fail'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
          {state.scene === 'output' && (
            <>
              <p>
                <code>prediction.npz</code>: points[T,N,3] in mm, shared faces[M,3]. Return{' '}
                <code>solve.py</code>, <code>method.md</code>, volume/EF <code>summary.json</code>{' '}
                and saved pre-model assessment.
              </p>
              <p>
                <b>One completed Sol/xhigh attempt · original reward 0.</b> Valid artifacts and
                input response coexist with failed EF, ESV and category checks.
              </p>
            </>
          )}
        </div>
      </div>
      <small className={styles.cavityAttribution}>
        Elias Stenhede et al. · EchoXFlow · CC BY-NC-SA 4.0
      </small>
    </aside>
  );
}

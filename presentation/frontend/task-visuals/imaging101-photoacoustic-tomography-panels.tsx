import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  signalsImage,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  type ImagingPhotoacousticState,
} from './imaging101-photoacoustic-tomography';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging101-photoacoustic-tomography.module.css';
function Trace({ m }: { m: number }) {
  const values = source.native_profiles.values[m],
    xy = source.native_profiles.detector_xy_mm[m];
  return (
    <figure className={css.native}>
      <svg
        viewBox="0 0 270 165"
        role="img"
        aria-label={`Native pressure time trace detector ${branches[m]}; no reconstructed image`}
      >
        <path d="M14 8V148H258" stroke="#657984" fill="none" />
        <line x1="14" x2="258" y1="78" y2="78" stroke="#b2c2ce" />
        <polyline
          points={values.map((v, j) => `${14 + (j * 244) / 1300},${78 - v * 650}`).join(' ')}
          stroke="#57d1cc"
          strokeWidth="1.5"
          fill="none"
        />
        <text x="17" y="17" fill="#dfeef3" fontSize="10">
          signed pressure (a.u.)
        </text>
        <text x="174" y="161" fill="#dfeef3" fontSize="10">
          time 0–65 µs →
        </text>
      </svg>
      <figcaption>
        Teal: all 1,301 source samples; gray: zero. Detector ({xy[0].toFixed(1)}, {xy[1].toFixed(1)}
        ) mm.
      </figcaption>
    </figure>
  );
}
export function ImagingPhotoacousticScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingPhotoacousticState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [showRules, setShowRules] = useState(false);
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (state.scene !== 'reference' || state.frame < previous.current) setShowRules(false);
    previous.current = state.frame;
  }, [state.frame, state.scene]);
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-imaging-photoacoustic-scene={state.scene}
      data-imaging-photoacoustic-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Synthetic acoustic input; reconstruction absent</h3>
          <figure className={css.native}>
            <img
              src={signalsImage}
              alt="Native center-y pressure slice: time columns, detector-x rows; red positive, blue negative, white zero"
            />
            <figcaption>
              31 detector-x rows × 1,301 time columns, center-y index 15. Blue / red: negative /
              positive pressure, fixed ±0.1 a.u.; white zero.
            </figcaption>
          </figure>
          <p>
            961 detectors · 20 MHz · 65 µs. Native signed signals from four simulated spheres; no
            tissue scan or calibrated pressure.
          </p>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>From arrival time to source backprojection rules</h3>
          <nav className={css.controls} aria-label="Photoacoustic steps">
            {steps.map((s, j) => (
              <button
                key={s}
                type="button"
                aria-pressed={i === j}
                disabled={!onSeekFrame}
                onClick={() => onSeekFrame?.(operationFrame(plan, j, m))}
              >
                {s}
              </button>
            ))}
          </nav>
          <div className={css.socket}>
            {i === 0 ? (
              <>
                <b>t = distance / c; sample = round(distance × fs / c)</b>
                <p>
                  c = 1,484 m/s; sampling 20 MHz; detectors z = 0, target plane z = 15 mm.
                  Coordinates metres, time seconds.
                </p>
                <small>
                  Authored distance 15 mm → 10.108 µs → index {fixture.toy_sample_index}. Units
                  fixture only; no reconstructed pixel or native target claim.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Select native detector trace">
                  {branches.map((s, j) => (
                    <button
                      key={s}
                      type="button"
                      aria-pressed={m === j}
                      disabled={!onSeekFrame}
                      onClick={() => onSeekFrame?.(operationFrame(plan, 1, j))}
                    >
                      {s}
                    </button>
                  ))}
                </nav>
                <Trace m={m} />
              </>
            ) : (
              <>
                <b>b = 2p − 2tc IFFT(−ik FFT(p)); k = 2πf / c</b>
                <p>
                  Nearest arrival sample; solid-angle weights, then weight-sum and complex peak
                  normalization. Grid 41 × 41, 0.5 mm spacing.
                </p>
                <small>
                  Signed derivative; no FFT or backprojection run. No optical fluence model,
                  iterative solver, positivity guarantee or calibrated absorption.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual reconstruction.npy absent</h3>
          <code>output/reconstruction.npy · 41 × 41 target plane</code>
          <p>
            Participant image / score empty. Saved source artifacts are historical examples; no
            tissue finding or recovered pressure here.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later source-truth and crop rules</h3>
          <button
            type="button"
            aria-expanded={referenceVisible(state, showRules)}
            aria-controls="pa-reader-rules"
            disabled={state.reference <= 0.5}
            onClick={() => setShowRules(!showRules)}
          >
            {showRules ? 'Hide source rules' : 'Reveal source rules'}
          </button>
          {referenceVisible(state, showRules) ? (
            <div
              id="pa-reader-rules"
              className={css.socket}
              data-imaging-photoacoustic-reference-revealed
            >
              <b>{reference.role}</b>
              <p>
                Binary geometric support is solver-visible, not calibrated pressure. Source crop: 33
                × 33 = 1,089 pixels; generic full image: 1,681 pixels.
              </p>
              <small>
                Both include 101 positive support pixels. Reference / reconstruction images and
                metric absent; exit / backward / reset covers rules.
              </small>
            </div>
          ) : (
            <p>Reader rules covered; truth/output images absent.</p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Keep synthetic acoustics separate from tissue claims</h3>
          <p>{source.actual_data_gap}</p>
          <small>
            No reconstructed finding, fluence / absorption inference or numerical performance.
          </small>
        </>
      )}
    </section>
  );
}
export function ImagingPhotoacousticOutput({ state }: { state: ImagingPhotoacousticState }) {
  return (
    <aside
      data-imaging-photoacoustic-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Synthetic acoustic measurement contract</b>
      <p>Exact native signed pressure slice and detector traces.</p>
      <p>Participant image / score absent; no calibrated tissue signal.</p>
      <small>
        Source rules require an explicit reveal in the reference chapter; backward seek, scene exit
        and Reset cover them before paint. No private image or answer is revealed.
      </small>
    </aside>
  );
}

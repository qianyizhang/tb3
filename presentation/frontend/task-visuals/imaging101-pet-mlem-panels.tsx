import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  sinogramImage,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  type ImagingPetMlemState,
} from './imaging101-pet-mlem';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging101-pet-mlem.module.css';
function Profile({ m }: { m: number }) {
  const values = source.native_profiles.values[m],
    b = source.native_profiles.background;
  return (
    <figure className={css.native}>
      <svg
        viewBox="0 0 270 165"
        role="img"
        aria-label={`Native scaled-count radial profile at ${source.native_profiles.angles_deg[m]} degrees; no reconstructed activity`}
      >
        <path d="M14 8V148H258" stroke="#657984" fill="none" />
        <line
          x1="14"
          x2="258"
          y1={148 - (b * 140) / 220}
          y2={148 - (b * 140) / 220}
          stroke="#b2c2ce"
          strokeWidth="2"
        />
        <polyline
          points={values
            .map((v, j) => `${14 + (j * 244) / 127},${148 - (v * 140) / 220}`)
            .join(' ')}
          stroke="#57d1cc"
          strokeWidth="2"
          fill="none"
        />
        <text x="17" y="17" fill="#dfeef3" fontSize="10">
          y=C / 1000
        </text>
        <text x="183" y="161" fill="#dfeef3" fontSize="10">
          radial index →
        </text>
      </svg>
      <figcaption>
        Teal: native observed y; gray: r={b.toFixed(3)}. 128 radial bins; {branches[m]}.
      </figcaption>
    </figure>
  );
}
export function ImagingPetMlemScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingPetMlemState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [showRules, setShowRules] = useState(false);
  const previousFrame = useRef(state.frame);
  const previousBeat = useRef(state.beatId);
  const stable =
    state.scene === 'reference' &&
    previousBeat.current === state.beatId &&
    state.frame >= previousFrame.current;
  useLayoutEffect(() => {
    if (!stable) setShowRules(false);
    previousFrame.current = state.frame;
    previousBeat.current = state.beatId;
  }, [state.frame, state.scene, state.beatId, stable]);
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-imaging-pet-mlem-scene={state.scene}
      data-imaging-pet-mlem-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Actual synthetic sinogram; activity image absent</h3>
          <div className={css.two}>
            <figure className={css.native}>
              <img
                src={sinogramImage}
                alt="Native synthetic sinogram: radial rows, angle columns; grayscale scaled counts, no activity reconstruction"
              />
              <figcaption>
                Black 0 → white 220: y=C / 1000. 128 radial rows × 120 angle columns, 0°…178.5°.
              </figcaption>
            </figure>
            <div>
              <b>15,360 measurement bins ·relative units</b>
              <p>
                Poisson draws divided by 1,000. Background is additive in the mean; no patient scan
                or calibrated uptake.
              </p>
              <small>No projection, backprojection, reconstruction or score computed.</small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Separate measured bins from multiplicative image updates</h3>
          <nav className={css.controls} aria-label="PET MLEM steps">
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
                <b>C ~ Poisson(1000 × (A x + r)); y=C / 1000</b>
                <p>
                  Uniform source background r≈10.928 relative units; not subtracted before the fit.
                  No attenuation, separate scatter or detector normalization.
                </p>
                <small>
                  Authored A=3, x=2, r=2, y=8 gives x_new={fixture.toy_updated_x}; scalar rule only,
                  no native activity image.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Select native projection angle profile">
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
                <div className={css.two}>
                  <Profile m={m} />
                  <div>
                    <b>Background and observations share one scale</b>
                    <p>
                      Angles 0° / 90° / 178.5°; native values only. Some bins can be below
                      background; no clipping/subtraction here.
                    </p>
                    <small>
                      Display choice never changes acquisition, draws noise or runs a solver. Radial
                      index is not mm.
                    </small>
                  </div>
                </div>
              </>
            ) : (
              <>
                <b>x←x / (B1) × B(y / (Ax+r))</b>
                <p>
                  MLEM: 50 updates. OSEM: 10 cycles × 6 interleaved subsets = 60 updates, 20 angles
                  per subset.
                </p>
                <small>
                  B is unfiltered iradon, not verified exact transpose or FBP. Floors 1e−10; no
                  explicit prior. MLEM history is pre-update, OSEM post-cycle; no convergence claim.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual reconstruction.npy absent</h3>
          <code>output/reconstruction.npy ·128 × 128 relative activity</code>
          <p>
            Participant image / score empty. Saved source MLEM/OSEM artifacts are separate from
            fresh execution or clinical uptake.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later source-truth and evaluator denominators</h3>
          <button
            type="button"
            aria-expanded={stable && showRules}
            aria-controls="pet-reader-rules"
            disabled={state.reference <= 0.5}
            onClick={() => setShowRules(!showRules)}
          >
            {stable && showRules ? 'Hide source rules' : 'Reveal source rules'}
          </button>
          {referenceVisible(state, stable && showRules) ? (
            <div
              id="pet-reader-rules"
              className={css.socket}
              data-imaging-pet-mlem-reference-revealed
            >
              <b>{reference.role}</b>
              <p>
                Source mask: 7,379 positive pixels, range 5.5. Generic: 16,384 pixels, range 6; no
                source mask or scale normalization.
              </p>
              <p>
                Source baseline thresholds select best NCC and NRMSE independently; matched live
                comparison unverified.
              </p>
              <small>
                No activity or truth image, likelihood run, uptake value or score displayed. Exit /
                backward / reset covers rules.
              </small>
            </div>
          ) : (
            <p>Reader rules covered; truth/output absent.</p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Keep synthetic counts separate from uptake claims</h3>
          <p>{source.actual_data_gap}</p>
          <small>
            Native measurements are input evidence only. No reconstructed finding, likelihood
            monotonicity, clinical uptake or numerical performance.
          </small>
        </>
      )}
    </section>
  );
}
export function ImagingPetMlemOutput({ state }: { state: ImagingPetMlemState }) {
  return (
    <aside
      data-imaging-pet-mlem-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Synthetic PET measurement contract</b>
      <p>Native scaled-count sinogram and background profiles.</p>
      <p>Participant activity image / score absent; no patient or SUV evidence.</p>
      <small>
        Reader rules require an explicit late reveal; backward / exit / reset covers them.
      </small>
    </aside>
  );
}

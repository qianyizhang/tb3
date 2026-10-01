import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  images,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  type ImagingToothGridrecState,
} from './imaging101-xray-tooth-gridrec';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging101-xray-tooth-gridrec.module.css';
function ReaderRules({ state }: { state: ImagingToothGridrecState }) {
  const [requested, setRequested] = useState(false);
  const previous = useRef({ frame: state.frame, beat: state.beatId });
  const backward = state.frame < previous.current.frame || state.beatId !== previous.current.beat;
  useLayoutEffect(() => {
    if (backward) setRequested(false);
    previous.current = { frame: state.frame, beat: state.beatId };
  }, [state.frame, state.beatId, backward]);
  const visible = referenceVisible(state, requested && !backward);
  return (
    <>
      <button
        type="button"
        disabled={state.reference <= 0.5}
        aria-pressed={visible}
        onClick={() => setRequested((v) => !v)}
      >
        {visible ? 'Hide public reference rules' : 'Reveal public reference rules'}
      </button>
      {visible ? (
        <div className={css.socket} data-imaging-tooth-gridrec-reference-revealed>
          <b>{reference.role}</b>
          <p>
            Saved reference equals solver-visible baseline. Source metrics use first slice, 409,600
            pixels; filesystem generic uses both slices, 819,200.
          </p>
          <small>
            Not independent truth. No-filesystem requires absent ground_truth.npy; no listed
            boundary file. Actual output and score absent.
          </small>
        </div>
      ) : (
        <p>Public reference rules covered; actual output absent.</p>
      )}
    </>
  );
}
function Native({ index = 0 }: { index?: number }) {
  return (
    <figure className={css.native}>
      <img
        src={images[index]}
        alt={`Native tooth raw detector count matrix, detector row ${index}, angle rows and detector columns; no log or reconstruction`}
        data-imaging-tooth-gridrec-native={index}
      />
      <figcaption>
        Row {index} · angle rows / detector columns; stride 2 / 4. Gray:{' '}
        {source.native_display.raw_min}–{source.native_display.raw_max} raw counts. No calibrated
        photons.
      </figcaption>
    </figure>
  );
}
function Calibration() {
  const profiles = source.native_display.calibration_profiles;
  return (
    <figure className={css.native}>
      <svg
        viewBox="0 0 320 100"
        role="img"
        aria-label="Native first flat and dark frame row zero detector profiles, raw counts zero to 35000; not stack means"
      >
        {profiles.map((v, i) => (
          <polyline
            key={v.key}
            points={v.values.map((y, x) => `${(x / 639) * 320},${95 - (y / 35000) * 85}`).join(' ')}
            fill="none"
            stroke={i === 0 ? '#54d3dd' : '#aebec8'}
            strokeWidth="1.5"
          />
        ))}
      </svg>
      <figcaption>
        Teal flat / gray dark: frame 0, row 0, all 640 detector cells. Vertical 0–35,000 counts;
        these are NOT ten-frame means.
      </figcaption>
    </figure>
  );
}
export function ImagingToothGridrecScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingToothGridrecState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-imaging-tooth-gridrec-scene={state.scene}
      data-imaging-tooth-gridrec-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Native tooth counts; calibrated attenuation / result absent</h3>
          <div className={css.two}>
            <Native />
            <div>
              <b>181 angles × 2 rows × 640 detectors</b>
              <p>
                231,680 native count cells, not an attenuation cross-section. Source identifies an
                experimental tooth specimen.
              </p>
              <small>
                No detector/voxel spacing, photon calibration, energy, independent truth or
                participant output.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Separate measured count rows from inverse reconstruction</h3>
          <nav className={css.controls} aria-label="Tooth CT steps">
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
                <b>T = (I − mean(D)) / (mean(F) − mean(D))</b>
                <p>
                  Ten flat and ten dark frames. Zero denominator → 1; −log clips only below 10⁻¹².
                  Transmission above 1 stays above 1.
                </p>
                <small>
                  Authored I = 500, F = 1000, D = 100 gives T ={' '}
                  {fixture.toy_transmission.toFixed(4)}; no native correction/log or new sinogram
                  computed.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Select native count input">
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
                {m < 2 ? <Native index={m} /> : <Calibration />}
              </>
            ) : (
              <>
                <b>Source runs pixel-driven FBP, not a TomoPy gridrec call</b>
                <p>
                  Centre: first / reversed last correlation, then 20 variance-based FBP trials. Init
                  290 unused; midpoint 319.5 detector pixels.
                </p>
                <small>
                  640 detectors → padded FFT length 2048; ramp |frequency|, factor π/181, circular
                  radius 304 pixels. Rules only; no FFT, centre estimate or inverse executed.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Participant reconstruction absent</h3>
          <code>output/reconstruction.npy · (2, 640, 640)</code>
          <p>
            819,200 pixel-scaled values intended; calibrated attenuation units unknown. Saved
            baseline, centre and sinogram are prior provenance.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later reference identity and metric scope</h3>
          <ReaderRules state={state} key={state.beatId} />
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Resolve calibration, runtime and independent reference</h3>
          <p>{source.actual_data_gap}</p>
          <small>
            No reconstructed anatomy, resolution, clinical findings or source-gridrec equivalence
            claim.
          </small>
        </>
      )}
    </section>
  );
}
export function ImagingToothGridrecOutput({ state }: { state: ImagingToothGridrecState }) {
  return (
    <aside
      data-imaging-tooth-gridrec-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Native projections; participant output empty</b>
      <p>Count rows and calibration profiles only.</p>
      <small>
        Independent truth / calibrated attenuation absent. Reference rules reader-controlled; reset
        / exit covers.
      </small>
    </aside>
  );
}

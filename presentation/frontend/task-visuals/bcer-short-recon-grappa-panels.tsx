import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  resetOnBackward,
  type BcerGrappaState,
} from './bcer-short-recon-grappa';
import type { StoryPlan } from '../contracts.generated';
import css from './bcer-short-recon-grappa.module.css';
function Mask({ mode }: { mode: number }) {
  return (
    <figure className={css.mask}>
      <svg
        viewBox="0 0 342 112"
        role="img"
        aria-label="Symbolic two-coil sampling layout; horizontal ky and vertical kx frequency indices"
      >
        <text x="18" y="12" fill="#d8ecf5" fontSize="10">
          ky frequency index → · each coil shares this symbolic mask
        </text>
        {Array.from({ length: fixture.kx }, (_, kx) =>
          Array.from({ length: fixture.ky }, (_, ky) => (
            <rect
              key={`${kx}-${ky}`}
              x={18 + ky * 9.5}
              y={20 + kx * 9.5}
              width="8"
              height="8"
              fill={
                ky >= fixture.ACS_bounds[0] && ky < fixture.ACS_bounds[1]
                  ? '#57d1cc'
                  : fixture.masks[mode][ky]
                    ? '#88b4e0'
                    : '#526373'
              }
            />
          )),
        )}
        <text x="18" y="108" fill="#d8ecf5" fontSize="10">
          kx rows: 8 · ky columns: 32 · 2 coils · no amplitudes/patient data
        </text>
      </svg>
      <figcaption>
        Blue = sampled outside ACS · teal = central ACS24 · gray = missing. These are frequency
        samples, not missing image pixels.
      </figcaption>
    </figure>
  );
}
export function BcerGrappaScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: BcerGrappaState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [readerRequested, setReaderRequested] = useState(false);
  const previous = useRef({ frame: state.frame, beat: state.beatId });
  useLayoutEffect(() => {
    if (
      previous.current.beat !== state.beatId ||
      resetOnBackward(previous.current.frame, state.frame)
    )
      setReaderRequested(false);
    previous.current = { frame: state.frame, beat: state.beatId };
  }, [state.frame, state.beatId]);
  const visible = referenceVisible(state, readerRequested);
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section className={css.scene} data-bcer-grappa-scene={state.scene}>
      {state.scene === 'input' && (
        <>
          <h3>No matching cardiac H5; symbolic coil/mask contract</h3>
          <Mask mode={0} />
          <p>
            Example 8 kx × 32 ky × 2 coils; complex axes and calibration must be verified from an
            actual H5. No representative prostate image stands in for cardiac k-space.
          </p>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Calibration and mode decide what reconstruction means</h3>
          <nav className={css.controls} aria-label="BCER GRAPPA contract steps">
            {steps.map((s, j) => (
              <button
                data-bcer-grappa-operation-step={j}
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
                <b>Frame (kx,ky,coils); slice/time order separate</b>
                <p>
                  Last two H5 axes presumed kx/ky; last remaining axis ≤64 chosen as coils unless
                  hint. Nonspatial order/spacing metadata unresolved; placeholder 1 mm is not
                  patient geometry.
                </p>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Explore BCER reconstruction rules">
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
                  <Mask mode={m} />
                  <div>
                    <b>
                      {fixture.sampled_lines[m]}/32 ky lines sampled; {fixture.sampled_fraction[m]}
                    </b>
                    {m === 0 ? (
                      <p>
                        Below 0.90 energy predicate → GRAPPA branch. Example R2 + ACS24 retains 28
                        lines; net 32/28, not 2× acquisition acceleration.
                      </p>
                    ) : m === 1 ? (
                      <p>
                        Fully sampled → skip GRAPPA; IFFT+RSS only. Output file does not prove a
                        kernel was applied.
                      </p>
                    ) : (
                      <p>
                        If pygrappa raises → zero-filled frame; count failed separately. This is a
                        hypothetical rule, no observed failure or reconstruction.
                      </p>
                    )}
                    <small>
                      BCER ACS24 vs FAQ 16-line/16×16 needs case-specific reconciliation; no
                      matching calibration.
                    </small>
                  </div>
                </div>
              </>
            ) : (
              <>
                <b>ifftshift → IFFT2 → ifftshift → RSS magnitude</b>
                <p>
                  sqrt(sum|coil image|²), float32. Optional retrospective decimation/crop off by
                  default; crop needs explicit request and shifts origin. No measured image output
                  shown.
                </p>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual reconstructed_nifti absent</h3>
          <code data-bcer-grappa-output-schema>
            artifacts/grappa/reconstructed_&lt;h5stem&gt;.nii.gz
          </code>
          <p>
            Actual mode, image, frame counts and quality null. Preserve source_key, axes/order,
            spacing_source, crop and applied/skipped/failed counts for a real run.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Mode/grader rules; no pristine cardiac truth</h3>
          <button
            className={css.reveal}
            type="button"
            disabled={state.reference <= 0.5}
            aria-pressed={visible}
            onClick={() => setReaderRequested((value) => !value)}
          >
            {visible ? 'Cover public mode rule' : 'Reveal public mode rule'}
          </button>
          {visible ? (
            <div className={css.socket} data-bcer-grappa-reference-revealed>
              <b>{reference.role}</b>
              <p>
                GRAPPA-applied, sampled-skip, image-passthrough and frame-zero-fill differ. Artifact
                success does not validate method or image fidelity.
              </p>
              <p>
                Stage/path/nonempty only; no applied-kernel, axes/spacing or PSNR/SSIM check. Read
                failure may fall back to file size.
              </p>
            </div>
          ) : (
            <p data-bcer-grappa-reference-hidden>
              Public rule stays covered until requested; no clean/private image is bundled.
            </p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Matching measurement, calibration and quality absent</h3>
          <p>{source.actual_data_gap}</p>
          <div className={css.socket}>
            <b>Verify H5 format and mode before claiming GRAPPA</b>
            <p>
              No actual k-space, ACS coefficients, reconstruction, pristine reference or patient
              findings. Mode diagram and mask are symbolic.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
export function BcerGrappaOutput({ state }: { state: BcerGrappaState }) {
  return (
    <aside data-bcer-grappa-output={state.scene} className={css.output}>
      <b>Cardiac H5 reconstruction contract</b>
      <p>Actual reconstructed_nifti empty. Symbolic masks only.</p>
      <p>Applied/skip/passthrough/failure modes stay distinct.</p>
      <small>
        Public mode rule is reader-controlled in its later chapter. Backward seek, exit and reset
        cover it; no private image is bundled.
      </small>
    </aside>
  );
}

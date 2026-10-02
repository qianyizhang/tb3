import upstream from '../../task-explorer/automedbench-full-synthrad2025-mrct-task/upstream-mr-slice.png';
import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  steps,
  operationIndex,
  operationFrame,
  referenceVisible,
  resetOnBackward,
  type AutomedSynthradMrctState,
} from './automedbench-full-synthrad2025-mrct-task';
import type { StoryPlan } from '../contracts.generated';
import css from './automedbench-full-synthrad2025-mrct-task.module.css';
function RoleDiagram() {
  const roles = [
    ['mr', 'Public MRI', 'Arbitrary units · absent', 'mr.nii.gz'],
    ['mask', 'Public outline mask', 'Binary ROI · absent', 'mask.nii.gz'],
    ['sct', 'Expected synthetic CT', 'HU · output unset', 'sct.nii.gz'],
    ['private', 'Private paired CT', 'HU · reference absent', 'ct.nii.gz'],
  ];
  return (
    <figure
      className={css.roles}
      aria-label="Symbolic MR, helper mask, synthetic CT and private evaluation roles"
    >
      <div className={css.roleGrid}>
        {roles.map(([role, title, units, file]) => (
          <div className={css.role} data-mrct-role={role} key={role}>
            <b>{title}</b>
            <div className={css.roleCells} aria-hidden="true">
              {[0, 1, 2, 3].map((i) => (
                <span key={i}>{role === 'mr' ? '?' : ''}</span>
              ))}
            </div>
            <code>{file}</code>
            <small>{units}</small>
          </div>
        ))}
      </div>
      <figcaption>
        MR + mask → required sCT. Private CT → evaluation only. Symbolic role sockets; no anatomy,
        model conversion, patient pixels or predicted HU values.
      </figcaption>
    </figure>
  );
}
export function AutomedSynthradMrctScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedSynthradMrctState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [show, setShow] = useState(false);
  const [format, setFormat] = useState(false);
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  const [metric, setMetric] = useState<'MAE' | 'PSNR' | 'SSIM'>('MAE');
  const previous = useRef({ frame: state.frame, beat: state.beatId, scene: state.scene });
  useLayoutEffect(() => {
    if (
      previous.current.beat !== state.beatId ||
      previous.current.scene !== state.scene ||
      resetOnBackward(previous.current.frame, state.frame)
    ) {
      setShow(false);
      setFormat(false);
      setTier('lite');
      setMetric('MAE');
    }
    previous.current = { frame: state.frame, beat: state.beatId, scene: state.scene };
  }, [state.frame, state.beatId, state.scene]);
  const stable =
    previous.current.beat === state.beatId &&
    previous.current.scene === state.scene &&
    state.frame >= previous.current.frame;
  const i = operationIndex(state);
  return (
    <section className={css.scene} data-mrct-scene={state.scene}>
      <RoleDiagram />
      {state.scene === 'input' && (
        <>
          <h3>MR → synthetic CT, not super-resolution</h3>
          <div className={css.socket}>
            <b>mr.nii.gz + mask.nii.gz → sct.nii.gz</b>
            <p>
              Public MRI: arbitrary intensity. Outline mask: helper ROI. Private paired CT: HU,
              absent. Actual input/output/reference voxels: 0.
            </p>
          </div>
          <p>
            Upstream training MHA does not establish Full HN20 selection, NIfTI conversion, paired
            geometry or partition.
          </p>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Inspect cross-modality synthesis contracts</h3>
          <nav className={css.controls} aria-label="MRCT contract steps">
            {steps.map((s, j) => (
              <button
                key={s}
                type="button"
                data-mrct-operation-step={j}
                aria-pressed={i === j}
                disabled={!onSeekFrame}
                onClick={() => onSeekFrame?.(operationFrame(plan, j))}
              >
                {s}
              </button>
            ))}
          </nav>
          <div className={css.socket} data-mrct-currentstage={i}>
            {i === 0 ? (
              <>
                <b>Mask guides ROI; it is not the CT answer</b>
                <p>
                  Teal = public MR role, arbitrary units. Outline = absent sCT in HU. Gray = absent
                  private CT. All roles are symbolic; no pixel conversion or anatomy.
                </p>
              </>
            ) : i === 1 ? (
              <>
                <b>Same shape does not prove alignment</b>
                <p>
                  No 2× downsample/resize contract. Full NIfTI affine, spacing, orientation,
                  registration and MR normalization are unknown. Checker defaults to MR shape, not
                  physical geometry.
                </p>
              </>
            ) : i === 2 ? (
              <>
                <nav className={css.controls} aria-label="MRCT assistance">
                  {(['lite', 'standard'] as const).map((t) => (
                    <button
                      type="button"
                      key={t}
                      aria-pressed={tier === t}
                      onClick={() => setTier(t)}
                    >
                      {t}
                    </button>
                  ))}
                  <button type="button" aria-expanded={format} onClick={() => setFormat(!format)}>
                    Format boundary
                  </button>
                </nav>
                <p data-mrct-tier>
                  {tier === 'lite'
                    ? 'Prescribed VBoussot HN CV_0–CV_4 ensemble + Prediction.yml; checkpoint absent.'
                    : 'Compare HN VBoussot, aehrc HN and AB-TH fallback; inference-only, no training.'}
                </p>
                {format && (
                  <p data-mrct-format>
                    Finite loadable 3D, same MR shape if MR exists. No affine check. Missing output,
                    constant or extreme HU can leave format valid; completion/scoring separate.
                  </p>
                )}
              </>
            ) : (
              <>
                <nav className={css.controls} aria-label="MRCT metric rules">
                  {(['MAE', 'PSNR', 'SSIM'] as const).map((m) => (
                    <button
                      type="button"
                      key={m}
                      aria-pressed={metric === m}
                      onClick={() => setMetric(m)}
                    >
                      {m}
                    </button>
                  ))}
                </nav>
                <p data-mrct-metric>
                  {metric === 'MAE'
                    ? 'MAE/RMSE: un-clipped HU error, mask >0.5 ROI; empty ROI falls back whole volume. Valid-case means.'
                    : metric === 'PSNR'
                      ? 'PSNR: range 4095 HU, un-clipped error; perfect infinity excluded from finite-case mean.'
                      : 'SSIM: clipped CT [−1024,3071], full x-y slices; mask sum<16/min dimension<7 skipped, optional backend. Available-slice then available-case mean.'}
                </p>
                <small>
                  Rules only; no metric computed. Supplied IDs set completion; 20 not enforced.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Participant synthetic CT remains absent</h3>
          <code data-mrct-output-schema>agents_outputs/&lt;case_id&gt;/sct.nii.gz</code>
          <div className={css.socket}>
            <b>Expected HU-domain volume, not an acquired CT</b>
            <p>
              No generated sCT, private target, normalization inverse, reconstruction or metric is
              bundled.
            </p>
          </div>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Reader-only evaluator rules</h3>
          <button type="button" aria-expanded={show} onClick={() => setShow(!show)}>
            {show ? 'Hide upstream MR and rules' : 'Reveal upstream MR and source rules'}
          </button>
          {referenceVisible(state, show && stable) ? (
            <div className={css.socket} data-mrct-reference-revealed>
              <figure className={css.native}>
                <img
                  src={upstream}
                  alt="Upstream public training MR 1HNC117 native k20 stride 3 grayscale display, not Full MRCT input or synthetic CT"
                />
                <figcaption>
                  Upstream MR 1HNC117: k20, i/j stride 3, 101², plane-local normalization. CC BY-NC
                  4.0; Thummerer et al., DOI 10.5281/zenodo.15373853. No paired CT or Full
                  membership.
                </figcaption>
              </figure>
              <b>No CT image or private answer revealed</b>
              <p>{reference.rating}</p>
              <small>
                Named clinical_score is clipped SSIM × completion, not medical validation. Rules
                reset before paint on backward seek, beat exit and reset.
              </small>
            </div>
          ) : (
            <p>
              Private paired CT stays absent. Explicit reader reveal required even in this chapter.
            </p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Recover exact pairs before a data view</h3>
          <div className={css.socket}>
            <p>{source.actual_data_gap}</p>
            <small>
              Generic prompts naming Dice and organ/lesion outputs conflict with task-specific
              sct.nii.gz. No segmentation, SR or LDCT defaults borrowed.
            </small>
          </div>
        </>
      )}
    </section>
  );
}
export function AutomedSynthradMrctOutput({ state }: { state: AutomedSynthradMrctState }) {
  return (
    <aside className={css.output} data-mrct-output>
      <b>MRCT contract only</b>
      <p>Input: MRI arbitrary units + outline mask. Output: synthetic CT HU, absent.</p>
      <small>
        Private CT, model outputs and measured quality remain unavailable. Current step:{' '}
        {state.scene === 'operation' ? operationIndex(state) + 1 : '—'}.
      </small>
    </aside>
  );
}

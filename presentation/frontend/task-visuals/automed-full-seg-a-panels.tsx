import {
  segAPacks,
  segAIndex,
  segARevealed,
  type AutoMedSegAState,
  type SegAPack,
} from './automed-full-seg-a';
import shared from './task-visual.module.css';
import css from './automed-full-seg-a.module.css';
const TITLES = {
  input: 'Start with the unmarked volume',
  stack: 'Move through native slices',
  labels: 'Map labels to one output grid',
  schema: 'Produce a NIfTI label map',
  reference: 'Inspect the upstream label separately',
  limits: 'Keep the benchmark boundary clear',
} as const;
const ROLE = {
  aeropath:
    'Lung (1) and airway (2) are two scored structures. The source masks overlap, so airway 2 overwrites lung 1 in the combined map.',
  colon: 'Only the primary colon cancer is class 1. A whole-colon organ mask is not the target.',
  feta: 'The task asks for seven fetal brain tissues in T2 MRI, IDs 1–7. No authorized image or label is available here.',
  heart:
    'Class 1 is the left atrium in cardiac MRI. The task config calls it “heart,” but it does not ask for the entire heart.',
};
function Slice({
  p,
  index,
  reference = false,
}: {
  p: SegAPack;
  index: number;
  reference?: boolean;
}) {
  if (!p.images.length)
    return (
      <div className={css.missing} data-sega-source="unavailable">
        <b>No FeTA MRI acquired</b>
        <span>
          Official access requires the research/education agreement and Synapse route. This blank
          grid is not a fetal image.
        </span>
      </div>
    );
  const item = p.source.slices[index];
  return (
    <figure className={css.slice} data-sega-source="upstream-volume">
      <div className={css.head}>
        <b>{p.source.input_filename} · source slice</b>
        <span>
          native k={item.native_k} · {p.source.axis_codes} {p.key === 'heart' ? 'header' : 'axes'}
        </span>
      </div>
      <div className={css.canvas}>
        <img
          src={p.images[index]}
          alt={`Unmarked official upstream ${p.key} source slice k ${item.native_k}`}
        />
        {reference && (
          <img
            className={css.overlay}
            src={p.labels[index]}
            alt=""
            data-sega-reference="upstream-source-label"
          />
        )}
      </div>
      <figcaption>
        {p.source.shape_ijk?.join('×')} voxels ·{' '}
        {p.source.voxel_spacing_mm?.map((x) => x.toFixed(2)).join('×')} mm · native voxel sampling ·
        PNG scaled for display
      </figcaption>
    </figure>
  );
}
function Input({ p }: { p: SegAPack }) {
  return (
    <div className={css.two} data-sega-input>
      <Slice p={p} index={p.images.length ? 1 : 0} />
      <div className={css.card}>
        <b>Input role</b>
        <p>
          {p.images.length
            ? 'Official upstream scan, displayed without its available source annotation. Full sampled-case membership is unverified.'
            : 'Symbolic input socket only; no patient volume was accessed.'}
        </p>
        <code>
          public/{'{case_id}'}/{p.source.input_filename}
        </code>
        <small>No predicted mask or private benchmark label is shown.</small>
      </div>
    </div>
  );
}
function FetaVolume({ slice }: { slice: number }) {
  const t = Math.min(1, Math.max(0, slice));
  const y = 189 - 96 * t;
  return (
    <figure
      className={css.fetaVolume}
      data-sega-symbolic-volume
      data-sega-sampling-plane={t.toFixed(2)}
    >
      <div className={css.head}>
        <b>Authored voxel-volume schematic</b>
        <span>native dimensions unknown</span>
      </div>
      <svg
        viewBox="0 0 440 270"
        role="img"
        aria-label="Abstract i j k voxel-volume wireframe with a sampling plane moving along the k axis; no MRI or tissue is shown"
      >
        <g className={css.fetaWire} fill="none" strokeWidth="2">
          <path d="M80 77H320V221H80Z M126 34H366V178H126Z M80 77L126 34 M320 77L366 34 M320 221L366 178 M80 221L126 178" />
          <path d="M160 77V221 M240 77V221 M80 125H320 M80 173H320" className={css.fetaGrid} />
        </g>
        <polygon
          points={`80,${y} 320,${y} 366,${y - 43} 126,${y - 43}`}
          className={css.fetaPlane}
        />
        <path
          d="M80 238H160 M80 238L116 204 M67 221V141 M67 141L62 150 M67 141L72 150"
          className={css.fetaAxes}
        />
        <text x="169" y="243" className={css.fetaAxisLabel}>
          i
        </text>
        <text x="120" y="202" className={css.fetaAxisLabel}>
          j
        </text>
        <text x="59" y="137" className={css.fetaAxisLabel}>
          k
        </text>
      </svg>
      <figcaption>
        Sampling plane position {Math.round(t * 100)}% along schematic k · no native index, shape,
        image, or label available
        <br />
        <span className={css.fetaLegend}>
          <i />
          Cyan plane = sampling position, not tissue or annotation
        </span>
      </figcaption>
    </figure>
  );
}
function Stack({ p, s }: { p: SegAPack; s: AutoMedSegAState }) {
  const i = p.images.length ? segAIndex(s, p) : 0;
  if (p.key === 'feta')
    return (
      <div className={css.two} data-sega-stack>
        <FetaVolume slice={s.slice} />
        <div className={css.card}>
          <b>One 3D grid, one moving plane</b>
          <p>
            The cyan plane moves along the schematic k axis. Every i, j, k voxel would receive
            exactly one output ID, but the native dimensions, MRI, tissue boundaries, and labels are
            unavailable.
          </p>
          <p>
            This is an authored operation diagram, not a fetal scan, prediction, or reference. A
            single plane cannot replace the required 3D NIfTI.
          </p>
        </div>
      </div>
    );
  return (
    <div className={css.two} data-sega-stack>
      <Slice p={p} index={i} />
      <div className={css.card}>
        <b>One volume, three selected planes</b>
        <p>
          {p.key === 'heart'
            ? 'The cyan locator steps through three preselected native-k source planes.'
            : 'The cyan locator steps through three preselected axial source slices.'}{' '}
          They were chosen using the upstream annotation after the fact, so this view does not test
          finding a target in the full volume. No mask is inferred.
        </p>
        <div className={css.steps}>
          {p.source.slices.map((x, n) => (
            <span className={n === i ? css.active : ''} key={x.native_k}>
              k={x.native_k}
            </span>
          ))}
        </div>
        <p>
          Keep the output on the same spatial grid as the input. A slice screenshot alone cannot
          stand in for the required 3D NIfTI.
        </p>
        {p.key === 'heart' && (
          <small>
            RAS comes from the stored affine; patient-plane orientation was not independently
            verified.
          </small>
        )}
      </div>
    </div>
  );
}

function badge(p: SegAPack, id: string) {
  return p.images.length
    ? id === '1'
      ? css.cyan
      : id === '2' && p.key === 'aeropath'
        ? css.amber
        : ''
    : '';
}
function Labels({ p }: { p: SegAPack }) {
  return (
    <div className={css.two} data-sega-labels>
      <div className={css.card}>
        <b>Integer label codebook</b>
        <div className={css.labels}>
          {Object.entries(p.output.label_values).map(([id, name]) => (
            <div key={id}>
              <strong className={badge(p, id)}>{id}</strong>
              <span>{name}</span>
            </div>
          ))}
        </div>
      </div>
      <div className={css.card}>
        <b>Distinct target</b>
        <p>{ROLE[p.key]}</p>
        <p>
          {p.key === 'feta'
            ? 'These are literal required output IDs, not labels measured in this schematic. No source annotation or private reference was acquired.'
            : 'These are output IDs. Upstream source labels are kept for later reader reveal; the Full solver receives an image, not this selected label map.'}
        </p>
      </div>
    </div>
  );
}
function Schema({ p }: { p: SegAPack }) {
  return (
    <div className={css.two} data-sega-schema>
      <div className={css.card}>
        <b>Required output</b>
        <code>agents_outputs/{'{case_id}'}/dseg.nii.gz</code>
        <p>
          One 3D integer label map with values {Object.keys(p.output.label_values).join(', ')} on
          the input spatial shape. Preserve the affine for physical interpretation.
        </p>
        <strong className={css.empty}>Prediction absent · no dseg file generated</strong>
      </div>
      <div className={css.card}>
        <b>What shape check means</b>
        <p>
          The task requires 3D integer labels. The formatter rounds unique voxel values before
          checking allowed IDs and compares shape only when an input scan is present; it does not
          separately enforce integer voxels, three dimensions, or affine equality. No model output
          exists here.
        </p>
        {p.source.shape_ijk && (
          <code>{p.source.shape_ijk.join(' × ')} voxels in selected source example</code>
        )}
      </div>
    </div>
  );
}
function Reference({ p, s }: { p: SegAPack; s: AutoMedSegAState }) {
  const reveal = segARevealed(s, p);
  if (!p.images.length)
    return (
      <div className={css.covered} data-sega-reference-state="unavailable">
        <b>FeTA label unavailable</b>
        <p>
          Access to official MRI and labels was not obtained; no source or private mask can be
          revealed.
        </p>
      </div>
    );
  if (!reveal)
    return (
      <div className={css.covered} data-sega-reference-state="covered">
        <b>Upstream source annotation covered</b>
        <p>
          Use the reader reference reveal to mount the source training masks. They are not a Full
          private label or a prediction.
        </p>
      </div>
    );
  const i = segAIndex(s, p);
  return (
    <div className={css.two} data-sega-reference-state="revealed">
      <Slice p={p} index={i} reference />
      <div className={css.card}>
        <b>Source label on native k={p.source.slices[i].native_k}</b>
        <p className={css.legend}>
          Solid translucent fill: cyan = class 1{p.key === 'aeropath' ? ', amber = class 2' : ''}.
          These colors match the PNG overlay.
        </p>
        <div className={css.labels}>
          {Object.entries(p.reference.slice_label_voxels[i] ?? {}).map(([id, n]) => (
            <div key={id}>
              <strong className={badge(p, id)}>{id}</strong>
              <span>
                {p.output.label_values[id]} · {n.toLocaleString()} labeled voxels in this slice
              </span>
            </div>
          ))}
        </div>
        <p>
          {p.reference.fusion ||
            'The colored area is an official upstream training label, not a saved model output.'}{' '}
          These slices were selected after inspecting that annotation; they do not represent blind
          localization.
        </p>
        <small>{p.reference.warning}</small>
      </div>
    </div>
  );
}
function Limits({ p }: { p: SegAPack }) {
  return (
    <div className={css.limits} data-sega-limits>
      <div>
        <b>Source evidence</b>
        <p>
          {p.images.length
            ? 'Hash-pinned upstream NIfTI image and matching label, projected into three deterministic teaching slices.'
            : 'Pinned Full harness and restricted official source record only.'}
        </p>
      </div>
      <div>
        <b>Full boundary</b>
        <p>
          No verified staged Full case, private evaluator mask, generated `dseg.nii.gz` or model
          result.
        </p>
      </div>
      <div>
        <b>Scoring contract</b>
        <p>
          Foreground Dice per class, then macro mean across classes and cases. The pinned scorer
          treats both-empty masks as Dice 1.0.{' '}
          {p.key === 'aeropath'
            ? 'AeroPath config prose instead says empty-GT classes are skipped; that discrepancy remains unresolved.'
            : ''}
        </p>
      </div>
    </div>
  );
}
export function AutoMedSegAScene({ state }: { state: AutoMedSegAState }) {
  const p = segAPacks[state.recipe];
  return (
    <section
      className={css.scene}
      data-sega-scene={state.scene}
      data-sega-task={p.key}
      data-sega-basis={p.images.length ? 'mixed' : 'symbolic'}
    >
      <h3>
        {p.key === 'feta'
          ? (
              {
                input: 'Input image unavailable',
                stack: 'Sample an abstract voxel grid',
                labels: 'Read the required output IDs',
                schema: 'Produce a NIfTI label map',
                reference: 'No reference available',
                limits: 'Keep the source boundary clear',
              } as const
            )[state.scene]
          : TITLES[state.scene]}
      </h3>
      {state.scene === 'input' && <Input p={p} />}
      {state.scene === 'stack' && <Stack p={p} s={state} />}
      {state.scene === 'labels' && <Labels p={p} />}
      {state.scene === 'schema' && <Schema p={p} />}
      {state.scene === 'reference' && <Reference p={p} s={state} />}
      {state.scene === 'limits' && <Limits p={p} />}
    </section>
  );
}
export function AutoMedSegAOutput({ state }: { state: AutoMedSegAState }) {
  const p = segAPacks[state.recipe];
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-sega-output>
      <b>{state.scene === 'input' ? 'Input' : 'Output schema'}</b>
      <p>
        {state.scene === 'input'
          ? p.images.length
            ? 'Unmarked upstream source slice; Full sampled-case membership unverified.'
            : 'No official FeTA scan available; symbolic contract only.'
          : p.key === 'feta'
            ? 'Required 3D integer dseg.nii.gz on the input grid; native dimensions unavailable. No prediction or Dice result.'
            : 'One combined dseg.nii.gz with integer IDs and native spatial shape. No prediction or Dice result.'}
      </p>
      {state.scene !== 'input' && (
        <>
          <b>Reference</b>
          <p>
            {segARevealed(state, p)
              ? 'Upstream source training label shown to reader only.'
              : p.key === 'feta'
                ? 'No source label or Full private reference was acquired.'
                : 'Full private reference unavailable; source label covered or absent.'}
          </p>
        </>
      )}
    </aside>
  );
}

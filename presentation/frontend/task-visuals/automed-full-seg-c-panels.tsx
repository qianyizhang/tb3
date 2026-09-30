import {
  segCPacks,
  segCIndex,
  segCHelperRevealed,
  type AutoMedSegCState,
  type SegCPack,
} from './automed-full-seg-c';
import shared from './task-visual.module.css';
import css from './automed-full-seg-c.module.css';

const TITLES = {
  input: 'Inspect the input contract',
  channels: 'Keep the source geometry',
  mapping: 'Map the task-specific labels',
  output: 'Write the required mask files',
  helper: 'Separate training help from private truth',
  limits: 'Read the evidence boundary',
} as const;
function Missing({ p }: { p: SegCPack }) {
  return (
    <div className={css.missing} data-segc-source="unavailable">
      <b>No native PANTHER MRI acquired</b>
      <span>
        The outlined input socket is a contract symbol. It contains no patient pixels or measured
        contour.
      </span>
    </div>
  );
}
function ImagePanel({
  p,
  index,
  channel,
  helper = false,
}: {
  p: SegCPack;
  index: number;
  channel: 't2' | 'adc';
  helper?: boolean;
}) {
  const sl = p.source.slices[index],
    src = channel === 't2' ? p.t2[index] : p.adc[index];
  return (
    <figure className={css.slice} data-segc-source="upstream-training">
      <div className={css.head}>
        <b>{channel === 't2' ? 'T2 anatomy · channel 0' : 'ADC diffusion contrast · channel 1'}</b>
        <span>native k={sl.native_k}</span>
      </div>
      <div className={css.canvas}>
        <img
          src={src}
          alt={`Official MSD prostate_00 ${channel.toUpperCase()} native slice k ${sl.native_k}`}
        />
        {helper && (
          <img
            className={css.overlay}
            src={p.labels[index]}
            alt=""
            data-segc-training-helper="visible"
          />
        )}
      </div>
      <figcaption>
        {p.source.geometry?.shape_ijk_channels?.join('×')} source dimensions ·{' '}
        {p.source.geometry?.voxel_spacing_mm.map((x) => x.toFixed(2)).join('×')} mm ·{' '}
        {p.source.geometry?.axis_codes} · native k plane
      </figcaption>
    </figure>
  );
}
function CTPanel({ p, index }: { p: SegCPack; index: number }) {
  const sl = p.source.slices[index];
  return (
    <figure className={css.slice} data-segc-source="upstream-input">
      <div className={css.head}>
        <b>Official PanTSMini CT · input only</b>
        <span>native k={sl.native_k}</span>
      </div>
      <div className={css.canvas}>
        <img
          src={p.ct[index]}
          alt={`PanTS_00000684 CT input slice at native k ${sl.native_k}; no label overlay`}
        />
      </div>
      <figcaption>
        {p.source.geometry?.shape_ijk?.join('×')} source dimensions · 1.5 mm stored spacing ·{' '}
        {p.source.geometry?.axis_codes} · window of stored values −160 to 240; HU unverified
      </figcaption>
    </figure>
  );
}
function Input({ p, s }: { p: SegCPack; s: AutoMedSegCState }) {
  const real = p.key === 'prostate';
  return (
    <div className={css.two} data-segc-input>
      {real ? (
        <ImagePanel p={p} index={segCIndex(s, p)} channel="t2" />
      ) : p.key === 'pancreas' ? (
        <CTPanel p={p} index={segCIndex(s, p)} />
      ) : (
        <Missing p={p} />
      )}
      <div className={css.card}>
        <b>
          {real
            ? 'Two-channel 4D source volume'
            : p.key === 'pancreas'
              ? 'Upstream CT input volume'
              : 'Required single-volume input'}
        </b>
        <p>
          {real
            ? 'This official MSD training image has a T2 channel and an ADC channel on the same native grid. Its training annotation is hidden here. Full case membership is unverified.'
            : p.key === 'pancreas'
              ? 'This official PanTSMini CT is an upstream input-only example. Its Full selection is unverified; no matching label, private target or prediction is shown.'
              : `The Full ${p.key} task expects ${p.operation.modality} as ${p.source.input_filename}. The harness contains no image and no task-matched native sample was recovered.`}
        </p>
        <code>
          public/{'{case_id}'}/{p.source.input_filename}
        </code>
        <small>
          Initial view shows the input role only; no output or private target is displayed.
        </small>
      </div>
    </div>
  );
}
function Channels({ p, s }: { p: SegCPack; s: AutoMedSegCState }) {
  if (p.key === 'prostate') {
    const i = segCIndex(s, p);
    return (
      <div data-segc-channels>
        <div className={css.pair}>
          <ImagePanel p={p} index={i} channel="t2" />
          <ImagePanel p={p} index={i} channel="adc" />
        </div>
        <div className={css.steps}>
          {p.source.slices.map((x, n) => (
            <span key={x.native_k} className={n === i ? css.active : ''}>
              k={x.native_k}
            </span>
          ))}
        </div>
        <p className={css.note}>
          T2 and ADC are channels of one 4D NIfTI at the same oblique native i,j,k. These sampled
          planes are display-oriented but not regridded. The required output is one 3D label map.
        </p>
      </div>
    );
  }
  if (p.key === 'pancreas') {
    const i = segCIndex(s, p);
    return (
      <div data-segc-channels>
        <CTPanel p={p} index={i} />
        <div className={css.steps}>
          {p.source.slices.map((x, n) => (
            <span key={x.native_k} className={n === i ? css.active : ''}>
              k={x.native_k}
            </span>
          ))}
        </div>
        <p className={css.note}>
          These are fixed input-only native k planes on the stored 266×158×152 CT grid. Display uses
          a stored-intensity window; HU calibration and original acquisition geometry are
          unverified. No source label or output mask is present.
        </p>
      </div>
    );
  }
  return (
    <div className={css.two} data-segc-channels>
      <Missing p={p} />
      <div className={css.card}>
        <b>One spatial grid, two independent targets</b>
        <p>{p.operation.spatial_operation}</p>
        <div className={css.flow}>
          <span>Input 3D volume</span>
          <b>→</b>
          <span>organ 0/1</span>
          <b>+</b>
          <span>lesion 0/1</span>
        </div>
        <small>No sample spacing, affine or anatomy is asserted for this unavailable source.</small>
      </div>
    </div>
  );
}
function Mapping({ p }: { p: SegCPack }) {
  if (p.key === 'prostate')
    return (
      <div className={css.two} data-segc-mapping>
        <div className={css.card}>
          <b>One voxel, one zone code</b>
          <div className={css.labels}>
            {Object.entries(p.operation.labels || {}).map(([v, n]) => (
              <div key={v}>
                <strong className={v === '1' ? css.cyan : v === '2' ? css.amber : ''}>{v}</strong>
                <span>{n}</span>
              </div>
            ))}
          </div>
          <p>
            Read T2 and ADC at the same 3D location. Assign a mutually exclusive peripheral-zone,
            transition-zone or background ID.
          </p>
        </div>
        <div className={css.card}>
          <b>Source-label helper</b>
          <p>
            Official MSD training labels use these IDs. They are available as training help and
            appear only in the later helper scene; they are not a saved Full prediction or its
            private reference.
          </p>
        </div>
      </div>
    );
  const panther = p.key !== 'pancreas';
  return (
    <div className={css.two} data-segc-mapping>
      <div className={css.card}>
        <b>{panther ? 'PANTHER native source codes' : 'PanTS taxonomy remains unresolved'}</b>
        <p>{p.operation.source_mapping}</p>
        {panther && (
          <div className={css.labels}>
            <div>
              <strong>0</strong>
              <span>background → organ 0, lesion 0</span>
            </div>
            <div>
              <strong>1</strong>
              <span>tumor → organ 1, lesion 1</span>
            </div>
            <div>
              <strong>2</strong>
              <span>parenchyma → organ 1, lesion 0</span>
            </div>
          </div>
        )}
      </div>
      <div className={css.card}>
        <b>Full output is two binary maps</b>
        <p>
          Organ and lesion occupy separate files. Organ foreground cannot be submitted as a stand-in
          for tumor foreground.
        </p>
        <div className={css.flow}>
          <span>source taxonomy</span>
          <b>→</b>
          <span>whole organ</span>
          <b>+</b>
          <span>tumor only</span>
        </div>
        <small>Diagram is a label transform, not a segmentation result.</small>
      </div>
    </div>
  );
}
function Output({ p }: { p: SegCPack }) {
  return (
    <div className={css.two} data-segc-schema>
      <div className={css.card}>
        <b>Exact saved output</b>
        {p.output.files.map((f) => (
          <code key={f}>{f}</code>
        ))}
        <p>
          {p.key === 'prostate'
            ? 'One 3D integer map: 0 background, 1 peripheral zone, 2 transition zone.'
            : 'Two independent 3D binary maps with 0 background and 1 foreground in each file.'}{' '}
          Match input spatial dimensions and preserve its affine for physical alignment.
        </p>
        <strong className={css.empty}>No predicted NIfTI file exists in this pack.</strong>
      </div>
      <div className={css.card}>
        <b>Scoring contract, not a result</b>
        <p>{p.output.score_contract}</p>
        <p>
          {p.key === 'prostate'
            ? 'The task requires integer IDs; the formatter rounds values before checking them. Shape is checked when input exists, without an affine comparison. Partial submissions scale Dice by completion; medal uses unscaled macro Dice.'
            : 'The formatter checks allowed values and shape when the input exists; it does not compare affines. Missing masks are tracked as incomplete. No Dice value was observed.'}
        </p>
      </div>
    </div>
  );
}
function Helper({ p, s }: { p: SegCPack; s: AutoMedSegCState }) {
  if (p.key !== 'prostate')
    return (
      <div className={css.covered} data-segc-helper-state="unavailable">
        <b>No source label was acquired</b>
        <p>Full private targets are also unavailable. Nothing can be revealed for this task.</p>
      </div>
    );
  if (!segCHelperRevealed(s, p))
    return (
      <div className={css.covered} data-segc-helper-state="covered">
        <b>MSD training label helper covered</b>
        <p>
          An explicit helper reveal can show the official upstream training zones. This is public
          training material, not Full private ground truth.
        </p>
      </div>
    );
  const i = segCIndex(s, p),
    sl = p.source.slices[i],
    counts = p.helper.slice_label_voxels[i];
  return (
    <div className={css.two} data-segc-helper-state="revealed">
      <ImagePanel p={p} index={i} channel="t2" helper />
      <div className={css.card}>
        <b>Upstream training label at k={sl.native_k}</b>
        <p className={css.legend}>
          Solid translucent fill: cyan = peripheral zone, amber = transition zone. Colors match the
          overlay PNG.
        </p>
        <div className={css.labels}>
          <div>
            <strong className={css.cyan}>1</strong>
            <span>peripheral zone · {counts.peripheral_zone.toLocaleString()} source voxels</span>
          </div>
          <div>
            <strong className={css.amber}>2</strong>
            <span>transition zone · {counts.transition_zone.toLocaleString()} source voxels</span>
          </div>
        </div>
        <p>
          These source slices were selected after inspecting the training label; this does not test
          blind localization. Counts describe this slice, not model performance.
        </p>
        <small>{p.helper.warning}</small>
      </div>
    </div>
  );
}
function Limits({ p }: { p: SegCPack }) {
  return (
    <div className={css.limits} data-segc-limits>
      <div>
        <b>What was recovered</b>
        <p>
          {p.key === 'prostate'
            ? 'Hash-pinned official MSD training MRI and matching zone label, sampled into three native-grid teaching slices.'
            : p.key === 'pancreas'
              ? 'Hash-pinned official PanTSMini CT input sampled at three fixed native k planes; no matching source label.'
              : 'Pinned Full harness and official acquisition metadata only; no task-matched native image or label.'}
        </p>
      </div>
      <div>
        <b>What remains unavailable</b>
        <p>
          Verified Full staged-case membership, private evaluator targets, generated masks, model
          run and observed score.
        </p>
      </div>
      <div>
        <b>Interpretation limit</b>
        <p>
          {p.key === 'prostate'
            ? 'This is zonal prostate segmentation, not cancer localization.'
            : p.key === 'pancreas'
              ? 'The CT is input only. Without a matching label, this view cannot identify the target contours or verify the source-to-Full label transform.'
              : 'Two required binary outputs have distinct organ and tumor meanings. The symbolic transformation does not locate anatomy.'}
        </p>
      </div>
    </div>
  );
}
export function AutoMedSegCScene({ state }: { state: AutoMedSegCState }) {
  const p = segCPacks[state.recipe];
  return (
    <section
      className={css.scene}
      data-segc-scene={state.scene}
      data-segc-task={p.key}
      data-segc-basis={p.key === 'prostate' || p.key === 'pancreas' ? 'mixed' : 'symbolic'}
    >
      <h3>{TITLES[state.scene]}</h3>
      {state.scene === 'input' && <Input p={p} s={state} />}
      {state.scene === 'channels' && <Channels p={p} s={state} />}
      {state.scene === 'mapping' && <Mapping p={p} />}
      {state.scene === 'output' && <Output p={p} />}
      {state.scene === 'helper' && <Helper p={p} s={state} />}
      {state.scene === 'limits' && <Limits p={p} />}
    </section>
  );
}
export function AutoMedSegCOutput({ state }: { state: AutoMedSegCState }) {
  const p = segCPacks[state.recipe];
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-segc-output>
      <b>{state.scene === 'input' ? 'Input' : 'Required output'}</b>
      <p>
        {state.scene === 'input'
          ? p.key === 'prostate'
            ? 'Upstream 4D T2+ADC MRI, unmarked at first read.'
            : p.key === 'pancreas'
              ? 'Upstream PanTSMini CT input only; Full selection unverified.'
              : 'No native source pixels available; symbolic input contract.'
          : p.key === 'prostate'
            ? 'One 3D dseg.nii.gz, no prediction retained.'
            : 'Two binary 3D masks, no prediction retained.'}
      </p>
      {state.scene !== 'input' && (
        <>
          <b>Boundary</b>
          <p>
            {segCHelperRevealed(state, p)
              ? 'Upstream MSD training helper visible; Full private reference absent.'
              : 'Full private reference absent; no score observed.'}
          </p>
        </>
      )}
    </aside>
  );
}

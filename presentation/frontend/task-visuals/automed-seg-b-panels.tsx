import type { ReactNode } from 'react';
import shared from './task-visual.module.css';
import styles from './automed-seg-b.module.css';
import {
  segBData,
  segBKidneyReference,
  segBLiverReference,
  segBIndex,
  type AutomedSegBKey,
  type AutomedSegBState,
} from './automed-seg-b';

const REOPENING: Record<AutomedSegBKey, string> = {
  hepaticvessel:
    'Match an actual Full staged CT to its private vessel/tumor reference before making a result claim.',
  kidney:
    'Resolve the flagged staging-path mismatch and verify any KiTS19-to-Full case and mask mapping.',
  liver:
    'Resolve declared LiTS versus MSD source identity and the flagged staging path before pairing any masks.',
  'pancreas-oar':
    'Acquire permitted local PanTS cases and verify the nonconsecutive label map without redistributing derivatives.',
};

function SourceView({
  task,
  state,
  overlay = false,
}: {
  task: AutomedSegBKey;
  state: AutomedSegBState;
  overlay?: boolean;
}) {
  const doc = segBData[task].source;
  if (!doc.views.length || !doc.native_geometry) {
    return (
      <figure className={styles.scanFigure} data-automed-b-symbolic-input>
        <svg
          className={styles.symbolic}
          viewBox="0 0 360 280"
          role="img"
          aria-label="Symbolic NIfTI voxel grid; no PanTS patient pixels"
        >
          <rect x="15" y="12" width="330" height="244" rx="14" fill="#20384b" />
          {Array.from({ length: 8 }, (_, i) => (
            <path key={i} d={`M${48 + 37 * i} 40v180M48 ${40 + 26 * i}h259`} stroke="#52768a" />
          ))}
          <text x="180" y="140" textAnchor="middle" fill="#fff" fontSize="17">
            CT voxel grid
          </text>
          <text x="180" y="166" textAnchor="middle" fill="#cfdee5" fontSize="12">
            shape and affine unknown here
          </text>
        </svg>
        <figcaption>Symbolic grid only · no PanTS case or anatomy shown</figcaption>
      </figure>
    );
  }
  const index = segBIndex(state.view, doc.views.length);
  const image = doc.views[index];
  const reference =
    overlay && state.scene === 'reference' && state.reference > 0.5
      ? task === 'kidney'
        ? segBKidneyReference.views[index]
        : task === 'liver'
          ? segBLiverReference.views[index]
          : null
      : null;
  const shape = doc.native_geometry.shape_ijk;
  const axis = doc.native_geometry.slice_axis_ijk;
  const axisName = 'ijk'[axis];
  return (
    <figure
      className={styles.scanFigure}
      data-automed-b-native-input
      data-native-axis={axisName}
      data-native-index={image.native_index}
    >
      <div className={styles.scanFrame}>
        <svg
          viewBox="0 0 512 512"
          role="img"
          aria-label={`${segBData[task].short} sampled native axial CT plane ${axisName}=${image.native_index}${reference ? ' with public source annotation revealed' : ''}`}
        >
          <image href={image.ct_png} width="512" height="512" />
          {reference && (
            <image
              data-automed-b-reference-overlay
              href={reference.overlay_png}
              width="512"
              height="512"
            />
          )}
          <rect x="1" y="1" width="510" height="510" fill="none" stroke="#91abb9" strokeWidth="2" />
        </svg>
      </div>
      <figcaption>
        {segBData[task].short} · native {axisName}={image.native_index} of {shape[axis] - 1} · WL 40
        / WW 400 HU
        <br />
        i×j×k = {shape.join(' × ')} voxels · spacing ={' '}
        {doc.native_geometry.voxel_spacing_mm.map((v) => Number(v.toFixed(3))).join(' × ')} mm along
        i×j×k
      </figcaption>
    </figure>
  );
}

function OutputGrid({ task }: { task: AutomedSegBKey }) {
  const files = segBData[task].output.paths;
  return (
    <div className={styles.fileGrid} data-automed-b-empty-output>
      <div className={styles.fileCard}>
        <b>Input</b>
        <span>ct.nii.gz</span>
        <small>native grid</small>
      </div>
      <div className={styles.arrow}>→</div>
      {files.map((path) => (
        <div className={styles.fileCard} key={path}>
          <b>Empty target</b>
          <span>{path.split('/').at(-1)}</span>
          <small>same shape + physical frame</small>
        </div>
      ))}
    </div>
  );
}

function LabelKey({ task, selected }: { task: AutomedSegBKey; selected: number }) {
  const out = segBData[task].output;
  if (out.mask_layout === 'separate-binary')
    return (
      <div className={styles.labelArea} data-automed-b-label-map>
        <div className={styles.labelList}>
          {out.paths.map((path, i) => (
            <div key={path} data-current={i === selected}>
              <b>0/1</b>
              <span>{path.split('/').at(-1)} · background/foreground</span>
            </div>
          ))}
        </div>
        <p className={styles.smallNote}>
          Submit exact 0/1 in both masks. The formatter checks 0/1; the separate Dice routine
          thresholds at &gt;0.5.{' '}
          {task === 'kidney'
            ? 'The public KiTS19 label IDs are a different representation and appear only after reader reveal.'
            : 'A matching public MSD source annotation is available for reader reveal; its label-to-file conversion is not a Full mapping result.'}
        </p>
      </div>
    );
  const labels = Object.entries(out.labels)
    .filter(([id]) => id !== '0')
    .sort((a, b) => Number(a[0]) - Number(b[0]));
  return (
    <div className={styles.labelArea}>
      <div className={styles.labelList} data-automed-b-label-map>
        {labels.map(([id, label], i) => (
          <div key={id} data-current={i === selected}>
            <b>{id}</b>
            <span>{label.replaceAll('_', ' ')}</span>
          </div>
        ))}
      </div>
      <p className={styles.smallNote}>
        Foreground IDs are literal integer voxel values. Background is 0. A label key defines the
        requested output; it is not an observed segmentation.
      </p>
    </div>
  );
}

export function AutomedSegBScene({
  task,
  state: s,
}: {
  task: AutomedSegBKey;
  state: AutomedSegBState;
}) {
  const { source: src, output: out, title: taskTitle } = segBData[task];
  const labels = Object.keys(out.labels)
    .filter((id) => id !== '0')
    .sort((a, b) => Number(a) - Number(b));
  const selected = segBIndex(
    s.class,
    out.mask_layout === 'separate-binary' ? out.paths.length : labels.length,
  );
  const hasSourceReference = task === 'kidney' || task === 'liver';
  const revealed = hasSourceReference && s.scene === 'reference' && s.reference > 0.5;
  let heading = '';
  let body: ReactNode;
  switch (s.scene) {
    case 'inputs':
      heading = `Start with ${taskTitle.toLowerCase()} input`;
      body = (
        <div className={styles.columns}>
          <SourceView task={task} state={s} />
          <article>
            <p className={styles.kicker}>INPUT · BEFORE OUTPUT OR REFERENCE</p>
            <h4>{src.views.length ? 'Public upstream CT' : 'Document-pinned CT contract'}</h4>
            <p>
              {task === 'kidney'
                ? 'Three fixed curated native planes; their selection method is undocumented. Full membership is unverified.'
                : task === 'liver'
                  ? 'Three fixed native planes plus one post-hoc public-label-guided plane. This teaching sample is not unbiased Full evidence.'
                  : src.views.length
                    ? 'Three fixed native planes from an official upstream volume. This example has not been matched to a Full staged case.'
                    : 'The Full harness names per-case ct.nii.gz, but no PanTS CT pixels are retained. The grid is abstract.'}
            </p>
            <p>
              {src.views.length
                ? 'Move the view control across selected planes. The actual task consumes a volume, not these teaching images.'
                : 'No native plane is present, so the view control does not reveal patient pixels; the actual task expects a 3D CT.'}
            </p>
            <p className={styles.smallNote}>
              No participant prediction, private ground truth or patient Dice is present.
            </p>
          </article>
        </div>
      );
      break;
    case 'mapping':
      heading = 'Map the target IDs before writing a mask';
      body = (
        <div className={styles.columns}>
          <SourceView task={task} state={s} />
          <article>
            <p className={styles.kicker}>REQUIRED LABEL SEMANTICS · SOURCE CONTRACT</p>
            <LabelKey task={task} selected={selected} />
            {task === 'kidney' || task === 'liver' ? (
              <p>
                These tasks ask for separate binary organ and lesion files. The pinned Full config
                does not define an organ–lesion overlap rule.{' '}
                {task === 'kidney'
                  ? 'The public KiTS19 conversion is shown only after reader reveal.'
                  : 'The public MSD source-label conversion is shown only after reader reveal; its Full mapping remains unverified.'}
              </p>
            ) : (
              <p>
                These IDs belong in one integer dseg map.{' '}
                {task === 'pancreas-oar'
                  ? 'The 21 foreground IDs have gaps: a compact 1–21 recoding would violate the contract.'
                  : '1 is vessel; 2 is hepatic tumor.'}
              </p>
            )}
          </article>
        </div>
      );
      break;
    case 'output':
      heading = 'Keep the required output visibly empty';
      body = (
        <div className={styles.outputBody}>
          <p className={styles.kicker}>SCHEMA · NO SAVED PARTICIPANT MASK</p>
          <OutputGrid task={task} />
          <p>
            Write each required file under <code>agents_outputs/&#123;case_id&#125;/</code>. Voxel
            arrays must use the input shape; physical interpretation also requires its affine and
            orientation.
          </p>
          <p className={styles.smallNote}>
            A file-format or array-overlap check does not establish anatomical alignment in
            millimeters.
          </p>
        </div>
      );
      break;
    case 'reference':
      heading = hasSourceReference
        ? 'Reveal a released source label to the reader'
        : 'Keep the missing Full reference explicit';
      body = hasSourceReference ? (
        <div className={styles.columns}>
          <SourceView task={task} state={s} overlay />
          <article>
            <p className={styles.kicker}>
              {task === 'kidney' ? 'KITS19' : 'MSD TASK03 LIVER'} PUBLIC SOURCE LABEL · NOT FULL
              PRIVATE GT
            </p>
            {revealed ? (
              <div data-automed-b-reference-revealed>
                <p>
                  {task === 'kidney'
                    ? 'Released KiTS19 case_00000 annotation is visible for teaching. Cyan denotes source kidney/organ; gold denotes source lesion.'
                    : 'Official MSD Task03 liver_53 training annotation is visible for teaching. Cyan denotes source liver/organ; gold denotes source tumor.'}
                </p>
                <div className={styles.legend}>
                  <span>
                    <i className={styles.cyan} />
                    Source {task === 'kidney' ? 'organ' : 'liver/organ'}
                  </span>
                  <span>
                    <i className={styles.gold} />
                    Source {task === 'kidney' ? 'lesion' : 'tumor'}
                  </span>
                </div>
                <p>
                  {task === 'kidney'
                    ? 'For an oracle format example only, organ = source labels 1 or 2 and lesion = label 2. These are not a participant output or Full score.'
                    : 'For an oracle format example only, liver organ = MSD source labels 1 or 2 and lesion/tumor = source label 2. This public-source conversion is not a Full overlap rule, participant output, private GT or score.'}
                </p>
              </div>
            ) : (
              <p className={styles.smallNote} data-automed-b-reference-closed>
                Move the explicit reader reveal control to show the public source annotation. No
                reference layer is in the input view.
              </p>
            )}
          </article>
        </div>
      ) : (
        <div className={styles.columns}>
          <SourceView task={task} state={s} />
          <article>
            <p className={styles.kicker}>NO REFERENCE ASSET IN THIS PACK</p>
            <p>
              {task === 'pancreas-oar'
                ? 'No PanTS image or label was retained. The symbolic grid cannot demonstrate anatomy or segmentation quality.'
                : 'The official upstream CT was recovered without a matched source label. Full private ground truth is absent.'}
            </p>
            <p className={styles.smallNote}>
              The class names and file requirements remain source-backed contract text, not observed
              mask pixels.
            </p>
          </article>
        </div>
      );
      break;
    case 'scorer':
      heading = 'Read what the pinned scorer actually checks';
      body = (
        <div className={styles.scoreCards}>
          <article>
            <b>Submission path</b>
            <p>{out.paths.map((x) => `agents_outputs/${x}`).join(' and ')}</p>
          </article>
          <article>
            <b>Label overlap</b>
            <p>{out.scoring_note}</p>
          </article>
          <article>
            <b>Physical frame</b>
            <p>
              The pinned Dice implementation checks array shape but does not compare NIfTI affines.
              Same shape is insufficient for physical alignment.
            </p>
          </article>
          <article>
            <b>Unavailable result</b>
            <p>
              No Full prediction, private mask, evaluation call or patient score is retained here.
            </p>
          </article>
        </div>
      );
      break;
    case 'limits':
      heading = 'Preserve the source and result boundary';
      body = (
        <div className={styles.scoreCards}>
          <article>
            <b>Actual source</b>
            <p>
              {src.views.length
                ? `${segBData[task].short} public upstream CT, sampled in native space.${task === 'liver' ? ' Matching training label is reader-reveal only.' : ''}`
                : 'Pinned Full task contract only; symbolic input grid.'}
            </p>
          </article>
          <article>
            <b>Full release</b>
            <p>
              The exact Full package excludes dataset pixels. Membership of this upstream example in
              the staged split is unverified.
            </p>
          </article>
          <article>
            <b>Open gate</b>
            <p>{REOPENING[task]}</p>
          </article>
          <article>
            <b>Acquisition</b>
            <p>
              <a href={src.notice.url}>{src.notice.url}</a>
            </p>
          </article>
        </div>
      );
      break;
  }
  return (
    <section className={styles.scene} data-automed-b-scene={s.scene} data-automed-b-task={task}>
      <h3>{heading}</h3>
      {body}
    </section>
  );
}

export function AutomedSegBOutput({
  task,
  state: s,
}: {
  task: AutomedSegBKey;
  state: AutomedSegBState;
}) {
  const src = segBData[task].source;
  const caption =
    s.scene === 'inputs'
      ? src.views.length
        ? 'Input only. Selected public planes are teaching samples; Full staged-case membership is unverified.'
        : 'Input contract only. No PanTS patient CT is retained.'
      : s.scene === 'output'
        ? 'Required output slots remain empty because no participant mask is retained.'
        : s.scene === 'reference'
          ? s.reference > 0.5 && task === 'kidney'
            ? 'Public KiTS19 source annotation revealed to the reader; Full private GT remains unavailable.'
            : s.reference > 0.5 && task === 'liver'
              ? 'Public MSD Task03 liver annotation revealed to the reader; Full private GT remains unavailable.'
              : 'No reference pixels are visible.'
          : s.scene === 'scorer'
            ? 'The pinned scorer compares array labels and shape; this pack has no evaluated result.'
            : 'Contract explanation only; no model or clinical performance claim.';
  return (
    <aside className={`${shared.storyOutput} ${styles.aside}`} data-automed-b-output={s.scene}>
      <b>{segBData[task].title}</b>
      <p>{caption}</p>
      <small>
        {src.views.length ? 'Upstream teaching sample' : 'Pinned task terms'}: {src.license} · Full
        source/case rights are separate
      </small>
    </aside>
  );
}

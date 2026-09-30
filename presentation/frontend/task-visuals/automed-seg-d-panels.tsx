import { useState, type ReactNode } from 'react';
import shared from './task-visual.module.css';
import styles from './automed-seg-d.module.css';
import {
  segDData,
  spleenTrainingLabel,
  segDIndex,
  type AutomedSegDKey,
  type AutomedSegDState,
} from './automed-seg-d';

function Native({
  task,
  state,
  overlay = false,
}: {
  task: AutomedSegDKey;
  state: AutomedSegDState;
  overlay?: boolean;
}) {
  const src = segDData[task].source;
  const i = segDIndex(state.view, src.views.length);
  const v = src.views[i];
  const showLabel = task === 'spleen' && overlay && state.reference > 0.5;
  const label = showLabel ? spleenTrainingLabel.views[i] : null;
  const imageWidth = v.width;
  const imageHeight = v.height;
  return (
    <figure className={styles.scanFigure} data-automed-d-native-input data-native-index={v.index}>
      <div className={styles.scanFrame}>
        <svg
          viewBox={`0 0 ${imageWidth} ${imageHeight}`}
          role="img"
          aria-label={`${task === 'spleen' ? 'MSD Spleen axial' : 'TotalSegmentator coronal'} public source CT plane ${v.index}${showLabel ? ', public training label revealed' : ''}`}
        >
          <image href={v.png} width={imageWidth} height={imageHeight} />
          {label && (
            <image
              data-automed-d-training-label
              href={label.overlay_png}
              width={imageWidth}
              height={imageHeight}
            />
          )}
        </svg>
      </div>
      <figcaption>
        {src.source_case} · {task === 'spleen' ? 'axial k' : 'coronal y'}={v.index} · display WL 40
        / WW 400
        <br />
        {src.native_geometry.shape.join(' × ')} voxels ·{' '}
        {src.native_geometry.spacing_mm.map((x) => Number(x.toFixed(3))).join(' × ')} mm
      </figcaption>
    </figure>
  );
}

function LabelOperation({ task, selected }: { task: AutomedSegDKey; selected: number }) {
  const labels = Object.entries(segDData[task].output.labels).filter(([id]) => id !== '0');
  const [manual, setManual] = useState<number | null>(null);
  const active = manual ?? selected;
  const [id, name] = labels[active];
  return (
    <div className={styles.labelArea}>
      <div className={styles.fileGrid} data-automed-d-label-operation>
        <div className={styles.fileCard}>
          <b>Class name</b>
          <span data-automed-d-class-name>{name.replaceAll('_', ' ')}</span>
          <small>pinned Full config</small>
        </div>
        <div className={styles.arrow}>→</div>
        <div className={styles.fileCard}>
          <b>Integer voxel</b>
          <span data-automed-d-class-id>{id}</span>
          <small>in dseg.nii.gz</small>
        </div>
      </div>
      {task === 'tsg-multiorgan' && (
        <>
          <p className={styles.smallNote}>
            Browse all 117 exact Full class names. Source s1366 has no Full-case identity proof, and
            no source label pixels enter this operation.
          </p>
          <label className={styles.labelPicker}>
            Inspect a class
            <select
              data-automed-d-117-key
              aria-label="Full class mapping"
              value={active}
              onChange={(event) => setManual(Number(event.currentTarget.value))}
            >
              {labels.map(([value, label], i) => (
                <option key={value} value={i}>
                  {value} · {label}
                </option>
              ))}
            </select>
          </label>
          {manual !== null && (
            <button type="button" onClick={() => setManual(null)}>
              Follow playback
            </button>
          )}
        </>
      )}
      {task === 'spleen' && (
        <p className={styles.smallNote}>
          Only 0 background and 1 spleen are valid. The source training label remains hidden until
          the separate reader reveal.
        </p>
      )}
    </div>
  );
}

export function AutomedSegDScene({
  task,
  state: s,
}: {
  task: AutomedSegDKey;
  state: AutomedSegDState;
}) {
  const { source: src, output: out } = segDData[task];
  const selected = segDIndex(s.label, Object.keys(out.labels).length - 1);
  const revealed = task === 'spleen' && s.scene === 'reference' && s.reference > 0.5;
  let title = '';
  let body: ReactNode;
  switch (s.scene) {
    case 'inputs':
      title = 'Read the public CT before labels';
      body = (
        <div className={styles.columns}>
          <Native task={task} state={s} />
          <article>
            <p className={styles.kicker}>ACTUAL UPSTREAM CT · INPUT ONLY</p>
            <h4>
              {task === 'spleen'
                ? 'MSD Task09 training case'
                : 'TotalSegmentator source case s1366'}
            </h4>
            <p>
              Move across three retained native planes.{' '}
              {task === 'spleen'
                ? 'These planes were selected after inspecting the public training label.'
                : 'The center plane was previously selected using Lite kidney-reference information.'}{' '}
              These are teaching samples, not solver-provided locations. The Full input contract is
              a full <code>ct.nii.gz</code> volume.
            </p>
            <p className={styles.smallNote}>
              The exact Full archive contains no images, and this source example is not proven to be
              in its staged split.
            </p>
          </article>
        </div>
      );
      break;
    case 'mapping':
      title =
        task === 'spleen'
          ? 'One foreground ID defines the target'
          : 'Map all 117 names to exact integer IDs';
      body = (
        <div className={styles.columns}>
          <Native task={task} state={s} />
          <article>
            <p className={styles.kicker}>SOURCE CONFIG · NOT OBSERVED PREDICTION</p>
            <LabelOperation task={task} selected={selected} />
          </article>
        </div>
      );
      break;
    case 'output':
      title = 'The required result remains empty';
      body = (
        <div className={styles.outputBody} data-automed-d-empty-output>
          <p className={styles.kicker}>COMBINED NIFTI SCHEMA · NO PARTICIPANT MASK</p>
          <div className={styles.fileGrid}>
            <div className={styles.fileCard}>
              <b>Input</b>
              <span>ct.nii.gz</span>
              <small>native CT grid</small>
            </div>
            <div className={styles.arrow}>→</div>
            <div className={styles.fileCard}>
              <b>Empty target</b>
              <span>dseg.nii.gz</span>
              <small>{task === 'spleen' ? '0 or 1' : '0 or 1–117'}</small>
            </div>
          </div>
          <p>
            Submit <code>{out.path}</code> on each Full case's own input grid. Preserve its physical
            frame for meaningful alignment; the pinned checker compares shape when input exists,
            without an affine comparison. No saved output array is present.
          </p>
        </div>
      );
      break;
    case 'reference':
      title =
        task === 'spleen'
          ? 'Reveal the public training label to the reader'
          : 'Keep the Full reference unavailable';
      body = (
        <div className={styles.columns}>
          <Native task={task} state={s} overlay />
          <article>
            <p className={styles.kicker}>
              {task === 'spleen'
                ? 'PUBLIC MSD TRAINING HELPER · NOT FULL PRIVATE GT'
                : 'NO REFERENCE PIXELS IN THIS PACK'}
            </p>
            {revealed ? (
              <div data-automed-d-training-label-revealed>
                <p>
                  <i className={styles.pink} /> Pink is the released MSD spleen training annotation
                  on the same native grid. It illustrates what label 1 means.
                </p>
                <p>It is neither a participant prediction nor the hidden Full evaluation mask.</p>
              </div>
            ) : task === 'spleen' ? (
              <p data-automed-d-training-label-closed>
                Move the explicit reader reveal control to show the public training label. Input
                views contain CT alone.
              </p>
            ) : (
              <p>
                The previous Lite audit retained five source label masks, but this Full draft does
                not relabel them as its private reference. The Full source-ID mapping is not
                verified.
              </p>
            )}
          </article>
        </div>
      );
      break;
    case 'scorer':
      title = 'Separate label overlap from physical alignment';
      body = (
        <div className={styles.scoreCards}>
          <article>
            <b>Shape and labels</b>
            <p>
              {out.scorer_boundary} The format checker rounds values before its allowed-ID test; the
              required output is still an integer label map.
            </p>
          </article>
          <article>
            <b>Native frame</b>
            <p>
              The saved NIfTI affine matters for anatomical interpretation, even though the pinned
              Dice scorer checks array shape rather than affine equality.
            </p>
          </article>
          <article>
            <b>Reference</b>
            <p>
              The Full private separated class masks are unavailable. No Full case Dice is
              calculated.
            </p>
          </article>
          <article>
            <b>Coverage</b>
            <p>
              {task === 'tsg-multiorgan'
                ? 'The Full config names 117 classes; the source CT alone proves no prediction coverage. Its config and scorer disagree on empty-class averaging.'
                : 'The one-class target is spleen only; the public training mask is a teaching helper.'}
            </p>
          </article>
        </div>
      );
      break;
    case 'limits':
      title = 'State the source and result boundary';
      body = (
        <div className={styles.scoreCards}>
          <article>
            <b>Verified source</b>
            <p>
              {task === 'spleen'
                ? 'Matched public MSD Task09 CT and training label, 512 × 512 × 51 native voxels.'
                : 'Hash-verified TotalSegmentator source CT s1366; exact Full 117-class configuration.'}
            </p>
          </article>
          <article>
            <b>Full release</b>
            <p>
              Exact Full task harness with dataset.included=false. Staged case identity and private
              reference are not verified.
            </p>
          </article>
          <article>
            <b>Unavailable result</b>
            <p>No participant output, model trace, evaluator call or clinical score.</p>
          </article>
          <article>
            <b>Official route</b>
            <p>
              <a href={src.notice.url}>{src.notice.url}</a>
            </p>
          </article>
        </div>
      );
      break;
  }
  return (
    <section className={styles.scene} data-automed-d-task={task} data-automed-d-scene={s.scene}>
      <h3>{title}</h3>
      {body}
    </section>
  );
}

export function AutomedSegDOutput({
  task,
  state: s,
}: {
  task: AutomedSegDKey;
  state: AutomedSegDState;
}) {
  const caption =
    s.scene === 'inputs'
      ? 'Actual upstream CT only; Full staged-case identity is unverified.'
      : s.scene === 'output'
        ? 'The required dseg NIfTI slot is empty. No participant output is retained.'
        : s.scene === 'reference'
          ? task === 'spleen' && s.reference > 0.5
            ? 'Public training label revealed to reader; no Full private GT.'
            : 'No reference pixels visible.'
          : s.scene === 'scorer'
            ? 'Pinned array scorer contract, with no evaluated patient result.'
            : 'Source-backed contract illustration; no clinical performance claim.';
  return (
    <aside className={`${shared.storyOutput} ${styles.aside}`} data-automed-d-output={s.scene}>
      <b>{segDData[task].title}</b>
      <p>{caption}</p>
      <small>{segDData[task].license} · local source interpretation</small>
    </aside>
  );
}

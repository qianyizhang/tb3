import {
  cellsegFocusImage,
  cellsegForegroundMap,
  cellsegHelper,
  cellsegImage,
  cellsegInstanceMap,
  cellsegMetric,
  cellsegOutput,
  cellsegSelectedInstance,
  cellsegSource,
  type RexCellsegState,
} from './rexmle-cellseg';
import shared from './task-visual.module.css';
import css from './rexmle-cellseg.module.css';

function ImagePanel({
  overlay,
  caption,
  helper = false,
}: {
  overlay?: string;
  caption: string;
  helper?: boolean;
}) {
  return (
    <figure className={css.imagePanel} data-cellseg-real-training-input>
      <div className={css.imageHead}>
        <b>cell_00944.png</b>
        <span>source training · 512 × 512 px</span>
      </div>
      <div className={css.imageStack}>
        <img
          src={cellsegImage}
          width="512"
          height="512"
          alt="Original CellSeg fluorescence microscopy training patch, without a model prediction"
        />
        {overlay && (
          <img
            className={css.overlay}
            src={overlay}
            width="512"
            height="512"
            alt={
              helper ? 'Source training-label overlay; positive integer IDs distinguish cells' : ''
            }
            data-cellseg-training-label-helper={helper ? 'visible' : undefined}
          />
        )}
      </div>
      <figcaption>{caption}</figcaption>
    </figure>
  );
}

function Split() {
  const s = cellsegSource.split;
  return (
    <div className={css.split} data-cellseg-split>
      <div>
        <b>{s.source_training_pairs}</b>
        <span>original Training-labeled pairs</span>
      </div>
      <span>+</span>
      <div>
        <b>{s.source_tuning_pairs}</b>
        <span>original Tuning pairs</span>
      </div>
      <span>seed 42 →</span>
      <div>
        <b>{s.reconstructed_public_train}</b>
        <span>expected public train · this patch</span>
      </div>
      <div>
        <b>{s.reconstructed_private_test}</b>
        <span>expected private-label test</span>
      </div>
      <small>
        Seed 42 split reconstructed from pinned source IDs; ReX preparer was not executed.
      </small>
    </div>
  );
}

function Input() {
  return (
    <div className={css.inputScene}>
      <ImagePanel caption="Actual official training image; no source label shown yet." />
      <div className={css.side}>
        <b>What the solver receives</b>
        <p>
          Public training images and matching instance labels support method development. A held-out
          test image would require a separate per-case mask submission; no held-out image is
          retained in this teaching pack.
        </p>
        <div className={css.emptySlot}>
          Held-out case input
          <br />
          <strong>not retained</strong>
        </div>
        <Split />
      </div>
    </div>
  );
}

function Helper({ reveal }: { reveal: boolean }) {
  return (
    <div className={css.inputScene}>
      <ImagePanel
        overlay={reveal ? cellsegInstanceMap : undefined}
        caption={
          reveal
            ? 'Official source training TIFF rendered as colored instance boundaries; no predicted cells.'
            : 'Original image alone; reveal the supplied training label.'
        }
        helper={reveal}
      />
      <div className={css.side}>
        <b>Supplied training annotation</b>
        <p>
          The TIFF shares the 512 × 512 pixel grid. Value 0 is background; IDs 1–36 mark separate
          cell instances. The IDs are arbitrary identities, not cell types.
        </p>
        <div className={css.counts}>
          <div>
            <b>36</b>
            <span>distinct labeled cells</span>
          </div>
          <div>
            <b>8,479</b>
            <span>foreground pixels / 262,144</span>
          </div>
        </div>
        <div className={css.legend}>
          Source-label colors{' '}
          {cellsegHelper.focus_ids.slice(0, 3).map((id) => (
            <span key={id}>
              <i
                style={{
                  borderTopColor: `rgb(${cellsegHelper.instances[id - 1].color_rgb.join(',')})`,
                }}
              />{' '}
              ID {id}
            </span>
          ))}{' '}
          <span>· dark image = original input</span>
        </div>
        <p className={css.boundary}>
          This is allowed training help. No held-out test label or evaluator reference is present.
        </p>
      </div>
    </div>
  );
}

function Instances({ state }: { state: RexCellsegState }) {
  const selected = cellsegSelectedInstance(state.instance);
  const rgb = `rgb(${selected.color_rgb.join(',')})`;
  return (
    <div className={css.instances} data-cellseg-instance-operation>
      <div className={css.imagePair}>
        <div>
          <ImagePanel
            overlay={cellsegForegroundMap}
            caption="Binary foreground: all 36 IDs collapse to one value."
            helper
          />
          <span className={css.pairLabel}>All positive pixels → 1</span>
        </div>
        <div>
          <ImagePanel
            overlay={cellsegInstanceMap}
            caption="Instance mask: each positive ID remains separate."
            helper
          />
          <span className={css.pairLabel}>Positive IDs 1–36 stay distinct</span>
        </div>
      </div>
      <div className={css.focus}>
        <div className={css.focusImage}>
          <img
            src={cellsegFocusImage(selected)}
            alt={`Source-label-guided crop around training instance ${selected.id}`}
            data-cellseg-selected-helper
          />
        </div>
        <div>
          <b>Inspect one source instance</b>
          <strong style={{ color: rgb }}>ID {selected.id}</strong>
          <span>
            {selected.pixels} pixels · inclusive box {selected.bbox_xyxy_inclusive.join(', ')}
          </span>
          <p>
            This post-hoc crop uses the training label to choose its location. The channel samples
            four real IDs from the 36-cell TIFF; it is not a model search result.
          </p>
        </div>
      </div>
    </div>
  );
}

function Submission() {
  return (
    <div className={css.submission} data-cellseg-empty-test-output>
      <div className={css.emptyCase}>
        <b>Held-out microscopy image</b>
        <span>No exact ReX prepared test image retained</span>
        <div className={css.emptySlot}>image pixels unavailable</div>
      </div>
      <div className={css.arrow}>→</div>
      <div className={css.schema}>
        <b>Required saved artifact</b>
        <code>submission/submission.csv</code>
        <div className={css.csv}>
          <strong>image_id</strong>
          <strong>predicted_mask_path</strong>
          <span>&lt;held-out image_id&gt;</span>
          <span>predictions/&lt;image_id&gt;_label.tiff</span>
        </div>
        <div className={css.emptySlot}>
          2D integer instance-mask TIFF
          <br />
          <strong>empty · no prediction retained</strong>
        </div>
        <p>
          0 = background. Each predicted cell needs its own positive integer ID on the image pixel
          grid.
        </p>
      </div>
    </div>
  );
}

function Scoring({ state }: { state: RexCellsegState }) {
  return (
    <div className={css.scoring} data-cellseg-symbolic-metric>
      <div className={css.pipeline}>
        <div>
          <b>Private held-out label</b>
          <span>not present</span>
        </div>
        <span>×</span>
        <div>
          <b>Submitted instance mask</b>
          <span>not present</span>
        </div>
        <span>→</span>
        <div>
          <b>Pairwise IoU</b>
          <span>intersection / union</span>
        </div>
        <span>→</span>
        <div>
          <b>One-to-one match</b>
          <span>Hungarian assignment</span>
        </div>
        <span>→</span>
        <div>
          <b>TP · FP · FN</b>
          <span>then instance F1</span>
        </div>
      </div>
      <div className={css.thresholds}>
        <b>Source grader threshold sweep</b>
        <div>
          {cellsegMetric.thresholds_iou.map((t, i) => (
            <span className={state.metric >= i / 4 ? css.active : ''} key={t}>
              IoU ≥ {t.toFixed(1)}
            </span>
          ))}
        </div>
        <p>
          Match status depends on the threshold. No IoU matrix or F1 is measured for this source
          training example.
        </p>
      </div>
      <div className={css.metricNotes}>
        <span>
          <b>Boundary rule</b> Cells touching the outer 2-pixel margin are removed before instance
          matching.
        </span>
        <span>
          <b>Large images</b> At least 25 million pixels triggers 2000 × 2000 ROI tiling. This 512²
          patch would take the direct branch.
        </span>
        <span>
          <b>Shape mismatch</b> Grader resizes a prediction nearest-neighbor to reference array
          shape; that tolerance is not proof of a sound mask.
        </span>
      </div>
    </div>
  );
}

function Limits() {
  return (
    <div className={css.limits}>
      <div>
        <b>Actual</b>
        <p>
          Hash-verified official RGB image and 16-bit training instance TIFF. IDs 1–36 and 8,479
          foreground pixels are source counts.
        </p>
      </div>
      <div>
        <b>Reconstructed</b>
        <p>
          1,000 Training-labeled plus 101 Tuning pairs; seeded 880/221 split. This patch is expected
          in public train. Pinned preparer was not run.
        </p>
      </div>
      <div>
        <b>Absent</b>
        <p>
          No retained prepared held-out image, private test label, predicted mask, model run, grader
          run or F1.
        </p>
      </div>
      <div>
        <b>Scope difference</b>
        <p>
          The pinned ReX preparer narrows the original challenge: it uses those labeled pairs for
          its split; downloaded original Testing and unlabeled material are not copied into the
          prepared public/test directories.
        </p>
      </div>
    </div>
  );
}

const titles: Record<RexCellsegState['scene'], string> = {
  input: 'One real public-training patch',
  helper: 'Supplied training instance label',
  instances: 'Binary foreground versus 36 cell identities',
  submission: 'Held-out output schema, still empty',
  scoring: 'How the pinned grader would match instances',
  limits: 'What was recovered and what remains absent',
};

export function RexCellsegScene({ state }: { state: RexCellsegState }) {
  return (
    <section className={css.scene} data-cellseg-scene={state.scene}>
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' && <Input />}
      {state.scene === 'helper' && <Helper reveal={state.helper > 0.5} />}
      {state.scene === 'instances' && <Instances state={state} />}
      {state.scene === 'submission' && <Submission />}
      {state.scene === 'scoring' && <Scoring state={state} />}
      {state.scene === 'limits' && <Limits />}
    </section>
  );
}

export function RexCellsegOutput({ state }: { state: RexCellsegState }) {
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-cellseg-output>
      <b>Case role</b>
      <p>
        Official source training image. Matching label is supplied learning help, not a held-out
        reference.
      </p>
      {state.scene !== 'input' && (
        <>
          <b>Required test output</b>
          <p>
            {cellsegOutput.status === 'not-retained'
              ? 'Integer instance-mask TIFF and image_id,predicted_mask_path CSV; no prediction retained.'
              : 'Unexpected status'}
          </p>
        </>
      )}
      <b>Evidence status</b>
      <p>
        No ReX preparer, model, grader or F1 run. The 880/221 split is a reconstruction from pinned
        code.
      </p>
      <small>CellSeg 10719375 · CC-BY-NC-ND-4.0 · local noncommercial teaching</small>
    </aside>
  );
}

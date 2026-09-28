import {
  rexInputs as src,
  rexReference as ref,
  rexContract as data,
  rexSelection,
  rexReveal,
  type RexState,
  type RexFixture,
} from './rex-topcow';
import css from './rex-topcow.module.css';
const fixtureNames = [
  'Exact labels',
  'One broken vessel',
  'Names swapped',
  'Extra absent class',
  'All background',
];
const observations = [
  'Both synthetic vessels match. Dice rounds to 1; no patient prediction is involved.',
  'One missing voxel splits label 11. Mean B0 error rises to 0.5, but the anterior topology verdict still passes.',
  'IDs 11 and 12 swap. Class Dice is zero; merging all foreground for clDice hides the wrong names.',
  'Three extra voxels carry ID 15. Reference-present Dice omits that absent class; the anterior verdict rejects it.',
  'Both reference vessels are missed. Dice and clDice are zero; mean B0 error is one.',
];
function Native({ index = 1, reveal = false }: { index?: number; reveal?: boolean }) {
  const v = src.views[index];
  return (
    <figure className={css.native}>
      <svg
        viewBox="0 0 266 371"
        role="img"
        aria-label={`Native axial CTA z=${v.z}; right rightward, anterior upward${reveal ? ', held-out source label revealed' : ''}`}
      >
        <image href={v.png} width="266" height="371" />
        {reveal && (
          <>
            <image data-rex-reference="full" href={ref.views[index].png} width="266" height="371" />
            <rect
              x="78"
              y="113"
              width="102"
              height="65"
              fill="none"
              stroke="white"
              strokeDasharray="4 3"
              strokeWidth="1"
            />
          </>
        )}
        <g fill="white" fontSize="11">
          <text x="4" y="191">
            L
          </text>
          <text x="251" y="191">
            R
          </text>
          <text x="129" y="13">
            A
          </text>
        </g>
      </svg>
      <figcaption>
        <b>Native axial z={v.z}</b>
        <span>266 × 371 pixels · −100 to 700 HU</span>
      </figcaption>
    </figure>
  );
}
function Key({ selected }: { selected?: number }) {
  return (
    <div className={css.key} data-rex-key>
      {ref.structures.map((r, i) => (
        <div key={r.id} data-current={selected === i}>
          <i style={{ background: r.color }} />
          <span>
            {r.id} · {r.name}
          </span>
        </div>
      ))}
    </div>
  );
}
function Toy({ fixture, predicted }: { fixture: RexFixture; predicted: boolean }) {
  const points = predicted
    ? fixture.prediction_voxels
    : fixture.reference_voxels.map((ijk) => ({ ijk, label: ijk[1] === 3 ? 11 : 12 }));
  return (
    <figure className={css.toy}>
      <svg
        viewBox="0 0 198 140"
        role="img"
        aria-label={`${predicted ? 'Prediction' : 'Reference'} in a nonclinical 9 by 9 by 9 toy; x-y projection`}
      >
        <rect x="0" y="0" width="198" height="140" fill="#142b23" />
        {points.map((p, j) => (
          <rect
            key={j}
            x={16 + p.ijk[0] * 18}
            y={9 + p.ijk[1] * 16}
            width="16"
            height="14"
            fill={ref.structures.find((r) => r.id === p.label)?.color}
          />
        ))}
      </svg>
      <figcaption>{predicted ? 'Toy prediction' : 'Toy reference'} · x–y projection</figcaption>
    </figure>
  );
}
export function RexScene({ state: s }: { state: RexState }) {
  const i = rexSelection(s),
    reveal = rexReveal(s);
  let title = '',
    body;
  switch (s.scene) {
    case 'inputs':
      title = 'Train a model, then label unseen CTA volumes';
      body = (
        <div className={css.columns}>
          <Native index={i} />
          <article>
            <p className={css.kicker}>TOPCOW · CTA TRACK 1 / TASK 1</p>
            <h4>266 × 371 × 311 voxels</h4>
            <p>Case 012 · about 0.498 × 0.498 × 0.5 mm</p>
            <p>
              The agent develops and trains a segmentation pipeline, then predicts integer vessel
              IDs.
            </p>
            <p className={css.callout}>
              These three planes were selected post hoc using reference labels. They are a reader’s
              tour, not a supplied target or an agent search trace.
            </p>
            <p>Full source volume enters the task. No prediction is shown.</p>
          </article>
        </div>
      );
      break;
    case 'split':
      title = 'An upstream training case can become a ReX test case';
      body = (
        <>
          <div className={css.flow}>
            <b>125 matched CTAs</b>
            <span>sorted names → seed 42</span>
            <b>100 train / 25 test</b>
          </div>
          <div className={css.columns}>
            <article>
              <p className={css.kicker}>PUBLIC TO SOLVER</p>
              <h4>100 CTAs + labels</h4>
              <p>25 test CTAs, task description, grader and leaderboard.</p>
              <p>Train and infer from the supplied data.</p>
            </article>
            <article>
              <p className={css.kicker}>PRIVATE REFERENCE</p>
              <h4>25 test label maps</h4>
              <p>Case 012 belongs here in the reproduced split.</p>
              <p>No ROI or vessel-edge annotations are copied into the prepared task.</p>
            </article>
          </div>
          <p className={css.callout}>
            Actual pinned preparer replayed on filename-only placeholders from the complete ZIP
            directory. This assumes all 125 matched release pairs; no prepared medical run was
            executed.
          </p>
        </>
      );
      break;
    case 'labels':
      title = 'Each integer names one vessel class';
      body = (
        <>
          <Key selected={i} />
          <div className={css.selected}>
            <b>
              {ref.structures[i].id} → {ref.structures[i].name}
            </b>
            <p>Public label vocabulary · 13 foreground IDs, plus 0 for background.</p>
          </div>
          <p>
            R/L are anatomical sides. BA: basilar; PCA: posterior cerebral; ICA: internal carotid;
            MCA: middle cerebral; Pcom: posterior communicating; Acom: anterior communicating; ACA:
            anterior cerebral; 3rd-A2: third A2 segment.
          </p>
          <p className={css.callout}>
            Preserve these identities in a single integer NIfTI. The color key is a teaching
            display, not additional solver assistance.
          </p>
        </>
      );
      break;
    case 'submission':
      title = 'Submit a CSV and one label volume per test case';
      body = (
        <>
          <pre
            className={css.file}
          >{`submission.csv\nimage_id,modality,predicted_mask_path\n012,CTA,predictions/topcow_ct_012_0000.nii.gz`}</pre>
          <div className={css.columns}>
            <article>
              <h4>Requested contract</h4>
              <p>
                Predict in the input image geometry. Keep integer IDs, native shape, spacing, origin
                and direction.
              </p>
              <p>
                Train a model and run inference; the task instructions prohibit hand-labeling test
                data.
              </p>
            </article>
            <article>
              <h4>Inspected validation</h4>
              <p>Checks ID sets and prediction paths. Missing files fail.</p>
              <p>
                The code does not enforce the modality column or unique row counts. Keep the
                declared format anyway.
              </p>
            </article>
          </div>
          <p className={css.small}>
            The row is the source sample convention. No output file or trained model is claimed.
          </p>
        </>
      );
      break;
    case 'reference':
      title = reveal
        ? 'Reveal the held-out source labels and ROI'
        : 'Case 012 starts with the CTA alone';
      body = (
        <div className={css.referenceColumns}>
          <Native index={reveal ? i : 1} reveal={reveal} />
          <article>
            {reveal ? (
              <>
                <figure className={css.crop} data-rex-crop>
                  <svg
                    viewBox="0 0 102 65"
                    role="img"
                    aria-label="Magnified annotation-selected ROI, 102 by 65 native pixels"
                  >
                    <image href={ref.views[i].ct_crop_png} width="102" height="65" />
                    <image
                      data-rex-reference="crop"
                      href={ref.views[i].crop_png}
                      width="102"
                      height="65"
                    />
                  </svg>
                  <figcaption>
                    Magnified reader ROI · 102 × 65 native pixels
                    <br />
                    Dashed white box in full view · same source pixels
                  </figcaption>
                </figure>
                <Key />
                <p className={css.small}>
                  11 classes present in the full label volume. IDs 8 and 15 have no annotated
                  voxels; this is not an independent clinical absence judgment. Some labels extend
                  beyond this crop.
                </p>
              </>
            ) : (
              <>
                <p className={css.kicker}>EXPLICIT READER REFERENCE REVEAL</p>
                <h4>Mask and ROI stay hidden</h4>
                <p>
                  Continue playback to reveal the separately stored source annotation and its
                  magnified crop.
                </p>
                <p className={css.callout}>
                  The release makes these bytes public, but the pinned ReX preparation assigns this
                  case’s label to its private test subset.
                </p>
                <p>No model output is overlaid.</p>
              </>
            )}
          </article>
        </div>
      );
      break;
    case 'metrics': {
      title = 'Overlap, vessel names and continuity can disagree';
      const f = data.fixtures[i];
      body = (
        <>
          <div className={css.toys}>
            <Toy fixture={f} predicted={false} />
            <Toy fixture={f} predicted />
            <div className={css.toyKey}>
              <b>{fixtureNames[i]}</b>
              <span style={{ color: '#ffcd8b' }}>■ 11 · R-ACA</span>
              <span style={{ color: '#c9a4ff' }}>■ 12 · L-ACA</span>
              <span style={{ color: '#f09de4' }}>■ 15 · 3rd-A2</span>
            </div>
          </div>
          <table data-rex-fixtures>
            <thead>
              <tr>
                <th>Nonclinical fixture</th>
                <th>Dice ↑</th>
                <th>clDice ↑</th>
                <th>B0 error ↓</th>
                <th>Anterior*</th>
              </tr>
            </thead>
            <tbody>
              {data.fixtures.map((f, j) => (
                <tr key={f.id} data-current={i === j}>
                  <td>{fixtureNames[j]}</td>
                  <td>{f.dice.toFixed(3)}</td>
                  <td>{f.cldice.toFixed(3)}</td>
                  <td>{f.b0_error.toFixed(1)}</td>
                  <td>{f.anterior_topology ? 'pass' : 'fail'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className={css.selected}>{observations[i]}</p>
          <p className={css.small}>
            9³ constructed arrays. B0 uses 26-connectivity. *Simplified source “topology,” explained
            next. No HD95 execution.
          </p>
        </>
      );
      break;
    }
    case 'topology':
      title = 'The pinned “topology” test checks presence and overlap';
      body = (
        <>
          <div className={css.columns}>
            <article>
              <h4>For every named class</h4>
              <p>Reference present → IoU must be at least 0.25.</p>
              <p>Reference absent → prediction must also omit it.</p>
              <p>All class checks must pass for the case’s regional verdict.</p>
            </article>
            <article>
              <h4>Two regions</h4>
              <p>Anterior: IDs 10, 11, 12, 15.</p>
              <p>Posterior: IDs 2, 3, 8, 9.</p>
              <p>No vessel adjacency graph is evaluated by this simplified function.</p>
            </article>
          </div>
          <div className={css.selected}>
            <b>{i === 0 ? 'Broken vessel still passes' : 'Four fields, two verdict rates'}</b>
            <p>
              {i === 0
                ? 'The removed voxel leaves enough overlap to pass every anterior class check, even though label 11 is disconnected.'
                : 'Anterior/posterior graph accuracy use all-correct targets and duplicate the corresponding anterior/posterior match rates.'}
            </p>
          </div>
          <p className={css.small}>
            Group-2 F1 separately scores IDs 8, 9, 10 and 15. An all-true-negative class contributes
            0, so the exact two-vessel toy has group-2 F1 = 0.
          </p>
        </>
      );
      break;
    case 'geometry':
      title = 'A permissive cast does not establish correct geometry';
      body = (
        <>
          <div className={css.columns}>
            <article>
              <p className={css.kicker}>REQUIRED OUTPUT</p>
              <h4>Keep the input grid</h4>
              <p>
                Origin, spacing, direction, shape and integer vessel identities define the physical
                mask.
              </p>
              <p>Shape mismatches trigger nearest-neighbor resampling in the inspected grader.</p>
            </article>
            <article data-rex-geometry>
              <p className={css.kicker}>SOURCE FRAGMENT REPLAY</p>
              <h4>{i === 0 ? 'Origin +100 mm → 0 mm' : '11.5 / 12.5 → 11 / 12'}</h4>
              <p>
                {i === 0
                  ? 'CopyInformation replaces prediction metadata with reference metadata for the same-shaped toy.'
                  : 'The UInt8 cast truncates fractional toy values before the metric functions.'}
              </p>
              <p>The source fragment was executed in isolation.</p>
            </article>
          </div>
          <p className={css.callout}>
            This is not whole-grader acceptance. Preserve the declared geometry and label types; a
            cast or metadata overwrite cannot validate the original physical alignment.
          </p>
          <p className={css.small}>Native source views in this story are never resampled.</p>
        </>
      );
      break;
    case 'ranking':
      title = 'The primary prose and final ranking are different';
      body = (
        <>
          <div className={css.columns}>
            <article>
              <h4>Description: mean Dice</h4>
              <p>
                Implementation returns nine measures and ranks against the supplied leaderboard.
              </p>
              <p>Higher: Dice, clDice, group-2 F1, two graph accuracies and two topology rates.</p>
              <p>Lower: B0 error and HD95.</p>
            </article>
            <article>
              <h4>Mean of nine positions</h4>
              <p>
                Ties use minimum rank. The final overall value is mean position; lower is better.
              </p>
              <p>Constructed leaderboard tie: positions 2, 1, 1, 3, 1, 3, 4, 1, 3.</p>
              <p className={css.rank}>19 / 9 = {data.ranking.positions.mean_position.toFixed(3)}</p>
            </article>
          </div>
          <p className={css.callout}>
            Eight selected metrics were reproduced on synthetic labels. HD95 was inspected in source
            only: prediction-to-reference edges, reference spacing and a 90 mm empty-mask fallback.
            The full grader was not executed.
          </p>
          <p className={css.small}>
            If ranking is unavailable, code falls back to negative Dice. The tie example reuses an
            existing leaderboard row; it is not a new result.
          </p>
        </>
      );
      break;
    case 'limits':
      title = 'One source-backed task explanation, no capability result';
      body = (
        <div className={css.cards}>
          <article>
            <b>Native source verified</b>
            <p>
              CTA, mask and ROI match the complete release directory’s sizes and CRCs, with retained
              SHA-256 hashes.
            </p>
          </article>
          <article>
            <b>Split and boundary resolved</b>
            <p>
              100/25 partition from the pinned preparer on filenames; case 012 reference remains
              reader-only.
            </p>
          </article>
          <article>
            <b>Bounded scorer reproduction</b>
            <p>
              Five nonclinical label fixtures, one geometry fragment and a ranking tie. Eight of
              nine metrics executed.
            </p>
          </article>
          <article>
            <b>Still outside this review</b>
            <p>
              HD95 execution, full grader/runtime isolation, training, test predictions and the
              other 19 ReX challenge tasks.
            </p>
          </article>
        </div>
      );
      break;
  }
  return (
    <section className={css.scene} data-rex-scene={s.scene}>
      <h3>{title}</h3>
      {body}
    </section>
  );
}
export function RexOutput({ state: s }: { state: RexState }) {
  const copy = {
    inputs:
      'The task is model development and generalization. Looking at one selected CTA section does not complete it.',
    split:
      'Upstream release membership and the benchmark’s prepared partition are different facts. The current complete-release replay places case 012 in test.',
    labels:
      'Names anchor the integer map. A foreground mask with swapped names can preserve shape but fail class-aware evaluation.',
    submission:
      'The example row explains the file contract. Every held-out case still requires an actual trained-model prediction.',
    reference:
      'The colored mask and annotation-derived crop are reader references. Their public release does not make them supplied test-time assistance.',
    metrics:
      'Class Dice averages reference-present foreground classes. Binary clDice merges all positive IDs. Neither number alone captures every error.',
    topology:
      'This source implementation uses presence and IoU tests. It does not certify anatomical vessel connectivity.',
    geometry:
      'Metadata replacement and casting are observed implementation behavior. They do not relax the task’s native-grid output requirement.',
    ranking:
      'Inspect the actual aggregation. Nine ranked fields include two pairs that duplicate the same regional verdict rates.',
    limits:
      'This review explains the pinned TopCoW CTA task. It supplies no patient score, clinical judgment or model performance claim.',
  };
  return (
    <aside className={css.aside} data-rex-aside>
      <b>Read the contract with its evidence</b>
      <p>{copy[s.scene]}</p>
      <small>
        ReX-MLE · b3d8f7c3
        <br />
        TopCoW 2024 · non-commercial source terms
        <br />
        No model run
      </small>
    </aside>
  );
}

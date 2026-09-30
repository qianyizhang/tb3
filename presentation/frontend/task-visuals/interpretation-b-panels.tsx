import { BrainFullOperationFocus } from './brain-full-operation-focus';
import { CardiacCineOperation } from './cardiac-cine-operation';
import { BrainGradeStageFocus } from './brain-grade-stage-focus';
import {
  interpretationBPacks,
  type InterpretationBPack,
  type InterpretationBState,
} from './interpretation-b';
import shared from './task-visual.module.css';
import css from './interpretation-b.module.css';

const titles = {
  input: 'Start with the supplied case',
  route: 'Map the required operation',
  operation: 'Inspect the task mechanism',
  output: 'Write the required result',
  limits: 'Read the evidence boundary',
} as const;
function EmptyImage({ label }: { label: string }) {
  return (
    <div className={css.emptyImage} data-intb-image-state="unavailable">
      <span>{label}</span>
      <small>Source pixels unavailable · no patient image synthesized</small>
    </div>
  );
}
function Modalities({ p }: { p: InterpretationBPack }) {
  return (
    <div className={css.modalities} data-intb-modalities>
      {p.source.modalities.map((m, i) => (
        <div key={m} className={css.modality}>
          <b>{String(i + 1).padStart(2, '0')}</b>
          <span>{m}</span>
          <small>Input path empty</small>
        </div>
      ))}
    </div>
  );
}
function Input({ p }: { p: InterpretationBPack }) {
  return (
    <div className={css.columns} data-intb-input>
      <div>
        <Modalities p={p} />
        <EmptyImage
          label={p.key === 'cardiac-full' ? 'Cine cardiac MRI' : 'Four-sequence brain MRI'}
        />
      </div>
      <div className={css.card}>
        <b>Case manifest</b>
        <p>
          {p.key === 'cardiac-full'
            ? 'One cine NIfTI or cine H5 source must be bound. Raw H5 requires reconstruction before the segmentation chain.'
            : 'T1, T1c, T2 and FLAIR must all resolve to one matching case; a plausible path with the wrong modality is not a valid mapping.'}
        </p>
        <small>All image sockets are symbolic; there is no case-matched scan in this pack.</small>
      </div>
    </div>
  );
}
function Stages({ p, progress }: { p: InterpretationBPack; progress: number }) {
  const stages = p.operation.stages;
  const active = Math.min(
    stages.length - 1,
    Math.max(0, Math.floor(Math.max(0, Math.min(1, progress)) * stages.length)),
  );
  return (
    <div className={css.stages} data-intb-stage-map>
      {stages.map((s, i) => (
        <div key={s} className={i === active ? css.active : ''} data-intb-stage={s}>
          <span>{String(i + 1).padStart(2, '0')}</span>
          <b>{s.replaceAll('_', ' ')}</b>
          <small>{i === active ? 'Required stage · illustrated' : 'Required stage'}</small>
        </div>
      ))}
    </div>
  );
}
function Route({ p, state }: { p: InterpretationBPack; state: InterpretationBState }) {
  return (
    <div data-intb-route>
      <Stages p={p} progress={state.progress} />
      <div className={css.branch}>
        <b>Conditional branch</b>
        <span>{p.operation.conditional_branch}</span>
      </div>
    </div>
  );
}
function Operation({ p, state }: { p: InterpretationBPack; state: InterpretationBState }) {
  if (p.key === 'cardiac-full')
    return (
      <div data-intb-operation>
        <CardiacCineOperation operation={p.operation} detail={state.detail} />
      </div>
    );
  if (p.key === 'brain-grade')
    return (
      <div data-intb-operation>
        <BrainGradeStageFocus
          operation={{ stages: p.operation.stage_details }}
          progress={state.progress}
        />
      </div>
    );
  return (
    <div data-intb-operation>
      <BrainFullOperationFocus operation={p.operation} progress={state.progress} />
    </div>
  );
}

function Output({ p }: { p: InterpretationBPack }) {
  return (
    <div className={css.columns} data-intb-output-schema>
      <div className={css.card}>
        <b>Required artifact keys</b>
        <div className={css.keyList}>
          {Object.keys(p.output.schema).map((k) => (
            <div key={k}>
              <code>{k}</code>
              <span>unset · no saved output</span>
            </div>
          ))}
        </div>
      </div>
      <div className={css.card}>
        <b>Evaluation boundary</b>
        <p>
          {p.key === 'brain-full'
            ? 'TCR counts five stage successes plus five artifact paths (ten checks). Separate five-tool success and seven invariants check files, mask affines, feature rows and fields. None compares a mask, grade or report with clinical truth.'
            : p.key === 'cardiac-full'
              ? 'TCR counts five stage successes and four artifact paths (nine checks). Separate tool-success and four nonempty invariants do not compare with expert truth. UNCLASSIFIED can pass the nonempty group check.'
              : 'The completion ratio tracks four required stage successes and two artifact paths; the separate success rule names grade-classifier tool success. Nonempty CSV and predicted_grade checks are invariants. None compares the grade with a diagnosis.'}
        </p>
        <strong>No prediction · no score</strong>
      </div>
    </div>
  );
}
function Limits({ p }: { p: InterpretationBPack }) {
  return (
    <div className={css.columns} data-intb-limits>
      <div className={css.card}>
        <b>Verified source</b>
        <p>
          Pinned BCER task registry, evaluator and dataset layout. The displayed tool order and
          required artifact names come from that contract.
        </p>
      </div>
      <div className={css.card}>
        <b>Missing evidence</b>
        <p>
          {p.key === 'brain-grade'
            ? 'Matched four-modality MRI, independent annotation and true HGG/LGG grade are unavailable. The pinned benchmark checks no grade truth. BraTS MGMT labels are a different target.'
            : p.key === 'cardiac-full'
              ? 'No matched cine, expert mask or independent group is available. Source code reads Info.cfg Group and can echo ground_truth_group and ground_truth_match. That does not prove answer isolation or accuracy.'
              : 'Matched four-modality MRI, expert mask and true HGG/LGG grade are absent. A heuristic mask can be nonempty and affine-matched. BraTS MGMT labels do not supply grade truth.'}
        </p>
        <p>
          There is no observed agent action, saved answer, private reference or evaluator result in
          this pack.
        </p>
      </div>
    </div>
  );
}
export function InterpretationBScene({ state }: { state: InterpretationBState }) {
  const p = interpretationBPacks[state.recipe];
  return (
    <section
      className={css.scene}
      data-intb-scene={state.scene}
      data-intb-task={p.key}
      data-intb-basis={p.basis}
    >
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' && <Input p={p} />}
      {state.scene === 'route' && <Route p={p} state={state} />}
      {state.scene === 'operation' && <Operation p={p} state={state} />}
      {state.scene === 'output' && <Output p={p} />}
      {state.scene === 'limits' && <Limits p={p} />}
    </section>
  );
}
export function InterpretationBOutput({ state }: { state: InterpretationBState }) {
  const p = interpretationBPacks[state.recipe];
  return (
    <aside className={`${shared.storyOutput} ${css.aside}`} data-intb-aside>
      <b>{state.scene === 'input' ? 'Input boundary' : 'Artifact registry'}</b>
      <p>
        {state.scene === 'input' ? 'No answer or private reference is present.' : p.output.path}
      </p>
      {state.scene !== 'input' && <small>No observed prediction, action or score.</small>}
    </aside>
  );
}

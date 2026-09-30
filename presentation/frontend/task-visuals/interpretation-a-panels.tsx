import { CxrClauseGate } from './cxr-clause-gate';
import { useState } from 'react';
import {
  interpretationAPacks,
  inspectionTile,
  type InterpretationAState,
  type InterpretationAPack,
} from './interpretation-a';
import shared from './task-visual.module.css';
import css from './interpretation-a.module.css';

const TITLE = {
  input: 'Start with the supplied input',
  inspect: 'Inspect the case without its answer',
  operation: 'Apply the task-specific operation',
  schema: 'Write only the required output',
  reference: 'Keep evaluator material separate',
  limits: 'Read what this source does and does not show',
} as const;
function EmptyInput({ label, detail }: { label: string; detail: string }) {
  return (
    <div className={css.emptyInput} data-inta-input-state="unavailable">
      <b>{label}</b>
      <span>{detail}</span>
    </div>
  );
}
function Slide({ state, grid = false }: { state: InterpretationAState; grid?: boolean }) {
  const [manualIndex, setManualIndex] = useState<number | null>(null);
  const storyTile = inspectionTile(state.cursor);
  const index = grid && manualIndex !== null ? manualIndex : storyTile.index;
  const x = index % 28,
    y = Math.floor(index / 28);
  const nativeX0 = x * 4096,
    nativeY0 = y * 4096;
  const nativeX1 = Math.min(nativeX0 + 4096, 114688);
  const nativeY1 = Math.min(nativeY0 + 4096, 100352);
  const left = 16 + x * 18,
    top = 16 + y * 18;
  const cellHeight = y === 24 ? 9 : 18;
  return (
    <figure className={css.slide} data-inta-input-state={grid ? 'symbolic-grid' : 'unavailable'}>
      <div className={css.slideHead}>
        <b>slide_0001 · original image absent</b>
        <span>verified extent 114,688 × 100,352 native px</span>
      </div>
      {!grid ? (
        <div className={css.emptyInput} data-inta-original-image="absent">
          <b>Whole-slide image absent from this pack</b>
          <span>No patient pixels, tissue, tumor annotation, or answer are shown.</span>
        </div>
      ) : (
        <>
          <svg
            viewBox="0 0 560 480"
            role="img"
            aria-label={`Authored blank 28-column by 25-row task grid; unclassified cursor at x ${x}, y ${y}; final row half-height`}
            data-inta-grid
            style={{ display: 'block', width: '100%', maxHeight: 215, background: '#0b2635' }}
          >
            <rect x="16" y="16" width="504" height="441" fill="#153747" />
            {Array.from({ length: 29 }, (_, i) => (
              <line
                key={`x${i}`}
                x1={16 + i * 18}
                x2={16 + i * 18}
                y1="16"
                y2="457"
                stroke="#557b8d"
                strokeWidth="0.6"
              />
            ))}
            {Array.from({ length: 25 }, (_, i) => (
              <line
                key={`y${i}`}
                x1="16"
                x2="520"
                y1={16 + i * 18}
                y2={16 + i * 18}
                stroke="#557b8d"
                strokeWidth="0.6"
              />
            ))}
            <line x1="16" x2="520" y1="457" y2="457" stroke="#9eb8c4" strokeWidth="1" />
            <rect
              x={left}
              y={top}
              width="18"
              height={cellHeight}
              fill="#ffd16a"
              fillOpacity=".16"
              stroke="#ffd16a"
              strokeWidth="2"
              data-inta-unclassified-cursor
            />
          </svg>
          <div className={css.gridControls}>
            <label>
              Inspection coordinate
              <input
                type="range"
                min="0"
                max="699"
                step="1"
                value={index}
                onChange={(event) => setManualIndex(Number(event.currentTarget.value))}
                aria-label="Unclassified tile coordinate, 0 through 699"
                data-inta-cursor-control
              />
            </label>
            <div>
              <output aria-live="polite">
                Cursor ({x}, {y})
              </output>
              <button type="button" onClick={() => setManualIndex(null)}>
                Follow story cursor
              </button>
            </div>
          </div>
        </>
      )}
      <figcaption>
        {grid
          ? `Authored coordinate schematic only. Cursor (${x}, ${y}) maps native x [${nativeX0}, ${nativeX1}), y [${nativeY0}, ${nativeY1}); it marks no tumor or prediction.`
          : 'The real source image is required by the task but excluded from this collection pack pending access and derivative-use review.'}
      </figcaption>
    </figure>
  );
}

function Input({ p, state }: { p: InterpretationAPack; state: InterpretationAState }) {
  const k = p.key;
  return (
    <div className={css.two} data-inta-input>
      {k === 'healthagentbench-tumor-tiles' ? (
        <Slide state={state} />
      ) : (
        <EmptyInput
          label={
            k === 'healthagentbench-cxr-correction'
              ? 'Current and prior CXR studies unavailable'
              : k === 'radagent'
                ? 'Chest CT unavailable'
                : 'Exact chest CT unavailable'
          }
          detail={
            k === 'healthagentbench-cxr-correction'
              ? 'The source manifest names 12 chronological studies, but no views or draft report were acquired.'
              : k === 'radagent'
                ? 'No matched CT or saved specialist-tool trace is in the pinned source.'
                : 'The valid_16_a_1 CT and its generated labels.txt require CT-RATE access.'
          }
        />
      )}
      <div className={css.card}>
        <b>Solver input</b>
        <p>
          {k === 'healthagentbench-tumor-tiles'
            ? 'One whole slide, a public task row and an editable submission template are required. The collection contains the verified grid contract, with no slide pixels.'
            : k === 'healthagentbench-cxr-correction'
              ? 'A patient’s highest-numbered CXR study is current; earlier studies and their reports are helpers. The target study carries a draft FINDINGS section.'
              : k === 'radagent'
                ? 'A chest CT path is passed to specialist services. The report agent starts from the request and image identity.'
                : 'A non-contrast chest CT and a case-specific labels.txt list. The actual requested names were not acquired.'}
        </p>
        <small>No private reference or model answer is mounted in the initial view.</small>
      </div>
    </div>
  );
}
function Inspect({ p, state }: { p: InterpretationAPack; state: InterpretationAState }) {
  const k = p.key;
  if (k === 'healthagentbench-tumor-tiles')
    return (
      <div className={css.two} data-inta-inspect>
        <Slide state={state} grid />
        <div className={css.card}>
          <b>Explore the unclassified grid</b>
          <p>
            Each task tile is 256×256 at downsample 16, covering 4,096×4,096 level-0 pixels. The
            exact slide has 28 columns × 25 rows = 700 possible coordinates; the final row covers
            only 2,048 level-0 pixels in height.
          </p>
          <p>
            Move the outlined cursor to inspect a coordinate. This authored blank grid contains no
            tissue or tumor labels. Only the native extent comes from the source audit.
          </p>
        </div>
      </div>
    );
  if (k === 'healthagentbench')
    return (
      <div className={css.two} data-inta-inspect>
        <EmptyInput label="3D CT viewer socket" detail="No patient slices or findings are shown." />
        <div className={css.card}>
          <b>Requested-label list is a helper</b>
          <p>
            The bootstrap checks 17 report-phrase categories. Present-only or absent-only matches
            are retained; both or neither are omitted. Only retained names reach the solver. The
            actual count and names are unavailable.
          </p>
          <code>&lt;exact name from labels.txt&gt;: yes | no</code>
        </div>
      </div>
    );
  if (k === 'radagent') return <RadChecklist p={p} />;

  return (
    <div className={css.steps} data-inta-inspect>
      <div>
        <b>Prior studies</b>
        <p>
          The pinned manifest lists 11 prior studies with 20 views and full reports as runtime
          helpers. No patient files were acquired.
        </p>
      </div>
      <div>
        <b>Current target</b>
        <p>
          The highest-numbered folder is the target: one listed view, non-generated report sections
          and a counterfactual draft FINDINGS. Manifest counts do not prove loaded files.
        </p>
      </div>
      <div>
        <b>Evidence check</b>
        <p>Compare only claims already in the draft against current images and history.</p>
      </div>
    </div>
  );
}
function RadChecklist({ p }: { p: InterpretationAPack }) {
  const [index, setIndex] = useState(0);
  const items = p.operation.checklist ?? [];
  const names = [
    'Airways',
    'Lung parenchyma',
    'Pleura',
    'Heart',
    'Cardiovascular and mediastinum',
    'Diaphragm and upper abdomen',
    'Spine, ribs and clavicles',
    'Chest wall, breasts and axillae',
    'Devices',
  ];
  return (
    <div className={css.steps} data-inta-inspect>
      <div>
        <b>01 · Prompt-directed draft</b>
        <p>
          The v8c prompt requests a report_generation_tool draft first. The tool description instead
          suggests drafting after checking regions.
        </p>
        <p>No saved trace establishes an actual order.</p>
      </div>
      <div className={css.card}>
        <b>02 · Explore the nine-item checklist</b>
        <div className={css.ruleRows}>
          <label>
            Checklist area
            <select
              aria-label="RadAgent checklist area"
              value={index}
              onChange={(e) => setIndex(Number(e.target.value))}
            >
              {names.map((n, i) => (
                <option value={i} key={n}>
                  {i + 1} · {n}
                </option>
              ))}
            </select>
          </label>
        </div>
        <p data-inta-checklist-text>{items[index]}</p>
        <small>These are source instructions, not observed patient findings.</small>
      </div>
      <div>
        <b>03 · Check contradictions</b>
        <p>
          Whole-volume and slice VQA, classification, segmentation, slice selection and windowing
          can supply preliminary evidence.
        </p>
        <p>
          The prompt directs further checks when findings conflict. No tool result or final report
          is shown.
        </p>
      </div>
    </div>
  );
}
function FindingRule() {
  const [answers, setAnswers] = useState(['match', 'match', 'missing']);
  const matches = answers.filter((x) => x === 'match').length;
  return (
    <div className={css.two} data-inta-operation>
      <div className={css.card}>
        <b>One answer per requested name</b>
        <p>
          Inspect the CT and write yes or no for each supplied finding. The actual names, answers
          and private gold are unavailable.
        </p>
        <code>&lt;exact requested label&gt;: yes|no</code>
        <p>
          Three hypothetical names below illustrate comparison outcomes only. They are not patient
          findings or predictions.
        </p>
      </div>
      <div className={css.card}>
        <b>Try the all-labels rule</b>
        <div className={css.ruleRows}>
          {answers.map((answer, i) => (
            <label key={i}>
              <span>Hypothetical name {i + 1}</span>
              <select
                aria-label={`Hypothetical name ${i + 1} comparison`}
                value={answer}
                onChange={(e) =>
                  setAnswers((old) => old.map((x, j) => (i === j ? e.target.value : x)))
                }
              >
                <option value="match">Matches hypothetical gold</option>
                <option value="mismatch">Mismatch</option>
                <option value="missing">Missing answer</option>
              </select>
            </label>
          ))}
        </div>
        <p data-inta-rule-result aria-live="polite">
          Illustrative matches: {matches}/3 · rule returns {matches === 3 ? '1' : '0'}
        </p>
        <small>
          Diagnostic agreement {matches}/3 does not replace the all-labels rule. Extra names are
          ignored.
        </small>
        <button type="button" onClick={() => setAnswers(['match', 'match', 'missing'])}>
          Reset illustration
        </button>
      </div>
    </div>
  );
}
function Operation({ p }: { p: InterpretationAPack }) {
  const k = p.key;
  if (k === 'healthagentbench-tumor-tiles')
    return (
      <div className={css.two} data-inta-operation>
        <div className={css.card}>
          <b>Level-zero coordinate transform</b>
          <div className={css.equation}>
            grid x = floor(pixel x / 4096)
            <br />
            grid y = floor(pixel y / 4096)
          </div>
          <p>
            Each cell is a candidate region. The private expert mask defines whether its tumor
            fraction reaches the public threshold of 0.2; that mask was not recovered.
          </p>
        </div>
        <div className={css.card}>
          <b>Selection remains empty</b>
          <p>
            The blank grid explains coordinate mapping. It cannot identify tumor-bearing tissue. The
            cursor is unclassified; no selection or prediction is retained.
          </p>
          <code>predicted_tumor_tiles: [&#123;x, y&#125;, …]</code>
        </div>
      </div>
    );
  if (k === 'healthagentbench') return <FindingRule />;
  if (k === 'radagent')
    return (
      <div className={css.two} data-inta-operation>
        <div className={css.card}>
          <b>Tool action · key fields</b>
          <code>{'{"action":"call_tool","tool_name":"<specialist>","arguments":{…}}'}</code>
          <p>
            Draft, classification, VQA, masks and slice tools supply preliminary evidence. Their
            outputs may disagree and need reconciliation.
          </p>
        </div>
        <div className={css.card}>
          <b>Final action · key fields</b>
          <code>{'{"action":"final_answer","answer":"<report>"}'}</code>
          <p>
            The minimal request omits the paired reference report. Original full host scenarios can
            retain it for optional reward; this does not prove filesystem isolation. No actual
            report is retained.
          </p>
        </div>
      </div>
    );
  return <CxrClauseGate />;
}
function Schema({ p }: { p: InterpretationAPack }) {
  return (
    <div className={css.two} data-inta-schema>
      <div className={css.card}>
        <b>Required output</b>
        <code>{p.output.path}</code>
        {p.key === 'healthagentbench-tumor-tiles' ? (
          <p>
            Write a one-row JSON list retaining task_id and instruction. Set contains_tumor and list
            integer &#123;x,y&#125; pairs. The scorer ignores contains_tumor, deduplicates pairs and
            does not validate grid bounds. No coordinates are selected here.
          </p>
        ) : p.key === 'healthagentbench-cxr-correction' ? (
          <p>
            Use a one-row JSON list with task_id case_01. Set final_answer to a literal FINDINGS:
            header on its own line, then corrected existing claims only. No IMPRESSION. The parser
            is more tolerant than this required format.
          </p>
        ) : p.key === 'healthagentbench' ? (
          <p>
            One exact requested label per line, followed by yes or no. Actual label names are
            unavailable.
          </p>
        ) : (
          <p>
            Return a final_answer action with an answer string and retain the tool interaction
            trace. No report was produced.
          </p>
        )}
        <strong className={css.absent}>Output absent · no prediction or score</strong>
      </div>
      <div className={css.card}>
        <b>What the evaluator sees</b>
        <p>
          {p.key === 'healthagentbench-tumor-tiles'
            ? 'Private label-2 mask fractions define gold tiles at 20% or above. Tile F1 ≥ 0.90 passes; both-empty sets score 0. This is tile-set scoring, not slide-level AUC.'
            : p.key === 'healthagentbench-cxr-correction'
              ? 'Private original FINDINGS are compared by CheXprompt. Defaults: five calls and an absolute threshold of three zero-significant-error votes. Environment overrides exist; failed calls do not shrink the threshold.'
              : p.key === 'healthagentbench'
                ? 'Evaluator-only report-derived gold labels and evidence sentences; all retained names must match.'
                : 'A paired report used by separate text and label metrics; the final trace alone is not proof of report quality.'}
        </p>
      </div>
    </div>
  );
}
function Reference({ p }: { p: InterpretationAPack }) {
  return (
    <div className={css.covered} data-inta-reference-state="unavailable">
      <b>No case-specific evaluator answer in this pack</b>
      <p>
        {p.key === 'healthagentbench-tumor-tiles'
          ? 'The expert tumor mask and hidden gold tile coordinates were not copied.'
          : p.key === 'healthagentbench-cxr-correction'
            ? 'The current gold FINDINGS and judge result were not acquired.'
            : p.key === 'healthagentbench'
              ? 'Paired report, requested names, gold yes/no values and evidence sentences were not acquired.'
              : 'No matching reference CT report or saved generated trace was acquired.'}
      </p>
    </div>
  );
}
function Limits({ p }: { p: InterpretationAPack }) {
  return (
    <div className={css.limits} data-inta-limits>
      <div>
        <b>Source</b>
        <p>
          {p.key === 'healthagentbench-tumor-tiles'
            ? 'Pinned task files, public task row and bounded native WSI headers establish the geometry. No slide pixels are in this pack.'
            : p.key === 'radagent'
              ? 'Exact pinned RadAgent source is verified; no task-matched native image is available.'
              : 'Exact pinned HealthAgentBench source is verified; no task-matched native image is available.'}
        </p>
      </div>
      <div>
        <b>Missing</b>
        <p>
          Private reference, patient answer, model output and observed score.{' '}
          {p.key === 'healthagentbench-tumor-tiles'
            ? 'The local audit recovered only bounded ranges and an overview, not the full slide.'
            : ''}
        </p>
      </div>
      <div>
        <b>Interpretation</b>
        <p>
          {p.key === 'healthagentbench'
            ? 'Report-phrase agreement is not independent diagnosis or localization. Missing or empty gold is a staging error, not measured model failure.'
            : p.key === 'radagent'
              ? 'Offline report metrics are separate from optional full-orchestrator reward. Minimal batch reward 0.0 is placeholder metadata; no quality measurement was run.'
              : p.key === 'healthagentbench-tumor-tiles'
                ? 'The cursor is not a tumor selection or F1 measurement.'
                : 'CheXprompt is installed from unpinned main. Missing gold and judge errors are infrastructure states. No patient correction or clinical result was measured.'}
        </p>
      </div>
    </div>
  );
}
export function InterpretationAScene({ state }: { state: InterpretationAState }) {
  const p = interpretationAPacks[state.recipe];
  return (
    <section
      className={css.scene}
      data-inta-scene={state.scene}
      data-inta-task={p.key}
      data-inta-basis="symbolic"
    >
      <h3>{TITLE[state.scene]}</h3>
      {state.scene === 'input' && <Input p={p} state={state} />}
      {state.scene === 'inspect' && <Inspect p={p} state={state} />}
      {state.scene === 'operation' && <Operation p={p} />}
      {state.scene === 'schema' && <Schema p={p} />}
      {state.scene === 'reference' && <Reference p={p} />}
      {state.scene === 'limits' && <Limits p={p} />}
    </section>
  );
}
export function InterpretationAOutput({ state }: { state: InterpretationAState }) {
  const p = interpretationAPacks[state.recipe];
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-inta-output>
      <b>
        {state.scene === 'input'
          ? 'Input role'
          : p.key === 'healthagentbench-cxr-correction'
            ? 'Required FINDINGS-only output'
            : 'Required output'}
      </b>
      <p>
        {state.scene === 'input'
          ? p.key === 'healthagentbench-tumor-tiles'
            ? 'Original WSI absent; authored blank grid follows.'
            : 'Symbolic input socket; no patient image.'
          : p.output.path}
      </p>
      {state.scene !== 'input' && (
        <>
          <b>Status</b>
          <p>
            {p.key === 'healthagentbench-cxr-correction'
              ? 'No patient report or observed judge result; private gold unavailable.'
              : 'No generated answer or observed score; private reference unavailable.'}
          </p>
        </>
      )}
    </aside>
  );
}

import {
  radagentVqaPack as pack,
  operationFrame,
  operationIndex,
  operationLabels,
  vqaReferenceVisible,
  type RadagentVqaState,
} from './radagent-vqa';
import type { StoryPlan } from '../types';
import shared from './task-visual.module.css';
import css from './radagent-vqa.module.css';
function MissingInput() {
  return (
    <div className={css.inputs}>
      <div className={css.stack}>
        <span />
        <span />
        <span />
        <strong>Native CT absent</strong>
        <small>Abstract stack, not patient geometry or slice count</small>
      </div>
      <div className={css.card}>
        <b>Original VQA row absent</b>
        <p>question + exact options: —</p>
        <p>qid / image_id: —</p>
        <small>No supplied clinical question or finding is invented.</small>
      </div>
    </div>
  );
}
function FieldMap() {
  return (
    <div className={css.fields} data-radagent-vqa-field-map>
      <span>question → task text</span>
      <span>qid → task_id</span>
      <span>image_id → configured CT path</span>
      <span>CSV answer → host gt; no value</span>
    </div>
  );
}
export function RadagentVqaScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: RadagentVqaState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const index = operationIndex(state.progress);
  const visible = vqaReferenceVisible(state);
  return (
    <section className={css.scene} data-radagent-vqa-scene={state.scene}>
      {(state.scene === 'input' || state.scene === 'operation') && (
        <>
          <h3>CT + exact question → optional model evidence → one full option</h3>
          <p className={css.label}>Symbolic workflow; original case and tool evidence absent.</p>
          {state.scene === 'input' && (
            <>
              <MissingInput />
              <FieldMap />
            </>
          )}
          {state.scene === 'operation' && (
            <>
              <div className={css.controls}>
                {operationLabels.map((label, i) => (
                  <button
                    type="button"
                    key={label}
                    aria-pressed={i === index}
                    onClick={() => onSeekFrame?.(operationFrame(plan, i))}
                    disabled={!onSeekFrame}
                  >
                    {label}
                  </button>
                ))}
              </div>
              <div className={css.card} data-radagent-vqa-tool-scope>
                {index === 0 ? (
                  <>
                    <b>Whole-volume ct_vqa_tool, if supplied</b>
                    <p>query + image_path → model-derived text</p>
                    <p>Observed response: —</p>
                    <small>V8minus excludes this tool and disease classifier.</small>
                  </>
                ) : index === 1 ? (
                  <>
                    <b>Selected-slice slice_vqa_tool</b>
                    <p>question + selected 2D image_paths → model-derived text</p>
                    <p>Observed response: —</p>
                    <small>
                      Can inspect several slices; not an entire volume. No slice or selection result
                      is fabricated.
                    </small>
                  </>
                ) : (
                  <>
                    <b>Reconcile scope and disagreement</b>
                    <p>
                      Compare independently derived tool evidence against the exact
                      question/options.
                    </p>
                    <p>Tool 1 evidence: — · tool 2 evidence: —</p>
                    <small>Consensus is requested by the prompt; none is observed here.</small>
                  </>
                )}
              </div>
            </>
          )}
          <small>
            Only task text/path enters initial user prompt; host scenario retains gt. Runtime
            filesystem isolation is unaudited.
          </small>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Keep full option text including its prefix</h3>
          <div className={css.card}>
            <b>Actual participant output: absent</b>
            <pre>{'{"action":"final_answer","answer":"—"}'}</pre>
            <p>Actual trace and score: —</p>
          </div>
          <div className={css.card} data-radagent-vqa-illustrative-format>
            <b>Authored nonclinical formatting fixture</b>
            <p>
              Declared teaching selection: <code>{pack.fixture.teaching_selected_option}</code>
            </p>
            <pre>
              {JSON.stringify({
                action: 'final_answer',
                answer: pack.fixture.teaching_selected_option,
              })}
            </pre>
            <small>
              A token syntax example, not a patient question, generated answer, participant
              submission or correctness result. Bare letter/text fragments change the option string.
            </small>
          </div>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Evaluator role and reward conditions; no private value</h3>
          {visible ? (
            <div data-radagent-vqa-reference-revealed>
              <p>
                CSV answer → host scenario gt; excluded from initial model messages. Host state
                retains it; runtime filesystem isolation remains unaudited.
              </p>
              <div className={css.card}>
                <b>Source reward branch</b>
                <p>
                  Completed VQA: trim/lower full-option equality + BLEU1 + ROUGE-L; configured tool
                  terms may augment reward. Validation compute_reward=False; training True. No
                  observed reward.
                </p>
              </div>
              <table>
                <caption>Authored format controls, not scored VQA examples</caption>
                <thead>
                  <tr>
                    <th>Candidate string</th>
                    <th>Matches declared toy option</th>
                  </tr>
                </thead>
                <tbody>
                  {pack.fixture.candidate_controls.map((item) => (
                    <tr key={item.candidate}>
                      <td>{item.candidate}</td>
                      <td>
                        {item.exact_toy_full_option ? 'Same full string' : 'Changed option string'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p data-radagent-vqa-reference-hidden>
              Evaluator-role explanation and format comparison covered until reader reveal.
            </p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>CT-RATE gate and absent observed result</h3>
          <p>{pack.source.actual_data_gap}</p>
          <p>
            Direct loader default end_idx=None errors; explicit endpoint is inclusive. CLI
            end_id=5000 supplies an integer. Source-only fixtures are not an actual task invocation.
          </p>
          <p>
            Sixty-turn limit. Source reward exists, but main validation disables its computation. No
            clinical performance, tool quality or runtime-isolation claim.
          </p>
        </>
      )}
    </section>
  );
}
export function RadagentVqaOutput({ state }: { state: RadagentVqaState }) {
  return (
    <aside data-radagent-vqa-output={state.scene} className={`${shared.storyOutput} ${css.output}`}>
      <b>RadAgent VQA</b>
      <p>{operationLabels[operationIndex(state.progress)]}</p>
      <p>Answer format: full selected option text including prefix.</p>
      <small>
        Original CT/question, model-derived evidence, participant response and score absent.
        Reference-role explanation {vqaReferenceVisible(state) ? 'revealed' : 'covered'}.
      </small>
    </aside>
  );
}

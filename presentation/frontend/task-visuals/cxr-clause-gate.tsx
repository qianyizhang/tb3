import { useState } from 'react';
import css from './cxr-clause-gate.module.css';

type Evidence = 'unchecked' | 'supported' | 'conflict';
type Edit = 'keep' | 'correct' | 'remove';
type Slot = { evidence: Evidence; edit: Edit };
const START: Slot[] = [
  { evidence: 'unchecked', edit: 'keep' },
  { evidence: 'unchecked', edit: 'keep' },
];
const LABELS = ['Existing draft clause A', 'Existing draft clause B'] as const;

function gate({ evidence, edit }: Slot): string {
  if (evidence === 'unchecked') return 'Needs current/prior evidence check';
  if (evidence === 'supported' && edit === 'remove')
    return 'Review deletion of a supported existing claim';
  if (evidence === 'conflict' && edit === 'keep')
    return 'Cannot keep a conflicting or unsupported claim';
  return 'Allowed edit path illustrated; no clinical correctness inferred';
}

export function CxrClauseGate() {
  const [slots, setSlots] = useState<Slot[]>(START);
  const update = (i: number, patch: Partial<Slot>) =>
    setSlots((old) => old.map((slot, j) => (i === j ? { ...slot, ...patch } : slot)));
  return (
    <div className={css.root} data-inta-cxr-clause-gate>
      <div className={css.head}>
        <strong>Existing-clause edit gate · authored placeholders</strong>
        <span>No patient draft, image, or judge output is loaded.</span>
      </div>
      <div className={css.rows}>
        {slots.map((slot, i) => (
          <fieldset className={css.row} key={i}>
            <legend>{LABELS[i]}</legend>
            <label>
              Hypothetical evidence check
              <select
                value={slot.evidence}
                onChange={(e) => update(i, { evidence: e.currentTarget.value as Evidence })}
                aria-label={`${LABELS[i]} evidence`}
              >
                <option value="unchecked">Not checked</option>
                <option value="supported">Assume evidence supports it</option>
                <option value="conflict">Assume conflict / unsupported</option>
              </select>
            </label>
            <label>
              Action on existing clause
              <select
                value={slot.edit}
                onChange={(e) => update(i, { edit: e.currentTarget.value as Edit })}
                aria-label={`${LABELS[i]} edit`}
              >
                <option value="keep">Keep existing wording</option>
                <option value="correct">Correct existing claim</option>
                <option value="remove">Remove existing claim</option>
              </select>
            </label>
            <output className={css.result} aria-live="polite" data-inta-cxr-gate-result>
              {gate(slot)}
            </output>
          </fieldset>
        ))}
      </div>
      <div className={css.foot}>
        <span>
          <b>New finding:</b> no add-claim action. Final format is FINDINGS only.
        </span>
        <button type="button" onClick={() => setSlots(START)}>
          Reset schematic
        </button>
      </div>
    </div>
  );
}

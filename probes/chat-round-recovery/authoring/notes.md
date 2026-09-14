# H02 — Simulated chat recovery

Original feasibility probe, BR-003. The user's Tavern history motivates the
request-ownership and resident-lifecycle boundary. The richer timeout/late-result
schedule is a new synthetic construction, not a recovered historical failure.
No workbench code, private message content, or service identifiers are copied.

The oracle is an imperative reducer. Verifier checkpoints are separately
hand-authored in `make_cases.py`; they are not calculated by calling the oracle.
Full effect sets catch unexpected duplicate jobs/replies, and full public views
catch loss of finished or cancelled state. Every input invokes a fresh process
through the adapter, so module globals cannot accidentally pass the controls.
The transport's idempotency is a stated assumption; the task never promises
exactly-once effects over a non-idempotent remote endpoint.

Before a model run, check all fixtures against the author reference and run
targeted incorrect controls. This is a fixed, short finite-schedule test,
not a concurrency stress benchmark or proof over all asynchronous programs.
No human-authored submission experience is claimed.

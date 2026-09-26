# Video skill review cases

Use these during skill maintenance. Give a reviewer the request and source
artifacts before showing the criteria. A completed case needs observed actions
and inspected output; reading this file alone is not behavioral validation.

| Case | Request and source | Observable criteria |
| --- | --- | --- |
| Canonical export | Make a video for `tb3-oblique-pose`; provide the bound `rigid-correspondence` story and its workspace contract. | Reuses canonical words/timing and the shared exporter; no duplicate storyboard. Resolves the contract from the workspace when the skill is installed elsewhere. |
| Standalone source | Plan a 45-second explanation of an existing finding that has no story binding. | Produces a concise local storyboard grounded in the finding. Does not invent a binding, alter a score or render when only a plan was requested. |
| Changed source | Export two bound entries, then change a declared dependency between exports in an isolated fixture. | Stops, retains the partial batch and names the changed source. Does not combine different snapshots into a passed batch. |
| Export versus acceptance | Supply a batch whose receipt hashes pass but whose final frame has an unreadable legend. | Reports the visual defect; does not count the entry as reviewed merely because decoding or hashes passed. |

Record skill version, source snapshot, actual observations and unresolved limits.
Use local fixtures and explicit execution scope. No case requires patient data,
publication, a new medical model attempt or a default-model change.

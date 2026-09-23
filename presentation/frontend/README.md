# Browser frontend

The overview and Task Explorer use React and strict TypeScript. Python remains
the authority for records, evidence status, task composition and export assembly.
The browser is read-only. Both production outputs work without a Node server.

## Build and develop

Use the repository's Python environment and Node 22.13 or newer:

```sh
npm ci
npm run frontend:build
uv run med present --serve
```

`make site` builds and serves the portable site with available local tours.
`make site-dev` builds a data snapshot and serves the React/TypeScript sources
through Vite.

`npm run frontend:dev` builds a local data snapshot and opens a Vite development
server on loopback. Vite serves the TypeScript entries against that generated
snapshot; restart the command after changing Python projections or source records.
Never point the development server at raw research runtime directories.

The build writes two self-contained browser bundles under `.local/frontend/`.
Its manifest hashes the frontend source, package lock, build script and TypeScript
configuration, plus compiled output bytes. Python rejects missing, modified or
stale bundles with an explicit rebuild instruction. Source changes during a build
also reject that build. Compiled assets are local outputs, not tracked source.

`med present` copies the overview bundle and assembles static story pages.
`med brief build` embeds the Explorer bundle, CSS, records, source previews,
teaching art and anatomy into one HTML file that opens directly from disk. Assets
and licenses are retained locally; the standalone browser does not fetch them.

## Shared contracts

[presentation_contracts.py](../../src/tb3_medical/presentation_contracts.py) owns
the versioned Python `TypedDict` projections, nested runtime validation and
TypeScript generation. The overview and task-brief builders validate the actual
payload before publication. Extensible scientific fields remain with their
original source records; these interfaces describe browser-consumed fields.

```sh
# After deliberately changing a Python presentation type:
npm run contracts:generate
npm run typecheck
```

`contracts.generated.ts` is generated source; do not edit or separately format it.
`make contracts-check` and `npm run typecheck` reject drift. Browser entry parsers
also check version and essential fields, displaying an error for incompatible
payloads rather than rendering a misleading partial view.

## Component ownership

- `explorer.tsx` owns the application shell and browser history; `state.ts` owns
  explicit navigation/filter transitions; `model.ts` owns presentation selectors.
- `task-browser.tsx`, `task-detail.tsx` and `datasets.tsx` own their interactive
  views. Authored rich HTML is rendered through a small trusted-content boundary.
- `overview.tsx` and `overview-data.ts` own evidence browsing, URL filters and the
  displayed shared vocabulary. They do not derive scientific verdicts.
- Shared visual foundations stay in `../ui.css`. New component-specific styles
  use CSS Modules. Scene rendering is imported through the `TaskScenes` ES module,
  with effect cleanup when its task/view is replaced. Vite bundles teaching art,
  anatomy and notices into the Explorer through direct module imports.
- [Reusable teaching assets](../assets/README.md) own task illustrations and
  plain-language action recipes. Source-derived anatomy keeps its original
  provenance, hashes and notices.

Modality is a separate authored axis from capability, research role and agent
work. Multiple tags describe a task's scope or alternative conditions; they do
not imply every input is supplied together. The filter composes with search and
other filters, and is retained in the URL. Unspecified modalities remain explicit.

## Verification

`make check` covers Python contracts and generated-type consistency.
`make presentation-check` builds real bundles, runs JavaScript checks, then uses
the disposable-browser harness for standalone and served navigation, all task
conditions, source/reference reveals, scenes, keyboard behavior and mobile views.
Follow the root macOS execution instructions for browser launches.

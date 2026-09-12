# Codex CLI repair log

Date: 2026-09-12

## Diagnosis

The global Node installation at `/Users/zhangqy/.nvm/versions/node/v25.9.0`
contained `@openai/codex@0.147.0`, but its platform-specific optional runtime
package, `@openai/codex-darwin-arm64`, was absent. As a result, both `codex
--version` and `codex login status` stopped before starting and reported the
missing optional dependency.

The npm configuration did not omit optional dependencies, and the machine is
`arm64` macOS.

## Repair

The official OpenAI documentation installs the CLI through npm as
`npm -g i @openai/codex@latest`. To repair the existing pinned installation
without changing its version, this command was run with optional dependencies
explicitly included:

```bash
env -u HTTPS_PROXY -u HTTP_PROXY -u ALL_PROXY \
  NPM_CONFIG_INCLUDE=optional \
  /Users/zhangqy/.nvm/versions/node/v25.9.0/bin/npm \
  install -g @openai/codex@0.147.0
```

It completed successfully, adding the missing
`@openai/codex-darwin-arm64@npm:@openai/codex@0.147.0-darwin-arm64` package.
No files under `~/.codex` were edited or removed.

## Verification

```text
codex --version       -> codex-cli 0.147.0
codex login status    -> Logged in using ChatGPT
```

The CLI emits a non-fatal warning that it cannot create PATH aliases due to an
operation-permission error. The existing NVM executable remains callable at
`/Users/zhangqy/.nvm/versions/node/v25.9.0/bin/codex`, and version and login
status both completed successfully. No model trial was part of the CLI repair; later Harbor trials are recorded in ledger.md.

Source: [Official OpenAI Codex installation example](https://developers.openai.com/cookbook/examples/codex/secure_quality_gitlab)

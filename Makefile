PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
PRESENTATION_OUTPUT ?= .local/presentation-check
PRESENTATION_REPORTS ?= .local/presentation-qa

.PHONY: actionlint artifacts build-check check docs-check format format-check hooks hygiene js-check lint med-check \
	presentation-check pre-commit-check site style test type-check
check: hygiene test med-check docs-check type-check style actionlint

hygiene:
	$(PYTHON) -m tb3_medical.hygiene

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

# Portable medical chapters and source-linked figures; no native runtime data.
med-check:
	$(PYTHON) -m tb3_medical.cli check

docs-check:
	$(PYTHON) -m tb3_medical.doc_links

type-check:
	$(PYTHON) -m mypy

actionlint:
	uv run --locked --no-sync actionlint

pre-commit-check:
	$(PYTHON) -m pre_commit run --all-files --show-diff-on-failure

# Build and install the wheel outside the repository, then import it from an
# unrelated directory. The temporary directory is removed on exit.
build-check:
	@set -eu; \
	build_root="$$(mktemp -d)"; \
	trap 'rm -rf "$$build_root"' EXIT; \
	uv build --out-dir "$$build_root/dist"; \
	uv venv --python "$(PYTHON)" "$$build_root/venv"; \
	uv pip install --python "$$build_root/venv/bin/python" "$$build_root"/dist/*.whl; \
	cd "$$build_root"; \
	"$$build_root/venv/bin/python" -c 'from tb3_medical import doc_links, score_ct, score_mri, scoring'; \
	"$$build_root/venv/bin/med" --root "$(CURDIR)" check >/dev/null

# Browser-free JavaScript checks; no scans, encoder or model runtime.
js-check:
	npm run format:check
	node tests/tour_state.cjs
	node tests/task_scene_models.cjs
	node tests/media_export.cjs

# Optional browser regressions. Uses declared, already installed Node/Playwright.
presentation-check: js-check
	$(PYTHON) -m tb3_medical.cli present --output "$(PRESENTATION_OUTPUT)"
	node tests/presentation.cjs "$(PRESENTATION_OUTPUT)" "$(PRESENTATION_REPORTS)"

# Open the read-only medical index and available local tours.
site:
	$(PYTHON) -m tb3_medical.cli present --serve --local-media

# Inventory only: never delete ignored runs, caches, or frozen inputs.
artifacts:
	git status --short
	du -sh .cache .venv* runs probes docs/evidence 2>/dev/null || true

hooks:
	@existing="$$(git config --local --get core.hooksPath || true)"; \
	if [ -n "$$existing" ] && [ "$$existing" != .githooks ]; then \
	  echo "Existing hooksPath=$$existing; integrate .githooks/pre-commit manually." >&2; exit 1; \
	fi
	uv sync --locked --inexact --group dev
	git config --local core.hooksPath .githooks
	$(PYTHON) -m pre_commit install-hooks

style: lint format-check

lint:
	$(PYTHON) -m ruff check src tests

format-check:
	$(PYTHON) -m ruff format --check src tests

format:
	$(PYTHON) -m ruff format src tests

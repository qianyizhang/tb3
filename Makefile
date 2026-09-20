PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: check hygiene test artifacts hooks site med-check style presentation-check
check: hygiene test med-check style

hygiene:
	$(PYTHON) -m tb3_medical.hygiene

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

# Portable medical chapters and source-linked figures; no native runtime data.
med-check:
	$(PYTHON) -m tb3_medical.cli check

# Optional browser regressions. Uses declared, already installed Node/Playwright.
presentation-check:
	$(PYTHON) -m tb3_medical.cli present --output .local/presentation-check
	node tests/tour_state.cjs
	node tests/workbench_ui.cjs .local/presentation-check
	node tests/task_explorer_ui.cjs .local/presentation-check/task-explorer/index.html .local/presentation-check/explorer-qa.json

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
	git config --local core.hooksPath .githooks

style:
	$(PYTHON) -m ruff check src tests
	$(PYTHON) -m ruff format --check src tests

PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: check hygiene test artifacts hooks site
check: hygiene test

hygiene:
	$(PYTHON) scripts/check_hygiene.py

test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

# Reopen the report and native scan explorer; no model trials or downloads.
site:
	$(PYTHON) scripts/serve_site.py --open

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

PYTHONPATH := src

.PHONY: notion-test notion-dry-run

notion-test:
	PYTHONPATH=$(PYTHONPATH) pytest tests/notion_sync

notion-dry-run:
	DRY_RUN=true PYTHONPATH=$(PYTHONPATH) python -m notion_sync.cli --dry-run

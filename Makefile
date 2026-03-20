.PHONY: install test lint check
UV=python3 -m uv

install:
	$(UV) venv --python 3.11
	$(UV) pip install --python .venv/bin/python -e ".[dev]"

test:
	$(UV) run pytest

lint:
	$(UV) run ruff check --select C901 src tests

check:
	$(UV) run ruff check --select C901 src tests
	$(UV) run pytest

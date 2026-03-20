.PHONY: install test lint check

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

lint:
	ruff check .

check:
	ruff check .
	python -m pytest

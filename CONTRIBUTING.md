# Contributing

Thanks for contributing to `imgclean`.

## Local setup

```bash
git clone https://github.com/Weiykong/imgclean.git
cd imgclean
python3.10 -m venv .venv
source .venv/bin/activate
make install
```

If you already have a Python 3.10+ environment, `make install` is enough.

## Common commands

```bash
make test
make lint
make check
```

These map to:

- `make install`: editable install with dev dependencies
- `make test`: run the test suite with `python -m pytest`
- `make lint`: run `ruff check .`
- `make check`: run lint and tests together

## Project shape

- `src/imgclean/cli`: Typer CLI commands
- `src/imgclean/api`: public Python API
- `src/imgclean/core`: scan orchestration pipeline
- `src/imgclean/checks`: independent dataset checks
- `src/imgclean/reports`: HTML, JSON, and CSV outputs
- `tests`: unit and integration coverage

## Pull requests

- Keep changes scoped to one concern where possible.
- Add or update tests for behavior changes.
- Update `README.md` when CLI flags, outputs, or workflows change.
- Do not commit generated reports, cache files, or quarantine outputs.

## Adding a new check

1. Implement a new `BaseCheck` subclass under `src/imgclean/checks`.
2. Register it in the scan registry.
3. Add unit tests and, if needed, one integration test.
4. Document the check in the README.

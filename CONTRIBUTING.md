# Contributing to dcleaner

Thanks for your interest in improving `dcleaner`! This guide gets you set up.

## Development setup

```bash
git clone https://github.com/Shivmahlan/dcleaner.git
cd dcleaner
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"   # editable install + dev tools
pip install pytest        # if not already present
```

> If you don't have a `dev` extra, just run `pip install -e .` and `pip install pytest`.

## Running the tests

```bash
pytest -q
```

Tests live in `tests/` and use a small generated CSV (`tests/data/sample.csv`),
so they run fully offline.

## Project layout

```
dclean/            # the package (core.py is the Data fluent API)
tests/             # pytest suite
examples/          # demo + with/without comparison notebooks
pyproject.toml     # metadata, deps, build config
```

## Making a change

1. Fork and create a branch: `git checkout -b fix/short-description`.
2. Make your change. Keep it small and focused.
3. Add or update tests for the behavior you changed.
4. Run `pytest -q` and make sure it's green.
5. Open a pull request against `main` and fill in the PR template.

## Style

- Keep the fluent API chainable: transform/clean methods must `return self`.
- Prefer vectorized pandas (`.eval`/`.query`) over Python row loops.
- Match the existing docstring style in `core.py`.

## Releasing

Maintainers only. Bump `version` in `pyproject.toml`, update `CHANGELOG.md`,
tag the commit, and run:

```bash
python -m build
python -m twine upload dist/*
```

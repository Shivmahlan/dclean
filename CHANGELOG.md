# Changelog

All notable changes to `dcleaner` are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.5] - 2026-07-19

### Added
- `to_table([max_rows])` — render the FULL dataset as a tidy GitHub-style
  table, so you can print the whole frame (not just a slice) on screen.
- `nulls([plot])` — print missing-value counts per column plus the grand
  total; pass `plot=True` to also render a bar chart of the null counts.
- `to_float(*cols)` — convert string/object column(s) to float (unparseable
  values become NaN). With no args, every object column is coerced.

### Changed
- `head()` / `tail()` now render clean GitHub-style tables via `tabulate`
  with **all columns shown** (pandas' `...` truncation is gone — both the
  `display.max_columns` option and tabulate ensure every column prints).
- `describe()` now prints a highlighted banner and a tidy table, and calls out
  the **mean** per column so the headline statistic jumps out at a glance.
- `print(d)` / `repr(d)` now shows shape AND the column list
  (e.g. `dclean.Data(60×4, cols=[city, age, salary, score])`) instead of just
  the shape, so it no longer duplicates `shape()`'s output.
- Added `tabulate>=0.8` as a dependency for table rendering.

### Fixed
- README/code parity: every documented method now ships and works as written.

## [0.1.3] - 2026-07-10

### Added
- Bundled sample dataset `sample_sales.csv` ships inside the package. A bare
  filename that isn't found on disk is resolved against the bundled data, so
  `Data("sample_sales.csv")` works immediately after `pip install dcleaner` on
  any machine — no manual file downloads.

## [0.1.2] - 2026-07-10

### Fixed
- `keep(*cols)` now accepts multiple positional column names (e.g.
  `.keep("name", "price")`), matching `select(*cols)` — previously required a
  list.
- `filter("x between lo and hi")` is now supported (SQL-style `between`),
  rewritten to `x >= lo and x <= hi`.
- Spaced column names in `filter()` documented with backticks
  (`` d.filter("`total sales` > 100") ``); single quotes compared a string
  literal and raised. Single quotes already worked for string equality on
  normal columns (e.g. `city == 'NY'`).

## [0.1.1] - 2026-07-10

### Added
- `import dcleaner` shim so both `import dcleaner` (then `dcleaner.Data`)
  and `from dclean import Data` work, removing the pip-name/import-name
  confusion.

## [0.1.0] - 2026-07-10

### Added
- Initial release of `dcleaner`: a fluent data-cleaning and visualization
  layer on top of pandas.
- `Data` fluent API: `load`, `head`/`tail`/`shape`/`cols`/`describe`,
  `dropna`/`fillna`/`dedupe`/`drop`/`keep`/`rename`/`lower_cols`/`astype`,
  `filter` (expression strings), `mutate`/`select`/`sort`,
  `groupby`/`agg`/`summarize`/`corr`, `plot` (line/bar/hist/scatter/box/pie)
  and `plot_corr` heatmap, `savefig`/`show`, `to_csv`/`to_df`.
- Auto-format loading for CSV / Excel / JSON / Parquet.
- Headless-safe matplotlib backend (plots save in scripts/CI/servers).
- MIT license, PyPI-ready `pyproject.toml`, 8-test suite, demo notebook,
  and GitHub Actions CI (Python 3.8–3.11).

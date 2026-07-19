"""Core fluent DataFrame wrapper for dclean."""
import os
import re
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless-safe; plots still save/show in notebooks
import matplotlib.pyplot as plt

# Show every column (no "..." truncation) on any raw pandas print.
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 40)

try:  # tabulate gives clean, non-truncated tables; fall back gracefully
    from tabulate import tabulate
except ImportError:  # pragma: no cover - optional dependency
    def tabulate(df, **kwargs):
        showindex = kwargs.get("showindex", True)
        return df.to_string(index=bool(showindex))

class Data:
    """Fluent wrapper around a pandas DataFrame.

    Every transform method returns ``self`` so calls chain:

        from dclean import Data
        (Data("sales.csv")
         .dropna()
         .filter("age > 18")
         .groupby("city").agg("mean", "salary")
         .plot("bar", x="city", y="salary")
         .show())

    Drop back to raw pandas anytime with ``.to_df()``.
    """

    def __init__(self, source=None, df=None):
        if df is not None:
            self.df = df.copy()
        elif isinstance(source, pd.DataFrame):
            self.df = source.copy()
        elif isinstance(source, str):
            self.df = self._load(source)
        elif source is None:
            self.df = pd.DataFrame()
        else:
            raise TypeError(f"Data() can't handle source of type {type(source).__name__}")
        self._group = None
        self._fig = None

    # ----------------------------------------------------------- LOAD
    @staticmethod
    def _sample_path(name):
        """Resolve a bare filename against the bundled sample datasets."""
        here = os.path.dirname(os.path.abspath(__file__))
        cand = os.path.join(here, "data", name)
        return cand if os.path.exists(cand) else None

    @staticmethod
    def _load(path):
        # Bare name (no directory) that isn't on disk -> try bundled samples,
        # so `Data("sample_sales.csv")` works after a plain `pip install`.
        if os.sep not in str(path) and not os.path.exists(path):
            bundled = Data._sample_path(path)
            if bundled:
                path = bundled
        if path.endswith(".csv") or path.endswith(".csv.gz"):
            return pd.read_csv(path)
        if path.endswith((".xls", ".xlsx")):
            return pd.read_excel(path)
        if path.endswith(".json"):
            return pd.read_json(path)
        if path.endswith(".parquet"):
            return pd.read_parquet(path)
        raise ValueError(f"Unsupported file type: {path}")

    @classmethod
    def from_records(cls, records):
        """Build from a list of dicts."""
        return cls(df=pd.DataFrame(records))

    # ----------------------------------------------------------- INSPECT
    def head(self, n=5):
        print(tabulate(self.df.head(n), headers="keys", tablefmt="github",
                       showindex=False))
        return self

    def tail(self, n=5):
        print(tabulate(self.df.tail(n), headers="keys", tablefmt="github",
                       showindex=False))
        return self

    def to_table(self, max_rows=None):
        """Render the FULL dataset as a formatted table (no column truncation).

        Pass ``max_rows`` to cap the number of printed rows — every column is
        always shown. Useful when ``head()`` / ``tail()`` only show part of the
        data and you want the whole thing on screen.
        """
        df = self.df if max_rows is None else self.df.head(max_rows)
        print(tabulate(df, headers="keys", tablefmt="github", showindex=False))
        return self

    def print(self, n=None):
        """Print the dataset itself (chainable).

        No argument -> print the FULL frame. Pass ``n`` to cap to the first
        ``n`` rows (like head()). Returns ``self`` so it can sit inside a
        pipeline, e.g. dump the cleaned data right before exporting it::

            (Data("sales.csv")
             .dropna()
             .print()                 # dump the cleaned data to stdout
             .filter("age > 18")
             .to_csv("out.csv"))

        For a quick look at just the head, use ``.head()`` instead.
        """
        df = self.df if n is None else self.df.head(n)
        print(tabulate(df, headers="keys", tablefmt="github", showindex=False))
        return self

    def info(self):
        self.df.info()
        return self

    def shape(self):
        """Print the shape, the column list, and each feature's dtype.

        (Previously this only printed ``N rows x M cols`` — which overlapped
        with ``repr(Data)``. Now it also surfaces columns and dtypes, so it
        is the one-stop shape+type inspector.)
        """
        print(f"{self.df.shape[0]} rows x {self.df.shape[1]} cols")
        print("columns:", list(self.df.columns))
        print("dtypes:")
        print(self.df.dtypes.to_string())
        return self

    def dtypes(self):
        """Print each feature's data type (a tidy ``column -> dtype`` list).

        Example output::

            city    object
            age      int64
            salary  float64
            score     int64

        For just the raw pandas Series, use ``.to_df().dtypes``.
        """
        print(self.df.dtypes.to_string())
        return self

    def cols(self):
        print(list(self.df.columns))
        return self

    def describe(self):
        """Pretty, highlighted summary of numeric columns.

        Prints a banner + a tidy table, then calls out the headline statistic
        (the **mean**) per column so the main description jumps out at a glance.
        """
        desc = self.df.describe()
        print("\n\033[1m\033[4mDESCRIPTIVE STATISTICS (numeric columns)\033[0m")
        print(tabulate(desc, headers="keys", tablefmt="github",
                       showindex=True, floatfmt=".3f"))
        means = desc.loc["mean"].to_dict()
        if means:
            callout = ", ".join(f"{k}: {v:.3f}" for k, v in means.items())
            print(f"\033[1m→ mean | {callout}\033[0m\n")
        return self

    # ----------------------------------------------------------- CLEAN
    def dropna(self, subset=None):
        self.df = self.df.dropna(subset=subset)
        return self

    def fillna(self, value):
        self.df = self.df.fillna(value)
        return self

    def drop(self, cols):
        cols = [cols] if isinstance(cols, str) else list(cols)
        self.df = self.df.drop(columns=cols)
        return self

    def keep(self, *cols):
        cols = [c for c in cols if isinstance(c, str)]
        self.df = self.df[cols]
        return self

    def rename(self, **kwargs):
        self.df = self.df.rename(columns=kwargs)
        return self

    def dedupe(self, subset=None):
        self.df = self.df.drop_duplicates(subset=subset)
        return self

    def astype(self, **kwargs):
        self.df = self.df.astype(kwargs)
        return self

    def lower_cols(self):
        """Rename all columns to lowercase (common cleaning step)."""
        self.df = self.df.rename(columns={c: str(c).lower() for c in self.df.columns})
        return self

    def nulls(self, plot=False):
        """Show missing-value counts per column (and the total).

        Returns ``self`` so it can sit in a chain right before ``.dropna()``.
        Set ``plot=True`` to also render a bar chart of the null counts
        (finish with ``.savefig()`` / ``.show()``).
        """
        counts = self.df.isna().sum()
        total = int(counts.sum())
        report = counts.rename("nulls").reset_index()
        report.columns = ["column", "nulls"]
        print(tabulate(report, headers="keys", tablefmt="github",
                       showindex=False))
        print(f"\033[1m→ total nulls: {total} across {len(self.df)} rows\033[0m")
        if plot:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(counts.index.astype(str), counts.values)
            ax.set_title("Missing values per column")
            ax.set_ylabel("nulls")
            plt.xticks(rotation=45, ha="right")
            self._fig = fig
        return self

    def to_float(self, *cols):
        """Convert string/object column(s) to float.

        Named columns: ``.to_float("price", "qty")``. With no arguments, every
        object/string column is coerced: ``.to_float()``. Unparseable values
        become NaN (``errors="coerce"``).
        """
        targets = list(cols) if cols else list(
            self.df.select_dtypes(include="object").columns)
        for c in targets:
            self.df[c] = pd.to_numeric(self.df[c], errors="coerce")
        return self

    # ----------------------------------------------------------- FILTER
    def filter(self, expr):
        """Filter with a readable expression string.

        Supports: == != > < >= <= and or in not in
        e.g. filter("age > 18 and city in ['NY','LA']")
        Also supports a SQL-style `between`: filter("score between 70 and 100")
        resolves to score >= 70 and score <= 100.
        Columns with spaces must use back-ticks: filter("`total sales` > 100")
        """
        self.df = self.df[self._eval_expr(expr)]
        return self

    def _eval_expr(self, expr):
        # SQL-style `between x and y` -> `x >= lo and x <= hi`
        m = re.match(r"^\s*(.+?)\s+between\s+(.+?)\s+and\s+(.+?)\s*$", expr, re.IGNORECASE)
        if m:
            col, lo, hi = m.group(1), m.group(2), m.group(3)
            expr = f"({col} >= {lo} and {col} <= {hi})"
        try:
            return self.df.eval(expr)
        except Exception:
            return self.df.query(expr, engine="python")

    # ----------------------------------------------------------- TRANSFORM
    def mutate(self, **kwargs):
        """Add/overwrite columns from expressions.

        mutate(bmi="weight / (height**2)", age1="age + 1")
        A non-string value is assigned literally.
        """
        for col, expr in kwargs.items():
            self.df[col] = self.df.eval(expr) if isinstance(expr, str) else expr
        return self

    def select(self, *cols):
        self.df = self.df[list(cols)]
        return self

    def sort(self, by, ascending=True):
        self.df = self.df.sort_values(by, ascending=ascending)
        return self

    # ----------------------------------------------------------- AGGREGATE
    def groupby(self, *cols):
        self._group = list(cols)
        return self

    def agg(self, how, col=None):
        if not self._group:
            raise RuntimeError("Call groupby() before agg()")
        grp = self.df.groupby(self._group)
        if col is None:
            self.df = grp.agg(how)
        else:
            self.df = grp.agg({col: how}).reset_index()
        self._group = None
        return self

    def summarize(self, **kwargs):
        """Quick named stats. summarize(mean_sal='mean(salary)', n='count()')"""
        out = {}
        for k, v in kwargs.items():
            m = re.match(r"(\w+)\(([\w ]*)\)", v)
            if m:
                func, col = m.group(1), m.group(2).strip()
                if col:
                    out[k] = getattr(self.df[col], func)()
                elif func == "count":
                    out[k] = len(self.df)
                else:
                    out[k] = getattr(self.df, func)()
        self.df = pd.DataFrame([out])
        return self

    def corr(self, method="pearson"):
        """Return the correlation matrix as a DataFrame."""
        self.df = self.df.corr(numeric_only=True, method=method)
        return self

    def plot_corr(self, title="Correlation matrix", cmap="coolwarm"):
        """Heatmap of the numeric correlation matrix."""
        fig, ax = plt.subplots(figsize=(8, 6))
        c = self.df.corr(numeric_only=True)
        im = ax.imshow(c, cmap=cmap)
        ax.set_xticks(range(len(c.columns)))
        ax.set_yticks(range(len(c.columns)))
        ax.set_xticklabels(c.columns, rotation=45, ha="right")
        ax.set_yticklabels(c.columns)
        fig.colorbar(im, ax=ax)
        ax.set_title(title)
        self._fig = fig
        return self

    # ----------------------------------------------------------- VISUALIZE
    def plot(self, kind="line", x=None, y=None, title=None, **kwargs):
        """One-liner plot. kind: line|bar|hist|scatter|box|pie"""
        fig, ax = plt.subplots(figsize=(8, 5))
        if kind == "scatter":
            ax.scatter(self.df[x], self.df[y])
        elif kind == "hist":
            ax.hist(self.df[x or y], **kwargs)
        elif kind == "box":
            self.df.boxplot(column=y, by=x, ax=ax)
        elif kind == "pie":
            self.df.plot(kind="pie", y=y, labels=self.df[x], ax=ax, **kwargs)
        else:
            self.df.plot(kind=kind, x=x, y=y, ax=ax, **kwargs)
        if title:
            ax.set_title(title)
        self._fig = fig
        return self

    def show(self):
        if self._fig is not None:
            plt.show()
        else:
            print(self.df)
        return self

    def savefig(self, path):
        if self._fig is not None:
            self._fig.savefig(path, bbox_inches="tight")
            print(f"saved plot -> {path}")
        else:
            raise RuntimeError("No figure to save. Call plot()/plot_corr() first.")
        return self

    # ----------------------------------------------------------- EXPORT
    def to_csv(self, path):
        self.df.to_csv(path, index=False)
        print(f"saved -> {path}")
        return self

    def to_df(self):
        """Hand back the raw DataFrame for full pandas power."""
        return self.df

    # ----------------------------------------------------------- DUNDERS
    def __str__(self):
        """`print(d)` shows the full dataset (not just the terse repr)."""
        return tabulate(self.df, headers="keys", tablefmt="github", showindex=False)

    def __repr__(self):
        cols = ", ".join(map(str, self.df.columns)) if len(self.df.columns) else "-"
        return f"dclean.Data({self.df.shape[0]}×{self.df.shape[1]}, cols=[{cols}])"

    def __len__(self):
        return len(self.df)

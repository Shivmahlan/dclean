import os
import matplotlib
matplotlib.use("Agg")
import pandas as pd

from dclean import Data

HERE = os.path.dirname(__file__)
SAMPLE = os.path.join(HERE, "data", "sample.csv")


def test_load_and_shape():
    d = Data(SAMPLE)
    assert len(d) == 60
    assert d.df.shape[1] == 4


def test_dropna_removes_nulls():
    d = Data(SAMPLE).dropna()
    assert d.df.isna().sum().sum() == 0
    # we injected 4 NaN salaries + 1 NaN age -> at least 4 rows dropped
    assert len(d) <= 56


def test_filter_expression():
    d = Data(SAMPLE).dropna().filter("age > 18")
    assert (d.df["age"] > 18).all()


def test_groupby_agg():
    d = (Data(SAMPLE).dropna()
         .groupby("city").agg("mean", "salary"))
    assert "salary" in d.df.columns
    assert "city" in d.df.columns
    assert len(d.df) == 3  # NY, LA, SF


def test_mutate_new_column():
    d = Data(SAMPLE).dropna().mutate(double_salary="salary * 2")
    assert "double_salary" in d.df.columns
    assert (d.df["double_salary"] == d.df["salary"] * 2).all()


def test_corr_returns_matrix():
    d = Data(SAMPLE).dropna().corr()
    assert isinstance(d.df, pd.DataFrame)
    assert d.df.shape[0] == d.df.shape[1]


def test_plot_savefig(tmp_path):
    out = tmp_path / "plot.png"
    (Data(SAMPLE).dropna()
        .groupby("city").agg("mean", "salary")
        .plot("bar", x="city", y="salary")
        .savefig(str(out)))
    assert out.exists()
    assert os.path.getsize(out) > 0


def test_to_df_returns_pandas():
    d = Data(SAMPLE)
    raw = d.to_df()
    assert isinstance(raw, pd.DataFrame)
    assert raw.shape == d.df.shape


def test_nulls_reports_total(capsys):
    d = Data(SAMPLE).dropna()
    d.nulls()
    out = capsys.readouterr().out
    assert "total nulls" in out


def test_to_float_coerces(monkeypatch):
    # Build a frame with a string-number column and a clean one.
    d = Data.from_records([
        {"x": "1.5", "y": "2"},
        {"x": "bad", "y": "3"},
    ])
    d.to_float("x", "y")
    assert pd.api.types.is_float_dtype(d.df["x"])
    assert pd.isna(d.df["x"].iloc[1])   # "bad" -> NaN
    assert d.df["y"].iloc[1] == 3.0


def test_to_table_prints_all_columns(capsys):
    d = Data(SAMPLE)
    d.to_table()
    out = capsys.readouterr().out
    # every column header should appear in the printed table
    for col in d.df.columns:
        assert col in out


def test_repr_shows_shape_and_cols():
    d = Data(SAMPLE)
    r = repr(d)
    assert "dclean.Data(" in r
    assert "cols=" in r
    assert str(len(d.df.columns)) in r

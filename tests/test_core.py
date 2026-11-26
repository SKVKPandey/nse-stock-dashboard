"""Offline tests: yfinance and NSE are replaced by fakes, and the LSTM by a stub."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import forecast  # noqa: E402
import market  # noqa: E402

DAYS = pd.bdate_range("2024-01-01", periods=5)


def fake_download(tickers, **kw):
    tickers = [tickers] if isinstance(tickers, str) else tickers
    closes = {"A.NS": [100, 100, 100, 100, 110], "B.NS": [50, 50, 50, 50, 45], "C.NS": [10, 10, 10, 10, 10.5],
              "^NSEI": [22000, 22100, 22200, 22300, 22500]}
    cols = pd.MultiIndex.from_tuples([(f, t) for f in ("Open", "High", "Low", "Close") for t in tickers])
    data = {(f, t): closes.get(t, [np.nan] * 5) for f, t in cols}
    df = pd.DataFrame(data, index=DAYS)
    return df if len(tickers) > 1 else df.droplevel(1, axis=1)


def test_constituents_parses_nse_csv():
    csv = b"Company Name,Industry,Symbol,Series,ISIN Code\nAlpha Ltd.,IT,A,EQ,X\nBeta Ltd.,Banks,B,EQ,Y\n"
    df = market.constituents("NIFTY 50", fetch=lambda url: csv)
    assert df["symbol"].tolist() == ["A", "B"] and df["company"].iloc[0] == "Alpha Ltd."


def test_index_quote():
    q = market.index_quote("NIFTY 50", download=fake_download)
    assert q["last"] == 22500 and q["change"] == 200 and q["pchange"] == round(200 / 22300 * 100, 2)


def test_movers_split_and_order():
    g, l = market.movers(["A", "B", "C", "MISSING"], download=fake_download)
    assert g.index.tolist() == ["A", "C"] and l.index.tolist() == ["B"]
    assert g.loc["A", "pchange"] == 10.0


def test_history_flat_columns():
    df = market.history("A", download=fake_download)
    assert list(df.columns) == ["Open", "High", "Low", "Close"] and len(df) == 5


def test_windows():
    X, y = forecast.windows(np.arange(10), 3)
    assert X.shape == (7, 3) and X[0].tolist() == [0, 1, 2] and y[0] == 3 and y[-1] == 9


def test_trading_days_skip_weekends():
    d = forecast.trading_days_after(pd.Timestamp("2024-01-05"), 3)  # a Friday
    assert [x.day_name() for x in d] == ["Monday", "Tuesday", "Wednesday"]


class LastValue:
    """Stub model: predicts the last value of each window."""
    def fit(self, *a, **k):
        pass

    def predict(self, X, verbose=0):
        return X[:, -1, :]


def test_run_end_to_end_with_stub():
    idx = pd.bdate_range("2020-01-01", periods=400)
    close = pd.Series(np.linspace(100, 200, 400), index=idx)
    res = forecast.run(close, step=20, days=5, model_factory=lambda step: LastValue())
    assert len(res["forecast"]) == 5 and res["forecast"].index[0] > idx[-1]
    assert np.allclose(res["forecast"], close.iloc[-1])            # last-value model stays flat
    assert 0 < res["rmse"] < 1                                    # one step behind a smooth line
    assert res["test"].index[-1] == idx[-1]


def test_run_rejects_short_history():
    close = pd.Series(np.arange(50.0), index=pd.bdate_range("2024-01-01", periods=50))
    try:
        forecast.run(close, step=20, model_factory=lambda s: LastValue())
    except ValueError:
        return
    raise AssertionError("expected ValueError")

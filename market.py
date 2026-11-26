"""Market data for the dashboard: index lists, quotes, movers and price history.

Everything comes from public sources:
- index constituents: the CSV files NSE publishes on archives.nseindia.com
- prices: Yahoo Finance through the yfinance package (NSE symbols end in ".NS")

The original 2023 version used nsetools, which stopped working when NSE closed
its unofficial quote endpoints. This module replaces it.
"""
from __future__ import annotations

import io
import urllib.request

import pandas as pd

INDICES = {
    # name shown in the app: (Yahoo symbol for the index, NSE constituents file)
    "NIFTY 50": ("^NSEI", "ind_nifty50list.csv"),
    "NIFTY NEXT 50": ("^NSMIDCP", "ind_niftynext50list.csv"),
    "NIFTY MIDCAP 50": ("^NSEMDCP50", "ind_niftymidcap50list.csv"),
    "NIFTY BANK": ("^NSEBANK", "ind_niftybanklist.csv"),
    "NIFTY FIN SERVICE": ("NIFTY_FIN_SERVICE.NS", "ind_niftyfinancelist.csv"),
}
NSE_ARCHIVE = "https://archives.nseindia.com/content/indices/"
HEADERS = {"User-Agent": "Mozilla/5.0 (nse-stock-dashboard)"}


def _yf():
    import yfinance as yf  # imported lazily so tests can run without network
    return yf


def constituents(index: str, fetch=None) -> pd.DataFrame:
    """Company name and symbol for every stock in an index, from NSE's published list."""
    _, fname = INDICES[index]
    if fetch is None:
        req = urllib.request.Request(NSE_ARCHIVE + fname, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read()
    else:
        raw = fetch(NSE_ARCHIVE + fname)
    df = pd.read_csv(io.BytesIO(raw))
    df.columns = [c.strip() for c in df.columns]
    return df[["Company Name", "Symbol"]].rename(columns={"Company Name": "company", "Symbol": "symbol"})


def index_quote(index: str, download=None) -> dict:
    """Last close, change and % change for an index, from its last two daily closes."""
    sym, _ = INDICES[index]
    hist = (download or _yf().download)(sym, period="5d", interval="1d", progress=False, auto_adjust=False)
    closes = _close(hist, sym).dropna()
    if len(closes) < 2:
        return {"index": index, "last": None, "change": None, "pchange": None}
    last, prev = float(closes.iloc[-1]), float(closes.iloc[-2])
    return {"index": index, "last": round(last, 2), "change": round(last - prev, 2),
            "pchange": round((last - prev) / prev * 100, 2)}


def movers(symbols: list[str], top: int = 10, download=None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Top gainers and losers among the given NSE symbols, by % change over the last session."""
    tickers = [s + ".NS" for s in symbols]
    hist = (download or _yf().download)(tickers, period="5d", interval="1d", progress=False,
                                        auto_adjust=False, group_by="column")
    rows = []
    for s, t in zip(symbols, tickers):
        c = _close(hist, t).dropna()
        if len(c) < 2:
            continue
        last, prev = float(c.iloc[-1]), float(c.iloc[-2])
        rows.append({"symbol": s, "last": round(last, 2), "change": round(last - prev, 2),
                     "pchange": round((last - prev) / prev * 100, 2)})
    df = pd.DataFrame(rows, columns=["symbol", "last", "change", "pchange"])
    if df.empty:
        return df, df
    df = df.sort_values("pchange", ascending=False).set_index("symbol")
    gainers = df[df["pchange"] > 0].head(top)
    losers = df[df["pchange"] < 0].sort_values("pchange").head(top)
    return gainers, losers


def history(symbol: str, years: int = 5, download=None) -> pd.DataFrame:
    """Daily OHLC for one NSE stock."""
    t = symbol + ".NS"
    df = (download or _yf().download)(t, period=f"{years}y", interval="1d", progress=False, auto_adjust=False)
    if isinstance(df.columns, pd.MultiIndex):
        df = df.xs(t, axis=1, level=-1) if t in df.columns.get_level_values(-1) else df.droplevel(-1, axis=1)
    return df[["Open", "High", "Low", "Close"]].dropna()


def _close(hist: pd.DataFrame, ticker: str) -> pd.Series:
    """The Close column for one ticker, whether yfinance returned flat or multi-level columns."""
    if hist is None or hist.empty:
        return pd.Series(dtype=float)
    if isinstance(hist.columns, pd.MultiIndex):
        if ("Close", ticker) in hist.columns:
            return hist[("Close", ticker)]
        return pd.Series(dtype=float)
    return hist["Close"]

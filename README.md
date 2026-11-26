# NSE Stock Dashboard

A Streamlit dashboard for Indian stocks: index tiles, the day's top gainers and losers in an index, a candlestick chart for any stock in it, and a 30-day LSTM price forecast that shows its own test error.

First built in May 2023. Brought up to date in November 2026, because the library it relied on for live NSE data (`nsetools`) stopped working when NSE closed its unofficial quote endpoints.

> For learning only. This is not investment advice, and a model like this cannot predict the market reliably.

## What it shows

- **Five index tiles:** NIFTY 50, NIFTY NEXT 50, NIFTY MIDCAP 50, NIFTY BANK and NIFTY FIN SERVICE, each with the last close and the change on the day.
- **Top gainers and losers:** pick an index in the sidebar. Its member list is read from the CSV files NSE publishes, and the % change is worked out from the last two daily closes.
- **Candlestick chart:** pick a stock to see 1 to 10 years of daily prices.
- **LSTM forecast** (optional): trains a three-layer LSTM on the first 65% of the closing prices and tests it on the rest. It then projects 30 trading days ahead. The test error (RMSE, in rupees) is shown next to the forecast, so you can see how far off the model was on prices it hadn't seen.

## Run it

```bash
pip install -r requirements.txt
pip install tensorflow          # only needed for the forecast
streamlit run app.py
```

Prices are end-of-day from Yahoo Finance (NSE symbols end in `.NS`), so the tiles and movers reflect the last completed session.

## Tests

```bash
pip install pytest
python -m pytest -q
```

The tests run offline. Yahoo Finance and NSE are replaced with fake data, and the LSTM with a stub, to check the data handling, the gainer and loser split, the train/test windows and the forecast dates.

## Files

| File | What it does |
|---|---|
| `app.py` | The Streamlit page |
| `market.py` | Index lists, index quotes, movers and price history |
| `forecast.py` | Windowing, the LSTM, test error and the 30-day projection |
| `tests/test_core.py` | Offline tests |
| `legacy/nsepredic.py` | The original 2023 single-file version, kept for reference |

## What changed from the 2023 version

- `nsetools` was replaced with NSE's published index lists plus Yahoo Finance prices.
- `DataFrame.append`, which pandas 2 removed, was replaced.
- The test error is now shown. Before, it was computed and thrown away.
- Forecast dates skip weekends. NSE holidays are still counted.
- The code is split into three modules with tests, instead of one 600-line class.

"""LSTM price forecast, as in the 2023 version, with the evaluation made visible.

The model is trained on the first 65% of the closing prices and tested on the
rest. The app shows the test error (RMSE, in rupees) next to the forecast, so
it is clear how far off the model was on data it had not seen.

This is a learning project. A model like this does not predict markets
reliably, and nothing here is investment advice.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def windows(series: np.ndarray, step: int) -> tuple[np.ndarray, np.ndarray]:
    """Split a 1-D series into (X, y): each X row is `step` values, y is the next value."""
    s = np.asarray(series, dtype=float).ravel()
    if len(s) <= step:
        return np.empty((0, step)), np.empty(0)
    X = np.lib.stride_tricks.sliding_window_view(s[:-1], step)
    y = s[step:]
    return X, y


def split(series: np.ndarray, train_share: float = 0.65) -> tuple[np.ndarray, np.ndarray]:
    n = int(len(series) * train_share)
    return series[:n], series[n:]


def build_model(step: int):
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
    from tensorflow.keras.models import Sequential
    model = Sequential([
        Input(shape=(step, 1)),
        LSTM(50, return_sequences=True), Dropout(0.2),
        LSTM(50, return_sequences=True), Dropout(0.3),
        LSTM(50),
        Dense(1),
    ])
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model


def roll_forward(model, last_window: np.ndarray, days: int) -> np.ndarray:
    """Predict `days` steps ahead, feeding each prediction back in as the newest input."""
    w = list(np.asarray(last_window, dtype=float).ravel())
    step = len(w)
    out = []
    for _ in range(days):
        x = np.array(w[-step:]).reshape(1, step, 1)
        yhat = float(np.asarray(model.predict(x, verbose=0)).ravel()[0])
        out.append(yhat)
        w.append(yhat)
    return np.array(out)


def trading_days_after(last: pd.Timestamp, n: int) -> pd.DatetimeIndex:
    """The next n weekdays after `last` (NSE holidays are not removed)."""
    return pd.bdate_range(pd.Timestamp(last) + pd.Timedelta(days=1), periods=n)


def run(close: pd.Series, step: int = 100, days: int = 30, epochs: int = 30, model_factory=build_model):
    """Train, test and forecast. Returns a dict with the test RMSE and the forecast series."""
    from sklearn.preprocessing import MinMaxScaler
    values = close.to_numpy(dtype=float).reshape(-1, 1)
    if len(values) < step * 3:
        raise ValueError(f"Need at least {step * 3} days of prices, got {len(values)}.")
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values).ravel()
    train, test = split(scaled)
    Xtr, ytr = windows(train, step)
    Xte, yte = windows(np.concatenate([train[-step:], test]), step)
    model = model_factory(step)
    model.fit(Xtr[..., None], ytr, validation_data=(Xte[..., None], yte), epochs=epochs, batch_size=64, verbose=0)
    pred_test = scaler.inverse_transform(np.asarray(model.predict(Xte[..., None], verbose=0)).reshape(-1, 1)).ravel()
    actual_test = scaler.inverse_transform(yte.reshape(-1, 1)).ravel()
    rmse = float(np.sqrt(np.mean((pred_test - actual_test) ** 2)))
    future = scaler.inverse_transform(roll_forward(model, scaled[-step:], days).reshape(-1, 1)).ravel()
    idx = trading_days_after(close.index[-1], days)
    return {
        "rmse": rmse,
        "test": pd.Series(pred_test, index=close.index[-len(pred_test):]),
        "forecast": pd.Series(future, index=idx),
    }

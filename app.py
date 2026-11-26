"""NSE Stock Dashboard (Streamlit).

    streamlit run app.py

Index tiles, top gainers and losers for the chosen index, a candlestick chart
for any stock in it, and an optional 30-day LSTM forecast with its test error.
Prices are end-of-day from Yahoo Finance. Learning project, not investment advice.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import market

st.set_page_config(page_title="NSE Stock Dashboard", layout="wide")


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def get_constituents(index):
    return market.constituents(index)


@st.cache_data(ttl=600, show_spinner=False)
def get_quote(index):
    return market.index_quote(index)


@st.cache_data(ttl=600, show_spinner=False)
def get_movers(symbols):
    return market.movers(list(symbols))


@st.cache_data(ttl=3600, show_spinner=False)
def get_history(symbol, years):
    return market.history(symbol, years)


def tile(col, q):
    if q["last"] is None:
        col.metric(q["index"], "n/a")
    else:
        col.metric(q["index"], f"{q['last']:,.2f}", f"{q['change']:+,.2f} ({q['pchange']:+.2f}%)")


st.title("NSE Stock Dashboard")
st.caption("End-of-day prices from Yahoo Finance. For learning only; not investment advice.")

cols = st.columns(len(market.INDICES))
for col, name in zip(cols, market.INDICES):
    try:
        tile(col, get_quote(name))
    except Exception:
        col.metric(name, "n/a")

index = st.sidebar.radio("Index", list(market.INDICES))
try:
    members = get_constituents(index)
except Exception as e:
    st.error(f"Could not load the {index} list from NSE ({type(e).__name__}). Try again in a minute.")
    st.stop()

symbol = st.sidebar.selectbox("Stock", ["(none)"] + members["symbol"].tolist())
years = st.sidebar.slider("Years of history", 1, 10, 5)

if symbol == "(none)":
    with st.spinner(f"Loading {index} movers..."):
        gainers, losers = get_movers(tuple(members["symbol"]))
    names = members.set_index("symbol")["company"]
    left, right = st.columns(2)
    left.subheader("Top gainers")
    left.dataframe(gainers.join(names), width="stretch")
    right.subheader("Top losers")
    right.dataframe(losers.join(names), width="stretch")
    st.stop()

company = members.set_index("symbol").loc[symbol, "company"]
st.header(f"{company} ({symbol})")
df = get_history(symbol, years)
if df.empty:
    st.warning("No price history returned for this stock.")
    st.stop()

fig = go.Figure(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"]))
fig.update_layout(xaxis_rangeslider_visible=False, height=480, margin=dict(t=20, b=20))
st.plotly_chart(fig, width="stretch")

st.subheader("LSTM forecast")
st.write("Trains a small LSTM on 65% of the closing prices, tests it on the rest, then projects 30 trading days. "
         "Training takes a minute or two and needs TensorFlow (`pip install tensorflow`).")
if st.button("Train and forecast"):
    try:
        import forecast
        with st.spinner("Training..."):
            res = forecast.run(df["Close"])
    except ImportError:
        st.error("TensorFlow is not installed. Run `pip install tensorflow` and restart.")
        st.stop()
    except ValueError as e:
        st.warning(str(e))
        st.stop()
    st.metric("Error on the test period (RMSE)", f"Rs {res['rmse']:,.2f}")
    f = go.Figure()
    f.add_scatter(x=df.index, y=df["Close"], name="Close")
    f.add_scatter(x=res["test"].index, y=res["test"], name="Model on test period")
    f.add_scatter(x=res["forecast"].index, y=res["forecast"], name="Forecast")
    f.update_layout(height=420, margin=dict(t=20, b=20))
    st.plotly_chart(f, width="stretch")
    st.dataframe(res["forecast"].rename("forecast close").round(2).head(10).to_frame(), width="stretch")
    st.caption("A model like this follows recent prices. It does not know about news, results or the wider market.")
